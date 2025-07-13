from obswebsocket import obsws, requests
from actions import register_action

host = "localhost"  # Change to your OBS WebSocket host if different
port = 4455         # Default OBS WebSocket port
password = ""       # Set your OBS WebSocket password if you have one

ws = None
connected = False

if host and port and password:
    try:
        ws = obsws(host, port, password)
        ws.connect()
        version_info = ws.call(requests.GetVersion())
        connected = True
        print(f"[OBS] Connected to OBS WebSocket - Version: {version_info.datain}")
    except Exception as e:
        print(f"[OBS] Connection failed: {e}")
else:
    print("[OBS] Host or port not set. Skipping OBS WebSocket connection.")

@register_action("change_scene")
def change_scene(scene_name):
    if not connected:
        print("[Action:change_scene] Not connected to OBS.")
        return
    try:
        response = ws.call(requests.SetCurrentProgramScene(sceneName=scene_name))
        print(f"[Action:change_scene] Changed to scene: {scene_name} - Response: {response}")
    except Exception as e:
        print(f"[Action:change_scene] Failed to change scene to {scene_name}: {e}")

@register_action("start_recording")
def start_recording():
    if not connected:
        print("[Action:start_recording] Not connected to OBS.")
        return
    try:
        ws.call(requests.StartRecord())
        print("[Action:start_recording] Recording started.")
    except Exception as e:
        print(f"[Action:start_recording] Failed to start recording: {e}")

@register_action("stop_recording")
def stop_recording():
    if not connected:
        print("[Action:stop_recording] Not connected to OBS.")
        return
    try:
        ws.call(requests.StopRecord())
        print("[Action:stop_recording] Recording stopped.")
    except Exception as e:
        print(f"[Action:stop_recording] Failed to stop recording: {e}")

@register_action("toggle_studio_mode")
def toggle_studio_mode():
    if not connected:
        print("[Action:toggle_studio_mode] Not connected to OBS.")
        return
    try:
        status_response = ws.call(requests.GetStudioModeEnabled())
        current_status = status_response.datain.get('studioModeEnabled', False)
        ws.call(requests.SetStudioModeEnabled(studioModeEnabled=not current_status))
        print(f"[Action:toggle_studio_mode] Studio mode {'enabled' if not current_status else 'disabled'}.")
    except Exception as e:
        print(f"[Action:toggle_studio_mode] Failed to toggle studio mode: {e}")

def disconnect():
    if not connected or not ws:
        print("[OBS] Not connected, nothing to disconnect.")
        return
    try:
        ws.disconnect()
        print("[OBS] Disconnected from OBS WebSocket")
    except Exception as e:
        print(f"[OBS] Error disconnecting: {e}")
