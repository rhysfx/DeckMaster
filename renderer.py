import asyncio
import hashlib
import json
import os
import tempfile
import urllib.request
from typing import List, Tuple, Optional, Dict

import aiomysql
import pyautogui
from dotenv import load_dotenv
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut, QCursor
from PySide6.QtCore import Qt, QTimer, QUrl

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
    
    # Web browser dimensions
    WEB_HEIGHT = 300
    WEB_MARGIN_TOP = 0
    
    # Navigation button positions
    NAV_LEFT_X = 985
    NAV_RIGHT_X = 1153
    NAV_Y = 662
    
    # Update interval (milliseconds)
    UPDATE_INTERVAL = 500
    
    # PyAutoGUI cursor position after button click
    CURSOR_PARK_X = 1900
    CURSOR_PARK_Y = 1060

class DeckMasterApp(QMainWindow):
    """Main application class for DeckMaster Control Panel."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.current_page = 1
        self.created_buttons = []
        self.web_browser = None
        self.web_container = None
        self.current_page_data = None
        self.last_buttons_hash = None
        self.last_page_hash = None
        
        # Disable PyAutoGUI failsafe
        pyautogui.FAILSAFE = False
        
        # Load environment variables
        load_dotenv()
        
        # Load action handlers
        self._load_action_handlers()
        
        # Setup UI
        self._setup_ui()
    
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

    def _setup_ui(self) -> None:
        """Setup the main UI."""
        self.setWindowTitle("DeckMaster Control Panel")
        self.showFullScreen()
        self.setStyleSheet(f"QMainWindow {{ background-color: {Config.BG_COLOR}; }}")
        self.setCursor(QCursor(Qt.BlankCursor))  # Hide cursor
        
        # Central widget for absolute positioning
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Setup web browser
        self._setup_web_browser()
        
        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        # Add navigation buttons
        self.add_navigation_buttons()
        
        # Start update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._asyncio_fetch_and_update)
        self.timer.start(Config.UPDATE_INTERVAL)

    def resizeEvent(self, event):
        """Handle window resize to adjust web browser width and position."""
        if self.web_container and self.web_browser:
            width = self.width()  # Full width
            self.web_container.setGeometry(0, 0, width, Config.WEB_HEIGHT)  # Top-left corner
            self.web_browser.setGeometry(0, 0, width, Config.WEB_HEIGHT)
        super().resizeEvent(event)

    def _setup_web_browser(self) -> None:
        """Setup the embedded web browser at the top of the interface."""
        try:
            # Create container for web browser
            self.web_container = QWidget(self.central_widget)
            self.web_container.setFixedHeight(Config.WEB_HEIGHT)
            self.web_container.setStyleSheet(f"background-color: {Config.BG_COLOR};")
            width = self.width()  # Initial full width
            self.web_container.setGeometry(0, 0, width, Config.WEB_HEIGHT)  # Position at top
            self.web_container.lower()  # Ensure it stays at the bottom of the z-order
            
            # Create web browser
            self.web_browser = QWebEngineView(self.web_container)
            self.web_browser.setGeometry(0, 0, width, Config.WEB_HEIGHT)
            
            # Initially hide web browser
            self.web_container.hide()
            
            print("Web browser embedded successfully")
            
        except Exception as e:
            print(f"Error setting up web browser: {e}")
            self.web_browser = None
            self.web_container = None

    def _update_webpage_display(self, page_data: Optional[Dict]) -> None:
        """
        Update the webpage display based on page data.
        
        Args:
            page_data: Dictionary containing page configuration
        """
        if not self.web_browser or not self.web_container:
            return
            
        try:
            if page_data and page_data.get('show_webpage') and page_data.get('webpage_url'):
                # Show and load webpage
                if not self.web_container.isVisible():
                    self.web_container.show()
                    self.web_container.raise_()  # Bring to front when shown
                
                current_url = self.web_browser.url().toString()
                new_url = page_data['webpage_url']
                
                # Only load if URL has changed
                if current_url != new_url:
                    try:
                        self.web_browser.setUrl(QUrl(new_url))
                        print(f"Loaded webpage: {new_url}")
                    except Exception as e:
                        print(f"Error loading webpage {new_url}: {e}")
            else:
                # Hide webpage
                if self.web_container.isVisible():
                    self.web_container.hide()
                    print("Webpage hidden for current page")
        except Exception as e:
            print(f"Error in webpage display: {e}")
    
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
    
    def _load_image(self, image_path: str) -> Optional[QPixmap]:
        """
        Load an image from local file or URL.
        
        Args:
            image_path: Path to local file or URL
            
        Returns:
            QPixmap object or None if loading failed
        """
        if not image_path:
            return None
            
        try:
            if image_path.startswith(("http://", "https://")):
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                urllib.request.urlretrieve(image_path, tmp_file.name)
                pixmap = QPixmap(tmp_file.name)
                os.unlink(tmp_file.name)  # Clean up temporary file
                return pixmap
            elif os.path.isfile(image_path):
                return QPixmap(image_path)
        except Exception as e:
            print(f"Failed to load image '{image_path}': {e}")
        
        return None
    
    def create_button(self, label: str, x: int, y: int, bg: str, fg: str, 
                     action: Optional[str] = None, image_path: Optional[str] = None) -> QPushButton:
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
        button = QPushButton(self.central_widget)
        click_handler = self._create_button_click_handler(label, action)
        button.clicked.connect(click_handler)
        
        pixmap = self._load_image(image_path)
        if pixmap:
            button.setIcon(pixmap)
            button.setIconSize(pixmap.size().scaled(Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT, Qt.KeepAspectRatio))
            button.setStyleSheet(
                f"QPushButton {{"
                f"background-color: {bg};"
                f"border: 2px solid {fg};"
                f"border-radius: 4px;"
                f"}}"
                f"QPushButton:pressed {{"
                f"background-color: {Config.BUTTON_ACTIVE_BG};"
                f"}}"
            )
        else:
            button.setText(label)
            button.setStyleSheet(
                f"QPushButton {{"
                f"background-color: {bg};"
                f"color: {fg};"
                f"font: bold 10px Arial;"
                f"border: 2px solid {fg};"
                f"border-radius: 4px;"
                f"}}"
                f"QPushButton:pressed {{"
                f"background-color: {Config.BUTTON_ACTIVE_BG};"
                f"}}"
            )

        button.setGeometry(
            x + Config.OFFSET_X,
            y + Config.OFFSET_BUTTON_V,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )

        return button
    
    async def fetch_page_data(self, page: int = 1) -> Optional[Dict]:
        """
        Fetch page configuration from database.
        
        Args:
            page: Page number to fetch
            
        Returns:
            Dictionary with page data or None
        """
        try:
            conn = await aiomysql.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                db=os.getenv('DB_NAME')
            )

            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("""
                    SELECT page_number, webpage_url, show_webpage, background_color
                    FROM pages 
                    WHERE page_number = %s
                """, (page,))
                result = await cur.fetchone()

            conn.close()
            return result

        except Exception as e:
            print(f"Database error fetching page data: {e}")
            return None
    
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
    
    def _hash_page_data(self, page_data: Optional[Dict]) -> str:
        """
        Generate hash of page data for change detection.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            MD5 hash string
        """
        serialized = json.dumps(page_data or {}, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()
    
    def update_buttons_if_changed(self, buttons_data: List[Tuple]) -> None:
        """
        Update buttons if data has changed.
        
        Args:
            buttons_data: List of button data tuples
        """
        new_hash = self._hash_buttons_data(buttons_data)
        
        if new_hash != self.last_buttons_hash:
            self.last_buttons_hash = new_hash
            
            # Remove old buttons
            for btn in self.created_buttons:
                btn.deleteLater()
            self.created_buttons.clear()
            
            # Create new buttons
            for button_data in buttons_data:
                btn = self._create_button_from_data(button_data)
                if btn:
                    self.created_buttons.append(btn)
                    btn.show()

    def update_page_if_changed(self, page_data: Optional[Dict]) -> None:
        """
        Update page configuration if data has changed.
        
        Args:
            page_data: Page data dictionary
        """
        new_hash = self._hash_page_data(page_data)
        
        if new_hash != self.last_page_hash:
            self.last_page_hash = new_hash
            self.current_page_data = page_data
            self._update_page_ui(page_data)
    
    def _update_page_ui(self, page_data: Optional[Dict]) -> None:
        """
        Update page UI elements.
        
        Args:
            page_data: Page data dictionary
        """
        try:
            # Update webpage display
            self._update_webpage_display(page_data)
            
            # Update background color if specified
            if page_data and page_data.get('background_color'):
                self.setStyleSheet(f"QMainWindow {{ background-color: {page_data['background_color']}; }}")
            else:
                self.setStyleSheet(f"QMainWindow {{ background-color: {Config.BG_COLOR}; }}")
        except Exception as e:
            print(f"Error updating page UI: {e}")
    
    def _create_button_from_data(self, button_data: Tuple) -> Optional[QPushButton]:
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
            self._asyncio_fetch_and_update()
            pyautogui.moveTo(Config.CURSOR_PARK_X, Config.CURSOR_PARK_Y)
        
        def previous_page():
            if self.current_page > 1:
                self.current_page -= 1
                self._asyncio_fetch_and_update()
                pyautogui.moveTo(Config.CURSOR_PARK_X, Config.CURSOR_PARK_Y)
        
        return previous_page, next_page
    
    def add_navigation_buttons(self) -> None:
        """Add navigation buttons to the interface."""
        try:
            arrow_left = QPixmap("assets/arrow_left.png")
            arrow_right = QPixmap("assets/arrow_right.png")
        except Exception as e:
            print(f"Error loading arrow images: {e}")
            return
        
        previous_page, next_page = self._create_navigation_handlers()
        
        # Left arrow button
        left_button = QPushButton(self.central_widget)
        left_button.setIcon(arrow_left)
        left_button.setIconSize(arrow_left.size().scaled(Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT, Qt.KeepAspectRatio))
        left_button.setGeometry(
            Config.NAV_LEFT_X + Config.OFFSET_X,
            Config.NAV_Y + Config.OFFSET_BUTTON_V,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )
        left_button.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Config.NAV_BUTTON_BG};"
            f"border: none;"
            f"}}"
            f"QPushButton:pressed {{"
            f"background-color: {Config.BUTTON_ACTIVE_BG};"
            f"}}"
        )
        left_button.clicked.connect(previous_page)
        left_button.show()
        
        # Right arrow button
        right_button = QPushButton(self.central_widget)
        right_button.setIcon(arrow_right)
        right_button.setIconSize(arrow_right.size().scaled(Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT, Qt.KeepAspectRatio))
        right_button.setGeometry(
            Config.NAV_RIGHT_X + Config.OFFSET_X,
            Config.NAV_Y + Config.OFFSET_BUTTON_V,
            Config.BUTTON_WIDTH,
            Config.BUTTON_HEIGHT
        )
        right_button.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {Config.NAV_BUTTON_BG};"
            f"border: none;"
            f"}}"
            f"QPushButton:pressed {{"
            f"background-color: {Config.BUTTON_ACTIVE_BG};"
            f"}}"
        )
        right_button.clicked.connect(next_page)
        right_button.show()
    
    def _asyncio_fetch_and_update(self) -> None:
        """
        Fetch page and button data from database and update UI.
        Called periodically for live updates.
        """
        async def fetch_task():
            try:
                page_data = await self.fetch_page_data(self.current_page)
                buttons_data = await self.fetch_buttons(self.current_page)
                return page_data, buttons_data
            except Exception as e:
                print(f"Error in fetch_task: {e}")
                return None, []
        
        try:
            if self.isVisible():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                page_data, buttons_data = loop.run_until_complete(fetch_task())
                loop.close()
                
                # Update page configuration
                if page_data is not None:
                    self.update_page_if_changed(page_data)
                
                # Update buttons
                if buttons_data:
                    self.update_buttons_if_changed(buttons_data)
            
        except Exception as e:
            print(f"Error in _asyncio_fetch_and_update: {e}")
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        # Escape to exit fullscreen
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.showNormal)
        
        # Q or q to quit
        q_shortcut = QShortcut(QKeySequence("q"), self)
        q_shortcut.activated.connect(self.close)
        Q_shortcut = QShortcut(QKeySequence("Q"), self)
        Q_shortcut.activated.connect(self.close)
    
    def run(self) -> None:
        """Run the application."""
        self.show()
        QApplication.instance().exec()

def main():
    """Main entry point."""
    app = QApplication([])
    window = DeckMasterApp()
    window.run()

if __name__ == "__main__":
    main()