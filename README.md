# DeckMaster
DeckMaster provides a fullscreen interface with configurable buttons that can execute various actions, making it perfect for control panels or automation dashboards.

![image](https://github.com/user-attachments/assets/7cad3c88-6036-4d74-ac16-b5cc4b812bd2)

## Table of Contents

- [Showcase](#example-showcase)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Running the Control Panel](#running-the-control-panel)
  - [Running the Dashboard](#running-the-dashboard)
- [Built-in Actions](#built-in-actions)
- [Built-in Presets](#built-in-presets)
- [Configuration](#configuration)
  - [Adding Buttons](#adding-buttons)
  - [Configuring Pages](#configuring-pages)
  - [Creating Custom Actions](#creating-custom-actions)
  - [Button Layout](#button-layout)
  - [Color Scheme](#color-scheme)
  - [Web Browser Integration](#web-browser-integration)
- [Architecture](#architecture)
  - [Core Components](#core-components)
  - [System Flow](#system-flow)
  - [Database Schema](#database-schema)
  - [Action System](#action-system)
- [Debugging](#debugging)
- [Acknowledgments](#acknowledgments)

## Example Showcase

These are some examples of control panels I’ve spun up using DeckMaster. 

Each layout demonstrates how customizable the interface is.

### 🎮 Windows Control Panel

<img src="https://github.com/user-attachments/assets/9ba7dc48-21cf-4627-bc87-91679b56fa9d" width="700" />

### 💡Lights Control
<img src="https://github.com/user-attachments/assets/c41e281b-b18b-4d59-a231-f33690d15fbe" width="700" />

## Features
- **Database-Driven Configuration**: All buttons and pages are stored in a MySQL database for easy management
- **Embedded Web Browser**: Display web pages directly in the interface using QtWebEngine
- **Built-in Actions**: Comprehensive library of pre-built actions for common automation tasks
- **Customisable Actions**: Extensible action system for executing commands, scripts, and automations
- **Multi-Page Support**: Navigate between different pages of buttons with arrow navigation
- **Live Updates**: Real-time synchronisation with database changes (500ms polling)
- **Fullscreen Interface**: Clean, distraction-free fullscreen experience
- **Image Support**: Buttons can display custom images from local files or URLs
- **Responsive Design**: Configurable layout with consistent button positioning
- **Device Templates**: Pre-configured database templates for popular devices and use cases

## Prerequisites

- Python 3.13+
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

    CREATE TABLE `pages` (
      `id` int(11) NOT NULL,
      `page_number` int(11) NOT NULL,
      `webpage_url` varchar(500) DEFAULT NULL,
      `show_webpage` tinyint(1) DEFAULT 0,
      `background_color` varchar(7) DEFAULT '#1e1e1e'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

    CREATE TABLE `buttons` (
      `id` int(11) NOT NULL,
      `label` varchar(50) NOT NULL,
      `pos_x` int(11) NOT NULL,
      `pos_y` int(11) NOT NULL,
      `color_bg` varchar(7) DEFAULT '#2d2d30',
      `color_fg` varchar(7) DEFAULT 'white',
      `action` varchar(255) DEFAULT NULL,
      `page` varchar(255) DEFAULT '1',
      `image_path` varchar(255) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

   CREATE TABLE `settings` (
      `key` varchar(255) NOT NULL,
      `value` text NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

   ALTER TABLE `pages`
    ADD PRIMARY KEY (`id`),
    ADD UNIQUE KEY `page_number` (`page_number`);

   ALTER TABLE `buttons`
    ADD PRIMARY KEY (`id`);

   ALTER TABLE `settings`
    ADD PRIMARY KEY (`key`);
   ```

## Quick Start

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

The dashboard provides a web interface for managing your control panel configuration - currently in works and non-functional at all.

## Built-in Actions

DeckMaster comes with a library of pre-built actions that cover common automation and control tasks. These actions are ready to use out of the box and can be referenced in your button configurations.

For a complete list of available actions and their parameters, refer to the `actions/` directory in the project.

## Built-in Presets

DeckMaster includes pre-configured database presets for popular devices and use cases. These templates provide ready-to-use button layouts and actions that you can import directly into your database.

For a complete list of available presets, refer to the `presets/` directory in the project.

## Configuration

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
UPDATE buttons SET action = 'my_custom_action:some_parameter' WHERE id = 1;
```

### Button Layout

The interface uses a grid-based layout system:
- **Button Size**: 121x128 pixels
- **Spacing**: Configurable via `OFFSET_X` and `OFFSET_BUTTON_V` within settings table of database
- **Position**: Absolute positioning using `pos_x` and `pos_y` in database

### Color Scheme

Default colors can be customized in the settings table of the database.
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

### System Flow

1. **Dashboard** → Creates/modifies buttons and pages → **Database**
2. **Database** → Live updates (500ms polling) → **Renderer** 
3. **Renderer** → Displays interface and executes button actions

### Database Schema

The application uses two main tables:
- `pages`: Page-level configuration (background, web content)
- `buttons`: Individual button definitions with actions
- `settings`: Defines system-wide configuration options

<img src="https://github.com/user-attachments/assets/f74b1c16-0e15-41c7-9714-2e97a4d9937a" width="600" />


### Action System

Actions follow the format `command:parameter` and are handled by registered functions in the `actions` dictionary.

### Debugging

The application includes extensive logging. Check console output for:
- Database connection issues
- Action execution errors
- Image loading problems
- Web browser integration issues

On-screen errors *may* also be displayed within the renderer.

<img src="https://github.com/user-attachments/assets/5989cddd-6c36-4ec9-af60-1339a0b661f4" width="600" />

## Acknowledgments

- Built with [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI
- Uses [QtWebEngine](https://doc.qt.io/qtforpython-6/overviews/qtwebengine-overview.html) for embedded web pages  
- Database integration via [aiomysql](https://github.com/aio-libs/aiomysql)
- Automation capabilities powered by [PyAutoGUI](https://github.com/asweigart/pyautogui)
---

**DeckMaster** - *A clean and simple control interface*
