"""Settings screen - edit .env configuration."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Button, Static, Rule

from ro_admin.config import Config, rate_display, REBUILD_REQUIRED


class SettingsScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="settings"):
            yield Label("[bold]Game Rates[/]")
            yield Label("  (100 = 1x, 1000 = 10x, 5000 = 50x)")
            with Horizontal(classes="field"):
                yield Label("Base EXP Rate ", classes="field-label")
                yield Input(id="inp-base-exp", type="integer")
            with Horizontal(classes="field"):
                yield Label("Job EXP Rate  ", classes="field-label")
                yield Input(id="inp-job-exp", type="integer")
            with Horizontal(classes="field"):
                yield Label("Drop Rate     ", classes="field-label")
                yield Input(id="inp-drop", type="integer")
            with Horizontal(classes="field"):
                yield Label("Card Drop Rate", classes="field-label")
                yield Input(id="inp-card-drop", type="integer")

            yield Rule()
            yield Label("[bold]Server Info[/]")
            with Horizontal(classes="field"):
                yield Label("Server Name   ", classes="field-label")
                yield Input(id="inp-name")
            with Horizontal(classes="field"):
                yield Label("Server IP     ", classes="field-label")
                yield Input(id="inp-ip")

            yield Rule()
            yield Label("[bold]Build Config[/] [dim](requires rebuild)[/]")
            with Horizontal(classes="field"):
                yield Label("PACKETVER     ", classes="field-label")
                yield Input(id="inp-packetver", type="integer")
            with Horizontal(classes="field"):
                yield Label("Build Mode    ", classes="field-label")
                yield Input(id="inp-build-mode", placeholder="re or pre-re")

            yield Rule()
            yield Static("", id="changes-preview")
            with Horizontal(id="buttons"):
                yield Button("Save & Apply", variant="primary", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")
        yield Footer()

    def on_mount(self) -> None:
        cfg = self.app.config
        self.query_one("#inp-base-exp", Input).value = cfg.get("BASE_EXP_RATE")
        self.query_one("#inp-job-exp", Input).value = cfg.get("JOB_EXP_RATE")
        self.query_one("#inp-drop", Input).value = cfg.get("DROP_RATE")
        self.query_one("#inp-card-drop", Input).value = cfg.get("CARD_DROP_RATE")
        self.query_one("#inp-name", Input).value = cfg.get("SERVER_NAME")
        self.query_one("#inp-ip", Input).value = cfg.get("SERVER_IP")
        self.query_one("#inp-packetver", Input).value = cfg.get("PACKETVER")
        self.query_one("#inp-build-mode", Input).value = cfg.get("BUILD_MODE")

    def on_input_changed(self, event: Input.Changed) -> None:
        self._update_preview()

    def _update_preview(self) -> None:
        cfg = self.app.config
        mapping = {
            "BASE_EXP_RATE": "#inp-base-exp",
            "JOB_EXP_RATE": "#inp-job-exp",
            "DROP_RATE": "#inp-drop",
            "CARD_DROP_RATE": "#inp-card-drop",
            "SERVER_NAME": "#inp-name",
            "SERVER_IP": "#inp-ip",
            "PACKETVER": "#inp-packetver",
            "BUILD_MODE": "#inp-build-mode",
        }
        lines = []
        need_rebuild = False
        for var, selector in mapping.items():
            new_val = self.query_one(selector, Input).value
            old_val = cfg.get(var)
            if new_val != old_val:
                extra = ""
                if var in REBUILD_REQUIRED:
                    extra = " [red](rebuild needed)[/]"
                    need_rebuild = True
                lines.append(f"  {var}: {old_val} -> {new_val}{extra}")

        preview = self.query_one("#changes-preview", Static)
        if lines:
            header = "[bold yellow]Changes:[/]\n"
            if need_rebuild:
                header += "[red bold]Warning: rebuild required![/]\n"
            preview.update(header + "\n".join(lines))
        else:
            preview.update("[dim]No changes[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
            return

        if event.button.id == "btn-save":
            self._save_and_apply()

    def _save_and_apply(self) -> None:
        cfg = self.app.config
        mapping = {
            "BASE_EXP_RATE": "#inp-base-exp",
            "JOB_EXP_RATE": "#inp-job-exp",
            "DROP_RATE": "#inp-drop",
            "CARD_DROP_RATE": "#inp-card-drop",
            "SERVER_NAME": "#inp-name",
            "SERVER_IP": "#inp-ip",
            "PACKETVER": "#inp-packetver",
            "BUILD_MODE": "#inp-build-mode",
        }

        changes = []
        for var, selector in mapping.items():
            new_val = self.query_one(selector, Input).value
            old_val = cfg.get(var)
            if new_val != old_val:
                changes.append((var, old_val, new_val))
                cfg.set(var, new_val)

        if not changes:
            self.notify("No changes to save")
            return

        cfg.save()
        need_rebuild = any(k in REBUILD_REQUIRED for k, _, _ in changes)

        if need_rebuild:
            self.notify(
                "Config saved. Rebuild required — run build.sh + deploy.sh",
                severity="warning",
                timeout=5,
            )
        else:
            # Apply: upload .env and restart
            self.run_worker(self._apply_restart())

        self.app.pop_screen()

    async def _apply_restart(self) -> None:
        ssh = self.app.ssh
        if not ssh:
            self.notify("SSH not configured", severity="error")
            return

        self.notify("Uploading config...")
        rc, msg = await asyncio.to_thread(
            ssh.scp_upload,
            self.app.config.path,
            f"{ssh.cfg.remote_dir}/.env",
        )
        if rc != 0:
            self.notify(f"Upload failed: {msg}", severity="error")
            return

        self.notify("Restarting server...")
        rc, out, err = await asyncio.to_thread(
            ssh.docker_compose, "restart rathena", 60
        )
        if rc == 0:
            self.notify("Server restarted!", severity="information")
        else:
            self.notify(f"Restart failed: {err}", severity="error")
