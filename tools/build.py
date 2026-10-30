#!/usr/bin/env python3
"""Static page generator for the 8th CPC Pension Calculator site.

Run from the site root:  python3 tools/build.py
It (re)writes every index.html, sitemap.xml and robots.txt.
You do NOT need to run this to update numbers in the calculator: those live
in the CONFIG object at the top of assets/app.js. Run it only if you edit
page text below or change DOMAIN.
"""
import json, os, re, html, subprocess, sys
from decimal import Decimal, ROUND_CEILING
from urllib.parse import urlparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seo_meta import SEO_META

# ---------------------------------------------------------------------------
# DOMAIN is the ONLY place the site address lives. Change it here and run
# `python3 tools/build.py`: canonicals, hreflang, OG/Twitter images, JSON-LD,
# sitemap.xml, robots.txt and the contact address are all regenerated from it.
# ---------------------------------------------------------------------------
DOMAIN = "https://8cpc-pension-calculator.vercel.app"          # <<< replace with your real domain (no trailing slash)
CONTACT_EMAIL = "contact@" + (urlparse(DOMAIN).hostname or "example.com").removeprefix("www.")  # override if you use another inbox
SITE_NAME = "8th Pay Commission Pension Calculator"
LAST_UPDATED = "2026-10-30"
LAST_UPDATED_HUMAN = "30 October 2026"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dated, newest first. Add an entry whenever a rate, rule or page changes.
# (date ISO, date human, [entries as HTML strings])
CHANGELOG = [
    ("2026-10-30", "30 October 2026", [
        "Dearness Relief updated to the official <strong>63% from 1 July 2026</strong> (was 60%). The Union Cabinet approved the 3-point increase on 28 October 2026 (<a href=\"https://pib.gov.in/PressReleasePage.aspx?PRID=2329485\" rel=\"noopener\">PIB release ID 2329485</a>): about 48.54 lakh employees and 68.71 lakh pensioners, Rs 10,016.10 crore a year. The DoPPW order for pensioners was still awaited on 30 October 2026.",
        "All calculators now use 63% as today's DR. Worked examples and tables recomputed (for example ₹20,000 + 63% DR = ₹32,600; break-even fitment factor 1.63). The <a href=\"/da-dr-calculator/\">DA/DR calculator</a> now shows the actual 60% → 63% increase and arrears instead of an estimate.",
    ]),
    ("2026-10-29", "29 October 2026", [
        "Added <a href=\"/pension-by-amount/\">pension by amount</a>: one page for each basic pension from ₹9,000 to ₹1,00,000 (18 amounts, English and Hindi) with the estimate at every fitment factor, DR, arrears, the 40% commutation case and family pension. Numbers come from the same settings and rounding as the calculator. No rates changed.",
    ]),
    ("2026-10-28", "28 October 2026 (afternoon)", [
        "Added the <a href=\"/basic-pension-finder/\">basic pension finder</a>: works back from the monthly bank credit (DR, additional pension, commutation deduction, Fixed Medical Allowance and other deductions) or from PPO figures, and pre-fills the main calculator.",
        "Added the <a href=\"/pre-2016-pensioners/\">pre-2016 pensioners calculator</a>: both 7th CPC methods (pension on 31.12.2015 × 2.57, and 50%/30% of notional pay on 01.01.2016) as set out in DoPPW OMs dated 04.08.2016 and 12.05.2017, checked against the worked examples in the 12.05.2017 OM.",
        "Added the <a href=\"/da-dr-calculator/\">DA/DR calculator</a> with arrears for a DR increase. The July 2026 rate is pre-filled as an estimate (63%) and labelled as not announced.",
        "Added <a href=\"/how-we-calculate/\">How we calculate</a> (formulas, assumptions, official sources) and this changelog; linked from every footer and every calculator result.",
        "Checked pib.gov.in at about 2:00 pm IST (list last updated 1:47 pm): no Cabinet decision on the July 2026 DA/DR instalment. DR stays at 60%.",
        "Rates are now also published as a machine-readable file, <a href=\"/assets/rates.json\">/assets/rates.json</a>, generated from the calculator settings.",
        "Navigation simplified for pensioner tasks; fitment, defence and chart pages moved to the footer and related links.",
    ]),
    ("2026-10-28", "28 October 2026", [
        "Site launched: main 8th CPC pension calculator, fitment factor calculator, family pension calculator, defence pension calculator, Hindi page, pension chart and dated latest-update page.",
        "Rates used: DR 60% from 01.01.2026 (Cabinet decision 18.04.2026; DoPPW OM 24.04.2026); minimum pension ₹9,000; maximum ₹1,25,000; family pension 30% / 50%; additional pension 20–100% from age 80. No official 8th CPC fitment factor.",
    ]),
]


def load_i18n():
    """UI strings live once, in assets/app.js. Read them through Node so the
    static HTML labels and the JS translations can never drift apart."""
    try:
        out = subprocess.check_output(["node", "-e", "process.stdout.write(JSON.stringify(require(process.argv[1]).I18N))",
                                       os.path.join(ROOT, "assets", "app.js")])
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit("Node.js is required to build (reads I18N from assets/app.js): " + str(e))
    return json.loads(out)


I18N = load_i18n()


def T(lang, k):
    return html.escape(I18N[lang][k])


def up(x):
    """Round up to the next rupee, like up() in app.js."""
    return int(Decimal(str(x)).to_integral_value(rounding=ROUND_CEILING))

CHART_ROWS = [9000, 10000, 11000, 12500, 15000, 17500, 20000, 22500, 25000, 27500, 30000, 35000, 40000, 45000,
              50000, 55000, 60000, 65000, 70000, 75000, 80000, 90000, 100000, 110000, 125000]
CHART_FACTORS = ["1.92", "2.28", "2.57", "2.86", "3.0", "3.833"]


def inr(n):
    s = str(int(n))
    if len(s) > 3:
        last3, rest = s[-3:], s[:-3]
        rest = re.sub(r"\B(?=(\d{2})+(?!\d))", ",", rest)
        s = rest + "," + last3
    return "₹" + s


def ceil_mul(b, f):
    return int((Decimal(b) * Decimal(f)).to_integral_value(rounding=ROUND_CEILING))


# ------------------------------------------------------------------ shell
NAV = [("/", "nav_home"), ("/basic-pension-finder/", "nav_finder"), ("/family-pension-calculator/", "nav_family"),
       ("/pre-2016-pensioners/", "nav_pre2016"), ("/da-dr-calculator/", "nav_dadr"), ("/latest-update/", "nav_updates")]
NAV_TXT = {lg: {k: I18N[lg][k] for k in ("nav_home", "nav_finder", "nav_family", "nav_pre2016", "nav_dadr", "nav_updates",
                                         "nav_fitment", "nav_defence", "nav_chart")} for lg in ("en", "hi")}
# footer: (href, i18n key)
FOOTER_TOOLS = [("/fitment-factor-calculator/", "nav_fitment"), ("/defence-pension-calculator/", "nav_defence"),
                ("/pension-chart/", "nav_chart"), ("/pension-by-amount/", "nav_byamount"), ("/basic-pension-finder/", "nav_finder"), ("/pre-2016-pensioners/", "nav_pre2016"),
                ("/da-dr-calculator/", "nav_dadr"), ("/commutation-calculator/", "nav_commutation"),
                ("/minimum-pension-8th-pay-commission/", "nav_minpension"), ("/life-certificate/", "nav_lifecert")]
FOOTER_SITE = [("/how-we-calculate/", "ftr_how"), ("/editorial-policy/", "ftr_editorial"), ("/changelog/", "ftr_changelog"), ("/latest-update/", "nav_updates"),
               ("/about/", "ftr_about"), ("/privacy/", "ftr_privacy"), ("/disclaimer/", "ftr_disclaimer"), ("/contact/", "ftr_contact")]

UI = {
    "en": dict(skip="Skip to calculator", menu="Menu", langbtn="हिंदी",
               est="Estimate — not official. The 8th Pay Commission has not announced a fitment factor.",
               status="Status", status_text="8th CPC constituted 3 Nov 2025 · Report due about May 2027 · No official fitment factor · DR 63% from 1 Jul 2026 (Cabinet 28 Oct 2026)",
               updated="Data last updated:",
               disc="Independent, unofficial calculator. Not affiliated with, endorsed by or part of the Government of India, DoPPW, CPAO or the 8th Central Pay Commission. All results are estimates for information only.",
               about="About", privacy="Privacy", disclaimer="Disclaimer", contact="Contact", hindi="हिंदी में पढ़ें", faq="Frequently asked questions",
               related="Related calculators and guides", home="Home"),
    "hi": dict(skip="कैलकुलेटर पर जाएँ", menu="मेनू", langbtn="English",
               est="अनुमान — आधिकारिक नहीं। 8वें वेतन आयोग ने अभी कोई फिटमेंट फैक्टर घोषित नहीं किया है।",
               status="स्थिति", status_text="8वाँ वेतन आयोग 3 नवंबर 2025 को गठित · रिपोर्ट लगभग मई 2027 तक · कोई आधिकारिक फिटमेंट फैक्टर नहीं · 1 जुलाई 2026 से DR 63% (कैबिनेट 28 अक्टूबर 2026)",
               updated="डेटा अंतिम बार अपडेट:",
               disc="स्वतंत्र, अनौपचारिक कैलकुलेटर। भारत सरकार, DoPPW, CPAO या 8वें केंद्रीय वेतन आयोग से कोई संबंध, समर्थन या हिस्सा नहीं। सभी परिणाम केवल जानकारी हेतु अनुमान हैं।",
               about="हमारे बारे में", privacy="गोपनीयता", disclaimer="अस्वीकरण", contact="संपर्क", hindi="Read in English", faq="अक्सर पूछे जाने वाले सवाल",
               related="संबंधित कैलकुलेटर और गाइड", home="होम"),
}

CALC_LABELS = {
    "en": dict(calc_title="8th CPC pension calculator", lbl_basic="Current basic pension (7th CPC), ₹ per month",
               hint_basic="As shown in your PPO / bank pension slip — before DR and commutation deduction.",
               lbl_type="Pension type", opt_sup="Superannuation / retiring pension", opt_fpn="Family pension — normal rate (30%)",
               opt_fpe="Family pension — enhanced rate (50%)", lbl_age="Age of pensioner / family pensioner (years)",
               hint_age="Additional pension starts at 80 (20%), 85 (30%), 90 (40%), 95 (50%), 100 (100%).",
               lbl_factor="Fitment factor", lbl_custom="Custom fitment factor", lbl_dr="Current Dearness Relief (DR) %",
               hint_dr="63% from 1 Jul 2026 (Cabinet decision 28 Oct 2026). Change it if a new DR is announced.", lbl_eff="Assumed date of effect (arrears from)",
               hint_eff="Widely expected 1 Jan 2026 — not official.", lbl_pay="Month revised pension starts being paid",
               hint_pay="Arrears are counted up to the month before this.", btn_calc="Calculate", btn_reset="Reset"),
    "hi": dict(calc_title="8वाँ वेतन आयोग पेंशन कैलकुलेटर", lbl_basic="वर्तमान मूल पेंशन (7वाँ वेतन आयोग), ₹ प्रति माह",
               hint_basic="PPO / बैंक पेंशन स्लिप में दी गई राशि — DR और कम्यूटेशन कटौती से पहले।",
               lbl_type="पेंशन का प्रकार", opt_sup="सेवानिवृत्ति पेंशन (सुपरएनुएशन / रिटायरिंग)", opt_fpn="पारिवारिक पेंशन — सामान्य दर (30%)",
               opt_fpe="पारिवारिक पेंशन — बढ़ी हुई दर (50%)", lbl_age="पेंशनभोगी / पारिवारिक पेंशनभोगी की आयु (वर्ष)",
               hint_age="अतिरिक्त पेंशन: 80 वर्ष पर 20%, 85 पर 30%, 90 पर 40%, 95 पर 50%, 100 पर 100%।",
               lbl_factor="फिटमेंट फैक्टर", lbl_custom="अपना फिटमेंट फैक्टर", lbl_dr="वर्तमान महंगाई राहत (DR) %",
               hint_dr="1 जुलाई 2026 से 63% (कैबिनेट निर्णय 28 अक्टूबर 2026)। नई DR घोषित हो तो बदलें।", lbl_eff="मानी गई लागू तिथि (एरियर कब से)",
               hint_eff="1 जनवरी 2026 की व्यापक उम्मीद — आधिकारिक नहीं।", lbl_pay="नई पेंशन का भुगतान किस महीने से",
               hint_pay="एरियर इससे पिछले महीने तक गिना जाता है।", btn_calc="गणना करें", btn_reset="रीसेट"),
}


def calc_block(lang, default_type="sup", extra=""):
    L = CALC_LABELS[lang]
    def s(k):
        return f'<span data-i18n="{k}">{html.escape(L[k])}</span>'
    extra_html = ""
    if extra == "family":
        x = {"en": ("Don't know your family pension? Work it out from last pay", "Last basic pay drawn (7th CPC), ₹", "Work out"),
             "hi": ("पारिवारिक पेंशन नहीं पता? अंतिम वेतन से निकालें", "अंतिम मूल वेतन (7वाँ आयोग), ₹", "निकालें")}[lang]
        extra_html = f'''<div class="card extra"><h2 data-i18n="fp_title">{x[0]}</h2>
<div class="grid"><div><label for="lastPay" data-i18n="lbl_lastpay">{x[1]}</label><input id="lastPay" type="number" inputmode="numeric" min="18000" max="250000" step="1" placeholder="e.g. 56100"></div>
<div style="align-self:end"><button type="button" class="btn" id="fpBtn" data-i18n="btn_fp">{x[2]}</button></div></div>
<p id="fpOut" class="note" role="status" aria-live="polite"></p></div>'''
    if extra == "reverse":
        x = {"en": ("Find the fitment factor from two amounts", "Current basic pension (₹)", "Expected new basic pension (₹)", "Find factor"),
             "hi": ("दो राशियों से फिटमेंट फैक्टर निकालें", "वर्तमान मूल पेंशन (₹)", "अपेक्षित नई मूल पेंशन (₹)", "फैक्टर निकालें")}[lang]
        extra_html = f'''<div class="card extra"><h2 data-i18n="reverse_title">{x[0]}</h2>
<div class="grid"><div><label for="revOld" data-i18n="lbl_rev_old">{x[1]}</label><input id="revOld" type="number" inputmode="numeric" min="1" step="1" placeholder="9000"></div>
<div><label for="revNew" data-i18n="lbl_rev_new">{x[2]}</label><input id="revNew" type="number" inputmode="numeric" min="1" step="1" placeholder="25740"></div></div>
<div class="btnrow"><button type="button" class="btn" id="revBtn" data-i18n="btn_rev">{x[3]}</button></div>
<p id="revOut" class="note" role="status" aria-live="polite"></p></div>'''
    return f'''<section class="card" id="calc" aria-labelledby="calcTitle">
<h2 id="calcTitle" data-i18n="calc_title">{L["calc_title"]}</h2>
<p id="officialBanner" class="note" hidden></p>
<form id="calcForm" novalidate data-default-type="{default_type}">
<div class="grid">
<div class="full"><label for="basic">{s("lbl_basic")}<span class="hint" data-i18n="hint_basic">{L["hint_basic"]}</span></label>
<input id="basic" name="bp" type="number" inputmode="numeric" min="1000" max="250000" step="1" required placeholder="e.g. 20000">
<a class="hint" href="/basic-pension-finder/" data-i18n="link_finder">{T(lang, "link_finder")}</a></div>
<div><label for="ptype">{s("lbl_type")}</label>
<select id="ptype" name="type"><option value="sup" data-i18n="opt_sup">{L["opt_sup"]}</option><option value="fpn" data-i18n="opt_fpn">{L["opt_fpn"]}</option><option value="fpe" data-i18n="opt_fpe">{L["opt_fpe"]}</option></select></div>
<div><label for="age">{s("lbl_age")}<span class="hint" data-i18n="hint_age">{L["hint_age"]}</span></label>
<input id="age" name="age" type="number" inputmode="numeric" min="18" max="120" step="1" placeholder="e.g. 68"></div>
<div><label for="factor">{s("lbl_factor")}</label><select id="factor" name="ff"><option value="2.57">2.57</option></select></div>
<div id="customWrap" hidden><label for="customFactor">{s("lbl_custom")}</label><input id="customFactor" type="number" inputmode="decimal" min="1" max="6" step="0.001" placeholder="e.g. 2.95"></div>
<div><label for="dr">{s("lbl_dr")}<span class="hint" data-i18n="hint_dr">{L["hint_dr"]}</span></label>
<input id="dr" name="dr" type="number" inputmode="decimal" min="0" max="200" step="0.01" value="63"></div>
<div><label for="effFrom">{s("lbl_eff")}<span class="hint" data-i18n="hint_eff">{L["hint_eff"]}</span></label><select id="effFrom" name="from"></select></div>
<div><label for="payMonth">{s("lbl_pay")}<span class="hint" data-i18n="hint_pay">{L["hint_pay"]}</span></label><select id="payMonth" name="pay"></select></div>
</div>
<p id="formError" class="err" role="alert" hidden></p>
<div class="btnrow"><button type="submit" class="btn" data-i18n="btn_calc">{L["btn_calc"]}</button><button type="reset" class="btn sec" data-i18n="btn_reset">{L["btn_reset"]}</button></div>
</form>
</section>
<section id="results" class="card" aria-live="polite" hidden></section>
<!-- ===== AdSense slot (results) =====
     After AdSense approval, paste your <ins class="adsbygoogle" ...> unit here,
     add the AdSense loader <script> in <head>, and extend the CSP in vercel.json
     (script-src/img-src/frame-src/connect-src for *.googlesyndication.com, *.doubleclick.net,
     *.google.com, *.gstatic.com, adservice.google.com). See README.md.
<div class="ad-slot"></div>
===== /AdSense slot ===== -->
{extra_html}'''


ALL_PATHS = set()   # filled in main() before rendering


def hi_path(p):
    return "/hi/" if p == "/" else "/hi" + p


def en_path(p):
    return "/" if p == "/hi/" else p[3:]


def counterpart(p):
    """The same page in the other language, or None."""
    c = en_path(p) if p.startswith("/hi/") else hi_path(p)
    return c if c in ALL_PATHS else None


def L(lang, h):
    """An internal link in the page's own language."""
    if lang != "hi" or not h.startswith("/") or h.startswith("/hi/") or h.startswith("/assets/"):
        return h
    return hi_path(h) if hi_path(h) in ALL_PATHS or not ALL_PATHS else h


VERIFIED_HUMAN = {"en": "30 Oct 2026", "hi": "30 अक्टूबर 2026"}


def sources_box(lang, keys):
    if not keys:
        return ""
    h = {"en": ("Sources", "Last verified: " + VERIFIED_HUMAN["en"] + ". Every link below was opened and checked on that date. Official documents are primary sources; news reports are used only for demands and are labelled as such.",
                "How we check facts"),
         "hi": ("स्रोत", "अंतिम जाँच: " + VERIFIED_HUMAN["hi"] + "। नीचे दिया हर लिंक उसी दिन खोलकर जाँचा गया। सरकारी दस्तावेज़ मुख्य स्रोत हैं; समाचार रिपोर्टें केवल माँगों के लिए इस्तेमाल होती हैं और उन पर यह लिखा होता है।",
                "हम तथ्य कैसे जाँचते हैं")}[lang]
    items = "".join(f'<li><a href="{SRC[k][0]}" rel="noopener">{html.escape(SRC[k][1 if lang == "en" else 2])}</a></li>' for k in keys)
    return (f'<section class="card sources" id="sources" aria-labelledby="srcH"><h2 id="srcH">{h[0]}</h2><p class="fine">{h[1]}</p>'
            f'<ul>{items}</ul><p class="fine"><a href="{L(lang, "/editorial-policy/")}">{h[2]}</a> · <a href="{L(lang, "/how-we-calculate/")}">'
            f'{"How we calculate" if lang == "en" else "हम गणना कैसे करते हैं"}</a></p></section>')


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def page(p):
    lang = p.get("lang", "en")
    U = UI[lang]
    path = p["path"]
    url = DOMAIN + path
    home = "/hi/" if lang == "hi" else "/"
    crumbs = [(U["home"], home)] + list(p.get("parents", [])) + ([(p["crumb"], path)] if path not in ("/", "/hi/") else [])
    cp = counterpart(path)
    cur_attr = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{L(lang, h)}"{cur_attr if L(lang, h) == path else ""} data-i18n="{k}">{NAV_TXT[lang][k]}</a></li>' for h, k in NAV)
    other = "en" if lang == "hi" else "hi"
    switch_href = cp or ("/" if lang == "hi" else "/hi/")
    nav += f'<li><a href="{switch_href}" lang="{other}" hreflang="{other}-IN">{U["hindi"]}</a></li>'
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + h} for i, (n, h) in enumerate(crumbs)]}]
    if p.get("faqs"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in p["faqs"]]})
    if p.get("webapp"):
        ld.append({"@context": "https://schema.org", "@type": "WebApplication", "name": p["h1"], "url": url,
                   "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "browserRequirements": "Requires JavaScript",
                   "inLanguage": "hi-IN" if lang == "hi" else "en-IN", "isAccessibleForFree": True,
                   "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
                   "description": p["desc"], "dateModified": LAST_UPDATED, "publisher": {"@id": DOMAIN + "/#org"}})
    org = {"@type": "Organization", "@id": DOMAIN + "/#org", "name": SITE_NAME, "alternateName": "8CPC Pension Calculator team",
           "url": DOMAIN + "/", "logo": DOMAIN + "/icon-512.png", "email": CONTACT_EMAIL,
           "publishingPrinciples": DOMAIN + "/editorial-policy/"}
    ld.append({"@context": "https://schema.org", "@type": "WebPage", "@id": url + "#webpage", "url": url,
               "name": p["title"], "description": p["desc"], "inLanguage": "hi-IN" if lang == "hi" else "en-IN",
               "isPartOf": {"@id": DOMAIN + "/#website"}, "publisher": {"@id": DOMAIN + "/#org"},
               "dateModified": p.get("lastmod", LAST_UPDATED), "datePublished": p.get("published", "2026-10-28"),
               **({"lastReviewed": LAST_UPDATED} if p.get("sources") else {}),
               **({"workTranslation" if lang == "en" else "translationOfWork": {"@id": DOMAIN + cp + "#webpage"}} if cp else {})})
    if path in ("/", "/hi/"):
        ld.append(dict({"@context": "https://schema.org"}, **org))
        ld.append({"@context": "https://schema.org", "@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/",
                   "name": SITE_NAME, "inLanguage": ["en-IN", "hi-IN"], "publisher": {"@id": DOMAIN + "/#org"}})
    alt = ""
    if cp:
        en_u, hi_u = (cp, path) if lang == "hi" else (path, cp)
        alt = (f'<link rel="alternate" hreflang="en-IN" href="{DOMAIN}{en_u}">'
               f'<link rel="alternate" hreflang="hi-IN" href="{DOMAIN}{hi_u}">'
               f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{en_u}">')
    crumb_html = "".join(
        (f'<li><a href="{h}">{html.escape(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{html.escape(n)}</li>')
        for i, (n, h) in enumerate(crumbs))
    faq_html = ""
    if p.get("faqs"):
        faq_html = f'<section class="faq" aria-labelledby="faqH"><h2 id="faqH">{U["faq"]}</h2>' + "".join(
            f"<details><summary>{html.escape(q)}</summary><p>{a}</p></details>" for q, a in p["faqs"]) + "</section>"
    rel_html = ""
    if p.get("related"):
        rel_html = f'<section class="related" aria-labelledby="relH"><h2 id="relH">{U["related"]}</h2><ul>' + "".join(
            f'<li><a href="{L(lang, h)}">{html.escape(t)}</a> — {html.escape(d)}</li>' for h, t, d in p["related"]) + "</ul></section>"
    calc = calc_block(lang, p.get("default_type", "sup"), p.get("extra", "")) if p.get("calc") else p.get("widget", "")
    skip = f'<a class="skip" href="#{"calc" if (p.get("calc") or p.get("widget")) else "main"}">{U["skip"]}</a>'
    _o = SEO_META.get(path)
    if _o:
        if _o[0]: p["title"] = _o[0]
        if _o[1]: p["desc"] = _o[1]
    title = html.escape(p["title"])
    desc = html.escape(p["desc"])
    verified_line = ""
    if p.get("sources"):
        verified_line = ({"en": f'<p class="verified"><strong>Last verified: {VERIFIED_HUMAN["en"]}</strong> against official orders · <a href="#sources">Sources</a></p>',
                          "hi": f'<p class="verified"><strong>अंतिम जाँच: {VERIFIED_HUMAN["hi"]}</strong> — सरकारी आदेशों से मिलान · <a href="#sources">स्रोत</a></p>'}[lang])
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="hGSoJI1wRbG8Ewhdi9yIwZpeqSmH9ahDJwkpcl-5GFw">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
{alt}
<meta name="robots" content="{p.get("robots", "index,follow,max-image-preview:large")}">
<meta name="theme-color" content="#0b3d91">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{"hi_IN" if lang == "hi" else "en_IN"}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{DOMAIN}/og-image.png">
<link rel="stylesheet" href="/assets/style.css">
<script src="/assets/app.js" defer></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-563KPY9L7M"></script>
<script src="/assets/ga.js"></script>
<!-- AdSense loader goes here after approval (see README.md and update CSP in vercel.json) -->
{"".join(jsonld(x) for x in ld)}
</head>
<body>
{skip}
<header class="site"><div class="wrap">
<a class="brand" href="{home}"><img src="/favicon.svg" alt="" width="30" height="30"><span>{"8वाँ वेतन आयोग पेंशन कैलकुलेटर" if lang == "hi" else "8th CPC Pension Calculator"}</span></a>
<button type="button" class="hbtn" id="menuBtn" aria-expanded="false" aria-controls="mainNav" data-i18n="nav_menu">{U["menu"]}</button>
<nav class="main" id="mainNav" aria-label="Main"><ul>{nav}</ul></nav>
<a class="hbtn" id="langLink" href="{switch_href}" lang="{other}" hreflang="{other}-IN" aria-label="{"Read this page in English" if lang == "hi" else "यह पेज हिंदी में पढ़ें"}">{U["langbtn"]}</a>
</div></header>
<div class="strip" role="note"><div class="wrap"><strong data-i18n="status_label">{U["status"]}</strong>: <span data-i18n="status_text">{U["status_text"]}</span> · <span data-i18n="updated">{U["updated"]}</span> <span data-cfg="lastUpdated">{LAST_UPDATED}</span></div></div>
<main id="main" class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><ol>{crumb_html}</ol></nav>
<h1>{p["h1"]}</h1>
<p class="lead">{p["lead"]}</p>
<p class="estbar" data-i18n="est_banner">{U["est"]}</p>
{verified_line}
{calc}
<article>
{p["body"]}
</article>
{sources_box(lang, p.get("sources"))}
{faq_html}
{rel_html}
</main>
<footer class="site"><div class="wrap">
<p data-i18n="footer_disc">{U["disc"]}</p>
<p><strong data-i18n="ftr_tools">{T(lang, "ftr_tools")}</strong></p>
<ul>{"".join(f'<li><a href="{L(lang, h)}" data-i18n="{k}">{T(lang, k)}</a></li>' for h, k in FOOTER_TOOLS)}</ul>
<ul>{"".join(f'<li><a href="{L(lang, h)}" data-i18n="{k}">{T(lang, k)}</a></li>' for h, k in FOOTER_SITE)}</ul>
<p><span data-i18n="updated">{U["updated"]}</span> <span data-cfg="lastUpdated">{LAST_UPDATED}</span> · © 2026 {SITE_NAME}</p>
</div></footer>
</body>
</html>
'''


# ------------------------------------------------------------------ content
REL_ALL = {
    "/": ("8th Pay Commission pension calculator", "full calculator with arrears and comparison"),
    "/fitment-factor-calculator/": ("Fitment factor calculator", "what each multiplier means for your pension"),
    "/family-pension-calculator/": ("Family pension calculator", "normal 30% and enhanced 50% rates"),
    "/defence-pension-calculator/": ("Defence pension calculator", "for armed forces pensioners"),
    "/pension-chart/": ("8th CPC pension chart", "₹9,000 to ₹1,25,000 at six fitment factors"),
    "/latest-update/": ("Latest 8th CPC update", "dated status as of " + LAST_UPDATED_HUMAN),
    "/hi/": ("8वां वेतन आयोग पेंशन कैलकुलेटर (हिंदी)", "पूरी जानकारी हिंदी में"),
    "/basic-pension-finder/": ("Basic pension finder", "work out basic pension from the bank credit or PPO"),
    "/pre-2016-pensioners/": ("Pre-2016 pensioners calculator", "2.57× vs notional pay fixation, and the 8th CPC estimate"),
    "/da-dr-calculator/": ("DA / DR calculator", "Dearness Relief and arrears for a DR hike"),
    "/how-we-calculate/": ("How we calculate", "formulas, assumptions and official sources"),
    "/changelog/": ("Changelog", "every dated change to rates and pages"),
}


def rel(*paths):
    return [(p, REL_ALL[p][0], REL_ALL[p][1]) for p in paths]


chart_head = "".join(f"<th scope=\"col\">×{f}</th>" for f in CHART_FACTORS)
chart_rows = "".join(
    f"<tr><th scope=\"row\">{inr(b)}</th>" + "".join(f"<td>{inr(ceil_mul(b, f))}</td>" for f in CHART_FACTORS) + "</tr>"
    for b in CHART_ROWS)
CHART_TABLE = (f'<div class="tbl-wrap"><table class="chart" id="chartTable" data-factors="{",".join(CHART_FACTORS)}" '
               f'data-rows="{",".join(map(str, CHART_ROWS))}"><caption>New basic pension only (no DR). Rounded up to the next rupee. '
               f'Estimate — not official.</caption><thead><tr><th scope="col">Basic pension (7th CPC)</th>{chart_head}</tr></thead>'
               f'<tbody>{chart_rows}</tbody></table></div>')

FACTOR_TABLE = """<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Fitment factor</th><th scope="col">Where the number comes from</th><th scope="col">₹9,000 becomes</th></tr></thead><tbody>
<tr><td>1.92</td><td>Low-end estimate seen in media reports</td><td>₹17,280</td></tr>
<tr><td>2.28</td><td>Media estimate</td><td>₹20,520</td></tr>
<tr><td>2.57</td><td>Factor actually used by the 7th CPC in 2016</td><td>₹23,130</td></tr>
<tr><td>2.86</td><td>Media estimate</td><td>₹25,740</td></tr>
<tr><td>3.00</td><td>Round-number estimate</td><td>₹27,000</td></tr>
<tr><td>3.25</td><td>Media estimate</td><td>₹29,250</td></tr>
<tr><td>3.68</td><td>Often-quoted union figure</td><td>₹33,120</td></tr>
<tr><td>3.833</td><td>Demand of the NC-JCM staff side and pensioner bodies</td><td>₹34,497</td></tr>
</tbody></table></div>"""

PAGES = []

# ---------------- index
PAGES.append(dict(
    path="/", crumb="Home", webapp=True, calc=True,
    title="8th Pay Commission Pension Calculator 2026 – Salary Calculator for Pensioners",
    desc="Free 8th Pay Commission pension calculator for central government pensioners: new basic pension, DR, monthly increase and arrears at every fitment factor (1.92–3.833). Estimate, not official.",
    h1="8th Pay Commission Salary Calculator for Pensioners",
    lead="Enter your 7th CPC basic pension to estimate your revised pension under the 8th Central Pay Commission — new basic pension, total monthly pension, increase and arrears — at any fitment factor. Updated " + LAST_UPDATED_HUMAN + ".",
    body=f"""
<h2>Where the 8th Pay Commission stands today</h2>
<p>The Union Cabinet approved the Terms of Reference of the 8th Central Pay Commission on 28 October 2025, and the Commission was formally constituted on 3 November 2025 under the chairmanship of Justice Ranjana Prakash Desai. It has 18 months from that date to make its recommendations, which puts the report at around May 2027. Since then it has collected memorandums (submissions closed on 15 June 2026) and held consultations in cities including Jaipur, Chandigarh, Bengaluru and Mumbai.</p>
<p>As of {LAST_UPDATED_HUMAN} <strong>no fitment factor, new pension matrix or date of effect has been announced</strong>. The Government's press release said that, going by the usual ten-year cycle, the effect of the recommendations "would normally be expected from 01.01.2026" — a statement of past practice, not a decision. Every number this calculator produces is therefore an estimate built on assumptions that you can change.</p>

<h2>How the calculator works</h2>
<p>The 7th Pay Commission revised pensions by multiplying the existing basic pension by a single fitment factor (2.57) and rounding up to the next rupee. Dearness Relief then started again from zero on the new pension. This calculator applies the same method to your current 7th CPC basic pension:</p>
<ol>
<li><strong>Your pension today</strong> = basic pension + additional pension for age (if 80 or older) + Dearness Relief (63% of basic plus additional pension from 1 July 2026).</li>
<li><strong>New basic pension</strong> = current basic pension × fitment factor, rounded up. If the result falls below an estimated new minimum (₹9,000 × the same factor), it is raised to that minimum.</li>
<li><strong>New total</strong> = new basic + new additional pension (same percentage for your age) + DR on the new pension (assumed 0% at the start).</li>
<li><strong>Arrears</strong> = monthly increase × number of months from the assumed date of effect to the month before the revised pension is first paid.</li>
</ol>
<p>Because DR is already 63%, a factor needs to be above 1.63 just for your total pension to stay the same once DR resets. That is why the comparison table shows a much smaller jump in total pension than the factor alone suggests. At 2.57, ₹9,000 basic becomes ₹23,130 — but today's ₹9,000 pension already pays ₹14,670 with DR, so the real monthly gain is ₹8,460 (about 58%).</p>

<h2>Current 7th CPC rules used in the calculation</h2>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Item</th><th scope="col">Current rule</th><th scope="col">Source</th></tr></thead><tbody>
<tr><td>Minimum pension / family pension</td><td>₹9,000 per month</td><td>CCS (Pension) Rules, 2021</td></tr>
<tr><td>Maximum pension</td><td>₹1,25,000 (50% of highest pay ₹2,50,000)</td><td>CCS (Pension) Rules, 2021</td></tr>
<tr><td>Maximum family pension</td><td>₹75,000 normal (30%); ₹1,25,000 enhanced (50%)</td><td>Rule 50, CCS (Pension) Rules, 2021</td></tr>
<tr><td>Additional pension for age</td><td>80–84: 20% · 85–89: 30% · 90–94: 40% · 95–99: 50% · 100+: 100%</td><td>Rules 44 &amp; 50, CCS (Pension) Rules, 2021</td></tr>
<tr><td>Dearness Relief</td><td>63% from 1 July 2026 (60% from 1 January 2026 before that)</td><td>Cabinet decision 28.10.2026, PIB release 2329485; DoPPW order awaited as of {LAST_UPDATED_HUMAN}</td></tr>
</tbody></table></div>

<h2>Which fitment factor should you pick?</h2>
<p>Nobody knows the final figure yet. Use 2.57 to see what a repeat of the 7th CPC would mean, 3.833 to see the demand made by the staff side of the National Council (JCM) and pensioner associations, and something in between for a middle case. Employee bodies' demands range widely — one railway association has even proposed graded factors up to 4.38 for the top pay levels — while the lowest figures quoted in the media are around 1.92. The <a href="/fitment-factor-calculator/">fitment factor calculator</a> explains each number, and the <a href="/pension-chart/">pension chart</a> lists ready-made results from ₹9,000 to ₹1,25,000.</p>

<h2>What the estimate does not include</h2>
<ul>
<li><strong>Commutation:</strong> if you commuted part of your pension, the monthly deduction continues until restoration. Enter your full basic pension, not the reduced amount credited. If you only know what reaches your bank, the <a href="/basic-pension-finder/">basic pension finder</a> works it out.</li>
<li><strong>Income tax, Fixed Medical Allowance and CGHS:</strong> not part of the calculation.</li>
<li><strong>Changes in DR before implementation:</strong> the July 2026 increase (to 63%) is already in the DR box; if a January 2027 or later DR increase is announced, your current pension rises and the arrears change. Update the DR box to reflect it, or use the <a href="/da-dr-calculator/">DA/DR calculator</a> for the DR arrears alone.</li>
<li><strong>Special rules the Commission may recommend:</strong> for example a different method for older pensioners (the 7th CPC gave <a href="/pre-2016-pensioners/">pre-2016 pensioners</a> the higher of two methods), a new minimum pension or changed age slabs. When official numbers arrive this site will be updated. Our formulas and sources are on <a href="/how-we-calculate/">How we calculate</a>.</li>
</ul>
<p>Family pensioners can use the <a href="/family-pension-calculator/">family pension calculator</a> to work out normal (30%) or enhanced (50%) family pension from last pay, and armed forces pensioners should read the notes on the <a href="/defence-pension-calculator/">defence pension calculator</a>. For a dated record of announcements, see the <a href="/latest-update/">latest update</a> page. यह जानकारी <a href="/hi/">हिंदी में</a> भी उपलब्ध है।</p>
""",
    faqs=[
        ("What is the fitment factor for pensioners in the 8th Pay Commission?", "It has not been announced. As of " + LAST_UPDATED_HUMAN + " the Commission has not submitted its report. The 7th CPC used 2.57; the NC-JCM staff side and pensioner bodies have asked for 3.833. Figures like 1.92, 2.28 or 2.86 are estimates, not official numbers."),
        ("How much will a ₹9,000 pension become under the 8th Pay Commission?", "At a factor of 2.57 it would become ₹23,130; at 2.86, ₹25,740; at 3.0, ₹27,000; at 3.833, ₹34,497. These are estimates. Remember that DR (63% from July 2026) is expected to restart from zero, so the gain in total pension is smaller than the jump in basic pension."),
        ("When will the 8th Pay Commission be implemented for pensioners?", "The date has not been fixed. The Commission's report is due within 18 months of 3 November 2025, around May 2027. The Government has said the effect would normally be expected from 1 January 2026 based on past practice, which is why arrears are commonly estimated from that date."),
        ("Will pensioners get arrears from January 2026?", "If the Government sets 1 January 2026 as the date of effect, as happened with the 7th CPC (effective 1 January 2016, paid from mid-2016), pensioners would get arrears for the gap. This is not yet decided. The calculator lets you change both the date of effect and the payment month."),
        ("Is Dearness Relief included in the new pension?", "Past pay commissions merged the DR into the new basic pension through the fitment factor and restarted DR at 0%. The calculator assumes the same. You can see DR today (63%) and after revision side by side."),
        ("Is this calculator official?", "No. It is an independent tool and is not affiliated with the Government of India, DoPPW, CPAO or the 8th Pay Commission. Every result is an estimate. Your actual revised pension will be fixed by your Pension Disbursing Authority under official orders."),
    ],
    related=rel("/basic-pension-finder/", "/pre-2016-pensioners/", "/da-dr-calculator/", "/fitment-factor-calculator/", "/family-pension-calculator/", "/defence-pension-calculator/", "/pension-chart/", "/how-we-calculate/", "/latest-update/", "/hi/"),
))

# ---------------- fitment factor
PAGES.append(dict(
    path="/fitment-factor-calculator/", crumb="Fitment Factor Calculator", webapp=True, calc=True, extra="reverse",
    title="8th Pay Commission Fitment Factor Calculator for Pension (1.92 to 3.833)",
    desc="See what each 8th CPC fitment factor — 1.92, 2.28, 2.57, 2.86, 3.0, 3.25, 3.68, 3.833 or your own — means for your basic pension and total pension. Includes a reverse factor finder.",
    h1="8th Pay Commission Fitment Factor Calculator",
    lead="The fitment factor is the multiplier that turns your 7th CPC basic pension into an 8th CPC basic pension. Test any factor below, or work backwards from an amount to the factor it implies.",
    body=f"""
<h2>What is a fitment factor?</h2>
<p>A fitment factor is a single number by which the old basic pay or basic pension is multiplied to fix the new one when a pay commission is implemented. For pensioners the method under the 7th CPC was simple: the pension being drawn on 31 December 2015 was multiplied by 2.57 and rounded up to the next rupee. That one multiplier did two jobs at once — it absorbed the Dearness Relief that had built up (125% at the time) and added a real increase on top.</p>
<p>Because the 8th CPC has not reported, there is <strong>no official fitment factor yet</strong>. The table below explains where the commonly quoted numbers come from, so you can choose sensible scenarios instead of believing a viral figure.</p>
{FACTOR_TABLE}
<p class="note">None of these is official. The 7th CPC staff side had asked for a factor of about 3.7 in 2015 and got 2.57, which shows how far a final figure can be from the demand.</p>

<h2>The break-even factor: why 1.63 matters</h2>
<p>Dearness Relief is 63% of basic pension from 1 July 2026 (Cabinet decision of 28 October 2026). If DR resets to zero when the new pension starts, a fitment factor of exactly 1.63 would leave your total monthly pension unchanged. Only the part of the factor above 1.63 is a real increase. For a ₹20,000 basic pension:</p>
<ul>
<li>Today: ₹20,000 + 63% DR (₹12,600) = <strong>₹32,600</strong></li>
<li>At 1.92: ₹38,400 → an increase of ₹5,800 (about 18%)</li>
<li>At 2.57: ₹51,400 → an increase of ₹18,800 (about 58%)</li>
<li>At 2.86: ₹57,200 → an increase of ₹24,600 (about 75%)</li>
<li>At 3.833: ₹76,660 → an increase of ₹44,060 (about 135%)</li>
</ul>
<p>If another DR instalment is announced before implementation (the next would normally take effect from 1 January 2027), the break-even point moves up with it. Change the DR box in the calculator to see the effect.</p>

<h2>How the 8th CPC is likely to arrive at its factor</h2>
<p>Historically the factor has been worked out from a proposed minimum pay. The 7th CPC fixed the minimum pay at ₹18,000 against ₹7,000 earlier, a ratio of 2.57, and applied it uniformly. Employee bodies use the same logic for their demands: the NC-JCM staff side's proposed minimum pay of ₹69,000 divided by ₹18,000 gives 3.833. The Commission's Terms of Reference ask it to keep in view fiscal prudence, the unfunded cost of non-contributory pension schemes and the impact on state finances, which is why most analysts expect a final figure well below union demands. One railway supervisors' association has suggested graded factors (2.92 for lower levels up to 4.38 for the highest), but a single uniform factor for pensioners has been the norm so far.</p>

<h2>Using the reverse calculator</h2>
<p>If a news report says "minimum pension may rise to ₹25,740", enter ₹9,000 and ₹25,740 in the reverse box above: the implied factor is 2.86. This is a quick way to check whether a headline figure is consistent with a known factor, or simply made up.</p>

<h2>Tips for reading fitment factor news</h2>
<ul>
<li>Check whether a figure is a <strong>demand</strong>, an <strong>estimate</strong> or an <strong>order</strong>. Only a Cabinet decision on pib.gov.in followed by a DoPPW/DoE order is official.</li>
<li>A higher basic does not mean the same percentage rise in take-home pension, because DR resets.</li>
<li>For pre-2016 and post-2016 pensioners the Commission may recommend different methods (the 7th CPC also offered a <a href="/pre-2016-pensioners/">notional pay-fixation option</a>). Treat any single-factor result as a first estimate.</li>
</ul>
<p>For ready-made numbers see the <a href="/pension-chart/">pension chart</a>; for the full result including additional pension and arrears, use the <a href="/">main pension calculator</a>.</p>
""",
    faqs=[
        ("Has the 8th Pay Commission fitment factor been announced?", "No. As of " + LAST_UPDATED_HUMAN + " no fitment factor has been announced. The Commission's report is expected around May 2027."),
        ("What fitment factor did the 7th Pay Commission use for pensioners?", "2.57. Pension drawn on 31.12.2015 was multiplied by 2.57 and rounded up to the next rupee, with DR restarting at zero from 1 January 2016."),
        ("Why do unions demand 3.833?", "The NC-JCM staff side has proposed a minimum pay of ₹69,000. Divided by the current minimum pay of ₹18,000, that gives 3.833. Pensioner associations have backed the same figure."),
        ("What fitment factor keeps my pension the same?", "With DR at 63%, a factor of 1.63 would leave the total unchanged if DR resets to zero. Any factor above that is a real increase."),
        ("Is 2.86 the confirmed fitment factor?", "No. 2.86 is one of several estimates in media reports. It has no official basis as of " + LAST_UPDATED_HUMAN + "."),
    ],
    related=rel("/", "/pension-chart/", "/pre-2016-pensioners/", "/family-pension-calculator/", "/how-we-calculate/", "/latest-update/"),
))

# ---------------- family pension
PAGES.append(dict(
    path="/family-pension-calculator/", crumb="Family Pension Calculator", webapp=True, calc=True, default_type="fpn", extra="family",
    title="8th Pay Commission Family Pension Calculator – Normal 30% & Enhanced 50%",
    desc="Estimate revised family pension under the 8th CPC: normal (30%) and enhanced (50%) rates, minimum ₹9,000, additional family pension at 80+, DR 63% and arrears. Estimate, not official.",
    h1="8th Pay Commission Family Pension Calculator",
    lead="For widows, widowers and other eligible family members of central government employees and pensioners. Work out your family pension from last pay if you need to, then see the estimated 8th CPC revision.",
    body=f"""
<h2>Family pension rules today (7th CPC)</h2>
<p>Family pension for central civil employees is governed by Rule 50 of the CCS (Pension) Rules, 2021. There are two rates, both calculated on the <em>last pay drawn</em> (basic pay) of the employee:</p>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Rate</th><th scope="col">Amount</th><th scope="col">Limits</th><th scope="col">When it applies</th></tr></thead><tbody>
<tr><td>Normal (ordinary)</td><td>30% of last pay</td><td>Min ₹9,000 · Max ₹75,000</td><td>Default rate; also applies after the enhanced period ends</td></tr>
<tr><td>Enhanced</td><td>50% of last pay</td><td>Min ₹9,000 · Max ₹1,25,000</td><td>For a limited period after death (see below)</td></tr>
</tbody></table></div>
<h3>How long the enhanced rate lasts</h3>
<ul>
<li><strong>Death while in service:</strong> enhanced rate for 10 years from the day after death. Since 1 October 2019 there is no minimum service requirement — the earlier condition of seven years' continuous service was removed.</li>
<li><strong>Death after retirement:</strong> enhanced rate for seven years, or until the date the deceased would have turned 67, whichever is earlier. It cannot exceed the pension that was authorised to the pensioner. DoPPW clarified in October 2025 that this applies whatever the retirement age.</li>
</ul>
<p>After the enhanced period, family pension falls to the normal 30% rate. Your Pension Payment Order (PPO) shows both amounts and the date the enhanced rate ends.</p>

<h2>Additional family pension for older family pensioners</h2>
<p>Family pensioners aged 80 and above get additional family pension on the basic family pension: 20% from 80, 30% from 85, 40% from 90, 50% from 95 and 100% from 100 years, payable from the first day of the month in which the age is reached. Dearness Relief (63% from 1 July 2026) is paid on basic family pension plus additional family pension. Enter the family pensioner's age in the calculator and it is added automatically.</p>

<h2>How the 8th CPC revision is estimated</h2>
<p>Under the 7th CPC, family pension was revised the same way as pension: the family pension being drawn was multiplied by 2.57 and DR restarted at zero. This calculator applies your chosen fitment factor to your current basic family pension, raises it to an estimated new minimum (₹9,000 × factor) if needed, and limits it to the estimated new maximum for that rate. For example, a widow drawing the minimum ₹9,000 family pension at age 70 receives ₹14,670 today with 63% DR. At a factor of 2.57 the estimated new family pension is ₹23,130; at 2.86 it is ₹25,740.</p>
<p>If you are currently drawing enhanced family pension and it is due to drop to the normal rate before the revision, run the calculator twice — once with the enhanced amount and once with the normal amount — to see both phases.</p>

<h2>Working out family pension from last pay</h2>
<p>If you do not have the PPO at hand, the helper box above calculates both rates from the employee's last basic pay under the 7th CPC (for example ₹56,100 gives ₹16,830 normal and ₹28,050 enhanced). Use the button to copy the figure into the calculator. If the employee retired or died before 2016, use the revised 7th CPC family pension shown on your latest PPO or bank statement instead, because pre-2016 amounts were already revised.</p>

<h2>Common questions from family pensioners</h2>
<p>Many family pensioners worry whether the 8th CPC covers them. The Commission's Terms of Reference include retirement benefits, and the Government has stated that pensions are within its scope; family pensions have been revised along with pensions after every past pay commission. A viral claim that pensioners would stop getting pay commission revisions under the Finance Act 2025 was declared fake by PIB Fact Check on 13 November 2025. As with all figures here, wait for the official order before relying on any amount, and never share OTPs or bank details with anyone offering to "calculate" your pension.</p>
<p>See also the <a href="/">main pension calculator</a>, the <a href="/pension-chart/">ready-reckoner chart</a> and the <a href="/latest-update/">latest update</a>.</p>
""",
    faqs=[
        ("What is the minimum family pension under the 7th CPC?", "₹9,000 per month, plus Dearness Relief (63% from 1 July 2026). The maximum is ₹75,000 at the normal rate and ₹1,25,000 at the enhanced rate."),
        ("What is the difference between normal and enhanced family pension?", "Normal family pension is 30% of the employee's last basic pay. Enhanced family pension is 50% of last pay and is paid for a limited period: 10 years after a death in service, or seven years / until the deceased would have turned 67 (whichever is earlier) after a death following retirement."),
        ("Will family pensioners get the 8th Pay Commission benefit?", "Family pensions have been revised along with pensions after every past pay commission, and pension matters are within the 8th CPC's Terms of Reference. The method and amounts will be known only after the report and Government orders."),
        ("Is additional pension given to family pensioners above 80?", "Yes. Additional family pension is 20% at 80, 30% at 85, 40% at 90, 50% at 95 and 100% at 100 years, on the basic family pension, with DR on top."),
        ("How much will ₹9,000 family pension become in the 8th CPC?", "At 2.57 it would be about ₹23,130; at 2.86, ₹25,740; at 3.0, ₹27,000. These are estimates only; no factor has been announced."),
    ],
    related=rel("/", "/basic-pension-finder/", "/pre-2016-pensioners/", "/fitment-factor-calculator/", "/pension-chart/", "/hi/"),
))

# ---------------- defence
PAGES.append(dict(
    path="/defence-pension-calculator/", crumb="Defence Pension Calculator", webapp=True, calc=True,
    title="8th Pay Commission Defence Pension Calculator – Armed Forces Pensioners",
    desc="Estimate how the 8th CPC fitment factor could change a defence (armed forces) basic pension, with DR and arrears. Notes on MSP, OROP, disability pension and SPARSH. Estimate, not official.",
    h1="8th Pay Commission Defence Pension Calculator",
    lead="A simple estimate for retired soldiers, sailors, air warriors, officers and their families: apply a fitment factor to the basic pension shown in your PPO or SPARSH account.",
    body=f"""
<h2>Before you calculate: how defence pensions differ</h2>
<p>Armed forces pensions are not governed by the CCS (Pension) Rules that apply to civilians. They are regulated by the Pension Regulations of the Army, Navy and Air Force and by orders of the Department of Ex-Servicemen Welfare (DESW), Ministry of Defence, and today most are disbursed through SPARSH. Pay commission recommendations for the forces are implemented through separate DESW orders, usually issued after the civilian orders. So treat this page as a <strong>rough estimate of the basic-pension element only</strong>.</p>
<p>Key differences to keep in mind:</p>
<ul>
<li><strong>Military Service Pay (MSP):</strong> for most ranks MSP was counted as part of the pay on which pension was calculated. The basic pension on your PPO already reflects it, so enter that figure as it is.</li>
<li><strong>One Rank One Pension (OROP):</strong> OROP revisions are separate from pay commissions and are carried out periodically by DESW orders. An 8th CPC revision and a future OROP revision could interact in ways no simple calculator can predict.</li>
<li><strong>Disability and war injury elements:</strong> disability element, war injury element and liberalised family pension are calculated under their own rules (often as a percentage tied to disability and rank). This calculator does not handle them. Enter only the service pension or ordinary family pension.</li>
<li><strong>Family pension:</strong> ordinary family pension at enhanced rate (50%) is payable for 10 years after a death in service with no upper age limit, and for seven years or till the deceased would have reached 67 after a death following retirement. The seven-year service condition for the enhanced rate was removed from 1 October 2019 (PIB, Ministry of Defence).</li>
<li><strong>Reservist, Territorial Army and DSC pensions</strong> have their own rules.</li>
</ul>

<h2>What the calculator assumes</h2>
<p>The method is the same as for civilian pensioners because the 7th CPC used the same 2.57 multiplier for the basic pension of pre-2016 armed forces pensioners, with DR restarting from zero, and the ₹9,000 minimum pension applied to them too. Additional pension for age (20% at 80, rising to 100% at 100) is added automatically; confirm on your PPO that it applies to you. DR is set to 63% from 1 July 2026, the same rate approved for all central pensioners. If you prefer, choose "Family pension" in the pension type box for ordinary family pension.</p>
<p>Example: an ex-Havildar with a basic pension of ₹25,000, aged 62, draws ₹40,750 a month today including 63% DR. At a factor of 2.57 the estimated new basic pension is ₹64,250; at 2.86 it is ₹71,500. The increase in total monthly pension is ₹23,500 and ₹30,750 respectively — before any OROP effect.</p>

<h2>Where to check your figures</h2>
<ul>
<li><strong>SPARSH portal or your PPO/e-PPO</strong> for basic pension, additional pension and the enhanced-family-pension end date.</li>
<li><strong>Your bank or Defence Pension Disbursing Office</strong> statement for DR actually credited.</li>
<li><strong>DESW orders</strong> (desw.gov.in) and PIB releases for official decisions once the 8th CPC report is accepted.</li>
</ul>

<h2>A note on misinformation</h2>
<p>Defence pensioner groups on WhatsApp often circulate unverified tables and "confirmed" multipliers. As of {LAST_UPDATED_HUMAN} the 8th CPC has not recommended anything, and no rank-wise 8th CPC pension table exists. Never share OTPs, bank details or SPARSH credentials with anyone who offers to calculate or "update" your pension. Report such messages to the cybercrime helpline 1930.</p>
<p>For full details on the factors, see the <a href="/fitment-factor-calculator/">fitment factor calculator</a>; for ready-made numbers, the <a href="/pension-chart/">pension chart</a>.</p>
""",
    faqs=[
        ("Will the 8th Pay Commission apply to armed forces pensioners?", "Past pay commissions covered defence forces personnel and pensioners, with implementation through separate Ministry of Defence (DESW) orders. The 8th CPC's specific recommendations for the forces are not known yet."),
        ("Should I include MSP when entering my basic pension?", "Enter the basic pension shown on your PPO or SPARSH. Where MSP counted for pension, it is already included in that figure."),
        ("Does this calculator include disability pension or OROP?", "No. Disability and war injury elements and OROP revisions follow separate rules. The calculator estimates only the service or ordinary family pension element."),
        ("What is the minimum defence pension under the 7th CPC?", "The 7th CPC minimum pension of ₹9,000 per month applied to armed forces pensioners as well, plus Dearness Relief."),
        ("What DR is paid to defence pensioners now?", "63% of basic pension from 1 July 2026, the same rate approved for all central government pensioners (Cabinet decision of 28 October 2026). It was 60% from 1 January 2026."),
    ],
    related=rel("/", "/family-pension-calculator/", "/da-dr-calculator/", "/fitment-factor-calculator/", "/latest-update/"),
))

# ---------------- Hindi
PAGES.append(dict(
    path="/hi/", lang="hi", crumb="8वां वेतन आयोग पेंशन कैलकुलेटर", webapp=True, calc=True,
    title="8वां वेतन आयोग पेंशन कैलकुलेटर 2026 – नई पेंशन, DR और एरियर",
    desc="केंद्रीय सरकारी पेंशनभोगियों के लिए मुफ्त 8वां वेतन आयोग पेंशन कैलकुलेटर: नई मूल पेंशन, DR, मासिक बढ़ोतरी और एरियर, हर फिटमेंट फैक्टर (1.92–3.833) पर। अनुमान, आधिकारिक नहीं।",
    h1="8वां वेतन आयोग पेंशन कैलकुलेटर",
    lead="अपनी 7वें वेतन आयोग की मूल पेंशन दर्ज करें और 8वें केंद्रीय वेतन आयोग के बाद अनुमानित नई पेंशन, कुल मासिक पेंशन, बढ़ोतरी और एरियर देखें। अपडेट: 28 अक्टूबर 2026।",
    body="""
<h2>8वें वेतन आयोग की ताज़ा स्थिति</h2>
<p>केंद्रीय मंत्रिमंडल ने 28 अक्टूबर 2025 को 8वें केंद्रीय वेतन आयोग के कार्य-क्षेत्र (Terms of Reference) को मंज़ूरी दी और 3 नवंबर 2025 को आयोग का औपचारिक गठन हुआ। इसकी अध्यक्ष न्यायमूर्ति रंजना प्रकाश देसाई हैं। आयोग को गठन से 18 महीने के भीतर सिफारिशें देनी हैं, यानी रिपोर्ट लगभग मई 2027 तक आने की उम्मीद है। आयोग ने 15 जून 2026 तक ज्ञापन (memorandum) लिए और जयपुर, चंडीगढ़, बेंगलुरु और मुंबई जैसे शहरों में कर्मचारी व पेंशनभोगी संगठनों से चर्चा की है।</p>
<p>30 अक्टूबर 2026 तक <strong>कोई फिटमेंट फैक्टर, नई पेंशन तालिका या लागू होने की तारीख घोषित नहीं हुई है</strong>। सरकार की प्रेस विज्ञप्ति में केवल यह कहा गया कि पिछले रुझान के अनुसार सिफारिशों का असर "सामान्यतः 01.01.2026 से अपेक्षित" होगा — यह निर्णय नहीं, केवल पिछली परंपरा का उल्लेख है। इसलिए यहाँ दिखाया गया हर आँकड़ा एक अनुमान है।</p>

<h2>कैलकुलेटर कैसे काम करता है</h2>
<p>7वें वेतन आयोग ने पेंशन को एक ही फिटमेंट फैक्टर (2.57) से गुणा करके अगले पूरे रुपये तक बढ़ाया था और महंगाई राहत (DR) शून्य से दोबारा शुरू हुई थी। यह कैलकुलेटर उसी तरीके को अपनाता है:</p>
<ol>
<li><strong>आज की पेंशन</strong> = मूल पेंशन + आयु के आधार पर अतिरिक्त पेंशन (80 वर्ष या अधिक होने पर) + DR (1 जुलाई 2026 से मूल व अतिरिक्त पेंशन का 63%)।</li>
<li><strong>नई मूल पेंशन</strong> = वर्तमान मूल पेंशन × फिटमेंट फैक्टर (अगले पूरे रुपये तक)। अगर यह अनुमानित नई न्यूनतम पेंशन (₹9,000 × फैक्टर) से कम हो, तो उसे न्यूनतम तक बढ़ा दिया जाता है।</li>
<li><strong>नई कुल पेंशन</strong> = नई मूल पेंशन + उसी प्रतिशत से नई अतिरिक्त पेंशन + नई पेंशन पर DR (शुरुआत में 0% माना गया)।</li>
<li><strong>एरियर</strong> = मासिक बढ़ोतरी × लागू तिथि से भुगतान शुरू होने से पहले के महीने तक के महीने।</li>
</ol>
<p>ध्यान दें: DR पहले से 63% है, इसलिए फैक्टर 1.63 होने पर कुल पेंशन लगभग उतनी ही रहेगी। उदाहरण के लिए, ₹9,000 मूल पेंशन वाले को आज DR सहित ₹14,670 मिलते हैं। 2.57 के फैक्टर पर नई पेंशन ₹23,130 होगी, यानी असली बढ़ोतरी ₹8,460 (लगभग 58%)।</p>

<h2>7वें वेतन आयोग के मौजूदा नियम</h2>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">विषय</th><th scope="col">वर्तमान नियम</th></tr></thead><tbody>
<tr><td>न्यूनतम पेंशन / पारिवारिक पेंशन</td><td>₹9,000 प्रति माह</td></tr>
<tr><td>अधिकतम पेंशन</td><td>₹1,25,000 (सर्वोच्च वेतन ₹2,50,000 का 50%)</td></tr>
<tr><td>अधिकतम पारिवारिक पेंशन</td><td>सामान्य दर ₹75,000 (30%); बढ़ी हुई दर ₹1,25,000 (50%)</td></tr>
<tr><td>आयु आधारित अतिरिक्त पेंशन</td><td>80–84: 20% · 85–89: 30% · 90–94: 40% · 95–99: 50% · 100+: 100%</td></tr>
<tr><td>महंगाई राहत (DR)</td><td>1 जुलाई 2026 से 63% (कैबिनेट निर्णय 28.10.2026, PIB विज्ञप्ति 2329485; DoPPW आदेश की प्रतीक्षा); इससे पहले 1 जनवरी 2026 से 60%</td></tr>
</tbody></table></div>

<h2>कौन-सा फिटमेंट फैक्टर चुनें?</h2>
<p>अंतिम आँकड़ा अभी किसी को नहीं पता। 7वें आयोग जैसी स्थिति देखने के लिए 2.57 चुनें; राष्ट्रीय परिषद (JCM) के कर्मचारी पक्ष और पेंशनभोगी संगठनों की माँग देखने के लिए 3.833 चुनें; बीच की स्थिति के लिए 2.86 या 3.0। मीडिया में सबसे कम अनुमान लगभग 1.92 का है, जबकि एक रेलवे संगठन ने ऊँचे वेतन स्तरों के लिए 4.38 तक की माँग की है। ये सब माँगें या अनुमान हैं, आदेश नहीं।</p>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">फैक्टर</th><th scope="col">₹9,000 बनेगा</th><th scope="col">₹20,000 बनेगा</th></tr></thead><tbody>
<tr><td>1.92</td><td>₹17,280</td><td>₹38,400</td></tr><tr><td>2.57</td><td>₹23,130</td><td>₹51,400</td></tr>
<tr><td>2.86</td><td>₹25,740</td><td>₹57,200</td></tr><tr><td>3.0</td><td>₹27,000</td><td>₹60,000</td></tr>
<tr><td>3.833</td><td>₹34,497</td><td>₹76,660</td></tr></tbody></table></div>

<h2>पारिवारिक पेंशन और रक्षा पेंशन</h2>
<p>पारिवारिक पेंशन सामान्य दर पर अंतिम वेतन का 30% और बढ़ी हुई दर पर 50% होती है। सेवा के दौरान मृत्यु होने पर बढ़ी हुई दर 10 वर्ष तक मिलती है (1 अक्टूबर 2019 से न्यूनतम सेवा की शर्त हटा दी गई है); सेवानिवृत्ति के बाद मृत्यु होने पर 7 वर्ष या मृतक की 67 वर्ष की आयु तक, जो पहले हो। कैलकुलेटर में पेंशन का प्रकार बदलकर पारिवारिक पेंशन का अनुमान देखें। सशस्त्र बलों के पेंशनभोगी अपने PPO या SPARSH में दी गई मूल पेंशन दर्ज करें; विकलांगता तत्व और OROP अलग नियमों से चलते हैं और इसमें शामिल नहीं हैं।</p>

<h2>इस अनुमान में क्या शामिल नहीं है</h2>
<ul>
<li><strong>कम्यूटेशन कटौती:</strong> पूरी मूल पेंशन दर्ज करें, कटौती के बाद मिलने वाली राशि नहीं।</li>
<li><strong>आयकर, फिक्स्ड मेडिकल अलाउंस और CGHS</strong> शामिल नहीं हैं।</li>
<li><strong>लागू होने से पहले DR में बदलाव:</strong> नई DR घोषित हो तो DR वाले बॉक्स में बदलें।</li>
<li><strong>आयोग के विशेष प्रावधान:</strong> जैसे 2016 से पहले के पेंशनभोगियों के लिए अलग तरीका या नई न्यूनतम पेंशन — आधिकारिक आदेश आने पर यह साइट अपडेट की जाएगी।</li>
</ul>
<p><strong>सावधान:</strong> कोई भी वेबसाइट, ऐप या WhatsApp संदेश अगर पेंशन "कैलकुलेट" करने के नाम पर OTP, बैंक खाता, PAN, आधार या PPO विवरण माँगे तो उसे न दें। यह कैलकुलेटर आपके ब्राउज़र में ही चलता है और कोई जानकारी कहीं नहीं भेजता। साइबर धोखाधड़ी की शिकायत 1930 पर करें।</p>
<h2>नए टूल: मूल पेंशन, 2016 से पहले के पेंशनर और DR</h2>
<ul>
<li><a href="/basic-pension-finder/">मूल पेंशन पता करें</a> — बैंक में हर महीने आने वाली रकम (DR, कम्यूटेशन कटौती और FMA घटाकर) या PPO से अपनी मूल पेंशन निकालें और सीधे कैलकुलेटर में भरें।</li>
<li><a href="/pre-2016-pensioners/">2016 से पहले रिटायर पेंशनभोगी</a> — 7वें आयोग में मिली दो तरीकों (2.57 गुणा या नोशनल वेतन का 50%) में से ज़्यादा वाली पेंशन की गणना।</li>
<li><a href="/da-dr-calculator/">DA/DR कैलकुलेटर</a> — DR बढ़ने पर मासिक बढ़ोतरी और एरियर। 1 जुलाई 2026 से 60% से 63% की आधिकारिक बढ़ोतरी पहले से भरी है।</li>
<li><a href="/how-we-calculate/">हम गणना कैसे करते हैं</a> और <a href="/changelog/">बदलाव सूची</a> — हर सूत्र, मान्यता और सरकारी स्रोत।</li>
</ul>
<p>अंग्रेज़ी में विस्तृत गाइड: <a href="/">pension calculator</a>, <a href="/fitment-factor-calculator/">fitment factor</a>, <a href="/family-pension-calculator/">family pension</a>, <a href="/pension-chart/">pension chart</a>, <a href="/latest-update/">latest update</a>।</p>
""",
    faqs=[
        ("8वें वेतन आयोग में पेंशनभोगियों का फिटमेंट फैक्टर क्या है?", "अभी घोषित नहीं हुआ है। 30 अक्टूबर 2026 तक आयोग ने रिपोर्ट नहीं दी है। 7वें आयोग ने 2.57 लागू किया था; कर्मचारी पक्ष (NC-JCM) और पेंशनभोगी संगठनों ने 3.833 की माँग की है। 1.92, 2.28 या 2.86 जैसे आँकड़े केवल अनुमान हैं।"),
        ("₹9,000 पेंशन 8वें वेतन आयोग में कितनी हो जाएगी?", "2.57 फैक्टर पर ₹23,130, 2.86 पर ₹25,740, 3.0 पर ₹27,000 और 3.833 पर ₹34,497 (अनुमान)। DR शून्य से शुरू होने की संभावना के कारण कुल पेंशन में असली बढ़ोतरी कम होगी।"),
        ("8वां वेतन आयोग पेंशनभोगियों के लिए कब लागू होगा?", "तारीख तय नहीं है। रिपोर्ट 3 नवंबर 2025 से 18 महीने में, यानी लगभग मई 2027 तक आनी है। सरकार ने कहा है कि पिछली परंपरा के अनुसार असर सामान्यतः 1 जनवरी 2026 से अपेक्षित होगा।"),
        ("क्या जनवरी 2026 से एरियर मिलेगा?", "अगर सरकार 1 जनवरी 2026 को लागू तिथि तय करती है, जैसा 7वें आयोग में 1 जनवरी 2016 को हुआ था, तो एरियर मिलेगा। यह अभी तय नहीं है। कैलकुलेटर में लागू तिथि और भुगतान का महीना दोनों बदल सकते हैं।"),
        ("80 साल से ऊपर के पेंशनभोगियों को अतिरिक्त पेंशन कितनी मिलती है?", "80 वर्ष पर 20%, 85 पर 30%, 90 पर 40%, 95 पर 50% और 100 वर्ष पर 100% अतिरिक्त पेंशन, जिस पर DR भी मिलती है।"),
        ("क्या यह कैलकुलेटर सरकारी है?", "नहीं। यह एक स्वतंत्र टूल है और भारत सरकार, DoPPW, CPAO या 8वें वेतन आयोग से जुड़ा नहीं है। सभी परिणाम अनुमान हैं।"),
    ],
    related=[("/", "8th Pay Commission Pension Calculator (English)", "पूरा कैलकुलेटर अंग्रेज़ी में"),
             ("/family-pension-calculator/", "Family Pension Calculator", "पारिवारिक पेंशन 30% / 50%"),
             ("/pension-chart/", "8th CPC Pension Chart", "₹9,000 से ₹1,25,000 तक तालिका"),
             ("/basic-pension-finder/", "Basic Pension Finder", "बैंक में आई रकम या PPO से मूल पेंशन"),
             ("/pre-2016-pensioners/", "Pre-2016 Pensioners", "2.57× बनाम नोशनल वेतन"),
             ("/da-dr-calculator/", "DA/DR Calculator", "DR बढ़ोतरी और एरियर"),
             ("/latest-update/", "Latest Update", "तारीख के साथ ताज़ा स्थिति")],
))

# ---------------- chart
PAGES.append(dict(
    path="/pension-chart/", crumb="Pension Chart",
    title="8th Pay Commission Pension Chart – ₹9,000 to ₹1,25,000 at Each Fitment Factor",
    desc="Ready-reckoner 8th CPC pension chart: revised basic pension for 7th CPC pensions from ₹9,000 to ₹1,25,000 at fitment factors 1.92, 2.28, 2.57, 2.86, 3.0 and 3.833. Estimate, not official.",
    h1="8th Pay Commission Pension Chart (Ready Reckoner)",
    lead="Find your current 7th CPC basic pension in the left column and read across to see the estimated 8th CPC basic pension at six fitment factors.",
    body=f"""
{CHART_TABLE}
<p class="fine">Values = 7th CPC basic pension × fitment factor, rounded up to the next rupee. Additional pension for age and Dearness Relief are not included. ₹1,25,000 is the current maximum pension (50% of the highest pay of ₹2,50,000).</p>

<h2>How to read this chart</h2>
<p>Each row starts with a 7th CPC basic pension — the figure on your PPO before Dearness Relief and before any commutation deduction. Each column applies one fitment factor. The cell where they meet is the estimated new basic pension. For example, a pensioner on ₹30,000 would get ₹77,100 at 2.57, ₹85,800 at 2.86 and ₹1,14,990 at 3.833.</p>
<p>If your pension falls between two rows, use the <a href="/">calculator</a> for an exact figure, or multiply your basic pension by the factor yourself and round up to the next rupee.</p>

<h2>Why the jump looks bigger than it is</h2>
<p>The chart shows basic pension only. Today you also receive Dearness Relief at 63% of basic pension (from 1 July 2026). When the new pension starts, DR is expected to restart from zero, as it did after the 6th and 7th pay commissions. So compare the new basic pension with your <strong>current basic pension × 1.63</strong>, not with your basic pension alone:</p>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Basic pension</th><th scope="col">Total today (with 63% DR)</th><th scope="col">New basic at 2.57</th><th scope="col">Real monthly gain</th></tr></thead><tbody>
<tr><td>₹9,000</td><td>₹14,670</td><td>₹23,130</td><td>₹8,460</td></tr>
<tr><td>₹20,000</td><td>₹32,600</td><td>₹51,400</td><td>₹18,800</td></tr>
<tr><td>₹50,000</td><td>₹81,500</td><td>₹1,28,500</td><td>₹47,000</td></tr>
<tr><td>₹1,00,000</td><td>₹1,63,000</td><td>₹2,57,000</td><td>₹94,000</td></tr>
</tbody></table></div>

<h2>Pensioners aged 80 and above</h2>
<p>If you get additional pension for age, it is calculated as a percentage of the basic pension, so it rises in the same proportion. At 80–84 years, add 20% to the figure in the chart; at 85–89, 30%; at 90–94, 40%; at 95–99, 50%; and at 100 or more, 100%. For instance, an 86-year-old on ₹20,000 basic would have an estimated new basic of ₹51,400 at 2.57 plus 30% additional pension (₹15,420), a total of ₹66,820 before DR.</p>

<h2>Family pensioners</h2>
<p>The same chart works for family pension: find your basic family pension in the left column. The current maximum is ₹75,000 at the normal rate and ₹1,25,000 at the enhanced rate. The <a href="/family-pension-calculator/">family pension calculator</a> also works out the amount from the employee's last pay.</p>

<h2>About the fitment factors in the columns</h2>
<p>None of the six factors is official. 2.57 is what the 7th CPC used in 2016. 3.833 is the factor demanded by the staff side of the National Council (JCM) and pensioner associations, based on their proposed minimum pay of ₹69,000. 1.92, 2.28, 2.86 and 3.0 are estimates that have circulated in the media. The final factor — and whether a single factor will apply to everyone — will be known only after the Commission reports (expected around May 2027) and the Government accepts the recommendations. See the <a href="/fitment-factor-calculator/">fitment factor calculator</a> for details.</p>
<p>When an official factor is announced, this chart will show it as an extra column automatically.</p>
""",
    faqs=[
        ("What will ₹9,000 pension be after the 8th Pay Commission?", "Estimated new basic pension: ₹17,280 at 1.92, ₹20,520 at 2.28, ₹23,130 at 2.57, ₹25,740 at 2.86, ₹27,000 at 3.0 and ₹34,497 at 3.833. No factor is official yet."),
        ("Does the chart include DR?", "No. It shows the new basic pension only. DR is expected to restart from 0% on the revised pension."),
        ("Is the maximum pension also going to increase?", "The current maximum of ₹1,25,000 is 50% of the highest pay. If the highest pay is revised, the maximum would normally change with it, but the 8th CPC has not recommended anything yet."),
        ("Can I use this chart for family pension?", "Yes. Look up your basic family pension in the left column. The calculator on the family pension page gives a more detailed result."),
    ],
    related=rel("/", "/basic-pension-finder/", "/fitment-factor-calculator/", "/family-pension-calculator/", "/hi/"),
))

# ---------------- latest update
PAGES.append(dict(
    path="/latest-update/", crumb="Latest Update",
    title="8th Pay Commission Latest Update for Pensioners – Status as of 30 October 2026",
    desc="8th Pay Commission timeline for pensioners as of 30 October 2026: DA/DR raised to 63% from 1 July 2026 (Cabinet 28 Oct), ToR, consultations, fitment factor status.",
    h1="8th Pay Commission Latest Update for Pensioners",
    lead="Status as of " + LAST_UPDATED_HUMAN + ". Each entry is dated and labelled Official (order or Government release), Demand (union or association) or Estimate (calculation, not a decision).",
    body="""
<h2>At a glance</h2>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Item</th><th scope="col">Position on 30 Oct 2026</th><th scope="col">Label</th></tr></thead><tbody>
<tr><td>Commission constituted</td><td>3 November 2025</td><td>Official</td></tr>
<tr><td>Chairperson</td><td>Justice Ranjana Prakash Desai; Prof. Pulak Ghosh (Member, part-time); Shri Pankaj Jain (Member-Secretary)</td><td>Official</td></tr>
<tr><td>Report due</td><td>Within 18 months of constitution — about May 2027</td><td>Official deadline / estimated date</td></tr>
<tr><td>Fitment factor</td><td>Not announced</td><td>Official</td></tr>
<tr><td>Date of effect</td><td>Not decided; "would normally be expected from 01.01.2026" (past practice)</td><td>Official statement, not a decision</td></tr>
<tr><td>Dearness Relief</td><td>63% from 1 July 2026 (Cabinet decision 28 October 2026; DoPPW order awaited)</td><td>Official</td></tr>
<tr><td>DR from 1 January 2026</td><td>60% (previous rate)</td><td>Official</td></tr>
<tr><td>Fitment factor demanded</td><td>3.833 (NC-JCM staff side; pensioner associations)</td><td>Demand</td></tr>
</tbody></table></div>

<h2>Timeline</h2>
<ol class="timeline">
<li><time datetime="2025-01">January 2025</time>The Government announces that the 8th Central Pay Commission will be set up. <em>Official</em></li>
<li><time datetime="2025-10-28">28 October 2025</time>Union Cabinet approves the Terms of Reference. The Commission is a temporary body with a Chairperson, one part-time Member and a Member-Secretary, and must report within 18 months. It must keep in view fiscal prudence, resources for development and welfare, the unfunded cost of non-contributory pension schemes, the impact on state finances, and pay in CPSUs and the private sector. PIB adds that the effect "would normally be expected from 01.01.2026". <em>Official</em></li>
<li><time datetime="2025-11-03">3 November 2025</time>Commission constituted by Government Resolution, chaired by Justice Ranjana Prakash Desai. <em>Official</em></li>
<li><time datetime="2025-11-13">13 November 2025</time>PIB Fact Check marks as fake a viral claim that, under the Finance Act 2025, retired employees would no longer get DA hikes or pay commission revisions. <em>Official</em></li>
<li><time datetime="2025-12">December 2025</time>Parliament is told there is no proposal under consideration to merge DA with basic pay. <em>Official</em></li>
<li><time datetime="2026-04-18">18 April 2026</time>Cabinet approves a 2% increase in DA and DR, from 58% to 60% with effect from 1 January 2026, benefiting about 68.27 lakh pensioners. DoPPW issues the DR order on 24 April 2026 (OM No. 42/02/2024-P&amp;PW(D)/E-9475); DR is paid on basic pension including additional pension. <em>Official</em></li>
<li><time datetime="2026-05-19">May 2026</time>Consultations with employee bodies under way. The Indian Railway Technical Supervisors' Association proposes graded fitment factors from 2.92 (Levels 1–5) to 4.38 (Levels 17–18). <em>Demand</em></li>
<li><time datetime="2026-06-15">15 June 2026</time>Last date for memorandums to the Commission (extended). <em>Official</em></li>
<li><time datetime="2026-08">July–August 2026</time>Replying in Parliament, the Government says the Commission has not yet submitted recommendations, so the fitment factor and implementation date cannot be stated. <em>Official (as reported)</em></li>
<li><time datetime="2026-09">August–September 2026</time>Commission visits Jaipur (31 August–1 September) and Chandigarh (16–18 September). NC-JCM staff side's demand of ₹69,000 minimum pay and a 3.833 factor is widely reported. <em>Official visits / Demand</em></li>
<li><time datetime="2026-09-30">30 September 2026</time>Labour Bureau releases CPI-IW for August 2026 at 154.4. <em>Official</em></li>
<li><time datetime="2026-10-08">7–8 October 2026</time>Commission's consultations in Bengaluru. A pensioners' association seeks a 3.833 factor and higher annual increments. <em>Official visit / Demand</em></li>
<li><time datetime="2026-10-23">22–23 October 2026</time>Commission's consultations in Mumbai. No further visits had been listed for November–December when checked on 23 October. <em>Official</em></li>
<li><time datetime="2026-10-28">28 October 2026</time>Union Cabinet approves a 3% increase in DA and DR, from 60% to 63% with effect from 1 July 2026, benefiting about 48.54 lakh employees and 68.71 lakh pensioners at a cost of Rs 10,016.10 crore a year (<a href="https://pib.gov.in/PressReleasePage.aspx?PRID=2329485" rel="noopener">PIB release ID 2329485</a>). Still no fitment factor, pension matrix or date of effect for the 8th CPC. <em>Official</em></li>
<li><time datetime="2026-10-30">30 October 2026</time>This site updated to DR 63%. The DoPPW office memorandum implementing the increase for pensioners had not been published on doppw.gov.in or pensionersportal.gov.in as of 30 October 2026; banks pay the new rate once it is issued. Arrears from July are typically paid with the first pension at the new rate. See the <a href="/da-dr-calculator/">DA/DR calculator</a> for your increase and arrears. <em>Official position</em></li>
</ol>

<h2>What pensioners should expect next</h2>
<p>The Commission may send interim reports if it chooses, but its final report is due around May 2027. Past experience suggests that implementation follows a few months after the report: the 7th CPC reported in November 2015, the Cabinet approved it in June 2016, and revised pensions with arrears from 1 January 2016 were paid later that year. Meanwhile, Dearness Relief continues to be revised twice a year under the 7th CPC formula, so the July 2026 increase to 63% and the January 2027 instalment still matter for your current pension and for any arrears calculation.</p>

<h2>How to verify an announcement</h2>
<ul>
<li>A genuine decision first appears as a Cabinet release on <strong>pib.gov.in</strong>.</li>
<li>For pensioners, the <strong>Department of Pension &amp; Pensioners' Welfare</strong> (doppw.gov.in) then issues an office memorandum; for armed forces pensioners, the Department of Ex-Servicemen Welfare.</li>
<li>The Commission's own notices are on <strong>8cpc.gov.in</strong>.</li>
<li>Screenshots, YouTube thumbnails and forwarded PDFs without a link to these sites are not orders.</li>
</ul>

<h2>Sources</h2>
<ul>
<li>PIB, Cabinet approves Terms of Reference of 8th CPC, 28.10.2025 — pib.gov.in (PRID 2183289)</li>
<li>PIB / PM India, Cabinet approves additional DA and DR w.e.f. 01.01.2026, 18.04.2026</li>
<li>PIB release ID 2329485, 28.10.2026 — Cabinet approves DA/DR from 60% to 63% w.e.f. 01.07.2026</li>
<li>DoPPW OM No. 42/02/2024-P&amp;PW(D)/E-9475 dated 24.04.2026 (DR 60% from 01.01.2026)</li>
<li>8cpc.gov.in — composition and notices of city visits</li>
<li>CCS (Pension) Rules, 2021 — pensionersportal.gov.in</li>
<li>Labour Bureau CPI-IW press release, 30.09.2026</li>
<li>Reported demands: Mint, Economic Times, Financial Express (May–October 2026)</li>
</ul>
<p>Use the <a href="/">pension calculator</a> to see what any scenario means for you.</p>
""",
    faqs=[
        ("Has the 8th Pay Commission submitted its report?", "No. As of 30 October 2026 the report has not been submitted. It is due within 18 months of 3 November 2025, around May 2027."),
        ("What is the current DR for central government pensioners?", "63% of basic pension (including additional pension) from 1 July 2026, approved by the Cabinet on 28 October 2026. It was 60% from 1 January 2026."),
        ("Has the July 2026 DA/DR been announced?", "Yes. On 28 October 2026 the Union Cabinet approved DA and DR of 63% from 1 July 2026, up from 60% (PIB release ID 2329485). The DoPPW order for pensioners was awaited as of 30 October 2026."),
        ("Who heads the 8th Pay Commission?", "Justice Ranjana Prakash Desai is the Chairperson. Prof. Pulak Ghosh is the part-time Member and Shri Pankaj Jain is the Member-Secretary."),
    ],
    related=rel("/", "/da-dr-calculator/", "/changelog/", "/fitment-factor-calculator/", "/pension-chart/", "/hi/"),
))

# ---------------- about
PAGES.append(dict(
    path="/about/", crumb="About",
    title="About – 8th Pay Commission Pension Calculator",
    desc="Who runs this independent 8th Pay Commission pension calculator, how the numbers are calculated, where the data comes from and how it is kept up to date.",
    h1="About this calculator",
    lead="An independent, free tool that helps central government pensioners and family pensioners understand what the 8th Pay Commission could mean for them.",
    body=f"""
<h2>Why this site exists</h2>
<p>Every pay commission brings a flood of headlines, WhatsApp forwards and YouTube thumbnails promising a "confirmed" new pension. Most of them mix up demands, estimates and actual orders, and very few explain the arithmetic. Pensioners — many of them in their seventies, eighties and nineties — deserve a clear, honest way to see what different outcomes would mean for their own monthly pension, without signing up, downloading an app or sharing personal details.</p>
<p>This site was built by Manish, an independent developer in India, to do exactly that: a fast calculator that runs entirely in your browser, written in plain English and Hindi, with every assumption shown on screen.</p>

<h2>What we do</h2>
<ul>
<li><strong>Calculate transparently.</strong> Each result shows the step-by-step formula, so you can check it with a pen and paper.</li>
<li><strong>Label everything.</strong> Every result is marked "Estimate — not official". Figures on the <a href="/latest-update/">latest update</a> page are labelled Official, Demand or Estimate.</li>
<li><strong>Use primary sources.</strong> Current rules — the ₹9,000 minimum pension, the ₹1,25,000 maximum, family pension rates, additional pension for age and the 63% Dearness Relief — are taken from the CCS (Pension) Rules, 2021, DoPPW office memoranda and Cabinet releases on pib.gov.in.</li>
<li><strong>Update quickly.</strong> All official numbers sit in a single settings block in the site's code, so when the Government announces the fitment factor or a new DR rate, the calculator can be updated within minutes. The date of the last update is shown at the top of every page.</li>
</ul>

<h2>What we don't do</h2>
<ul>
<li>We are <strong>not</strong> a government website and are not connected with the Government of India, DoPPW, CPAO, the Department of Ex-Servicemen Welfare, any bank or the 8th Central Pay Commission.</li>
<li>We do not ask for your name, PPO number, bank account, Aadhaar, PAN or OTP — ever. Anyone who asks for these in our name is a fraud.</li>
<li>We do not store the numbers you type. The calculation happens on your own device.</li>
<li>We do not predict the final fitment factor. We let you test scenarios.</li>
</ul>

<h2>How the calculation works</h2>
<p>The method follows the way the 7th Pay Commission revised pensions in 2016: your basic pension is multiplied by a fitment factor and rounded up to the next rupee; additional pension for age is applied at the same percentage; and Dearness Relief is assumed to restart at zero on the new pension. Arrears are estimated as the monthly increase multiplied by the number of months between the assumed date of effect and the month the revised pension is first paid. The full list of assumptions is shown under every result and explained on the <a href="/">calculator page</a>.</p>
<p>This approach is a reasonable first estimate, but the 8th CPC may recommend something different — for example a separate method for older pensioners, a new minimum pension or changes to the age slabs. When that happens, the calculator will be changed to match the official orders.</p>

<h2>Corrections</h2>
<p>If you spot a mistake — a wrong rule, a broken calculation or an outdated date — please write to us through the <a href="/contact/">contact page</a> with a link to the official order if you have one. Verified corrections are made promptly and the "last updated" date is changed.</p>

<h2>Accessibility and languages</h2>
<p>The site is designed to work on low-cost phones and slow connections: no external fonts, only a lightweight analytics tag and no heavy images. Text can be enlarged with your browser's zoom, form fields have clear labels, and the whole interface can be switched to Hindi with one tap. A full Hindi guide is available at <a href="/hi/">8वां वेतन आयोग पेंशन कैलकुलेटर</a>.</p>
<p>Data last updated: {LAST_UPDATED_HUMAN}.</p>
""",
    faqs=[
        ("Is this a government website?", "No. It is an independent website run by a private individual and is not affiliated with any government body."),
        ("Is the calculator free?", "Yes. It is free to use and needs no registration."),
        ("How often is the data updated?", "Whenever a relevant official order or announcement appears, such as a DR instalment or 8th CPC decision. The last update date is shown on every page."),
    ],
    related=rel("/", "/how-we-calculate/", "/changelog/", "/latest-update/", "/hi/"),
))

# ---------------- privacy
PAGES.append(dict(
    path="/privacy/", crumb="Privacy Policy",
    title="Privacy Policy – 8th Pay Commission Pension Calculator",
    desc="Privacy policy: the pension calculator runs in your browser, stores no personal data, uses only Google Analytics cookies for visitor counts and explains what changes if advertising is enabled.",
    h1="Privacy Policy",
    lead="Short version: the numbers you type stay on your device. We do not collect your name, PPO number, bank details or any other personal information.",
    body=f"""
<p>Effective date: {LAST_UPDATED_HUMAN}. This policy explains what information is and is not processed when you use this website (the "Site").</p>

<h2>1. Information you enter in the calculator</h2>
<p>The calculator runs entirely in your web browser using JavaScript. The values you enter — basic pension, age, pension type, fitment factor, DR and months — are processed on your own device and are <strong>not sent to our server</strong> or to anyone else. When you press "Calculate", the values are added to the address bar of your browser (for example <code>?bp=20000&amp;ff=2.57</code>) so that you can bookmark or share the result. That link is only shared if you choose to share it.</p>

<h2>2. Information stored on your device</h2>
<p>If you switch between English and Hindi, your language choice is saved in your browser's local storage so the Site remembers it next time. It contains only the word "en" or "hi". You can clear it at any time from your browser settings. Apart from the Google Analytics cookies described in section 4, we do not set tracking cookies.</p>

<h2>3. Server logs</h2>
<p>The Site is hosted on Vercel. Like every web host, Vercel may automatically process technical information such as your IP address, browser type, the page requested and the time of the request, for security, abuse prevention and to deliver the Site. This processing is governed by Vercel's own privacy policy. We do not use these logs to identify individual visitors.</p>

<h2>4. Analytics</h2>
<p>The Site uses Google Analytics 4 to understand, in aggregate, how many people visit and which pages and calculators are useful. Google Analytics sets first-party cookies (such as <code>_ga</code>) and collects information like pages viewed, approximate location (city/country), device and browser type, and how the visitor arrived. It does <strong>not</strong> receive the values you type into the calculator. IP addresses are not logged or stored by Google Analytics 4. You can block it with your browser's cookie settings, a content blocker, or the <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">Google Analytics opt-out add-on</a>. See <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">how Google uses data from sites that use its services</a>.</p>

<h2>5. Advertising</h2>
<p>The Site may in future display advertisements through Google AdSense to cover running costs. If that happens:</p>
<ul>
<li>Google and its partners may use cookies or similar technologies to serve ads based on your previous visits to this and other websites.</li>
<li>You can opt out of personalised advertising at Google's Ads Settings (adssettings.google.com) or at www.aboutads.info.</li>
<li>This policy will be updated, and a consent notice shown where required, before ads are enabled.</li>
</ul>

<h2>6. Sharing buttons</h2>
<p>The "Share on WhatsApp" button simply opens WhatsApp (wa.me) with a pre-filled message containing your result link. Nothing is sent until you choose to send it in WhatsApp, and WhatsApp's own privacy policy then applies. The "Download result" button creates a text file on your device; nothing is uploaded.</p>

<h2>7. Email</h2>
<p>If you contact us by email, we receive your email address and whatever you write. We use it only to reply and to fix any problem you report, and we do not sell or share it. Please do not send PPO numbers, bank details, Aadhaar or other sensitive documents — we do not need them.</p>

<h2>8. Children</h2>
<p>The Site is meant for adults and does not knowingly collect information from children.</p>

<h2>9. Security</h2>
<p>The Site is served over HTTPS with security headers that restrict which scripts can run. Since no personal data is collected, there is very little that could be exposed. Beware of imitation websites or apps that ask for OTPs or bank details in the name of an "8th Pay Commission calculator"; report them to the national cybercrime helpline 1930 or cybercrime.gov.in.</p>

<h2>10. Your rights</h2>
<p>Because we do not keep personal data from the calculator, there is usually nothing to access or delete. If you have emailed us and want that correspondence deleted, write to us and we will do so. Indian users have rights under the Digital Personal Data Protection Act, 2023, and we will honour any valid request.</p>

<h2>11. Changes</h2>
<p>We may update this policy, for example if advertising or analytics are added. The effective date at the top will change when we do.</p>

<h2>12. Contact</h2>
<p>Questions about privacy: see the <a href="/contact/">contact page</a>.</p>
""",
    faqs=[
        ("Do you store the pension amount I enter?", "No. The calculation runs in your browser and the numbers are not sent to our server."),
        ("Do you use cookies?", "Only Google Analytics cookies (such as _ga), used for aggregate visitor counts; the amounts you type are never sent to it. Your language choice is saved in your browser's local storage. If ads are added in future, this policy will be updated first."),
        ("Will you ever ask for my PPO or bank details?", "Never. Anyone asking for PPO, bank, Aadhaar, PAN or OTP details in our name is a fraud."),
    ],
    related=rel("/", "/hi/"),
))

# ---------------- disclaimer
PAGES.append(dict(
    path="/disclaimer/", crumb="Disclaimer",
    title="Disclaimer – Not an Official Government Website",
    desc="Disclaimer: this 8th Pay Commission pension calculator is independent, not affiliated with the Government of India, and all results are estimates for information only.",
    h1="Disclaimer",
    lead="Please read this before relying on any figure from this website.",
    body=f"""
<h2>Not a government website</h2>
<p>This website is an independent, privately run information tool. It is <strong>not affiliated with, endorsed by, sponsored by or part of</strong> the Government of India, the Ministry of Finance, the Department of Expenditure, the Department of Pension &amp; Pensioners' Welfare (DoPPW), the Central Pension Accounting Office (CPAO), the Ministry of Defence or the Department of Ex-Servicemen Welfare, SPARSH, any Pension Disbursing Authority or bank, or the 8th Central Pay Commission. Names of government bodies are used only to describe the rules and announcements we refer to.</p>

<h2>All results are estimates</h2>
<p>As of {LAST_UPDATED_HUMAN}, the 8th Central Pay Commission has not submitted its report, and the Government has not announced a fitment factor, a revised pension structure, a new minimum or maximum pension, or a date of effect. Every figure produced by the calculators, charts and examples on this website is therefore a <strong>hypothetical estimate</strong> based on:</p>
<ul>
<li>the fitment factor you select, none of which is official;</li>
<li>the method used by the 7th Pay Commission in 2016, which the 8th CPC may or may not follow;</li>
<li>an assumed new minimum and maximum pension (current limit × fitment factor);</li>
<li>an assumption that Dearness Relief restarts at 0% on the revised pension;</li>
<li>an assumed date of effect (1 January 2026 by default) and a payment month that you choose;</li>
<li>the current DR rate entered, applied for the whole arrears period.</li>
</ul>
<p>Your actual revised pension, family pension and arrears will be decided only by official Government orders and fixed by your Pension Disbursing Authority. They may differ substantially from any estimate here.</p>

<h2>Not financial, legal or tax advice</h2>
<p>Nothing on this website is financial, legal, tax or investment advice. Do not make financial commitments — such as loans, purchases or investment decisions — on the basis of estimated pension or arrears. For your individual case, consult your PPO, your Pension Disbursing Authority, your bank's pension cell, the DoPPW (doppw.gov.in), CPAO or, for armed forces pensioners, SPARSH and DESW.</p>

<h2>Accuracy of information</h2>
<p>We take care to base current rules on official sources (CCS (Pension) Rules, 2021, DoPPW orders and PIB releases) and to date every update. However, rules change, orders are amended and errors can happen. We make no warranty that the information is complete, accurate or up to date at the moment you read it. Information about demands by unions and associations is taken from published news reports and is labelled as such.</p>

<h2>Defence, railway and other pensioners</h2>
<p>The calculation follows the general method for central civil pensioners. Armed forces, railway, autonomous body, state government and bank pensioners may be governed by different rules, orders or timelines. In particular, disability and war injury elements, OROP revisions and state government pay commissions are not covered.</p>

<h2>External links</h2>
<p>Links to government and news websites are provided for reference. We are not responsible for their content or availability.</p>

<h2>Limitation of liability</h2>
<p>To the maximum extent permitted by law, the owner of this website is not liable for any loss or damage arising from the use of, or reliance on, any information or estimate on this website. By using the website you accept this disclaimer.</p>

<h2>Beware of fraud</h2>
<p>This website never asks for an OTP, bank details, PAN, Aadhaar, PPO number or any payment. There is no official "8th Pay Commission calculator" app. If anyone asks for such details to "calculate" or "activate" a revised pension, it is fraud — report it to 1930 or cybercrime.gov.in.</p>
<p>See also our <a href="/privacy/">privacy policy</a> and <a href="/about/">about page</a>.</p>
""",
    faqs=[
        ("Is the 8th Pay Commission fitment factor on this site official?", "No. None of the fitment factors is official as of " + LAST_UPDATED_HUMAN + ". They are scenarios for estimation."),
        ("Can I rely on the arrears estimate?", "Only as a rough guide. Actual arrears depend on the official date of effect, the revised pension and the DR actually drawn each month."),
        ("Who decides my actual revised pension?", "Your Pension Disbursing Authority, following orders issued by the Government after it accepts the Pay Commission's recommendations."),
    ],
    related=rel("/", "/latest-update/"),
))

# ---------------- contact
PAGES.append(dict(
    path="/contact/", crumb="Contact",
    title="Contact – 8th Pay Commission Pension Calculator",
    desc="Contact the team behind the independent 8th Pay Commission pension calculator to report an error, suggest a feature or ask about the site. We cannot handle individual pension cases.",
    h1="Contact us",
    lead="Found an error, have a suggestion, or want to tell us about a new official order? We'd like to hear from you.",
    body=f"""
<h2>Email</h2>
<p class="note">Write to <a href="mailto:{CONTACT_EMAIL}?subject=8th%20CPC%20Pension%20Calculator">{CONTACT_EMAIL}</a>. We usually reply within a few working days.</p>
<!-- OWNER: this address is built from DOMAIN / CONTACT_EMAIL at the top of tools/build.py. -->

<h2>What we can help with</h2>
<ul>
<li><strong>Corrections:</strong> a wrong rule, rate or date on the site. Please include a link to the official order or PIB release, if you have it, so we can verify and fix it quickly.</li>
<li><strong>Calculation problems:</strong> if a result looks wrong, use the "Copy share link" button under your result and paste the link in your email. It contains the exact inputs (and nothing personal), so we can reproduce the calculation.</li>
<li><strong>Suggestions:</strong> features that would make the calculator more useful — for example another language, a different chart range or a new pensioner category.</li>
<li><strong>Accessibility issues:</strong> anything that makes the site hard to read or use on your phone, with a screen reader or at a larger text size.</li>
<li><strong>Media and partnership queries.</strong></li>
</ul>

<h2>What we cannot help with</h2>
<p>We are an independent website, not a government office. We cannot:</p>
<ul>
<li>check, revise, release or speed up anyone's pension, family pension or arrears;</li>
<li>access PPOs, bank records, SPARSH or CPAO accounts;</li>
<li>tell you the final 8th Pay Commission fitment factor before it is officially announced.</li>
</ul>
<p><strong>Please do not send</strong> PPO numbers, bank account details, Aadhaar, PAN, life certificates, OTPs or copies of personal documents. We do not need them and will delete them.</p>

<h2>Where to go for official help</h2>
<ul>
<li><strong>Civil pensioners:</strong> your Pension Disbursing Authority (usually your bank's pension branch), the Central Pension Accounting Office (cpao.nic.in) and the Department of Pension &amp; Pensioners' Welfare (doppw.gov.in). Grievances can be lodged on CPENGRAMS through pgportal.gov.in.</li>
<li><strong>Armed forces pensioners:</strong> the SPARSH portal and helpline, your Defence Pension Disbursing Office, and the Department of Ex-Servicemen Welfare (desw.gov.in).</li>
<li><strong>Family pensioners:</strong> the same authority that pays the family pension, as shown on your PPO.</li>
<li><strong>Fraud:</strong> if someone has asked for your OTP or bank details in the name of a pension revision, call the national cybercrime helpline <strong>1930</strong> or report at cybercrime.gov.in immediately.</li>
</ul>

<h2>Our commitment</h2>
<p>Every correction we receive is checked against official sources. If it is right, we fix the site and change the "last updated" date shown at the top of every page. If we disagree, we will explain why. Your email address is used only to reply to you; see our <a href="/privacy/">privacy policy</a>.</p>

<h2>Languages and response times</h2>
<p>You can write to us in English or Hindi. We read every message, but because the site is run by one person, replies can take a few working days — longer in the busy weeks after a major announcement such as a DR instalment or the 8th CPC report. Corrections that affect the calculation are always handled first.</p>

<h2>Tips for a useful report</h2>
<ul>
<li>Name the page (for example "Family pension calculator") and the device you used (phone or computer, and browser).</li>
<li>Say what you expected to see and what you actually saw.</li>
<li>For a rule or rate, quote the order number and date, such as "DoPPW OM dated 24.04.2026".</li>
<li>A screenshot of the result section is helpful, but crop out anything personal.</li>
</ul>

<h2>Before you write</h2>
<p>Many common questions are already answered on the site. The <a href="/">pension calculator</a> page explains the method and assumptions; the <a href="/fitment-factor-calculator/">fitment factor page</a> explains where each number comes from; the <a href="/family-pension-calculator/">family pension page</a> covers normal and enhanced rates; and the <a href="/latest-update/">latest update</a> page gives the dated status of the 8th Pay Commission. हिंदी में जानकारी के लिए <a href="/hi/">यहाँ देखें</a>।</p>
""",
    faqs=[
        ("Can you check my pension or arrears?", "No. We are an independent website and cannot access pension records. Contact your Pension Disbursing Authority, CPAO or SPARSH."),
        ("How do I report a mistake on the site?", "Email us with the page, what is wrong and, ideally, a link to the official order. Include your result's share link for calculation issues."),
        ("Is there a phone number?", "No. To keep the site free and independent we handle queries by email only."),
    ],
    related=rel("/", "/latest-update/"),
))



# ------------------------------------------------------------------ extra calculators (added 28 Oct 2026)
def fld(lang, fid, lbl, hint=None, control="", full=False, wrap_id=None, hidden=False):
    attrs = (' class="full"' if full else "") + (f' id="{wrap_id}"' if wrap_id else "") + (" hidden" if hidden else "")
    h = f'<span class="hint" data-i18n="{hint}">{T(lang, hint)}</span>' if hint else ""
    return f'<div{attrs}><label for="{fid}"><span data-i18n="{lbl}">{T(lang, lbl)}</span>{h}</label>{control}</div>'


def num_input(fid, ph, mn=0, mx=500000, step="1", value=""):
    v = f' value="{value}"' if value != "" else ""
    return f'<input id="{fid}" type="number" inputmode="decimal" min="{mn}" max="{mx}" step="{step}" placeholder="{ph}"{v}>'


def type_select(lang, fid):
    return (f'<select id="{fid}"><option value="sup" data-i18n="opt_sup">{T(lang, "opt_sup")}</option>'
            f'<option value="fpn" data-i18n="opt_fpn">{T(lang, "opt_fpn")}</option>'
            f'<option value="fpe" data-i18n="opt_fpe">{T(lang, "opt_fpe")}</option></select>')


def finder_widget(lang="en"):
    modes = "".join(f'<option value="{v}" data-i18n="{k}">{T(lang, k)}</option>' for v, k in
                    [("credit", "bf_mode_credit"), ("ppo7", "bf_mode_ppo7"), ("ppo6", "bf_mode_ppo6"), ("lastpay", "bf_mode_lastpay")])
    comm = "".join(f'<option value="{v}" data-i18n="{k}">{T(lang, k)}</option>' for v, k in
                   [("none", "bf_comm_none"), ("amount", "bf_comm_amt"), ("pct", "bf_comm_pct")])
    return f'''<section class="card" id="calc" aria-labelledby="bfTitle">
<h2 id="bfTitle" data-i18n="bf_title">{T(lang, "bf_title")}</h2>
<div class="grid">
{fld(lang, "bfMode", "bf_lbl_mode", control=f'<select id="bfMode">{modes}</select>', full=True)}
{fld(lang, "bfType", "lbl_type", control=type_select(lang, "bfType"))}
{fld(lang, "bfAge", "lbl_age", "hint_age", num_input("bfAge", "e.g. 72", 18, 120))}
</div>
<div class="grid" id="bfWrap_credit">
{fld(lang, "bfCredit", "bf_lbl_credit", "bf_hint_credit", num_input("bfCredit", "e.g. 25000", 1000, 500000), full=True)}
{fld(lang, "bfDR", "bf_lbl_dr", "bf_hint_dr", num_input("bfDR", "63", 0, 200, "0.01", 63))}
{fld(lang, "bfCommMode", "bf_lbl_comm", control=f'<select id="bfCommMode">{comm}</select>')}
{fld(lang, "bfCommVal", "bf_lbl_commval", "bf_hint_commval", num_input("bfCommVal", "e.g. 8000 or 40", 0, 200000, "0.01"), wrap_id="bfCommValWrap", hidden=True)}
{fld(lang, "bfOther", "bf_lbl_other", "bf_hint_other", num_input("bfOther", "0", 0, 200000))}
<div class="full"><label class="check" for="bfFma"><input id="bfFma" type="checkbox"><span><span data-i18n="bf_lbl_fma">{T(lang, "bf_lbl_fma")}</span><span class="hint" data-i18n="bf_hint_fma">{T(lang, "bf_hint_fma")}</span></span></label></div>
</div>
<div class="grid" id="bfWrap_ppo7" hidden>{fld(lang, "bfPpo7", "bf_lbl_ppo7", "bf_hint_ppo7", num_input("bfPpo7", "e.g. 23130", 1000, 500000), full=True)}</div>
<div class="grid" id="bfWrap_ppo6" hidden>{fld(lang, "bfPpo6", "bf_lbl_ppo6", "bf_hint_ppo6", num_input("bfPpo6", "e.g. 12600", 1000, 500000), full=True)}</div>
<div class="grid" id="bfWrap_lastpay" hidden>{fld(lang, "bfLastPay", "bf_lbl_lastpay", "bf_hint_lastpay", num_input("bfLastPay", "e.g. 56100", 1000, 500000), full=True)}</div>
<p id="bfErr" class="err" role="alert" hidden></p>
<div class="btnrow"><button type="button" class="btn" id="bfBtn" data-i18n="bf_btn">{T(lang, "bf_btn")}</button></div>
</section>
<section id="bfOut" class="card" aria-live="polite" hidden></section>'''


def pre2016_widget(lang="en"):
    return f'''<section class="card" id="calc" aria-labelledby="p6Title">
<h2 id="p6Title" data-i18n="p6_title">{T(lang, "p6_title")}</h2>
<div class="grid">
{fld(lang, "p6Type", "lbl_type", control=type_select(lang, "p6Type"))}
{fld(lang, "p6Age", "lbl_age", "hint_age", num_input("p6Age", "e.g. 78", 18, 120))}
{fld(lang, "p6Pre", "p6_lbl_pre", "p6_hint_pre", num_input("p6Pre", "e.g. 12600", 1000, 125000))}
{fld(lang, "p6Np", "p6_lbl_np", "p6_hint_np", num_input("p6Np", "e.g. 71800", 0, 250000))}
{fld(lang, "p6Factor", "lbl_factor", control='<select id="p6Factor"><option value="2.57">2.57</option></select>')}
</div>
<p id="p6Err" class="err" role="alert" hidden></p>
<div class="btnrow"><button type="button" class="btn" id="p6Btn" data-i18n="p6_btn">{T(lang, "p6_btn")}</button></div>
</section>
<section id="p6Out" class="card" aria-live="polite" hidden></section>'''


def dr_widget(lang="en"):
    return f'''<section class="card" id="calc" aria-labelledby="drTitle">
<h2 id="drTitle" data-i18n="dr_title">{T(lang, "dr_title")}</h2>
<div class="grid">
{fld(lang, "drBasic", "dr_lbl_basic", "dr_hint_basic", num_input("drBasic", "e.g. 20000", 1000, 250000))}
{fld(lang, "drAge", "lbl_age", "hint_age", num_input("drAge", "e.g. 70", 18, 120))}
{fld(lang, "drOld", "dr_lbl_old", "dr_hint_old", num_input("drOld", "60", 0, 200, "0.01", 60))}
<div><label for="drNew"><span data-i18n="dr_lbl_new">{T(lang, "dr_lbl_new")}</span><span class="hint" id="drNewHint"></span></label>{num_input("drNew", "63", 0, 200, "0.01", 63)}</div>
{fld(lang, "drFrom", "dr_lbl_from", control='<select id="drFrom"></select>')}
{fld(lang, "drPay", "dr_lbl_pay", "dr_hint_pay", '<select id="drPay"></select>')}
{fld(lang, "drComm", "dr_lbl_comm", "dr_hint_comm", num_input("drComm", "0", 0, 200000))}
</div>
<p id="drErr" class="err" role="alert" hidden></p>
<div class="btnrow"><button type="button" class="btn" id="drBtn" data-i18n="dr_btn">{T(lang, "dr_btn")}</button></div>
</section>
<section id="drOut" class="card" aria-live="polite" hidden></section>'''


def credit_of(basic, age_pct, dr, comm=0, fma=0, other=0):
    add = up(Decimal(basic) * age_pct / 100)
    d = up((Decimal(basic) + add) * Decimal(str(dr)) / 100)
    return basic + add + d - comm + fma - other, add, d


EX1 = credit_of(20000, 0, 63, comm=8000, fma=1000)      # (25600, 0, 12600)
EX2 = credit_of(15000, 20, 63)                          # (29340, 3000, 11340)

# ---------------- basic pension finder
PAGES.append(dict(
    path="/basic-pension-finder/", crumb="Basic Pension Finder", webapp=True, widget=finder_widget("en"),
    title="Find Your Basic Pension from Bank Credit or PPO – 8th CPC Helper",
    desc="Work out your basic pension from the amount credited to your bank each month (DR 63%, additional pension, commutation, FMA) or from PPO figures, then open the 8th Pay Commission calculator pre-filled.",
    h1="Basic Pension Finder: From Bank Credit or PPO",
    lead="Every 8th Pay Commission estimate starts from your basic pension — not the amount that reaches your bank. If you only know the monthly credit, or have an old PPO, work your basic pension out here and carry it straight into the calculator.",
    body=f"""
<h2>Why the amount in your bank is not your basic pension</h2>
<p>The figure in your passbook is built up from several pieces. Your <strong>basic pension</strong> is the starting point. If you are 80 or older, an <strong>additional pension</strong> for age is added (20% at 80, rising to 100% at 100). <strong>Dearness Relief</strong> — 63% from 1 July 2026 — is then paid on basic plus additional pension. If you commuted part of your pension at retirement, the <strong>commuted amount is deducted</strong> every month until it is restored after 15 years. Pensioners outside CGHS areas also receive <strong>Fixed Medical Allowance</strong> of ₹1,000 a month. Finally the bank may deduct <strong>income tax (TDS)</strong> or a recovery.</p>
<p>Putting the credited amount into a pay-commission calculator therefore overstates or understates the result — usually by a lot. The fitment factor applies only to the basic pension.</p>

<h2>The formula this tool reverses</h2>
<p class="note">Amount credited = basic + additional pension + DR − commutation deduction + FMA − other deductions<br>
where additional pension = basic × age % (rounded up to the next rupee) and DR = (basic + additional pension) × DR % (rounded up to the next rupee).</p>
<p>Two official rules matter here. First, DR is calculated on the <em>original</em> pension, before the commutation deduction — the Pensioners' Portal of the Department of Pension &amp; Pensioners' Welfare states that "Dearness Relief, however, will continue to be calculated on the basis of the original pension (i.e. without reduction of commuted portion)". Second, any fraction of a rupee in DR is rounded up to the next rupee, as every DR order says. Because of that rounding, a credit sometimes matches two neighbouring basic pensions, or none exactly; the tool tells you when that happens and shows the nearest figure.</p>

<h2>Worked examples</h2>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Item</th><th scope="col">Example 1: age 70, commuted, non-CGHS area</th><th scope="col">Example 2: family pensioner aged 82</th></tr></thead><tbody>
<tr><td>Basic pension</td><td>₹20,000</td><td>₹15,000</td></tr>
<tr><td>Additional pension</td><td>— (under 80)</td><td>{inr(EX2[1])} (20%)</td></tr>
<tr><td>DR at 63%</td><td>{inr(EX1[2])}</td><td>{inr(EX2[2])}</td></tr>
<tr><td>Commutation deduction</td><td>−₹8,000 (40% commuted)</td><td>—</td></tr>
<tr><td>Fixed Medical Allowance</td><td>+₹1,000</td><td>—</td></tr>
<tr><td><strong>Credited to bank</strong></td><td><strong>{inr(EX1[0])}</strong></td><td><strong>{inr(EX2[0])}</strong></td></tr>
</tbody></table></div>
<p>Enter ₹25,600 with age 70, DR 63%, a ₹8,000 commutation deduction and FMA ticked, and the tool returns a basic pension of ₹20,000 — not ₹25,600. At a fitment factor of 2.57 that is the difference between an estimated new basic of ₹51,400 and a wrong ₹65,792.</p>

<h2>Using PPO figures instead</h2>
<ul>
<li><strong>PPO issued from 2016 onwards (or a revised PPO):</strong> the "basic pension" printed there is already a 7th CPC figure. Use it as it is.</li>
<li><strong>Old PPO showing pension as on 31.12.2015:</strong> under DoPPW's OM of 4 August 2016, that pension was multiplied by 2.57 and rounded up to the next rupee, with a minimum of ₹9,000. Some pensioners later received a higher figure through notional pay fixation (OM of 12 May 2017). The <a href="/pre-2016-pensioners/">pre-2016 pensioners calculator</a> compares both.</li>
<li><strong>Only the last pay is known:</strong> pension is 50% of the last basic pay (or of the 10-month average, if that is higher), within ₹9,000–₹1,25,000. Family pension is 30% of last pay at the normal rate and 50% at the enhanced rate.</li>
</ul>

<h2>Common mistakes the tool catches</h2>
<ul>
<li><strong>Using a month with arrears.</strong> A DR increase is usually paid with arrears for several months at once. That month's credit is not a normal month; pick another.</li>
<li><strong>Wrong DR rate.</strong> The 63% rate was approved by the Cabinet on 28 October 2026 with effect from 1 July 2026; banks are expected to apply it from about the November 2026 pension. Credits paid before your bank applied it carry 60% (and before about May 2026, 58%).</li>
<li><strong>Forgetting FMA.</strong> If you live outside a CGHS area, ₹1,000 of your credit is medical allowance, not pension.</li>
<li><strong>Result below ₹9,000.</strong> No central civil pension is below ₹9,000, so a lower result means a deduction or allowance is missing.</li>
</ul>
<p>When the result looks right, press "Use in the 8th CPC calculator" to open the <a href="/">main calculator</a> with your basic pension and age already filled in. You can also check the effect of a DR increase on the <a href="/da-dr-calculator/">DA/DR calculator</a>. How every number is worked out is explained on <a href="/how-we-calculate/">How we calculate</a>.</p>

<section lang="hi">
<h2>हिंदी में: बैंक में आई पेंशन से मूल पेंशन कैसे निकालें</h2>
<p>8वें वेतन आयोग का फिटमेंट फैक्टर केवल <strong>मूल पेंशन (basic pension)</strong> पर लगेगा, बैंक में आने वाली कुल रकम पर नहीं। बैंक की रकम में मूल पेंशन के साथ 80 वर्ष से ऊपर की अतिरिक्त पेंशन, 63% महंगाई राहत (DR, 1 जुलाई 2026 से), CGHS क्षेत्र से बाहर रहने पर ₹1,000 फिक्स्ड मेडिकल अलाउंस जुड़ता है, और कम्यूटेशन की मासिक कटौती व आयकर (TDS) घटता है।</p>
<p class="note">बैंक में आई रकम = मूल पेंशन + अतिरिक्त पेंशन + DR − कम्यूटेशन कटौती + FMA − अन्य कटौती</p>
<p><strong>उदाहरण:</strong> 70 वर्ष के पेंशनभोगी के खाते में हर महीने ₹25,600 आते हैं। उन्होंने 40% पेंशन कम्यूट की थी (₹8,000 कटौती) और CGHS क्षेत्र से बाहर रहते हैं (₹1,000 FMA)। ऊपर के टूल में ये आँकड़े डालने पर मूल पेंशन ₹20,000 निकलती है: ₹20,000 + ₹12,600 DR (63%) − ₹8,000 + ₹1,000 = ₹25,600। ध्यान दें कि DR पूरी मूल पेंशन (₹20,000) पर मिलती है, कटौती के बाद वाली रकम पर नहीं।</p>
<p>अगर आपके पास PPO है: 2016 या उसके बाद के PPO में लिखी मूल पेंशन सीधे इस्तेमाल करें। पुराने PPO में 31.12.2015 की पेंशन लिखी हो तो उसे 2.57 से गुणा करें (कम से कम ₹9,000)। केवल अंतिम वेतन पता हो तो पेंशन उसका 50% होती है; पारिवारिक पेंशन 30% (सामान्य) या 50% (बढ़ी हुई)। ऊपर "हिंदी" बटन दबाकर पूरा टूल हिंदी में चला सकते हैं। मूल पेंशन मिलने के बाद "8वें आयोग के कैलकुलेटर में डालें" बटन से <a href="/hi/">हिंदी कैलकुलेटर</a> अपने-आप भर जाएगा।</p>
</section>
""",
    faqs=[
        ("How do I find my basic pension from the amount credited to my bank?", "Remove the parts that are not basic pension: subtract Fixed Medical Allowance (₹1,000, if you get it), add back the commutation deduction and any tax deducted, then divide by (1 + DR%) — and by (1 + age %) if you are 80 or older. Because DR is rounded up to the next rupee, the tool checks every nearby whole-rupee figure and shows the one that reproduces your credit."),
        ("Is DR paid on the commuted portion of pension?", "Yes. DR is calculated on the original basic pension, before the commutation deduction. The commuted amount is simply deducted in rupees each month until restoration after 15 years."),
        ("Where is the basic pension written on my PPO?", "The Pension Payment Order lists the basic pension, the commuted portion (if any), the date of restoration and, for family pension, the enhanced and normal rates. Revised authorities issued after 2016 show the 7th CPC basic pension."),
        ("My result is below ₹9,000. What went wrong?", "Central civil pensions cannot be below ₹9,000. Usually FMA is included in the credit but not ticked, a deduction (tax, commutation) was not entered, or the credit includes or misses a DR change."),
        ("Can I use this for family pension?", "Yes. Choose the family pension type; age-based additional family pension and DR work the same way. Family pensioners usually have no commutation deduction."),
        ("Is my data stored?", "No. The calculation runs in your browser and nothing you type is sent anywhere."),
    ],
    related=rel("/", "/pre-2016-pensioners/", "/da-dr-calculator/", "/family-pension-calculator/", "/how-we-calculate/", "/hi/"),
))

# ---------------- pre-2016 pensioners
OM_CASES = [  # DoPPW OM 12.05.2017, Annexure I (pension: pre-revised, x2.57, notional pay 1.1.2016, first formulation, payable)
    ("31.12.1984 (4th CPC notional)", 4191, 10771, 23100, 11550, 11550),
    ("31.01.1989 (4th CPC)", 12600, 32382, 71800, 35900, 35900),
    ("30.06.1999 (5th CPC)", 5424, 13940, 29600, 14800, 14800),
    ("31.05.2015 (6th CPC)", 39500, 101515, 205100, 102550, 102550),
]
for _, pre, a, np_, b, pay in OM_CASES:   # self-check against our own rounding rule
    assert max(up(Decimal(pre) * Decimal("2.57")), 9000) == a and up(Decimal(np_) / 2) == b and max(a, b) == pay
om_rows = "".join(f"<tr><td>{d}</td><td>{inr(p)}</td><td>{inr(a)}</td><td>{inr(n)}</td><td>{inr(b)}</td><td><strong>{inr(y)}</strong></td></tr>"
                  for d, p, a, n, b, y in OM_CASES)

PAGES.append(dict(
    path="/pre-2016-pensioners/", crumb="Pre-2016 Pensioners", webapp=True, widget=pre2016_widget("en"),
    title="Pre-2016 Pensioners: 2.57× vs Notional Pay Fixation – 8th CPC Estimate",
    desc="For central pensioners who retired before 2016: how the 7th CPC revised your pension (higher of 2.57× or 50% of notional pay, DoPPW OM 12.05.2017), a calculator for both methods, and an 8th CPC estimate.",
    h1="Pre-2016 Pensioners: Both 7th CPC Methods and the 8th CPC Estimate",
    lead="If you retired, or your family pension started, before 1 January 2016, your current pension was fixed by the higher of two methods. Check which one applies to you, then see what the 8th Pay Commission could mean.",
    body=f"""
<h2>The two methods used by the 7th CPC</h2>
<p>The 7th Central Pay Commission recommended two "formulations" for revising the pension of people who retired before 2016. The Government implemented them in two steps, and every pre-2016 central civil pensioner is entitled to <strong>whichever gives the higher pension</strong>.</p>
<h3>Method A — the 2.57 multiplier (DoPPW OM dated 4 August 2016)</h3>
<p>The pension or family pension "as had been fixed at the time of implementation of 6th CPC recommendations" was multiplied by 2.57 and rounded off to the next higher rupee, with effect from 1 January 2016. The existing pension here is the basic pension <em>including any commuted portion</em> and <em>excluding</em> additional pension for age. Anything below ₹9,000 was stepped up to ₹9,000. Banks applied this automatically, without a fresh authority.</p>
<h3>Method B — notional pay fixation (DoPPW OM dated 12 May 2017)</h3>
<p>The pensioner's pay is fixed notionally in the 7th CPC pay matrix, at the level corresponding to the pay scale (or pay band and grade pay) at which they retired, by carrying it through each intervening pay commission's fixation formula. <strong>50% of that notional pay as on 01.01.2016</strong> is the revised pension; 30% is the normal family pension and 50% the enhanced family pension, each rounded up to the next rupee. The OM then says that "higher of the two Formulations" shall be granted. Unlike Method A, this revision is done by the Head of Department and Pay &amp; Accounts Office, who issue a revised authority under the existing PPO number.</p>
<p class="note">Same limits for both: minimum ₹9,000 (excluding additional pension); maximum 50% of the highest pay of ₹2,50,000 for pension (₹1,25,000) and 30% for family pension (₹75,000). Additional pension for age (20% at 80 … 100% at 100) is added on top of the revised basic.</p>

<h2>Worked examples from the official order</h2>
<p>These are the four pension examples printed in Annexure I of the 12 May 2017 OM. The calculator above reproduces each of them exactly.</p>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Retired on</th><th scope="col">Pension before revision</th><th scope="col">Method A (×2.57)</th><th scope="col">Notional pay on 1.1.2016</th><th scope="col">Method B (50%)</th><th scope="col">Payable</th></tr></thead><tbody>
{om_rows}
</tbody></table></div>
<p>In all four cases Method B was higher — but the gap varies from about 1% to 11%. For family pension in the same order, case 1 shows why the minimum matters: ₹3,500 × 2.57 = ₹8,995, stepped up to ₹9,000.</p>

<h2>Why the calculator asks for your notional pay instead of working it out</h2>
<p>Method B needs your exact pay scale on retirement, the fixation rules of every pay commission since then, and the concordance tables that DoPPW circulated on 6 July 2017 to map old scales to 7th CPC levels. Getting any one of those wrong gives a confident but wrong answer, so this site does <strong>not</strong> guess it. Instead:</p>
<ul>
<li>Enter your <strong>notional pay as on 01.01.2016</strong> if it is written on your revised PPO or revision authority. The calculator then compares both methods.</li>
<li>If you don't have it, leave it blank: you will see Method A, which is the minimum you are entitled to.</li>
<li>The Department of Pension's Pensioners' Portal has an official "Revised Pension Calculator for pre-2016 Pensioners" that uses the concordance tables; you can use it to find your notional figure.</li>
</ul>

<h2>What the 8th Pay Commission could mean for pre-2016 pensioners</h2>
<p>Whatever method fixed your pension, the result became your <strong>basic pension from 1 January 2016</strong>, and Dearness Relief has been paid on it since (63% from 1 July 2026). The calculator's 8th CPC figure applies the fitment factor you choose to that basic pension — the same approach the 7th CPC took for everyone through Method A. It is an <strong>estimate</strong>: no fitment factor has been announced as of {LAST_UPDATED_HUMAN}, and nobody yet knows whether the 8th CPC will again offer older pensioners a notional-pay option, or a different method altogether. Pensioner associations have raised the treatment of older pensioners in their submissions; the Commission's report is due around May 2027.</p>
<p>For defence pensioners, note that the two OMs above apply to central civil pensioners (including CAPFs, railway and All India Services pensioners). Armed forces pensions were revised through separate Ministry of Defence orders; see the <a href="/defence-pension-calculator/">defence pension page</a>.</p>

<section lang="hi">
<h2>हिंदी में: 2016 से पहले रिटायर पेंशनभोगी</h2>
<p>7वें वेतन आयोग में 1.1.2016 से पहले रिटायर हुए केंद्रीय सिविल पेंशनभोगियों को दो तरीकों में से <strong>जो ज़्यादा हो</strong> वह पेंशन मिली: (A) 31.12.2015 की पेंशन × 2.57, अगले पूरे रुपये तक, कम से कम ₹9,000 (DoPPW OM 04.08.2016); या (B) 7वें आयोग के पे मैट्रिक्स में 01.01.2016 को तय नोशनल वेतन का 50% (पारिवारिक पेंशन में 30%, बढ़ी हुई दर पर 50%) (DoPPW OM 12.05.2017)। तरीका B का संशोधन विभागाध्यक्ष / PAO ने संशोधित प्राधिकार से किया, बैंक ने अपने-आप नहीं।</p>
<p>ऊपर के कैलकुलेटर में 31.12.2015 की पेंशन डालें; संशोधित PPO में नोशनल वेतन लिखा हो तो वह भी डालें। आपको दोनों तरीकों की राशि, आज की कुल पेंशन और चुने गए फिटमेंट फैक्टर पर 8वें आयोग का अनुमान दिखेगा। 8वें आयोग में पुराने पेंशनभोगियों के लिए कौन-सा तरीका होगा, यह अभी तय नहीं है — इसलिए यह केवल अनुमान है।</p>
</section>
""",
    faqs=[
        ("How was pension revised for pre-2016 pensioners in the 7th CPC?", "By the higher of two methods: the pension fixed under the 6th CPC multiplied by 2.57 (DoPPW OM 04.08.2016), or 50% of notional pay fixed in the 7th CPC pay matrix as on 01.01.2016 (DoPPW OM 12.05.2017). Family pension used 30% (normal) or 50% (enhanced) of notional pay."),
        ("Does the 2.57 multiplier include the commuted portion?", "Yes. The existing pension for this purpose is the basic pension inclusive of the commuted portion. The commuted amount continues to be deducted from monthly disbursements until restoration."),
        ("Is additional pension for age included before multiplying by 2.57?", "No. Only basic pension is multiplied. Additional pension for those aged 80 and above is then calculated on the revised basic pension."),
        ("How do I know my notional pay as on 01.01.2016?", "It appears in the revised pension authority issued by your Head of Department / Pay and Accounts Office under your existing PPO number. The Pensioners' Portal also has an official revised-pension calculator for pre-2016 pensioners."),
        ("Will the 8th Pay Commission use the same two methods?", "Not known. The 8th CPC has not reported yet. This calculator shows an estimate based on your current basic pension multiplied by the fitment factor you choose."),
        ("Were arrears paid for notional fixation before 2016?", "No. The 12.05.2017 OM says no arrears are admissible for any period before 01.01.2016; arrears from 01.01.2016 were paid after adjusting what had already been paid under the 2.57 method."),
    ],
    related=rel("/", "/basic-pension-finder/", "/family-pension-calculator/", "/fitment-factor-calculator/", "/how-we-calculate/", "/hi/"),
))

# ---------------- DA / DR calculator
DR_ROWS = [9000, 15000, 20000, 30000, 50000, 100000]
def _dr(b, p):
    return up(Decimal(b) * Decimal(p) / 100)
dr_rows = "".join(f"<tr><td>{inr(b)}</td><td>{inr(_dr(b, 60))}</td><td>{inr(_dr(b, 63))}</td><td>{inr(_dr(b, 63) - _dr(b, 60))}</td><td>{inr((_dr(b, 63) - _dr(b, 60)) * 4)}</td></tr>" for b in DR_ROWS)

PAGES.append(dict(
    path="/da-dr-calculator/", crumb="DA / DR Calculator", webapp=True, widget=dr_widget("en"),
    title="DA / DR Calculator for Pensioners – 63% from July 2026, Arrears",
    desc="DR calculator for central government pensioners: official 63% from 1 July 2026 (Cabinet 28 Oct 2026) vs 60%, monthly increase and July–October arrears.",
    h1="DA / DR Calculator for Pensioners (with Arrears)",
    lead="Dearness Relief is revised twice a year and paid with arrears. Enter your basic pension to see your DR today, what a new rate would add each month, and the arrears you would receive.",
    body=f"""
<h2>Where DR stands on {LAST_UPDATED_HUMAN}</h2>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Instalment</th><th scope="col">DR rate</th><th scope="col">Status</th><th scope="col">Order</th></tr></thead><tbody>
<tr><td>From 1 July 2025</td><td>58%</td><td>Official</td><td>DoPPW OM No. 42/02/2024-P&amp;PW(D) dated 08.10.2025 (as cited in the 24.04.2026 OM)</td></tr>
<tr><td>From 1 January 2026</td><td>60%</td><td>Official</td><td>Cabinet decision 18.04.2026; DoPPW OM No. 42/02/2024-P&amp;PW(D)/E-9475 dated 24.04.2026</td></tr>
<tr><td>From 1 July 2026</td><td><strong>63%</strong></td><td>Official — current rate</td><td>Cabinet decision 28.10.2026 (<a href="https://pib.gov.in/PressReleasePage.aspx?PRID=2329485" rel="noopener">PIB release ID 2329485</a>); DoPPW order awaited as of 30.10.2026</td></tr>
</tbody></table></div>
<p>The DoPPW order of 24 April 2026 raised DR "from the existing rate of 58% to 60% of the basic pension/family pension (including additional pension/additional family pension)" with effect from 1 January 2026, for all central government pensioners and family pensioners, including armed forces, railway and All India Services pensioners. It also says that a fraction of a rupee in DR is rounded up to the next rupee.</p>
<p>On 28 October 2026 the Union Cabinet approved an additional instalment of DR to pensioners with effect from 1 July 2026, "representing an increase of 3% over the existing rates of 60%" — taking DR to 63%. The Government put the cost of the DA and DR increase together at Rs 10,016.10 crore a year, benefiting about 48.54 lakh employees and 68.71 lakh pensioners. The DoPPW office memorandum that implements it for pensioners had not been published as of 30 October 2026; this page will cite it once it is out. The calculator pre-fills the official 60% → 63% change.</p>

<h2>How DR and DR arrears are calculated</h2>
<p class="note">DR = (basic pension + additional pension for age) × DR %, rounded up to the next rupee<br>
Monthly increase = DR at new rate − DR at old rate<br>
Arrears = monthly increase × number of months from the date of effect up to the month before the new rate is first paid</p>
<ul>
<li><strong>Commutation does not reduce DR.</strong> DR is paid on the full basic pension; the commuted amount is deducted separately.</li>
<li><strong>Fixed Medical Allowance</strong> (₹1,000 outside CGHS areas) does not attract DR.</li>
<li><strong>Additional pension</strong> for pensioners aged 80 and above does attract DR.</li>
<li><strong>Arrears</strong> are paid in the first month the new rate is credited, so that month's credit looks unusually high. Do not use it to work out your basic pension.</li>
</ul>

<h2>Ready reckoner: DR 60% → 63% from 1 July 2026, with arrears</h2>
<p>DR rose from 60% to 63% with effect from 1 July 2026. If, as is typical, the new rate is first paid with the November 2026 pension, arrears cover four months (July to October). The exact month depends on when the DoPPW order is issued and your bank applies it, so treat the arrears column as typical rather than certain. Figures are for pensioners below 80 years.</p>
<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col">Basic pension</th><th scope="col">DR at 60%</th><th scope="col">DR at 63%</th><th scope="col">Extra per month</th><th scope="col">Arrears, Jul–Oct (4 months)</th></tr></thead><tbody>
{dr_rows}
</tbody></table></div>

<h2>DR and the 8th Pay Commission</h2>
<p>When the 7th CPC was implemented, the DR built up by then (125%) was absorbed into the new basic pension through the 2.57 fitment factor, and DR restarted from zero. If the 8th CPC follows the same pattern, every DR instalment granted until implementation (63% from July 2026, and the January 2027 and later instalments) raises the break-even fitment factor: at 60% DR a factor of 1.60 merely kept total pension unchanged; at today's 63%, 1.63. That is why the <a href="/">main 8th CPC calculator</a> lets you change the DR box, and why every DR decision matters for the estimate. The Government told Parliament in December 2025 that there was no proposal to merge DA with basic pay.</p>
<p>Not sure of your basic pension? Use the <a href="/basic-pension-finder/">basic pension finder</a>. For our formulas and the official orders behind each rate, see <a href="/how-we-calculate/">How we calculate</a>; every rate change is recorded in the <a href="/changelog/">changelog</a>.</p>

<section lang="hi">
<h2>हिंदी में: महंगाई राहत (DR) और एरियर</h2>
<p>1 जुलाई 2026 से केंद्रीय पेंशनभोगियों की DR मूल पेंशन (आयु वाली अतिरिक्त पेंशन सहित) का <strong>63%</strong> है — केंद्रीय मंत्रिमंडल ने 28 अक्टूबर 2026 को 60% से 63% की बढ़ोतरी मंज़ूर की (PIB विज्ञप्ति 2329485)। पेंशनभोगियों के लिए DoPPW का आदेश 30 अक्टूबर 2026 तक जारी नहीं हुआ था। इससे पहले 1 जनवरी 2026 से DR 60% थी।</p>
<p class="note">DR = (मूल पेंशन + अतिरिक्त पेंशन) × DR %, अगले पूरे रुपये तक · एरियर = मासिक बढ़ोतरी × लागू तिथि से भुगतान वाले महीने से पहले तक के महीने</p>
<p>उदाहरण: ₹20,000 मूल पेंशन पर 60% DR = ₹12,000; 63% पर ₹12,600, यानी ₹600 प्रति माह ज़्यादा। आम तौर पर नई दर नवंबर 2026 की पेंशन के साथ मिले तो जुलाई–अक्टूबर के 4 महीनों का एरियर ₹2,400 होगा (महीना आदेश और बैंक पर निर्भर)। कम्यूटेशन कटौती से DR कम नहीं होती — DR पूरी मूल पेंशन पर मिलती है। ऊपर "हिंदी" बटन से कैलकुलेटर हिंदी में चलाएँ।</p>
</section>
""",
    faqs=[
        ("What is the current DR for central government pensioners?", "63% of basic pension (including additional pension) from 1 July 2026, following the Cabinet decision of 28.10.2026 (PIB release ID 2329485). It was 60% from 1 January 2026 under DoPPW OM dated 24.04.2026."),
        ("Has the July 2026 DA/DR been announced?", "Yes. The Union Cabinet approved it on 28 October 2026: DA and DR go from 60% to 63% with effect from 1 July 2026. The DoPPW order for pensioners was awaited as of 30 October 2026."),
        ("When will the July–October DR arrears be paid?", "Typically with the first pension paid at the new rate, often November. It depends on when the DoPPW order is issued and your bank processes it. For ₹20,000 basic pension, 4 months of arrears is ₹2,400."),
        ("How are DR arrears calculated?", "Arrears = (DR at the new rate − DR at the old rate) × the number of months from the date of effect until the month before the new rate is first paid. Each month's DR is rounded up to the next rupee."),
        ("Is DR paid on the commuted part of pension?", "Yes. DR is calculated on the original basic pension before the commutation deduction."),
        ("Do family pensioners get the same DR?", "Yes. The same DR percentage applies to family pension, including additional family pension for those aged 80 and above."),
        ("Is DR paid on Fixed Medical Allowance?", "No. FMA of ₹1,000 a month is a flat allowance and does not attract DR."),
    ],
    related=rel("/", "/basic-pension-finder/", "/latest-update/", "/how-we-calculate/", "/changelog/", "/hi/"),
))

# ---------------- how we calculate
SOURCES = [
    ("https://pib.gov.in/PressReleasePage.aspx?PRID=2183289", "PIB, 28.10.2025 — Cabinet approves Terms of Reference of 8th Central Pay Commission (18-month deadline; effect \"would normally be expected from 01.01.2026\")"),
    ("https://8cpc.gov.in/composition/", "8th Central Pay Commission — Composition (Chairperson, part-time Member, Member-Secretary)"),
    ("https://www.pmindia.gov.in/en/news_updates/cabinet-approves-additional-instalment-of-dearness-allowance-to-central-government-employees-and-dearness-relief-dr-to-pensioners-w-e-f-01-01-2026/", "PM India, 18.04.2026 — Cabinet approves DA/DR increase from 58% to 60% w.e.f. 01.01.2026"),
    ("https://documents.doptcirculars.nic.in/D3/D03ppw/DR%20OrderxUYZn.pdf", "DoPPW OM No. 42/02/2024-P&PW(D)/E-9475 dated 24.04.2026 — DR 60% on basic + additional pension; fractions rounded up"),
    ("https://pib.gov.in/PressReleasePage.aspx?PRID=2329485", "PIB release ID 2329485, 28.10.2026 — Cabinet approves DA/DR from 60% to 63% w.e.f. 01.07.2026 (48.54 lakh employees, 68.71 lakh pensioners, Rs 10,016.10 crore a year)"),
    ("https://documents.doptcirculars.nic.in/D3/D03ppw/PPWA_7thCPC3_040816_S.pdf", "DoPPW OM No. 38/37/2016-P&PW(A)(ii) dated 04.08.2016 — pre-2016 pension × 2.57, minimum ₹9,000, ceilings, additional pension slabs"),
    ("https://documents.doptcirculars.nic.in/D3/D03ppw/PPWA_12052017.pdf", "DoPPW OM No. 38/37/2016-P&PW(A) dated 12.05.2017 — notional pay fixation, 50%/30% of notional pay, higher of the two formulations, worked examples"),
    ("https://pensionersportal.gov.in/retire-benefit.aspx", "Pensioners' Portal (DoPPW) — Retirement benefits: minimum ₹9,000 / maximum ₹1,25,000; commutation up to 40%, restored after 15 years, DR on original pension"),
    ("https://sansad.in/getFile/annex/258/AU1086.pdf", "Rajya Sabha Unstarred Question 1086, 15.12.2022 — Fixed Medical Allowance ₹1,000 per month from 01.07.2017"),
]
src_html = "".join(f'<li><a href="{u}" rel="noopener">{html.escape(t)}</a></li>' for u, t in SOURCES)

PAGES.append(dict(
    path="/how-we-calculate/", crumb="How We Calculate",
    title="How We Calculate – Formulas, Assumptions & Official Sources",
    desc="Every formula behind this 8th Pay Commission pension calculator: rounding, DR, additional pension, minimum and maximum pension, pre-2016 methods, basic pension finder and DR arrears — with links to the official orders.",
    h1="How We Calculate",
    lead="Every result on this site can be checked with a pen and paper. This page lists each formula, what is official, what is an assumption, and the official documents we read — checked on " + LAST_UPDATED_HUMAN + ".",
    body=f"""
<h2>Official vs estimate</h2>
<p>Two kinds of numbers appear on this site. <strong>Official</strong> numbers come from a Government order or release we have read: the current DR rate (63% from 1 July 2026), the minimum and maximum pension, family pension rates, additional pension for age, Fixed Medical Allowance and the 7th CPC pre-2016 methods. <strong>Estimates</strong> are anything about the 8th Pay Commission — the fitment factor, the new minimum and maximum, DR after revision, the date of effect and arrears — and any DR rate not yet announced. Every estimate is labelled "Estimate — not official" on screen.</p>

<h2>Rounding</h2>
<p>Pension, additional pension and DR are rounded <strong>up to the next rupee</strong>. DR orders say so explicitly ("The payment of Dearness Relief involving a fraction of a rupee shall be rounded off to the next higher rupee"), and the 7th CPC orders rounded revised pension "off to next higher rupee". The code first trims floating-point noise (so 23,129.999… becomes 23,130), then rounds up.</p>

<h2>Current pension (7th CPC)</h2>
<p class="note">Additional pension = basic × age % · DR = (basic + additional) × DR % · Total = basic + additional + DR</p>
<ul>
<li>Age %: 20% from 80, 30% from 85, 40% from 90, 50% from 95, 100% from 100 years (OM 04.08.2016 para 4.5; CCS (Pension) Rules, 2021).</li>
<li>DR: 63% from 01.07.2026, paid on basic plus additional pension (Cabinet decision 28.10.2026, PIB release 2329485; DoPPW order awaited). 60% from 01.01.2026 (DoPPW OM 24.04.2026).</li>
<li>Limits: minimum ₹9,000; maximum ₹1,25,000 for pension and enhanced family pension, ₹75,000 for normal family pension (50% / 30% of the highest pay of ₹2,50,000).</li>
</ul>

<h2>8th CPC estimate (main calculator)</h2>
<p class="note">New basic = basic × fitment factor (rounded up), raised to new minimum = ₹9,000 × factor, limited to new maximum = 7th CPC maximum × factor<br>
New total = new basic + new basic × age % + DR after revision (assumed 0%)<br>
Arrears = max(0, new total − current total) × months from date of effect to the month before first payment</p>
<p>Assumptions, all changeable on screen: the factor you pick (none is official); the 7th CPC method of a single multiplier; DR restarting at 0%; date of effect 1 January 2026 (the Government said effect "would normally be expected" then, based on past practice); today's DR used for the whole arrears period. Commutation, income tax and FMA are excluded.</p>

<h2>Pre-2016 pensioners</h2>
<p class="note">Method A = pension on 31.12.2015 × 2.57 (rounded up, min ₹9,000)<br>
Method B = notional pay on 01.01.2016 × 50% (pension, enhanced family pension) or 30% (normal family pension), rounded up<br>
7th CPC basic = higher of A and B, within the limits above</p>
<p>Method B's notional pay is entered by the user from their revised PPO; we do not compute notional fixation because it needs each pensioner's scale history and the DoPPW concordance tables. The calculator reproduces all four pension examples in Annexure I of the 12.05.2017 OM (₹11,550, ₹35,900, ₹14,800 and ₹1,02,550). The 8th CPC estimate then applies the chosen factor to the 7th CPC basic.</p>

<h2>Basic pension finder</h2>
<p class="note">Credit = basic + additional + DR − commutation deduction + FMA (₹1,000 if ticked) − other deductions</p>
<p>The tool inverts this formula by testing every whole-rupee basic pension near the algebraic estimate and keeping the one that reproduces the credit exactly (or the nearest, with the difference shown). DR is applied to the full pension before commutation, as DoPPW's Pensioners' Portal states. When the commutation is entered as a percentage, the deduction is approximated as basic × % rounded to the nearest rupee; the rupee amount from the PPO is more accurate. PPO modes: a post-2016 PPO basic is used as is; a 31.12.2015 pension is × 2.57 (min ₹9,000); last pay gives 50% (pension), 30% or 50% (family pension) within the limits.</p>

<h2>DA / DR calculator</h2>
<p class="note">DR = (basic + additional) × rate, rounded up · Monthly increase = DR(new) − DR(old) · Arrears = increase × months from date of effect to the month before first payment</p>
<p>Basic pension and age slab are held constant over the arrears period, and arrears are shown before any income-tax deduction. The pre-filled rates are the latest official change, 60% → 63% from 1 July 2026. A rate not yet announced, if you type one, is labelled as an estimate.</p>

<h2>Where the numbers live</h2>
<p>All rates are kept in one settings block in the site's script, and published in machine-readable form at <a href="/assets/rates.json">/assets/rates.json</a> (generated from the same settings, so the two cannot disagree). When an order changes a rate, we update it, record the change with its date and source on the <a href="/changelog/">changelog</a>, and change the "data last updated" date shown on every page.</p>

<h2>Official sources we read</h2>
<p>Each link below was opened and checked on {LAST_UPDATED_HUMAN} or earlier.</p>
<ul>{src_html}</ul>
<p>Other references used on the site, not re-opened for this page: CCS (Pension) Rules, 2021 (pensionersportal.gov.in) for family pension and additional pension rules; DoPPW concordance tables OM dated 06.07.2017; news reports (Mint, Economic Times, Financial Express) for union demands such as the 3.833 factor, which are always labelled as demands.</p>

<h2>Found an error?</h2>
<p>Please tell us through the <a href="/contact/">contact page</a>, ideally with the order number and date. Verified corrections are made promptly and logged on the <a href="/changelog/">changelog</a>.</p>
""",
    faqs=[
        ("Are the results official?", "No. Current rules are taken from official orders, but every 8th Pay Commission figure is an estimate until the Government issues orders."),
        ("Why does the site round up instead of to the nearest rupee?", "Because the official orders do: DR and revised pension fractions are rounded off to the next higher rupee."),
        ("Why is DR set to 0% after revision?", "When the 6th and 7th pay commissions were implemented, the accumulated DR was absorbed into the new basic pension and DR restarted from zero. The 8th CPC may decide differently; you can see DR before and after in every result."),
        ("Where can I see what changed and when?", "On the changelog page, which lists every dated change to rates, rules and pages."),
    ],
    related=rel("/", "/changelog/", "/latest-update/", "/pre-2016-pensioners/", "/da-dr-calculator/"),
))

# ---------------- changelog
cl_html = "".join(
    f'<li><time datetime="{d}">{h}</time><ul>' + "".join(f"<li>{e}</li>" for e in items) + "</ul></li>" for d, h, items in CHANGELOG)
PAGES.append(dict(
    path="/changelog/", crumb="Changelog",
    title="Changelog – Dated Updates to Rates, Rules and Calculators",
    desc="Every dated change to this 8th Pay Commission pension calculator: DR rates, official orders checked, new calculators and corrections, starting 28 October 2026.",
    h1="Changelog",
    lead="A dated record of every change to the rates, rules and calculators on this site, newest first. For the status of the 8th Pay Commission itself, see the latest update page.",
    body=f"""
<ol class="timeline">{cl_html}</ol>
<h2>How we log changes</h2>
<p>An entry is added whenever a rate changes (for example a new DR instalment), an official order is checked, a calculation is corrected or a page is added. Each rate change names the order it comes from, and the "data last updated" date at the top of every page changes with it. Formulas and sources are on <a href="/how-we-calculate/">How we calculate</a>; announcements by the Government and the Commission are tracked on the <a href="/latest-update/">latest update</a> page.</p>
""",
    faqs=[
        ("How do I know the calculator uses the latest DR?", "The current DR and the date it was last checked are shown in the status strip on every page and logged here with the order number."),
        ("Will the site be updated when the fitment factor is announced?", "Yes. The official factor becomes the default in every calculator and the change is logged here the same day."),
    ],
    related=rel("/", "/how-we-calculate/", "/latest-update/", "/da-dr-calculator/"),
))


# ------------------------------------------------------------------ bilingual content (added 28 Oct 2026)
for _f in ("content_shared.py", "content_en_more.py", "content_hi_tools.py", "content_hi_tools2.py", "content_hi_info.py", "content_depth.py", "content_amounts.py"):
    exec(compile(open(os.path.join(ROOT, "tools", _f), encoding="utf-8").read(), _f, "exec"))


# ------------------------------------------------------------------ write
def words(s):
    return len(re.sub(r"<[^>]+>", " ", s).split())


def export_rates():
    """Write assets/rates.json from CONFIG in assets/app.js (CONFIG stays the single source of truth;
    the JSON is a public, machine-readable copy that the pages do not load)."""
    subprocess.check_call(["node", os.path.join(ROOT, "tools", "export-rates.js")])


LLMS_TXT = """# 8th CPC Pension Calculator

> Free, bilingual (English + Hindi) calculators and guides for Indian central government pensioners and family pensioners to estimate their pension under the 8th Central Pay Commission. Every page exists in English and in Hindi (/hi/...). All 8th CPC figures are estimates: the official fitment factor has not been announced. Published by the independent 8CPC Pension Calculator team; not a government website.

Key facts (as of 30 October 2026, verified against official orders):
- 8th Central Pay Commission constituted 3 November 2025; chair Justice Ranjana Prakash Desai; report expected around mid-2027.
- Official 8th CPC fitment factor: not yet announced. 7th CPC factor was 2.57. Common estimates range 1.92 to 2.86; 3.833 is a union (NC-JCM staff side) demand.
- Date of effect: 1 January 2026 is expected based on past practice, not officially decided.
- Dearness Relief (DR): 63% from 1 July 2026 (Cabinet decision 28 October 2026, PIB release ID 2329485; DoPPW order awaited as of 30 October 2026). Previously 60% from 1 January 2026.
- Formula: new basic pension = current basic pension x fitment factor (rounded up to the next rupee). Additional pension for age 80+ (20%), 85+ (30%), 90+ (40%), 95+ (50%), 100+ (100%).
- Minimum pension Rs 9,000 (raised from Rs 3,500 in 2016); maximum Rs 1,25,000. Family pension: 30% of last pay (normal), 50% enhanced for a limited period.
- Commutation: up to 40% of pension; restored after 15 years; DR is paid on the full pension; commuted value = commuted pension x factor (8.194 at age next birthday 61) x 12.
- Life certificate: every November; pensioners aged 80+ from 1 October.

## Calculators (English | Hindi)
- [8th Pay Commission pension calculator]({DOMAIN}/) | [हिंदी]({DOMAIN}/hi/): new pension, DR comparison and arrears
- [Basic pension finder]({DOMAIN}/basic-pension-finder/) | [हिंदी]({DOMAIN}/hi/basic-pension-finder/): basic pension from the monthly bank credit or PPO
- [Pre-2016 pensioners]({DOMAIN}/pre-2016-pensioners/) | [हिंदी]({DOMAIN}/hi/pre-2016-pensioners/): higher of 2.57x and notional pay fixation
- [DA / DR calculator]({DOMAIN}/da-dr-calculator/) | [हिंदी]({DOMAIN}/hi/da-dr-calculator/)
- [Fitment factor calculator]({DOMAIN}/fitment-factor-calculator/) | [हिंदी]({DOMAIN}/hi/fitment-factor-calculator/)
- [Family pension calculator]({DOMAIN}/family-pension-calculator/) | [हिंदी]({DOMAIN}/hi/family-pension-calculator/)
- [Defence pension calculator]({DOMAIN}/defence-pension-calculator/) | [हिंदी]({DOMAIN}/hi/defence-pension-calculator/)
- [Commutation & restoration calculator]({DOMAIN}/commutation-calculator/) | [हिंदी]({DOMAIN}/hi/commutation-calculator/)
- [8th CPC pension chart]({DOMAIN}/pension-chart/) | [हिंदी]({DOMAIN}/hi/pension-chart/)
- [8th CPC pension by amount]({DOMAIN}/pension-by-amount/) | [हिंदी]({DOMAIN}/hi/pension-by-amount/): one page per basic pension, Rs 9,000 to Rs 1,00,000

## Pension by amount (estimate at every fitment factor, DR, arrears, commutation, family pension)
{AMOUNT_LINKS}

## Guides
- [Minimum pension under the 8th CPC]({DOMAIN}/minimum-pension-8th-pay-commission/) | [हिंदी]({DOMAIN}/hi/minimum-pension-8th-pay-commission/)
- [Life certificate (Jeevan Pramaan) guide]({DOMAIN}/life-certificate/) | [हिंदी]({DOMAIN}/hi/life-certificate/)
- [Latest 8th CPC update]({DOMAIN}/latest-update/) | [हिंदी]({DOMAIN}/hi/latest-update/)

## Sources, method and trust
- [How we calculate]({DOMAIN}/how-we-calculate/) | [हिंदी]({DOMAIN}/hi/how-we-calculate/)
- [Editorial policy]({DOMAIN}/editorial-policy/) | [हिंदी]({DOMAIN}/hi/editorial-policy/)
- [About]({DOMAIN}/about/) | [हिंदी]({DOMAIN}/hi/about/)
- [Changelog]({DOMAIN}/changelog/) | [हिंदी]({DOMAIN}/hi/changelog/)
- [Machine-readable rates]({DOMAIN}/assets/rates.json)
"""

def main():
    ALL_PATHS.update(p["path"] for p in PAGES)
    report = []
    for p in PAGES:
        out_dir = os.path.join(ROOT, p["path"].strip("/"))
        os.makedirs(out_dir, exist_ok=True)
        doc = page(p)
        fn = os.path.join(out_dir, "index.html")
        with open(fn, "w", encoding="utf-8") as f:
            f.write(doc)
        wc = words(p["body"]) + sum(words(q) + words(a) for q, a in p.get("faqs", []))
        report.append((p["path"], wc, len(doc.encode("utf-8"))))
    # 404
    p404 = dict(path="/404/", crumb="Page not found", robots="noindex", title="Page not found – 8th Pay Commission Pension Calculator",
                desc="The page you are looking for does not exist.", h1="Page not found",
                lead="Sorry, that page does not exist. Try the links below.",
                body='<ul><li><a href="/">8th Pay Commission pension calculator</a></li><li><a href="/pension-chart/">Pension chart</a></li><li><a href="/latest-update/">Latest update</a></li><li><a href="/hi/">हिंदी</a></li></ul>')
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(page(p404).replace(f'<link rel="canonical" href="{DOMAIN}/404/">\n', ""))
    # sitemap
    urls = "".join(f"<url><loc>{DOMAIN}{p['path']}</loc><lastmod>{p.get('lastmod', LAST_UPDATED)}</lastmod></url>\n" for p in PAGES)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    export_rates()
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"# Generated by tools/build.py from DOMAIN\nUser-agent: *\nAllow: /\nDisallow: /tools/\n\n# AI / answer engines welcome (GEO)\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\nUser-agent: Bingbot\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(LLMS_TXT.replace("{AMOUNT_LINKS}", "\n".join(f"- [Rs {b:,} basic pension]({{DOMAIN}}/pension-{b}-8th-pay-commission/) | [हिंदी]({{DOMAIN}}/hi/pension-{b}-8th-pay-commission/)" for b in AMT_LIST)).replace("{DOMAIN}", DOMAIN))
    for r in report:
        print(f"{r[0]:32s} words={r[1]:5d} html={r[2]/1024:.1f}KB")


if __name__ == "__main__":
    main()
