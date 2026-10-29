# Shared data for the bilingual pages. Executed inside tools/build.py (same globals).
# Every URL in SRC was opened and checked on 28 Oct 2026 (see the changelog entry for that date).

SRC = {
    "pib_tor": ("https://pib.gov.in/PressReleasePage.aspx?PRID=2183289",
                "PIB, 28.10.2025 — Cabinet approves Terms of Reference of the 8th Central Pay Commission",
                "PIB, 28.10.2025 — 8वें केंद्रीय वेतन आयोग के कार्य-क्षेत्र (ToR) को कैबिनेट की मंज़ूरी"),
    "cpc8": ("https://8cpc.gov.in/", "8th Central Pay Commission — official website (notices, visits)",
             "8वाँ केंद्रीय वेतन आयोग — आधिकारिक वेबसाइट (सूचनाएँ, दौरे)"),
    "cpc8_comp": ("https://8cpc.gov.in/composition/", "8th CPC — Composition (Chairperson Justice Ranjana Prakash Desai)",
                  "8वाँ वेतन आयोग — संरचना (अध्यक्ष न्यायमूर्ति रंजना प्रकाश देसाई)"),
    "pm_dr": ("https://www.pmindia.gov.in/en/news_updates/cabinet-approves-additional-instalment-of-dearness-allowance-to-central-government-employees-and-dearness-relief-dr-to-pensioners-w-e-f-01-01-2026/",
              "PM India, 18.04.2026 — Cabinet approves DA/DR rise from 58% to 60% w.e.f. 01.01.2026",
              "PM India, 18.04.2026 — 01.01.2026 से DA/DR 58% से 60% करने को कैबिनेट की मंज़ूरी"),
    "om_dr": ("https://documents.doptcirculars.nic.in/D3/D03ppw/DR%20OrderxUYZn.pdf",
              "DoPPW OM No. 42/02/2024-P&PW(D)/E-9475 dated 24.04.2026 — DR 60% on basic + additional pension",
              "DoPPW कार्यालय ज्ञापन 42/02/2024-P&PW(D)/E-9475, दिनांक 24.04.2026 — मूल + अतिरिक्त पेंशन पर 60% DR"),
    "pib_all": ("https://pib.gov.in/allRel.aspx", "PIB — all press releases (checked for a July 2026 DA/DR decision)",
                "PIB — सभी प्रेस विज्ञप्तियाँ (जुलाई 2026 DA/DR निर्णय के लिए जाँची गईं)"),
    "om_0816": ("https://documents.doptcirculars.nic.in/D3/D03ppw/PPWA_7thCPC3_040816_S.pdf",
                "DoPPW OM dated 04.08.2016 — pre-2016 pension × 2.57, minimum ₹9,000, additional pension slabs, commuted portion",
                "DoPPW कार्यालय ज्ञापन 04.08.2016 — 2016 से पहले की पेंशन × 2.57, न्यूनतम ₹9,000, अतिरिक्त पेंशन, कम्यूटेड हिस्सा"),
    "om_0517": ("https://documents.doptcirculars.nic.in/D3/D03ppw/PPWA_12052017.pdf",
                "DoPPW OM dated 12.05.2017 — notional pay fixation, higher of two formulations, worked examples",
                "DoPPW कार्यालय ज्ञापन 12.05.2017 — नोशनल वेतन निर्धारण, दो तरीकों में से ज़्यादा, उदाहरण"),
    "portal_rb": ("https://pensionersportal.gov.in/retire-benefit.aspx",
                  "Pensioners' Portal (DoPPW) — Retirement benefits: minimum/maximum pension, commutation, DR on original pension",
                  "पेंशनर्स पोर्टल (DoPPW) — सेवानिवृत्ति लाभ: न्यूनतम/अधिकतम पेंशन, कम्यूटेशन, मूल पेंशन पर DR"),
    "portal_faq": ("https://pensionersportal.gov.in/FAQ_Civil.pdf",
                   "Pensioners' Portal FAQs (Central Civil Services) — family pension, FMA ₹1,000, commutation, DR",
                   "पेंशनर्स पोर्टल FAQ (केंद्रीय सिविल सेवा) — पारिवारिक पेंशन, FMA ₹1,000, कम्यूटेशन, DR"),
    "comm_table": ("https://pensionersportal.gov.in/commtable.aspx", "Pensioners' Portal — Commutation tables",
                   "पेंशनर्स पोर्टल — कम्यूटेशन तालिकाएँ"),
    "doe": ("https://doe.gov.in/", "Department of Expenditure, Ministry of Finance — implements Pay Commission recommendations",
            "व्यय विभाग, वित्त मंत्रालय — वेतन आयोग की सिफारिशें लागू करने वाला विभाग"),
    "doppw": ("https://doppw.gov.in/", "Department of Pension & Pensioners' Welfare (DoPPW)",
              "पेंशन और पेंशनभोगी कल्याण विभाग (DoPPW)"),
    "cpao": ("https://cpao.nic.in/", "Central Pension Accounting Office (CPAO)", "केंद्रीय पेंशन लेखा कार्यालय (CPAO)"),
    "sparsh": ("https://sparsh.defencepension.gov.in/", "SPARSH — defence pension portal (PCDA Pension)",
               "SPARSH — रक्षा पेंशन पोर्टल (PCDA पेंशन)"),
    "desw": ("https://desw.gov.in/", "Department of Ex-Servicemen Welfare, Ministry of Defence",
             "पूर्व सैनिक कल्याण विभाग, रक्षा मंत्रालय"),
    "jeevan": ("https://jeevanpramaan.gov.in/", "Jeevan Pramaan — Digital Life Certificate (official portal)",
               "जीवन प्रमाण — डिजिटल जीवन प्रमाण पत्र (आधिकारिक पोर्टल)"),
    "uidai_lc": ("https://uidai.gov.in/images/FAQs_Digital_Life_Certificate.pdf",
                 "UIDAI — Life Certificate FAQs (November window, 80+ from 1 October, doorstep options)",
                 "UIDAI — जीवन प्रमाण पत्र FAQ (नवंबर, 80+ के लिए 1 अक्टूबर से, घर बैठे विकल्प)"),
    "pib_dlc": ("https://www.pib.gov.in/PressReleasePage.aspx?PRID=2247920",
                "PIB, 01.04.2026 — Parliament reply on Digital Life Certificate campaigns",
                "PIB, 01.04.2026 — डिजिटल जीवन प्रमाण पत्र अभियान पर संसद में उत्तर"),
    "doppw_lc": ("https://doppw.gov.in/en/life-certificate", "DoPPW — Life Certificate orders",
                 "DoPPW — जीवन प्रमाण पत्र से जुड़े आदेश"),
    "pib_min": ("https://www.pib.gov.in/newsite/PrintRelease.aspx?relid=200447",
                "PIB, 19.03.2020 — DoPPW initiatives (minimum pension ₹3,500 → ₹9,000; enhanced family pension rule)",
                "PIB, 19.03.2020 — DoPPW पहलें (न्यूनतम पेंशन ₹3,500 → ₹9,000; बढ़ी पारिवारिक पेंशन का नियम)"),
    "pgportal": ("https://pgportal.gov.in/", "CPGRAMS / CPENGRAMS — public and pension grievance portal",
                 "CPGRAMS / CPENGRAMS — शिकायत पोर्टल (पेंशन शिकायत सहित)"),
    "labour": ("https://labourbureau.gov.in/", "Labour Bureau — CPI-IW (basis of DA/DR)", "श्रम ब्यूरो — CPI-IW (DA/DR का आधार)"),
    "cyber": ("https://cybercrime.gov.in/", "National Cyber Crime Reporting Portal (helpline 1930)",
              "राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल (हेल्पलाइन 1930)"),
}

SRC_TOOL = ["pib_tor", "cpc8_comp", "om_dr", "pm_dr", "om_0816", "portal_rb", "doe", "doppw"]

REL_ALL.update({
    "/commutation-calculator/": ("Commutation & restoration calculator", "monthly deduction, lump sum and the 15-year restoration date"),
    "/minimum-pension-8th-pay-commission/": ("Minimum pension under the 8th CPC", "₹9,000 today and what each fitment factor would make it"),
    "/life-certificate/": ("Life certificate (Jeevan Pramaan) guide", "November deadline, 80+ from 1 October, face authentication"),
    "/editorial-policy/": ("Editorial policy", "sources, verification, corrections and independence"),
    "/about/": ("About us", "who runs this site and why"),
    "/contact/": ("Contact", "report an error or ask about the site"),
    "/privacy/": ("Privacy policy", "nothing you type leaves your device"),
    "/disclaimer/": ("Disclaimer", "not a government website; estimates only"),
})

REL_HI = {
    "/": ("8वां वेतन आयोग पेंशन कैलकुलेटर", "नई पेंशन, DR और एरियर का अनुमान"),
    "/fitment-factor-calculator/": ("फिटमेंट फैक्टर कैलकुलेटर", "हर फैक्टर का आपकी पेंशन पर असर"),
    "/family-pension-calculator/": ("पारिवारिक पेंशन कैलकुलेटर", "सामान्य 30% और बढ़ी हुई 50% दर"),
    "/defence-pension-calculator/": ("रक्षा पेंशन कैलकुलेटर", "सशस्त्र बलों के पेंशनभोगियों के लिए"),
    "/pension-chart/": ("8वें वेतन आयोग का पेंशन चार्ट", "₹9,000 से ₹1,25,000 तक, छह फैक्टर पर"),
    "/latest-update/": ("8वें वेतन आयोग का ताज़ा अपडेट", "तारीख के साथ स्थिति"),
    "/basic-pension-finder/": ("मूल पेंशन पता करें", "बैंक में आई रकम या PPO से मूल पेंशन"),
    "/pre-2016-pensioners/": ("2016 से पहले के पेंशनभोगी", "2.57 गुना बनाम नोशनल वेतन, और 8वें आयोग का अनुमान"),
    "/da-dr-calculator/": ("DA / DR कैलकुलेटर", "महंगाई राहत और एरियर"),
    "/how-we-calculate/": ("हम गणना कैसे करते हैं", "सूत्र, मान्यताएँ और सरकारी स्रोत"),
    "/changelog/": ("बदलाव सूची", "दरों और पेजों में हर बदलाव, तारीख के साथ"),
    "/commutation-calculator/": ("कम्यूटेशन और बहाली कैलकुलेटर", "मासिक कटौती, एकमुश्त राशि और 15 साल बाद बहाली"),
    "/minimum-pension-8th-pay-commission/": ("8वें वेतन आयोग में न्यूनतम पेंशन", "आज ₹9,000 — हर फैक्टर पर कितनी"),
    "/life-certificate/": ("जीवन प्रमाण पत्र गाइड", "नवंबर की समय-सीमा, 80+ के लिए 1 अक्टूबर से, चेहरे से प्रमाणीकरण"),
    "/editorial-policy/": ("संपादकीय नीति", "स्रोत, जाँच, सुधार और स्वतंत्रता"),
    "/about/": ("हमारे बारे में", "यह साइट कौन चलाता है और क्यों"),
    "/contact/": ("संपर्क", "गलती बताएँ या साइट के बारे में पूछें"),
    "/privacy/": ("गोपनीयता नीति", "आपकी भरी जानकारी आपके डिवाइस पर ही रहती है"),
    "/disclaimer/": ("अस्वीकरण", "सरकारी वेबसाइट नहीं; केवल अनुमान"),
}


def rel_hi(*paths):
    return [(p, REL_HI[p][0], REL_HI[p][1]) for p in paths]


def commutation_widget(lang="en"):
    modes = "".join(f'<option value="{v}" data-i18n="{k}">{T(lang, k)}</option>' for v, k in [("pct", "cm_mode_pct"), ("amount", "cm_mode_amt")])
    return f'''<section class="card" id="calc" aria-labelledby="cmTitle">
<h2 id="cmTitle" data-i18n="cm_title">{T(lang, "cm_title")}</h2>
<div class="grid">
{fld(lang, "cmBasic", "cm_lbl_basic", "cm_hint_basic", num_input("cmBasic", "e.g. 30000", 1000, 250000), full=True)}
{fld(lang, "cmMode", "cm_lbl_mode", control=f'<select id="cmMode">{modes}</select>')}
{fld(lang, "cmPct", "cm_lbl_pct", "cm_hint_pct", num_input("cmPct", "40", 1, 40, "0.01", 40), wrap_id="cmPctWrap")}
{fld(lang, "cmAmt", "cm_lbl_amt", "cm_hint_amt", num_input("cmAmt", "e.g. 12000", 1, 100000), wrap_id="cmAmtWrap", hidden=True)}
{fld(lang, "cmStart", "cm_lbl_start", "cm_hint_start", '<select id="cmStart"></select>')}
{fld(lang, "cmAge", "lbl_age", "hint_age", num_input("cmAge", "e.g. 66", 18, 120))}
{fld(lang, "cmCvf", "cm_lbl_cvf", "cm_hint_cvf", num_input("cmCvf", "8.194", 1, 20, "0.001", "8.194"))}
{fld(lang, "cmFit", "lbl_factor", control='<select id="cmFit"><option value="2.57">2.57</option></select>')}
</div>
<p id="cmErr" class="err" role="alert" hidden></p>
<div class="btnrow"><button type="button" class="btn" id="cmBtn" data-i18n="cm_btn">{T(lang, "cm_btn")}</button></div>
</section>
<section id="cmOut" class="card" aria-live="polite" hidden></section>'''


def ex_table(lang, rows, cols):
    """Small HTML table helper: cols = header labels, rows = lists of cell strings."""
    head = "".join(f'<th scope="col">{c}</th>' for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl-wrap"><table class="data"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def gain_rows(basics, factors, dr=60):
    """[basic, total today, new basic at each factor, real gain at each factor] using the site's rounding."""
    out = []
    for b in basics:
        today = b + up(Decimal(b) * dr / 100)
        cells = [inr(b), inr(today)]
        for f in factors:
            nb = max(ceil_mul(b, f), ceil_mul(9000, f))
            cells.append(f"{inr(nb)} <small>(+{inr(nb - today)})</small>")
        out.append(cells)
    return out


def page_by_path(path):
    for p in PAGES:
        if p["path"] == path:
            return p
    raise KeyError(path)
