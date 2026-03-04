# Boop

A Python-based text manipulation tool inspired by the original [Boop](https://github.com/IvanMathy/Boop) macOS app.

**GUI-only application** - No command line interface, just like the original Boop.app.

---

## Features

- 🎨 **Native GUI Interface** - Tkinter-based UI mimicking Boop.app design
- ⌨️ **Keyboard Shortcuts** - Customizable shortcuts
- 📁 **Built-in Configuration** - Config stored in `config.json`
- 🔧 **Preferences Window** - GUI for all settings
- 🐍 **Python Scripts** - Write text manipulation scripts in Python
- 🎯 **Custom Script Directories** - Configure multiple script locations
- 🔄 **Isolated Execution** - Scripts run in subprocesses for safety
- 📝 **Line Numbers** - Editor with line number display
- ↩️ **Undo/Redo** - History-based undo/redo functionality
- 🔍 **Script Search** - Search scripts by name and tags
- 📊 **Status Bar** - Shows cursor position and character count
- ⚡ **Fast Startup** - Background script metadata loading
- 🗄️ **Metadata Caching** - JSON-based metadata cache for faster loading

---

## Quick Start

### Installation

```bash
cd /path/to/BoopPython

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 -m boop
```

### Requirements

- Python 3.9+
- Tkinter (usually included with Python)

### Build Standalone App

See [BUILD.md](BUILD.md) for detailed build instructions.

```bash
# Build for current platform
./build.sh

# Output: dist/Boop-1.0.0-macos.dmg (or .tar.gz / .zip)
```

---

## Usage

### Launch the Application

```bash
python3 -m boop
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+B` (or `Ctrl+B`) | Open Script Picker |
| `Cmd+,` | Open Preferences |
| `Cmd+Q` | Quit Application |
| `Cmd+Z` (or `Ctrl+Z`) | Undo |
| `Cmd+Shift+Z` (or `Ctrl+Shift+Z`) | Redo |
| `Cmd+X` (or `Ctrl+X`) | Cut |
| `Cmd+C` (or `Ctrl+C`) | Copy |
| `Cmd+V` (or `Ctrl+V`) | Paste |
| `Cmd+A` (or `Ctrl+A`) | Select All |

### Menu Options

**Boop Menu:**
- About Boop - Application information
- Preferences... - Open settings window
- Quit - Exit the application

**Edit Menu:**
- Undo - Undo last action
- Redo - Redo last action
- Cut/Copy/Paste - Standard editing
- Select All - Select all text

**Script Menu:**
- Run Script - Open script selection dialog

---

## Configuration

Configuration is stored in `config.json` in the project root directory.

### Configurable Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `script_directories` | List of script directories | `[boop/scripts]` |
| `python_path` | Python interpreter path | Current Python |
| `window_width` | Window width | 800 |
| `window_height` | Window height | 600 |
| `maximize_window` | Whether to maximize window on startup | false |
| `font_family` | Editor font family | Menlo |
| `font_size` | Editor font size | 14 |
| `shortcuts` | Keyboard shortcuts configuration | Built-in shortcuts |

### Modifying Configuration

Use the **Preferences window** (`Cmd+,`) to modify settings:

1. **General Tab**: Set Python interpreter path and window settings
2. **Scripts Tab**: Add/remove script directories and install dependencies
3. **Editor Tab**: Configure font settings

---

## Writing Scripts

Each Python script must have:
1. A module-level docstring with JSON metadata
2. A `main(state)` function

### Script Template

```python
'''
{
    "api": 1,
    "name": "My Script",
    "description": "What this script does",
    "author": "Your Name",
    "icon": "star",
    "tags": ["tag1", "tag2"],
    "dependencies": ["requests", "beautifulsoup4"],
    "help": "Detailed help text."
}
'''

def main(state):
    """Main function that processes text."""
    # Get input text
    text = state.text
    
    # Process the text
    result = text.upper()
    
    # Set output
    state.text = result
    
    # Show message
    state.post_info("Text converted!")
```

### ScriptExecution API

| Property/Method | Description |
|-----------------|-------------|
| `state.text` | Get/set current text (selection or full) |
| `state.full_text` | Get/set entire editor content |
| `state.selection` | Get/set selected text |
| `state.insert(str)` | Insert text at cursor |
| `state.post_info(msg)` | Show info message |
| `state.post_error(msg)` | Show error message |

### Dependency Management

Boop Python supports managing dependencies for scripts. You can define dependencies in the script metadata, and the application will install them for you.

#### Adding Dependencies to Scripts

Add a `dependencies` field to your script's metadata: 

```python
'''
{
    "api": 1,
    "name": "My Script",
    "description": "What this script does",
    "tags": ["example"],
    "dependencies": ["requests==2.31.0", "beautifulsoup4==4.12.2"],
    "help": "Detailed help text."
}
'''
```

#### Installing Dependencies

To install dependencies:

1. Open the Preferences window (`Cmd+,`)
2. Go to the **Scripts** tab
3. Click the **Install All Dependencies** button
4. The application will automatically install all dependencies defined in your scripts

#### How It Works

- Dependencies are installed in the application's internal Python environment
- This keeps your system Python environment clean and isolated
- Dependencies are only installed once, and reused across all scripts
- The application will use the internal Python environment for script execution

### Script System Overview

Boop Python comes with a variety of built-in scripts that cover common text manipulation tasks, including:

- **Text Transformation**: Case conversion, whitespace handling, line manipulation
- **Formatting**: JSON, YAML, XML, CSS, and other file formats
- **Encoding/Decoding**: Base64, URL encoding, ASCII/Unicode conversion
- **Data Analysis**: Character, word, and line counting
- **Utilities**: Hash generation, sequence number insertion, text comparison

The script system is extensible, allowing you to add your own custom scripts to handle specific text processing needs. All scripts run in isolated subprocesses for safety and stability.

---

## Project Structure

```
Boop/
├── boop/
│   ├── __init__.py          # Package init
│   ├── __main__.py          # GUI entry point
│   ├── config/
│   │   └── settings.py      # ConfigManager, BoopConfig
│   ├── core/
│   │   ├── __init__.py      # Core package init
│   │   ├── cache.py         # Metadata cache
│   │   ├── event.py         # Event system
│   │   ├── logging.py       # Logging system
│   │   ├── path.py          # Path utilities
│   │   ├── script.py        # Script manager
│   │   ├── script_metadata.py # Script metadata
│   │   ├── script_wrapper.py # Script execution wrapper
│   │   └── utils.py         # Utility functions
│   ├── scripts/             # Default script directory
│   ├── tests/               # Test files
│   ├── ui/
│   │   ├── __init__.py      # UI package init
│   │   ├── editor.py        # Editor component
│   │   ├── main.py          # Main application window
│   │   ├── preferences.py   # Preferences window
│   │   └── script_picker.py # Script selection dialog
├── config.json              # Application configuration
├── icons/                   # Icon resources
├── build.sh                 # Build script
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── SIMPLIFIED_DESIGN.md     # Design document
└── REQUIREMENTS.md          # Business requirements
```

---

## Differences from Original Boop

| Feature | Original Boop | Boop Python |
|---------|--------------|-------------|
| Script Language | JavaScript | Python |
| Execution | JavaScriptCore (in-process) | Subprocess (isolated) |
| Configuration | macOS Preferences | JSON config file |
| UI | Native macOS (Swift) | Tkinter (Cross-platform) |
| Script Path | ~/Library/... | Configurable via GUI |
| CLI Support | No | No (GUI only) |

---

## Documentation

- **[README.md](README.md)** - This file (overview and quick start)
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - Business requirements document
- **[SIMPLIFIED_DESIGN.md](SIMPLIFIED_DESIGN.md)** - Technical design document

---

## License

Inspired by the original Boop project. See the original [LICENSE](https://github.com/IvanMathy/Boop/blob/main/LICENSE).
