#!/usr/bin/env python3
"""Extract & localize the narrative text of LY Corporation's Media Transparency Report.

`build_japan.py` pulls the *numbers* (the per-service quarterly posts / removals /
removal-rate tables) out of LY Corporation's FY2024 Media Transparency Report
(メディア透明性レポート, `raw/lycorp-transparency-2024.pdf`). This script pulls the
**prose** — how each service (Yahoo! Chiebukuro, Yahoo! Finance boards, LINE
OpenChat, LINE VOOM, Yahoo! News comments) describes its purpose, its rules, how
it responds to violations, how it detects them (AI + human review), and the
cross-service ("共通編") sections on countering misinformation, new initiatives,
the monitoring framework and healthy-discourse work — so it can be full-text
searched alongside the other report narratives (NY ToS, CA AB 587, DSA Table-11).

The source report is **Japanese-only**, so — unlike the other narrative corpora —
each section is stored **bilingually**: an English translation followed by the
Japanese original prose. Both go into one searchable `text` field.

The translations are curated here (like `build_japan.py`'s expected-figure
constants) rather than machine-generated at build time, so the build stays
deterministic and offline. To guard against the vendored PDF drifting out from
under the translation, every section carries a `ja_check` — a distinctive phrase
that must still appear in that page's extracted text; the build raises if it
doesn't (the same fail-loud contract as `build_japan.py`'s EXPECT_ANNUAL_POSTS).

Tidy-long output — one row per narrative section (shape shared with the other
narrative corpora via the API's `_build_narratives`):

  company, platform, period, page, heading, text

- **company** — always ``LY Corporation``.
- **platform** — the service the section is about (blank for the intro / the
  cross-service 共通編 sections).
- **period** — the report's fiscal year, ``2024-04..2025-03``.
- **page** — the printed page number where the section begins (which equals the
  0-based PDF index for this report; a reference anchor — the PDF isn't mirrored
  in-repo, so there's no deep link).
- **heading** — an English section heading.
- **text** — the English translation, then a blank line, then the Japanese
  original prose.

Deterministic: builds purely from ``raw/lycorp-transparency-2024.pdf`` + the
curated SECTIONS below; no wall-clock, no network. Pure stdlib + PyMuPDF.
"""
from __future__ import annotations

import argparse
import json
import os
import re

import fitz  # PyMuPDF

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "raw", "lycorp-transparency-2024.pdf")
OUT_JSON = os.path.join(HERE, "japan-narratives.json")

SOURCE = "https://www.lycorp.co.jp/ja/company/transparency-report/"
PERIOD = "2024-04..2025-03"
COMPANY = "LY Corporation"
COLUMNS = ["company", "platform", "period", "page", "heading", "text"]

_WS = re.compile(r"\s+")


# Curated bilingual narrative sections. Each: the PDF page the section starts on,
# the service it concerns (blank = the intro / a cross-service 共通編 section), an
# English heading, an English translation (`en`), the Japanese original prose
# (`ja`), and `ja_check` — a distinctive phrase that must still appear in that
# page's extracted text (a fail-loud guard against the PDF drifting).
SECTIONS: list[dict] = [
    {
        "page": 3, "platform": "", "heading": "About the Media Transparency Report",
        "ja_check": "メディア透明性レポートとは",
        "en": (
            "LINE Yahoo operates several user-posting platform services as places "
            "where users can freely express themselves, communicate and debate on "
            "everything from everyday concerns to major social issues. Each platform "
            "sets rules and guidelines suited to its purpose, prohibits inappropriate "
            "posts such as defamation of individuals, and takes firm measures — "
            "removing posts, suspending posting — against violations. At the same "
            "time, because posting platforms are critical infrastructure for the "
            "circulation of information in modern society, it is also important to "
            "preserve an environment in which users can transmit information freely "
            "and without censorship. Content moderation must therefore be carried "
            "out 'without excess or deficiency', striking a careful balance between "
            "removing inappropriate content and protecting freedom of expression. "
            "Following a December 2020 recommendation by its in-house expert panel "
            "on the proper design of platform services (chaired by Prof. Tatsuhiko "
            "Yamamoto of Keio University Law School), LINE Yahoo has published this "
            "Media Transparency Report every fiscal year since FY2020, disclosing "
            "each service's removal record and internal moderation arrangements so "
            "that feedback from users and outside experts can inform continuous "
            "improvement. In April 2025 the Information Distribution Platform Act "
            "(情プラ法) — the amendment to the Provider Liability Limitation Act — took "
            "effect, imposing new duties on large platform operators to speed up "
            "removal handling and increase operational transparency. On 30 April "
            "2025 Yahoo! Chiebukuro, Yahoo! Finance boards, LINE OpenChat and LINE "
            "VOOM were designated as subject to these rules. This FY2024 report "
            "(1 April 2024 – 31 March 2025) covers those four services plus Yahoo! "
            "News comments (collectively, the 'covered services')."
        ),
        "ja": (
            "LINE ヤフーでは、ユーザーが身近な問題から重要な社会問題まで幅広く表現や"
            "議論を行える「場」として、複数の投稿型プラットフォームサービスを提供して"
            "います。各サービスでは目的や特性に応じた利用のルールやガイドラインを定め、"
            "誹謗中傷などの不適切な投稿を禁止し、違反行為に対して投稿の削除や投稿停止"
            "措置などの厳正な措置を行っています。一方で、投稿型プラットフォームは情報"
            "流通の基盤として重要な役割を果たしており、ユーザーが検閲を受けることなく"
            "自由に情報発信できる環境の確保も重要です。コンテンツモデレーションは、"
            "不適切な投稿の排除と表現の自由とのバランスを確保しつつ「過不足なく」"
            "実施することが求められます。LINE ヤフーは、社内の有識者会議（座長：山本"
            "龍彦 慶應義塾大学大学院教授）の提言（20 年12 月）を踏まえ、20 年度以降"
            "毎年度、各サービスの投稿削除の実績や社内体制を「メディア透明性レポート」"
            "として公開しています。25 年4 月には情報流通プラットフォーム対処法（情プラ"
            "法）が施行され、大規模なプラットフォーム事業者に削除対応の迅速化と運用状況"
            "の透明化を求める新たな規律が課されました。25 年4 月30 日にYahoo!知恵袋、"
            "Yahoo!ファイナンス掲示板、LINE オープンチャット、LINE VOOM の4 サービスが"
            "対象として指定されています。本レポートは24 年度を対象に、これら4 サービスに"
            "Yahoo!ニュース コメントを加えた「対象サービス」について作成しています。"
        ),
    },
    {
        "page": 5, "platform": "Yahoo! Chiebukuro",
        "heading": "Yahoo! Chiebukuro — purpose and rules of use",
        "ja_check": "知恵袋の提供目的",
        "en": (
            "Yahoo! Chiebukuro is a knowledge-sharing service where users resolve "
            "everyday questions by asking others and answering their questions, in "
            "the spirit of building a 'world of mutual help'. Chiebukuro treats a "
            "safe environment for all users as its highest priority: while it allows "
            "free posting of questions and answers, it asks every user to follow the "
            "rules of use and to refrain from defamation and other violations. For "
            "example, posting personal information, illegal content, malicious links, "
            "offensive material, or content that seriously harms or attacks someone "
            "is prohibited."
        ),
        "ja": (
            "Yahoo!知恵袋は、日常のあらゆる疑問を他のユーザーに質問したり回答したり"
            "することで解決していく「知恵」の共有サービスで、「助け合いの世界を作りたい」"
            "という考えのもと提供しています。知恵袋では、すべてのユーザーが安心・安全に"
            "利用できることを最も重要と考えており、質問や回答の自由な投稿を可能としつつ、"
            "利用のルールの遵守と、誹謗中傷その他の違反行為を控えることを呼び掛けています。"
            "例えば、個人情報の書き込み、法令違反、悪質なリンク、不快な内容、誰かを著しく"
            "傷つけ攻撃する内容などの投稿は禁止されています。"
        ),
    },
    {
        "page": 6, "platform": "Yahoo! Chiebukuro",
        "heading": "Yahoo! Chiebukuro — responding to violations",
        "ja_check": "違反への対応について",
        "en": (
            "When a post is judged to violate the rules of use it is removed. Posts "
            "judged highly likely to breach the rules may be hidden as inappropriate "
            "on the question-detail page; a hidden post can still be viewed by "
            "pressing a 'show' button. From FY2023, where a user is judged to be "
            "trolling through repeated posting, a mechanism suppresses that user's "
            "consecutive posts. A user who makes a certain number of violating posts "
            "within a set period is barred from Chiebukuro for one week (temporary "
            "posting suspension); an account repeatedly suspended may face a full "
            "posting ban. Clearly malicious or fraudulent activity can trigger a "
            "posting suspension and suspension of the Yahoo! JAPAN ID without prior "
            "notice. As a 'specified telecommunications service provider' under the "
            "情プラ法, LINE Yahoo also receives out-of-court and court-based removal "
            "and sender-information-disclosure requests from people whose rights were "
            "infringed, and removal requests from public authorities."
        ),
        "ja": (
            "投稿が利用のルールに違反したと判断された場合は投稿を削除します。禁止事項に"
            "該当する蓋然性が高い投稿は、不適切な投稿として質問詳細ページで非表示となる"
            "ことがあり、ユーザーが「表示する」ボタンを押すと内容を確認できます。23 年度"
            "からは、連続投稿による荒らし行為等を行っていると判断されたユーザーの連続投稿"
            "を抑制する仕組みを導入しています。一定期間内に一定数の違反投稿を行ったユーザー"
            "は1 週間知恵袋を利用できなくなり（一時投稿停止）、繰り返し違反し複数回停止"
            "された場合は完全投稿停止となることがあります。明らかに悪意のある行為には、"
            "予告なく投稿停止やYahoo! JAPAN ID の利用停止を行う場合があります。LINE ヤフー"
            "は情プラ法上の「特定電気通信役務提供者」として、権利を侵害された方からの削除"
            "請求・発信者情報開示請求や、公的機関からの削除要請を受け付けています。"
        ),
    },
    {
        "page": 11, "platform": "Yahoo! Chiebukuro",
        "heading": "Yahoo! Chiebukuro — detection, non-display measures and appeals",
        "ja_check": "自ら探知して行った",
        "en": (
            "Removals arise both from user violation reports and from LINE Yahoo's "
            "own detection; posting suspensions are made entirely through the "
            "company's own detection. Chiebukuro detects violations by combining AI "
            "models with human review by a specialist team: an AI model flags posts "
            "with a high probability of violation for human review, and staff also "
            "actively patrol high-priority themes — but Chiebukuro does **not** use AI "
            "for automatic removal. In FY2024, 62,871 posts were removed following "
            "user reports and 381,856 through the company's own detection. Separately, "
            "a 'low-quality-post model' scores posts and automatically **hides** "
            "(not removes) those above a threshold; a hidden post reappears if the "
            "user presses 'show'. For appeals, users who question a removal or "
            "suspension can enquire through a help form; in FY2024, of 65 removal "
            "enquiries 16 led to re-display, and of 170 suspension enquiries 4 led to "
            "release — none of these involved AI-based actions."
        ),
        "ja": (
            "投稿の削除は、ユーザーからの違反報告を受けて行う場合と自ら探知して行う場合が"
            "あり、投稿停止措置については全件、LINE ヤフー自らの探知により行っています。"
            "知恵袋では、AI と専門チームによる「人の目」を組み合わせて違反投稿を探知して"
            "おり、AI モデルで違反の蓋然性が高い投稿を人の目による審査フローに移すほか、"
            "対応の必要性が高いテーマについて専門チームが積極的にパトロールしています。"
            "なお、知恵袋ではAI モデルを用いた自動削除は行っていません。24 年度は、ユーザー"
            "からの違反報告を受けた削除が62,871 件、自ら探知して行った削除が381,856 件"
            "でした。また、「低品質投稿判定モデル」がスコアを付与し、閾値を超えた投稿を"
            "自動的に非表示（削除ではない）とし、ユーザーが「表示する」を押すと表示されます。"
            "異議申立てについては、削除・投稿停止に疑問等があるユーザーからヘルプ・問い合わせ"
            "フォームで受け付けており、24 年度は削除に対する問い合わせ65 件のうち16 件が"
            "再表示に、投稿停止に対する問い合わせ170 件のうち4 件が解除に至りました"
            "（いずれもAI 等による措置は含まれません）。"
        ),
    },
    {
        "page": 15, "platform": "Yahoo! Finance boards",
        "heading": "Yahoo! Finance boards — purpose and prohibited conduct",
        "ja_check": "ファイナンス掲示板の提供目的",
        "en": (
            "Yahoo! Finance boards let users exchange information about stocks, "
            "foreign exchange, FX and similar topics. Per-issue boards run one thread "
            "per listed stock (users cannot create threads), while 'stock chat' and "
            "'FX / forex chat' categories allow user-created threads. Prohibited "
            "conduct is defined on a dedicated page. Because posts concern financial "
            "instruments, the service urges users not to rely solely on board "
            "information for investment decisions but to verify facts through "
            "trustworthy institutions; it also flags conduct banned under the "
            "Financial Instruments and Exchange Act (spreading rumours, market "
            "manipulation) and links to the Securities and Exchange Surveillance "
            "Commission's tip page. Posts judged to breach the rules are removed, and "
            "in certain cases the Yahoo! JAPAN ID is suspended from posting."
        ),
        "ja": (
            "Yahoo!ファイナンス掲示板は、株式・為替・FX などの話題についてユーザーが"
            "相互に情報交換することを目的に提供しています。銘柄別掲示板は1 銘柄1 スレッド"
            "で構成され、ユーザーはスレッドを作成できませんが、「株式雑談」「FX、為替雑談」"
            "カテゴリではスレッドを作成できます。禁止行為は専用ページで周知しています。"
            "金融商品に関する投稿が行われることから、掲示板の情報のみを信頼して投資判断"
            "するのではなく信頼できる機関で事実確認を行うことを推奨し、金融商品取引法で"
            "禁止された「風説の流布」「相場操縦」への注意や、証券取引等監視委員会への情報"
            "提供ページへのリンクを掲載しています。禁止行為に該当すると判断された投稿は"
            "削除し、一定の場合にはYahoo! JAPAN ID に対し投稿停止措置を行います。"
        ),
    },
    {
        "page": 21, "platform": "Yahoo! Finance boards",
        "heading": "Yahoo! Finance boards — detection, automated removal and appeals",
        "ja_check": "自らが探知して行った削除",
        "en": (
            "Finance boards provide a per-post violation-report form and also patrol "
            "actively: staff visually check comment sections for posts that were not "
            "reported. Removals therefore come from user reports and from the "
            "company's own detection; in FY2024 the split of the 492,236 removals was "
            "262,887 from user reports and 229,349 from own detection. From FY2024, "
            "Finance boards use generative AI to automatically remove images judged "
            "obscene or violent, and machine-learning scoring to auto-remove posts "
            "that likely aim to advertise or drive users to external sites/SNS; of "
            "the own-detection removals, 91,187 were automatic (chiefly duplicate/"
            "keyword removals). For appeals, in March 2025 there were 4 removal "
            "enquiries (0 re-displayed); FY2024 posting-suspension enquiries rose to "
            "273 (from 64), with none released — an enquiry rate of 6.2%."
        ),
        "ja": (
            "ファイナンス掲示板では投稿ごとに違反報告フォームを設けるとともに、違反報告が"
            "ない投稿についても専門チームがコメント欄を積極的に巡回して目視確認しています。"
            "投稿の削除はユーザーからの違反報告を受けて行う場合と自ら探知して行う場合が"
            "あり、24 年度の削除492,236 件の内訳はユーザー報告262,887 件、自ら探知229,349 件"
            "でした。24 年度からは生成AI を用いてわいせつ・暴力的と判断された画像を自動削除"
            "する仕組みや、外部サイト・SNS への誘導など広告目的の可能性を機械学習で点数化し"
            "一定基準を超えた投稿を自動削除する取組を開始しており、自ら探知した削除のうち"
            "AI 等による自動削除は91,187 件（重複・キーワード削除が中心）でした。異議申立て"
            "については、25 年3 月の削除に対する問い合わせは4 件（再表示0 件）、24 年度の"
            "投稿停止に対する問い合わせは273 件（前年64 件）で解除は0 件、問い合わせを受けた"
            "割合は6.2％でした。"
        ),
    },
    {
        "page": 23, "platform": "LINE OpenChat",
        "heading": "LINE OpenChat — purpose and prohibited conduct",
        "ja_check": "オープンチャットの提供目的",
        "en": (
            "LINE OpenChat lets users connect over shared interests and chat with "
            "people who are not their LINE 'friends'. Rooms can be joined via a shared "
            "URL or QR code without adding friends, hold up to 5,000 members, and "
            "support real-time voice as well as text via a live-talk feature. Posts "
            "are governed by the OpenChat Prohibited-Conduct Rules, which the relevant "
            "departments review carefully — balancing prevention of rights "
            "infringement against users' freedom of expression — in light of shifting "
            "social conditions, SNS trends, national cultures and user needs around "
            "misinformation and defamation. A Safety Guideline explains those rules in "
            "plain terms."
        ),
        "ja": (
            "LINE オープンチャットは、ユーザーが共通点でつながることができるサービスで、"
            "LINE の「友だち」でないユーザーともトークでき、URL やQR コードの共有で招待"
            "が簡単に行えます。グループトークには最大5,000 人が参加でき、ライブトーク機能"
            "では音声でもリアルタイムにコミュニケーションが可能です。投稿にはオープン"
            "チャット禁止規定が適用され、偽・誤情報や誹謗中傷等を巡り日々変化する社会情勢"
            "やSNS トレンド、各国の文化、ユーザーのニーズを踏まえつつ、権利侵害の防止と"
            "表現の自由への配慮のバランスが取れた基準となるよう、関係各部門が連携して"
            "慎重に検討しています。安心・安全ガイドラインでは禁止規定をわかりやすく解説"
            "しています。"
        ),
    },
    {
        "page": 24, "platform": "LINE OpenChat",
        "heading": "LINE OpenChat — safety content, display restrictions and responding to violations",
        "ja_check": "禁止行為違反への対応について",
        "en": (
            "Posts judged to violate the Prohibited-Conduct Rules are removed, and the "
            "personal LINE account of a repeat violator may be barred from posting in "
            "OpenChat. Through the LINE Safety Center, LINE Yahoo publishes posting "
            "guidelines and information for guardians and educators to keep minors "
            "safe; in FY2024 it also solicited and showcased stickers reminding users "
            "of room etiquette. Newly created rooms and rooms whose name or details "
            "were just updated are restricted for a time from appearing on OpenChat's "
            "main screen or in search results, supporting safe community operation and "
            "an environment users can join with confidence."
        ),
        "ja": (
            "オープンチャット禁止規定への違反と判定された投稿は削除し、違反を繰り返す"
            "ユーザーのLINE 個人アカウントに対してオープンチャットでの投稿停止措置を行う"
            "ことがあります。LINE Safety Center（LINE の安心安全ガイド）を通じて、各"
            "サービスの投稿ガイドラインや、保護者・教育関係者に向けた未成年者の被害防止"
            "情報を掲載しており、24 年度にはトークルームのルールやマナーに関する注意喚起"
            "を目的としたスタンプを募集し紹介しました。また、新規作成されたトークルームや"
            "名称等が更新されたトークルームについて、メイン画面や検索結果に一定時間表示"
            "されないよう制限を設け、安全で適切なコミュニティ運営とユーザーが安心して参加"
            "できる環境づくりを行っています。"
        ),
    },
    {
        "page": 29, "platform": "LINE OpenChat",
        "heading": "LINE OpenChat — detection and appeals",
        "ja_check": "違反報告に関するデータ",
        "en": (
            "OpenChat places a 'report' button on posts, room main screens and user "
            "profiles to collect violation reports widely, and also detects proactively "
            "through automated means and patrols. In FY2024 the vast majority of the "
            "6,980,935 removals — 6,683,162 (95.7%) — came from the company's own "
            "detection versus 297,773 from user reports, with automated 'keyword "
            "removal' and 'solicitation of encounters (dating)' the largest categories. "
            "For appeals, there were 279 removal enquiries (2 re-displayed) and 3,186 "
            "posting-suspension enquiries (2 released)."
        ),
        "ja": (
            "オープンチャットでは投稿・トークルームのメイン画面・プロフィール画面に「通報"
            "ボタン」を設置してユーザーからの違反報告を幅広く受け付けるとともに、機械的な"
            "探知手段や巡回パトロールによる積極的な探知に努めています。24 年度の削除"
            "6,980,935 件のうち、自ら探知して行った削除が6,683,162 件（95.7％）、ユーザー"
            "からの違反報告を受けて行った削除が297,773 件で、「キーワード削除」や「出会いを"
            "求める行為」による自動削除が多くを占めました。異議申立てについては、削除に"
            "対する問い合わせ279 件（再表示2 件）、投稿停止に対する問い合わせ3,186 件"
            "（解除2 件）でした。"
        ),
    },
    {
        "page": 33, "platform": "LINE VOOM",
        "heading": "LINE VOOM — purpose and prohibited conduct",
        "ja_check": "VOOM の提供目的",
        "en": (
            "LINE VOOM is a video platform for short videos and the like. Users can "
            "post and view short videos, photos and text, and can 'like', comment on "
            "or share posts. Videos shared by LINE Official Accounts or personal "
            "accounts are viewable by non-friends, and follow relationships let "
            "accounts and videos reach a wide, unspecified audience. Posts are governed "
            "by the LINE VOOM Community Rules, which the relevant departments review "
            "carefully to keep a balanced standard — preventing rights infringement "
            "while respecting freedom of expression — amid changing social conditions "
            "and SNS trends. Posts judged to violate the rules are removed, and repeat "
            "violators face measures such as suspension of a personal account's "
            "posting, suspension of an Official Account, or forced withdrawal."
        ),
        "ja": (
            "LINE VOOM は、ショート動画などが楽しめる動画プラットフォームです。ユーザーは"
            "ショート動画・写真・テキストの投稿や閲覧ができ、投稿に「いいね」やコメントを"
            "付けたりシェアしたりできます。公式アカウントや個人アカウントがシェアした動画は"
            "友だち以外も閲覧でき、フォロー関係を通じてアカウントや動画の認知拡大にも活用"
            "できます。投稿には「LINE VOOM コミュニティー利用規則」が適用され、偽・誤情報"
            "や誹謗中傷等を巡り日々変化する社会情勢やSNS トレンド、ユーザーのニーズを踏まえ"
            "つつ、権利侵害の防止と表現の自由への配慮のバランスが取れた基準となるよう関係"
            "各部門が連携して慎重に検討しています。利用規則の違反と判定された投稿は削除し、"
            "違反を繰り返すユーザーには個人アカウントの投稿停止措置や公式アカウントの停止・"
            "強制退会の措置を講じています。"
        ),
    },
    {
        "page": 37, "platform": "LINE VOOM",
        "heading": "LINE VOOM — responding to violations, detection and appeals",
        "ja_check": "誤情報の拡散",
        "en": (
            "In FY2024, of VOOM's 3,055,002 removals, 1,594,995 (52.2%) were by AI; "
            "spam was especially common among AI removals, while 'offensive "
            "expression / nuisance conduct' and 'sexual expression' led the "
            "non-AI removals. The 'offensive expression / nuisance conduct' category "
            "included 1,223 removals for 'spreading misinformation'. VOOM places a "
            "'report' button on posts, stories and comments/replies for user reports, "
            "and also detects proactively through automated means and patrols. For "
            "appeals, users can object through an enquiry form; measures include "
            "suspending a personal account's posting or suspending/forcing withdrawal "
            "of an Official Account."
        ),
        "ja": (
            "24 年度のVOOM の削除3,055,002 件のうち、AI 等による削除が1,594,995 件"
            "（52.2％）で、AI 等による削除では特にスパム行為が多く、AI 等による削除を除くと"
            "「不快表現/迷惑行為」「性的な表現」が多い傾向にありました。「不快表現/迷惑行為」"
            "には「誤情報の拡散」による削除件数（1,223 件）が含まれています。VOOM では投稿・"
            "ストーリー投稿・コメント・リプライに「通報ボタン」を設置してユーザーからの違反"
            "報告を受け付けるとともに、機械的な探知手段や巡回パトロールによる積極的な探知に"
            "努めています。異議申立てはお問い合わせフォームで受け付けており、違反を繰り返す"
            "ユーザーには個人アカウントの投稿停止や公式アカウントの停止・強制退会の措置を"
            "講じています。"
        ),
    },
    {
        "page": 42, "platform": "Yahoo! News comments",
        "heading": "Yahoo! News comments — purpose and comment policy",
        "ja_check": "ヤフコメの提供目的",
        "en": (
            "Yahoo! News comments (ヤフコメ) is a place where diverse opinions and "
            "impressions about news and current events gather. Yahoo! News believes "
            "that encountering others' views in the comments helps users organise "
            "their own thinking and understand news more deeply and from multiple "
            "angles, and — using the interactivity of the internet — it lets users "
            "become senders of information alongside the media. A safe environment is "
            "paramount, so Yahoo! News defines a Comment Policy that clearly sets out "
            "prohibited comments and conduct. To keep the service safe, the policy "
            "also prohibits offensive comments even where they do not necessarily "
            "amount to a rights infringement or legal violation."
        ),
        "ja": (
            "Yahoo!ニュース コメント（ヤフコメ）は、ニュースや世の中の出来事に関連する"
            "多様な意見や考え、感想が集まる場所です。Yahoo!ニュースでは、コメント欄で他の"
            "ユーザーの意見に触れることが、自分の考えを整理したりニュースを多角的に理解"
            "したりするきっかけになると考え、インターネットの双方向性を生かし、ユーザーが"
            "発信主体となる場を提供しています。安心して利用できる環境が何よりも重要である"
            "ため、Yahoo!ニュースはコメントポリシーを定め、投稿が禁止されるコメントや行為を"
            "わかりやすく示しています。なお、コメントポリシーでは、必ずしも権利侵害や法令"
            "違反に至らない場合であっても、不快な内容を含むコメント等を禁止の対象として"
            "います。"
        ),
    },
    {
        "page": 43, "platform": "Yahoo! News comments",
        "heading": "Yahoo! News comments — user controls and posting-time warnings",
        "ja_check": "投稿時注意メッセージの掲出",
        "en": (
            "When the Comment Policy is breached, the comment is removed and, "
            "depending on severity and repetition, the user may be suspended from "
            "commenting. A suspended user's registered mobile-phone number is matched "
            "so that comments from Yahoo! JAPAN IDs obtained with the same number are "
            "restricted; a mobile-phone number is mandatory to comment. Users can hide "
            "the comment section entirely when reading an article, or hide comments "
            "from specific users, with such settings visible only to the user who set "
            "them. For users who repeatedly post comments judged to be violations, a "
            "message is shown urging them to reconsider what they are about to post; "
            "the message content is updated from time to time."
        ),
        "ja": (
            "コメントポリシーへの違反があった場合は対象投稿を削除するほか、違反の重大性や"
            "回数に応じてコメントの投稿停止措置を行います。投稿停止措置を受けたユーザーに"
            "ついては、Yahoo! JAPAN ID 登録情報である携帯電話番号を照合し、同一の番号で"
            "取得されたID からのコメント投稿を制限しています（コメント投稿には携帯電話番号"
            "の設定が必須です）。記事閲覧時にコメント欄を表示させたくない場合はユーザー自身"
            "が非表示に設定でき、特定ユーザーのコメントに限って非表示にすることも可能で、"
            "非表示設定は設定した本人のみが確認できます。また、違反と判定されたコメントを"
            "複数回投稿しているユーザーに対しては、投稿内容の再考を促す注意メッセージを"
            "掲出しており、内容は随時アップデートしています。"
        ),
    },
    {
        "page": 49, "platform": "Yahoo! News comments",
        "heading": "Yahoo! News comments — detection, comment-section hiding and appeals",
        "ja_check": "機微なニュアンス",
        "en": (
            "Yahoo! News comments detects violations with AI plus human review; posts "
            "with subtle nuances that are hard for AI to judge are decided by the "
            "specialist team's human eyes. Of the removals, roughly 58% were by AI and "
            "40% by human review, led by automatic removal of posts judged "
            "inappropriate, then human removal of 'duplicate posts' and 'excessive "
            "criticism / defamation'. For comment sections with enough posts, a feature "
            "can automatically hide an entire comment section based on criteria such as "
            "the AI-judged number of violating posts; in FY2024 this was applied 87 "
            "times, tending to target the comment sections of negative articles (e.g. "
            "incidents or accidents) that attract pile-ons against those involved. For "
            "appeals, FY2024 saw 120 removal enquiries (0 re-displayed) and 1,249 "
            "posting-suspension enquiries (3 released), the latter down over 40% "
            "year-on-year."
        ),
        "ja": (
            "ヤフコメでは、AI と専門チームによる「人の目」を組み合わせて違反投稿を探知して"
            "おり、AI 等による判定が困難な機微なニュアンスを含んだ投稿については専門チームが"
            "人の目により違反かどうかを判断しています。削除のうち約58％がAI 等による削除、"
            "約40％が人の目による削除で、AI 等による不適切投稿の自動削除が多く、次いで人の目"
            "による「重複投稿」「過度な批判や誹謗中傷等」が多くなっています。一定以上の投稿数"
            "があるコメント欄を対象に、AI が判定した違反投稿数などの基準に従いコメント欄全体"
            "を自動的に非表示とする機能を導入しており、24 年度の非表示措置は87 件で、加害者"
            "バッシングが集まりやすい事件・事故などのネガティブな記事のコメント欄が対象と"
            "なりやすい傾向にありました。異議申立てについては、24 年度の削除に対する問い合わせ"
            "は120 件（再表示0 件）、投稿停止に対する問い合わせは1,249 件（解除3 件）で、"
            "前年度比で4 割強減少しました。"
        ),
    },
    {
        "page": 53, "platform": "",
        "heading": "Common — countering false and misleading information",
        "ja_check": "偽・誤情報対策",
        "en": (
            "Beyond prohibiting and removing posts that are clearly false or "
            "misleading under each service's rules, LINE Yahoo works on delivering and "
            "supporting fact information and on awareness-raising and literacy. On the "
            "delivery side, Yahoo! News actively features debunking/alerting articles "
            "in Yahoo! News Topics and adds expert commentary; Yahoo! Search surfaces "
            "correct information from public bodies for queries such as COVID-19 and "
            "medical information; and LINE NEWS points users to trustworthy sources "
            "(central ministries, NHK) and to fact-checking organisations. LINE Yahoo "
            "also supports the FactCheck Initiative Japan (FIJ) and the Japan Fact-check "
            "Center (JFC) financially and through content links. On the education side, "
            "Yahoo! News produces awareness content with experts and media; OpenChat "
            "publishes alerts on disaster-time misinformation and fraud; and the LINE "
            "Mirai Foundation develops the free 'GIGA Workbook' information-morals "
            "teaching material (adopted as official material in 18 prefectures and 82 "
            "municipalities as of March 2025) and 'information disaster-prevention' "
            "education for using information calmly in emergencies."
        ),
        "ja": (
            "LINE ヤフーは、規約・ガイドライン等で偽・誤情報であることが明らかな投稿を禁止"
            "し削除等の対応を行うことに加え、ファクト情報の伝達・支援と、啓蒙啓発・リテラ"
            "シー向上にも取り組んでいます。伝達・支援としては、Yahoo!ニュースで打ち消し・"
            "注意喚起に有効な記事をトピックスへ積極掲載し専門家による解説を行うほか、"
            "Yahoo!検索で新型コロナや医療情報など特定クエリに公的機関等の正しい情報を掲載し、"
            "LINE NEWS で中央省庁やNHK 等の信頼できる情報やファクトチェック団体への導線を"
            "設けています。ファクトチェック・イニシアティブ（FIJ）や日本ファクトチェック"
            "センター（JFC）の活動に賛同し資金・コンテンツ面で連携しています。啓蒙啓発・"
            "リテラシー向上としては、Yahoo!ニュースが有識者やメディアと連携して啓発コンテンツ"
            "を制作し、オープンチャットが災害時の誤情報や詐欺への注意喚起ページを公開し、"
            "LINE みらい財団が無償の情報モラル教材「GIGA ワークブック」（25 年3 月時点で"
            "18 都県・82 市区町村が公式教材として導入）や、災害時の「情報防災教育」に取り組んで"
            "います。"
        ),
    },
    {
        "page": 56, "platform": "",
        "heading": "Common — new initiatives in FY2024",
        "ja_check": "24 年度の新たな取組について",
        "en": (
            "In March 2025 LINE Yahoo revised removal and posting-suspension criteria "
            "across services, harmonising the wording of commonly occurring "
            "prohibitions (defamation, discriminatory speech, legal violations) and "
            "consolidating each service's criteria into a single set of terms, "
            "referencing the MIC's illegal-information guidelines. On monitoring, "
            "OpenChat strengthened oversight of dangerous misuse — issuing alerts on "
            "dating/real-money-trading and, given the 'dark part-time job' (闇バイト) "
            "problem, reflecting the MHLW's interpretation of the Employment Security "
            "Act and, in March 2025, revising its rules to prohibit recruitment posts "
            "in principle; Finance boards expanded generative-AI auto-removal of "
            "obscene/violent images and ad-purpose posts. To curb anonymous-account "
            "abuse, Chiebukuro abolished its 'ID-private' feature in July 2024 and "
            "Finance boards began matching mobile numbers to block re-registration by "
            "suspended users. On architecture, Yahoo! News comments introduced a "
            "proprietary 'comment-revision model' (September 2024) that suggests "
            "rewrites before posting — cutting 'offensive comments' by about 24% — and "
            "services expanded user-side moderation tools (Chiebukuro block lists, "
            "OpenChat message-hiding) and OpenChat added a thread feature."
        ),
        "ja": (
            "LINE ヤフーは、25 年3 月に各サービスの削除・投稿停止の基準を横断的に見直し、"
            "「誹謗中傷」「差別的な発言」「法令違反」など共通して発生し得る行為の禁止内容や"
            "文言を可能な限り共通化するとともに、各サービスごとに一つの規約に一本化し、"
            "総務省の違法情報ガイドラインを参考に類型を反映しました。モニタリングの強化では、"
            "オープンチャットが出会いを求める行為やリアルマネートレード等への注意喚起を行い、"
            "闇バイト問題を踏まえ厚労省の職業安定法解釈を審査基準に反映し25 年3 月に原則と"
            "して求人投稿を禁止したほか、ファイナンス掲示板が生成AI によるわいせつ・暴力的"
            "画像や広告目的投稿の自動削除を拡充しました。匿名アカウントの濫用防止として、"
            "知恵袋は24 年7 月にID 非公開機能を廃止し、ファイナンス掲示板は携帯電話番号の"
            "照合による投稿制限を開始しました。サービスアーキテクチャの改善として、ヤフコメが"
            "24 年9 月に独自AI「コメント添削モデル」を導入して投稿完了前に見直しを提案し"
            "（「不快なコメント」が約24％減少）、知恵袋のブロックリスト強化やオープンチャットの"
            "「メッセージ非表示」機能などユーザー自身によるモデレーション手段を拡張し、"
            "オープンチャットはスレッド機能を追加しました。"
        ),
    },
    {
        "page": 61, "platform": "",
        "heading": "Common — monitoring framework: AI systems",
        "ja_check": "違反投稿の監視体制",
        "en": (
            "LINE Yahoo combines AI with human review to monitor violating posts, "
            "revising its models over time as user feedback, training data and accuracy "
            "checks accumulate. For Chiebukuro, Finance boards and Yahoo! News comments, "
            "a machine-learning system built on LINE Yahoo's own deep-learning "
            "supercomputer 'kukai' judges the probability that a post breaches the "
            "rules and either auto-removes it or routes it to priority human review. "
            "Chiebukuro uses a 'low-quality-post model' (for obscenity, unintelligible "
            "or offensive posts) and a broader 'violating-post model'. Yahoo! News "
            "comments uses an 'inappropriate-post model' for auto-removal plus a "
            "'constructive-comment ranking model' and a 'comment-diversification model' "
            "to order comments in 'recommended' view. OpenChat and VOOM use a patrol "
            "platform with an AI image filter and an AI text filter that score and flag "
            "posts likely to breach the guidelines for monitoring."
        ),
        "ja": (
            "LINE ヤフーは、AI と専門チームによる「人の目」を組み合わせて違反投稿の監視を"
            "行っており、ユーザーからの評価やAI モデルの学習データの充実、正答率の検証を"
            "踏まえて適時にモデルを見直し、正確性の向上に取り組んでいます。知恵袋・ファイ"
            "ナンス掲示板・ヤフコメでは、LINE ヤフーが独自開発したディープラーニング特化型"
            "スパコン「kukai」等を活用した機械学習システムにより、投稿が禁止事項に抵触する"
            "確率を判定し、自動削除や専門チームによる優先確認フローへの移送を行っています。"
            "知恵袋は「低品質投稿判定モデル」（わいせつ・文意不明・過度な批判や誹謗中傷等）"
            "と、すべての禁止行為を対象とする「違反投稿判定モデル」を用いています。ヤフコメは"
            "「不適切投稿判定モデル」を自動削除に用いるほか、「建設的コメント順位付けモデル」"
            "「コメント多様化モデル」を加えた3 モデルで「おすすめ順」の表示順序を決定して"
            "います。オープンチャット・VOOM では、パトロール・プラットフォーム上で「AI 画像"
            "フィルター」と「AI テキストフィルター」が投稿ガイドライン違反の可能性が高い投稿"
            "に点数を付与してフラグ付けを行っています。"
        ),
    },
    {
        "page": 65, "platform": "",
        "heading": "Common — monitoring framework: expert teams and training",
        "ja_check": "専門チームによる対応体制",
        "en": (
            "LINE Yahoo keeps 191 staff (as of March 2025) able to handle content "
            "moderation in Japanese: 92 for Yahoo! News comments / Chiebukuro / Finance "
            "boards and 89 for OpenChat and VOOM, operating 24/365 to detect and judge "
            "violating posts across the services and act promptly on removals. The "
            "team's decisions are learned as ground-truth data for the AI models. Posts "
            "raising doubt about whether they breach the rules are decided through "
            "multi-perspective team discussion and, where needed, escalated to a "
            "specialist department for legal judgement (10 people, including lawyers). "
            "On training, in addition to per-service posting guidelines the company "
            "maintains internal operating manuals to avoid inconsistency, and specialist "
            "staff take at least one month of basic training (classroom, monitoring, "
            "OJT) on assignment; the legal department shares information on issues "
            "specific to Japanese society (e.g. discrimination) as needed."
        ),
        "ja": (
            "LINE ヤフーは、コンテンツモデレーションを日本語で対応可能な人員として191 人"
            "（25 年3 月時点）を常用しています。ヤフコメ・知恵袋・ファイナンス掲示板は"
            "92 人体制、オープンチャットとVOOM は89 人体制の専門チームが24 時間365 日"
            "稼働で違反投稿の探知・判定を行い、探知した場合は速やかに削除等の措置を行い"
            "ました。専門チームの判定結果はAI モデルの正解データとして学習されます。"
            "禁止事項への抵触に疑義が生じた投稿は、専門チーム内での協議による複眼的な"
            "判断を行うだけでなく、必要に応じて法的判断を行う専門部門（弁護士を含む10 人）"
            "へエスカレーションしています。教育体制としては、投稿ガイドラインに加え内部の"
            "運用マニュアルを作成して判断のぶれを防ぎ、専門チームは配属時に1 ヶ月以上の"
            "基礎研修（座学・モニタリング・OJT）を受けたスタッフが対応し、日本の風俗・社会"
            "に関する問題（差別問題等）については法的判断を行う専門部門から必要に応じて情報"
            "共有を行っています。"
        ),
    },
    {
        "page": 67, "platform": "",
        "heading": "Common — initiatives for a healthy online public sphere",
        "ja_check": "言論空間の健全化を目指した取組",
        "en": (
            "LINE Yahoo's development division releases some software and data for "
            "researchers: about 2.06 million resolved Chiebukuro questions and their "
            "~5.14 million answers are provided to researchers via the National "
            "Institute of Informatics (NII). Since September 2020, Yahoo! News has "
            "offered the API of its constructive-comment ranking model free of charge "
            "(four companies have adopted it; the underlying AI holds several patents), "
            "letting other services improve comment health without the heavy initial "
            "investment of building training data. LINE Yahoo also runs internet-safety "
            "awareness work — a nationwide 'net common-sense mock exam', child-safety "
            "programmes at its Hachinohe centre, the LINE Mirai Foundation's 13,000+ "
            "outreach classes, anti-fraud campaigns with the National Police Agency and "
            "others (including a generative-AI 'SNS investment/romance-fraud simulation "
            "tool'), and dark-part-time-job awareness — and participates in industry "
            "bodies, the public-private 'DIGITAL POSITIVE ACTION' project, and the "
            "Christchurch Call against terrorist and violent extremist content."
        ),
        "ja": (
            "LINE ヤフーの開発部門は、大学や公的研究機関の研究者に広く利用してもらうため"
            "一部のソフトウエアとデータを公開しており、知恵袋のデータベースからランダム"
            "サンプリングした解決済みの質問（約206 万件）とその回答（約514 万件）を国立"
            "情報学研究所（NII）を通じて研究者に提供しています。また、Yahoo!ニュースは"
            "20 年9 月より「建設的コメント順位付けモデル」のAPI を外部に無償提供しており"
            "（4 社の導入実績、複数の特許を取得）、大量の学習データ整備等の初期投資をかけずに"
            "コメントの健全化に向けた対策を可能にしています。さらに、「全国統一ネット常識力"
            "模試」の提供、八戸センターでの子どもを守るインターネットセーフティ事業、LINE "
            "みらい財団による13,000 回以上の出前授業、警察庁等と連携した詐欺防止の啓発"
            "（生成AI を用いた「SNS 型投資・ロマンス詐欺被害 仮想体験ツール」を含む）や"
            "闇バイトに関する啓発活動に取り組み、業界団体や官民連携プロジェクト「DIGITAL "
            "POSITIVE ACTION」、テロリスト・暴力的過激主義コンテンツに対処する「クライスト"
            "チャーチ・コール宣言」にも参画しています。"
        ),
    },
]


def _page_texts(pdf_path: str) -> list[str]:
    """Whitespace-stripped text of every page (index = 0-based PDF page index)."""
    with fitz.open(pdf_path) as doc:
        return [re.sub(r"\s+", "", doc[i].get_text()) for i in range(doc.page_count)]


def build(pdf_path: str) -> dict:
    pages = _page_texts(pdf_path)
    rows: list[list] = []
    for sec in SECTIONS:
        page = sec["page"]
        # This report's printed page number equals the 0-based PDF index (the cover
        # is unnumbered at index 0, printed page "1" is at index 1, and so on).
        if page < 1 or page >= len(pages):
            raise ValueError(f"section '{sec['heading']}' references page {page} "
                             f"but the PDF has {len(pages)} pages")
        check = re.sub(r"\s+", "", sec["ja_check"])
        if check not in pages[page]:
            raise ValueError(
                f"section '{sec['heading']}' (page {page}): ja_check "
                f"'{sec['ja_check']}' not found on that page — has the PDF changed?")
        text = _WS.sub(" ", sec["en"]).strip() + "\n\n" + _WS.sub(" ", sec["ja"]).strip()
        rows.append([COMPANY, sec["platform"], PERIOD, page, sec["heading"], text])
    rows.sort(key=lambda r: (r[3], r[1]))
    return {"source": SOURCE, "coverage": PERIOD, "columns": COLUMNS, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", default=PDF, help="Path to the archived report PDF")
    ap.add_argument("--out", default=OUT_JSON, help="Output dataset JSON path")
    args = ap.parse_args()

    data = build(args.pdf)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print(f"wrote {args.out}: {len(data['rows'])} bilingual narrative sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
