# 📦 Python Library Manager

<div align="center">

![Version](https://img.shields.io/badge/version-2.6-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)

**A modern, professional GUI application for managing Python packages with advanced features**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Screenshots](#-screenshots) • [Contributing](#-contributing)

</div>

---

## 🚀 Features

### **Core Package Management**
- 📦 **220+ Python Packages** organized in 27 categories
- ⚡ **Bulk Install/Uninstall** - Select multiple packages at once
- 🔍 **Smart Caching** - 16x faster performance with O(1) lookups
- 📊 **Real-time Logging** - Watch installation progress live
- ✅ **Installation Status** - Visual indicators for installed packages
- 🎨 **Modern UI** - Clean, professional interface with tabbed navigation

### **10 Advanced Features**

#### 1. **📋 Package Details**
View comprehensive package information:
- Version, author, license, homepage
- Complete dependency tree
- Reverse dependencies
- Installation location
- Copy to clipboard

#### 2. **🔧 Virtual Environment Manager**
Full virtual environment management:
- Create new environments
- Monitor disk space usage
- View package counts
- Get activation commands
- Delete environments safely

#### 3. **📌 Package Version Selector**
Install any package version:
- Browse all available versions from PyPI
- Visual indicators (★ CURRENT, ⭐ LATEST)
- Upgrade/downgrade packages
- Version comparison

#### 4. **🌳 Dependency Viewer**
Visualize package dependencies:
- Tree view (3 levels deep)
- Installation status for each dependency
- Reverse dependency checking
- Circular dependency detection
- Export to clipboard

#### 5. **🐍 Multi-Python Version Support**
Switch between Python installations:
- Auto-detect all Python versions
- Windows (py launcher, registry, common paths)
- Linux (system paths, pyenv, alternatives)
- macOS (Homebrew, framework, pyenv)
- Mark virtual environments
- Switch versions seamlessly

#### 6. **🔔 System Tray Integration**
Background operations:
- Minimize to system tray
- Desktop notifications
- Quick access menu
- Keep app running when closed

#### 7. **⬆️ Bulk Update Manager**
Update all packages at once:
- Check for outdated packages
- View current → latest versions
- Update all with one click
- Update individual packages
- Real-time progress tracking

#### 8. **📄 Requirements.txt Manager**
Import/Export package lists:
- Import from requirements.txt
- Export all installed packages
- Export selected packages
- Include/exclude version numbers
- Install all from file

#### 9. **🔍 Scan Installed Packages**
Discover what's installed:
- Scan system for installed packages
- Match with database categories
- Show package details
- Package count summary

#### 10. **⚙️ Settings (Theme & Language)**
Customize your experience:
- Light/Dark theme switch
- Multi-language UI (English / 中文), applied instantly
- Preferences persist across restarts
- Consistent blue color scheme

---

## 📂 Package Categories (27)

<details>
<summary>Click to expand all categories</summary>

1. **GUI Development** - PyQt6, Tkinter, Kivy, wxPython, PySide6, DearPyGui
2. **WhatsApp API** - yowsup, WhatsApp Cloud API, PyWhatKit, Selenium
3. **Artificial Intelligence** - PyTorch, TensorFlow, Transformers, OpenAI, LangChain
4. **Data Science** - pandas, numpy, scikit-learn, matplotlib, seaborn, plotly
5. **ERPNext / Frappe** - frappe-client, frappe-bench, erpnext-client
6. **Networking / Automation** - paramiko, netmiko, scapy, ansible, fabric
7. **Web Development** - Flask, Django, FastAPI, Scrapy, Streamlit
8. **General Python** - requests, pillow, pyinstaller, pytest, black
9. **Database** - MongoDB, PostgreSQL, MySQL, SQLAlchemy, Redis
10. **Security & Cryptography** - cryptography, bcrypt, PyJWT, PyOTP
11. **Computer Vision** - OpenCV, Pillow, scikit-image
12. **Natural Language Processing** - NLTK, spaCy, TextBlob
13. **Game Development** - pygame, panda3d, arcade
14. **Audio/Video Processing** - moviepy, pydub, ffmpeg-python
15. **Testing** - pytest, unittest, selenium, coverage
16. **DevOps** - docker, kubernetes, ansible
17. **Cloud Services** - boto3, azure, google-cloud
18. **API Development** - FastAPI, Flask-RESTful, Django REST
19. **Task Scheduling** - Celery, APScheduler, schedule
20. **File Processing** - openpyxl, PyPDF2, python-docx
21. **Email** - smtplib, imaplib, yagmail
22. **PDF Tools** - ReportLab, PyPDF2, pdfplumber
23. **Scraping** - BeautifulSoup, Scrapy, Selenium
24. **Visualization** - matplotlib, seaborn, plotly, bokeh
25. **Math & Science** - scipy, sympy, numpy
26. **Image Processing** - Pillow, opencv-python, imageio
27. **Utilities** - tqdm, colorama, python-dotenv

</details>

---

## 🖼️ Screenshots

### Main Interface
```
┌────────────────────────────────────────────────────────────────────────┐
│ [Packages] [Scan] [Virtual Envs] [Python] [Bulk Update] [...] [Settings] │
├─────────────┬──────────────────────────────────────────────────────────┤
│ Categories  │  GUI Development                                         │
│ ─────────── │  ──────────────────────────────────────────────────────  │
│             │                                                            │
│ GUI Dev     │  ☐ PyQt6                    [Versions] [Details] [Deps]  │
│ WhatsApp    │     Professional cross-platform GUI framework             │
│ AI/ML       │     ✓ INSTALLED                                          │
│ Data Sci    │                                                            │
│ Web Dev     │  ☐ Kivy                     [Versions] [Details] [Deps]  │
│ Database    │     Multitouch application framework                     │
│ Security    │                                                            │
│ ...         │                                                            │
│             │  [Select All] [Deselect All] [Install] [Uninstall]       │
├─────────────┴──────────────────────────────────────────────────────────┤
│ 📝 Installation Logs:                                                  │
│ Installing PyQt6...                                                    │
│ Successfully installed PyQt6-6.6.0                                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📥 Installation

### Prerequisites
- **Python 3.8+** installed
- **pip** package manager
- **Git** (optional)

### Quick Start

#### Windows
```bash
# Clone the repository
git clone https://github.com/yourusername/Python-Library-Manager.git
cd Python-Library-Manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Linux / macOS
```bash
# Clone the repository
git clone https://github.com/yourusername/Python-Library-Manager.git
cd Python-Library-Manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
```

### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## 🎯 Usage

### Basic Usage

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Select Category** - Click on any category in the sidebar

3. **Choose Packages** - Check boxes next to packages you want

4. **Install/Uninstall** - Click the Install or Uninstall button

5. **Monitor Progress** - Watch real-time logs at the bottom

### Advanced Features

#### 🔍 Check Package Details
- Click the **"Details"** button next to any package
- View complete information including dependencies

#### 📌 Install Specific Version
- Click **"Versions"** button
- Select the version you want
- Click Install

#### 🌳 View Dependencies
- Click **"Dependencies"** button
- Explore the full dependency tree
- Check what else needs to be installed

#### 🔧 Manage Virtual Environments
- Click **"Manage Virtual Envs"** tab
- Create new environments
- View existing environments
- Delete environments

#### 🐍 Switch Python Version
- Click **"Select Python Version"** tab
- Choose from detected Python installations
- Click "Select This Python"

#### ⬆️ Update All Packages
- Click **"Bulk Update"** tab
- Click "Check for Updates"
- Review outdated packages
- Click "Update All"

#### 📄 Export/Import Requirements
- Click **"Requirements.txt"** tab
- **Export**: Save installed packages to file
- **Import**: Install packages from file

#### 🔍 Scan Installed Packages
- Click **"Scan Installed Packages"** tab
- Click "Start Scan"
- View all installed packages with categories

---

## 🏗️ Project Structure

```
Python-Library-Manager/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── LICENSE                          # MIT License
├── README.md                        # This file
├── AGENTS.md                        # AI-agent guidance for this repo
├── PythonLibraryManager.spec        # PyInstaller build spec
├── .gitignore                       # Git ignore rules
│
├── core/                            # Core functionality (9 modules)
│   ├── __init__.py
│   ├── installer.py                # Package installation engine
│   ├── library_data.py             # 220+ packages database (27 categories)
│   ├── venv_manager.py             # Virtual environment management
│   ├── dependency_manager.py       # Dependency analysis
│   ├── package_version_manager.py  # Version management
│   ├── python_detector.py          # Python installation detection
│   ├── update_manager.py           # Bulk update functionality
│   ├── requirements_manager.py     # Requirements.txt handling
│   └── runtime.py                  # Frozen-exe aware interpreter resolution
│
├── ui/                              # User interface (9 modules)
│   ├── __init__.py
│   ├── main_window.py              # Main application window (tabbed interface)
│   ├── theme_manager.py            # Theme switching
│   ├── i18n.py                     # en/zh translations (tr() helper)
│   ├── package_details_dialog.py   # Package information dialog
│   ├── version_selector_dialog.py  # Version selector
│   ├── dependency_viewer_dialog.py # Dependency tree viewer
│   ├── venv_manager_dialog.py      # Virtual env manager (legacy)
│   ├── python_selector_dialog.py   # Python selector (legacy)
│   └── system_tray.py              # System tray integration
│
└── tests/                           # Test suite (53 cases, core-only, Qt-free)
    ├── conftest.py                  # sys.path bootstrap
    ├── test_installer.py
    ├── test_dependency_manager.py
    ├── test_library_data.py
    ├── test_package_version_manager.py
    ├── test_requirements_manager.py
    └── test_venv_manager.py
```

---

## ⚙️ Configuration

### Adding Custom Packages

Edit `core/library_data.py`:

```python
LIBRARY_CATEGORIES = {
    "Your Category": [
        {
            "name": "package-name",
            "description": "Package description",
            "install_cmd": "pip install package-name",
            "docs": "https://docs.example.com"
        }
    ]
}
```

### Customizing Theme

Edit `ui/theme_manager.py` to modify colors:

```python
# Primary color
"background-color: #3498db;"  # Blue

# Change to your preferred color
"background-color: #e74c3c;"  # Red
```

---

## 🐛 Troubleshooting

### Issue: PyQt6 not installing

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install PyQt6
pip install PyQt6 --no-cache-dir
```

### Issue: Permission denied

**Windows:** Run as Administrator
**Linux/Mac:** Use virtual environment or:
```bash
pip install --user -r requirements.txt
```

### Issue: Python not detected

**Solution:** Make sure Python is in your PATH:
```bash
# Windows
where python

# Linux/Mac
which python3
```

### Issue: Application won't start

**Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "Add AmazingFeature"
   ```
4. **Push** to your branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Python-Library-Manager.git
cd Python-Library-Manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install in development mode
pip install -e .

# Make changes and test
python main.py
```

---

## 📝 Version History

### **Version 2.6** (Current) - 2026
- ✅ New Settings view: theme + language (English / 中文) with live switching
- ✅ Full UI internationalization framework (`ui/i18n.py`)
- ✅ China mirror sources localized in both languages
- ✅ Fixed critical bug: packaged exe spawned itself infinitely
- ✅ Added automated test suite (53 cases covering `core/`)
- ✅ Repository cleanup + `.gitignore`

### **Version 2.5** - 2024
- ✅ Added Bulk Update Manager
- ✅ Added Requirements.txt Manager
- ✅ All features embedded (no popups)
- ✅ Consistent blue theme
- ✅ Removed all icons from buttons
- ✅ 7 tabbed views for easy navigation

### **Version 2.1** - 2024
- ✅ Multi-Python Version Support
- ✅ Auto-detect Python installations
- ✅ Python switcher with detailed info

### **Version 2.0** - 2024
- ✅ Package Details Dialog
- ✅ Virtual Environment Manager
- ✅ Package Version Selector
- ✅ Dependency Viewer
- ✅ System Tray Integration

### **Version 1.5** - 2024
- ✅ Scan functionality
- ✅ Performance improvements (caching)
- ✅ Theme switching fixes

### **Version 1.0** - 2024
- ✅ Initial release
- ✅ 27 categories, 220+ packages
- ✅ Basic install/uninstall
- ✅ Light/Dark themes

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 DevTools Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 👨‍💻 Authors

- **Original author:** DevTools Team (Umair Wali)
- **Maintainer:** upquark

---

## 🌟 Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Professional GUI framework
- Inspired by package managers like npm, pip, and apt
- Icons from Material Design
- Thanks to all contributors!

---

## 📊 Statistics

- **Total Files:** 26 Python files
- **Lines of Code:** 4,500+
- **Categories:** 27
- **Packages:** 220+
- **Features:** 10 major features
- **Tabs:** 7 navigation tabs (incl. Settings)
- **Languages:** English / 中文
- **Tests:** 53 automated cases
- **Performance:** 16x faster with caching

---

## 🚀 Roadmap

### Planned Features
- [ ] Package search functionality
- [ ] Export/import configurations
- [ ] More UI languages (community contributions welcome)
- [ ] Package comparison tool
- [ ] Installation history
- [ ] Scheduled updates

### Completed Features
- [x] Package version selection ✅
- [x] Virtual environment management ✅
- [x] Dependency viewer ✅
- [x] System tray integration ✅
- [x] Package details dialog ✅
- [x] Multi-Python support ✅
- [x] Bulk update manager ✅
- [x] Requirements.txt manager ✅
- [x] Multi-language UI (English / 中文) ✅

---

## 📞 Support

### Get Help
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/Python-Library-Manager/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/Python-Library-Manager/discussions)
- 📧 **Email:** support@devtools.com

### Resources
- 📖 **Documentation:** [Wiki](https://github.com/yourusername/Python-Library-Manager/wiki)
- 🎥 **Video Tutorial:** Coming soon
- 📚 **Examples:** [Examples folder](examples/)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Umair Wali** · Maintained by **upquark**

[⬆ Back to Top](#-python-library-manager)

</div>
