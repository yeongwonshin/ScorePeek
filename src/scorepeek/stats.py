from __future__ import annotations

import statistics

from .models import HistogramBin, ScoreRecord, ScoreSummary


def build_histogram(values: list[float], bin_size: int = 10) -> list[HistogramBin]:
    bins: list[HistogramBin] = []
    for lower in range(0, 100, bin_size):
        upper = lower + bin_size
        if upper >= 100:
            count = sum(lower <= value <= upper for value in values)
            label = f"{lower}-{upper}"
        else:
            count = sum(lower <= value < upper for value in values)
            label = f"{lower}-{upper - 1}"
        bins.append(HistogramBin(label=label, lower=float(lower), upper=float(upper), count=int(count)))
    return bins


def percentile_rank(values: list[float], my_score: float) -> float:
    if not values:
        return 0.0
    less_or_equal = sum(value <= my_score for value in values)
    return round((less_or_equal / len(values)) * 100, 2)


def estimated_rank(values: list[float], my_score: float) -> int:
    return 1 + sum(value > my_score for value in values)


def compute_summary(
    course_id: str,
    assessment: str,
    records: list[ScoreRecord],
    my_score: float | None = None,
    min_anonymous_count: int = 1,
) -> ScoreSummary:
    values = [record.normalized_score for record in records]
    count = len(values)
    privacy_status = "ok" if count >= min_anonymous_count else "insufficient_samples"

    if not values:
        return ScoreSummary(
            course_id=course_id,
            assessment=assessment,
            count=0,
            privacy_status="insufficient_samples",
            message="No anonymous scores have been submitted yet.",
            histogram=build_histogram([]),
        )

    mean = round(statistics.fmean(values), 2)
    median = round(statistics.median(values), 2)
    stdev = round(statistics.pstdev(values), 2) if count > 1 else 0.0
    minimum = round(min(values), 2)
    maximum = round(max(values), 2)

    my_percentile = None
    my_rank = None
    if my_score is not None:
        my_percentile = percentile_rank(values, my_score)
        my_rank = estimated_rank(values, my_score)

    if privacy_status == "insufficient_samples":
        message = f"Only {count} score(s) have been submitted. Treat the distribution as provisional."
    else:
        message = f"{count} anonymous score(s) are included in this distribution."

    return ScoreSummary(
        course_id=course_id,
        assessment=assessment,
        count=count,
        mean=mean,
        median=median,
        stdev=stdev,
        minimum=minimum,
        maximum=maximum,
        my_score=round(my_score, 2) if my_score is not None else None,
        my_percentile=my_percentile,
        my_estimated_rank=my_rank,
        privacy_status=privacy_status,
        message=message,
        histogram=build_histogram(values),
    )
