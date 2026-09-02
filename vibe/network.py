import requests

class RoutedSession(requests.Session):
    def __init__(self, mode="privacy", tor_port=None):
        super().__init__()
        self.mode=mode
        self.tor_port=tor_port
        if mode=="tor":
            if not tor_port:
                raise RuntimeError("Tor is selected but no Tor SOCKS port is available.")
            proxy=f"socks5h://127.0.0.1:{tor_port}"
            self.proxies.update({"http":proxy,"https":proxy})
        elif mode=="privacy":
            # Privacy mode is intentionally conservative: no provider-specific
            # tracking headers/cookies are added. Tor can be selected explicitly.
            pass
