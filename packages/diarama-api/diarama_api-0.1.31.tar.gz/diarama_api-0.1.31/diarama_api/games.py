class Games:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/games/")

    def get(self, game_id):
        return self.client._get(f"/games/{game_id}")

    def create(self, name, version, author, description, platform_id, media_id):
        data = {
            "name": name,
            "version": version,
            "author": author,
            "description": description,
            "platform_id": platform_id,
            "media_id": media_id
        }
        return self.client._post("/games/", data)

    def update(self, game_id, **kwargs):
        allowed = ["name", "version", "author", "description", "platforms", "media_id"]
        data = {k: v for k, v in kwargs.items() if k in allowed}
        return self.client._put(f"/games/{game_id}", data)

    def delete(self, game_id):
        return self.client._delete(f"/games/{game_id}")
