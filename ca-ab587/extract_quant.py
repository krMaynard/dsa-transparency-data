#!/usr/bin/env python3
"""Extract a conservative, category-normalized subset of AB 587 statistics.

The filings do not share a template.  This intentionally covers only tables
whose category and metric can be retained without guessing.  Missing rows are
therefore "not extracted", never zero.  See QUANTITATIVE.md for coverage.
"""
import csv
import os
import re

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "pdfs")
DST = os.path.join(HERE, "ca_ab587_normalized.csv")

CATEGORIES = {
    "a": "hate_speech_or_racism",
    "b": "extremism_or_radicalization",
    "c": "disinformation_or_misinformation",
    "d": "harassment",
    "e": "foreign_political_interference",
}

FILINGS = [
    ("discord", "2023 Q3", "discord-2023-q3-c05561.pdf", "generic"),
    ("discord", "2023 Q4", "discord-2023-q4-9ba386.pdf", "generic"),
    ("linkedin", "2023 Q4", "linkedin-2023-q4-52a75b.pdf", "generic"),
    ("linkedin", "2024 H1", "linkedin-2024-h1-4401df.pdf", "generic"),
    ("reddit", "2023 Q3", "reddit-2023-q3-f4ce7d.pdf", "reddit"),
    ("reddit", "2023 Q4", "reddit-2023-q4-3211c9.pdf", "reddit"),
    ("roblox", "2023 Q3", "roblox-2023-q3-f7002b.pdf", "roblox"),
    ("roblox", "2023 Q4", "roblox-2023-q4-365a2a.pdf", "roblox"),
    ("snap", "2023 Q4", "snap-2023-q4-cc142e.pdf", "snap"),
    ("snap", "2024 H1", "snap-2024-h1-583a9b.pdf", "snap"),
    ("tiktok", "2023 Q3", "tiktok-2023-q3-a253e7.pdf", "generic"),
    ("tiktok", "2023 Q4", "tiktok-2023-q4-09410d.pdf", "generic"),
]

OUT_COLS = ["company", "period", "ab587_category", "original_label",
            "geographic_scope", "content_format", "grain", "metric",
            "submetric", "value", "unit", "page", "source_file"]


def clean(value):
    return re.sub(r"\s+", " ", (value or "").replace("\u200b", " ")).strip()


def number(value):
    text = clean(value).replace(",", "")
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*%", text)
    if match:
        return match.group(1), "percent"
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", text):
        return text, "count"
    return None, None


def category(company, label, table=""):
    text = clean(label).lower()
    title = clean(table).lower()
    if company == "reddit":
        text = title
    exact = {
        "hateful and derogatory": "a", "hate speech": "a",
        "discrimination, slurs, and hate speech": "a",
        "extremism or radicalization": "b",
        "dangerous organizations or individuals": "b",
        "terrorism and violent extremism": "b",
        "terrorism & violent extremism": "b", "terrorism &": "b",
        "false and misleading": "c", "false information": "c",
        "disinformation or misinformation": "c",
        "threats, bullying, and harassment": "d", "harassment": "d",
        "harassment & bullying": "d",
        "foreign political interference": "e",
    }
    text = re.sub(r"^\([a-e]\)\s*", "", text)
    if text in exact:
        return CATEGORIES[exact[text]]
    if company == "reddit":
        if "hateful content" in text:
            return CATEGORIES["a"]
        if "terroris" in text:
            return CATEGORIES["b"]
        if "harassment" in text:
            return CATEGORIES["d"]
    return ""


def record(company, period, filename, page, label, table, column, value, unit,
           scope="reported", grain="category_total", content_format=""):
    cat = category(company, label, table)
    if not cat:
        return None
    metric = clean(table)
    # A PDF extraction artifact occasionally shifts a category into Discord's
    # metric header. Preserve the value, but do not present that as a metric.
    if company == "discord" and category(company, metric):
        metric = "metric_not_recovered"
    return {
        "company": company, "period": period, "ab587_category": cat,
        "original_label": clean(label), "geographic_scope": scope,
        "content_format": content_format, "grain": grain,
        "metric": metric, "submetric": clean(column), "value": value,
        "unit": unit, "page": page, "source_file": filename,
    }


def extract_generic(company, period, filename):
    out = []
    with pymupdf.open(os.path.join(PDF_DIR, filename)) as doc:
        for page in doc:
            for table in page.find_tables().tables:
                cells = table.extract()
                if len(cells) < 2:
                    continue
                header = [clean(cell) for cell in cells[0]]
                table_label = header[0] if header else ""
                for row in cells[1:]:
                    row = [clean(cell) for cell in row]
                    if not row or not category(company, row[0], table_label):
                        continue
                    for index, raw in enumerate(row[1:], 1):
                        value, unit = number(raw)
                        if value is None:
                            continue
                        item = record(company, period, filename, page.number + 1,
                                      row[0], table_label,
                                      header[index] if index < len(header) else "",
                                      value, unit)
                        if item:
                            out.append(item)
    return out


def extract_reddit(company, period, filename):
    out = []
    with pymupdf.open(os.path.join(PDF_DIR, filename)) as doc:
        for page in doc:
            for table in page.find_tables().tables:
                cells = table.extract()
                if len(cells) < 2:
                    continue
                header = [clean(cell) for cell in cells[0]]
                title = header[0] if header else ""
                cat = category(company, "", title)
                if not cat:
                    continue
                for row in cells[1:]:
                    row = [clean(cell) for cell in row]
                    if not row:
                        continue
                    label = row[0]
                    grain = "category_total" if label.lower() == "total" else "breakdown"
                    for index, raw in enumerate(row[1:], 1):
                        value, unit = number(raw)
                        if value is None:
                            continue
                        item = record(company, period, filename, page.number + 1,
                                      label, title,
                                      header[index] if index < len(header) else "",
                                      value, unit, grain=grain,
                                      content_format="" if grain == "category_total" else label)
                        if item:
                            item["original_label"] = (
                                "Hateful content" if cat == CATEGORIES["a"] else
                                "Terrorism" if cat == CATEGORIES["b"] else "Harassment")
                            out.append(item)
    return out


def extract_roblox(company, period, filename):
    dim_headers = {"VIOLATION CATEGORY", "IDENTIFICATION SOURCE",
                   "TYPE OF ACTION", "MEDIA TYPE", "CATEGORY"}
    value_headers = {"TOTAL FLAGGED", "TOTAL ACTIONS", "CONTENT REMOVED",
                     "ACTIONS WITH USER CONSEQUENCES", "APPROVED APPEALS",
                     "TOTAL APPEALS"}
    rows, out = [], []
    with pymupdf.open(os.path.join(PDF_DIR, filename)) as doc:
        rows = [(page.number + 1, clean(line)) for page in doc
                for line in page.get_text().splitlines() if clean(line)]
    index = 0
    while index < len(rows):
        page, text = rows[index]
        if text not in dim_headers:
            index += 1
            continue
        cursor = index + 1
        while cursor < len(rows) and rows[cursor][1] in dim_headers:
            cursor += 1
        metrics = []
        while cursor < len(rows):
            candidate = rows[cursor][1]
            if candidate in value_headers:
                metrics.append(candidate.title())
                cursor += 1
            elif (cursor + 1 < len(rows) and
                  candidate + " " + rows[cursor + 1][1] in value_headers):
                metrics.append((candidate + " " + rows[cursor + 1][1]).title())
                cursor += 2
            else:
                break
        if not metrics:
            index += 1
            continue
        while cursor < len(rows):
            row_page, label = rows[cursor]
            if number(label)[0] is not None or cursor + len(metrics) >= len(rows):
                break
            values = [number(rows[cursor + offset][1])
                      for offset in range(1, len(metrics) + 1)]
            if any(value is None for value, _unit in values):
                break
            for metric, (value, unit) in zip(metrics, values):
                item = record(company, period, filename, row_page, label,
                              metric, "", value, unit)
                if item:
                    out.append(item)
            cursor += len(metrics) + 1
        index = max(cursor, index + 1)
    return out


def _anchors(page):
    anchors = []
    for block in page.get_text("blocks"):
        text = clean(block[4]).lower()
        if "global figures" in text:
            anchors.append((block[1], "global"))
        if "u.s. figures" in text or "us figures" in text:
            anchors.append((block[1], "united_states"))
    return sorted(anchors)


def extract_snap(company, period, filename):
    out, scope, headers, current_category = [], "reported", [], ""
    with pymupdf.open(os.path.join(PDF_DIR, filename)) as doc:
        for page in doc:
            anchors = _anchors(page)
            for table in sorted(page.find_tables().tables, key=lambda item: item.bbox[1]):
                for y, anchor_scope in anchors:
                    if y < table.bbox[1]:
                        scope = anchor_scope
                cells = table.extract()
                for raw_row in cells:
                    row = [clean(cell) for cell in raw_row]
                    if len(row) != 15:
                        continue
                    if row[0].lower().startswith("category of violation"):
                        headers = row
                        current_category = ""
                        continue
                    if not headers:
                        continue
                    if row[0]:
                        # A new, out-of-scope category ends any prior mapped
                        # category; otherwise its blank continuation row would
                        # be misattributed to the preceding category.
                        current_category = row[0] if category(company, row[0]) else ""
                    if not current_category or row[1].lower() not in {
                            "human report", "automatic detection"}:
                        continue
                    for index, raw in enumerate(row[2:], 2):
                        value, unit = number(raw)
                        if value is None:
                            continue
                        item = record(company, period, filename, page.number + 1,
                                      current_category, row[1], headers[index],
                                      value, unit, scope=scope)
                        if item:
                            out.append(item)
    return out


def main():
    extractors = {"generic": extract_generic, "reddit": extract_reddit,
                  "roblox": extract_roblox, "snap": extract_snap}
    rows = []
    for company, period, filename, kind in FILINGS:
        rows.extend(extractors[kind](company, period, filename))
    rows.sort(key=lambda row: tuple(str(row[col]) for col in OUT_COLS))
    with open(DST, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUT_COLS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} normalized AB 587 cells from {len(FILINGS)} filings")


if __name__ == "__main__":
    main()
