"""Server operations screen - restart, rebuild, logs."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Button, Label, Log, Rule


class ServerOpsScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="server-ops"):
            yield Label("[bold]Server Operations[/]")
            yield Button("Restart Server", variant="primary", id="btn-restart")
            yield Button("Stop Server", variant="error", id="btn-stop")
            yield Button("Start Server", variant="success", id="btn-start")
            yield Rule()
            yield Button("View Recent Logs", variant="default", id="btn-logs")
            yield Button("Server Status", variant="default", id="btn-status")
            yield Rule()
            yield Label("[bold]Output[/]")
            yield Log(id="op-log", auto_scroll=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        actions = {
            "btn-restart": ("Restarting...", "restart rathena", 60),
            "btn-stop": ("Stopping...", "down", 30),
            "btn-start": ("Starting...", "up -d", 30),
            "btn-logs": ("Fetching logs...", "logs --tail=50 rathena", 15),
            "btn-status": ("Checking status...", "ps", 10),
        }
        bid = event.button.id
        if bid in actions:
            msg, cmd, timeout = actions[bid]
            self.run_worker(self._run_op(msg, cmd, timeout))

    async def _run_op(self, msg: str, cmd: str, timeout: int) -> None:
        log = self.query_one("#op-log", Log)
        log.write_line(f">>> {msg}")

        ssh = self.app.ssh
        if not ssh:
            log.write_line("[ERROR] SSH not configured")
            return

        rc, out, err = await asyncio.to_thread(
            ssh.docker_compose, cmd, timeout
        )

        if out:
            for line in out.splitlines():
                log.write_line(line)
        if err:
            for line in err.splitlines():
                log.write_line(line)

        if rc == 0:
            log.write_line(">>> Done")
        else:
            log.write_line(f">>> Failed (exit code {rc})")
        log.write_line("")
