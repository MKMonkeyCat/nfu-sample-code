from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

from project.csv_tool import CSVManager, csv_field
from project.types import VoteRecord

CONFIG_FILE = Path("data/config/vote_configs.json")


@dataclass
class VoteCsvRow:
    name: str = csv_field("姓名")
    option: str = csv_field("選項")
    round: str = csv_field("輪次", default="default")


@dataclass
class VoteConfig:
    name: str
    options: set[str]
    start_time: str
    end_time: str
    rounds: dict[str, VoteRoundConfig]
    path: Path

    @staticmethod
    def from_dict(data: dict[str, Any]) -> VoteConfig:
        rounds_data = data.get("rounds", {})
        rounds: dict[str, VoteRoundConfig] = {}
        if isinstance(rounds_data, dict):
            for round_uuid, round_value in rounds_data.items():
                if isinstance(round_value, dict):
                    rounds[str(round_uuid)] = VoteRoundConfig.from_dict(round_value)

        if not rounds:
            now = datetime.now(UTC)
            rounds["default"] = VoteRoundConfig(
                name="預設輪次",
                start_time=now.isoformat(timespec="seconds"),
                end_time=(now + timedelta(days=3650)).isoformat(timespec="seconds"),
            )

        start_time = str(data.get("start_time", "")).strip()
        end_time = str(data.get("end_time", "")).strip()
        if not start_time or not end_time:
            raise ValueError("Vote config start_time/end_time cannot be empty")

        return VoteConfig(
            name=data["name"],
            options=set(data["options"]),
            start_time=start_time,
            end_time=end_time,
            rounds=rounds,
            path=Path(data["path"]),
        )


@dataclass
class VoteRoundConfig:
    name: str
    start_time: str
    end_time: str

    @staticmethod
    def from_dict(data: dict[str, Any]) -> VoteRoundConfig:
        start_time = str(data.get("start_time", "")).strip()
        end_time = str(data.get("end_time", "")).strip()
        if not start_time or not end_time:
            raise ValueError("Round config start_time/end_time cannot be empty")

        return VoteRoundConfig(
            name=str(data.get("name", "未命名輪次")).strip() or "未命名輪次",
            start_time=start_time,
            end_time=end_time,
        )


def _parse_datetime(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("Datetime cannot be empty")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    dt = datetime.fromisoformat(text)
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _is_time_in_window(now: datetime, start_time: str, end_time: str) -> bool:
    start_dt = _parse_datetime(start_time)
    end_dt = _parse_datetime(end_time)
    return start_dt <= now <= end_dt


class VoteCoreSystem:
    def __init__(self, config_path=CONFIG_FILE) -> None:
        self.config_path = config_path
        self.votes: dict[Path, CSVManager[VoteCsvRow, Any]] = {}
        self.vote_configs: dict[str, VoteConfig] = {}
        self.setup_votes_from_config(self.config_path)

    def setup_votes_from_config(self, config_path: Path) -> None:
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("{}", encoding="utf-8")
        else:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Invalid config format: expected a JSON object")

            for uuid, config_data in data.items():
                config = VoteConfig.from_dict(config_data)
                self.vote_configs[uuid] = config
                self.votes[config.path] = CSVManager(config.path, VoteCsvRow)
                self.votes[config.path].ensure_file()

    def list_vote_configs(self) -> list[tuple[str, VoteConfig]]:
        return list(self.vote_configs.items())

    def get_vote_config(self, uuid: str) -> VoteConfig | None:
        return self.vote_configs.get(uuid)

    def create_vote(self, name: str, options: set[str]) -> str:
        uuid = str(uuid4())
        file_slug = uuid.replace("-", "")[:12]
        default_round_uuid = str(uuid4())
        now = datetime.now(UTC)
        default_start = now.isoformat(timespec="seconds")
        default_end = (now + timedelta(days=3650)).isoformat(timespec="seconds")

        config = VoteConfig(
            name=name,
            options=set(options),
            start_time=default_start,
            end_time=default_end,
            rounds={
                default_round_uuid: VoteRoundConfig(
                    name="第1輪", start_time=default_start, end_time=default_end
                ),
            },
            path=Path(f"data/vote_{file_slug}.csv"),
        )
        self.vote_configs[uuid] = config
        self.votes[config.path] = CSVManager(config.path, VoteCsvRow)
        self.votes[config.path].ensure_file()
        self.save_vote_configs(self.config_path)

        return uuid

    def delete_vote(self, uuid: str) -> VoteConfig | None:
        if uuid in self.vote_configs:
            old_config = self.vote_configs.get(uuid)

            config = self.vote_configs[uuid]
            if config.path in self.votes:
                del self.votes[config.path]

            del self.vote_configs[uuid]
            self.save_vote_configs(self.config_path)
            return old_config
        return None

    def update_vote(self, uuid: str, *, name: str, options: set[str]) -> VoteConfig:
        config = self.vote_configs.get(uuid)
        if config is None:
            raise ValueError("Vote config not found")

        normalized_name = name.strip()
        normalized_options = {item.strip() for item in options if item.strip()}

        if not normalized_name:
            raise ValueError("Vote name cannot be empty")
        if len(normalized_options) < 2:
            raise ValueError("Vote options must be at least 2")

        config.name = normalized_name
        config.options = normalized_options
        self.save_vote_configs(self.config_path)
        return config

    def update_vote_rounds(
        self,
        uuid: str,
        *,
        start_time: str,
        end_time: str,
        rounds: dict[str, VoteRoundConfig],
    ) -> VoteConfig:
        config = self.vote_configs.get(uuid)
        if config is None:
            raise ValueError("Vote config not found")

        normalized_rounds = {key.strip(): value for key, value in rounds.items() if key.strip()}
        if not normalized_rounds:
            raise ValueError("必須至少定義一輪")

        for round_uuid, round_config in normalized_rounds.items():
            if not round_config.name.strip():
                raise ValueError(f"錯誤，輪次名稱不能為空: {round_uuid[:8]}")

            round_start = _parse_datetime(round_config.start_time)
            round_end = _parse_datetime(round_config.end_time)
            if round_start > round_end:
                raise ValueError(f"錯誤，結束時間不能早於開始時間: {round_uuid[:8]}")

        vote_start = _parse_datetime(start_time)
        vote_end = _parse_datetime(end_time)
        if vote_start > vote_end:
            raise ValueError("錯誤，投票結束時間不能早於開始時間")

        config.start_time = start_time.strip()
        config.end_time = end_time.strip()
        config.rounds = normalized_rounds
        self.save_vote_configs(self.config_path)
        return config

    def get_active_round(self, uuid: str, now: datetime | None = None) -> tuple[str, VoteRoundConfig] | None:
        config = self.vote_configs.get(uuid)
        if config is None or not config.rounds:
            return None

        clock = now or datetime.now(UTC)
        if not _is_time_in_window(clock, config.start_time, config.end_time):
            return None

        sorted_rounds = sorted(
            config.rounds.items(),
            key=lambda item: item[1].start_time or "",
        )
        for round_uuid, round_config in sorted_rounds:
            if _is_time_in_window(clock, round_config.start_time, round_config.end_time):
                return round_uuid, round_config

        if len(sorted_rounds) == 1:
            return sorted_rounds[0]
        return None

    def get_round_name(self, uuid: str, round_uuid: str) -> str:
        config = self.vote_configs.get(uuid)
        if config is None:
            return round_uuid
        round_config = config.rounds.get(round_uuid)
        if round_config is None:
            return round_uuid
        return round_config.name

    def add_vote_record(self, uuid: str, voter_name: str, option: str, round_name: str = "default") -> None:
        config = self.vote_configs.get(uuid)
        if config is None:
            raise ValueError("Vote config not found")
        if option not in config.options:
            raise ValueError("Option not allowed in this vote")
        if round_name not in config.rounds:
            raise ValueError("Round not found in this vote")

        manager = self.votes[config.path]
        manager.append(
            VoteCsvRow(name=voter_name.strip(), option=option.strip(), round=round_name.strip() or "default")
        )

    def read_vote_records(self, uuid: str, round_name: str | None = None) -> list[VoteRecord]:
        config = self.vote_configs.get(uuid)
        if config is None:
            return []

        records: list[VoteRecord] = []
        for row in self.votes[config.path].read_all():
            if round_name is not None and row.round != round_name:
                continue
            records.append(VoteRecord(name=row.name, option=row.option, round=row.round))
        return records

    def save_vote_configs(self, config_path: Path) -> None:
        data = {}
        for uuid, config in self.vote_configs.items():
            data[uuid] = {
                "name": config.name,
                "options": list(config.options),
                "start_time": config.start_time,
                "end_time": config.end_time,
                "path": str(config.path),
                "rounds": {
                    round_uuid: {
                        "name": round_config.name,
                        "start_time": round_config.start_time,
                        "end_time": round_config.end_time,
                    }
                    for round_uuid, round_config in config.rounds.items()
                },
            }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
