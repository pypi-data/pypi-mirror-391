class Auth:
    def __init__(self, client):
        self.client = client

    def create_key(self, name: str):
        return self.client._post("/auth/create-key", {"name": name})

    def list(self):
        return self.client._get("/auth/keys")

    def deactivate(self, key_id: int):
        return self.client._delete(f"/auth/keys/{key_id}")
