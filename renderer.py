import tkinter as tk
import asyncio
import aiomysql
import os
from dotenv import load_dotenv
from actions import load_actions, action_handlers

# UI styling constants
BG_COLOR = "#1e1e1e"
BUTTON_ACTIVE_BG = "#007acc"
OFFSET_BUTTON_V = 7
OFFSET_X = 20
BUTTON_WIDTH = 121
BUTTON_HEIGHT = 128

load_dotenv()


def execute_action(action):
    """Execute an action using the registered action handlers.
    
    Args:
        action (str): Action string in format 'command:parameter'
    """
    if not action:
        print("No action defined")
        return
        
    if ':' not in action:
        print(f"Invalid action format: {action}")
        return
        
    command, param = action.split(':', 1)
    handler = action_handlers.get(command)
    
    if handler:
        try:
            handler(param)
        except Exception as e:
            print(f"Error executing action {command}: {e}")
    else:
        print(f"No handler for action '{command}'")


def create_button(root, label, x, y, bg, fg, action=None):
    """Create a styled button widget with optional action functionality.
    
    Args:
        root: Parent Tkinter window or frame
        label (str): Text displayed on the button
        x (int): Base x-coordinate for button placement
        y (int): Base y-coordinate for button placement
        bg (str): Background color (hex format)
        fg (str): Foreground/text color (hex format)
        action (str, optional): Action string to execute on click
    
    Returns:
        tk.Button: The created button widget
    """
    def on_button_click():
        if action:
            print(f"Executing action for button '{label}': {action}")
            execute_action(action)
        else:
            print(f"Button '{label}' clicked but no action defined")
    
    button = tk.Button(
        root,
        text=label,
        bg=bg,
        fg=fg,
        activebackground=BUTTON_ACTIVE_BG,
        command=on_button_click,
        font=("Arial", 10, "bold"),
        relief="raised",
        bd=2
    )
    
    button.place(
        x=x + OFFSET_X, 
        y=y + OFFSET_BUTTON_V, 
        width=BUTTON_WIDTH, 
        height=BUTTON_HEIGHT
    )
    
    return button


async def fetch_buttons():
    """Fetch button configuration data from MySQL database.
    
    Connects to the database and retrieves button properties including
    label, position, colors, and associated actions.
    
    Returns:
        list: List of tuples containing button data (label, pos_x, pos_y, color_bg, color_fg, action)
    """
    try:
        conn = await aiomysql.connect(
            host=os.getenv('DB_HOST'), 
            user=os.getenv('DB_USER'), 
            password=os.getenv('DB_PASS'), 
            db=os.getenv('DB_NAME')
        )
        
        async with conn.cursor() as cur:
            await cur.execute("SELECT label, pos_x, pos_y, color_bg, color_fg, action FROM buttons")
            result = await cur.fetchall()
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"Database error: {e}")
        return []


def run_asyncio_task(root, coro):
    """Execute async database operations and create UI buttons.
    
    Creates a new event loop to run the async coroutine, then uses the
    results to generate buttons on the Tkinter root window.
    
    Args:
        root: Tkinter root window for button placement
        coro: Async coroutine function (typically fetch_buttons)
    """
    try:
        # Create and run asyncio event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        buttons = loop.run_until_complete(coro)
        loop.close()

        # Create buttons from database data
        for button_data in buttons:
            if len(button_data) >= 6:
                label, x, y, bg, fg, action = button_data
                create_button(root, label, x, y, bg, fg, action)
            else:
                # Fallback for buttons without action column
                label, x, y, bg, fg = button_data[:5]
                create_button(root, label, x, y, bg, fg)
                
    except Exception as e:
        print(f"Error in run_asyncio_task: {e}")


def main():
    """Initialize the DeckMaster Control Panel application.
    
    Sets up the fullscreen Tkinter window, loads action handlers,
    fetches button data from database, and starts the main event loop.
    """
    # Load action handlers
    try:
        load_actions()
        print("Actions loaded successfully")
        print(f"Available action handlers: {list(action_handlers.keys())}")
    except Exception as e:
        print(f"Error loading actions: {e}")
    
    # Create and configure main window
    root = tk.Tk()
    root.title("DeckMaster Control Panel")
    root.attributes('-fullscreen', True)
    root.configure(bg=BG_COLOR)
    
    # Keyboard shortcuts
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.bind("<q>", lambda e: root.quit())
    root.bind("<Q>", lambda e: root.quit())

    # Load buttons from database and start UI
    run_asyncio_task(root, fetch_buttons())
    root.mainloop()


if __name__ == "__main__":
    main()