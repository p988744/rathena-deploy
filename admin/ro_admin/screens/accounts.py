"""Accounts screen - manage player accounts."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, DataTable, Label, Button, Input, Static, Rule


GM_LEVELS = {
    "0": "Player",
    "1": "Junior GM",
    "10": "GM",
    "99": "Admin",
}


class AccountsScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="accounts"):
            yield Label("[bold]Accounts[/]")
            yield DataTable(id="account-table")

            yield Rule()
            yield Label("[bold]Create Account[/]")
            with Horizontal(classes="field"):
                yield Label("Username ", classes="field-label")
                yield Input(id="inp-new-user", placeholder="6+ characters")
            with Horizontal(classes="field"):
                yield Label("Password ", classes="field-label")
                yield Input(id="inp-new-pass", placeholder="6+ characters", password=True)
            with Horizontal(classes="field"):
                yield Label("Sex      ", classes="field-label")
                yield Input(id="inp-new-sex", placeholder="M or F", max_length=1)
            with Horizontal(classes="field"):
                yield Label("GM Level ", classes="field-label")
                yield Input(id="inp-new-gm", placeholder="0=Player, 99=Admin", value="0", type="integer")
            yield Button("Create Account", variant="primary", id="btn-create")

            yield Rule()
            yield Label("[bold]Modify Account[/] (enter account ID)")
            with Horizontal(classes="field"):
                yield Label("Account ID", classes="field-label")
                yield Input(id="inp-mod-id", type="integer")
            with Horizontal(id="mod-buttons"):
                yield Button("Set GM 99", variant="warning", id="btn-gm99")
                yield Button("Set GM 0", variant="default", id="btn-gm0")
                yield Button("Ban", variant="error", id="btn-ban")
                yield Button("Unban", variant="success", id="btn-unban")
            yield Static("", id="mod-result")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#account-table", DataTable)
        table.add_columns("ID", "Username", "Sex", "GM", "Status", "Logins", "Last Login")
        self.action_refresh()

    def action_refresh(self) -> None:
        self.run_worker(self._load_accounts(), exclusive=True)

    async def _load_accounts(self) -> None:
        ssh = self.app.ssh
        if not ssh:
            return
        accounts = await asyncio.to_thread(ssh.account_list)
        table = self.query_one("#account-table", DataTable)
        table.clear()
        for a in accounts:
            gm = GM_LEVELS.get(a["group_id"], f"Lv{a['group_id']}")
            status = "Banned" if a["state"] != "0" else "Active"
            table.add_row(
                a["id"], a["userid"], a["sex"], gm, status,
                a["logincount"], a["lastlogin"],
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-create":
            self.run_worker(self._create_account())
        elif bid in ("btn-gm99", "btn-gm0", "btn-ban", "btn-unban"):
            self.run_worker(self._modify_account(bid))

    async def _create_account(self) -> None:
        user = self.query_one("#inp-new-user", Input).value.strip()
        passwd = self.query_one("#inp-new-pass", Input).value.strip()
        sex = self.query_one("#inp-new-sex", Input).value.strip().upper()
        gm = self.query_one("#inp-new-gm", Input).value.strip()

        if len(user) < 6 or len(passwd) < 6:
            self.notify("Username and password must be 6+ characters", severity="error")
            return
        if sex not in ("M", "F"):
            self.notify("Sex must be M or F", severity="error")
            return

        ssh = self.app.ssh
        rc, out, err = await asyncio.to_thread(
            ssh.docker_exec_db,
            f"INSERT INTO login (userid, user_pass, sex, group_id) "
            f"VALUES ('{user}', '{passwd}', '{sex}', {gm});"
        )
        if rc == 0:
            self.notify(f"Account '{user}' created!")
            self.action_refresh()
        else:
            self.notify(f"Failed: {err}", severity="error")

    async def _modify_account(self, action: str) -> None:
        acc_id = self.query_one("#inp-mod-id", Input).value.strip()
        if not acc_id:
            self.notify("Enter an account ID", severity="error")
            return

        sql_map = {
            "btn-gm99": f"UPDATE login SET group_id=99 WHERE account_id={acc_id};",
            "btn-gm0": f"UPDATE login SET group_id=0 WHERE account_id={acc_id};",
            "btn-ban": f"UPDATE login SET state=5 WHERE account_id={acc_id};",
            "btn-unban": f"UPDATE login SET state=0 WHERE account_id={acc_id};",
        }
        label_map = {
            "btn-gm99": "Set to Admin (GM 99)",
            "btn-gm0": "Set to Player (GM 0)",
            "btn-ban": "Banned",
            "btn-unban": "Unbanned",
        }

        ssh = self.app.ssh
        rc, out, err = await asyncio.to_thread(
            ssh.docker_exec_db, sql_map[action]
        )
        result = self.query_one("#mod-result", Static)
        if rc == 0:
            result.update(f"[green]Account {acc_id}: {label_map[action]}[/]")
            self.action_refresh()
        else:
            result.update(f"[red]Failed: {err}[/]")

