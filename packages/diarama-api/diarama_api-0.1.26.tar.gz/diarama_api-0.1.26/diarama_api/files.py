class Files:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client._get("/files")

    def download(self, filename):
        return self.client._get(f"/files/get/{filename}")

    def upload(self, file_obj, filename):
        files = {'file': (filename, file_obj)}
        return self.client._post("/files/upload", files=files)

    def edit(self, filename, content):
        data = {"content": content}
        return self.client._put(f"/files/edit/{filename}", json=data)

    def delete(self, filename):
        """Удаление файла"""
        return self.client._delete(f"/files/delete/{filename}")