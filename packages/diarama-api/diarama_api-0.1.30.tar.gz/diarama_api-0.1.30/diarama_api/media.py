class Media:
    def __init__(self, client):
        self.client = client

    def create_image(self, url, alt_text=None):
        data = {"url": url}
        if alt_text:
            data["alt_text"] = alt_text
        return self.client._post("/media/images", data)

    def create_avatar(self, image_id):
        return self.client._post("/media/avatars", {"image_id": image_id})

    def create_banner(self, image_id):
        return self.client._post("/media/banners", {"image_id": image_id})

    def upload(self, file_obj):
        """Загрузить файл как медиа"""
        # Если пришёл Flask FileStorage
        if hasattr(file_obj, "stream") and hasattr(file_obj, "filename"):
            file_tuple = (file_obj.filename, file_obj.stream, file_obj.mimetype)
            files = {'file': file_tuple}
        else:
            # обычный open('file.png', 'rb')
            files = {'file': file_obj}
        return self.client._post("/media/upload", files=files)

  # ------------------------
    # Работа с Media
    # ------------------------
    def create_media(self, avatar_id=None, banner_id=None, image_id=None):
        """Создать объект Media с привязкой к avatar, banner, image"""
        data = {}
        if avatar_id:
            data["avatar_id"] = avatar_id
        if banner_id:
            data["banner_id"] = banner_id
        if image_id:
            data["image_id"] = image_id
        return self.client._post("/media", data)

    def get_media(self, media_id):
        """Получить объект Media по media_id"""
        return self.client._get(f"/media/{media_id}")

    def update_media(self, media_id, avatar_id=None, banner_id=None, image_id=None):
        """Обновить существующий Media"""
        data = {}
        if avatar_id is not None:
            data["avatar_id"] = avatar_id
        if banner_id is not None:
            data["banner_id"] = banner_id
        if image_id is not None:
            data["image_id"] = image_id
        return self.client._put(f"/media/{media_id}", data)

    def delete_media(self, media_id):
        """Удалить объект Media"""
        return self.client._delete(f"/media/{media_id}")