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
