from actions import register_action
import requests

HOMEASSISTANT_URL = "http://homeassistant.local:8123"
HOMEASSISTANT_TOKEN = ""

headers = {
    "Authorization": f"Bearer {HOMEASSISTANT_TOKEN}",
    "Content-Type": "application/json"
}

@register_action("spotify_play")
def spotify_play(entity_id):
    """Resume Spotify playback."""
    payload = {"entity_id": entity_id}
    r = requests.post(
        f"{HOMEASSISTANT_URL}/api/services/media_player/media_play",
        headers=headers,
        json=payload
    )
    print(r.text if not r.ok else f"Spotify resumed on {entity_id}")

@register_action("spotify_pause")
def spotify_pause(entity_id):
    """Pause Spotify playback."""
    payload = {"entity_id": entity_id}
    r = requests.post(
        f"{HOMEASSISTANT_URL}/api/services/media_player/media_pause",
        headers=headers,
        json=payload
    )
    print(r.text if not r.ok else f"Spotify paused on {entity_id}")

@register_action("change_light_color")
def change_color(entity_id, RGB):
    """Change the color of a light in Home Assistant."""

    payload = {
        "entity_id": entity_id,
        "rgb_color": list(RGB)
    }
    response = requests.post(
        f"{HOMEASSISTANT_URL}/api/services/light/turn_on",
        headers=headers,
        json=payload
    )
    if response.ok:
        print(f"Light color changed to RGB {RGB} for {entity_id}")
    else:
        print(f"Error {response.status_code}: {response.text}")



