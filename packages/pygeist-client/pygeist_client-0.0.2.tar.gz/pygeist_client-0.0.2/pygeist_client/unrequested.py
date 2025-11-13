class Unrequested:
    def __init__(self, headers: str, body: str, raw: str) -> None:
        self.raw = raw
        self.headers = headers
        self.body = body
