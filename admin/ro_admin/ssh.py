"""SSH connection manager for remote server operations."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SSHConfig:
    host: str
    user: str
    port: int = 22
    key_path: str = ""
    remote_dir: str = "/opt/rathena"


class SSH:
    """Wraps SSH/SCP operations to the VPS."""

    def __init__(self, cfg: SSHConfig):
        self.cfg = cfg

    def _ssh_args(self) -> list[str]:
        args = ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no"]
        if self.cfg.key_path:
            args += ["-i", self.cfg.key_path]
        if self.cfg.port != 22:
            args += ["-p", str(self.cfg.port)]
        args.append(f"{self.cfg.user}@{self.cfg.host}")
        return args

    def run(self, cmd: str, timeout: int = 30) -> tuple[int, str, str]:
        """Execute a remote command. Returns (returncode, stdout, stderr)."""
        args = self._ssh_args() + [cmd]
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)

    def scp_upload(self, local: str | Path, remote: str) -> tuple[int, str]:
        """Upload a file via SCP."""
        args = ["scp", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no"]
        if self.cfg.key_path:
            args += ["-i", self.cfg.key_path]
        if self.cfg.port != 22:
            args += ["-P", str(self.cfg.port)]
        args += [str(local), f"{self.cfg.user}@{self.cfg.host}:{remote}"]
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=60)
            return r.returncode, r.stderr if r.returncode else r.stdout
        except Exception as e:
            return -1, str(e)

    def docker_compose(self, subcmd: str, timeout: int = 30) -> tuple[int, str, str]:
        """Run docker compose command in the remote directory."""
        return self.run(
            f"cd {self.cfg.remote_dir} && docker compose {subcmd}",
            timeout=timeout,
        )

    def docker_exec_db(self, sql: str) -> tuple[int, str, str]:
        """Execute SQL in the MariaDB container."""
        escaped = sql.replace("'", "'\\''")
        return self.docker_compose(
            f"exec -T db mysql -u ragnarok -pragnarok ragnarok -e '{escaped}'",
            timeout=15,
        )

    def server_status(self) -> dict:
        """Get server process status."""
        rc, out, _ = self.docker_compose("ps --format json", timeout=10)
        if rc != 0:
            return {"online": False, "error": "Cannot connect"}

        # Parse docker compose ps output
        services = {}
        for line in out.strip().splitlines():
            if '"rathena"' in line or '"db"' in line:
                import json
                try:
                    svc = json.loads(line)
                    services[svc.get("Service", "unknown")] = svc.get("State", "unknown")
                except json.JSONDecodeError:
                    pass

        return {
            "online": any(v == "running" for v in services.values()),
            "services": services,
        }

    def online_players(self) -> list[dict]:
        """Get online players from the database."""
        rc, out, _ = self.docker_exec_db(
            "SELECT c.name, c.base_level, c.job_level, c.class "
            "FROM `char` c WHERE c.online = 1;"
        )
        if rc != 0:
            return []
        players = []
        for line in out.strip().splitlines()[1:]:  # skip header
            parts = line.split("\t")
            if len(parts) >= 4:
                players.append({
                    "name": parts[0],
                    "base_level": parts[1],
                    "job_level": parts[2],
                    "class": parts[3],
                })
        return players

    def account_list(self) -> list[dict]:
        """Get all accounts from the database."""
        rc, out, _ = self.docker_exec_db(
            "SELECT l.account_id, l.userid, l.sex, l.group_id, l.state, "
            "l.logincount, l.lastlogin "
            "FROM login l WHERE l.account_id >= 2000000 ORDER BY l.account_id;"
        )
        if rc != 0:
            return []
        accounts = []
        for line in out.strip().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 7:
                accounts.append({
                    "id": parts[0],
                    "userid": parts[1],
                    "sex": parts[2],
                    "group_id": parts[3],
                    "state": parts[4],
                    "logincount": parts[5],
                    "lastlogin": parts[6],
                })
        return accounts

    def statpoint_table(self) -> dict[int, int]:
        """Fetch the statpoint table from the server. Returns {level: total_points}."""
        rc, out, _ = self.docker_compose(
            "exec -T rathena grep -E 'Level:|Points:' /rathena/db/re/statpoint.yml",
            timeout=10,
        )
        if rc != 0:
            return {}
        table = {}
        current_level = 0
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("- Level:"):
                current_level = int(line.split(":")[1].strip())
            elif line.startswith("Points:") and current_level > 0:
                table[current_level] = int(line.split(":")[1].strip())
        return table

    def item_search(self, keyword: str) -> list[dict]:
        """Search item_db YAML files for items matching keyword."""
        # grep -i for case-insensitive, -B2 to capture Id before Name match
        files = (
            "/rathena/db/re/item_db_usable.yml "
            "/rathena/db/re/item_db_equip.yml "
            "/rathena/db/re/item_db_etc.yml "
            "/rathena/db/import/item_db.yml"
        )
        escaped_kw = keyword.replace("'", "'\\''")
        rc, out, _ = self.docker_compose(
            f"exec -T rathena grep -h -i -B2 'Name:.*{escaped_kw}' {files}",
            timeout=15,
        )
        if rc != 0:
            return []

        items = []
        current: dict = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("- Id:"):
                current = {"id": line.split(":", 1)[1].strip()}
            elif line.startswith("AegisName:"):
                current["aegis"] = line.split(":", 1)[1].strip()
            elif line.startswith("Name:"):
                current["name"] = line.split(":", 1)[1].strip()
                if "id" in current:
                    items.append(current)
                current = {}
            elif line == "--":
                current = {}

        return items[:50]  # limit results
