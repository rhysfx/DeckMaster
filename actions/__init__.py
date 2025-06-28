import os
import importlib

action_handlers = {}

def register_action(name):
    def decorator(func):
        action_handlers[name] = func
        return func
    return decorator

def load_actions():
    actions_dir = os.path.dirname(__file__)
    for filename in os.listdir(actions_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"actions.{filename[:-3]}"
            importlib.import_module(module_name)
