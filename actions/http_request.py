import requests
from actions import register_action

@register_action("request")
def handle_request(url):
    try:
        response = requests.get(url)
        print(f"[Action:request] Requested {url} - Status code: {response.status_code}")
    except Exception as e:
        print(f"[Action:request] Failed to request {url}: {e}")