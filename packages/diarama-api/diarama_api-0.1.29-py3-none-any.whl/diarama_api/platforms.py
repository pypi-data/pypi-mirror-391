# api/platforms.py
class Platforms:
    def __init__(self, client):
        self.client = client

    def list(self):
        """Получить список всех платформ"""
        return self.client._get("/platforms/")

    def get(self, platform_id):
        """Получить платформу по ID"""
        return self.client._get(f"/platforms/{platform_id}")

    def create(self, name):
        """Создать новую платформу"""
        data = {"name": name}
        return self.client._post("/platforms/", data)

    def update(self, platform_id, name):
        """Обновить платформу"""
        data = {"name": name}
        return self.client._put(f"/platforms/{platform_id}", data)

    def delete(self, platform_id):
        """Удалить платформу"""
        return self.client._delete(f"/platforms/{platform_id}")
