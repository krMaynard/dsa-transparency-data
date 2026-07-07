#!/usr/bin/env python3
"""Build the Japan 情プラ法 (Information Distribution Platform Act) dataset.

Japan's amended Provider Liability Limitation Act ("情報流通プラットフォーム対処法",
in force 1 Apr 2025) requires MIC-designated large providers to publish
implementation-status statistics once a year under Art. 28. Two providers now do:

- **LY Corporation** (LINE / Yahoo! Japan) — its **Media Transparency Report**
  (メディア透明性レポート, FY2024) gives, per service, a quarterly table
  (『四半期ごとの投稿件数・投稿削除件数及び投稿削除割合』) with the FY2024 quarters
  and the annual total: posts, posts removed, and the removal rate. Those five
  tables (archived in ``raw/lycorp-transparency-2024.pdf``) are parsed here.
- **Google (YouTube)** — its **Japan Information Platform Act Transparency
  Report** (26 Jul 2025 – 31 Mar 2026, published May 2026, archived in
  ``raw/youtube-japan-2025h2-{en,ja}.pdf``) gives Japan-specific figures on legal
  removals (requests / items / removals by reason), policy removals (by reason
  and by first-detection source), user flags, channel suspensions, appeals, plus
  headline platform figures. Those tables are transcribed below and each
  breakdown is cross-checked against its stated Total, so a mistranscription
  can't slip through.

Output: ``japan-info-platform.json`` — ``{source, coverage, columns, rows}`` with
columns ``service, period, section, category, metric, unit, value``. LY Corp's
rows sit in section ``posts_activity`` (category ``All``); YouTube's carry a
``section`` per report table and a ``category`` per reason (``Total`` for the
section aggregate). Metrics/units are never comparable across sections, and each
section keeps its ``Total`` beside the breakdown — pin section + category before
aggregating.
"""
from __future__ import annotations

import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
LY_PDF = os.path.join(HERE, "raw", "lycorp-transparency-2024.pdf")
OUT = os.path.join(HERE, "japan-info-platform.json")

COLUMNS = ["service", "period", "section", "category", "metric", "unit", "value"]

SOURCE = "https://www.lycorp.co.jp/ja/company/transparencyreport2024.pdf"
LY_COVERAGE = "2024-04..2025-03"  # FY2024 (24年度)

# ── LY Corporation ──────────────────────────────────────────────────────────
# service section (page index, in-report label) -> canonical English name.
SERVICES = [
    (9, "知恵袋", "Yahoo! Chiebukuro"),
    (18, "ファイナンス掲示板", "Yahoo! Finance boards"),
    (26, "オープンチャット", "LINE OpenChat"),
    (36, "VOOM", "LINE VOOM"),
    (45, "ヤフコメ", "Yahoo! News comments"),
]

# FY2024 quarter labels -> coverage window.
QUARTERS = {
    "4-6": "2024-04..2024-06",
    "7-9": "2024-07..2024-09",
    "10-12": "2024-10..2024-12",
    "1-3": "2025-01..2025-03",
}

# Annual-total posts per service, taken from the report's prose summary — used to
# cross-check the parsed 年度合計 row so a table misparse can't slip through.
EXPECT_ANNUAL_POSTS = {
    "Yahoo! Chiebukuro": 66_199_309,
    "Yahoo! Finance boards": 29_415_652,
    "LINE OpenChat": 5_514_828_787,
    "LINE VOOM": 403_331_897,
    "Yahoo! News comments": 113_995_832,
}


def _num(s: str) -> int:
    return int(s.replace(",", ""))


# A cell is "<total> 件（<monthly avg> 件）", optionally with a footnote digit run
# stuck to 件 (e.g. "66,199,309 件10（…"). Parentheses are full-width （） on most
# services but half-width () on OpenChat. We keep the total, drop the avg.
_CELL = r"([\d,]+)\s*件\d*\s*[（(]\s*[\d,]+\s*件\d*\s*[）)]"
_ROW = re.compile(
    r"(4-6|7-9|10-12|1-3|年度合計)\s*(?:月期)?\s*（月平均）\s*"
    + _CELL + r"\s*" + _CELL + r"\s*([\d.]+)\s*[％%]"
)


def parse_service(doc, page_idx: int, label: str, name: str):
    # Some tables split across a page boundary (OpenChat), so read this page and
    # the next, then scope to this service's quarterly table.
    txt = re.sub(r"\s+", " ", doc[page_idx].get_text() + " "
                 + (doc[page_idx + 1].get_text() if page_idx + 1 < doc.page_count else ""))
    m0 = re.search(re.escape(f"[{label}]") + r"\s*四半期ごとの", txt)
    if not m0:
        raise ValueError(f"{name}: quarterly table not found on page {page_idx + 1}")
    chunk = txt[m0.start():m0.start() + 1600]
    rows = []
    for m in _ROW.finditer(chunk):
        qlabel, posts, removed, rate = m.group(1), _num(m.group(2)), _num(m.group(3)), float(m.group(4))
        period = LY_COVERAGE if qlabel == "年度合計" else QUARTERS[qlabel]
        rows.append((name, period, "posts_activity", "All", "posts", "count", posts))
        rows.append((name, period, "posts_activity", "All", "posts_removed", "count", removed))
        rows.append((name, period, "posts_activity", "All", "removal_rate", "percent", rate))
    # sanity: the annual total must be present and match the prose figure
    annual = [r for r in rows if r[1] == LY_COVERAGE and r[4] == "posts"]
    if not annual:
        raise ValueError(f"{name}: no 年度合計 row parsed")
    if name in EXPECT_ANNUAL_POSTS and annual[0][6] != EXPECT_ANNUAL_POSTS[name]:
        raise ValueError(f"{name}: parsed annual posts {annual[0][6]:,} != "
                         f"expected {EXPECT_ANNUAL_POSTS[name]:,}")
    return rows


# ── Google / YouTube ────────────────────────────────────────────────────────
# YouTube's Japan Information Platform Act Transparency Report, 26 Jul 2025 –
# 31 Mar 2026 (raw/youtube-japan-2025h2-{en,ja}.pdf). Transcribed from the report
# tables; each breakdown is validated against its stated Total below.
YT_SERVICE = "YouTube"
YT_SOURCE = "https://transparencyreport.google.com/"
YT_PERIOD = "2025-07-26..2026-03-31"

# section, metric, unit, {category: value}, stated Total.
# A 'Total' category row is emitted per section alongside the breakdown.
YT_BREAKDOWNS = [
    # Legal enforcement (Art. 28 (i)(ii)/(iv)).
    ("legal_requests", "requests", "count", {
        "Circumvention": 4, "Counterfeit": 110, "Defamation": 1002,
        "Other Legal": 987, "Privacy": 21, "Trademark": 326}, 2450),
    ("legal_extended_review_notifications", "notifications", "count", {
        "Defamation": 4, "Other Legal": 8}, 12),
    ("legal_items", "items", "count", {
        "Not removed": 3796, "Removed": 289}, 4085),
    ("legal_removals", "items_removed", "count", {
        "Circumvention": 0, "Counterfeit": 3, "Defamation": 155,
        "Other Legal": 13, "Privacy": 1, "Trademark": 117}, 289),
    # Policy enforcement (Art. 28 (iv)).
    ("user_flags", "flags", "count", {
        "Child Abuse": 133852, "Harmful or Dangerous Acts": 683070,
        "Hateful or Abusive": 1470212, "Promotes Terrorism": 236531,
        "Sexual": 672522, "Spam or Misleading": 2861555,
        "Suicide, self-harm, or eating disorders": 116385,
        "Violent or Repulsive": 1519165}, 7693292),
    ("policy_removals", "videos_removed", "count", {
        "Child Safety": 43211, "Harassment and Cyberbullying": 70695,
        "Harmful or Dangerous": 8598, "Hateful or Abusive": 5667,
        "Misinformation": 133, "Nudity or Sexual": 24743, "Other": 215,
        "Promotion of Violence and Violent Extremism": 1774,
        "Spam, Deceptive Practices and Scams": 1007,
        "Violent or Graphic": 6347}, 162390),
    ("policy_detection_source", "videos_removed", "count", {
        "Automated detection": 155131, "Government": 0,
        "Organisation": 1652, "User": 5607}, 162390),
    ("suspensions", "accounts_terminated", "count", {
        "Child Safety": 2026, "Harassment and Cyberbullying": 375,
        "Harmful or Dangerous": 1369, "Hateful or Abusive": 835,
        "Misinformation": 1727, "Multiple policy violations": 110,
        "Nudity or Sexual": 6000, "Other": 26,
        "Promotion of Violence and Violent Extremism": 177,
        "Spam, Deceptive Practices, and Scams": 139405,
        "Violent or Graphic": 53}, 152103),
]

# section, category, metric, unit, value — headline / single-value figures.
YT_SCALARS = [
    ("platform", "All", "monthly_active_users", "count", 106_400_000),
    ("platform", "All", "qualified_reviewers", "count", 293),
    ("platform", "All", "expert_investigation_cases", "count", 6),
    ("platform", "All", "notifications_withheld", "count", 0),
    ("appeals", "All", "appeals", "count", 20_759),
    ("appeals", "All", "reinstatements", "count", 3_090),
]


def build_youtube():
    rows = []
    for section, metric, unit, cats, total in YT_BREAKDOWNS:
        s = sum(cats.values())
        if s != total:
            raise ValueError(f"YouTube {section}: categories sum to {s:,} "
                             f"!= stated Total {total:,}")
        rows.append((YT_SERVICE, YT_PERIOD, section, "Total", metric, unit, total))
        for cat, val in cats.items():
            rows.append((YT_SERVICE, YT_PERIOD, section, cat, metric, unit, val))
    for section, cat, metric, unit, val in YT_SCALARS:
        rows.append((YT_SERVICE, YT_PERIOD, section, cat, metric, unit, val))
    return rows


# ── Meta (Facebook / Instagram / Threads) ────────────────────────────────────
# Meta's inaugural Japan IDPA ("情プラ法") Annual Transparency Report, reporting
# period 30 Jul 2025 – 31 Mar 2026 (published 31 May 2026, archived in
# raw/meta-japan-idpa-2026.pdf). Facebook, Instagram and Threads are each
# designated under the Act, so every quantitative table is per-service. Figures
# are transcribed from the report tables below.
#
# Two source caveats, faithfully preserved rather than "fixed":
#  * The per-policy breakdowns are the report's own "most prevalent categories"
#    — an ILLUSTRATIVE SUBSET, not an exhaustive partition — so the listed
#    categories do not sum to the stated Total (which covers "other violations"
#    too). We record each listed category plus the stated Total (category
#    ``Total``); never assume Total == sum(categories).
#  * A few request tables (2.2, 3.1.x) don't reconcile exactly either, per the
#    report's own logging-issue footnotes (Right-to-honor/Feelings-of-honor and
#    Trademark/Copyright reporting reasons are combined; <30 requests went
#    uncategorised). Transcribed as printed.
# Two tables are OMITTED: 5.3.4 (regulator requests) has a non-per-service
# "Requests" column and Meta itself flags (fn.10) it cannot disaggregate
# content- vs account-actions, with internally inconsistent tiny counts; 5.3.5
# (court orders) is all-zero ("None received"). Both are noted in the README.
META_SERVICES = ["Facebook", "Instagram", "Threads"]
META_SOURCE = "https://transparency.meta.com/"
META_PERIOD = "2025-07-30..2026-03-31"

# (section, metric, unit, {category: (facebook, instagram, threads)}). A
# ``Total`` category holds the report's stated section total (a superset of the
# listed categories, not their sum). Units are ``count`` except the Table 1.4
# platform figures, which Meta reports rounded ("633.5 million") → approx_count.
META_TABLES = [
    # Table 1.4 — cumulative content + monthly active accounts (rounded).
    ("platform", "content_pieces", "approx_count", {
        "All": (633_500_000, 4_200_000_000, 550_300_000)}),
    ("platform", "monthly_active_users", "approx_count", {
        "All": (22_100_000, 82_000_000, 20_600_000)}),
    # Table 2.2 — requests received through the IDPA channel, by reporting reason.
    ("requests_received", "requests", "count", {
        "Right to honor & Feelings of honor": (2458, 3070, 509),
        "Invasion of privacy": (1126, 1274, 323),
        "Peace in personal life": (814, 897, 190),
        "Portrait rights": (251, 1869, 407),
        "Right to one's name": (652, 321, 15),
        "Right of publicity": (217, 43, 8),
        "Trademarks, Copyrights, and neighboring rights": (1_338_662, 150_211, 2607),
        "Business interests": (358, 222, 53),
        "Total": (1_344_304, 156_048, 3705)}),
    # Table 3.1.1 — requests actioned within 7 days.
    ("decisions_within_7d", "requests_actioned", "count", {
        "Right to honor & Feelings of honor": (354, 638, 63),
        "Invasion of privacy": (203, 684, 97),
        "Peace in personal life": (84, 272, 20),
        "Portrait rights": (109, 932, 203),
        "Right to one's name": (72, 118, 1),
        "Right of publicity": (21, 7, 0),
        "Trademarks, Copyrights, and neighboring rights": (647_624, 35_455, 850),
        "Business interests": (33, 65, 6),
        "Total": (648_391, 37_243, 1037)}),
    # Table 3.1.2 — requests actioned after 7 days (specialist-consultation cases).
    ("decisions_after_7d", "requests_actioned", "count", {
        "Right to honor & Feelings of honor": (67, 436, 11),
        "Invasion of privacy": (17, 41, 6),
        "Peace in personal life": (4, 12, 2),
        "Portrait rights": (25, 153, 25),
        "Right to one's name": (9, 5, 0),
        "Right of publicity": (1, 0, 0),
        "Trademarks, Copyrights, and neighboring rights": (677, 563, 2),
        "Business interests": (2, 8, 2),
        "Total": (778, 1065, 23)}),
    # Table 3.1.3 — requests that resulted in no action.
    ("requests_no_action", "requests_no_action", "count", {
        "Right to honor & Feelings of honor": (2037, 1996, 435),
        "Invasion of privacy": (906, 549, 220),
        "Peace in personal life": (726, 613, 168),
        "Portrait rights": (117, 784, 179),
        "Right to one's name": (571, 198, 14),
        "Right of publicity": (195, 36, 8),
        "Trademarks, Copyrights, and neighboring rights": (690_361, 114_193, 1755),
        "Business interests": (323, 149, 45),
        "Total": (695_135, 117_740, 2645)}),
    # Table 4.2 — enforcement actions on content, by violation type.
    ("content_actions", "actions", "count", {
        "Local Law Violations": (11_890, 3741, 342),
        "Adult Nudity and Sexual Activity": (73_810, 249_245, 48_486),
        "Adult Sexual Exploitation": (8703, 10_440, 1540),
        "Adult Sexual Solicitation and Sexually Explicit Language": (37_021, 95_171, 115_445),
        "Bullying and Harassment": (8904, 19_404, 18_161),
        "Child Sexual Exploitation, Abuse, and Nudity": (55_620, 51_907, 7966),
        "Dangerous Organizations and Individuals": (10_376, 7931, 1623),
        "Fraud and Deception": (112_817, 25_229, 170_905),
        "Hateful Conduct": (4156, 3189, 16_205),
        "Human Exploitation": (36_456, 10_656, 1529),
        "Intellectual Property": (39_321, 60_103, 2350),
        "Restricted Goods and Services": (2285, 357, 642),
        "Spam": (420_954, 151_519, 1_059_618),
        "Suicide and Self-Injury": (11_949, 66_468, 3071),
        "Violence and Incitement": (3566, 5116, 8274),
        "Violent and Graphic Content": (584, 295, 69),
        "Total": (891_693, 798_330, 1_461_097)}),
    # Table 4.3 — enforcement actions on accounts, by violation type.
    ("account_actions", "actions", "count", {
        "Local Law Violations": (9, 336, 184),
        "Account Integrity and Authentic Identity": (10_883_834, 3_827_805, 331_704),
        "Adult Sexual Solicitation and Sexually Explicit Language": (3271, 13_898, 270),
        "Child Sexual Exploitation, Abuse, and Nudity": (12_775, 109_667, 177),
        "Fraud and Deception": (49_801, 72_014, 896),
        "Spam": (152_018, 513_073, 1047),
        "Total": (11_199_182, 4_690_678, 334_361)}),
    # Table 5.3.1 — content actioned after a user report, by reporting reason.
    ("user_report_actions", "content_actioned", "count", {
        "Adult Nudity and Sexual Activity": (11_117, 49_182, 3448),
        "Adult Sexual Exploitation": (8464, 38_001, 3643),
        "Adult Sexual Solicitation and Sexually Explicit Language": (3592, 41_927, 5294),
        "Bullying and Harassment": (4081, 14_756, 11_418),
        "Child Sexual Exploitation, Abuse, and Nudity": (9294, 37_311, 2770),
        "Dangerous Organizations and Individuals": (3875, 4050, 1810),
        "Fraud and Deception": (10_647, 118_104, 29_949),
        "Hateful Conduct": (5297, 10_455, 21_087),
        "Human Exploitation": (727, 525, 109),
        "Restricted Goods and Services": (242, 290, 275),
        "Spam": (16, 5928, 0),
        "Suicide and Self-Injury": (1353, 6930, 1193),
        "Violence and Incitement": (3734, 5815, 7985),
        "Violent and Graphic Content": (3325, 4996, 4037),
        "Total": (67_022, 377_437, 94_030)}),
    # Table 5.3.2 — content reported by users (reported vs not-actioned).
    ("user_report_reviewed", "content_reported", "count", {
        "Adult Nudity and Sexual Activity": (76_796, 405_752, 44_826),
        "Adult Sexual Exploitation": (62_287, 152_350, 27_771),
        "Adult Sexual Solicitation and Sexually Explicit Language": (25_656, 160_534, 46_081),
        "Bullying and Harassment": (143_117, 638_164, 266_241),
        "Child Sexual Exploitation, Abuse, and Nudity": (45_647, 154_722, 20_432),
        "Dangerous Organizations and Individuals": (76_273, 59_374, 26_925),
        "Fraud and Deception": (105_305, 698_059, 221_633),
        "Hateful Conduct": (139_949, 447_263, 348_039),
        "Human Exploitation": (8158, 7247, 1712),
        "Restricted Goods and Services": (8005, 17_150, 4278),
        "Spam": (2760, 263_700, 8371),
        "Suicide and Self-Injury": (12_948, 70_168, 11_264),
        "Violence and Incitement": (79_900, 117_710, 82_855),
        "Violent and Graphic Content": (66_212, 118_097, 33_455),
        "Total": (870_017, 3_623_945, 1_174_925)}),
    ("user_report_reviewed", "content_not_actioned", "count", {
        "Adult Nudity and Sexual Activity": (65_679, 356_570, 41_378),
        "Adult Sexual Exploitation": (53_823, 114_349, 24_128),
        "Adult Sexual Solicitation and Sexually Explicit Language": (22_064, 118_607, 40_787),
        "Bullying and Harassment": (139_036, 623_408, 254_823),
        "Child Sexual Exploitation, Abuse, and Nudity": (36_353, 117_411, 17_662),
        "Dangerous Organizations and Individuals": (72_398, 55_324, 25_115),
        "Fraud and Deception": (94_658, 579_955, 191_684),
        "Hateful Conduct": (134_652, 436_808, 326_952),
        "Human Exploitation": (7431, 6722, 1603),
        "Restricted Goods and Services": (7763, 16_860, 4003),
        "Spam": (2744, 257_772, 0),
        "Suicide and Self-Injury": (11_595, 63_238, 10_071),
        "Violence and Incitement": (76_166, 111_895, 74_870),
        "Violent and Graphic Content": (62_887, 113_101, 29_418),
        "Total": (802_359, 3_235_479, 1_067_189)}),
    # Table 5.3.3 — content proactively detected + actioned, by violation type.
    ("proactive_actions", "content_actioned", "count", {
        "Adult Nudity and Sexual Activity": (71_739, 233_348, 46_999),
        "Adult Sexual Exploitation": (7920, 8920, 1156),
        "Adult Sexual Solicitation and Sexually Explicit Language": (33_891, 70_307, 108_948),
        "Bullying and Harassment": (2182, 2656, 1408),
        "Child Sexual Exploitation, Abuse, and Nudity": (54_436, 44_764, 6459),
        "Dangerous Organizations and Individuals": (9926, 7604, 1196),
        "Fraud and Deception": (109_037, 19_689, 162_147),
        "Hateful Conduct": (615, 574, 1410),
        "Human Exploitation": (35_699, 9761, 1323),
        "Intellectual Property": (16_231, 13_131, 139),
        "Restricted Goods and Services": (1942, 257, 430),
        "Spam": (419_218, 148_859, 1_052_737),
        "Suicide and Self-Injury": (11_382, 63_345, 2538),
        "Violence and Incitement": (1508, 2725, 902),
        "Violent and Graphic Content": (517, 170, 33),
        "Total": (822_163, 660_882, 1_390_718)}),
]

# Tables 5.4.2.1–5.4.2.3 — account suspensions by reason × how the violation was
# detected. {service: {reason: (proactive, report_based, regulator, court)}}.
META_SUSP_METRICS = ["suspensions_proactive", "suspensions_report_based",
                     "suspensions_regulator", "suspensions_court_ordered"]
META_SUSPENSIONS = {
    "Facebook": {
        "Account Integrity and Authentic Identity": (10_837_873, 45_961, 2, 0),
        "Adult Sexual Solicitation and Sexually Explicit Language": (1782, 1489, 0, 0),
        "Child Sexual Exploitation, Abuse, and Nudity": (9931, 2844, 0, 0),
        "Fraud and Deception": (39_528, 10_273, 4, 0),
        "Spam": (122_504, 29_514, 0, 0),
        "Total": (11_091_862, 107_312, 6, 0)},
    "Instagram": {
        "Account Integrity and Authentic Identity": (3_634_421, 193_384, 24, 0),
        "Adult Sexual Solicitation and Sexually Explicit Language": (5921, 7977, 0, 0),
        "Child Sexual Exploitation, Abuse, and Nudity": (78_275, 31_392, 0, 0),
        "Fraud and Deception": (31_365, 40_649, 117, 0),
        "Spam": (449_543, 63_530, 1, 0),
        "Total": (4_330_847, 359_494, 173, 0)},
    "Threads": {
        "Account Integrity and Authentic Identity": (318_353, 13_351, 9, 0),
        "Adult Sexual Solicitation and Sexually Explicit Language": (139, 131, 0, 0),
        "Child Sexual Exploitation, Abuse, and Nudity": (145, 32, 1, 0),
        "Fraud and Deception": (632, 258, 4, 0),
        "Spam": (886, 161, 0, 0),
        "Total": (320_197, 13_974, 15, 0)},
}

# Table 7.1 — appeals, by appeal type. {metric: (facebook, instagram, threads)}.
META_APPEALS = {
    "content_appeals": (54_682, 70_297, 44_489),
    "content_appeals_ai": (25_856, 56_200, 43_279),
    "content_appeal_reversals": (18_485, 25_345, 14_479),
    "content_appeal_reversals_ai": (10_189, 18_380, 13_827),
    "account_appeals": (517_981, 1_379_466, 223_881),
    "account_appeals_ai": (499_504, 1_298_216, 219_402),
    "account_appeal_reversals": (127_713, 548_463, 139_175),
    "account_appeal_reversals_ai": (121_411, 515_660, 138_118),
}


def build_meta():
    rows = []
    # zip(..., strict=True) raises on any length mismatch, so a mistyped triple
    # (e.g. a value dropped) fails loudly rather than silently truncating.
    for section, metric, unit, catrows in META_TABLES:
        for cat, triple in catrows.items():
            for svc, val in zip(META_SERVICES, triple, strict=True):
                rows.append((svc, META_PERIOD, section, cat, metric, unit, val))
    for svc, catrows in META_SUSPENSIONS.items():
        for cat, vals in catrows.items():
            for metric, val in zip(META_SUSP_METRICS, vals, strict=True):
                rows.append((svc, META_PERIOD, "account_suspensions", cat, metric, "count", val))
    for metric, triple in META_APPEALS.items():
        for svc, val in zip(META_SERVICES, triple, strict=True):
            rows.append((svc, META_PERIOD, "appeals", "All", metric, "count", val))
    # Structural sanity only. We deliberately do NOT assert Total >= each
    # category or Total == sum(categories): Meta's own figures don't reconcile
    # (e.g. Table 3.1.2 lists Threads "Portrait rights"=25 above its stated
    # Threads Total of 23, and Table 2.2's breakdown sums above its Total),
    # per the report's documented logging-issue footnotes. Every value must be a
    # non-negative int and every per-service triple well-formed.
    for svc, period, section, cat, metric, unit, val in rows:
        if not isinstance(val, int) or val < 0:
            raise ValueError(f"Meta {section}/{svc}/{metric}/{cat}: bad value {val!r}")
    return rows


def main():
    rows = []
    with fitz.open(LY_PDF) as doc:
        for page_idx, label, name in SERVICES:
            rows.extend(parse_service(doc, page_idx, label, name))
    rows.extend(build_youtube())
    rows.extend(build_meta())
    data = {
        # Three providers on different report windows — keep a per-provider
        # source map and a coverage envelope spanning them all, rather than any
        # single provider's window.
        "sources": {"LY Corporation": SOURCE, "YouTube": YT_SOURCE,
                    "Meta": META_SOURCE},
        "coverage": "2024-04..2026-03",
        "columns": COLUMNS,
        "rows": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(rows)} rows")
    from collections import Counter
    print("rows per service:", dict(Counter(r[0] for r in rows)))
    print("YouTube sections:", sorted({r[2] for r in rows if r[0] == YT_SERVICE}))
    print("Meta sections:", sorted({r[2] for r in rows if r[0] in META_SERVICES}))


if __name__ == "__main__":
    main()
