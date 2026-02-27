"""Send Items / Zeny screen."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, DataTable, Label, Button, Input, Static, Rule


STARTER_PACK = [
    {"item_id": 601, "amount": 1, "name": "Fly Wing"},
    {"item_id": 602, "amount": 1, "name": "Butterfly Wing"},
    {"item_id": 14533, "amount": 100, "name": "Super Boost (Field Manual 100%)"},
    {"item_id": 12411, "amount": 1, "name": "Instant Level (HE Battle Manual)"},
    {"item_id": 22996, "amount": 1, "name": "Stat Reset (Neuralizer)"},
    {"item_id": 25464, "amount": 20, "name": "World Map (Tour Ticket)"},
    {"item_id": 17315, "amount": 1, "name": "Silvervine Fruit Box"},
]
STARTER_ZENY = 100_000_000


class SendItemsScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
        ("p", "starter_pack", "Starter Pack (All)"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="send-items"):
            yield Label("[bold]Send Items / Zeny[/]")

            yield Rule()
            yield Label("[bold]Accounts[/]")
            yield DataTable(id="send-account-table")

            yield Rule()
            yield Label("[bold]Item Search[/]  [dim](search rAthena item_db)[/]")
            with Horizontal(classes="field"):
                yield Label("Keyword   ", classes="field-label")
                yield Input(id="inp-search-kw", placeholder="e.g. potion, sword, card...")
            yield Button("Search", variant="primary", id="btn-search")
            yield DataTable(id="item-search-table")

            yield Rule()
            yield Label("[bold]Target[/]")
            with Horizontal(classes="field"):
                yield Label("Account ID", classes="field-label")
                yield Input(id="inp-target-id", type="integer", placeholder="Leave empty for all accounts")

            yield Rule()
            yield Label("[bold]Item[/]")
            with Horizontal(classes="field"):
                yield Label("Item ID   ", classes="field-label")
                yield Input(id="inp-item-id", type="integer", placeholder="e.g. 40001")
            with Horizontal(classes="field"):
                yield Label("Amount    ", classes="field-label")
                yield Input(id="inp-item-amt", type="integer", value="1")

            yield Rule()
            yield Label("[bold]Zeny[/]")
            with Horizontal(classes="field"):
                yield Label("Zeny      ", classes="field-label")
                yield Input(id="inp-zeny", type="integer", value="0", placeholder="e.g. 1000000")

            yield Rule()
            with Horizontal(id="send-buttons"):
                yield Button("Send to Account", variant="primary", id="btn-send-one")
                yield Button("Send to All", variant="warning", id="btn-send-all")
                yield Button("Starter Pack → All", variant="success", id="btn-starter-all")
                yield Button("Starter Pack → Account", id="btn-starter-one")
            yield Static("", id="send-result")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#send-account-table", DataTable)
        table.add_columns("ID", "Username", "Sex", "GM", "Logins")

        search_table = self.query_one("#item-search-table", DataTable)
        search_table.cursor_type = "row"
        search_table.add_columns("ID", "Name", "AegisName")

        self.action_refresh()

    def action_refresh(self) -> None:
        self.run_worker(self._load_accounts(), exclusive=True)

    async def _load_accounts(self) -> None:
        ssh = self.app.ssh
        if not ssh:
            return
        accounts = await asyncio.to_thread(ssh.account_list)
        table = self.query_one("#send-account-table", DataTable)
        table.clear()
        for a in accounts:
            gm_map = {"0": "Player", "1": "Jr GM", "10": "GM", "99": "Admin"}
            gm = gm_map.get(a["group_id"], f"Lv{a['group_id']}")
            table.add_row(a["id"], a["userid"], a["sex"], gm, a["logincount"])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "item-search-table":
            # Click search result → fill item ID
            table = self.query_one("#item-search-table", DataTable)
            row = table.get_row(event.row_key)
            if row:
                self.query_one("#inp-item-id", Input).value = str(row[0])
                self.notify(f"Selected: {row[1]} (ID: {row[0]})")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-search":
            self.run_worker(self._search_items())
        elif event.button.id == "btn-send-one":
            self.run_worker(self._send(all_accounts=False))
        elif event.button.id == "btn-send-all":
            self.run_worker(self._send(all_accounts=True))
        elif event.button.id == "btn-starter-all":
            self.run_worker(self._send_starter_pack(all_accounts=True))
        elif event.button.id == "btn-starter-one":
            self.run_worker(self._send_starter_pack(all_accounts=False))

    def action_starter_pack(self) -> None:
        self.run_worker(self._send_starter_pack(all_accounts=True))

    async def _search_items(self) -> None:
        keyword = self.query_one("#inp-search-kw", Input).value.strip()
        if not keyword:
            self.notify("Enter a search keyword", severity="error")
            return

        ssh = self.app.ssh
        if not ssh:
            return

        self.notify(f"Searching '{keyword}'...")
        items = await asyncio.to_thread(ssh.item_search, keyword)

        table = self.query_one("#item-search-table", DataTable)
        table.clear()

        if not items:
            self.notify("No items found", severity="warning")
            return

        for item in items:
            table.add_row(item["id"], item["name"], item.get("aegis", ""))

        self.notify(f"Found {len(items)} item(s)")

    async def _send(self, all_accounts: bool) -> None:
        item_id = self.query_one("#inp-item-id", Input).value.strip()
        item_amt = self.query_one("#inp-item-amt", Input).value.strip() or "0"
        zeny = self.query_one("#inp-zeny", Input).value.strip() or "0"
        result = self.query_one("#send-result", Static)

        has_item = item_id != "" and int(item_amt) > 0
        has_zeny = int(zeny) > 0

        if not has_item and not has_zeny:
            self.notify("Enter an Item ID or Zeny amount", severity="error")
            return

        ssh = self.app.ssh
        if not ssh:
            return

        # Get target characters
        if all_accounts:
            where = "c.account_id >= 2000000"
            target_label = "all characters"
        else:
            acc_id = self.query_one("#inp-target-id", Input).value.strip()
            if not acc_id:
                self.notify("Enter an Account ID", severity="error")
                return
            where = f"c.account_id = {acc_id}"
            target_label = f"account {acc_id}"

        # Query characters
        rc, out, err = await asyncio.to_thread(
            ssh.docker_exec_db,
            f"SELECT c.char_id, c.name FROM `char` c WHERE {where};"
        )
        if rc != 0:
            result.update(f"[red]Failed to query characters: {err}[/]")
            return

        chars = []
        for line in out.strip().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2:
                chars.append({"id": parts[0], "name": parts[1]})

        if not chars:
            result.update("[red]No characters found[/]")
            return

        # mail type: 0=text, 1=zeny, 2=item, 3=zeny+item
        mail_type = 0
        if has_item and has_zeny:
            mail_type = 3
        elif has_item:
            mail_type = 2
        elif has_zeny:
            mail_type = 1

        # Send mail to each character
        sent = 0
        for ch in chars:
            cid = ch["id"]
            cname = ch["name"]

            # Insert mail
            sql = (
                "INSERT INTO mail (send_name, send_id, dest_name, dest_id, "
                f"title, message, time, status, zeny, type) VALUES ("
                f"'GM', 0, '{cname}', {cid}, "
                f"'GM Gift', 'From server admin', UNIX_TIMESTAMP(), 0, "
                f"{zeny if has_zeny else 0}, {mail_type});"
            )
            rc, out, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
            if rc != 0:
                result.update(f"[red]Mail failed for {cname}: {err}[/]")
                return

            # Attach item if needed
            if has_item:
                sql = (
                    "INSERT INTO mail_attachments (id, `index`, nameid, amount, identify) "
                    f"VALUES (LAST_INSERT_ID(), 0, {item_id}, {item_amt}, 1);"
                )
                rc, out, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
                if rc != 0:
                    result.update(f"[red]Item attach failed for {cname}: {err}[/]")
                    return

            sent += 1

        desc = []
        if has_item:
            desc.append(f"Item {item_id} x{item_amt}")
        if has_zeny:
            desc.append(f"{int(zeny):,} Zeny")
        summary = " + ".join(desc)
        result.update(f"[green]Mailed {summary} to {sent} character(s) ({target_label})[/]")

    async def _send_starter_pack(self, all_accounts: bool) -> None:
        ssh = self.app.ssh
        if not ssh:
            return

        result = self.query_one("#send-result", Static)

        if all_accounts:
            where = "c.account_id >= 2000000"
            target_label = "all characters"
        else:
            acc_id = self.query_one("#inp-target-id", Input).value.strip()
            if not acc_id:
                self.notify("Enter an Account ID", severity="error")
                return
            where = f"c.account_id = {acc_id}"
            target_label = f"account {acc_id}"

        rc, out, err = await asyncio.to_thread(
            ssh.docker_exec_db,
            f"SELECT c.char_id, c.name FROM `char` c WHERE {where};"
        )
        if rc != 0:
            result.update(f"[red]Failed to query characters: {err}[/]")
            return

        chars = []
        for line in out.strip().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2:
                chars.append({"id": parts[0], "name": parts[1]})

        if not chars:
            result.update("[red]No characters found[/]")
            return

        result.update(f"[yellow]Sending starter pack to {len(chars)} character(s)...[/]")

        sent = 0
        for ch in chars:
            cid = ch["id"]
            cname = ch["name"]

            # Send each item as a separate mail
            for item in STARTER_PACK:
                sql = (
                    "INSERT INTO mail (send_name, send_id, dest_name, dest_id, "
                    f"title, message, time, status, zeny, type) VALUES ("
                    f"'GM', 0, '{cname}', {cid}, "
                    f"'Starter Pack', '{item[\"name\"]}', UNIX_TIMESTAMP(), 0, 0, 2);"
                )
                rc, _, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
                if rc != 0:
                    result.update(f"[red]Mail failed for {cname}: {err}[/]")
                    return
                sql = (
                    "INSERT INTO mail_attachments (id, `index`, nameid, amount, identify) "
                    f"VALUES (LAST_INSERT_ID(), 0, {item['item_id']}, {item['amount']}, 1);"
                )
                rc, _, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
                if rc != 0:
                    result.update(f"[red]Item attach failed for {cname}: {err}[/]")
                    return

            # Send zeny mail
            sql = (
                "INSERT INTO mail (send_name, send_id, dest_name, dest_id, "
                f"title, message, time, status, zeny, type) VALUES ("
                f"'GM', 0, '{cname}', {cid}, "
                f"'Starter Pack', '100M Zeny', UNIX_TIMESTAMP(), 0, {STARTER_ZENY}, 1);"
            )
            rc, _, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
            if rc != 0:
                result.update(f"[red]Zeny mail failed for {cname}: {err}[/]")
                return

            sent += 1

        items_desc = ", ".join(f"{i['name']} x{i['amount']}" for i in STARTER_PACK)
        result.update(
            f"[green]Starter Pack sent to {sent} character(s) ({target_label}): "
            f"{items_desc} + {STARTER_ZENY:,} Zeny[/]"
        )
