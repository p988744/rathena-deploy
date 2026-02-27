"""RO Admin - rAthena private server management TUI."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from ro_admin.config import Config
from ro_admin.ssh import SSH, SSHConfig
from ro_admin.screens.dashboard import DashboardScreen
from ro_admin.screens.settings import SettingsScreen
from ro_admin.screens.accounts import AccountsScreen
from ro_admin.screens.server_ops import ServerOpsScreen
from ro_admin.screens.send_items import SendItemsScreen
from ro_admin.screens.char_edit import CharEditScreen

# Default .env path relative to this tool
DEFAULT_ENV = Path(__file__).parent.parent.parent / "server" / ".env"
DEFAULT_SSH_KEY = Path.home() / ".ssh" / "aws" / "aws.pem"

CSS = """
Screen {
    background: $surface;
}

#dashboard, #settings, #accounts, #server-ops, #char-edit {
    padding: 1 2;
}

.field {
    height: 3;
    margin-bottom: 0;
}

.field-label {
    width: 18;
    padding-top: 1;
}

.field Input {
    width: 40;
}

#buttons, #mod-buttons {
    height: 3;
    margin-top: 1;
}

#buttons Button, #mod-buttons Button, #send-buttons Button, #edit-buttons Button {
    margin-right: 1;
}

#send-buttons, #edit-buttons {
    height: 3;
    margin-top: 1;
}

#send-result, #edit-result {
    margin-top: 1;
}

#item-search-table {
    height: 10;
}

#changes-preview {
    margin: 1 0;
    padding: 1;
    background: $panel;
}

#account-table, #ce-account-table, #send-account-table {
    height: 12;
}

#players-table {
    height: 8;
}

#op-log {
    height: 1fr;
    min-height: 10;
    border: solid $primary;
}

#status-box, #rates-box {
    padding-left: 2;
    height: auto;
}

#server-info {
    margin-top: 1;
    color: $text-muted;
}

StatusIndicator {
    height: 1;
}

RateDisplay {
    height: 1;
}

#server-ops Button {
    margin-bottom: 1;
    width: 30;
}
"""


class ROAdmin(App):
    TITLE = "RO Admin"
    SUB_TITLE = "rAthena Server Manager"
    CSS = CSS

    SCREENS = {
        "dashboard": DashboardScreen,
        "settings": SettingsScreen,
        "accounts": AccountsScreen,
        "server_ops": ServerOpsScreen,
        "send_items": SendItemsScreen,
        "char_edit": CharEditScreen,
    }

    BINDINGS = [
        Binding("d", "push_screen('dashboard')", "Dashboard"),
        Binding("s", "push_screen('settings')", "Settings"),
        Binding("a", "push_screen('accounts')", "Accounts"),
        Binding("i", "push_screen('send_items')", "Items"),
        Binding("c", "push_screen('char_edit')", "Characters"),
        Binding("o", "push_screen('server_ops')", "Operations"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self, env_path: str | Path | None = None):
        super().__init__()
        self._env_path = Path(env_path) if env_path else DEFAULT_ENV
        self.config: Config = Config.load(self._env_path)
        self.ssh: SSH | None = None

    def on_mount(self) -> None:
        # Setup SSH from config
        host = self.config.get("SERVER_IP")
        user = self.config.get("SERVER_USER", "ubuntu")
        port = int(self.config.get("SERVER_SSH_PORT", "22"))
        remote_dir = self.config.get("REMOTE_DIR", "/opt/rathena")

        key_path = str(DEFAULT_SSH_KEY) if DEFAULT_SSH_KEY.exists() else ""

        if host:
            self.ssh = SSH(SSHConfig(
                host=host,
                user=user,
                port=port,
                key_path=key_path,
                remote_dir=remote_dir,
            ))

        name = self.config.get("SERVER_NAME", "RO Server")
        self.sub_title = name
        self.push_screen("dashboard")


def main():
    import sys
    env_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = ROAdmin(env_path=env_path)
    app.run()


if __name__ == "__main__":
    main()
