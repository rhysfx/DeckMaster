from obswebsocket import obsws, requests
from actions import register_action

host = "localhost" # Change to your OBS WebSocket host if different
port = 4455 # Default OBS WebSocket port
password = "" # Set your OBS WebSocket password if you have one

ws = obsws(host, port, password)
ws.connect()

@register_action("change_scene")
def change_scene(scene_name):
    try:
        response = ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        print(f"[Action:change_scene] Changed to scene: {scene_name} - Response: {response}")
    except Exception as e:
        print(f"[Action:change_scene] Failed to change scene to {scene_name}: {e}")

@register_action("start_recording")
def start_recording():
    try:
        ws.call(requests.StartRecord())
        print("[Action:start_recording] Recording started.")
    except Exception as e:
        print(f"[Action:start_recording] Failed to start recording: {e}")

@register_action("stop_recording")
def stop_recording():
    try:
        ws.call(requests.StopRecord())
        print("[Action:stop_recording] Recording stopped.")
    except Exception as e:
        print(f"[Action:stop_recording] Failed to stop recording: {e}")

@register_action("toggle_studio_mode")
def toggle_studio_mode():
    try:
        status_response = ws.call(requests.GetStudioModeEnabled())
        current_status = status_response.datain.get('studioModeEnabled', False)
        ws.call(requests.SetStudioModeEnabled(studioModeEnabled=not current_status))
        print(f"[Action:toggle_studio_mode] Studio mode {'enabled' if not current_status else 'disabled'}.")
    except Exception as e:
        print(f"[Action:toggle_studio_mode] Failed to toggle studio mode: {e}")

def disconnect():
    try:
        ws.disconnect()
        print("[OBS] Disconnected from OBS WebSocket")
    except Exception as e:
        print(f"[OBS] Error disconnecting: {e}")

try:
    version_info = ws.call(requests.GetVersion())
    print(f"[OBS] Connected to OBS WebSocket - Version: {version_info.datain}")
except Exception as e:
    print(f"[OBS] Connection failed: {e}")