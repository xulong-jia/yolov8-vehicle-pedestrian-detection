"""Tests for lightweight Bad Case metadata collection."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_bad_case_record_serializes_and_jsonl_round_trips(tmp_path):
    from src.services.bad_case_service import BadCaseRecord, BadCaseService

    record = BadCaseRecord(
        module="tracker",
        case_type="id_switch",
        video_id="demo",
        frame_index=12,
        timestamp_sec=0.4,
        track_id=7,
        expected_result="single stable track",
        actual_result="track id changed",
        root_cause="occlusion",
        tags=["occlusion", "real_video_case"],
        snapshot_path="/tmp/snapshots/frame_12.jpg",
        added_to_eval_set=True,
    )

    data = record.to_dict()
    assert data["case_id"].startswith("BC-")
    assert data["tags"] == "occlusion,real_video_case"
    assert data["added_to_eval_set"] == "yes"
    assert data["created_at"]

    jsonl_path = tmp_path / "bad_cases.jsonl"
    service = BadCaseService(csv_path=tmp_path / "bad_cases.csv", jsonl_path=None)
    service.write_jsonl([record], jsonl_path)

    loaded = service.read_jsonl(jsonl_path)
    assert loaded == [data]


def test_bad_case_service_writes_and_reads_csv_and_jsonl(tmp_path):
    from src.services.bad_case_service import BAD_CASE_FIELDS, BadCaseService

    service = BadCaseService(
        csv_path=tmp_path / "bad_cases" / "bad_cases.csv",
        jsonl_path=tmp_path / "bad_cases" / "bad_cases.jsonl",
    )

    created = service.add_case(
        {
            "case_id": "BC-0001",
            "module": "counter",
            "case_type": "count_error",
            "video_id": "demo",
            "expected_result": "2 crossings",
            "actual_result": "1 crossing",
            "root_cause": "line boundary",
            "tags": "line_boundary,needs_review",
        }
    )

    assert set(created) == set(BAD_CASE_FIELDS)
    assert service.list_cases() == [created]
    assert service.csv_path.exists()
    assert service.jsonl_path is not None
    assert service.jsonl_path.exists()


def test_bad_case_api_create_and_list_use_metadata_only_service(monkeypatch, tmp_path):
    from src import api
    from src.services.bad_case_service import BadCaseService

    monkeypatch.setattr(
        api,
        "bad_case_service",
        BadCaseService(
            csv_path=tmp_path / "bad_cases.csv",
            jsonl_path=tmp_path / "bad_cases.jsonl",
        ),
    )
    client = TestClient(api.create_app())

    response = client.post(
        "/api/bad-cases",
        json={
            "module": "event",
            "case_type": "rule_error",
            "video_id": "demo",
            "frame_index": 5,
            "timestamp_sec": 0.17,
            "expected_result": "no warning",
            "actual_result": "crowd warning",
            "root_cause": "threshold too low",
            "tags": ["synthetic_case"],
            "snapshot_path": "/tmp/snapshots/event.png",
            "added_to_eval_set": False,
        },
    )

    assert response.status_code == 200
    created = response.json()
    assert created["module"] == "event"
    assert created["tags"] == "synthetic_case"
    assert created["snapshot_path"] == "/tmp/snapshots/event.png"

    listed = client.get("/api/bad-cases")
    assert listed.status_code == 200
    assert listed.json() == [created]
