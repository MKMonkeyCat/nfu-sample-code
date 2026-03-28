from __future__ import annotations

from collections import Counter

from project.types import (
    CountRow,
    RoundComparisonRow,
    StatisticsData,
    SummaryData,
    VoteRecord,
    VoteTableRow,
)


def summarize_votes(records: list[VoteRecord]) -> SummaryData:
    counts: Counter[str] = Counter(r.option for r in records)
    total = len(records)

    if not counts:
        return SummaryData(total=0, counts={}, modes=[], mode_count=0, least=[], least_count=0)

    mode_count = max(counts.values())
    least_count = min(counts.values())

    modes = sorted([option for option, count in counts.items() if count == mode_count])
    least = sorted([option for option, count in counts.items() if count == least_count])

    return SummaryData(
        total=total,
        counts=dict(sorted(counts.items())),
        modes=modes,
        mode_count=mode_count,
        least=least,
        least_count=least_count,
    )


def build_statistics(records: list[VoteRecord]) -> StatisticsData:
    summary = summarize_votes(records)
    rounds = sorted({r.round for r in records})
    unique_voters = len({r.name for r in records})

    return StatisticsData(
        total=summary.total,
        counts=summary.counts,
        modes=summary.modes,
        mode_count=summary.mode_count,
        least=summary.least,
        least_count=summary.least_count,
        unique_voters=unique_voters,
        unique_options=len(summary.counts),
        rounds=rounds,
    )


def build_count_rows(summary: SummaryData) -> list[CountRow]:
    if summary.total == 0:
        return []

    rows: list[CountRow] = []
    for option, votes in summary.counts.items():
        ratio = f"{(votes / summary.total) * 100:.1f}%"
        rows.append(CountRow(option=option, votes=votes, ratio=ratio))
    return rows


def build_vote_table_rows(records: list[VoteRecord]) -> list[VoteTableRow]:
    return [
        VoteTableRow(
            round_name=record.round,
            voter_name=record.name,
            option=record.option,
            vote_time=record.vote_time,
        )
        for record in records
    ]


def build_round_comparison_rows(records: list[VoteRecord]) -> list[RoundComparisonRow]:
    rounds = sorted({record.round for record in records})
    rows: list[RoundComparisonRow] = []

    for round_name in rounds:
        one_round = [record for record in records if record.round == round_name]
        summary = summarize_votes(one_round)
        modes_text = "、".join(summary.modes) if summary.modes else "無"
        rows.append(
            RoundComparisonRow(
                round_name=round_name,
                total_votes=summary.total,
                modes_text=f"{modes_text}（{summary.mode_count}票）" if summary.mode_count > 0 else "無",
            )
        )

    return rows


class VoteAnalysisService:
    summarize = staticmethod(summarize_votes)
    statistics = staticmethod(build_statistics)
    count_rows = staticmethod(build_count_rows)
    vote_rows = staticmethod(build_vote_table_rows)
    round_rows = staticmethod(build_round_comparison_rows)
