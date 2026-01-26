from __future__ import annotations

import re
from dataclasses import dataclass

from msl.decoder.io import AttributeRule, SerialRule


@dataclass(frozen=True)
class RuleIssue:
    rule_type: str
    brand: str
    style_name: str
    issue: str


def validate_serial_rules(rules: list[SerialRule]) -> tuple[list[SerialRule], list[RuleIssue]]:
    accepted: list[SerialRule] = []
    issues: list[RuleIssue] = []

    for r in rules:
        if r.rule_type == "guidance":
            if not r.guidance_action or not r.guidance_text:
                issues.append(RuleIssue("SerialDecodeRule", r.brand, r.style_name, "guidance_missing_fields"))
                continue
            accepted.append(r)
            continue

        # decode rules
        if not r.serial_regex:
            issues.append(RuleIssue("SerialDecodeRule", r.brand, r.style_name, "missing_serial_regex"))
            continue
        try:
            rx = re.compile(r.serial_regex)
        except Exception as e:
            issues.append(RuleIssue("SerialDecodeRule", r.brand, r.style_name, f"bad_regex:{e}"))
            continue
        if not r.example_serials:
            issues.append(RuleIssue("SerialDecodeRule", r.brand, r.style_name, "missing_examples"))
            continue
        if not any(rx.search(ex) for ex in r.example_serials if isinstance(ex, str)):
            issues.append(RuleIssue("SerialDecodeRule", r.brand, r.style_name, "examples_do_not_match_regex"))
            continue
        accepted.append(r)

    return accepted, issues


def validate_attribute_rules(rules: list[AttributeRule]) -> tuple[list[AttributeRule], list[RuleIssue]]:
    accepted: list[AttributeRule] = []
    issues: list[RuleIssue] = []

    for r in rules:
        if r.rule_type == "guidance":
            if not r.guidance_action or not r.guidance_text:
                issues.append(RuleIssue("AttributeDecodeRule", r.brand, r.attribute_name, "guidance_missing_fields"))
                continue
            accepted.append(r)
            continue

        if not r.attribute_name:
            issues.append(RuleIssue("AttributeDecodeRule", r.brand, r.attribute_name, "missing_attribute_name"))
            continue
        ve = r.value_extraction or {}
        if not isinstance(ve, dict) or not ve:
            issues.append(RuleIssue("AttributeDecodeRule", r.brand, r.attribute_name, "missing_value_extraction"))
            continue
        if "positions" not in ve and "pattern" not in ve:
            issues.append(
                RuleIssue("AttributeDecodeRule", r.brand, r.attribute_name, "value_extraction_missing_positions_or_pattern")
            )
            continue
        accepted.append(r)

    return accepted, issues
