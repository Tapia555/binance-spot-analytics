import hmac
import hashlib
import time
import requests

api_key = "v2VmTholflNNj5B8Gn"
api_secret = "wCLXOCfM84BJGBcvWZUywOljhKg9hW1UNFy7"
timestamp = str(int(time.time() * 1000))
recv_window = "5000"

# Для GET запроса без body - query_string пустой!
sign_str = f"{timestamp}{api_key}{recv_window}"
signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()

print(f"Timestamp: {timestamp}")
print(f"Sign str: {sign_str}")
print(f"Signature: {signature}")

url = "https://api-testnet.bybit.com/v5/account/wallet-balance"
headers = {
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-SIGN": signature,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": recv_window,
}
# Параметры в URL, но НЕ в подписи!
resp = requests.get(url, params={"accountType": "UNIFIED"}, headers=headers)
print(f"Response: {resp.json()}")
