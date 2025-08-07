# DeckMaster
Turn any screen into a powerful control center! 

DeckMaster gives you a clean, fullscreen interface with customizable buttons that can execute various actions - perfect for control panels, automation dashboards, or any situation where you need quick access to commands and controls.

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

Here are some real control panels I've built using DeckMaster. Each layout shows how flexible and customizable the interface can be.

### 🎮 Windows Control Panel

<img src="https://github.com/user-attachments/assets/9ba7dc48-21cf-4627-bc87-91679b56fa9d" width="700" />

### 💡Lights Control
<img src="https://github.com/user-attachments/assets/c41e281b-b18b-4d59-a231-f33690d15fbe" width="700" />

## Features

**What makes DeckMaster special:**

- **Database-Driven Configuration**: All buttons and pages live in a MySQL database, making management and updates straightforward
- **Embedded Web Browser**: Display web pages directly within your interface using QtWebEngine
- **Built-in Actions**: Comes with a comprehensive library of pre-built actions for common automation tasks
- **Customizable Actions**: Easy-to-extend action system lets you execute commands, scripts, and custom automations
- **Multi-Page Support**: Create multiple pages of buttons and navigate between them using arrow controls
- **Live Updates**: Changes sync in real-time with the database (polls every 500ms), so updates appear immediately
- **Fullscreen Interface**: Clean, distraction-free fullscreen experience that looks great on any display
- **Image Support**: Buttons can display custom images loaded from local files or URLs
- **Responsive Design**: Configurable layout system with consistent button positioning
- **Device Templates**: Pre-configured database templates get you up and running quickly with popular setups

## Prerequisites

Before getting started, make sure you have:

- Python 3.13+ (though earlier versions should work fine)
- MySQL database server
- The required Python packages (listed in `requirements.txt`)

## Installation

Getting DeckMaster running is straightforward:

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
   
   Create a `.env` file in the project root with your database connection details:
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

Launch your control panel interface:

```bash
python renderer.py
```

**Navigation and Controls:**
- **Click any button** to execute its assigned action
- **Arrow buttons** appear automatically when you have multiple pages
- **Escape** - Exit fullscreen mode (handy during setup and testing)
- **Q or q** - Quit the application completely

The interface automatically refreshes every 500ms, so any changes you make to the database will appear almost instantly without needing to restart.

### Running the Dashboard

Start the management dashboard for configuring your setup:

```bash
python dashboard.py
```

*Note: The dashboard provides a web interface for managing your control panel configuration, though it's currently a work in progress and not fully functional yet.*

## Built-in Actions

DeckMaster includes a library of ready-to-use actions that handle common automation and control tasks. You don't need to write any code - just reference these actions in your button configurations.

The actions cover a wide range of functionality, from basic system commands to more complex automation tasks. 

You'll find the complete list of available actions and their usage examples in the `actions/` directory.

## Built-in Presets

Jump-start your setup with pre-configured templates! DeckMaster includes ready-to-use database presets for popular devices and common use cases. These templates provide complete button layouts and actions that you can import directly into your database.

Browse the `presets/` directory to see what's available and find the perfect starting point for your control panel.

## Configuration

### Adding Buttons

Create new buttons by inserting them into the database. Here's a simple example:

```sql
INSERT INTO buttons (page, label, pos_x, pos_y, color_bg, color_fg, action, image_path) 
VALUES (1, 'My Button', 100, 100, '#007acc', '#ffffff', 'command:parameter', 'path/to/image.png');
```

**Understanding the fields:**
- `page`: Which page the button appears on (start with 1)
- `label`: Text displayed on the button
- `pos_x, pos_y`: Exact position on screen in pixels
- `color_bg, color_fg`: Background and text colors using hex codes
- `action`: What happens when clicked, formatted as `action_type:parameter`
- `image_path`: Optional path to an icon or image file

### Configuring Pages

Set up different pages to organize your buttons:

```sql
INSERT INTO pages (page_number, webpage_url, show_webpage, background_color) 
VALUES (1, 'https://example.com', TRUE, '#1e1e1e');
```

**Page configuration options:**
- `page_number`: Unique identifier for the page
- `webpage_url`: Optional URL to display web content
- `show_webpage`: Set to TRUE to actually show the web content
- `background_color`: Page background color using hex codes

### Creating Custom Actions

Extend DeckMaster's functionality by creating your own actions:

1. **Create your action handler** in the Actions directory:

```python
from actions import register_action

@register_action("my_custom_action")
def my_custom_action(param):
    print(f"[Action:my_custom_action] Executing with parameter: {param}")
    # Add your custom logic here
```

2. **Use the action in your buttons:**
```sql
UPDATE buttons SET action = 'my_custom_action:some_parameter' WHERE id = 1;
```

The action system is designed to be simple and extensible. Your custom actions can do anything Python can do - run shell commands, interact with APIs, control hardware, or integrate with other systems.

### Button Layout

DeckMaster uses an absolute positioning system that gives you complete control over your interface layout:

**Key measurements:**
- **Button Size**: 121×128 pixels (standard size)
- **Positioning**: Use `pos_x` and `pos_y` for exact pixel placement
- **Spacing**: Controlled via `OFFSET_X` and `OFFSET_BUTTON_V` settings in the database

**Layout tips:**
- Start with positions like 100, 250, 400 for evenly spaced buttons
- Leave enough space between buttons for comfortable clicking
- Test your layout on the actual screen where it'll be used

### Color Scheme

Customize the look and feel with colors that match your setup:

```sql
-- Change individual button colors
UPDATE buttons SET color_bg = '#ff6b6b', color_fg = '#ffffff' WHERE label = 'Emergency Stop';

-- Update page background
UPDATE pages SET background_color = '#2c3e50' WHERE page_number = 1;
```

**Default color scheme:**
- **Background**: `#1e1e1e` (dark gray)
- **Button Active**: `#007acc` (blue accent)
- **Navigation Buttons**: `#2d2d30` (slightly lighter gray)
- **Text**: `white`

You can customize these defaults through the settings table in your database.

### Web Browser Integration

One of DeckMaster's coolest features is embedding live web content directly in your interface:

```sql
-- Show a web page at the top of your control panel
UPDATE pages SET 
    webpage_url = 'https://your-dashboard.com', 
    show_webpage = TRUE 
WHERE page_number = 1;
```

This is perfect for displaying:
- System monitoring dashboards
- Smart home control interfaces  
- Live data feeds or status pages
- Custom web applications you've built

The web content appears at the top of the page, with your buttons positioned below it.

## Architecture

### Core Components

DeckMaster's architecture is clean and modular:

- **renderer.py**: The main control panel interface that displays your buttons and handles interactions
- **dashboard.py**: Web-based management interface for configuration (currently under development)
- **Database Layer**: MySQL database that stores all your configuration data
- **Action System**: Flexible framework for executing commands and automations

### System Flow

Here's how everything works together:

1. **Database** stores your configuration (buttons, pages, settings)
2. **Renderer** reads from the database and displays your interface
3. **Live polling** (every 500ms) keeps the interface synchronized with database changes
4. **Action system** handles button clicks and executes the appropriate commands

This design means you can make changes to your setup and see them appear almost immediately, without needing to restart anything.

### Database Schema

Three main tables work together to define your control panel:

- **`pages`**: Page-level configuration including background colors and web content settings
- **`buttons`**: Individual button definitions with positions, actions, and styling
- **`settings`**: System-wide configuration options like spacing and default colors

<img src="https://github.com/user-attachments/assets/f74b1c16-0e15-41c7-9714-2e97a4d9937a" width="600" />

### Action System

Actions use a simple but powerful format: `command_type:parameter`

When you click a button, DeckMaster:
1. Parses the action string from the database
2. Looks up the registered handler function for that command type
3. Calls the function with the parameter
4. Displays any results or errors

This makes it easy to add new functionality without modifying the core application code.

## Debugging

DeckMaster includes comprehensive logging to help you troubleshoot issues:

**Check the console output for:**
- Database connection problems
- Action execution errors  
- Image loading issues
- Web browser integration problems

**On-screen error display:**
The renderer can also show errors directly in the interface, making it easier to spot problems during development.

<img src="https://github.com/user-attachments/assets/5989cddd-6c36-4ec9-af60-1339a0b661f4" width="600" />

**Common troubleshooting tips:**
- Verify your `.env` file has the correct database credentials
- Check that your MySQL server is running and accessible
- Test actions individually to isolate problems
- Use absolute file paths for images to avoid loading issues

## Acknowledgments

DeckMaster is built with some excellent open source tools:

- Built with [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework
- Uses [QtWebEngine](https://doc.qt.io/qtforpython-6/overviews/qtwebengine-overview.html) for embedded web page support
- Database integration powered by [aiomysql](https://github.com/aio-libs/aiomysql)
- Automation capabilities provided by [PyAutoGUI](https://github.com/asweigart/pyautogui)

---

**DeckMaster** - *Clean, simple control interfaces for any purpose*
