class Players:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/players/")

    def get_by_username(self, username: str):
        return self.client._get(f"/players/{username}")

    def get(self, player_id: int):
        return self.client._get(f"/players/{player_id}")

    def create(self, username, password, email, role_id=None, avatar_id=None):
        data = {"username": username, "password": password, "email": email}
        if role_id: data["role_id"] = role_id
        if avatar_id: data["avatar_id"] = avatar_id
        return self.client._post("/players/", data)

    def login(self, username, password):
        data = {"username": username, "password": password}
        return self.client._post("/players/login", data)

    def update(self, player_id, **kwargs):
        allowed = ["email", "banned", "role_id", "avatar_id"]
        data = {k: v for k, v in kwargs.items() if k in allowed}
        return self.client._put(f"/players/{player_id}", data)

    def delete(self, player_id):
        return self.client._delete(f"/players/{player_id}")
