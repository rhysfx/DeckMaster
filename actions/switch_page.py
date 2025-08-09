from actions import register_action

@register_action("switch_page")
def handle_switch_page(param, app_instance=None):
    if app_instance is None:
        print("[Action:switch_page] Error: No app instance provided")
        return

    try:
        param_str = str(param)
        if param_str.lower() == "home":
            target_page = 1
        else:
            target_page = int(param)

        if target_page < 1:
            print(f"[Action:switch_page] Invalid page number: {target_page}. Must be >= 1")
            return

        print(f"[Action:switch_page] Switching from page {app_instance.current_page} to page {target_page}")
        app_instance.current_page = target_page

        app_instance._asyncio_fetch_and_update()

    except ValueError:
        print(f"[Action:switch_page] Invalid page parameter: '{param}'. Must be a number or 'home'")
    except Exception as e:
        print(f"[Action:switch_page] Unexpected error: {e}")
