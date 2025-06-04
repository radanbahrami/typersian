"""
tray.py

Provides the system tray icon, menu, and About dialog for the Typersian application.
"""

from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox,
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor, QFontDatabase, QPainter
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.Qt import QDesktopServices
from version import __version__
import sys
import os

def get_asset_path(filename):
    """Get path to asset file, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as an executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'assets', filename)

class AboutDialog(QDialog):
    """
    Custom About dialog for Typersian.
    Displays app logo, version, usage instructions, clickable links, and copyright.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Typersian")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 600)
        self.setWindowIcon(QIcon(get_asset_path("logo.png")))

        # Logo
        logo = QLabel()
        pixmap = QPixmap(get_asset_path("logo.png")).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)

        # Project name
        title = QLabel("<b>Typersian</b>")
        title.setAlignment(Qt.AlignCenter)

        # Version and description
        desc = QLabel(
            "Lets you convert Finglish to Persian<br>anywhere on your device.<br>"
            "<br><span style='font-size:10pt;'>How to Use:</span><br>"
            "<span style='font-size:10pt;'>1. Select and <b>copy</b> text (Ctrl + C)</span><br>"
            "<span style='font-size:10pt;'>2. Press <b>Ctrl + F9</b> to convert</span><br>"
            "<span style='font-size:10pt;'>3. <b>Paste</b> the result (Ctrl + V)</span><br>"
        )
        desc.setTextFormat(Qt.RichText)
        desc.setAlignment(Qt.AlignCenter)

        # Disclaimer
        disclaimer = QLabel(
            "Typersian can make mistakes. Review results before using."
        )
        disclaimer.setTextFormat(Qt.RichText)
        disclaimer.setAlignment(Qt.AlignCenter)
        disclaimer.setStyleSheet("font-size: 9pt;")

        # Copyright and license notice
        copyright_notice = QLabel(
            "<style>a { color: #fff; }</style>"
            "Typersian © 2025 Radan Bahrami<br>"
            "Licensed under the <a href='https://www.gnu.org/licenses/gpl-3.0.en.html'>GNU GPL v3</a> - No warranty provided.<br>"
            "Additional terms apply—see LICENSE.txt<br>"
        )
        copyright_notice.setTextFormat(Qt.RichText)
        copyright_notice.setAlignment(Qt.AlignCenter)
        copyright_notice.setStyleSheet("font-size: 9pt;")
        copyright_notice.setOpenExternalLinks(True)
        copyright_notice.setToolTip("See license details")

        # Version (move this to the bottom)
        version_label = QLabel(f"v{__version__}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 9pt;")

        # GitHub logo as clickable label (opens project page)
        github_logo = QLabel()
        svg_renderer = QSvgRenderer(get_asset_path("github-mark-white.svg"))
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()
        github_logo.setPixmap(pixmap)
        github_logo.setAlignment(Qt.AlignCenter)
        github_logo.setCursor(QCursor(Qt.PointingHandCursor))
        github_logo.setToolTip("Typersian on GitHub")

        def open_github():
            QDesktopServices.openUrl(QUrl("https://github.com/radanbahrami"))

        github_logo.mousePressEvent = lambda event: open_github()

        # An author logo as clickable label (opens author's website)
        author_logo = QLabel()
        svg_renderer = QSvgRenderer(get_asset_path("account_circle_24dp_E3E3E3_FILL1_wght400_GRAD0_opsz24.svg"))
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()
        author_logo.setPixmap(pixmap)
        author_logo.setAlignment(Qt.AlignCenter)
        author_logo.setCursor(QCursor(Qt.PointingHandCursor))
        author_logo.setToolTip("Author's Website")

        def open_website():
            QDesktopServices.openUrl(QUrl("https://radanbahrami.com"))

        author_logo.mousePressEvent = lambda event: open_website()

        # Create a horizontal layout for the icons
        icon_hbox = QHBoxLayout()
        icon_hbox.setAlignment(Qt.AlignCenter)
        icon_hbox.addWidget(github_logo)
        icon_hbox.addWidget(author_logo)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("font-size: 9pt;")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setFixedWidth(50)

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(logo)
        vbox.addWidget(title)
        vbox.addWidget(desc)
        vbox.addSpacing(15)
        vbox.addWidget(disclaimer)
        vbox.addSpacing(-20)
        vbox.addWidget(copyright_notice)
        vbox.addSpacing(-20)
        vbox.addLayout(icon_hbox)
        vbox.addSpacing(-20)
        vbox.addWidget(version_label)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(ok_btn)
        hbox.addStretch()
        vbox.addLayout(hbox)
        self.setLayout(vbox)

def tray(on_quit_callback):
    """
    Initializes and runs the system tray icon with menu actions.
    Applies dark theme, handles About dialog, and quit action.
    """
    QApplication.setQuitOnLastWindowClosed(False)
    app = QApplication(sys.argv)

    QFontDatabase.addApplicationFont(get_asset_path("OpenSans-Regular.ttf"))
    app.setFont(QFont("Open Sans"))

    dark_stylesheet = """
        QWidget {
            background-color: #232629;
            color: #f0f0f0;
            font-family: 'Open Sans', 'Segoe UI', 'Arial', sans-serif;
        }
        QLabel {
            color: #f0f0f0;
        }
        QPushButton {
            background-color: #393c3f;
            color: #f0f0f0;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 4px 12px;
        }
        QPushButton:hover {
            background-color: #505357;
        }
        QDialog {
            background-color: #232629;
        }
        QToolTip {
            background-color: #393c3f;
            color: #f0f0f0;
            padding: 4px;
            font-family: 'Open Sans', 'Segoe UI', 'Arial', sans-serif;
            font-size: 8pt;
            border: none;
        }
    """
    app.setStyleSheet(dark_stylesheet)

    # Check if the system supports tray icons
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray is not available!")
        sys.exit(1)

    # Create the system tray icon
    tray_icon = QSystemTrayIcon()
    tray_icon.setIcon(QIcon(get_asset_path("logo.png")))

    # Create a menu for the tray icon
    menu = QMenu()

    # Add actions to the menu
    def show_about():
        dlg = AboutDialog()
        dlg.exec_()

    about_action = QAction("About")
    about_action.triggered.connect(show_about)

    menu.addAction(about_action)

    quit_action = QAction("Quit")
    quit_action.triggered.connect(on_quit_callback)

    menu.addAction(quit_action)


    # Set the menu to the tray icon
    tray_icon.setContextMenu(menu)

    # Show the tray icon
    tray_icon.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    tray(lambda: print("Exiting..."))
    