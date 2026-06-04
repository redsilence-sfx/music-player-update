import json
import os
from dataclasses import dataclass

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)

try:
    import logger
except Exception:  # pragma: no cover
    logger = None


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "theme_config.json")


@dataclass(frozen=True)
class AppTheme:
    key: str
    name: str
    description: str
    bg: str
    bg2: str
    surface: str
    surface2: str
    card: str
    border: str
    text: str
    muted: str
    accent: str
    accent2: str
    button_text: str
    danger: str = "#EF4444"
    success: str = "#22C55E"


class ThemeManager:
    """
    Theme customization engine untuk SoundWave.

    Desainnya modular: tidak mengubah file .ui dan tidak menimpa fitur
    dynamic album gradient. Theme disimpan di config/theme_config.json.
    """

    THEMES = {
        "purple_dark": AppTheme(
            key="purple_dark",
            name="Purple Dark",
            description="Default SoundWave vibe",
            bg="#090914",
            bg2="#11111F",
            surface="#141420",
            surface2="#1F1B2E",
            card="rgba(20, 20, 32, 228)",
            border="rgba(196, 181, 253, 58)",
            text="#F8FAFC",
            muted="#A1A1AA",
            accent="#A78BFA",
            accent2="#C4B5FD",
            button_text="#0A0A0F",
        ),
        "midnight_blue": AppTheme(
            key="midnight_blue",
            name="Midnight Blue",
            description="Clean blue professional",
            bg="#07111F",
            bg2="#0B172A",
            surface="#0F1E33",
            surface2="#122845",
            card="rgba(15, 30, 51, 230)",
            border="rgba(96, 165, 250, 64)",
            text="#EFF6FF",
            muted="#93A4B8",
            accent="#60A5FA",
            accent2="#93C5FD",
            button_text="#06111F",
        ),
        "amoled_black": AppTheme(
            key="amoled_black",
            name="AMOLED Black",
            description="Deep black minimal",
            bg="#000000",
            bg2="#050505",
            surface="#080808",
            surface2="#111111",
            card="rgba(8, 8, 8, 238)",
            border="rgba(255, 255, 255, 36)",
            text="#FFFFFF",
            muted="#A3A3A3",
            accent="#FFFFFF",
            accent2="#E5E5E5",
            button_text="#000000",
        ),
        "aurora_green": AppTheme(
            key="aurora_green",
            name="Aurora Green",
            description="Fresh neon green accent",
            bg="#06130E",
            bg2="#0A1F17",
            surface="#0E2A20",
            surface2="#123527",
            card="rgba(14, 42, 32, 230)",
            border="rgba(52, 211, 153, 60)",
            text="#ECFDF5",
            muted="#9CC9B9",
            accent="#34D399",
            accent2="#6EE7B7",
            button_text="#04130D",
        ),
        "sakura_pink": AppTheme(
            key="sakura_pink",
            name="Sakura Pink",
            description="Soft modern pink",
            bg="#160B12",
            bg2="#23111D",
            surface="#2B1725",
            surface2="#3A2032",
            card="rgba(43, 23, 37, 230)",
            border="rgba(244, 114, 182, 60)",
            text="#FFF1F7",
            muted="#D6A7BC",
            accent="#F472B6",
            accent2="#FBCFE8",
            button_text="#160B12",
        ),
        "light_clean": AppTheme(
            key="light_clean",
            name="Light Clean",
            description="Bright clean dashboard",
            bg="#F8FAFC",
            bg2="#EEF2FF",
            surface="#FFFFFF",
            surface2="#F1F5F9",
            card="rgba(255, 255, 255, 242)",
            border="rgba(99, 102, 241, 68)",
            text="#0F172A",
            muted="#64748B",
            accent="#6366F1",
            accent2="#818CF8",
            button_text="#FFFFFF",
        ),
    }

    DEFAULT_THEME = "purple_dark"

    def __init__(self):
        self.current_key = self.load_theme_key()

    def load_theme_key(self) -> str:
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                key = data.get("theme", self.DEFAULT_THEME)
                if key in self.THEMES:
                    return key
        except Exception as exc:
            if logger:
                logger.warn(f"Theme config load failed: {exc}")
        return self.DEFAULT_THEME

    def save_theme_key(self, key: str):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"theme": key}, f, indent=2)
        except Exception as exc:
            if logger:
                logger.warn(f"Theme config save failed: {exc}")

    def get_theme(self, key: str | None = None) -> AppTheme:
        key = key or self.current_key
        return self.THEMES.get(key, self.THEMES[self.DEFAULT_THEME])

    def apply_to(self, window, key: str | None = None, save: bool = True) -> str:
        theme = self.get_theme(key)
        self.current_key = theme.key

        if save:
            self.save_theme_key(theme.key)

        # Simpan stylesheet awal sekali saja agar apply berulang tidak numpuk.
        if not hasattr(window, "_soundwave_base_stylesheet"):
            window._soundwave_base_stylesheet = window.styleSheet()

        window._active_theme_key = theme.key
        window._active_theme = theme
        window.setStyleSheet(window._soundwave_base_stylesheet + "\n" + self.build_qss(theme))

        self._apply_direct_widget_styles(window, theme)

        # Dynamic album gradient tetap boleh menang atas card now playing.
        if hasattr(window, "ui_enhancer"):
            try:
                window.ui_enhancer.apply_album_gradient()
            except Exception as exc:
                if logger:
                    logger.warn(f"Theme album gradient refresh failed: {exc}")

        if logger:
            logger.info(f"Theme applied: {theme.name}")
        return theme.name

    def build_qss(self, t: AppTheme) -> str:
        return f"""
        QMainWindow {{
            background-color: {t.bg};
        }}

        QWidget#centralwidget {{
            background-color: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {t.bg},
                stop:1 {t.bg2}
            );
            color: {t.text};
        }}

        QFrame#topNavBar {{
            background-color: rgba(8, 8, 14, 226);
            border-bottom: 1px solid {t.border};
        }}

        QWidget#topBrand,
        QWidget#topNavButtons {{
            background-color: transparent;
        }}

        QLabel {{
            color: {t.text};
        }}

        QLabel#appSubtitle,
        QLabel#artistName,
        QLabel#albumName,
        QLabel#lblQueueSub,
        QLabel#lblSearchHint,
        QLabel#timeElapsed,
        QLabel#timeDuration {{
            color: {t.muted};
        }}

        QWidget#nowPlayingCard,
        QWidget#queueArea,
        QWidget#devCard,
        QWidget#versionCard,
        QWidget#techCard,
        QWidget#licenseCard {{
            background-color: {t.card};
            border: 1px solid {t.border};
            border-radius: 22px;
        }}

        QListWidget {{
            background-color: rgba(255, 255, 255, 8);
            border: 1px solid {t.border};
            border-radius: 16px;
            color: {t.text};
            outline: none;
            padding: 7px;
        }}

        QListWidget::item {{
            color: {t.text};
            padding: 9px 10px;
            margin: 3px;
            border-radius: 11px;
            background-color: rgba(255, 255, 255, 5);
        }}

        QListWidget::item:hover {{
            background-color: rgba(255, 255, 255, 18);
            border: 1px solid {t.border};
        }}

        QListWidget::item:selected {{
            background-color: {t.accent};
            color: {t.button_text};
        }}

        QLineEdit {{
            background-color: rgba(255, 255, 255, 10);
            border: 1px solid {t.border};
            border-radius: 14px;
            color: {t.text};
            padding: 8px 12px;
            selection-background-color: {t.accent};
            selection-color: {t.button_text};
        }}

        QLineEdit:focus {{
            border: 1px solid {t.accent};
            background-color: rgba(255, 255, 255, 16);
        }}

        QPushButton {{
            color: {t.text};
            background-color: rgba(255, 255, 255, 9);
            border: 1px solid {t.border};
            border-radius: 13px;
            padding: 7px 11px;
        }}

        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 18);
            border: 1px solid {t.accent};
        }}

        QPushButton#btnAddSong,
        QPushButton#btnSmartPlaylist,
        QPushButton#btnTheme,
        QPushButton#smartCreate {{
            background-color: {t.accent};
            color: {t.button_text};
            border: none;
            font-weight: 800;
        }}

        QPushButton#btnAddSong:hover,
        QPushButton#btnSmartPlaylist:hover,
        QPushButton#btnTheme:hover,
        QPushButton#smartCreate:hover {{
            background-color: {t.accent2};
        }}

        QPushButton#btnNavSwitch {{
            background-color: rgba(255, 255, 255, 9);
            border: 1px solid {t.border};
            border-radius: 14px;
        }}

        QPushButton#btnPlay {{
            background-color: {t.accent};
            color: {t.button_text};
            border: none;
            border-radius: 28px;
            font-size: 20px;
            font-weight: bold;
        }}

        QSlider::groove:horizontal {{
            height: 4px;
            background: rgba(255, 255, 255, 32);
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background: {t.text};
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}

        QSlider::sub-page:horizontal {{
            background: {t.accent};
            border-radius: 2px;
        }}

        QMenu#aiChatMenu,
        QMenu {{
            background-color: {t.surface};
            color: {t.text};
            border: 1px solid {t.border};
            border-radius: 12px;
            padding: 6px;
        }}

        QMenu::item {{
            padding: 8px 18px;
            border-radius: 8px;
        }}

        QMenu::item:selected {{
            background-color: {t.accent};
            color: {t.button_text};
        }}

        QStatusBar {{
            background-color: {t.bg};
            color: {t.muted};
            border-top: 1px solid {t.border};
        }}
        """

    def _apply_direct_widget_styles(self, window, t: AppTheme):
        # Beberapa tombol di player.py diberi style langsung oleh method lain,
        # jadi theme manager mengunci style penting ini secara eksplisit.
        if hasattr(window, "btnPlay"):
            window.btnPlay.setFixedSize(56, 56)

        if hasattr(window, "topNavBar"):
            window.topNavBar.setStyleSheet(f"""
                QFrame#topNavBar {{
                    background-color: rgba(8, 8, 14, 226);
                    border-bottom: 1px solid {t.border};
                }}
                QWidget#topBrand, QWidget#topNavButtons {{
                    background-color: transparent;
                }}
            """)


class ThemeCustomizationDialog(QDialog):
    theme_applied = pyqtSignal(str)

    def __init__(self, manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.parent_window = parent
        self.selected_key = manager.current_key

        self.setWindowTitle("Theme Customization")
        self.setMinimumSize(720, 520)
        self.setObjectName("themeCustomizationDialog")
        self._build_ui()
        self._apply_dialog_style()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("Theme Customization")
        title.setObjectName("themeTitle")
        subtitle = QLabel("Pilih tema visual SoundWave. Pilihan akan tersimpan otomatis.")
        subtitle.setObjectName("themeSubtitle")
        root.addWidget(title)
        root.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(12)
        root.addLayout(grid, 1)

        row = 0
        col = 0
        for key, theme in self.manager.THEMES.items():
            card = self._make_theme_card(theme)
            grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.btn_close = QPushButton("Close")
        self.btn_close.setObjectName("themeClose")
        self.btn_close.clicked.connect(self.accept)

        bottom.addWidget(self.btn_close)
        root.addLayout(bottom)

    def _make_theme_card(self, theme: AppTheme) -> QFrame:
        frame = QFrame()
        frame.setObjectName("themeCard")
        frame.setCursor(Qt.PointingHandCursor)
        frame.setMinimumHeight(118)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        top = QHBoxLayout()
        name = QLabel(theme.name)
        name.setObjectName("themeCardName")
        badge = QLabel("Selected" if theme.key == self.manager.current_key else "Preview")
        badge.setObjectName("themeBadge")
        top.addWidget(name)
        top.addStretch(1)
        top.addWidget(badge)

        desc = QLabel(theme.description)
        desc.setObjectName("themeCardDesc")

        swatches = QHBoxLayout()
        for color in (theme.bg, theme.surface, theme.accent, theme.accent2):
            swatch = QLabel()
            swatch.setFixedSize(32, 20)
            swatch.setStyleSheet(f"background:{color}; border-radius:7px; border:1px solid rgba(255,255,255,45);")
            swatches.addWidget(swatch)
        swatches.addStretch(1)

        btn = QPushButton("Apply Theme")
        btn.setObjectName("applyThemeButton")
        btn.clicked.connect(lambda checked=False, k=theme.key: self._apply_theme(k))

        layout.addLayout(top)
        layout.addWidget(desc)
        layout.addLayout(swatches)
        layout.addWidget(btn)

        frame.setStyleSheet(f"""
            QFrame#themeCard {{
                background-color: {theme.card};
                border: 1px solid {theme.border};
                border-radius: 18px;
            }}
            QLabel#themeCardName {{
                color: {theme.text};
                font-size: 16px;
                font-weight: 900;
            }}
            QLabel#themeCardDesc {{
                color: {theme.muted};
                font-size: 12px;
            }}
            QLabel#themeBadge {{
                color: {theme.button_text};
                background-color: {theme.accent};
                border-radius: 9px;
                padding: 4px 8px;
                font-size: 10px;
                font-weight: 800;
            }}
            QPushButton#applyThemeButton {{
                background-color: {theme.accent};
                color: {theme.button_text};
                border: none;
                border-radius: 12px;
                padding: 8px 10px;
                font-weight: 800;
            }}
            QPushButton#applyThemeButton:hover {{
                background-color: {theme.accent2};
            }}
        """)
        return frame

    def _apply_theme(self, key: str):
        self.selected_key = key
        if self.parent_window is not None:
            self.manager.apply_to(self.parent_window, key)
        self.theme_applied.emit(key)
        self._refresh_cards()

    def _refresh_cards(self):
        # Rebuild dialog agar badge Selected ikut berubah.
        old = self.layout()
        while old.count():
            item = old.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._build_ui()

    def _apply_dialog_style(self):
        t = self.manager.get_theme()
        self.setStyleSheet(f"""
            QDialog#themeCustomizationDialog {{
                background-color: {t.bg};
            }}
            QLabel#themeTitle {{
                color: {t.text};
                font-size: 24px;
                font-weight: 900;
                font-family: "Segoe UI";
            }}
            QLabel#themeSubtitle {{
                color: {t.muted};
                font-size: 12px;
                font-family: "Segoe UI";
            }}
            QPushButton#themeClose {{
                min-width: 120px;
                min-height: 38px;
                background-color: rgba(255, 255, 255, 10);
                color: {t.text};
                border: 1px solid {t.border};
                border-radius: 14px;
                font-weight: 800;
            }}
            QPushButton#themeClose:hover {{
                background-color: rgba(255, 255, 255, 18);
                border: 1px solid {t.accent};
            }}
        """)
