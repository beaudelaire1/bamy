import base64, time, requests
from django.conf import settings

PAYPAL_BASE = "https://api-m.sandbox.paypal.com"
_token = {"value": None, "exp": 0}

def _creds():
    return settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET

def get_access_token():
    now = int(time.time())
    if _token["value"] and _token["exp"] - 30 > now:
        return _token["value"]
    cid, sec = _creds()
    auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
    r = requests.post(
        f"{PAYPAL_BASE}/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"},
        timeout=20
    )
    r.raise_for_status()
    data = r.json()
    _token["value"] = data["access_token"]
    _token["exp"]   = now + int(data.get("expires_in", 300))
    return _token["value"]

def create_order(amount, currency="EUR"):
    token = get_access_token()
    r = requests.post(
        f"{PAYPAL_BASE}/v2/checkout/orders",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"intent":"CAPTURE","purchase_units":[{"amount":{"currency_code":currency,"value":amount}}]},
        timeout=20
    )
    r.raise_for_status(); return r.json()

def capture_order(order_id):
    token = get_access_token()
    r = requests.post(
        f"{PAYPAL_BASE}/v2/checkout/orders/{order_id}/capture",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=20
    )
    r.raise_for_status(); return r.json()
