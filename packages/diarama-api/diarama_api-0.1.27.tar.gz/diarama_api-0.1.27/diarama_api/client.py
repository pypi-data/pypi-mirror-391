import json
import requests

class DiaramaAPIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.diaramastudio.ru"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json; charset=utf-8"
        }

    def _get(self, endpoint, params=None):
        r = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, params=params)
        r.raise_for_status()

        try:
            return r.json()
        except ValueError:
            content_type = r.headers.get("Content-Type", "")
            if "text" in content_type or "json" in content_type or "utf" in content_type:
                return {"content": r.text}
            else:
                return r.content


    def _post(self, endpoint, data=None, files=None):
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()

        if files:
            headers.pop("Content-Type", None)
            r = requests.post(url, headers=headers, files=files)
        else:
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
            r = requests.post(url, headers=headers, data=json_data)

        r.raise_for_status()
        return r.json()

    def _put(self, endpoint, data=None):
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        r = requests.put(f"{self.base_url}{endpoint}", headers=self.headers, data=json_data)
        r.raise_for_status()
        return r.json()

    def _delete(self, endpoint):
        """DELETE запрос"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.delete(url, headers=headers)
        if response.status_code in [200, 204]:
            try:
                return response.json()
            except:
                return {"success": True}
        else:
            response.raise_for_status()
