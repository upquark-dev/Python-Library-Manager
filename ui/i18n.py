"""Internationalization (i18n) support — English / Chinese UI strings.

Usage:
    from ui.i18n import tr, set_language, get_language

``tr(key)`` returns the string for the current language. Unknown keys fall
back to English, then to the key itself, so missing entries never crash.
Category names from ``core.library_data.LIBRARY_CATEGORIES`` are translated
via ``tr('cat.' + name)``.
"""

_EN = {
    # Header navigation
    'nav_packages': 'Packages',
    'nav_scan': 'Scan Installed Packages',
    'nav_venv': 'Manage Virtual Envs',
    'nav_python': 'Select Python Version',
    'nav_update': 'Bulk Update',
    'nav_requirements': 'Requirements.txt',
    'nav_settings': 'Settings',
    # Sidebar
    'sidebar_categories': 'Categories',
    # Packages view
    'content_select_category': 'Select a category',
    'btn_select_all': 'Select All',
    'btn_deselect_all': 'Deselect All',
    # Status bar
    'status_python': 'Python: {version} | Path: {path}',
    # Scan view
    'scan_title': '🔍 Scan Installed Packages',
    'scan_desc': 'Scan your system for installed Python packages and see which ones are in our database.',
    # Venv view
    'venv_title': '🔧 Virtual Environment Manager',
    # Python view
    'python_title': '🐍 Select Python Version',
    'python_desc': 'Select which Python installation to use for package management.',
    # Update view
    'update_title': 'Bulk Update Manager',
    'update_desc': 'Check for outdated packages and update them with one click.',
    'mirror_checkbox': 'China Mirrors',
    'mirror_tsinghua': 'Tsinghua University',
    'mirror_douban': 'Douban',
    'mirror_aliyun': 'Alibaba Cloud',
    'mirror_ustc': 'USTC',
    # Requirements view
    'req_title': 'Requirements.txt Manager',
    'req_desc': 'Import from or export to requirements.txt files.',
    # Settings view
    'settings_title': 'Settings',
    'settings_theme': 'Theme',
    'theme_light': 'Light',
    'theme_dark': 'Dark',
    'settings_language': 'Language / 语言',
    'settings_hint': 'Changes take effect immediately and are saved automatically.',
    'settings_close_behavior': 'On Close',
    'close_to_tray': 'Minimize to system tray',
    'close_exit': 'Exit application',
    'tray_minimized_msg': 'Application minimized to system tray. Double-click the tray icon to restore.',
    # Category names (keys are 'cat.' + LIBRARY_CATEGORIES key)
    'cat.GUI Development': 'GUI Development',
    'cat.WhatsApp API': 'WhatsApp API',
    'cat.Artificial Intelligence': 'Artificial Intelligence',
    'cat.Data Science': 'Data Science',
    'cat.ERPNext / Frappe': 'ERPNext / Frappe',
    'cat.Networking / Automation': 'Networking / Automation',
    'cat.Web Development': 'Web Development',
    'cat.General Python Packages': 'General Python Packages',
    'cat.Database': 'Database',
    'cat.Security & Cryptography': 'Security & Cryptography',
    'cat.Testing & QA': 'Testing & QA',
    'cat.DevOps & CI/CD': 'DevOps & CI/CD',
    'cat.API Development': 'API Development',
    'cat.Data Processing & ETL': 'Data Processing & ETL',
    'cat.File & Document Processing': 'File & Document Processing',
    'cat.Image & Video Processing': 'Image & Video Processing',
    'cat.Audio Processing': 'Audio Processing',
    'cat.Game Development': 'Game Development',
    'cat.Desktop Automation': 'Desktop Automation',
    'cat.Email & Communication': 'Email & Communication',
    'cat.Code Quality & Formatting': 'Code Quality & Formatting',
    'cat.Blockchain & Cryptocurrency': 'Blockchain & Cryptocurrency',
    'cat.IoT & Hardware': 'IoT & Hardware',
    'cat.Scientific Computing': 'Scientific Computing',
    'cat.CLI Tools & Productivity': 'CLI Tools & Productivity',
}

_ZH = {
    # Header navigation
    'nav_packages': '包管理',
    'nav_scan': '扫描已安装包',
    'nav_venv': '虚拟环境管理',
    'nav_python': '选择 Python 版本',
    'nav_update': '批量更新',
    'nav_requirements': 'Requirements.txt',
    'nav_settings': '设置',
    # Sidebar
    'sidebar_categories': '分类',
    # Packages view
    'content_select_category': '请选择一个分类',
    'btn_select_all': '全选',
    'btn_deselect_all': '取消全选',
    # Status bar
    'status_python': 'Python: {version} | 路径: {path}',
    # Scan view
    'scan_title': '🔍 扫描已安装的包',
    'scan_desc': '扫描系统中已安装的 Python 包，并查看哪些在我们的数据库中。',
    # Venv view
    'venv_title': '🔧 虚拟环境管理器',
    # Python view
    'python_title': '🐍 选择 Python 版本',
    'python_desc': '选择用于包管理的 Python 安装。',
    # Update view
    'update_title': '批量更新管理器',
    'update_desc': '检查过时的包并一键更新。',
    'mirror_checkbox': '国内源',
    'mirror_tsinghua': '清华大学',
    'mirror_douban': '豆瓣',
    'mirror_aliyun': '阿里云',
    'mirror_ustc': '中国科学技术大学',
    # Requirements view
    'req_title': 'Requirements.txt 管理器',
    'req_desc': '从 requirements.txt 文件导入或导出。',
    # Settings view
    'settings_title': '设置',
    'settings_theme': '主题',
    'theme_light': '浅色',
    'theme_dark': '深色',
    'settings_language': '语言 / Language',
    'settings_hint': '更改立即生效并自动保存。',
    'settings_close_behavior': '关闭时',
    'close_to_tray': '最小化到系统托盘',
    'close_exit': '退出程序',
    'tray_minimized_msg': '程序已最小化到系统托盘，双击托盘图标可恢复。',
    # Category names
    'cat.GUI Development': 'GUI 开发',
    'cat.WhatsApp API': 'WhatsApp API',
    'cat.Artificial Intelligence': '人工智能',
    'cat.Data Science': '数据科学',
    'cat.ERPNext / Frappe': 'ERPNext / Frappe',
    'cat.Networking / Automation': '网络 / 自动化',
    'cat.Web Development': 'Web 开发',
    'cat.General Python Packages': '常用 Python 包',
    'cat.Database': '数据库',
    'cat.Security & Cryptography': '安全与加密',
    'cat.Testing & QA': '测试与质量',
    'cat.DevOps & CI/CD': 'DevOps 与 CI/CD',
    'cat.API Development': 'API 开发',
    'cat.Data Processing & ETL': '数据处理与 ETL',
    'cat.File & Document Processing': '文件与文档处理',
    'cat.Image & Video Processing': '图像与视频处理',
    'cat.Audio Processing': '音频处理',
    'cat.Game Development': '游戏开发',
    'cat.Desktop Automation': '桌面自动化',
    'cat.Email & Communication': '邮件与通信',
    'cat.Code Quality & Formatting': '代码质量与格式化',
    'cat.Blockchain & Cryptocurrency': '区块链与加密货币',
    'cat.IoT & Hardware': '物联网与硬件',
    'cat.Scientific Computing': '科学计算',
    'cat.CLI Tools & Productivity': 'CLI 工具与效率',
}

_LANGUAGES = {'en': _EN, 'zh': _ZH}
_current_language = 'en'


def get_language() -> str:
    """Return the current language code ('en' or 'zh')."""
    return _current_language


def set_language(language: str) -> None:
    """Set the current language; unknown codes are ignored."""
    global _current_language
    if language in _LANGUAGES:
        _current_language = language


def tr(key: str) -> str:
    """Translate ``key`` into the current language.

    Falls back to English, then to the key itself.
    """
    table = _LANGUAGES.get(_current_language, _EN)
    return table.get(key) or _EN.get(key) or key
