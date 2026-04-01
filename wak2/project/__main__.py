from __future__ import annotations

from project.core import VoteCoreService
from project.core.storage import VoteRoundConfig

DEFAULT_VOTE_CONFIG_UUID = "05592901-b475-44f5-977a-6110235836e4"
DEFAULT_VOTE_ROUND_UUID = "05592901-b475-44f5-977a-6110235836e5"


def main() -> None:
    service = VoteCoreService()

    if not service.storage.get_vote_config(DEFAULT_VOTE_CONFIG_UUID):
        service.storage.create_vote(
            name="範例投票",
            options={"A", "B", "C"},
            rounds={
                DEFAULT_VOTE_ROUND_UUID: VoteRoundConfig(
                    name="第1輪",
                    start_time="2024-01-01T00:00:00Z",
                    end_time="2999-12-31T23:59:59Z",
                ),
            },
            uuid=DEFAULT_VOTE_CONFIG_UUID,
        )

    while True:
        info = input("請輸入投票資訊（格式：姓名 選項）or end：").strip()
        if info == "end":
            print("-" * 41)
            print("投票人\t選項\t投票時間")

            records = service.storage.read_vote_records(DEFAULT_VOTE_CONFIG_UUID)
            for record in records:
                print(f"{record.name}\t{record.option}\t{record.vote_time}")

            print("-" * 41)
            statistics = service.analysis.statistics(records)
            print(f"總人數：{statistics.total}")
            print(f"眾數：{', '.join(statistics.modes)}")
            print(f"最少選項：{', '.join(statistics.least)}")
            print(
                f"選項分布：{', '.join(f'{option}: {count}' for option, count in statistics.counts.items())}"
            )
            break

        try:
            name, option = info.split(maxsplit=1)
            options = service.storage.vote_configs[DEFAULT_VOTE_CONFIG_UUID].options
            if option not in options:
                print(f"選項錯誤，請選擇：{', '.join(options)}")
                continue

            service.storage.add_vote_record(DEFAULT_VOTE_CONFIG_UUID, name, option)
            print("投票成功！")
        except ValueError:
            print("輸入格式錯誤，請使用：姓名 選項")


if __name__ == "__main__":
    import sys
    from pathlib import Path

    args = set(sys.argv[1:])
    if "--web" in args:
        import subprocess

        import project.web as project_web

        script_path = Path(project_web.__file__)
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(script_path),
            "--server.headless",
            "true",
        ]

        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            pass
    else:
        main()
