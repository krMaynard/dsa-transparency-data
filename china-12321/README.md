# China 12321 — Internet bad & spam-information report handling

The **12321 网络不良与垃圾信息举报受理中心** (12321 Internet Bad & Spam
Information Reporting Center), run by the **Internet Society of China** (中国互联网协会)
under the **Ministry of Industry and Information Technology (MIIT)**, was China's
national hotline for reporting telecom / internet **nuisance and spam**. From
**2016-09 to 2019-02** it published a monthly bulletin, **"12321 举报中心工作情况
月报 / 12321举报受理情况播报"**, tallying how many public reports it received that
month per category. The series was **discontinued after Feb 2019** (12321 kept
operating, its work folded into MIIT's nuisance-call / spam systems).

This is the **telecom-spam complement** to the CAC/12377 content-reporting series
(`china-ciirc`): a different agency (MIIT / Internet Society of China, not CAC),
a different remit (spam & nuisance, not "illegal & harmful information"), and a
distinct — if now frozen — multi-year monthly series. **26 bulletins**
(2017-10's listing link 404s at source, so it's absent).

## Categories (reports **received** that month)

| `category` | 中文 | Coverage |
|------------|------|----------|
| `app` | 手机应用软件 / APP 举报 | all 26 |
| `sms` | 短信举报 (monthly total) | all 26 |
| `sms_spam` | 垃圾类短信 | most |
| `sms_illegal` | 涉嫌违法类短信 | most |
| `harassment_calls` | 骚扰电话举报 | all 26 |
| `bad_websites` | 不良网站举报 | all 26 |
| `fraud_comms` | 涉嫌通讯信息诈骗 | 2016-09..12 |
| `spam_email` | 垃圾邮件举报 | 2016-09..2017-04 |

The three SMS rows **overlap** — `sms` is the monthly total and `sms_spam`
(垃圾类) + `sms_illegal` (涉嫌违法类) are its two disjoint parts — so summing
them double-counts. The taxonomy narrows over the series: the 2016 bulletins also
break out comms fraud and spam email, dropped by 2017.

## What's built

`build_12321.py --download` scrapes the report listing (`/report`) and each
monthly PDF from `www.12321.cn`, archiving the raw PDFs under `raw/`; `build()`
then parses the archived PDFs **offline** (deterministic, PyMuPDF).

Output `china-12321.json`, tidy-long
(`publisher, period, section, category, metric, unit, value`).

```bash
python build_12321.py --download   # re-scrape www.12321.cn → raw/, then build
python build_12321.py              # rebuild offline from raw/
```

### Parsing notes

- **Units drift.** The 2016 bulletins state raw integer counts (`件次`); from
  2017 the figures are rounded to **万** (ten-thousands). All are stored as
  absolute counts, with `unit` marking the 万-rounded values `approx_count`
  (exact 2016 counts are `count`).
- **Whitespace & running headers.** The PDF text layer space-separates glyphs and
  injects a running page header (`2017年第2期总第101期5/11`) mid-sentence; the
  parser squashes all whitespace and strips that header before matching, so an
  anchor like `涉嫌违法类的` reaches its figure.
- **Combined-month bulletins** (2017-05_06, 2017-08_09, 2018-10_11) carry a
  coverage-window period `YYYY-MM..YYYY-MM`.
- **SMS reconciliation.** The build cross-checks that `sms_spam + sms_illegal`
  reconciles to the `sms` total within 万-rounding slack and **raises** on a real
  mismatch — the main fidelity guard for the per-category extraction.

Source: `www.12321.cn/report` (报告资料 / reports). One bulletin per month,
2016-09 … 2019-02.
