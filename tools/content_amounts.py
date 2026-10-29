# Amount-specific long-tail pages (29 Oct 2026): one EN + one HI page per basic pension amount,
# plus a /pension-by-amount/ hub pair. Executed inside tools/build.py (same globals).
# Every number comes from CONFIG in assets/app.js (read through Node) and the same rounding as calcPension().

_CFG = json.loads(subprocess.check_output(["node", "-e", "process.stdout.write(JSON.stringify(require(process.argv[1]).CONFIG))",
                                          os.path.join(ROOT, "assets", "app.js")]))
AMT_LIST = [9000, 10000, 12000, 15000, 18000, 20000, 22000, 25000, 30000, 35000, 40000, 45000,
            50000, 60000, 70000, 75000, 80000, 100000]
AMT_FACTORS = [repr(p["value"]) for p in _CFG["presetFactors"]]            # "1.92" … "3.833"
AMT_DR = _CFG["currentDR"]                                                  # 60
AMT_NEWDR = _CFG["newDRPercent"]                                            # 0 (assumption)
AMT_MIN = _CFG["minPension"]
AMT_MAX = _CFG["maxPension"]
AMT_MAXFN = _CFG["maxFamilyNormal"]
AMT_FPN = _CFG["familyNormalRate"]                                          # 30
AMT_FPE = _CFG["familyEnhancedRate"]                                        # 50


def _months(a, b):
    a, b = a.split("-"), b.split("-")
    return (int(b[0]) - int(a[0])) * 12 + int(b[1]) - int(a[1])


AMT_MONTHS = _months(_CFG["effectiveFrom"], _CFG["defaultPaymentMonth"])    # 21
_MON_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_MON_HI = ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]


def _ym(s, lang):
    y, m = s.split("-")
    return f"{(_MON_HI if lang == 'hi' else _MON_EN)[int(m) - 1]} {y}"


def _prev_ym(s):
    y, m = map(int, s.split("-"))
    return f"{y - 1}-12" if m == 1 else f"{y}-{m - 1:02d}"


EFF_EN, EFF_HI = _ym(_CFG["effectiveFrom"], "en"), _ym(_CFG["effectiveFrom"], "hi")
PAY_EN, PAY_HI = _ym(_CFG["defaultPaymentMonth"], "en"), _ym(_CFG["defaultPaymentMonth"], "hi")
LASTARR_EN, LASTARR_HI = _ym(_prev_ym(_CFG["defaultPaymentMonth"]), "en"), _ym(_prev_ym(_CFG["defaultPaymentMonth"]), "hi")


def amt_path(b, lang="en"):
    return ("/hi" if lang == "hi" else "") + f"/pension-{b}-8th-pay-commission/"


def _drv(x, pct):
    return up(Decimal(x) * Decimal(pct) / 100)


def amt_calc(b, f, age_pct=0):
    """Mirror of calcPension() in assets/app.js for a superannuation pension (no cap is reached for these amounts)."""
    add = _drv(b, age_pct)
    cur_dr = _drv(b + add, AMT_DR)
    cur_total = b + add + cur_dr
    nb = max(ceil_mul(b, f), ceil_mul(AMT_MIN, f))
    nb = min(nb, ceil_mul(AMT_MAX, f))
    nadd = _drv(nb, age_pct)
    ndr = _drv(nb + nadd, AMT_NEWDR)
    new_total = nb + nadd + ndr
    inc = new_total - cur_total
    return dict(add=add, cur_dr=cur_dr, cur_total=cur_total, nb=nb, nadd=nadd, ndr=ndr, new_total=new_total,
                inc=inc, arrears=max(0, inc) * AMT_MONTHS)


def _fx(f):
    return "3.00" if f in ("3", "3.0") else f


def amt_table(b, lang):
    today = amt_calc(b, "2.57")
    if lang == "en":
        cols = ["Scenario", "Basic pension", "Increase in basic", f"DR", "Total monthly pension", "Change vs today", f"Arrears ({AMT_MONTHS} months)"]
        first = ["Today (7th CPC)", inr(b), "—", f"{inr(today['cur_dr'])} ({AMT_DR}%)", inr(today["cur_total"]), "—", "—"]
        lab = lambda f: f"×{_fx(f)}" + (" (7th CPC factor)" if f == "2.57" else " (staff-side demand)" if f == "3.833" else "")
        cap = (f"Estimated 8th CPC pension for a ₹{inr(b)[1:]} basic pension, below age 80. New basic = {inr(b)} × factor, rounded up. "
               f"DR is today's official {AMT_DR}% on the current pension and is assumed to restart at {AMT_NEWDR}% on the new pension. "
               f"Totals are before commutation deduction, Fixed Medical Allowance and income tax. Estimate — not official.")
    else:
        cols = ["स्थिति", "मूल पेंशन", "मूल पेंशन में बढ़त", "DR", "कुल मासिक पेंशन", "आज से अंतर", f"एरियर ({AMT_MONTHS} महीने)"]
        first = ["आज (7वाँ आयोग)", inr(b), "—", f"{inr(today['cur_dr'])} ({AMT_DR}%)", inr(today["cur_total"]), "—", "—"]
        lab = lambda f: f"×{_fx(f)}" + (" (7वें आयोग का फैक्टर)" if f == "2.57" else " (कर्मचारी पक्ष की माँग)" if f == "3.833" else "")
        cap = (f"80 साल से कम उम्र, {inr(b)} मूल पेंशन पर 8वें वेतन आयोग का अनुमान। नई मूल पेंशन = {inr(b)} × फैक्टर, अगले रुपये तक ऊपर। "
               f"DR आज की आधिकारिक {AMT_DR}% दर है; नई पेंशन पर DR {AMT_NEWDR}% से शुरू मानी गई है। "
               f"कुल रकम कम्यूटेशन कटौती, फिक्स्ड मेडिकल अलाउंस और आयकर से पहले की है। अनुमान — आधिकारिक नहीं।")
    head = "".join(f'<th scope="col">{c}</th>' for c in cols)
    rows = ['<tr data-f="0">' + "".join(f"<td>{c}</td>" for c in first) + "</tr>"]
    for f in AMT_FACTORS:
        r = amt_calc(b, f)
        sign = "+" if r["inc"] >= 0 else "−"
        rows.append(f'<tr data-f="{f}" data-nb="{r["nb"]}" data-total="{r["new_total"]}" data-today="{r["cur_total"]}" '
                    f'data-inc="{r["inc"]}" data-arrears="{r["arrears"]}"><th scope="row">{lab(f)}</th><td>{inr(r["nb"])}</td>'
                    f'<td>+{inr(r["nb"] - b)}</td><td>{inr(r["ndr"])} ({AMT_NEWDR}%)</td><td>{inr(r["new_total"])}</td>'
                    f'<td>{sign}{inr(abs(r["inc"]))}</td><td>{inr(r["arrears"])}</td></tr>')
    return (f'<div class="tbl-wrap"><table class="data amt" id="amtTable" data-basic="{b}" data-dr="{AMT_DR}" data-months="{AMT_MONTHS}">'
            f'<caption>{cap}</caption><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def _neighbours(b):
    i = AMT_LIST.index(b)
    return (AMT_LIST[i - 1] if i > 0 else None), (AMT_LIST[i + 1] if i < len(AMT_LIST) - 1 else None)


def _special(b, lang):
    """Amount-specific facts, each derived from the rules in CONFIG."""
    en, hi = [], []
    if b == AMT_MIN:
        en.append(f"₹9,000 is the current <strong>minimum pension</strong> and minimum family pension. Under the 7th CPC the minimum was set at 50% of the minimum pay of ₹18,000. Our estimates assume a new minimum of ₹9,000 × the same factor, so nobody on the minimum falls behind the multiplier. See <a href=\"{L(lang, '/minimum-pension-8th-pay-commission/')}\">minimum pension under the 8th CPC</a>.")
        hi.append(f"₹9,000 आज की <strong>न्यूनतम पेंशन</strong> और न्यूनतम पारिवारिक पेंशन है। 7वें आयोग ने इसे न्यूनतम वेतन ₹18,000 का 50% रखा था। हमारे अनुमान में नई न्यूनतम पेंशन ₹9,000 × वही फैक्टर मानी गई है। देखें: <a href=\"/hi/minimum-pension-8th-pay-commission/\">8वें आयोग में न्यूनतम पेंशन</a>।")
    if b == AMT_MAXFN:
        en.append("₹75,000 is also the current <strong>maximum normal family pension</strong> (30% of the highest pay of ₹2,50,000). A family pensioner at this ceiling would see the same multiplier applied, assuming the ceiling is scaled by the same factor.")
        hi.append("₹75,000 आज की <strong>अधिकतम सामान्य पारिवारिक पेंशन</strong> भी है (सबसे ऊँचे वेतन ₹2,50,000 का 30%)। अगर यह सीमा भी उसी फैक्टर से बढ़े, तो इस सीमा पर पारिवारिक पेंशनभोगी को भी यही गुणा मिलेगा।")
    if b == 100000:
        en.append(f"₹1,00,000 is 80% of the current <strong>maximum pension of ₹1,25,000</strong>. The calculator assumes the maximum is scaled by the same factor (₹1,25,000 × 2.57 = {inr(ceil_mul(125000, '2.57'))}), so this pension is not capped in any scenario.")
        hi.append(f"₹1,00,000 आज की <strong>अधिकतम पेंशन ₹1,25,000</strong> का 80% है। कैलकुलेटर मानता है कि अधिकतम सीमा भी उसी फैक्टर से बढ़ेगी (₹1,25,000 × 2.57 = {inr(ceil_mul(125000, '2.57'))}), इसलिए इस पेंशन पर किसी भी स्थिति में सीमा नहीं लगती।")
    return en if lang == "en" else hi


def amt_page(b, lang):
    R = {f: amt_calc(b, f) for f in AMT_FACTORS}
    lo, mid, hi_ = R[AMT_FACTORS[0]], R["2.57"], R[AMT_FACTORS[-1]]
    r286 = R["2.86"]
    today = mid["cur_total"]
    a80 = amt_calc(b, "2.57", 20)
    comm = int(Decimal(b) * 40 / 100)
    lastpay = 2 * b
    fpn = min(max(_drv(lastpay, AMT_FPN), AMT_MIN), AMT_MAXFN)
    fpn_floor = _drv(lastpay, AMT_FPN) < AMT_MIN
    fpn_257 = max(ceil_mul(fpn, "2.57"), ceil_mul(AMT_MIN, "2.57"))
    fpn_lo = max(ceil_mul(fpn, AMT_FACTORS[0]), ceil_mul(AMT_MIN, AMT_FACTORS[0]))
    fpn_hi = max(ceil_mul(fpn, AMT_FACTORS[-1]), ceil_mul(AMT_MIN, AMT_FACTORS[-1]))
    fpn_today = fpn + _drv(fpn, AMT_DR)
    pre6 = round(b / 2.57)
    A = inr(b)
    prev_b, next_b = _neighbours(b)
    P = lambda h: L(lang, h)
    hub = P("/pension-by-amount/")
    nav_links = []
    sp = _special(b, lang)
    if lang == "en":
        if prev_b: nav_links.append(f'<a href="{amt_path(prev_b)}">← {inr(prev_b)} pension</a>')
        nav_links.append(f'<a href="{hub}">All amounts</a>')
        if next_b: nav_links.append(f'<a href="{amt_path(next_b)}">{inr(next_b)} pension →</a>')
        h1 = f"{A} Pension in 8th Pay Commission – How Much Will It Be?"
        lead = (f"A {A} basic pension is estimated to become <strong>{inr(lo['nb'])} to {inr(hi_['nb'])}</strong> a month under the 8th Pay Commission "
                f"(fitment factor {AMT_FACTORS[0]} to {AMT_FACTORS[-1]}). At 2.57, the factor the 7th CPC used, it would be <strong>{inr(mid['nb'])}</strong>. "
                f"Today the same pension pays {inr(today)} with {AMT_DR}% DR, so the real monthly gain at 2.57 is about {inr(mid['inc'])}. No factor is official yet.")
        desc = (f"{A} basic pension in the 8th CPC: estimated {inr(lo['nb'])}–{inr(hi_['nb'])} at factors {AMT_FACTORS[0]}–{AMT_FACTORS[-1]}, with DR, arrears and family pension.")
        who = (f"<p>A pensioner who retired after 1 January 2016 with at least 10 years' qualifying service gets 50% of last pay (or of the average of the last 10 months' pay, if that is higher). "
               f"So {A} is typically the pension of someone whose last basic pay was about <strong>{inr(lastpay)}</strong>. "
               + (f"For someone who retired before 2016, {A} usually means a 6th CPC pension of about {inr(pre6)} that was multiplied by 2.57 in 2016" if b != AMT_MIN else
                  "For someone who retired before 2016, it usually means a 6th CPC pension at the old ₹3,500 minimum, which × 2.57 fell just short and was stepped up to ₹9,000")
               + f". If you are not sure, the <a href=\"{P('/basic-pension-finder/')}\">basic pension finder</a> works it out from your bank credit or PPO.</p>")
        if b == AMT_MIN:
            who = who.replace(f"about <strong>{inr(lastpay)}</strong>", f"<strong>{inr(lastpay)} or less</strong> — ₹18,000 is the Level 1 starting pay and the lowest basic pay in the 7th CPC matrix")
        body = f"""
<p class="note">{" · ".join(nav_links)}</p>
<h2>{A} pension at every fitment factor</h2>
{amt_table(b, "en")}
<p>The range is wide because the factor is unknown. At the low-end media estimate of {AMT_FACTORS[0]}, the gain over today's {inr(today)} is only {inr(lo['inc'])} a month; at 2.86 it is {inr(r286['inc'])}; at the staff-side demand of 3.833 it is {inr(hi_['inc'])}. Any factor below 1.60 would leave a {A} pensioner with less than today, because the {AMT_DR}% DR is expected to be merged into the new basic.</p>
{"".join(f"<p>{x}</p>" for x in sp)}
<h2>Worked example: {A} at a factor of 2.57</h2>
<ol>
<li><strong>Pension today:</strong> {A} basic + {AMT_DR}% DR ({inr(mid['cur_dr'])}) = {inr(today)} a month.</li>
<li><strong>New basic pension:</strong> {A} × 2.57 = {inr(mid['nb'])} (rounded up to the next rupee).</li>
<li><strong>DR after revision:</strong> assumed to restart at {AMT_NEWDR}%, as after the 6th and 7th CPC, so the new total is {inr(mid['new_total'])}.</li>
<li><strong>Monthly gain:</strong> {inr(mid['new_total'])} − {inr(today)} = {inr(mid['inc'])} (about {round(mid['inc'] * 100 / today)}%).</li>
<li><strong>Later DR instalments</strong> would be added on {inr(mid['nb'])} from the first DR order after revision.</li>
</ol>
<p><strong>Aged 80 or more?</strong> Additional pension of 20% is added before DR. Today that makes {A} + {inr(a80['add'])} + DR {inr(a80['cur_dr'])} = {inr(a80['cur_total'])}. At 2.57 it would be {inr(a80['nb'])} + {inr(a80['nadd'])} = {inr(a80['new_total'])}. Higher slabs apply at 85, 90, 95 and 100.</p>
<h2>Estimated arrears on {A} pension</h2>
<p>The site assumes the revision takes effect from {EFF_EN} (the Government said that is "normally expected" from past practice; it is not decided) and that the new pension is first paid in {PAY_EN}. That gives {AMT_MONTHS} months of arrears, {EFF_EN} to {LASTARR_EN}. On {A}, arrears would be about <strong>{inr(mid['arrears'])}</strong> at 2.57, {inr(lo['arrears'])} at {AMT_FACTORS[0]} and {inr(hi_['arrears'])} at {AMT_FACTORS[-1]}, before tax. If DR rises again before implementation, today's total goes up and arrears come down. Change both dates in the <a href="{P('/')}">main calculator</a>.</p>
<h2>If you commuted 40% of {A}</h2>
<p>Commuting 40% means a fixed deduction of {inr(comm)} a month until restoration after 15 years. DR is still paid on the full {A}, so today the credit is {inr(today)} − {inr(comm)} = {inr(today - comm)} (before Fixed Medical Allowance and tax). In the 7th CPC revision the full pension was multiplied and the deduction stayed at the same rupee amount (DoPPW OM 04.08.2016). If that repeats, the credit at 2.57 would be {inr(mid['nb'])} − {inr(comm)} = <strong>{inr(mid['nb'] - comm)}</strong>, and the full {inr(mid['nb'])} once the commuted part is restored. Details: <a href="{P('/commutation-calculator/')}">commutation calculator</a>.</p>
<h2>Family pension after a {A} pension</h2>
<p>Normal family pension is {AMT_FPN}% of the employee's <em>last pay</em>, not of the pension. If {A} was 50% of a last pay of {inr(lastpay)}, the family pension would be {f"{inr(_drv(lastpay, AMT_FPN))} — below the minimum, so it is raised to " if fpn_floor else ""}<strong>{inr(fpn)}</strong> a month today, or {inr(fpn_today)} with {AMT_DR}% DR. At 2.57 that becomes {inr(fpn_257)} (range {inr(fpn_lo)} to {inr(fpn_hi)}). For a limited period the enhanced rate of {AMT_FPE}% of last pay — the full {A} — may apply instead. Use the <a href="{P('/family-pension-calculator/')}">family pension calculator</a> with the exact last pay from the PPO.</p>
<h2>Who gets a {A} pension?</h2>
{who}
<p>Next steps: try your exact figures in the <a href="{P('/')}">8th CPC pension calculator</a>, compare factors on the <a href="{P('/fitment-factor-calculator/')}">fitment factor page</a>, or see every amount side by side in the <a href="{P('/pension-chart/')}">pension chart</a>.</p>
<p class="note">{" · ".join(nav_links)}</p>
"""
        faqs = [
            (f"How much will {A} pension become in the 8th Pay Commission?",
             f"An estimated {inr(lo['nb'])} to {inr(hi_['nb'])} a month as basic pension, at fitment factors {AMT_FACTORS[0]} to {AMT_FACTORS[-1]}. At 2.57 it would be {inr(mid['nb'])}. No factor has been announced."),
            (f"How much will my {A} pension actually increase each month?",
             f"Today {A} pays {inr(today)} with {AMT_DR}% DR. If DR restarts at zero, the gain is {inr(lo['inc'])} at {AMT_FACTORS[0]}, {inr(mid['inc'])} at 2.57 and {inr(hi_['inc'])} at {AMT_FACTORS[-1]} a month."),
            (f"How much arrears will I get on {A} pension?",
             f"About {inr(mid['arrears'])} at 2.57 if the revision is effective from {EFF_EN} and first paid in {PAY_EN} ({AMT_MONTHS} months). Both dates are assumptions, not decisions."),
            (f"I commuted 40% of my {A} pension. What will I get after the 8th CPC?",
             f"The {inr(comm)} deduction is expected to stay the same until restoration. At 2.57 the credit would be about {inr(mid['nb'] - comm)} against {inr(today - comm)} today, before FMA and tax."),
            (f"What family pension will my spouse get on a {A} pension?",
             f"Normal family pension is {AMT_FPN}% of last pay. If {A} was 50% of a last pay of {inr(lastpay)}, it is {inr(fpn)} today and about {inr(fpn_257)} at 2.57."),
            (f"I am over 80 with {A} basic pension. What will I get?",
             f"With 20% additional pension at 80–84, today's total is {inr(a80['cur_total'])}. At 2.57 it would be {inr(a80['new_total'])} before any new DR."),
            (f"Will DR be added on top of the new {A} pension?",
             f"Not at the start. Past pay commissions merged DR into the new basic and restarted it at 0%. New DR instalments would then be paid on the revised basic, e.g. {inr(mid['nb'])} at 2.57."),
        ]
        title = h1
        crumb = f"{A} pension"
        parents = [("Pension by amount", "/pension-by-amount/")]
        related = [(amt_path(x), f"{inr(x)} pension in the 8th CPC", "estimate at every factor") for x in (prev_b, next_b) if x] + \
                  [("/pension-by-amount/", "Pension by amount", "all amounts from ₹9,000 to ₹1,00,000"),
                   ("/", REL_ALL["/"][0], REL_ALL["/"][1]), ("/fitment-factor-calculator/", REL_ALL["/fitment-factor-calculator/"][0], REL_ALL["/fitment-factor-calculator/"][1]),
                   ("/pension-chart/", REL_ALL["/pension-chart/"][0], REL_ALL["/pension-chart/"][1])]
    else:
        if prev_b: nav_links.append(f'<a href="{amt_path(prev_b, "hi")}">← {inr(prev_b)} पेंशन</a>')
        nav_links.append(f'<a href="{hub}">सभी राशियाँ</a>')
        if next_b: nav_links.append(f'<a href="{amt_path(next_b, "hi")}">{inr(next_b)} पेंशन →</a>')
        h1 = f"{A} पेंशन 8वें वेतन आयोग में कितनी होगी?"
        lead = (f"{A} मूल पेंशन 8वें वेतन आयोग में अनुमानित <strong>{inr(lo['nb'])} से {inr(hi_['nb'])}</strong> महीना हो सकती है "
                f"(फिटमेंट फैक्टर {AMT_FACTORS[0]} से {AMT_FACTORS[-1]})। 7वें आयोग वाले फैक्टर 2.57 पर यह <strong>{inr(mid['nb'])}</strong> होगी। "
                f"आज यही पेंशन {AMT_DR}% DR के साथ {inr(today)} देती है, इसलिए 2.57 पर असली मासिक बढ़त लगभग {inr(mid['inc'])} है। अभी कोई फैक्टर आधिकारिक नहीं है।")
        desc = (f"{A} मूल पेंशन 8वें वेतन आयोग में: फैक्टर {AMT_FACTORS[0]}–{AMT_FACTORS[-1]} पर अनुमानित {inr(lo['nb'])}–{inr(hi_['nb'])}, DR, एरियर और पारिवारिक पेंशन सहित।")
        who = (f"<p>1 जनवरी 2016 के बाद कम से कम 10 साल की अर्हक सेवा के साथ रिटायर होने वाले को अंतिम वेतन का 50% पेंशन मिलती है (या पिछले 10 महीनों के औसत वेतन का, अगर वह ज़्यादा हो)। "
               f"इसलिए {A} आम तौर पर उस व्यक्ति की पेंशन है जिसका अंतिम मूल वेतन लगभग <strong>{inr(lastpay)}</strong> था। "
               + (f"2016 से पहले रिटायर हुए व्यक्ति के लिए {A} का मतलब आम तौर पर लगभग {inr(pre6)} की 6वें आयोग वाली पेंशन है, जिसे 2016 में 2.57 से गुणा किया गया" if b != AMT_MIN else
                  "2016 से पहले रिटायर हुए व्यक्ति के लिए इसका मतलब आम तौर पर 6वें आयोग की पुरानी न्यूनतम पेंशन ₹3,500 है, जो × 2.57 पर थोड़ी कम पड़ती थी और ₹9,000 तक बढ़ाई गई")
               + f"। पक्का न हो तो <a href=\"/hi/basic-pension-finder/\">मूल पेंशन पता करें</a> टूल बैंक की रकम या PPO से निकाल देता है।</p>")
        if b == AMT_MIN:
            who = who.replace(f"लगभग <strong>{inr(lastpay)}</strong> था", f"<strong>{inr(lastpay)} या उससे कम</strong> था — ₹18,000 लेवल 1 का शुरुआती और 7वें आयोग की मैट्रिक्स का सबसे कम मूल वेतन है")
        body = f"""
<p class="note">{" · ".join(nav_links)}</p>
<h2>हर फिटमेंट फैक्टर पर {A} पेंशन</h2>
{amt_table(b, "hi")}
<p>फैक्टर तय न होने से दायरा बड़ा है। मीडिया के सबसे कम अनुमान {AMT_FACTORS[0]} पर आज के {inr(today)} से बढ़त सिर्फ़ {inr(lo['inc'])} महीना है; 2.86 पर {inr(r286['inc'])}; और कर्मचारी पक्ष की माँग 3.833 पर {inr(hi_['inc'])}। 1.60 से कम कोई भी फैक्टर {A} वाले पेंशनभोगी को आज से कम देगा, क्योंकि {AMT_DR}% DR नई मूल पेंशन में मिल जाने की उम्मीद है।</p>
{"".join(f"<p>{x}</p>" for x in sp)}
<h2>उदाहरण: 2.57 फैक्टर पर {A}</h2>
<ol>
<li><strong>आज की पेंशन:</strong> {A} मूल + {AMT_DR}% DR ({inr(mid['cur_dr'])}) = {inr(today)} महीना।</li>
<li><strong>नई मूल पेंशन:</strong> {A} × 2.57 = {inr(mid['nb'])} (अगले रुपये तक ऊपर)।</li>
<li><strong>बदलाव के बाद DR:</strong> {AMT_NEWDR}% से शुरू मानी गई, जैसा 6वें और 7वें आयोग के बाद हुआ था, इसलिए नई कुल रकम {inr(mid['new_total'])}।</li>
<li><strong>मासिक बढ़त:</strong> {inr(mid['new_total'])} − {inr(today)} = {inr(mid['inc'])} (लगभग {round(mid['inc'] * 100 / today)}%)।</li>
<li><strong>आगे की DR किस्तें</strong> बदलाव के बाद पहले DR आदेश से {inr(mid['nb'])} पर जुड़ेंगी।</li>
</ol>
<p><strong>उम्र 80 या ज़्यादा?</strong> DR से पहले 20% अतिरिक्त पेंशन जुड़ती है। आज: {A} + {inr(a80['add'])} + DR {inr(a80['cur_dr'])} = {inr(a80['cur_total'])}। 2.57 पर: {inr(a80['nb'])} + {inr(a80['nadd'])} = {inr(a80['new_total'])}। 85, 90, 95 और 100 साल पर दर और बढ़ती है।</p>
<h2>{A} पेंशन पर अनुमानित एरियर</h2>
<p>साइट मानती है कि बदलाव {EFF_HI} से लागू होगा (सरकार ने कहा है कि पुराने चलन के अनुसार यही "सामान्य रूप से अपेक्षित" है; यह तय नहीं है) और नई पेंशन पहली बार {PAY_HI} में मिलेगी। इससे {EFF_HI} से {LASTARR_HI} तक {AMT_MONTHS} महीने का एरियर बनता है। {A} पर एरियर 2.57 पर लगभग <strong>{inr(mid['arrears'])}</strong>, {AMT_FACTORS[0]} पर {inr(lo['arrears'])} और {AMT_FACTORS[-1]} पर {inr(hi_['arrears'])} होगा, टैक्स से पहले। लागू होने से पहले DR फिर बढ़ी तो आज की कुल रकम बढ़ेगी और एरियर घटेगा। दोनों तारीखें <a href="/hi/">मुख्य कैलकुलेटर</a> में बदलें।</p>
<h2>अगर आपने {A} का 40% कम्यूट किया है</h2>
<p>40% कम्यूट करने पर 15 साल बाद बहाली तक हर महीने {inr(comm)} की तय कटौती होती है। DR फिर भी पूरी {A} पर मिलती है, इसलिए आज खाते में {inr(today)} − {inr(comm)} = {inr(today - comm)} आते हैं (FMA और टैक्स से पहले)। 7वें आयोग में पूरी पेंशन को गुणा किया गया था और कटौती उतने ही रुपये रही (DoPPW ज्ञापन 04.08.2016)। ऐसा ही हुआ तो 2.57 पर खाते में {inr(mid['nb'])} − {inr(comm)} = <strong>{inr(mid['nb'] - comm)}</strong> आएँगे, और बहाली के बाद पूरे {inr(mid['nb'])}। विस्तार: <a href="/hi/commutation-calculator/">कम्यूटेशन कैलकुलेटर</a>।</p>
<h2>{A} पेंशन के बाद पारिवारिक पेंशन</h2>
<p>सामान्य पारिवारिक पेंशन कर्मचारी के <em>अंतिम वेतन</em> का {AMT_FPN}% होती है, पेंशन का नहीं। अगर {A} अंतिम वेतन {inr(lastpay)} का 50% था, तो पारिवारिक पेंशन {f"{inr(_drv(lastpay, AMT_FPN))} बनती है, जो न्यूनतम से कम है, इसलिए आज " if fpn_floor else "आज "}<strong>{inr(fpn)}</strong> महीना होगी, और {AMT_DR}% DR मिलाकर {inr(fpn_today)}। 2.57 पर यह {inr(fpn_257)} होगी (दायरा {inr(fpn_lo)} से {inr(fpn_hi)})। कुछ समय के लिए अंतिम वेतन का {AMT_FPE}% — यानी पूरी {A} — बढ़ी हुई दर पर मिल सकती है। PPO में दिए अंतिम वेतन के साथ <a href="/hi/family-pension-calculator/">पारिवारिक पेंशन कैलकुलेटर</a> इस्तेमाल करें।</p>
<h2>{A} पेंशन किसे मिलती है?</h2>
{who}
<p>आगे: अपने सटीक आँकड़े <a href="/hi/">8वां वेतन आयोग पेंशन कैलकुलेटर</a> में डालें, <a href="/hi/fitment-factor-calculator/">फिटमेंट फैक्टर पेज</a> पर फैक्टर मिलाएँ, या <a href="/hi/pension-chart/">पेंशन चार्ट</a> में सारी राशियाँ एक साथ देखें।</p>
<p class="note">{" · ".join(nav_links)}</p>
"""
        faqs = [
            (f"{A} पेंशन 8वें वेतन आयोग में कितनी हो जाएगी?",
             f"फिटमेंट फैक्टर {AMT_FACTORS[0]} से {AMT_FACTORS[-1]} पर मूल पेंशन अनुमानित {inr(lo['nb'])} से {inr(hi_['nb'])} महीना। 2.57 पर {inr(mid['nb'])}। कोई फैक्टर घोषित नहीं हुआ है।"),
            (f"मेरी {A} पेंशन हर महीने असल में कितनी बढ़ेगी?",
             f"आज {A} पर {AMT_DR}% DR मिलाकर {inr(today)} मिलते हैं। DR शून्य से शुरू हो तो बढ़त {AMT_FACTORS[0]} पर {inr(lo['inc'])}, 2.57 पर {inr(mid['inc'])} और {AMT_FACTORS[-1]} पर {inr(hi_['inc'])} महीना होगी।"),
            (f"{A} पेंशन पर कितना एरियर मिलेगा?",
             f"अगर बदलाव {EFF_HI} से लागू हो और पहला भुगतान {PAY_HI} में हो ({AMT_MONTHS} महीने), तो 2.57 पर लगभग {inr(mid['arrears'])}। दोनों तारीखें मान्यता हैं, फ़ैसला नहीं।"),
            (f"मैंने {A} पेंशन का 40% कम्यूट किया है। 8वें आयोग के बाद कितना मिलेगा?",
             f"{inr(comm)} की कटौती बहाली तक उतनी ही रहने की उम्मीद है। 2.57 पर खाते में लगभग {inr(mid['nb'] - comm)} आएँगे, आज के {inr(today - comm)} की जगह (FMA और टैक्स से पहले)।"),
            (f"{A} पेंशन पर पति/पत्नी को कितनी पारिवारिक पेंशन मिलेगी?",
             f"सामान्य पारिवारिक पेंशन अंतिम वेतन का {AMT_FPN}% है। अगर {A} अंतिम वेतन {inr(lastpay)} का 50% थी, तो आज {inr(fpn)} और 2.57 पर लगभग {inr(fpn_257)}।"),
            (f"मेरी उम्र 80 से ज़्यादा है और मूल पेंशन {A} है। कितना मिलेगा?",
             f"80–84 साल पर 20% अतिरिक्त पेंशन के साथ आज कुल {inr(a80['cur_total'])}। 2.57 पर नई DR से पहले {inr(a80['new_total'])}।"),
            (f"क्या नई {A} पेंशन पर DR अलग से जुड़ेगी?",
             f"शुरुआत में नहीं। पिछले वेतन आयोगों ने DR को नई मूल पेंशन में मिला दिया और DR 0% से शुरू की। फिर नई किस्तें बदली हुई मूल पेंशन पर मिलेंगी, जैसे 2.57 पर {inr(mid['nb'])} पर।"),
        ]
        title = h1
        crumb = f"{A} पेंशन"
        parents = [("राशि के अनुसार पेंशन", "/hi/pension-by-amount/")]
        related = [(amt_path(x, "hi"), f"8वें आयोग में {inr(x)} पेंशन", "हर फैक्टर पर अनुमान") for x in (prev_b, next_b) if x] + \
                  [("/hi/pension-by-amount/", "राशि के अनुसार पेंशन", "₹9,000 से ₹1,00,000 तक सभी राशियाँ")] + \
                  rel_hi("/", "/fitment-factor-calculator/", "/pension-chart/")
    return dict(path=amt_path(b, lang), lang=lang, crumb=crumb, parents=parents, title=title, desc=desc, h1=h1, lead=lead,
                body=body, faqs=faqs, related=related, lastmod="2026-10-29", published="2026-10-29",
                sources=["om_0816", "om_dr", "pm_dr", "pib_tor", "cpc8_comp", "portal_rb", "portal_faq", "comm_table"])


for _b in AMT_LIST:
    PAGES.append(amt_page(_b, "en"))
    PAGES.append(amt_page(_b, "hi"))


# ------------------------------------------------------------------ hub
def _hub_rows(lang):
    out = []
    for b in AMT_LIST:
        lo, mid, hi_ = amt_calc(b, AMT_FACTORS[0]), amt_calc(b, "2.57"), amt_calc(b, AMT_FACTORS[-1])
        label = f"{inr(b)} pension" if lang == "en" else f"{inr(b)} पेंशन"
        out.append([f'<a href="{amt_path(b, lang)}">{label}</a>', inr(mid["cur_total"]), f"{inr(lo['nb'])} – {inr(hi_['nb'])}",
                    inr(mid["nb"]), "+" + inr(mid["inc"])])
    return out


_hub_cols = {"en": ["Basic pension (7th CPC)", f"Total today ({AMT_DR}% DR)", f"New basic, ×{AMT_FACTORS[0]} to ×{AMT_FACTORS[-1]}", "New basic at ×2.57", "Monthly gain at ×2.57"],
             "hi": ["मूल पेंशन (7वाँ आयोग)", f"आज कुल ({AMT_DR}% DR)", f"नई मूल पेंशन, ×{AMT_FACTORS[0]} से ×{AMT_FACTORS[-1]}", "×2.57 पर नई मूल पेंशन", "×2.57 पर मासिक बढ़त"]}

PAGES.append(dict(
    path="/pension-by-amount/", crumb="Pension by amount", lastmod="2026-10-29", published="2026-10-29",
    title="8th CPC Pension by Amount – ₹9,000 to ₹1,00,000 Explained",
    desc="Pick your basic pension from ₹9,000 to ₹1,00,000 to see the estimated 8th CPC pension, DR, arrears, commutation and family pension.",
    h1="8th Pay Commission Pension by Amount",
    lead=f"Choose your current 7th CPC basic pension to open a page with the estimated 8th CPC pension at every fitment factor ({AMT_FACTORS[0]} to {AMT_FACTORS[-1]}), today's DR, arrears, commutation and family pension for that exact amount.",
    body=f"""
{ex_table("en", _hub_rows("en"), _hub_cols["en"])}
<p class="fine">Estimates for a pensioner below age 80. New basic = basic pension × factor, rounded up; DR is assumed to restart at {AMT_NEWDR}% on the new pension. No fitment factor is official yet.</p>
<h2>What each amount page shows</h2>
<ul>
<li>The new basic pension at all {len(AMT_FACTORS)} factors the site uses, the increase, DR and total monthly pension.</li>
<li>A step-by-step worked example at 2.57 and the figure for pensioners aged 80 or more.</li>
<li>Estimated arrears from {EFF_EN} to {LASTARR_EN} ({AMT_MONTHS} months) — an assumption, not a decision.</li>
<li>What happens if 40% of the pension was commuted, and the likely family pension.</li>
</ul>
<p>Your amount not listed? Enter it in the <a href="/">main calculator</a>, or use the <a href="/pension-chart/">pension chart</a>, which goes up to ₹1,25,000. If you only know your bank credit, start with the <a href="/basic-pension-finder/">basic pension finder</a>.</p>
""",
    faqs=[
        ("Which amount should I pick?", "Your basic pension as written on the PPO or pension slip — before DR, additional pension and any commutation deduction."),
        ("Are these figures official?", "No. The 8th Pay Commission has not recommended a fitment factor. Every figure is an estimate using the 7th CPC method."),
        ("Why is the gain smaller than the jump in basic pension?", f"Because today's {AMT_DR}% DR is expected to be merged into the new basic and restart at zero. A factor of 1.60 would only keep the total the same."),
        ("Do the pages work for family pension?", "The table works for any basic amount, including a basic family pension; each page also explains the family pension that follows a retirement pension."),
    ],
    sources=["om_0816", "om_dr", "pm_dr", "pib_tor", "portal_rb"],
    related=rel("/", "/pension-chart/", "/fitment-factor-calculator/", "/basic-pension-finder/", "/minimum-pension-8th-pay-commission/"),
))
PAGES.append(dict(
    path="/hi/pension-by-amount/", lang="hi", crumb="राशि के अनुसार पेंशन", lastmod="2026-10-29", published="2026-10-29",
    title="राशि के अनुसार 8वें वेतन आयोग की पेंशन – ₹9,000 से ₹1,00,000",
    desc="₹9,000 से ₹1,00,000 तक अपनी मूल पेंशन चुनें और 8वें आयोग में अनुमानित पेंशन, DR, एरियर, कम्यूटेशन और पारिवारिक पेंशन देखें।",
    h1="राशि के अनुसार 8वें वेतन आयोग की पेंशन",
    lead=f"अपनी मौजूदा 7वें आयोग वाली मूल पेंशन चुनें। हर पेज पर उसी राशि के लिए हर फिटमेंट फैक्टर ({AMT_FACTORS[0]} से {AMT_FACTORS[-1]}) पर अनुमानित पेंशन, आज की DR, एरियर, कम्यूटेशन और पारिवारिक पेंशन है।",
    body=f"""
{ex_table("hi", _hub_rows("hi"), _hub_cols["hi"])}
<p class="fine">80 साल से कम उम्र के पेंशनभोगी के लिए अनुमान। नई मूल पेंशन = मूल पेंशन × फैक्टर, अगले रुपये तक ऊपर; नई पेंशन पर DR {AMT_NEWDR}% से शुरू मानी गई है। अभी कोई फिटमेंट फैक्टर आधिकारिक नहीं है।</p>
<h2>हर राशि वाले पेज पर क्या है</h2>
<ul>
<li>साइट के सभी {len(AMT_FACTORS)} फैक्टरों पर नई मूल पेंशन, बढ़त, DR और कुल मासिक पेंशन।</li>
<li>2.57 पर चरण-दर-चरण उदाहरण और 80 साल या ज़्यादा उम्र वालों का आँकड़ा।</li>
<li>{EFF_HI} से {LASTARR_HI} तक ({AMT_MONTHS} महीने) का अनुमानित एरियर — यह मान्यता है, फ़ैसला नहीं।</li>
<li>40% पेंशन कम्यूट होने पर क्या होगा, और संभावित पारिवारिक पेंशन।</li>
</ul>
<p>आपकी राशि सूची में नहीं? उसे <a href="/hi/">मुख्य कैलकुलेटर</a> में डालें, या <a href="/hi/pension-chart/">पेंशन चार्ट</a> देखें जो ₹1,25,000 तक जाता है। सिर्फ़ बैंक की रकम पता हो तो <a href="/hi/basic-pension-finder/">मूल पेंशन पता करें</a> से शुरू करें।</p>
""",
    faqs=[
        ("मुझे कौन-सी राशि चुननी चाहिए?", "PPO या पेंशन स्लिप में लिखी मूल पेंशन — DR, अतिरिक्त पेंशन और कम्यूटेशन कटौती से पहले की।"),
        ("क्या ये आँकड़े आधिकारिक हैं?", "नहीं। 8वें वेतन आयोग ने अभी कोई फिटमेंट फैक्टर नहीं सुझाया है। हर आँकड़ा 7वें आयोग के तरीके से बना अनुमान है।"),
        ("बढ़त मूल पेंशन की छलाँग से कम क्यों है?", f"क्योंकि आज की {AMT_DR}% DR नई मूल पेंशन में मिलकर शून्य से शुरू होने की उम्मीद है। 1.60 का फैक्टर सिर्फ़ कुल रकम बराबर रखेगा।"),
        ("क्या ये पेज पारिवारिक पेंशन के लिए भी हैं?", "तालिका किसी भी मूल राशि पर चलती है, मूल पारिवारिक पेंशन पर भी; हर पेज यह भी बताता है कि सेवानिवृत्ति पेंशन के बाद पारिवारिक पेंशन कितनी होगी।"),
    ],
    sources=["om_0816", "om_dr", "pm_dr", "pib_tor", "portal_rb"],
    related=rel_hi("/", "/pension-chart/", "/fitment-factor-calculator/", "/basic-pension-finder/", "/minimum-pension-8th-pay-commission/"),
))

# hub links from the homepage and the pension chart (EN + HI)
_hub_en = '<h2>Pension by amount</h2><p>Want the full picture for one figure? See the <a href="/pension-by-amount/">8th CPC pension by amount</a> pages — ₹9,000 to ₹1,00,000, each with DR, arrears, commutation and family pension worked out.</p>'
_hub_hi = '<h2>राशि के अनुसार पेंशन</h2><p>किसी एक राशि की पूरी तस्वीर चाहिए? <a href="/hi/pension-by-amount/">राशि के अनुसार 8वें आयोग की पेंशन</a> देखें — ₹9,000 से ₹1,00,000 तक, हर पेज पर DR, एरियर, कम्यूटेशन और पारिवारिक पेंशन के साथ।</p>'
for _pth, _txt in (("/", _hub_en), ("/pension-chart/", _hub_en), ("/hi/", _hub_hi), ("/hi/pension-chart/", _hub_hi)):
    _pg = page_by_path(_pth)
    _pg["body"] = _pg["body"] + _txt
for _pth in ("/", "/pension-chart/"):
    _pg = page_by_path(_pth)
    if "/pension-by-amount/" not in [x[0] for x in _pg.get("related", [])]:
        _pg["related"] = list(_pg.get("related", [])) + [("/pension-by-amount/", "Pension by amount", "₹9,000 to ₹1,00,000, one page per amount")]
for _pth in ("/hi/", "/hi/pension-chart/"):
    _pg = page_by_path(_pth)
    if not any(x[0].endswith("/pension-by-amount/") for x in _pg.get("related", [])):
        _pg["related"] = list(_pg.get("related", [])) + [("/hi/pension-by-amount/", "राशि के अनुसार पेंशन", "₹9,000 से ₹1,00,000, हर राशि का अलग पेज")]
