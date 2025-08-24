import json
import logging

class AuthManager:
    def __init__(self, auth_file="Authentication.json"):
        self.log = logging.getLogger(self.__class__.__name__)
        self._load_auth(auth_file)

    def _load_auth(self, auth_file: str):
        with open(auth_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ACCESS_TOKEN = data.get("access_token")
        self.CLIENT_ID = data.get("client_id")
        self.CSRF = data.get("csrf")

        if not self.ACCESS_TOKEN:
            raise ValueError("Missing 'access_token' in Authentication.json")

        self.auth_header = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }
        self.cookie_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US",
            "x-requested-with": "XMLHttpRequest",
            "x-udemy-cache-logged-in": "1",
        }
        self.cookies = {"access_token": self.ACCESS_TOKEN}

        self.log.info("Authentication headers initialized")
