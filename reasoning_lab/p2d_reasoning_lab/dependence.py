"""Visible source-dependence clustering and sensitivity scenarios."""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from urllib.parse import urlsplit


def _origin_key(ground: dict[str, Any]) -> tuple[str, str]:
    origin = str(ground.get("origin_path") or "").strip().casefold()
    if origin:
        return ("origin_path", origin)
    url = str(ground.get("url") or "").strip()
    if url:
        parsed = urlsplit(url)
        return ("host", parsed.netloc.casefold())
    return ("unknown", str(ground.get("id") or "unidentified"))


def cluster_grounds(grounds: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    unknown: list[str] = []
    for ground in grounds:
        key = _origin_key(ground)
        identifier = str(ground.get("id") or "")
        groups[key].append(identifier)
        if key[0] == "unknown":
            unknown.append(identifier)
    clusters = [
        {
            "id": f"ECL{index}",
            "basis": key[0],
            "origin": key[1],
            "ground_ids": sorted(ids),
        }
        for index, (key, ids) in enumerate(sorted(groups.items()), start=1)
    ]
    return {
        "policy": "origin-path-then-host-v1",
        "clusters": clusters,
        "unknown_ground_ids": sorted(unknown),
        "independence_not_assumed": True,
        "distinct_clusters": len(clusters),
    }


def dependence_scenarios(record: dict[str, Any]) -> dict[str, Any]:
    clusters = list(record.get("clusters") or [])
    return {
        "optimistic_independence": {
            "effective_units": sum(len(item["ground_ids"]) for item in clusters),
            "assumption": "each ground is independent",
        },
        "origin_clustered": {
            "effective_units": len(clusters),
            "assumption": "grounds sharing an identified origin count once",
        },
        "strict_unknown_dependence": {
            "effective_units": sum(
                1 for item in clusters if item.get("basis") != "unknown"
            )
            + (1 if record.get("unknown_ground_ids") else 0),
            "assumption": "all unknown-origin grounds share one dependence cluster",
        },
    }
