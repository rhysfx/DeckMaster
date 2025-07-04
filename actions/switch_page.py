from actions import register_action

@register_action("switch_page")
def handle_switch_page(param, app_instance=None):
    """
    Switch to a specific page number.
    
    Args:
        param: Page number as string (e.g., "1", "2", "3")
        app_instance: DeckMasterApp instance (passed automatically)
    
    Usage in database:
        action column: "switch_page:2" (switches to page 2)
        action column: "switch_page:home" (switches to page 1, treating "home" as page 1)
    """
    if app_instance is None:
        print("[Action:switch_page] Error: No app instance provided")
        return
    
    try:
        # Handle special case for "home" -> page 1
        if param.lower() == "home":
            target_page = 1
        else:
            target_page = int(param)
        
        # Validate page number
        if target_page < 1:
            print(f"[Action:switch_page] Invalid page number: {target_page}. Must be >= 1")
            return
        
        print(f"[Action:switch_page] Switching from page {app_instance.current_page} to page {target_page}")
        app_instance.current_page = target_page
        
        # Trigger immediate UI update
        app_instance._asyncio_fetch_and_update()
        
    except ValueError:
        print(f"[Action:switch_page] Invalid page parameter: '{param}'. Must be a number or 'home'")
    except Exception as e:
        print(f"[Action:switch_page] Unexpected error: {e}")