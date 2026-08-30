import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

api_key = "v2VmTholflNNj5B8Gn"
api_secret = "wCLXOCfM84BJGBcvWZUywOljhKg9hW1UNFy7"
timestamp = str(int(time.time() * 1000))
recv_window = "5000"
params = {"accountType": "SPOT"}

query_string = urlencode(params)
sign_str = f"{timestamp}{api_key}{recv_window}{query_string}"
signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

print(f"Timestamp: {timestamp}")
print(f"Query string: {query_string}")
print(f"Sign str: {sign_str}")
print(f"Signature: {signature}")

url = "https://api-testnet.bybit.com/v5/account/wallet-balance"
headers = {
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-SIGN": signature,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": recv_window,
}
resp = requests.get(url, params=params, headers=headers)
print(f"Response: {resp.json()}")
