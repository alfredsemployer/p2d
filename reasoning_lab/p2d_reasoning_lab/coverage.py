"""Research coverage and evidence depth as separate, deterministic records."""

from __future__ import annotations

from typing import Any


COVERAGE_HARVEY_QUARTERS = {
    "not_assessed": 0,
    "limited": 1,
    "moderate": 2,
    "substantial": 3,
    "extensive": 4,
}


def build_coverage_record(lanes: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = [
        str(lane.get("direction") or "unknown")
        for lane in lanes
        if lane.get("direction")
    ]
    successful = [lane for lane in lanes if not lane.get("error")]
    succeeded = sorted(
        {
            str(lane.get("direction"))
            for lane in successful
            if lane.get("direction")
        }
    )
    queries = [
        query
        for lane in successful
        for query in lane.get("searches_run") or []
        if str(query).strip()
    ]
    grounds = [
        ground
        for lane in successful
        for ground in lane.get("grounds") or []
    ]
    source_urls = {
        str(ground.get("url") or "").strip()
        for ground in grounds
        if str(ground.get("url") or "").strip()
    }
    missing = [
        item
        for lane in lanes
        for item in lane.get("inaccessible_or_missing") or []
    ]
    saturation = [
        str(lane.get("observed_saturation") or "unclear")
        for lane in successful
    ]

    both_directions = {"support", "challenge"}.issubset(set(succeeded))
    all_saturated = bool(saturation) and all(item == "yes" for item in saturation)
    if not successful:
        state = "not_assessed"
        stopping_reason = "no_successful_research_lane"
    elif both_directions and all_saturated and len(source_urls) >= 4:
        state = "extensive"
        stopping_reason = "declared_saturation"
    elif both_directions and len(source_urls) >= 3:
        state = "substantial"
        stopping_reason = "bounded_resource_limit"
    elif both_directions:
        state = "moderate"
        stopping_reason = "bounded_resource_limit"
    else:
        state = "limited"
        stopping_reason = "missing_direction_or_lane_failure"

    return {
        "coverage_state": state,
        "directions_attempted": attempted,
        "directions_succeeded": succeeded,
        "queries_run": len(queries),
        "distinct_source_urls": len(source_urls),
        "inaccessible_or_missing": missing,
        "saturation_observations": saturation,
        "blind_spots": [
            str(lane.get("coverage_notes"))
            for lane in successful
            if str(lane.get("coverage_notes") or "").strip()
        ],
        "stopping_reason": stopping_reason,
        "opposition_sought": "challenge" in attempted,
        "harvey_quarters": COVERAGE_HARVEY_QUARTERS[state],
        "scale_quarters": 4,
        "mapping_version": "research-coverage-harvey-v1",
        "semantic_note": (
            "Coverage measures search breadth and stopping conditions, not "
            "truth, signed valence, or evidential force."
        ),
    }


def build_evidence_depth_record(grounds: list[dict[str, Any]]) -> dict[str, Any]:
    """Describe the depth of collected grounds without converting it to belief."""

    direct = sum(item.get("directness") == "direct" for item in grounds)
    urls = {
        str(item.get("url") or "").strip()
        for item in grounds
        if str(item.get("url") or "").strip()
    }
    primary = sum(
        str(item.get("source_type") or "").casefold()
        in {"primary", "official", "paper", "dataset"}
        for item in grounds
    )
    score = min(5, (1 if grounds else 0) + min(2, direct) + min(1, primary) + min(1, max(0, len(urls) - 1)))
    labels = {
        0: "no",
        1: "very limited",
        2: "limited",
        3: "moderate",
        4: "substantial",
        5: "deep",
    }
    return {
        "segments_filled": score,
        "segments_total": 5,
        "label": labels[score],
        "ground_count": len(grounds),
        "direct_ground_count": direct,
        "distinct_source_urls": len(urls),
        "primary_source_count": primary,
        "semantic_note": (
            "Evidence depth summarizes the record's depth; valence and "
            "confidence are assessed separately."
        ),
    }
