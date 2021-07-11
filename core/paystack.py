from jtec.settings import PAYSTACK_SECRET_KEY
import requests
import json

class Paystack:
    PAYSTACK_SECRET_KEY = PAYSTACK_SECRET_KEY
    base_url = 'https://api.paystack.co'

    def verify_payment(self, ref, *args, **kwargs):
        path = f'/transaction/verify/{ref}'

        headers = {
            'Authorization': f"Bearer {self.PAYSTACK_SECRET_KEY}",
            'content-type': 'application/json'
        }
        url = f"{self.base_url}{path}"
        response = requests.get(url, headers=headers)

        print(response.content)
        print(response.content)
        print(response.content)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'] , response_data['data']
        response_data = response.json() 
        return response_data["status"], response_data["messages"]

