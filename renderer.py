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
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication, QLabel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut, QCursor
from PySide6.QtCore import Qt, QTimer, QUrl

from actions import load_actions, action_handlers

# Load environment variables
load_dotenv()

async def load_settings(show_error=None, parent=None):
    try:
        conn = await aiomysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            db=os.getenv('DB_NAME')
        )
        async with conn.cursor() as cur:
            await cur.execute("SELECT `key`, `value` FROM settings")
            rows = await cur.fetchall()
            settings = {k: v for k, v in rows}
        conn.close()
        return settings
    except Exception as e:
        if show_error:
            show_error(parent, f"Database connection failed: {e}")
        return {}

def settings_get(settings, key, fallback):
    val = settings.get(key, fallback)
    if isinstance(fallback, int):
        try:
            return int(val)
        except Exception:
            return fallback
    return val

class DeckMasterApp(QMainWindow):
    """Main application class for DeckMaster Control Panel."""

    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.created_buttons = []
        self.web_browser = None
        self.web_container = None
        self.current_page_data = None
        self.last_buttons_hash = None
        self.last_page_hash = None

        # Synchronously load settings at startup, show error if DB fails
        self.settings = asyncio.run(load_settings(self.show_error_feedback, self))

        # Disable PyAutoGUI failsafe
        pyautogui.FAILSAFE = False

        self._load_action_handlers()
        self._setup_ui()

    def _setup_error_banner(self):
        self.error_banner = QLabel(self)
        self.error_banner.setGeometry(0, 0, self.width(), 60)
        self.error_banner.setStyleSheet(
            "background-color: #ff3333; color: white; font-size: 28px; font-weight: bold; border-bottom: 4px solid #b20000;"
        )
        self.error_banner.setAlignment(Qt.AlignCenter)
        self.error_banner.hide()
        self.error_banner.raise_()

    def resizeEvent(self, event):
        if hasattr(self, "error_banner"):
            self.error_banner.setGeometry(0, 0, self.width(), 60)
        if self.web_container and self.web_browser:
            width = self.width()
            self.web_container.setGeometry(0, 0, width, settings_get(self.settings, 'WEB_HEIGHT', 300))
            self.web_browser.setGeometry(0, 0, width, settings_get(self.settings, 'WEB_HEIGHT', 300))
        super().resizeEvent(event)

    def show_error_feedback(self, widget, message):
        if hasattr(self, "error_banner"):
            self.error_banner.setText(message)
            self.error_banner.show()
            self.error_banner.raise_()
            QTimer.singleShot(settings_get(self.settings, 'ERROR_BANNER_TIMEOUT', 5000), self.error_banner.hide)
        else:
            from PySide6.QtWidgets import QToolTip
            QToolTip.showText(self.mapToGlobal(self.rect().center()), message, self)
            QTimer.singleShot(settings_get(self.settings, 'ERROR_BANNER_TIMEOUT', 5000), QToolTip.hideText)

    def _load_action_handlers(self) -> None:
        try:
            load_actions()
            print("Actions loaded successfully")
            print(f"Available action handlers: {list(action_handlers.keys())}")
        except Exception as e:
            print(f"Error loading actions: {e}")
            self.show_error_feedback(self, f"Error loading actions: {e}")

    def execute_action(self, action: str) -> None:
        if not action:
            print("No action defined")
            return

        actions = [a.strip() for a in action.split('&&') if a.strip()]
        for act in actions:
            if ':' in act:
                command, param = act.split(':', 1)
            else:
                command, param = act, None

            handler = action_handlers.get(command)
            if handler:
                try:
                    import inspect
                    sig = inspect.signature(handler)
                    if len(sig.parameters) > 1:
                        handler(param, self)
                    elif len(sig.parameters) == 1:
                        handler(param)
                    else:
                        handler()
                except Exception as e:
                    print(f"Error executing action {command}: {e}")
                    self.show_error_feedback(self, f"Error executing action {command}: {e}")
            else:
                print(f"No handler for action '{command}'")
                self.show_error_feedback(self, f"No handler for action '{command}'")

    def _setup_ui(self) -> None:
        self.setWindowTitle("DeckMaster Control Panel")
        self.showFullScreen()
        self.setStyleSheet(
            f"QMainWindow {{ background-color: {settings_get(self.settings, 'BG_COLOR', '#1e1e1e')}; }}"
        )
        self.setCursor(QCursor(Qt.BlankCursor))  # Hide cursor

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self._setup_error_banner()
        self._setup_web_browser()
        self._setup_keyboard_shortcuts()
        self.add_navigation_buttons()

        self.timer = QTimer()
        self.timer.timeout.connect(self._asyncio_fetch_and_update)
        self.timer.start(settings_get(self.settings, 'UPDATE_INTERVAL', 500))

    def _setup_web_browser(self) -> None:
        try:
            self.web_container = QWidget(self.central_widget)
            web_height = settings_get(self.settings, 'WEB_HEIGHT', 300)
            self.web_container.setFixedHeight(web_height)
            self.web_container.setStyleSheet(
                f"background-color: {settings_get(self.settings, 'BG_COLOR', '#1e1e1e')};"
            )
            width = self.width()
            self.web_container.setGeometry(0, 0, width, web_height)
            self.web_container.lower()

            self.web_browser = QWebEngineView(self.web_container)
            self.web_browser.setGeometry(0, 0, width, web_height)

            self.web_container.hide()
            print("Web browser embedded successfully")
        except Exception as e:
            print(f"Error setting up web browser: {e}")
            self.web_browser = None
            self.web_container = None
            self.show_error_feedback(self, f"Error setting up web browser: {e}")

    def _update_webpage_display(self, page_data: Optional[Dict]) -> None:
        if not self.web_browser or not self.web_container:
            return
        try:
            if page_data and page_data.get('show_webpage') and page_data.get('webpage_url'):
                if not self.web_container.isVisible():
                    self.web_container.show()
                    self.web_container.raise_()

                current_url = self.web_browser.url().toString()
                new_url = page_data['webpage_url']
                if current_url != new_url:
                    try:
                        self.web_browser.setUrl(QUrl(new_url))
                        print(f"Loaded webpage: {new_url}")
                    except Exception as e:
                        print(f"Error loading webpage {new_url}: {e}")
                        self.show_error_feedback(self, f"Error loading webpage {new_url}: {e}")
            else:
                if self.web_container.isVisible():
                    self.web_container.hide()
                    print("Webpage hidden for current page")
        except Exception as e:
            print(f"Error in webpage display: {e}")
            self.show_error_feedback(self, f"Error in webpage display: {e}")

    def _create_button_click_handler(self, label: str, action: Optional[str]):
        def on_button_click():
            if action:
                print(f"Executing action for button '{label}': {action}")
                self.execute_action(action)
            else:
                print(f"Button '{label}' clicked but no action defined")
            pyautogui.moveTo(
                settings_get(self.settings, 'CURSOR_PARK_X', 1900),
                settings_get(self.settings, 'CURSOR_PARK_Y', 1060)
            )
        return on_button_click

    def _load_image(self, image_path: str) -> Optional[QPixmap]:
        if not image_path:
            return None
        try:
            if image_path.startswith(("http://", "https://")):
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                urllib.request.urlretrieve(image_path, tmp_file.name)
                pixmap = QPixmap(tmp_file.name)
                os.unlink(tmp_file.name)
                return pixmap
            elif os.path.isfile(image_path):
                return QPixmap(image_path)
        except Exception as e:
            print(f"Failed to load image '{image_path}': {e}")
            self.show_error_feedback(self, f"Failed to load image '{image_path}': {e}")
        return None

    def create_button(self, label: str, x: int, y: int, bg: str, fg: str,
                     action: Optional[str] = None, image_path: Optional[str] = None) -> QPushButton:
        button = QPushButton(self.central_widget)
        click_handler = self._create_button_click_handler(label, action)
        button.clicked.connect(click_handler)

        pixmap = self._load_image(image_path)
        button_width = settings_get(self.settings, 'BUTTON_WIDTH', 121)
        button_height = settings_get(self.settings, 'BUTTON_HEIGHT', 128)
        offset_x = settings_get(self.settings, 'OFFSET_X', 20)
        offset_v = settings_get(self.settings, 'OFFSET_BUTTON_V', 7)
        btn_active_bg = settings_get(self.settings, 'BUTTON_ACTIVE_BG', '#007acc')

        if pixmap:
            button.setIcon(pixmap)
            button.setIconSize(pixmap.size().scaled(button_width, button_height, Qt.KeepAspectRatio))
            button.setStyleSheet(
                f"QPushButton {{ background-color: {bg}; border: 2px solid {fg}; border-radius: 4px; }}"
                f"QPushButton:pressed {{ background-color: {btn_active_bg}; }}"
            )
        else:
            button.setText(label)
            button.setStyleSheet(
                f"QPushButton {{ background-color: {bg}; color: {fg}; font: bold 10px Arial; border: 2px solid {fg}; border-radius: 4px; }}"
                f"QPushButton:pressed {{ background-color: {btn_active_bg}; }}"
            )

        button.setGeometry(
            x + offset_x,
            y + offset_v,
            button_width,
            button_height
        )
        return button

    async def fetch_page_data(self, page: int = 1) -> Optional[Dict]:
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
            self.show_error_feedback(self, f"Database error fetching page data: {e}")
            return None

    async def fetch_buttons(self, page: int = 1) -> List[Tuple]:
        try:
            conn = await aiomysql.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASS'),
                db=os.getenv('DB_NAME')
            )

            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT label, pos_x, pos_y, color_bg, color_fg, action, image_path, page
                    FROM buttons
                """)
                result = await cur.fetchall()
                filtered = []
                for row in result:
                    pages = row[-1].split(",")
                    if str(page) in [p.strip() for p in pages]:
                        filtered.append(row[:-1])
                return filtered

        except Exception as e:
            print(f"Database error: {e}")
            self.show_error_feedback(self, f"Database error fetching buttons: {e}")
            return []

    def _hash_buttons_data(self, buttons_data: List[Tuple]) -> str:
        serialized = json.dumps(buttons_data, sort_keys=True)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()

    def _hash_page_data(self, page_data: Optional[Dict]) -> str:
        serialized = json.dumps(page_data or {}, sort_keys=True, default=str)
        return hashlib.md5(serialized.encode('utf-8')).hexdigest()

    def update_buttons_if_changed(self, buttons_data: List[Tuple]) -> None:
        new_hash = self._hash_buttons_data(buttons_data)

        if new_hash != self.last_buttons_hash:
            self.last_buttons_hash = new_hash

            for btn in self.created_buttons:
                btn.deleteLater()
            self.created_buttons.clear()

            for button_data in buttons_data:
                btn = self._create_button_from_data(button_data)
                if btn:
                    self.created_buttons.append(btn)
                    btn.show()

    def update_page_if_changed(self, page_data: Optional[Dict]) -> None:
        new_hash = self._hash_page_data(page_data)

        if new_hash != self.last_page_hash:
            self.last_page_hash = new_hash
            self.current_page_data = page_data
            self._update_page_ui(page_data)

    def _update_page_ui(self, page_data: Optional[Dict]) -> None:
        try:
            self._update_webpage_display(page_data)
            if page_data and page_data.get('background_color'):
                self.setStyleSheet(f"QMainWindow {{ background-color: {page_data['background_color']}; }}")
            else:
                self.setStyleSheet(f"QMainWindow {{ background-color: {self.settings.get('BG_COLOR', '#1e1e1e')}; }}")
        except Exception as e:
            print(f"Error updating page UI: {e}")
            self.show_error_feedback(self, f"Error updating page UI: {e}")

    def _create_button_from_data(self, button_data: Tuple) -> Optional[QPushButton]:
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
            self.show_error_feedback(self, f"Invalid button data: {button_data}")
            return None

    def _create_navigation_handlers(self):
        def next_page():
            self.current_page += 1
            self._asyncio_fetch_and_update()
            pyautogui.moveTo(
                int(self.settings.get('CURSOR_PARK_X', 1900)),
                int(self.settings.get('CURSOR_PARK_Y', 1060))
            )

        def previous_page():
            if self.current_page > 1:
                self.current_page -= 1
                self._asyncio_fetch_and_update()
                pyautogui.moveTo(
                    int(self.settings.get('CURSOR_PARK_X', 1900)),
                    int(self.settings.get('CURSOR_PARK_Y', 1060))
                )

        return previous_page, next_page

    def add_navigation_buttons(self) -> None:
        try:
            arrow_left = QPixmap("assets/arrow_left.png")
            arrow_right = QPixmap("assets/arrow_right.png")
        except Exception as e:
            print(f"Error loading arrow images: {e}")
            self.show_error_feedback(self, f"Error loading arrow images: {e}")
            return

        previous_page, next_page = self._create_navigation_handlers()

        left_button = QPushButton(self.central_widget)
        left_button.setIcon(arrow_left)
        left_button.setIconSize(
            arrow_left.size().scaled(
                int(self.settings.get('BUTTON_WIDTH', 121)),
                int(self.settings.get('BUTTON_HEIGHT', 128)),
                Qt.KeepAspectRatio
            )
        )
        left_button.setGeometry(
            int(self.settings.get('NAV_LEFT_X', 985)) + int(self.settings.get('OFFSET_X', 20)),
            int(self.settings.get('NAV_Y', 662)) + int(self.settings.get('OFFSET_BUTTON_V', 7)),
            int(self.settings.get('BUTTON_WIDTH', 121)),
            int(self.settings.get('BUTTON_HEIGHT', 128))
        )
        left_button.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {self.settings.get('NAV_BUTTON_BG', '#2d2d30')};"
            f"border: none;"
            f"}}"
            f"QPushButton:pressed {{"
            f"background-color: {self.settings.get('BUTTON_ACTIVE_BG', '#007acc')};"
            f"}}"
        )
        left_button.clicked.connect(previous_page)
        left_button.show()

        right_button = QPushButton(self.central_widget)
        right_button.setIcon(arrow_right)
        right_button.setIconSize(
            arrow_right.size().scaled(
                int(self.settings.get('BUTTON_WIDTH', 121)),
                int(self.settings.get('BUTTON_HEIGHT', 128)),
                Qt.KeepAspectRatio
            )
        )
        right_button.setGeometry(
            int(self.settings.get('NAV_RIGHT_X', 1153)) + int(self.settings.get('OFFSET_X', 20)),
            int(self.settings.get('NAV_Y', 662)) + int(self.settings.get('OFFSET_BUTTON_V', 7)),
            int(self.settings.get('BUTTON_WIDTH', 121)),
            int(self.settings.get('BUTTON_HEIGHT', 128))
        )
        right_button.setStyleSheet(
            f"QPushButton {{"
            f"background-color: {self.settings.get('NAV_BUTTON_BG', '#2d2d30')};"
            f"border: none;"
            f"}}"
            f"QPushButton:pressed {{"
            f"background-color: {self.settings.get('BUTTON_ACTIVE_BG', '#007acc')};"
            f"}}"
        )
        right_button.clicked.connect(next_page)
        right_button.show()

    def _asyncio_fetch_and_update(self) -> None:
        async def fetch_task():
            try:
                page_data = await self.fetch_page_data(self.current_page)
                buttons_data = await self.fetch_buttons(self.current_page)
                return page_data, buttons_data
            except Exception as e:
                print(f"Error in fetch_task: {e}")
                self.show_error_feedback(self, f"Error in fetch_task: {e}")
                return None, []

        try:
            if self.isVisible():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                page_data, buttons_data = loop.run_until_complete(fetch_task())
                loop.close()

                if page_data is not None:
                    self.update_page_if_changed(page_data)
                if buttons_data:
                    self.update_buttons_if_changed(buttons_data)

        except Exception as e:
            print(f"Error in _asyncio_fetch_and_update: {e}")
            self.show_error_feedback(self, f"Error in _asyncio_fetch_and_update: {e}")

    def _setup_keyboard_shortcuts(self) -> None:
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.showNormal)
        q_shortcut = QShortcut(QKeySequence("q"), self)
        q_shortcut.activated.connect(self.close)
        Q_shortcut = QShortcut(QKeySequence("Q"), self)
        Q_shortcut.activated.connect(self.close)

    def run(self) -> None:
        self.show()
        QApplication.instance().exec()

def main():
    app = QApplication([])
    window = DeckMasterApp()
    window.run()

if __name__ == "__main__":
    main()