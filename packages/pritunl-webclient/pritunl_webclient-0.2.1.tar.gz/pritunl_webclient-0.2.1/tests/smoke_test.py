"""Quick smoke test to ensure package imports and basic construction work."""

from pritunl_webclient import PritunlClient


def run():
    c = PritunlClient("https://example.invalid", verify=False)
    print("client created")
    c.close()


if __name__ == "__main__":
    run()
