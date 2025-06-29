# DeckMaster

A customisable, database-driven control panel application.

DeckMaster provides a fullscreen interface with configurable buttons that can execute various actions, making it perfect for control panels or automation dashboards.

![image](https://github.com/user-attachments/assets/7cad3c88-6036-4d74-ac16-b5cc4b812bd2)

## Features

- **Database-Driven Configuration**: All buttons and pages are stored in a MySQL database for easy management
- **Embedded Web Browser**: Display web pages directly in the interface using tkinterweb
- **Customisable Actions**: Extensible action system for executing commands, scripts, and automations
- **Multi-Page Support**: Navigate between different pages of buttons with arrow navigation
- **Live Updates**: Real-time synchronization with database changes (500ms polling)
- **Fullscreen Interface**: Clean, distraction-free fullscreen experience
- **Image Support**: Buttons can display custom images from local files or URLs
- **Responsive Design**: Configurable layout with consistent button positioning

## Prerequisites

- Python 3.7+
- MySQL database server
- Required Python packages (see `requirements.txt`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rhysfx/DeckMaster
   cd DeckMaster
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASS=your_password
   DB_NAME=deckmaster
   ```

4. **Set up the database**
   
   Create the required tables in your MySQL database:
   ```sql
   CREATE DATABASE deckmaster;
   USE deckmaster;

   CREATE TABLE pages (
       id INT AUTO_INCREMENT PRIMARY KEY,
       page_number INT NOT NULL UNIQUE,
       webpage_url VARCHAR(500),
       show_webpage BOOLEAN DEFAULT FALSE,
       background_color VARCHAR(7) DEFAULT '#1e1e1e'
   );

   CREATE TABLE buttons (
       id INT AUTO_INCREMENT PRIMARY KEY,
       page INT NOT NULL,
       label VARCHAR(100) NOT NULL,
       pos_x INT NOT NULL,
       pos_y INT NOT NULL,
       color_bg VARCHAR(7) DEFAULT '#2d2d30',
       color_fg VARCHAR(7) DEFAULT '#ffffff',
       action VARCHAR(200),
       image_path VARCHAR(500),
       INDEX idx_page (page)
   );
   ```

## Usage

### Running the Control Panel

Start the control panel interface that displays the pages and buttons:

```bash
python renderer.py
```

**Keyboard Shortcuts:**
- `Escape` - Exit fullscreen mode
- `Q` or `q` - Quit application

### Running the Dashboard

Start the management dashboard to configure buttons and pages:

```bash
python dashboard.py
```

The dashboard provides a web interface for managing your control panel configuration.

### Adding Buttons

Insert buttons into the database:

```sql
INSERT INTO buttons (page, label, pos_x, pos_y, color_bg, color_fg, action, image_path) 
VALUES (1, 'My Button', 100, 100, '#007acc', '#ffffff', 'command:parameter', 'path/to/image.png');
```

### Configuring Pages

Configure page settings:

```sql
INSERT INTO pages (page_number, webpage_url, show_webpage, background_color) 
VALUES (1, 'https://example.com', TRUE, '#1e1e1e');
```

### Creating Custom Actions

1. Create action handlers in the Actions directory:

```python
from actions import register_action

@register_action("my_custom_action")
def my_custom_action(param):
    print(f"[Action:my_custom_action] {param}")
```

2. Use the action in your button configuration:
```sql
UPDATE buttons SET action = 'my_command:some_parameter' WHERE id = 1;
```

## Configuration

### Button Layout

The interface uses a grid-based layout system:
- **Button Size**: 121x128 pixels
- **Spacing**: Configurable via `OFFSET_X` and `OFFSET_BUTTON_V`
- **Position**: Absolute positioning using `pos_x` and `pos_y` in database

### Color Scheme

Default colors can be customized in the `Config` class:
- **Background**: `#1e1e1e` (dark gray)
- **Button Active**: `#007acc` (blue)
- **Navigation Buttons**: `#2d2d30` (slightly lighter gray)

### Web Browser Integration

Pages can display embedded web content:
- Set `show_webpage = TRUE` in the pages table
- Specify the URL in `webpage_url`
- Web content appears at the top of the interface

## Architecture

### Core Components

- **renderer.py**: Control panel interface that reads from database and displays buttons
- **dashboard.py**: Management interface for configuring buttons, pages, and actions  
- **Database Layer**: MySQL database storing all configuration data
- **Action System**: Pluggable command execution framework
- **Web Integration**: Embedded browser using tkinterweb (renderer only)

### System Flow

1. **Dashboard** → Creates/modifies buttons and pages → **Database**
2. **Database** → Live updates (500ms polling) → **Renderer** 
3. **Renderer** → Displays interface and executes button actions

### Database Schema

The application uses two main tables:
- `pages`: Page-level configuration (background, web content)
- `buttons`: Individual button definitions with actions

### Action System

Actions follow the format `command:parameter` and are handled by registered functions in the `action_handlers` dictionary.

### Debugging

The application includes extensive logging. Check console output for:
- Database connection issues
- Action execution errors
- Image loading problems
- Web browser integration issues

## Acknowledgments

- Built with [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI
- Uses [tkinterweb](https://github.com/Andereoo/TkinterWeb) for embedded web browsing
- Database integration via [aiomysql](https://github.com/aio-libs/aiomysql)
- Automation capabilities powered by [PyAutoGUI](https://github.com/asweigart/pyautogui)

---

**DeckMaster** - *A clean and simple control interface*
