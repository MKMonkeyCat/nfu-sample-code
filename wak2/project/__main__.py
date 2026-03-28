from __future__ import annotations

from project.core import VoteCoreService


def main() -> None:
    service = VoteCoreService()
    print(service.storage.list_vote_configs())


if __name__ == "__main__":
    main()
