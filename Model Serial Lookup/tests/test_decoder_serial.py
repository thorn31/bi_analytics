from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from msl.decoder.decode import decode_serial
from msl.decoder.io import load_serial_rules_csv
from msl.decoder.normalize import normalize_brand
from msl.decoder.validate import validate_serial_rules


class TestDecoderSerial(unittest.TestCase):
    def test_decode_extracts_positions(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SerialDecodeRule.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "rule_type",
                        "brand",
                        "style_name",
                        "serial_regex",
                        "date_fields",
                        "example_serials",
                        "decade_ambiguity",
                        "guidance_action",
                        "guidance_text",
                        "evidence_excerpt",
                        "source_url",
                        "retrieved_on",
                        "image_urls",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "rule_type": "decode",
                        "brand": "TEST",
                        "style_name": "Style 1",
                        "serial_regex": r"^\d{6}$",
                        "date_fields": json.dumps(
                            {"year": {"positions": {"start": 1, "end": 2}}, "week": {"positions": {"start": 3, "end": 4}}}
                        ),
                        "example_serials": json.dumps(["250712"]),
                        "decade_ambiguity": json.dumps({"is_ambiguous": True}),
                        "guidance_action": "",
                        "guidance_text": "",
                        "evidence_excerpt": "excerpt",
                        "source_url": "url",
                        "retrieved_on": "2026-01-25",
                        "image_urls": "[]",
                    }
                )

            rules = load_serial_rules_csv(path)
            accepted, issues = validate_serial_rules(rules)
            self.assertEqual(len(issues), 0)

            res = decode_serial("TEST", "25 07 12", accepted)
            self.assertEqual(res.matched_style_name, "Style 1")
            self.assertEqual(res.manufacture_year_raw, "25")
            self.assertEqual(res.manufacture_week_raw, "07")
            self.assertTrue(res.ambiguous_decade)

    def test_guidance_is_returned_as_notes_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SerialDecodeRule.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "rule_type",
                        "brand",
                        "style_name",
                        "serial_regex",
                        "date_fields",
                        "example_serials",
                        "decade_ambiguity",
                        "guidance_action",
                        "guidance_text",
                        "evidence_excerpt",
                        "source_url",
                        "retrieved_on",
                        "image_urls",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "rule_type": "guidance",
                        "brand": "TEST",
                        "style_name": "Notes",
                        "serial_regex": "",
                        "date_fields": json.dumps({}),
                        "example_serials": json.dumps([]),
                        "decade_ambiguity": json.dumps({"is_ambiguous": True}),
                        "guidance_action": "contact_manufacturer",
                        "guidance_text": "Contact manufacturer",
                        "evidence_excerpt": "excerpt",
                        "source_url": "url",
                        "retrieved_on": "2026-01-25",
                        "image_urls": "[]",
                    }
                )
            rules = load_serial_rules_csv(path)
            accepted, _issues = validate_serial_rules(rules)

            res = decode_serial("TEST", "NOPE", accepted)
            self.assertEqual(res.confidence, "None")
            self.assertIn("Contact manufacturer", res.notes)

    def test_year_add_base_with_constraints_selects_correct_rule(self) -> None:
        # Simulates two rules that both match, but only one is valid by year constraint.
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Style old",
                serial_regex=r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000, "max_year": 2009}}},
                example_serials=["0901ABCD"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Style new",
                serial_regex=r"^(?=.*[A-Z])\d{4}[A-Z0-9]{3,30}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000, "min_year": 2010}}},
                example_serials=["1201ABCD"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res = decode_serial("TEST", "1201ABCD", accepted)
        self.assertEqual(res.matched_style_name, "Style new")
        self.assertEqual(res.manufacture_year, 2012)

    def test_equipment_type_gates_typed_serial_rule(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="Typed style",
                serial_regex=r"^\d{4}[A-Z]{2}$",
                equipment_types=["Cooling Condensing Unit"],
                date_fields={"year": {"positions": {"start": 1, "end": 4}}},
                example_serials=["2020AB"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res_ok = decode_serial("TEST", "2020AB", accepted, equipment_type="Cooling Condensing Unit")
        self.assertEqual(res_ok.confidence, "Low")
        self.assertEqual(res_ok.manufacture_year, 2020)

        res_mismatch = decode_serial("TEST", "2020AB", accepted, equipment_type="Boiler")
        self.assertEqual(res_mismatch.confidence, "None")

        res_missing = decode_serial("TEST", "2020AB", accepted, equipment_type=None)
        self.assertEqual(res_missing.manufacture_year, 2020)
        self.assertTrue(res_missing.typed_rule_applied_without_type_context)
        self.assertIn("type_context_missing_for_typed_serial_rule", res_missing.notes)

    def test_york_style1_and_style2_letter_codes(self) -> None:
        from msl.decoder.io import SerialRule

        month_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "K": 9, "L": 10, "M": 11, "N": 12}
        rules = [
            SerialRule(
                rule_type="decode",
                brand="YORK/JCI",
                priority=None,
                style_name="Manual: Style 1 (Plant + Y? + MonthLetter + ?Y + seq)",
                serial_regex=r"^[A-Z]\d[A-HK-N]\d\d{6,}$",
                equipment_types=[],
                date_fields={
                    "year": {"positions_list": [2, 4], "transform": {"type": "year_add_base", "base": 2000, "min_year": 2004, "max_year": 2035}},
                    "month": {"positions": {"start": 3, "end": 3}, "mapping": month_map},
                },
                example_serials=["A0A5896070"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="YORK/JCI",
                priority=None,
                style_name="Manual: Style 2 (Plant + MonthLetter + YearLetter + Letter + seq)",
                serial_regex=r"^(?:\([A-Z]\))?[A-Z][A-HK-N][BCDEH][A-Z]\d{6,}$",
                equipment_types=[],
                date_fields={
                    "month": {"pattern": {"regex": r"^(?:\([A-Z]\))?[A-Z]([A-HK-N])", "group": 1}, "mapping": month_map},
                    "year": {"pattern": {"regex": r"^(?:\([A-Z]\))?[A-Z][A-HK-N]([BCDEH])", "group": 1}, "mapping": {"B": 1994, "C": 1994, "H": 2002, "D": 2003, "E": 2003}},
                },
                example_serials=["NCHM034439", "(S)EBHM062202"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res1 = decode_serial("YORK/JCI", "A0A5896070", accepted)
        self.assertEqual(res1.manufacture_year, 2005)
        self.assertEqual(res1.manufacture_month, 1)

        res2 = decode_serial("YORK/JCI", "NCHM034439", accepted)
        self.assertEqual(res2.manufacture_year, 2002)
        self.assertEqual(res2.manufacture_month, 3)

        res3 = decode_serial("YORK/JCI", "(S)EBHM062202", accepted)
        self.assertEqual(res3.manufacture_year, 2002)
        self.assertEqual(res3.manufacture_month, 2)

    def test_friedrich_style2_yy_monthletter_sequence(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="FRIEDRICH",
                priority=None,
                style_name="Manual: Style 2 (YY + MonthLetter + Sequence)",
                serial_regex=r"^\d{2}[A-HJ-M][A-Z0-9]{5,}$",
                equipment_types=[],
                date_fields={
                    "year": {"positions": {"start": 1, "end": 2}},
                    "month": {"positions": {"start": 3, "end": 3}, "mapping": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "J": 9, "K": 10, "L": 11, "M": 12}},
                },
                example_serials=["92J010915", "85HO1432"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res = decode_serial("FRIEDRICH", "85HO1432", accepted, min_plausible_year=0)
        self.assertEqual(res.manufacture_year, 1985)
        self.assertEqual(res.manufacture_month, 8)

    def test_greenheck_style1_and_style2(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="GREENHECK",
                priority=None,
                style_name="Manual: Style 1 (YY + MonthLetter + 5 digits)",
                serial_regex=r"^\d{2}[A-L]\d{5}$",
                equipment_types=[],
                date_fields={
                    "year": {"positions": {"start": 1, "end": 2}},
                    "month": {"positions": {"start": 3, "end": 3}, "mapping": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12}},
                },
                example_serials=["85A00000"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="GREENHECK",
                priority=None,
                style_name="Manual: Style 2 (8 digits + YY + MM)",
                serial_regex=r"^\d{12}$",
                equipment_types=[],
                date_fields={
                    "year": {"positions": {"start": 9, "end": 10}, "transform": {"type": "year_add_base", "base": 2000, "min_year": 2005, "max_year": 2035}},
                    "month": {"positions": {"start": 11, "end": 12}},
                },
                example_serials=["103443330610"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        old = decode_serial("GREENHECK", "85A00000", accepted, min_plausible_year=0)
        self.assertEqual(old.manufacture_year, 1985)
        self.assertEqual(old.manufacture_month, 1)

        new = decode_serial("GREENHECK", "103443330610", accepted, min_plausible_year=0)
        self.assertEqual(new.manufacture_year, 2006)
        self.assertEqual(new.manufacture_month, 10)

    def test_mcquay_style6_skips_i_and_o_year_letters(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="MCQUAY",
                priority=None,
                style_name="Manual: Style 6 - DYM Format (1971-1994)",
                serial_regex=r"^[13457][A-HJ-NP-Z][A-M]\d+$",
                equipment_types=[],
                date_fields={
                    "year": {
                        "positions": {"start": 2, "end": 2},
                        "mapping": {
                            "A": 1971,
                            "B": 1972,
                            "C": 1973,
                            "D": 1974,
                            "E": 1975,
                            "F": 1976,
                            "G": 1977,
                            "H": 1978,
                            "J": 1979,
                            "K": 1980,
                            "L": 1981,
                            "M": 1982,
                            "N": 1983,
                            "P": 1984,
                            "Q": 1985,
                            "R": 1986,
                            "S": 1987,
                            "T": 1988,
                            "U": 1989,
                            "V": 1990,
                            "W": 1991,
                            "X": 1992,
                            "Y": 1993,
                            "Z": 1994,
                        },
                    },
                    "month": {
                        "positions": {"start": 3, "end": 3},
                        "mapping": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12, "M": 12},
                    },
                },
                example_serials=["5QF0025801", "3SF0054304"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        a = decode_serial("MCQUAY", "5QF0025801", accepted, min_plausible_year=0)
        self.assertEqual(a.manufacture_year, 1985)
        self.assertEqual(a.manufacture_month, 6)

        b = decode_serial("MCQUAY", "3SF0054304", accepted, min_plausible_year=0)
        self.assertEqual(b.manufacture_year, 1987)
        self.assertEqual(b.manufacture_month, 6)

    def test_decoder_rejects_invalid_month(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TEST",
                priority=None,
                style_name="YYMM style",
                serial_regex=r"^\d{2}\d{2}\d{6,}$",
                equipment_types=[],
                date_fields={
                    "year": {"positions": {"start": 1, "end": 2}, "transform": {"type": "year_add_base", "base": 2000}},
                    "month": {"positions": {"start": 3, "end": 4}},
                },
                example_serials=["1602393269"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        res = decode_serial("TEST", "2048480300176", accepted, min_plausible_year=0)
        self.assertEqual(res.confidence, "None")

    def test_climatemaster_style1_and_style2(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="CLIMATEMASTER",
                priority=None,
                style_name="Manual: Style 1 (Letter Year)",
                serial_regex=r"^[HABCDEFGJKLMNPQRSTUV]\d{8,9}$",
                equipment_types=[],
                date_fields={
                    "year": {
                        "positions": {"start": 1, "end": 1},
                        "mapping": {
                            "H": 1998,
                            "A": 1999,
                            "B": 2000,
                            "C": 2001,
                            "D": 2002,
                            "E": 2003,
                            "F": 2004,
                            "G": 2005,
                            "J": 2006,
                            "K": 2007,
                            "L": 2008,
                            "M": 2009,
                            "N": 2010,
                            "P": 2011,
                            "Q": 2012,
                            "R": 2013,
                            "S": 2014,
                            "T": 2015,
                            "U": 2016,
                            "V": 2017,
                        },
                    },
                    "week": {"positions": {"start": 3, "end": 4}},
                },
                example_serials=["S15219268"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="CLIMATEMASTER",
                priority=None,
                style_name="Manual: Style 2 (Numeric Year)",
                serial_regex=r"^\d{2}(0[1-9]|[1-4]\d|5[0-3])\d{5,}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 2}}, "week": {"positions": {"start": 3, "end": 4}}},
                example_serials=["19061010145", "920101015"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        s1 = decode_serial("CLIMATEMASTER", "S15219268", accepted, min_plausible_year=0)
        self.assertEqual(s1.manufacture_year, 2014)
        self.assertEqual(s1.manufacture_week, 52)

        s2 = decode_serial("CLIMATEMASTER", "920101015", accepted, min_plausible_year=0)
        self.assertEqual(s2.manufacture_year, 1992)
        self.assertEqual(s2.manufacture_week, 1)

    def test_snyder_general_year_letter_skips_i_and_o(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="SNYDER GENERAL",
                priority=None,
                style_name="Manual: Year letter (1971-1994, skips I/O)",
                serial_regex=r"^\d*[A-HJ-NP-Z][A-Z0-9-]+$",
                equipment_types=[],
                date_fields={
                    "year": {
                        "pattern": {"regex": r"^\d*([A-HJ-NP-Z])", "group": 1},
                        "mapping": {
                            "A": 1971,
                            "B": 1972,
                            "C": 1973,
                            "D": 1974,
                            "E": 1975,
                            "F": 1976,
                            "G": 1977,
                            "H": 1978,
                            "J": 1979,
                            "K": 1980,
                            "L": 1981,
                            "M": 1982,
                            "N": 1983,
                            "P": 1984,
                            "Q": 1985,
                            "R": 1986,
                            "S": 1987,
                            "T": 1988,
                            "U": 1989,
                            "V": 1990,
                            "W": 1991,
                            "X": 1992,
                            "Y": 1993,
                            "Z": 1994,
                        },
                    }
                },
                example_serials=["1UL83836-00", "UL83836-00"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        # Optional leading plant digit(s)
        r1 = decode_serial("SNYDER GENERAL", "1UL83836-00", accepted, min_plausible_year=0)
        self.assertEqual(r1.manufacture_year, 1989)  # U

        # No leading plant digit
        r2 = decode_serial("SNYDER GENERAL", "UL83836-00", accepted, min_plausible_year=0)
        self.assertEqual(r2.manufacture_year, 1989)  # U

    def test_emi_style1_year_from_two_digits_after_leading_digit(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="EMI",
                priority=None,
                style_name="Manual: Style 1 (1-YY-X-NNNN-WW)",
                serial_regex=r"^\d\d{2}[A-Z0-9]\d{4}\d{2}$",
                equipment_types=[],
                date_fields={
                    "year": {"pattern": {"regex": r"^\d(\d{2})", "group": 1}},
                    "week": {"pattern": {"regex": r"^\d\d{2}[A-Z0-9]\d{4}(\d{2})$", "group": 1}},
                },
                example_serials=["1996823830", "199C930510"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        a = decode_serial("EMI", "1-99-6-8238-30", accepted, min_plausible_year=0)
        self.assertEqual(a.manufacture_year, 1999)
        self.assertEqual(a.manufacture_week, 30)

        b = decode_serial("EMI", "1-99-C-9305-10", accepted, min_plausible_year=0)
        self.assertEqual(b.manufacture_year, 1999)
        self.assertEqual(b.manufacture_week, 10)

    def test_trane_legacy_letter_year_week_and_fallback_yy(self) -> None:
        from msl.decoder.io import SerialRule

        year_letter_map = {
            "W": 1983,
            "X": 1984,
            "Y": 1985,
            "S": 1986,
            "B": 1987,
            "C": 1988,
            "D": 1989,
            "E": 1990,
            "F": 1991,
            "G": 1992,
            "H": 1993,
            "J": 1994,
            "K": 1995,
            "L": 1996,
            "M": 1997,
            "N": 1998,
            "P": 1999,
            "R": 2000,
            "Z": 2001,
        }

        rules = [
            SerialRule(
                rule_type="decode",
                brand="TRANE",
                priority=None,
                style_name="Manual: Legacy letter-year + WW (1983-2001)",
                serial_regex=r"^[WXY SBCDEFGHJKLMNPRZ](0[1-9]|[1-4]\d|5[0-3])[1-7][A-Z0-9]{5,6}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 1, "end": 1}, "mapping": year_letter_map}, "week": {"positions": {"start": 2, "end": 3}}},
                example_serials=["P311K00FF"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
            SerialRule(
                rule_type="decode",
                brand="TRANE",
                priority=None,
                style_name="Manual: Legacy YY in positions 2-3 (1980-2001)",
                serial_regex=r"^[A-Z](5[4-9]|[6-9]\d)[A-Z0-9?]{6,7}$",
                equipment_types=[],
                date_fields={"year": {"positions": {"start": 2, "end": 3}}},
                example_serials=["S89C19905"],
                decade_ambiguity={"is_ambiguous": True},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            ),
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        # Letter-year + WW
        a = decode_serial("TRANE", "P311K00FF", accepted, min_plausible_year=0)
        self.assertEqual(a.manufacture_year, 1999)
        self.assertEqual(a.manufacture_week, 31)

        # YY fallback (digits 2-3)
        b = decode_serial("TRANE", "S89C19905", accepted, min_plausible_year=0)
        self.assertEqual(b.manufacture_year, 1989)

    def test_aerco_g_yy_4digits(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="AERCO",
                priority=None,
                style_name="Manual: G-YY-#### (2000+)",
                serial_regex=r"^G-?\d{2}-?\d{4}$",
                equipment_types=[],
                date_fields={
                    "year": {
                        "pattern": {"regex": r"^G-?(\d{2})", "group": 1},
                        "transform": {"type": "year_add_base", "base": 2000, "min_year": 2000, "max_year": 2035},
                    }
                },
                example_serials=["G-10-0919", "G-10-0924", "G-12-0785"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        a = decode_serial("AERCO", "G-10-0919", accepted, min_plausible_year=0)
        self.assertEqual(a.manufacture_year, 2010)

        b = decode_serial("AERCO", "G-10-0924", accepted, min_plausible_year=0)
        self.assertEqual(b.manufacture_year, 2010)

        c = decode_serial("AERCO", "G-12-0785", accepted, min_plausible_year=0)
        self.assertEqual(c.manufacture_year, 2012)

    def test_benchmark_g_yy_4digits(self) -> None:
        from msl.decoder.io import SerialRule

        rules = [
            SerialRule(
                rule_type="decode",
                brand="BENCHMARK",
                priority=None,
                style_name="Manual: G-YY-#### (2000+)",
                serial_regex=r"^G-?\d{2}-?\d{4}$",
                equipment_types=[],
                date_fields={
                    "year": {
                        "pattern": {"regex": r"^G-?(\d{2})", "group": 1},
                        "transform": {"type": "year_add_base", "base": 2000, "min_year": 2000, "max_year": 2035},
                    }
                },
                example_serials=["G-14-1293", "G-12-0683", "G-22-2696"],
                decade_ambiguity={"is_ambiguous": False},
                guidance_action="",
                guidance_text="",
                evidence_excerpt="",
                source_url="manual_additions",
                retrieved_on="",
                image_urls=[],
            )
        ]
        accepted, issues = validate_serial_rules(rules)
        self.assertEqual(len(issues), 0)

        a = decode_serial("BENCHMARK", "G-14-1293", accepted, min_plausible_year=0)
        self.assertEqual(a.manufacture_year, 2014)

        b = decode_serial("BENCHMARK", "G-12-0683", accepted, min_plausible_year=0)
        self.assertEqual(b.manufacture_year, 2012)

        c = decode_serial("BENCHMARK", "G-22-2696", accepted, min_plausible_year=0)
        self.assertEqual(c.manufacture_year, 2022)


if __name__ == "__main__":
    unittest.main()
