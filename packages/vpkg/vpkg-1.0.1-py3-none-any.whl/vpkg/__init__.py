import requests


class VaultClient:
    def __init__(self, env_key: str, product_name: str = None, base_url: str = "http://api.dallasformularacing.com/v1/vault", api_key: str = None):
        self.base_url = base_url
        self.env_key = env_key
        self.product_name = product_name
        self.api_key = api_key
        self.headers = {
            'x-env-key': self.env_key,
            'x-product-name': self.product_name,
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        

    def fetch_vault(self, product_name: str = None) -> dict:
        headers = self.headers.copy()
        if product_name:
            headers['x-product-name'] = product_name
            
        response = requests.get(self.base_url + "/decrypt_vault", headers=headers)
        
        if response.status_code == 200:
            return response.json().get('data', '')
        else:
            raise Exception(f"Failed to fetch vault {headers['x-product-name']} - Status code: {response.status_code}, Response: {response.text}")


    def fetch_secret(self, secret_name: str, product_name: str = None) -> str:
        headers = self.headers.copy()
        if product_name:
            headers['x-product-name'] = product_name
            
        headers['x-secret-name'] = secret_name
        response = requests.get(self.base_url + f"/decrypt_secret", headers=headers)
        
        if response.status_code == 200:
            return response.json().get('data', '')
        else:
            raise Exception(f"Failed to fetch secret {secret_name} - Status code: {response.status_code}, Response: {response.text}")


    def fetch_metadata(self) -> dict:
        headers = self.headers.copy()

        response = requests.get(self.base_url + "/metadata", headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch vault metadata - Status code: {response.status_code}, Response: {response.text}")
        
        
    def fetch_products(self) -> list:
        response = requests.get(self.base_url + "/list_products", headers=self.headers)

        if response.status_code == 200:
            return response.json().get('products', [])
        else:
            raise Exception(f"Failed to fetch products - Status code: {response.status_code}, Response: {response.text}")


    def create_vault(self, vault_data: dict = None, product_name: str = None) -> str:
        headers = self.headers.copy()
        if product_name:
            headers['x-product-name'] = product_name
            
        post_data = {}
        if vault_data:
            post_data = {
                headers['x-product-name']: vault_data
            }

        response = requests.post(self.base_url + "/create_vault", headers=headers, json=post_data)

        if response.status_code == 201:
            return response.json()['x-env-key']
        else:
            raise Exception(f"Failed to create vault - Status code: {response.status_code}, Response: {response.text}")


    def bulk_update_secrets(self, secrets: dict, product_name: str = None) -> None:
        headers = self.headers.copy()
        if product_name:
            headers['x-product-name'] = product_name
        
        post_data = {
            headers['x-product-name']: secrets
        }

        response = requests.post(self.base_url + "/update_vault", headers=headers, json=post_data)

        if response.status_code != 200:
            raise Exception(f"Failed to bulk update secrets - Status code: {response.status_code}, Response: {response.text}")


    def update_secret(self, secret_name: str, secret_value: str, product_name: str = None) -> None:
        return self.bulk_update_secrets({secret_name: secret_value}, product_name=product_name)
    
    
    def create_secret(self, secret_name: str, secret_value: str, product_name: str = None) -> None:
        return self.bulk_update_secrets({secret_name: secret_value}, product_name=product_name)
    
    
    def delete_secret(self, secret_name: str, product_name: str = None) -> None:
        return self.bulk_update_secrets({secret_name: None}, product_name=product_name)