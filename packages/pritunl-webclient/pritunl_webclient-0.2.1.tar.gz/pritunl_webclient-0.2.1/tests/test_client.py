"""Unit tests for PritunlClient."""

import httpx
import pytest
import respx

from pritunl_webclient import PritunlClient
from pritunl_webclient.exceptions import (
    AuthenticationError,
    NotAuthenticated,
    PritunlError,
    ServerNotFound,
)


@pytest.fixture
def base_url():
    """Base URL for testing."""
    return "https://pritunl.example.com"


@pytest.fixture
def client(base_url):
    """Create a PritunlClient instance for testing."""
    client = PritunlClient(base_url, verify=False, timeout=10)
    yield client
    client.close()


@pytest.fixture
def authenticated_client(base_url):
    """Create an authenticated PritunlClient instance."""
    client = PritunlClient(base_url, verify=False, timeout=10)
    # Manually set credentials and session cookie to simulate authenticated state
    client._username = "testuser"
    client._password = "testpass"
    client._client.cookies.set("session", "test-session-cookie")
    client._csrf_token = "test-csrf-token"
    yield client
    client.close()


class TestPritunlClientInit:
    """Test client initialization."""

    def test_init_strips_trailing_slash(self):
        """Test that trailing slash is removed from base_url."""
        client = PritunlClient("https://example.com/", verify=False)
        assert client.base_url == "https://example.com"
        client.close()

    def test_init_without_trailing_slash(self):
        """Test initialization with URL without trailing slash."""
        client = PritunlClient("https://example.com", verify=False)
        assert client.base_url == "https://example.com"
        client.close()

    def test_init_default_values(self, base_url):
        """Test that default values are set correctly."""
        client = PritunlClient(base_url)
        assert client.base_url == base_url
        assert client._csrf_token is None
        assert client._username is None
        assert client._password is None
        client.close()


class TestLogin:
    """Test login functionality."""

    @respx.mock
    def test_login_success(self, client, base_url):
        """Test successful login."""
        # Mock login endpoint
        login_route = respx.post(f"{base_url}/auth/session").mock(
            return_value=httpx.Response(200, json={"success": True})
        )

        # Mock state endpoint
        state_route = respx.get(f"{base_url}/state").mock(
            return_value=httpx.Response(
                200,
                json={"csrf_token": "new-csrf-token", "authenticated": True},
            )
        )

        # Perform login
        client.login("testuser", "testpass")

        # Verify credentials are stored
        assert client._username == "testuser"
        assert client._password == "testpass"
        assert client._csrf_token == "new-csrf-token"

        # Verify endpoints were called
        assert login_route.called
        assert state_route.called

    @respx.mock
    def test_login_failure(self, client, base_url):
        """Test login failure with incorrect credentials."""
        # Mock failed login
        respx.post(f"{base_url}/auth/session").mock(
            return_value=httpx.Response(401, json={"error": "Invalid credentials"})
        )

        # Attempt login and expect AuthenticationError
        with pytest.raises(AuthenticationError, match="login failed: 401"):
            client.login("baduser", "badpass")

    @respx.mock
    def test_login_network_error(self, client, base_url):
        """Test login with network error."""
        # Mock network error
        respx.post(f"{base_url}/auth/session").mock(side_effect=httpx.ConnectError("Connection failed"))

        # Attempt login and expect network error
        with pytest.raises(httpx.ConnectError):
            client.login("testuser", "testpass")


class TestEnsureAuth:
    """Test authentication enforcement."""

    def test_ensure_auth_with_session(self, authenticated_client):
        """Test that _ensure_auth passes when session exists."""
        # Should not raise exception
        authenticated_client._ensure_auth()

    def test_ensure_auth_without_session_no_credentials(self, client):
        """Test that _ensure_auth raises error when no session and no credentials."""
        with pytest.raises(NotAuthenticated, match="call login\\(\\) first"):
            client._ensure_auth()

    @respx.mock
    def test_ensure_auth_auto_login(self, client, base_url):
        """Test that _ensure_auth automatically logs in when credentials exist."""
        # Set credentials but no session
        client._username = "testuser"
        client._password = "testpass"

        # Mock login and state endpoints
        login_route = respx.post(f"{base_url}/auth/session").mock(
            return_value=httpx.Response(200, json={"success": True})
        )
        state_route = respx.get(f"{base_url}/state").mock(
            return_value=httpx.Response(
                200,
                json={"csrf_token": "auto-csrf-token", "authenticated": True},
            )
        )

        # Call _ensure_auth - should auto-login
        client._ensure_auth()

        # Verify login and state endpoints were called
        assert login_route.called
        assert state_route.called
        assert client._csrf_token == "auto-csrf-token"


class TestState:
    """Test _state method."""

    @respx.mock
    def test_state_success(self, authenticated_client, base_url):
        """Test successful state retrieval."""
        state_data = {
            "csrf_token": "updated-csrf-token",
            "authenticated": True,
            "username": "testuser",
        }

        respx.get(f"{base_url}/state").mock(return_value=httpx.Response(200, json=state_data))

        result = authenticated_client._state()

        assert result == state_data
        assert authenticated_client._csrf_token == "updated-csrf-token"

    @respx.mock
    def test_state_failure(self, authenticated_client, base_url):
        """Test state retrieval failure."""
        respx.get(f"{base_url}/state").mock(return_value=httpx.Response(500, json={"error": "Server error"}))

        with pytest.raises(PritunlError, match="_state failed: 500"):
            authenticated_client._state()


class TestListServers:
    """Test list_servers method."""

    @respx.mock
    def test_list_servers_success(self, authenticated_client, base_url):
        """Test successful server listing."""
        servers_data = {
            "servers": [
                {"id": "server1", "name": "VPN Server 1", "status": "online"},
                {"id": "server2", "name": "VPN Server 2", "status": "offline"},
            ]
        }

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        result = authenticated_client.list_servers(page=0)

        assert len(result) == 2
        assert result[0]["id"] == "server1"
        assert result[1]["id"] == "server2"

    @respx.mock
    def test_list_servers_with_pagination(self, authenticated_client, base_url):
        """Test server listing with pagination."""
        servers_data = {
            "servers": [
                {"id": "server3", "name": "VPN Server 3", "status": "online"},
            ]
        }

        route = respx.get(f"{base_url}/server", params={"page": "1"}).mock(
            return_value=httpx.Response(200, json=servers_data)
        )

        result = authenticated_client.list_servers(page=1)

        assert len(result) == 1
        assert result[0]["id"] == "server3"
        assert route.called

    @respx.mock
    def test_list_servers_failure(self, authenticated_client, base_url):
        """Test server listing failure."""
        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(403, json={"error": "Forbidden"}))

        with pytest.raises(PritunlError, match="list_servers failed: 403"):
            authenticated_client.list_servers()

    def test_list_servers_not_authenticated(self, client):
        """Test that list_servers requires authentication."""
        with pytest.raises(NotAuthenticated):
            client.list_servers()


class TestStartServer:
    """Test start_server method."""

    @respx.mock
    def test_start_server_with_server_obj(self, authenticated_client, base_url):
        """Test starting server with provided server object."""
        server_id = "server123"
        server_obj = {
            "id": server_id,
            "name": "Test Server",
            "status": "offline",
        }

        route = respx.put(f"{base_url}/server/{server_id}/operation/start").mock(
            return_value=httpx.Response(200, json={"status": "online"})
        )

        result = authenticated_client.start_server(server_id, server_obj)

        assert result["status"] == "online"
        assert route.called

    @respx.mock
    def test_start_server_without_server_obj(self, authenticated_client, base_url):
        """Test starting server without server object (fetches from list)."""
        server_id = "server456"
        servers_data = {"servers": [{"id": server_id, "name": "Auto Server", "status": "offline"}]}

        # Mock list_servers
        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        # Mock start operation
        respx.put(f"{base_url}/server/{server_id}/operation/start").mock(
            return_value=httpx.Response(200, json={"status": "online"})
        )

        result = authenticated_client.start_server(server_id)

        assert result["status"] == "online"

    @respx.mock
    def test_start_server_not_found(self, authenticated_client, base_url):
        """Test starting server that doesn't exist."""
        server_id = "nonexistent"
        servers_data = {"servers": []}

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        with pytest.raises(ServerNotFound, match=f"server {server_id} not found"):
            authenticated_client.start_server(server_id)

    @respx.mock
    def test_start_server_failure(self, authenticated_client, base_url):
        """Test start server operation failure."""
        server_id = "server789"
        server_obj = {"id": server_id, "name": "Test Server"}

        respx.put(f"{base_url}/server/{server_id}/operation/start").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )

        with pytest.raises(PritunlError, match="start_server failed: 500"):
            authenticated_client.start_server(server_id, server_obj)


class TestStopServer:
    """Test stop_server method."""

    @respx.mock
    def test_stop_server_with_server_obj(self, authenticated_client, base_url):
        """Test stopping server with provided server object."""
        server_id = "server123"
        server_obj = {
            "id": server_id,
            "name": "Test Server",
            "status": "online",
        }

        route = respx.put(f"{base_url}/server/{server_id}/operation/stop").mock(
            return_value=httpx.Response(200, json={"status": "offline"})
        )

        result = authenticated_client.stop_server(server_id, server_obj)

        assert result["status"] == "offline"
        assert route.called

    @respx.mock
    def test_stop_server_without_server_obj(self, authenticated_client, base_url):
        """Test stopping server without server object (fetches from list)."""
        server_id = "server456"
        servers_data = {"servers": [{"id": server_id, "name": "Auto Server", "status": "online"}]}

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        respx.put(f"{base_url}/server/{server_id}/operation/stop").mock(
            return_value=httpx.Response(200, json={"status": "offline"})
        )

        result = authenticated_client.stop_server(server_id)

        assert result["status"] == "offline"

    @respx.mock
    def test_stop_server_failure(self, authenticated_client, base_url):
        """Test stop server operation failure."""
        server_id = "server789"
        server_obj = {"id": server_id, "name": "Test Server"}

        respx.put(f"{base_url}/server/{server_id}/operation/stop").mock(
            return_value=httpx.Response(500, json={"error": "Server error"})
        )

        with pytest.raises(PritunlError, match="stop_server failed: 500"):
            authenticated_client.stop_server(server_id, server_obj)


class TestCheckServerStatus:
    """Test check_server_status method."""

    @respx.mock
    def test_check_server_status_success(self, authenticated_client, base_url):
        """Test successful server status check."""
        server_id = "server123"
        status_data = [
            {
                "host_id": "host1",
                "status": "online",
                "uptime": 3600,
                "user_count": 5,
            }
        ]

        respx.get(f"{base_url}/server/{server_id}/host").mock(return_value=httpx.Response(200, json=status_data))

        result = authenticated_client.check_server_status(server_id)

        assert len(result) == 1
        assert result[0]["host_id"] == "host1"
        assert result[0]["status"] == "online"
        assert result[0]["user_count"] == 5

    @respx.mock
    def test_check_server_status_failure(self, authenticated_client, base_url):
        """Test server status check failure."""
        server_id = "server456"

        respx.get(f"{base_url}/server/{server_id}/host").mock(
            return_value=httpx.Response(404, json={"error": "Not found"})
        )

        with pytest.raises(PritunlError, match="check_server_status failed: 404"):
            authenticated_client.check_server_status(server_id)

    def test_check_server_status_not_authenticated(self, client):
        """Test that check_server_status requires authentication."""
        with pytest.raises(NotAuthenticated):
            client.check_server_status("server123")


class TestGetHeaders:
    """Test _get_headers method."""

    def test_get_headers_basic(self, authenticated_client):
        """Test basic headers generation."""
        headers = authenticated_client._get_headers()

        assert "accept" in headers
        assert "x-requested-with" in headers
        assert headers["x-requested-with"] == "XMLHttpRequest"

    def test_get_headers_with_csrf_token(self, authenticated_client):
        """Test headers include CSRF token when available."""
        authenticated_client._csrf_token = "test-csrf-123"
        headers = authenticated_client._get_headers()

        assert headers["csrf-token"] == "test-csrf-123"

    def test_get_headers_without_csrf_token(self, client):
        """Test headers without CSRF token."""
        client._csrf_token = None
        headers = client._get_headers()

        assert "csrf-token" not in headers

    def test_get_headers_with_extra(self, authenticated_client):
        """Test headers with extra parameters."""
        extra = {"content-type": "application/json", "custom-header": "value"}
        headers = authenticated_client._get_headers(extra=extra)

        assert headers["content-type"] == "application/json"
        assert headers["custom-header"] == "value"
        assert "accept" in headers  # Original headers still present


class TestFindServerObj:
    """Test _find_server_obj method."""

    @respx.mock
    def test_find_server_obj_found(self, authenticated_client, base_url):
        """Test finding server object successfully."""
        server_id = "target-server"
        servers_data = {
            "servers": [
                {"id": "server1", "name": "Server 1"},
                {"id": server_id, "name": "Target Server"},
                {"id": "server3", "name": "Server 3"},
            ]
        }

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        result = authenticated_client._find_server_obj(server_id)

        assert result["id"] == server_id
        assert result["name"] == "Target Server"

    @respx.mock
    def test_find_server_obj_not_found(self, authenticated_client, base_url):
        """Test when server object is not found."""
        servers_data = {
            "servers": [
                {"id": "server1", "name": "Server 1"},
            ]
        }

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        with pytest.raises(ServerNotFound, match="server missing not found"):
            authenticated_client._find_server_obj("missing")

    @respx.mock
    def test_find_server_obj_empty_list(self, authenticated_client, base_url):
        """Test finding server in empty server list."""
        servers_data = {"servers": []}

        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json=servers_data))

        with pytest.raises(ServerNotFound):
            authenticated_client._find_server_obj("any-server")


class TestDecoratorIntegration:
    """Test that the require_auth decorator works correctly."""

    @respx.mock
    def test_decorator_allows_authenticated_calls(self, authenticated_client, base_url):
        """Test that decorated methods work when authenticated."""
        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json={"servers": []}))

        # Should not raise exception
        result = authenticated_client.list_servers()
        assert isinstance(result, list)

    def test_decorator_blocks_unauthenticated_calls(self, client):
        """Test that decorated methods are blocked when not authenticated."""
        # Should raise NotAuthenticated
        with pytest.raises(NotAuthenticated):
            client.list_servers()

    @respx.mock
    def test_decorator_auto_authenticates(self, client, base_url):
        """Test that decorator triggers auto-authentication when credentials exist."""
        # Set credentials
        client._username = "testuser"
        client._password = "testpass"

        # Mock login flow
        respx.post(f"{base_url}/auth/session").mock(return_value=httpx.Response(200, json={"success": True}))
        respx.get(f"{base_url}/state").mock(
            return_value=httpx.Response(200, json={"csrf_token": "csrf", "authenticated": True})
        )

        # Mock the actual list_servers call
        respx.get(f"{base_url}/server").mock(return_value=httpx.Response(200, json={"servers": []}))

        # Should auto-login and succeed
        result = client.list_servers()
        assert isinstance(result, list)


class TestClose:
    """Test close method."""

    def test_close(self, base_url):
        """Test that close properly closes the HTTP client."""
        client = PritunlClient(base_url)
        client.close()

        # After closing, the client should not be usable
        assert client._client.is_closed

    def test_context_manager(self, base_url):
        """Test that context manager properly closes the client."""
        with PritunlClient(base_url) as client:
            assert not client._client.is_closed

        # After exiting context, client should be closed
        assert client._client.is_closed
