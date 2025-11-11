class Shop:
    def __init__(self, client):
        self.client = client

    # -------------------- CATEGORIES --------------------
    def list_categories(self):
        return self.client._get("/shop/categories")

    def get_category(self, category_id: int):
        return self.client._get(f"/shop/categories/{category_id}")

    def create_category(self, name: str):
        data = {"name": name}
        return self.client._post("/shop/categories", data)

    def update_category(self, category_id: int, name: str):
        data = {"name": name}
        return self.client._put(f"/shop/categories/{category_id}", data)

    def delete_category(self, category_id: int):
        return self.client._delete(f"/shop/categories/{category_id}")

    # -------------------- PRODUCTS --------------------
    def list_products(self):
        return self.client._get("/shop/products")

    def get_product(self, product_id: int):
        return self.client._get(f"/shop/products/{product_id}")

    def create_product(
        self, title: str, short_description: str, price: float, product_type: str,
        full_description: str = None, requirements: str = None,
        seller_label: str = None, allow_multiple_purchase: bool = False,
        media_id: int = None
    ):
        data = {
            "title": title,
            "short_description": short_description,
            "price": price,
            "product_type": product_type,
            "full_description": full_description,
            "requirements": requirements,
            "seller_label": seller_label,
            "allow_multiple_purchase": allow_multiple_purchase,
            "media_id": media_id
        }
        return self.client._post("/shop/products", data)

    def update_product(self, product_id: int, **kwargs):
        allowed = [
            "title", "short_description", "full_description", "price", 
            "product_type", "requirements", "seller_label", "allow_multiple_purchase", "media_id"
        ]
        data = {k: v for k, v in kwargs.items() if k in allowed}
        return self.client._put(f"/shop/products/{product_id}", data)

    def delete_product(self, product_id: int):
        return self.client._delete(f"/shop/products/{product_id}")

    # -------------------- USER PURCHASES --------------------
    def list_user_purchases(self):
        return self.client._get("/shop/user-purchases")

    def create_user_purchase(self, player_id: int, product_id: int, purchase_price: float, license_key: str = None):
        data = {
            "player_id": player_id,
            "product_id": product_id,
            "purchase_price": purchase_price
        }
        if license_key:
            data["license_key"] = license_key
        return self.client._post("/shop/user-purchases", data)
