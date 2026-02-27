"""Character editor screen - modify character stats."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import VerticalScroll, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header, DataTable, Label, Button, Input, Static, Rule


GM_LEVELS = {
    "0": "Player",
    "1": "Jr GM",
    "10": "GM",
    "99": "Admin",
}


def stat_point_cost(val: int) -> int:
    """Cost to raise a stat by 1 at current value val (rAthena Renewal)."""
    if val < 100:
        return 2 + (val - 1) // 10
    else:
        return 16 + 4 * ((val - 100) // 5)


def total_stat_cost(target: int) -> int:
    """Total status points needed to raise a stat from 1 to target."""
    return sum(stat_point_cost(v) for v in range(1, target))


class CharEditScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._statpoint_table: dict[int, int] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="char-edit"):
            yield Label("[bold]Character Editor[/]")

            yield Rule()
            yield Label("[bold]1. Select Account[/]")
            yield DataTable(id="ce-account-table")

            yield Rule()
            yield Label("[bold]2. Characters[/]  [dim](click account above to load)[/]")
            yield DataTable(id="char-table")

            yield Rule()
            yield Label("[bold]3. Edit Character[/]  [dim](click character above to fill)[/]")
            with Horizontal(classes="field"):
                yield Label("Char ID   ", classes="field-label")
                yield Input(id="inp-char-id", type="integer", placeholder="Select from table above")

            yield Label("  [dim]── Level ──[/]")
            with Horizontal(classes="field"):
                yield Label("Base Level", classes="field-label")
                yield Input(id="inp-base-lv", type="integer", placeholder="1-275")
            with Horizontal(classes="field"):
                yield Label("Job Level ", classes="field-label")
                yield Input(id="inp-job-lv", type="integer", placeholder="1-70")
            with Horizontal(classes="field"):
                yield Label("Job Class ", classes="field-label")
                yield Input(id="inp-job", type="integer", placeholder="e.g. 4054=Rune Knight")

            yield Label("  [dim]── Stats ──[/]")
            with Horizontal(classes="field"):
                yield Label("STR       ", classes="field-label")
                yield Input(id="inp-str", type="integer")
            with Horizontal(classes="field"):
                yield Label("AGI       ", classes="field-label")
                yield Input(id="inp-agi", type="integer")
            with Horizontal(classes="field"):
                yield Label("VIT       ", classes="field-label")
                yield Input(id="inp-vit", type="integer")
            with Horizontal(classes="field"):
                yield Label("INT       ", classes="field-label")
                yield Input(id="inp-int", type="integer")
            with Horizontal(classes="field"):
                yield Label("DEX       ", classes="field-label")
                yield Input(id="inp-dex", type="integer")
            with Horizontal(classes="field"):
                yield Label("LUK       ", classes="field-label")
                yield Input(id="inp-luk", type="integer")

            yield Label("  [dim]── Resources (auto-calculated on save) ──[/]")
            with Horizontal(classes="field"):
                yield Label("Zeny      ", classes="field-label")
                yield Input(id="inp-zeny", type="integer")
            with Horizontal(classes="field"):
                yield Label("Status Pts", classes="field-label")
                yield Input(id="inp-status-pt", type="integer", placeholder="auto")
            with Horizontal(classes="field"):
                yield Label("Skill Pts ", classes="field-label")
                yield Input(id="inp-skill-pt", type="integer", placeholder="auto")

            yield Rule()
            with Horizontal(id="edit-buttons"):
                yield Button("Save Changes", variant="primary", id="btn-save")
                yield Button("Max Stats", variant="warning", id="btn-max")
                yield Button("Reset Stats", variant="error", id="btn-reset")
            yield Static("", id="edit-result")
        yield Footer()

    def on_mount(self) -> None:
        acc_table = self.query_one("#ce-account-table", DataTable)
        acc_table.cursor_type = "row"
        acc_table.add_columns("ID", "Username", "Sex", "GM", "Logins")

        char_table = self.query_one("#char-table", DataTable)
        char_table.cursor_type = "row"
        char_table.add_columns(
            "CharID", "Name", "BaseLv", "JobLv", "Class",
            "STR", "AGI", "VIT", "INT", "DEX", "LUK", "Zeny",
        )

        self.action_refresh()
        self.run_worker(self._load_statpoint_table())

    def action_refresh(self) -> None:
        self.run_worker(self._load_accounts(), exclusive=True)

    async def _load_statpoint_table(self) -> None:
        ssh = self.app.ssh
        if not ssh:
            return
        self._statpoint_table = await asyncio.to_thread(ssh.statpoint_table)

    async def _load_accounts(self) -> None:
        ssh = self.app.ssh
        if not ssh:
            return
        accounts = await asyncio.to_thread(ssh.account_list)
        table = self.query_one("#ce-account-table", DataTable)
        table.clear()
        for a in accounts:
            gm = GM_LEVELS.get(a["group_id"], f"Lv{a['group_id']}")
            table.add_row(a["id"], a["userid"], a["sex"], gm, a["logincount"])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table_id = event.data_table.id

        if table_id == "ce-account-table":
            acc_table = self.query_one("#ce-account-table", DataTable)
            row = acc_table.get_row(event.row_key)
            if row:
                self.run_worker(self._load_chars(str(row[0])))

        elif table_id == "char-table":
            char_table = self.query_one("#char-table", DataTable)
            row = char_table.get_row(event.row_key)
            if not row:
                return
            self.query_one("#inp-char-id", Input).value = str(row[0])
            self.query_one("#inp-base-lv", Input).value = str(row[2])
            self.query_one("#inp-job-lv", Input).value = str(row[3])
            self.query_one("#inp-job", Input).value = str(row[4])
            self.query_one("#inp-str", Input).value = str(row[5])
            self.query_one("#inp-agi", Input).value = str(row[6])
            self.query_one("#inp-vit", Input).value = str(row[7])
            self.query_one("#inp-int", Input).value = str(row[8])
            self.query_one("#inp-dex", Input).value = str(row[9])
            self.query_one("#inp-luk", Input).value = str(row[10])
            self.query_one("#inp-zeny", Input).value = str(row[11])
            # Auto-calc points for current state
            self._calc_points()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "btn-save":
            self.run_worker(self._save_char())
        elif bid == "btn-max":
            self._fill_max()
        elif bid == "btn-reset":
            self._reset_stats()

    def _get_stat_values(self) -> dict[str, int]:
        """Read current stat values from inputs."""
        stats = {}
        for key in ("str", "agi", "vit", "int", "dex", "luk"):
            val = self.query_one(f"#inp-{key}", Input).value.strip()
            stats[key] = int(val) if val else 1
        return stats

    def _calc_points(self) -> None:
        """Auto-calculate status_point and skill_point based on level and stats."""
        base_lv_str = self.query_one("#inp-base-lv", Input).value.strip()
        job_lv_str = self.query_one("#inp-job-lv", Input).value.strip()

        if not base_lv_str:
            return

        base_lv = int(base_lv_str)
        job_lv = int(job_lv_str) if job_lv_str else 1

        # Status points: total from table - cost of current stats
        total_points = self._statpoint_table.get(base_lv, 48)
        stats = self._get_stat_values()
        spent = sum(total_stat_cost(v) for v in stats.values())
        remaining = max(0, total_points - spent)
        self.query_one("#inp-status-pt", Input).value = str(remaining)

        # Skill points: job_level - 1 (approximation, ignores already-learned skills)
        self.query_one("#inp-skill-pt", Input).value = str(max(0, job_lv - 1))

    def _fill_max(self) -> None:
        """Set level to max and calculate achievable stats."""
        base_lv = 200
        job_lv = 70
        self.query_one("#inp-base-lv", Input).value = str(base_lv)
        self.query_one("#inp-job-lv", Input).value = str(job_lv)

        # Total points at level 200 = 4099
        total = self._statpoint_table.get(base_lv, 4099)

        # Find max even stat distribution for 6 stats
        # Binary search for the highest stat all 6 can reach
        lo, hi = 1, 130
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if total_stat_cost(mid) * 6 <= total:
                lo = mid
            else:
                hi = mid - 1
        max_stat = lo

        for key in ("str", "agi", "vit", "int", "dex", "luk"):
            self.query_one(f"#inp-{key}", Input).value = str(max_stat)

        spent = total_stat_cost(max_stat) * 6
        remaining = max(0, total - spent)
        self.query_one("#inp-status-pt", Input).value = str(remaining)
        self.query_one("#inp-skill-pt", Input).value = str(job_lv - 1)

        self.notify(f"Max even stats: {max_stat} all ({remaining} pts remaining)")

    def _reset_stats(self) -> None:
        """Reset all stats to 1 and give full points for current level."""
        base_lv_str = self.query_one("#inp-base-lv", Input).value.strip()
        job_lv_str = self.query_one("#inp-job-lv", Input).value.strip()
        if not base_lv_str:
            self.notify("Set a base level first", severity="error")
            return

        base_lv = int(base_lv_str)
        job_lv = int(job_lv_str) if job_lv_str else 1

        for key in ("str", "agi", "vit", "int", "dex", "luk"):
            self.query_one(f"#inp-{key}", Input).value = "1"

        total = self._statpoint_table.get(base_lv, 48)
        spent = total_stat_cost(1) * 6  # cost of 6 stats at 1 = 0
        self.query_one("#inp-status-pt", Input).value = str(total - spent)
        self.query_one("#inp-skill-pt", Input).value = str(max(0, job_lv - 1))
        self.notify(f"Stats reset! {total} status pts, {job_lv - 1} skill pts")

    async def _load_chars(self, acc_id: str) -> None:
        ssh = self.app.ssh
        if not ssh:
            return

        sql = (
            "SELECT c.char_id, c.name, c.base_level, c.job_level, c.class, "
            "c.str, c.agi, c.vit, c.int, c.dex, c.luk, c.zeny, "
            "c.status_point, c.skill_point "
            f"FROM `char` c WHERE c.account_id = {acc_id};"
        )
        rc, out, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
        if rc != 0:
            self.notify(f"Query failed: {err}", severity="error")
            return

        table = self.query_one("#char-table", DataTable)
        table.clear()
        lines = out.strip().splitlines()
        if len(lines) <= 1:
            self.notify(f"No characters for account {acc_id}", severity="warning")
            return

        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) >= 14:
                table.add_row(*parts[:12])

        self.notify(f"Loaded {len(lines) - 1} character(s) for account {acc_id}")

    async def _save_char(self) -> None:
        char_id = self.query_one("#inp-char-id", Input).value.strip()
        if not char_id:
            self.notify("Click a character row first", severity="error")
            return

        # Auto-calculate points before saving
        self._calc_points()

        fields = {
            "base_level": self.query_one("#inp-base-lv", Input).value.strip(),
            "job_level": self.query_one("#inp-job-lv", Input).value.strip(),
            "class": self.query_one("#inp-job", Input).value.strip(),
            "str": self.query_one("#inp-str", Input).value.strip(),
            "agi": self.query_one("#inp-agi", Input).value.strip(),
            "vit": self.query_one("#inp-vit", Input).value.strip(),
            "`int`": self.query_one("#inp-int", Input).value.strip(),
            "dex": self.query_one("#inp-dex", Input).value.strip(),
            "luk": self.query_one("#inp-luk", Input).value.strip(),
            "zeny": self.query_one("#inp-zeny", Input).value.strip(),
            "status_point": self.query_one("#inp-status-pt", Input).value.strip(),
            "skill_point": self.query_one("#inp-skill-pt", Input).value.strip(),
        }

        # Build SET clause, skip empty
        sets = []
        for col, val in fields.items():
            if val:
                sets.append(f"{col}={val}")

        if not sets:
            self.notify("No values to update", severity="error")
            return

        ssh = self.app.ssh
        if not ssh:
            return

        result = self.query_one("#edit-result", Static)

        # Check if character is online
        rc, out, _ = await asyncio.to_thread(
            ssh.docker_exec_db,
            f"SELECT online FROM `char` WHERE char_id={char_id};"
        )
        if rc == 0:
            lines = out.strip().splitlines()
            if len(lines) >= 2 and lines[1].strip() == "1":
                result.update(
                    f"[red]Character {char_id} is ONLINE! "
                    f"Player must log out first, otherwise server will overwrite changes.[/]"
                )
                return

        # Apply changes
        sql = f"UPDATE `char` SET {', '.join(sets)} WHERE char_id={char_id};"
        rc, out, err = await asyncio.to_thread(ssh.docker_exec_db, sql)
        if rc == 0:
            result.update(f"[green]Character {char_id} updated! Login to see changes.[/]")
        else:
            result.update(f"[red]Failed: {err}[/]")
