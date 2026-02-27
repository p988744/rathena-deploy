"""Dashboard screen - server status overview."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, DataTable, Label, Rule

from ro_admin.config import Config, rate_display, RATE_VARS


class StatusIndicator(Static):
    """Green/red status dot with label."""

    def __init__(self, label: str, online: bool = False, **kw):
        super().__init__(**kw)
        self.label_text = label
        self.is_online = online

    def render(self) -> str:
        dot = "[green]●[/]" if self.is_online else "[red]●[/]"
        return f"{dot} {self.label_text}"

    def set_online(self, online: bool) -> None:
        self.is_online = online
        self.refresh()


class RateDisplay(Static):
    """Display a rate variable with multiplier."""

    def __init__(self, label: str, value: str = "0", **kw):
        super().__init__(**kw)
        self.label_text = label
        self.rate_value = value

    def render(self) -> str:
        return f"  {self.label_text:<16} {rate_display(self.rate_value):>6}"

    def set_value(self, value: str) -> None:
        self.rate_value = value
        self.refresh()


class DashboardScreen(Screen):
    BINDINGS = [
        ("s", "push_screen('settings')", "Settings"),
        ("a", "push_screen('accounts')", "Accounts"),
        ("o", "push_screen('server_ops')", "Operations"),
        ("l", "push_screen('logs')", "Logs"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="dashboard"):
            yield Label("[bold]Server Status[/]", id="status-title")
            with Vertical(id="status-box"):
                yield StatusIndicator("rathena", id="st-rathena")
                yield StatusIndicator("database", id="st-db")
            yield Rule()
            yield Label("[bold]Rates[/]", id="rates-title")
            with Vertical(id="rates-box"):
                yield RateDisplay("Base EXP", id="rate-base")
                yield RateDisplay("Job EXP", id="rate-job")
                yield RateDisplay("Drop", id="rate-drop")
                yield RateDisplay("Card Drop", id="rate-card")
            yield Rule()
            yield Label("[bold]Online Players[/]", id="players-title")
            yield DataTable(id="players-table")
            yield Rule()
            yield Label("", id="server-info")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#players-table", DataTable)
        table.add_columns("Name", "BaseLv", "JobLv")
        self.refresh_data()

    def refresh_data(self) -> None:
        self.run_worker(self._load_data(), exclusive=True)

    async def _load_data(self) -> None:
        app = self.app
        cfg = app.config

        # Update rates
        self.query_one("#rate-base", RateDisplay).set_value(cfg.get("BASE_EXP_RATE"))
        self.query_one("#rate-job", RateDisplay).set_value(cfg.get("JOB_EXP_RATE"))
        self.query_one("#rate-drop", RateDisplay).set_value(cfg.get("DROP_RATE"))
        self.query_one("#rate-card", RateDisplay).set_value(cfg.get("CARD_DROP_RATE"))

        # Server info
        name = cfg.get("SERVER_NAME", "Unknown")
        ip = cfg.get("SERVER_IP", "Unknown")
        mode = cfg.get("BUILD_MODE", "re").upper()
        pv = cfg.get("PACKETVER", "?")
        self.query_one("#server-info", Label).update(
            f"  {name}  |  {ip}  |  {mode}  |  PACKETVER {pv}"
        )

        # Server status (in thread to avoid blocking)
        ssh = app.ssh
        if ssh:
            status = await asyncio.to_thread(ssh.server_status)
            services = status.get("services", {})
            self.query_one("#st-rathena", StatusIndicator).set_online(
                services.get("rathena") == "running"
            )
            self.query_one("#st-db", StatusIndicator).set_online(
                services.get("db") == "running"
            )

            # Online players
            players = await asyncio.to_thread(ssh.online_players)
            table = self.query_one("#players-table", DataTable)
            table.clear()
            if players:
                for p in players:
                    table.add_row(p["name"], p["base_level"], p["job_level"])
            else:
                table.add_row("(no players online)", "-", "-")
