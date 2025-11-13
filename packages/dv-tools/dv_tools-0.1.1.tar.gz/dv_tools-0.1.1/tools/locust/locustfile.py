from locust import HttpUser, task, between


class SaleCreatingUser(HttpUser):
    wait_time = between(1, 5)

    @task(10)
    def create_product(self):
        self.client.post(
            "/api/product/create",
            json=
            {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "name": "producto",
                    "default_code": "1123",
                    "list_price": 12.0,
                    "standard_price": 14.7
                }
            }
        )

    @task(10)
    def create_sale(self):
        self.client.post(
            "/api/sale_order/create",
            json=
            {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "name": "prueba",
                    "partner_id": 1,
                    "product_id": 1,
                    "product_uom_qty": 2,
                    "price_unit": 12.23
                }
            }
        )
