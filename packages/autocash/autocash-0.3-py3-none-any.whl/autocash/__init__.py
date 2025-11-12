import requests
import base64

class AutoCash:
    def __init__(self, user_id, panel_id):
        self.link = "https://cash.darksidehost.com/"
        self.user_id = user_id
        self.panel_id = panel_id

    def create_payment_link(self, extra=None):
        link = f"{self.link}page/vfcash?id={self.panel_id}"
        if extra:
            link += f"&extra={extra}"
        return link

    def create_payeer_payment_link(self, amount, callback_link, extra=None):
        link = f"{self.link}page/payeer?id={self.user_id}&a={amount}&c={requests.utils.quote(callback_link)}"
        if extra:
            link += f"&o={extra}"
        return link
    
    def create_okx_payment_link(self, amount, extra=None):
        link = f"{self.link}page/okx?id={self.panel_id}&amount={amount}"
        if extra:
            link += f"&extra={extra}"
        return link
    
    def create_binance_payment_link(self, amount, extra=None):
        link = f"{self.link}page/binance?id={self.panel_id}&amount={amount}"
        if extra:
            link += f"&extra={extra}"
        return link

    def get_payment_status(self, key):
        link = f"{self.link}page/vfcash?id={self.panel_id}&sms_key={key}"
        response = requests.post(link)
        return response.json()

    def check_payment(self, phone, amount, extra=None):
        link = self.create_payment_link(extra)
        data = {"phone": phone, "amount": amount, "api": True, "to": "callback"}
        response = requests.post(link, data=data)
        return response.json()
    
    def check_okx_payment(self, amount, txid, extra=None):
        link = self.create_okx_payment_link(amount, extra)
        data = {"txid": txid, "amount": amount, "api": True, "to": "callback"}
        response = requests.post(link, data=data)
        return response.json()
    
    def check_binance_payment(self, amount, txid, extra=None):
        link = self.create_binance_payment_link(amount, extra)
        data = {"txid": txid, "amount": amount, "api": True, "to": "callback"}
        response = requests.post(link, data=data)
        return response.json()

    def get_info(self):
        link = f"{self.link}rates/socpanel?id={self.panel_id}"
        response = requests.get(link)
        return response.json()

    def redirect(self, link):
        encoded_link = base64.b64encode(link.encode()).decode()
        return f"{self.link}redirect?l={encoded_link}"
