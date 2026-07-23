from p2d_reasoning_lab.coverage import (
    build_coverage_record,
    build_evidence_depth_record,
)
from p2d_reasoning_lab.dependence import cluster_grounds, dependence_scenarios


def test_coverage_is_not_a_truth_assessment() -> None:
    lanes = [
        {
            "direction": "support",
            "searches_run": ["q1"],
            "grounds": [{"id": "g1", "url": "https://a.test/x"}],
            "observed_saturation": "no",
        },
        {
            "direction": "challenge",
            "searches_run": ["q2"],
            "grounds": [{"id": "g2", "url": "https://b.test/y"}],
            "observed_saturation": "no",
        },
    ]
    record = build_coverage_record(lanes)
    assert record["coverage_state"] == "moderate"
    assert "truth" in record["semantic_note"]
    assert "valence" not in record


def test_evidence_depth_has_five_segment_scale() -> None:
    record = build_evidence_depth_record(
        [
            {
                "id": "g1",
                "url": "https://a.test/x",
                "directness": "direct",
                "source_type": "primary",
            }
        ]
    )
    assert record["segments_total"] == 5
    assert 1 <= record["segments_filled"] <= 5


def test_shared_origin_is_one_dependence_cluster() -> None:
    record = cluster_grounds(
        [
            {"id": "g1", "origin_path": "Dataset X", "url": "https://a.test"},
            {"id": "g2", "origin_path": "dataset x", "url": "https://b.test"},
        ]
    )
    assert record["distinct_clusters"] == 1
    scenarios = dependence_scenarios(record)
    assert scenarios["optimistic_independence"]["effective_units"] == 2
    assert scenarios["origin_clustered"]["effective_units"] == 1
