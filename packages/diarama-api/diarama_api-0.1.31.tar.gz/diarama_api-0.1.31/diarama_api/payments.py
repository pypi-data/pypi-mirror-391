class Payments:
    def __init__(self, client):
        self.client = client

    def list(self, player_id=None):
        params = {"player_id": player_id} if player_id else None
        return self.client._get("/payments/", params=params)

    def create(self, player_id, game_id, price, platform_id=None, paystatus_id=None):
        data = {"player_id": player_id, "game_id": game_id, "price": price}
        if platform_id: data["platform_id"] = platform_id
        if paystatus_id: data["paystatus_id"] = paystatus_id
        return self.client._post("/payments/", data)

    def update_status(self, payment_id, paystatus_id):
        return self.client._put(f"/payments/{payment_id}", {"paystatus_id": paystatus_id})
