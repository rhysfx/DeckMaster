from actions import register_action

@register_action("print")
def handle_print(param):
    print(f"[Action:print] {param}")