"""Unit tests for the bill status-derivation logic (no Spark session needed)."""

import sys

sys.path.append("..")
from jobs.common.bill_status import derive_status, derive_next_hearing_date, tag_topics


def test_derive_status_defaults_to_introduced_with_no_actions():
    assert derive_status([]) == "introduced"


def test_derive_status_walks_chronologically_to_latest_classification():
    actions = [
        {"date": "2026-01-05", "classification": ["introduction"]},
        {"date": "2026-02-10", "classification": ["committee-referral"]},
        {"date": "2026-03-01", "classification": ["reading-2"]},
    ]
    assert derive_status(actions) == "hearing_scheduled"


def test_derive_status_terminal_outcome():
    actions = [
        {"date": "2026-01-05", "classification": ["introduction"]},
        {"date": "2026-06-01", "classification": ["passage"]},
    ]
    assert derive_status(actions) == "passed"


def test_derive_next_hearing_date_picks_earliest_future_hearing_like_action():
    actions = [
        {"date": "2099-01-01", "classification": ["reading-2"]},
        {"date": "2099-05-05", "classification": ["committee-passage"]},
    ]
    assert derive_next_hearing_date(actions) == "2099-01-01"


def test_tag_topics_matches_housing_keywords():
    assert "housing" in tag_topics("This bill caps annual rent increases for tenants.")


def test_tag_topics_returns_empty_for_unrelated_text():
    assert tag_topics("A bill about fishing license fees.") == []
