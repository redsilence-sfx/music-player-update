"""
Installer patch sederhana untuk menambahkan Theme Customization ke SoundWave.
Jalankan dari root project:

    python scripts/install_theme_customization.py

Script ini akan:
1. Backup app/player.py dan features/__init__.py
2. Menambahkan import ThemeManager/ThemeCustomizationDialog
3. Menambahkan init ThemeManager
4. Menambahkan tombol Theme dan method handler
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PLAYER = ROOT / "app" / "player.py"
FEATURES_INIT = ROOT / "features" / "__init__.py"


def backup(path: Path):
    target = path.with_suffix(path.suffix + ".bak_theme")
    if not target.exists():
        shutil.copy2(path, target)
    return target


def patch_features_init():
    text = FEATURES_INIT.read_text(encoding="utf-8")
    backup(FEATURES_INIT)

    if "from .theme_customizer import ThemeManager, ThemeCustomizationDialog" not in text:
        text += "\nfrom .theme_customizer import ThemeManager, ThemeCustomizationDialog\n"

    if "ThemeManager" not in text.split("__all__", 1)[-1] if "__all__" in text else True:
        if "__all__" in text and "]" in text:
            text = text.replace(
                "]",
                '    "ThemeManager", "ThemeCustomizationDialog",\n]',
                1,
            )
        else:
            text += '\n__all__ = ["ThemeManager", "ThemeCustomizationDialog"]\n'

    FEATURES_INIT.write_text(text, encoding="utf-8")


def patch_player():
    text = PLAYER.read_text(encoding="utf-8")
    backup(PLAYER)

    # Import patch: tambah ke salah satu import from features import (...) yang tersedia.
    if "ThemeManager" not in text:
        if "StatsManager, StatsWidget," in text:
            text = text.replace(
                "StatsManager, StatsWidget,",
                "StatsManager, StatsWidget, ThemeManager, ThemeCustomizationDialog,",
                1,
            )
        elif "SmartPlaylistGenerator, SmartPlaylistDialog" in text:
            text = text.replace(
                "SmartPlaylistGenerator, SmartPlaylistDialog",
                "SmartPlaylistGenerator, SmartPlaylistDialog, ThemeManager, ThemeCustomizationDialog",
                1,
            )
        else:
            text = text.replace(
                "import constants as C",
                "from features import ThemeManager, ThemeCustomizationDialog\nimport constants as C",
                1,
            )

    # Init patch: setelah UIEnhancer install.
    if "self.theme_manager = ThemeManager()" not in text:
        text = text.replace(
            "self.ui_enhancer.install()",
            "self.ui_enhancer.install()\n        self.theme_manager = ThemeManager()\n        self.theme_manager.apply_to(self)",
            1,
        )

    # Setup button call.
    if "self._setup_theme_button()" not in text:
        text = text.replace(
            "self._setup_smart_playlist_button()",
            "self._setup_theme_button()\n        self._setup_smart_playlist_button()",
            1,
        )

    # Add methods before _setup_smart_playlist_button when possible.
    methods = r'''
    def _setup_theme_button(self):
        """Tambahkan tombol Theme ke top navigation."""
        if not hasattr(self, "topNavBar"):
            return

        self.btnTheme = QPushButton("Theme", self.topNavBar)
        self.btnTheme.setObjectName("btnTheme")
        self.btnTheme.setCursor(Qt.PointingHandCursor)
        self.btnTheme.setMinimumHeight(38)
        self.btnTheme.setMinimumWidth(86)
        self.btnTheme.setMaximumWidth(96)
        self.btnTheme.clicked.connect(self._open_theme_dialog)

        top_layout = self.topNavBar.layout()
        if top_layout:
            insert_index = max(0, top_layout.count() - 1)
            top_layout.insertWidget(insert_index, self.btnTheme)

    def _open_theme_dialog(self):
        """Buka dialog Theme Customization."""
        if not hasattr(self, "theme_manager"):
            self.theme_manager = ThemeManager()

        dialog = ThemeCustomizationDialog(self.theme_manager, self)
        dialog.theme_applied.connect(self._on_theme_applied)
        dialog.exec_()

    def _on_theme_applied(self, theme_key: str):
        """Callback setelah user memilih theme."""
        theme_name = self.theme_manager.get_theme(theme_key).name

        # Refresh active nav style agar page aktif tetap konsisten.
        try:
            self._go_page(self.stackedPages.currentIndex())
        except Exception:
            pass

        if hasattr(self, "ui_enhancer"):
            self.ui_enhancer.apply_album_gradient()

        if hasattr(self, "toast"):
            self.toast.show("Theme updated", f"{theme_name} applied.", "success")

        self.statusBar.showMessage(f"Theme updated: {theme_name}")
'''

    if "def _setup_theme_button(self):" not in text:
        marker = "    def _setup_smart_playlist_button(self):"
        if marker in text:
            text = text.replace(marker, methods + "\n" + marker, 1)
        else:
            raise RuntimeError("Tidak menemukan marker _setup_smart_playlist_button. Tambahkan method manual.")

    PLAYER.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    if not PLAYER.exists() or not FEATURES_INIT.exists():
        print("Jalankan script ini dari root project SoundWave.", file=sys.stderr)
        sys.exit(1)

    patch_features_init()
    patch_player()
    print("Theme Customization patch selesai. Backup dibuat dengan suffix .bak_theme")
