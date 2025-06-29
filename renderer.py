import asyncio
import hashlib
import json
import os
import tempfile
import tkinter as tk
import urllib.request
from typing import List, Tuple, Optional

import aiomysql
import pyautogui
from dotenv import load_dotenv

from actions import load_actions, action_handlers

# Configuration Constants
class Config:
    """Application configuration constants."""
    # UI styling
    BG_COLOR = "#1e1e1e"
    BUTTON_ACTIVE_BG = "#007acc"
    NAV_BUTTON_BG = "#2d2d30"
    
    # Layout constants
    OFFSET_BUTTON_V = 7
    OFFSET_X = 20
    BUTTON_WIDTH = 121
    BUTTON_HEIGHT = 128
    
    # Navigation button positions
    NAV_LEFT_X = 985
    NAV_RIGHT_X = 1153
    NAV_Y = 662
    
    # Update interval (milliseconds)
    UPDATE_INTERVAL = 500
    
    # PyAutoGUI cursor position after button click
    CURSOR_PARK_X = 1900
    CURSOR_PARK_Y = 1060


class DeckMasterApp:
    """Main application class for DeckMaster Control Panel."""
    
    def __init__(self):
        """Initialize the application."""
        self.current_page = 1
        self.created_buttons = []
        self.root = None
        self.arrow_images = None
        
        # Disable PyAutoGUI failsafe
        pyautogui.FAILSAFE = False
        
        # Load environment variables
        load_dotenv()
        
        # Load action handlers
        self._load_action_handlers()
    
    def _load_action_handlers(self) -> None:
        """Load action handlers from actions module."""
        try:
            load_actions()
            print("Actions loaded successfully")
            print(f"Available action handlers: {list(action_handlers.keys())}")
        except Exception as e:
            print(f"Error loading actions: {e}")
    
    def execute_action(self, action: str) -> None:
        """
        Execute an action command.
        
        Args:
            action: Action string in format 'command:parameter'
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
                # Check if handler accepts app instance as second parameter
                import inspect
                sig = inspect.signature(handler)
                if len(sig.parameters) > 1:
                    handler(param, self)
                else:
                    handler(param)
            except Exception as e:
                print(f"Error executing action {command}: {e}")
        else:
            print(f"No handler for action '{command}'")
    
    def _create_button_click_handler(self, label: str, action: Optional[str]):
        """Create a button click handler function."""
        def on_button_click():
            if action:
                print(f"Executing action for button '{label}': {action}")
                self.execute_action(action)
            else:
                print(f"Button '{label}' clicked but no action defined")
            
            # Park cursor in corner
            pyautogui.moveTo(Config.CURSOR_PARK_X, Config.CURSOR_PARK_Y)
        
        return on_button_click
    
    def _load_image(self, image_path: str) -> Optional[tk.PhotoImage]:
        """
        Load an image from local file or URL.
        
        Args:
            image_path: Path to local file or URL
            
        Returns:
            PhotoImage object or None if loading failed
        """
        if not image_path:
            return None
            
        try:
            if image_path.startswith(("http://", "https://")):
                # Download remote image to temporary file
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                urllib.request.urlretrieve(image_path, tmp_file.name)
                return tk.PhotoImage(file=tmp_file.name)
            elif os.path.isfile(image_path):
                return tk.PhotoImage(file=image_path)
        except Exception as e:
            print(f"Failed to load image '{image_path}': {e}")
        
        return None
    
    def create_button(self, label: str, x: int, y: int, bg: str, fg: str, 
                     action: Optional[str] = None, image_path: Optional[str] = None) -> tk.Button:
        """
        Create a button widget.
        
        Args:
            label: Button text label
            x, y: Button position
            bg, fg: Background and foreground colors
            action: Action to execute on click
            image_path: Path to button image
            
        Returns:
            Created button widget
        """
        click_handler = self._create_button_click_handler(label, action)
        photo = self._load_image(image_path)
        
        if photo:
            button = tk.Button(
                self.root,
                image=photo,
                bg=bg,
                fg=fg,
                activebackground=Config.BUTTON_ACTIVE_BG,
                command=click_handler,
                relief="raised",
                bd=2
            )
            button.image = photo  # Prevent garbage collection
        else:
            button = tk.Button(
                self.root,
                text=label,
                bg=bg,
                fg=fg,
                activebackground=Config.BUTTON_ACTIVE_BG,
                command=click_handler,
                font=("Arial", 10, "bold"),
                relief="raised",
                bd=2
            )

        button.place(
            x=x + Config.OFFSET_X,
            y=y + Config.OFFSET_BUTTON_V,
            width=Config.BUTTON_WIDTH,
            height=Config.BUTTON_HEIGHT
        )

        return button
    
    async def fetch_buttons(self, page: int = 1) -> List[Tuple]:
        """
        Fetch button data from database.
        
        Args:
            page: Page number to fetch
            
        Returns:
            List of button data tuples
        """
        try:
            conn = await aiomysql.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                db=os.getenv('DB_NAME')
            )

            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT label, pos_x, pos_y, color_bg, color_fg, action, image_path
                    FROM buttons 
                    WHERE page = %s
                """, (page,))
                result = await cur.fetchall()

            conn.close()
            return result

        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def _hash_buttons_data(self, buttons_data: List[Tuple]) -> str:
        """
        Generate hash of button data for change detection.
        
        Args:
            buttons_data: List of button data tuples
            
        Returns:
            MD5 hash string
        """
        serialized = json.dumps(buttons_data, sort_keys=True)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    def update_buttons_if_changed(self, buttons_data: List[Tuple]) -> None:
        """
        Update buttons if data has changed.
        
        Args:
            buttons_data: List of button data tuples
        """
        new_hash = self._hash_buttons_data(buttons_data)
        
        if not hasattr(self.root, 'last_buttons_hash'):
            self.root.last_buttons_hash = None
        
        if new_hash != self.root.last_buttons_hash:
            self.root.last_buttons_hash = new_hash
            
            # Remove old buttons
            for btn in self.created_buttons:
                btn.destroy()
            self.created_buttons.clear()
            
            # Create new buttons
            for button_data in buttons_data:
                btn = self._create_button_from_data(button_data)
                if btn:
                    self.created_buttons.append(btn)
    
    def _create_button_from_data(self, button_data: Tuple) -> Optional[tk.Button]:
        """
        Create button from database row data.
        
        Args:
            button_data: Tuple containing button data
            
        Returns:
            Created button or None
        """
        if len(button_data) >= 7:
            label, x, y, bg, fg, action, image_path = button_data
            return self.create_button(label, x, y, bg, fg, action, image_path)
        elif len(button_data) == 6:
            label, x, y, bg, fg, action = button_data
            return self.create_button(label, x, y, bg, fg, action)
        elif len(button_data) >= 5:
            label, x, y, bg, fg = button_data[:5]
            return self.create_button(label, x, y, bg, fg)
        else:
            print(f"Invalid button data: {button_data}")
            return None
    
    def _create_navigation_handlers(self):
        """Create navigation button click handlers."""
        def next_page():
            self.current_page += 1
            self.root.after(0, self._asyncio_fetch_and_update)
            pyautogui.moveTo(Config.CURSOR_PARK_X, Config.CURSOR_PARK_Y)
        
        def previous_page():
            if self.current_page > 1:
                self.current_page -= 1
                self.root.after(0, self._asyncio_fetch_and_update)
                pyautogui.moveTo(Config.CURSOR_PARK_X, Config.CURSOR_PARK_Y)
        
        return previous_page, next_page
    
    def add_navigation_buttons(self) -> None:
        """Add navigation buttons to the interface."""
        try:
            arrow_left = tk.PhotoImage(file="arrow_left.png")
            arrow_right = tk.PhotoImage(file="arrow_right.png")
        except Exception as e:
            print(f"Error loading arrow images: {e}")
            return
        
        # Store references to prevent garbage collection
        self.arrow_images = (arrow_left, arrow_right)
        
        previous_page, next_page = self._create_navigation_handlers()
        
        # Left arrow button
        tk.Button(
            self.root,
            image=arrow_left,
            command=previous_page,
            bg=Config.NAV_BUTTON_BG,
            activebackground=Config.BUTTON_ACTIVE_BG,
            borderwidth=0,
            highlightthickness=0
        ).place(
            x=Config.NAV_LEFT_X + Config.OFFSET_X,
            y=Config.NAV_Y + Config.OFFSET_BUTTON_V,
            width=Config.BUTTON_WIDTH,
            height=Config.BUTTON_HEIGHT
        )
        
        # Right arrow button
        tk.Button(
            self.root,
            image=arrow_right,
            command=next_page,
            bg=Config.NAV_BUTTON_BG,
            activebackground=Config.BUTTON_ACTIVE_BG,
            borderwidth=0,
            highlightthickness=0
        ).place(
            x=Config.NAV_RIGHT_X + Config.OFFSET_X,
            y=Config.NAV_Y + Config.OFFSET_BUTTON_V,
            width=Config.BUTTON_WIDTH,
            height=Config.BUTTON_HEIGHT
        )
    
    def _asyncio_fetch_and_update(self) -> None:
        """
        Fetch buttons from database and update UI.
        Called periodically for live updates.
        """
        async def fetch_task():
            return await self.fetch_buttons(self.current_page)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            buttons_data = loop.run_until_complete(fetch_task())
            loop.close()
            
            self.update_buttons_if_changed(buttons_data)
        except Exception as e:
            print(f"Error in _asyncio_fetch_and_update: {e}")
        
        # Schedule next update
        self.root.after(Config.UPDATE_INTERVAL, self._asyncio_fetch_and_update)
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<q>", lambda e: self.root.quit())
        self.root.bind("<Q>", lambda e: self.root.quit())
    
    def run(self) -> None:
        """Run the application."""
        self.root = tk.Tk()
        self.root.title("DeckMaster Control Panel")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=Config.BG_COLOR, cursor="none")
        
        self._setup_keyboard_shortcuts()
        self.add_navigation_buttons()
        self._asyncio_fetch_and_update()  # Start live updating loop
        
        self.root.mainloop()

def main():
    """Main entry point."""
    app = DeckMasterApp()
    app.run()

if __name__ == "__main__":
    main()