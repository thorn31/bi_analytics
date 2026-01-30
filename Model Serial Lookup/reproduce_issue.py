from msl.pipeline.normalize_rules import _heuristic_normalize_one
import json

record = {
    "brand": "TEST_BRAND",
    "section_title": "Style 1: Test",
    "section_text": "Year: See chart.",
    "source_url": "http://test.com",
    "retrieved_on": "2026-01-01",
    "image_urls": ["http://test.com/chart.jpg"]
}

normalized = _heuristic_normalize_one(record)
print(json.dumps(normalized, indent=2))
