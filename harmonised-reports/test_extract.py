"""Unit tests for harmonised extraction and corrected VLOP workbook values.

Google Hotels/Workspace ship an `NN_<section>_Ads.csv` sibling for sections 6-8;
the extractor folds it into the base section, tagging a trailing `Surface` column
(`Core` for the base, `Ads` for the ads rows). These tests pin that behaviour and
its edges (no-sibling passthrough, header drop, section restriction, orphan, the
filename regex) so a future refactor can't silently regress the fold.

Run: `python -m pytest harmonised-reports/test_extract.py`
"""
import extract
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import convert  # noqa: E402


def _hdr(cols):
    return ["Applicability"] + cols


def _make(n_data_rows, surface_label="All", width=5):
    """A tiny (header + data) section: leading Applicability col + filler cells."""
    rows = [_hdr([f"c{i}" for i in range(width - 1)])]
    for r in range(n_data_rows):
        rows.append([surface_label] + [str(r)] * (width - 1))
    return rows


def test_ads_re_matches_only_ads_siblings():
    assert extract._ADS_RE.match("6_own_initiative_TC_Ads.csv")
    assert extract._ADS_RE.match("8_automated_means_ADS.CSV")  # case-insensitive
    # A base section file is NOT an ads sibling.
    assert not extract._ADS_RE.match("6_own_initiative_TC.csv")
    # Must be anchored at the leading section number.
    assert not extract._ADS_RE.match("ads_6_foo.csv")


def test_stamp_surface_appends_trailing_column():
    rows = _make(2)
    stamped = extract._stamp_surface(rows, "Core")
    assert stamped[0][-1] == "Surface"            # header gains the column
    assert all(r[-1] == "Core" for r in stamped[1:])  # every data row tagged
    assert extract._stamp_surface([], "Core") == []   # empty is a no-op


def test_fold_merges_base_as_core_and_ads_as_ads():
    base = ("6_own_initiative_TC.csv", _make(3))
    ads = ("6_own_initiative_TC_Ads.csv", _make(2))
    out = extract._merge_ads_surfaces([base, ads])
    assert len(out) == 1                       # ads folded into the base section
    name, rows = out[0]
    assert name == "6_own_initiative_TC.csv"   # keeps the base (numbered) name
    assert rows[0][-1] == "Surface"
    data = rows[1:]
    surfaces = [r[-1] for r in data]
    assert surfaces.count("Core") == 3 and surfaces.count("Ads") == 2
    # The ads file's header row was dropped, not folded in as data.
    assert all(r[0] in ("All",) for r in data)  # no stray "Applicability" header


def test_report_without_ads_sibling_is_unchanged():
    pairs = [("6_own_initiative_TC.csv", _make(2)), ("4_notices.csv", _make(2))]
    out = extract._merge_ads_surfaces(pairs)
    assert out == pairs                                  # returned as-is
    assert all(row != "Surface" for _, rows in out for row in rows[0])  # no Surface col


def test_ads_outside_surface_sections_is_ignored(capsys):
    # A t4 ads file has no surface dimension downstream — it must NOT be folded
    # (that would double-count into a surface-less table); it is skipped + warned.
    base = ("4_notices.csv", _make(2))
    rogue = ("4_notices_Ads.csv", _make(2))
    out = extract._merge_ads_surfaces([base, rogue])
    assert out == [base]                                 # rogue dropped, base kept
    assert "ignoring ads-surface file" in capsys.readouterr().out


def test_multiple_ads_for_same_section_warns(capsys):
    # Two ads files mapping to the same section: the dict keeps the last, so warn
    # rather than silently drop the first.
    base = ("6_own_initiative_TC.csv", _make(2))
    ads1 = ("6_own_initiative_TC_Ads.csv", _make(1))
    ads2 = ("6_other_Ads.csv", _make(1))  # also parses to section 6
    out = extract._merge_ads_surfaces([base, ads1, ads2])
    assert "multiple ads-surface files for section 6" in capsys.readouterr().out
    assert len(out) == 1  # still folded into the one base section


def test_orphan_ads_without_base_kept_as_ads_section():
    # An _Ads (section 7) with no base sibling is kept under its own name, tagged
    # Ads, rather than silently dropped.
    orphan = ("7_appeals_and_recidivism_Ads.csv", _make(2))
    out = extract._merge_ads_surfaces([orphan])
    assert len(out) == 1
    name, rows = out[0]
    assert name == "7_appeals_and_recidivism_Ads.csv"
    assert rows[0][-1] == "Surface"
    assert all(r[-1] == "Ads" for r in rows[1:])


def test_shein_rich_text_corrections_use_replacement_values():
    rows = convert.read_xlsx_sheet(
        Path(__file__).resolve().parents[1] / "shein.xlsx",
        "7_appeals_and_recidivism",
    )
    disputes = [
        row for row in rows
        if convert.get(row, "Indicator") ==
        "Number of disputes submitted to out-of-court dispute settlement bodies"
    ]
    values = {
        convert.get(row, "Scope"): convert.parse_num(convert.get(row, "Value"))
        for row in disputes
    }
    assert values["Total number"] == 45
    assert values["Percentage of outcomes implemented"] == 100
