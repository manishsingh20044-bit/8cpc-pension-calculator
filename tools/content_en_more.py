# English additions (28 Oct 2026): deeper tool pages, new pages, E-E-A-T. Executed inside tools/build.py.
import re as _re

FX = ["1.92", "2.57", "2.86", "3.833"]
_gain_cols_en = ["Basic pension", "Total today (60% DR)"] + [f"New basic at ×{f} (real gain)" for f in FX]


def _hi_link(path, label):
    return f'<p class="note" lang="hi">यह पेज <a href="{hi_path(path)}" hreflang="hi-IN">हिंदी में पढ़ें</a> — {label}</p>'


def _strip_hi_section(body, path, label):
    return _re.sub(r'<section lang="hi">.*?</section>', _hi_link(path, label), body, flags=_re.S)


def extend(path, body="", faqs=(), sources=None, related_add=()):
    p = page_by_path(path)
    p["body"] = p["body"] + body
    p["faqs"] = list(p.get("faqs", [])) + list(faqs)
    if sources:
        p["sources"] = sources
    for r in related_add:
        if r not in [x[0] for x in p.get("related", [])]:
            p["related"] = list(p.get("related", [])) + rel(r)


# ------------------------------------------------------------------ home
extend("/", body=f"""
<h2>Who this calculator is for</h2>
<ul>
<li><strong>Central government civil pensioners</strong> drawing a pension under the CCS (Pension) Rules — including railway, postal, CAPF and All India Services pensioners, whose DR is revised by the same orders.</li>
<li><strong>Family pensioners</strong> (widows, widowers, eligible children and parents) — choose a family pension type in the form.</li>
<li><strong>Armed forces pensioners</strong> who want a first estimate of the basic-pension element (read the <a href="/defence-pension-calculator/">defence notes</a> first).</li>
<li><strong>Sons and daughters</strong> helping a parent understand the headlines. Every figure is shown with the steps, so you can explain it at the dinner table.</li>
</ul>
<p>It is <strong>not</strong> designed for state government pensioners, bank pensioners or EPS-95 pensioners — their pensions follow different rules and are not revised by the Central Pay Commission.</p>

<h2>How to use it in four steps</h2>
<ol>
<li><strong>Find your basic pension.</strong> It is printed on your PPO or pension slip as "basic pension". It is not the amount credited to your bank. If you only know the bank credit, use the <a href="/basic-pension-finder/">basic pension finder</a> first.</li>
<li><strong>Enter your age.</strong> From 80 years the additional pension (20% to 100%) is added automatically, and it also rises with the fitment factor.</li>
<li><strong>Pick a fitment factor.</strong> Start with 2.57 (what the 7th CPC used), then compare 1.92 and 3.833 to see the full range. None of these is official.</li>
<li><strong>Check the assumptions.</strong> DR is set to today's 60%, the date of effect to 1 January 2026 and the payment month to a date you can change. Press Calculate and read the "how this was worked out" box.</li>
</ol>

<h2>Worked examples: what different pensions could become</h2>
<p>The table applies four fitment factors to four common basic pensions for a pensioner below 80. "Real gain" is the new basic pension minus today's total pension (basic + 60% DR), because DR is expected to restart from zero. All figures are estimates.</p>
{ex_table("en", gain_rows([9000, 15000, 25000, 50000], FX), _gain_cols_en)}
<p>Two things stand out. First, at 1.92 a pensioner on ₹25,000 would gain ₹8,000 a month (20%), not the 92% that the factor alone suggests. Second, the minimum pension rises with the factor too: if ₹9,000 × factor becomes the new floor, nobody falls below it.</p>

<h2>Common mistakes to avoid</h2>
<ul>
<li><strong>Entering the bank credit instead of basic pension.</strong> The credit includes DR and medical allowance and excludes the commutation deduction, so it overstates or understates the result.</li>
<li><strong>Multiplying the total pension by the factor.</strong> The factor applies to basic pension only. DR already absorbed into the factor is not paid again.</li>
<li><strong>Treating a demand or estimate as a decision.</strong> 3.833 is a staff-side demand; 1.92–2.86 are media estimates. Only a Cabinet decision on pib.gov.in followed by a government order is official.</li>
<li><strong>Forgetting the commutation deduction.</strong> If you commuted part of your pension, the rupee deduction continues until restoration — see the <a href="/commutation-calculator/">commutation calculator</a>.</li>
<li><strong>Counting arrears as certain.</strong> Arrears depend on the official date of effect, which has not been fixed.</li>
</ul>
<p>Other new guides: <a href="/minimum-pension-8th-pay-commission/">minimum pension under the 8th CPC</a> and the <a href="/life-certificate/">life certificate (Jeevan Pramaan) guide</a> for this November.</p>
""", faqs=[
    ("Will DA/DR be merged with basic pension before the 8th Pay Commission?", "The Government told Parliament in December 2025 that there was no proposal to merge DA with basic pay. In past pay commissions the accumulated DR was absorbed into the new pension through the fitment factor on the date of effect, and DR restarted at zero."),
    ("Does the 8th Pay Commission cover pensioners who retired before 2016?", "Pension matters are within the Commission's Terms of Reference, and every past pay commission revised the pensions of earlier retirees. How older pensioners will be treated — a single factor or a notional-pay method like the 7th CPC's — will be known only from the report."),
    ("How do I find my basic pension?", "It is on your PPO or pension slip. If you only know the amount credited to your bank, the basic pension finder works backwards from it, removing DR, Fixed Medical Allowance and the commutation deduction."),
    ("Is the commuted part of pension revised by the fitment factor?", "Under the 7th CPC the full basic pension (including the commuted portion) was multiplied by 2.57, and the commuted amount continued to be deducted in rupees until restoration. The calculator assumes the 8th CPC will work the same way."),
    ("Why is my real increase smaller than the fitment factor?", "Because Dearness Relief (60% now) is expected to restart from zero. A factor of 1.60 would only keep your total pension the same; only the part above that is a real increase."),
    ("Will the minimum pension of ₹9,000 also go up?", "The 7th CPC raised the minimum from ₹3,500 to ₹9,000 (×2.57). The calculator assumes the new minimum will be ₹9,000 × the chosen factor. The actual figure will be in the 8th CPC report."),
], sources=SRC_TOOL + ["pib_all", "portal_faq"], related_add=("/commutation-calculator/", "/minimum-pension-8th-pay-commission/", "/life-certificate/"))

# ------------------------------------------------------------------ fitment factor
_be = [[f"{d}%", f"{1 + d / 100:.2f}", inr(up(Decimal(20000) * (100 + d) / 100)), inr(ceil_mul(20000, "2.57")), inr(ceil_mul(20000, "2.57") - up(Decimal(20000) * (100 + d) / 100))] for d in (60, 63, 66)]
extend("/fitment-factor-calculator/", body=f"""
<h2>Who should use this page</h2>
<p>Use this page if you have seen a "new fitment factor" headline and want to know what it means for your own pension, or if you want to compare the realistic range before the Commission reports. Pensioners, family pensioners and employees nearing retirement can all use it; the reverse calculator is also useful for checking numbers quoted in news videos.</p>

<h2>How to use the two calculators</h2>
<ol>
<li>In the main calculator, enter your 7th CPC basic pension and age, then switch the fitment factor between 1.92, 2.57, 2.86 and 3.833. Each result shows the new basic pension and the real change in your monthly total.</li>
<li>Choose "Custom" to test any other number, for example 2.47 or 3.0.</li>
<li>In the reverse box, enter an old amount and a new amount from a headline to see the factor it implies.</li>
</ol>

<h2>Worked example: how the break-even point moves with DR</h2>
<p>For a ₹20,000 basic pension, the break-even factor is simply 1 + DR. If more DR instalments are granted before the 8th CPC is implemented, a given factor delivers a smaller real gain. The 63% and 66% rows are hypothetical — only 60% is official.</p>
{ex_table("en", _be, ["DR at implementation", "Break-even factor", "Total today on ₹20,000", "New basic at ×2.57", "Real gain at ×2.57"])}

<h2>Common mistakes with fitment factors</h2>
<ul>
<li><strong>Applying the factor to the total pension.</strong> It applies to basic pension only.</li>
<li><strong>Comparing new basic with old basic.</strong> Compare the new basic with today's basic plus DR — that is what you actually receive.</li>
<li><strong>Assuming one factor for everyone.</strong> The Commission could recommend different methods for older pensioners or for different levels, as some associations have asked.</li>
<li><strong>Trusting "confirmed" factors on social media.</strong> As of {LAST_UPDATED_HUMAN} there is none.</li>
</ul>
""", faqs=[
    ("What is the formula for the fitment factor?", "Fitment factor = new basic pension ÷ old basic pension. Historically it has been derived from the proposed minimum pay: the 7th CPC raised minimum pay from ₹7,000 to ₹18,000, a ratio of 2.57."),
    ("Is the fitment factor the same for pensioners and employees?", "Under the 7th CPC the same 2.57 multiplier was used for employees' pay and for pre-2016 pensioners' pension (with a notional-pay alternative for pensioners). The 8th CPC's approach is not known yet."),
    ("How much will pension increase at a fitment factor of 2.86?", "Basic pension rises 2.86 times. Because DR (60%) restarts at zero, the total monthly pension rises by about 79% — for example, ₹20,000 basic goes from ₹32,000 today to ₹57,200."),
    ("Why do media reports quote 1.92 or 2.28?", "These are analysts' estimates based on assumptions about inflation and fiscal space. They are not recommendations of the Commission or decisions of the Government."),
    ("Can the fitment factor be lower than 2.57?", "Yes, it is possible. The Terms of Reference ask the Commission to keep fiscal prudence and the unfunded cost of pensions in view. Any factor above about 1.60 (with DR at 60%) still increases the total pension."),
    ("When will the fitment factor be announced?", "Only after the Commission submits its report (due around May 2027) and the Government decides on it. The 7th CPC reported in November 2015 and the Cabinet decided in June 2016."),
], sources=SRC_TOOL + ["labour"], related_add=("/minimum-pension-8th-pay-commission/",))

# ------------------------------------------------------------------ family pension
_fp = []
for lp in (18000, 35400, 56100, 100000):
    n, e = max(up(Decimal(lp) * 30 / 100), 9000), max(up(Decimal(lp) / 2), 9000)
    _fp.append([inr(lp), inr(n), inr(e), inr(ceil_mul(n, "2.57")), inr(ceil_mul(e, "2.57"))])
extend("/family-pension-calculator/", body=f"""
<h2>Who this page is for</h2>
<p>Widows and widowers of central government employees and pensioners, and other eligible family members — children up to 25, unmarried, widowed or divorced daughters, disabled children and siblings, and dependent parents — in the order laid down in the family pension rules. It also helps families who must claim family pension after a pensioner's death and want to know what to expect.</p>

<h2>How to use the calculator</h2>
<ol>
<li>If you know your current basic family pension (from the PPO or bank slip), enter it and choose normal or enhanced rate.</li>
<li>If you only know the employee's last basic pay, use the helper box: it works out 30% and 50% and copies the figure into the calculator.</li>
<li>Enter the family pensioner's age — additional family pension starts at 80.</li>
<li>Choose a fitment factor and press Calculate. Run it twice if your enhanced rate will end before the revision.</li>
</ol>

<h2>Worked examples from last pay</h2>
{ex_table("en", _fp, ["Last basic pay", "Normal family pension (30%, min ₹9,000)", "Enhanced (50%)", "Normal at ×2.57 (estimate)", "Enhanced at ×2.57 (estimate)"])}
<p>At ₹18,000 last pay, 30% is ₹5,400, so the ₹9,000 minimum applies. Enhanced family pension cannot exceed the pension that was authorised to a retired employee.</p>

<h2>Common mistakes</h2>
<ul>
<li><strong>Using the employee's pension instead of last pay.</strong> Family pension is a percentage of last pay, not of pension (for post-2016 cases).</li>
<li><strong>Assuming enhanced rate lasts for life.</strong> It lasts 10 years after a death in service, or seven years / until the deceased would have turned 67 after a death following retirement.</li>
<li><strong>Not informing the bank promptly.</strong> The pensioner's death should be reported to the bank within a month; where a joint account exists, the spouse can claim with a simple letter and the death certificate.</li>
<li><strong>Missing the life certificate.</strong> Family pensioners must also submit one every November — see the <a href="/life-certificate/">life certificate guide</a>.</li>
</ul>
""", faqs=[
    ("Who is eligible for family pension and in what order?", "First the widow or widower (until death or remarriage, with an exception for a childless widow with low income), then children up to 25, then disabled children for life, then unmarried, widowed or divorced daughters above 25, then dependent parents, then disabled dependent siblings."),
    ("How does a spouse claim family pension after a pensioner's death?", "Where the pension was credited to a joint account, the spouse can inform the bank by a simple letter with a copy of the death certificate. Otherwise Form 14 is submitted to the pension disbursing bank."),
    ("Is family pension paid to a divorced daughter?", "Yes, subject to the rules, including where divorce proceedings were filed during the lifetime of the employee, pensioner or spouse and the divorce took place after their death (DoPPW OM dated 19.07.2017)."),
    ("Do family pensioners get Fixed Medical Allowance?", "Family pensioners living in areas not covered by CGHS, and not using CGHS for OPD, receive Fixed Medical Allowance of ₹1,000 a month."),
    ("Is enhanced family pension available if the employee had less than seven years of service?", "Yes. Since 1 October 2019 the enhanced rate is payable to the family of an employee who dies in service even before completing seven years."),
], sources=["portal_faq", "pib_min", "om_dr", "om_0816", "doppw", "pib_tor", "cpc8_comp"], related_add=("/life-certificate/",))

# ------------------------------------------------------------------ defence
_dr_rows = [[inr(b), inr(b + up(Decimal(b) * 60 / 100)), inr(ceil_mul(b, "2.57")), inr(ceil_mul(b, "2.86")), inr(ceil_mul(b, "3.833"))] for b in (9000, 18000, 25000, 40000)]
extend("/defence-pension-calculator/", body=f"""
<h2>Who should use this page</h2>
<p>Ex-servicemen of the Army, Navy and Air Force drawing service pension, their widows drawing ordinary family pension, and families helping them read the numbers. If your pension includes a disability or war injury element, or you are awaiting an OROP revision, use the result only as a rough guide to the service element.</p>

<h2>How to use the calculator</h2>
<ol>
<li>Log in to SPARSH (or check your e-PPO / pension slip) and note the <strong>basic pension</strong> — not the total credited.</li>
<li>Enter it with your age; additional pension at 80+ is added automatically.</li>
<li>For a widow's ordinary family pension, choose a family pension type.</li>
<li>Compare factors 2.57, 2.86 and 3.833. Remember that MoD orders usually follow the civilian orders.</li>
</ol>

<h2>Worked examples (service element only)</h2>
{ex_table("en", _dr_rows, ["Basic pension", "Total today (60% DR)", "New basic ×2.57", "New basic ×2.86", "New basic ×3.833"])}
<p>No official rank-wise 8th CPC table exists. We have deliberately not published a rank-wise table, because the 7th CPC's rank-wise figures for armed forces pensioners came from separate Ministry of Defence orders and OROP tables, and no equivalent exists for the 8th CPC.</p>

<h2>Common mistakes</h2>
<ul>
<li><strong>Including the disability element.</strong> Enter only service pension or ordinary family pension.</li>
<li><strong>Using a month with arrears.</strong> OROP or DR arrears make one month's credit look larger.</li>
<li><strong>Sharing SPARSH details.</strong> SPARSH has warned that no WhatsApp numbers are authorised for SPARSH queries. Use the portal, the helpline 1800-180-5325 or an authorised SPARSH Service Centre.</li>
</ul>
""", faqs=[
    ("How do I find my basic pension in SPARSH?", "Log in to the SPARSH portal and open your entitlements or pension slip; the e-PPO is in the document repository. The basic pension is shown separately from DR and other elements."),
    ("Where can defence pensioners submit the life certificate?", "Through SPARSH (digital via Jeevan Pramaan, including face authentication, or manual life certificate), at SPARSH Service Centres, banks or CSCs. Check the date window announced by SPARSH / PCDA (Pension) for your category."),
    ("Will OROP be revised along with the 8th Pay Commission?", "OROP revisions are carried out separately by the Ministry of Defence. How an 8th CPC revision and a future OROP revision would interact is not known."),
    ("Is there a rank-wise 8th CPC pension table for Sepoy, Havildar or JCOs?", "No official table exists as of " + LAST_UPDATED_HUMAN + ". Tables circulating on social media are not official."),
    ("What is the SPARSH helpline number?", "The SPARSH website lists the helpline 1800-180-5325 and warns that no WhatsApp numbers are authorised for SPARSH queries."),
], sources=["sparsh", "desw", "om_dr", "pm_dr", "pib_tor", "cpc8_comp", "uidai_lc", "doe"], related_add=("/life-certificate/",))

# ------------------------------------------------------------------ chart
extend("/pension-chart/", body=f"""
<h2>How to use the chart in three steps</h2>
<ol>
<li>Find your 7th CPC basic pension (PPO or pension slip) in the first column, or the row just below it.</li>
<li>Read across to the factor you want to test. 2.57 shows a repeat of the 7th CPC; 3.833 shows the staff-side demand.</li>
<li>Add the additional pension for your age if you are 80 or older, then compare with your total today (basic × 1.6).</li>
</ol>

<h2>Common mistakes when reading pension charts</h2>
<ul>
<li><strong>Reading the bank credit row.</strong> Look up basic pension, not the credited amount.</li>
<li><strong>Adding today's DR on top.</strong> DR is expected to restart from zero on the revised pension.</li>
<li><strong>Using charts that show a "confirmed" factor.</strong> None has been announced; this chart labels every column as an estimate.</li>
<li><strong>Ignoring the commutation deduction.</strong> The rupee deduction continues until restoration — see the <a href="/commutation-calculator/">commutation calculator</a>.</li>
</ul>
<p>See also: <a href="/minimum-pension-8th-pay-commission/">minimum pension under the 8th CPC</a>.</p>
""", faqs=[
    ("What will ₹20,000 basic pension be after the 8th Pay Commission?", "Estimated new basic pension: ₹38,400 at 1.92, ₹51,400 at 2.57, ₹57,200 at 2.86 and ₹76,660 at 3.833. Today's total with 60% DR is ₹32,000."),
    ("What will ₹50,000 basic pension be after the 8th Pay Commission?", "₹96,000 at 1.92, ₹1,28,500 at 2.57, ₹1,43,000 at 2.86 and ₹1,91,650 at 3.833 (estimates; the current maximum pension is ₹1,25,000)."),
    ("Is there an official 8th CPC pension chart?", "No. An official table can exist only after the Government accepts the Commission's recommendations. Until then every chart, including this one, is an estimate."),
    ("Does the chart apply to defence pensioners?", "It shows the arithmetic for any basic pension, but armed forces pensions are revised by separate Ministry of Defence orders and OROP tables."),
    ("Why are the values rounded up?", "Official revision orders round revised pension and DR to the next higher rupee, so the chart does the same."),
    ("Can I download or print the chart?", "Yes — use your browser's print option to save it as a PDF. The values are also generated from the same settings published at /assets/rates.json."),
], sources=["om_0816", "om_0517", "pib_tor", "cpc8_comp", "om_dr", "portal_rb"], related_add=("/minimum-pension-8th-pay-commission/", "/commutation-calculator/"))

# ------------------------------------------------------------------ basic pension finder
_p = page_by_path("/basic-pension-finder/")
_p["body"] = _strip_hi_section(_p["body"], "/basic-pension-finder/", "बैंक में आई रकम से मूल पेंशन निकालने की पूरी गाइड।")
extend("/basic-pension-finder/", body="""
<h2>Who this tool is for and how to use it</h2>
<p>It is for any central civil or family pensioner who knows the monthly bank credit but not the basic pension, and for children doing the sums for a parent. Pick the mode that matches the paper you have:</p>
<ol>
<li><strong>Bank credit:</strong> take a normal month's credit from the passbook (not a month with arrears), enter age, DR (60% now), the commutation deduction if any, and tick FMA if you live outside a CGHS area.</li>
<li><strong>PPO (post-2016):</strong> type the basic pension printed on it.</li>
<li><strong>PPO (pension on 31.12.2015):</strong> the tool multiplies by 2.57 (minimum ₹9,000).</li>
<li><strong>Last pay only:</strong> the tool takes 50% (pension) or 30%/50% (family pension).</li>
</ol>
<p>Then press "Use in the 8th CPC calculator". The <a href="/commutation-calculator/">commutation calculator</a> will tell you when the deduction stops.</p>
""", faqs=[
    ("Which month's credit should I use?", "A normal month without arrears. DR increases are usually paid with arrears for several months in the first payment, which makes that credit unusually high."),
    ("What if the tool shows two possible basic pensions?", "Because DR is rounded up to the next rupee, two neighbouring basic pensions can give the same credit. Check your PPO or pension slip to pick the right one; the difference is usually one rupee."),
    ("Does income tax deducted by the bank matter?", "Yes. Enter any TDS or recovery under 'other deductions' so the tool adds it back."),
    ("Is Fixed Medical Allowance part of basic pension?", "No. FMA of ₹1,000 a month is paid only to pensioners in non-CGHS areas who do not use CGHS for OPD, and it does not attract DR."),
], sources=["portal_rb", "portal_faq", "om_dr", "om_0816", "om_0517", "pm_dr"], related_add=("/commutation-calculator/",))

# ------------------------------------------------------------------ pre-2016
_p = page_by_path("/pre-2016-pensioners/")
_p["body"] = _strip_hi_section(_p["body"], "/pre-2016-pensioners/", "2016 से पहले रिटायर पेंशनभोगियों के दोनों तरीकों की पूरी जानकारी।")
extend("/pre-2016-pensioners/", body="""
<h2>Who this page is for</h2>
<p>Central civil pensioners and family pensioners whose pension started before 1 January 2016, including CAPF, railway and All India Services pensioners. It is also useful if you suspect your pension was never revised under the 12 May 2017 notional-pay order.</p>

<h2>How to use the calculator</h2>
<ol>
<li>Enter your pension as on 31.12.2015 (before the 2.57 revision), from your old PPO or the bank's revision entry.</li>
<li>If your revised authority shows notional pay as on 01.01.2016, enter it to compare Method B.</li>
<li>Enter age and pension type, choose an 8th CPC factor and calculate.</li>
<li>If Method B is higher but you are still being paid Method A, write to your Head of Department / Pay and Accounts Office with a copy of the OM dated 12.05.2017, or file a grievance on CPENGRAMS (pgportal.gov.in).</li>
</ol>

<h2>Common mistakes</h2>
<ul>
<li><strong>Multiplying today's basic by 2.57 again.</strong> The 2.57 revision already happened in 2016; today's basic is the result.</li>
<li><strong>Including additional pension before multiplying.</strong> Only basic pension was multiplied.</li>
<li><strong>Expecting arrears before 2016.</strong> The 2017 OM allowed none before 01.01.2016.</li>
</ul>
""", faqs=[
    ("My pension was never revised by notional pay fixation. What can I do?", "Ask your Head of Department / Pay and Accounts Office for the revised authority under the OM dated 12.05.2017. If there is no reply, file a pension grievance on CPENGRAMS through pgportal.gov.in."),
    ("Do the 2016 and 2017 orders apply to armed forces pensioners?", "No. Both OMs say separate orders will be issued by the Ministry of Defence for armed forces pensioners and family pensioners."),
    ("Did banks revise pre-2016 pensions automatically?", "Banks applied the 2.57 multiplier automatically under the 04.08.2016 OM. The notional-pay revision needed a revised authority from the Head of Department / PAO under the existing PPO number."),
    ("Is the minimum ₹9,000 applied before or after additional pension?", "The minimum ₹9,000 excludes additional pension. Additional pension for age is then added on the revised basic."),
], sources=["om_0816", "om_0517", "portal_faq", "pgportal", "pib_tor", "cpc8_comp", "om_dr"])

# ------------------------------------------------------------------ DA/DR
_p = page_by_path("/da-dr-calculator/")
_p["body"] = _strip_hi_section(_p["body"], "/da-dr-calculator/", "महंगाई राहत (DR) और एरियर की पूरी गणना हिंदी में।")
extend("/da-dr-calculator/", body="""
<h2>Who should use this calculator and how</h2>
<p>Any central government pensioner or family pensioner — civil, railway, defence or All India Services — who wants to check the DR in their credit or estimate the effect of a new instalment.</p>
<ol>
<li>Enter your basic pension (before commutation) and age.</li>
<li>Keep 60% as the old rate. The new rate is pre-filled at 63% only as an estimate; change it when the official rate is announced.</li>
<li>Choose the month the new rate takes effect (1 July for the July instalment) and the month you expect it to be credited.</li>
<li>Read the monthly increase and arrears. If you entered a commutation deduction, the net credit is shown too.</li>
</ol>

<h2>Common mistakes</h2>
<ul>
<li><strong>Calculating DR on the reduced pension.</strong> DR is paid on the full basic pension before commutation.</li>
<li><strong>Adding DR on FMA.</strong> Fixed Medical Allowance does not attract DR.</li>
<li><strong>Believing a "DA hike" headline before the order.</strong> The Cabinet decision appears on pib.gov.in; DoPPW then issues the DR order for pensioners.</li>
</ul>
""", faqs=[
    ("How is DA/DR calculated from CPI-IW?", "The 7th CPC formula uses the 12-month average of the All-India Consumer Price Index for Industrial Workers published by the Labour Bureau. The Government announces the rate; calculations by others are only estimates."),
    ("When is the July DA/DR usually announced?", "There is no fixed date. The rate takes effect from 1 July, and the decision has often come in September–October, with arrears paid afterwards."),
    ("Do railway and defence pensioners get the same DR?", "Yes. The DoPPW order applies the same rate to armed forces, railway and All India Services pensioners and family pensioners."),
    ("Is DR taxable?", "DR forms part of pension income and is taxed with it under the normal rules; the bank deducts TDS where applicable."),
], sources=["om_dr", "pm_dr", "pib_all", "labour", "portal_faq", "doppw", "pib_tor"])

# ------------------------------------------------------------------ latest update / how we calculate / info pages
extend("/latest-update/", faqs=[
    ("What is the official website of the 8th Pay Commission?", "8cpc.gov.in. Notices about visits, consultations and memorandums are posted there."),
    ("When is the next DA/DR instalment due?", "The July 2026 instalment (effective 1 July 2026) had not been announced as of 28 October 2026. The next one would normally take effect from 1 January 2027."),
    ("Is the 8th Pay Commission going to exclude pensioners?", "Pension matters are within the Terms of Reference. A viral claim that retired employees would lose pay commission revisions was declared fake by PIB Fact Check on 13 November 2025."),
    ("What happens after the report is submitted?", "The Government examines it, the Cabinet takes a decision, and the departments concerned (DoE, DoPPW and, for the forces, DESW) issue orders. Only then are revised pensions paid."),
], sources=["pib_tor", "cpc8", "cpc8_comp", "pm_dr", "om_dr", "pib_all", "labour", "doe"])

_SOURCES_NEW = [(SRC[k][0], SRC[k][1]) for k in ("pib_tor", "cpc8_comp", "pm_dr", "om_dr", "pib_all", "om_0816", "om_0517", "portal_rb", "portal_faq", "comm_table", "uidai_lc", "pib_min")]
_p = page_by_path("/how-we-calculate/")
_p["body"] = _p["body"].replace(src_html, "".join(f'<li><a href="{u}" rel="noopener">{html.escape(t)}</a></li>' for u, t in _SOURCES_NEW))
_p["body"] = _p["body"].replace("<h2>Found an error?</h2>", """<h2>Commutation and restoration</h2>
<p class="note">Monthly deduction = basic pension × % commuted (or the rupee amount on the PPO) · Lump sum ≈ deduction × commutation factor × 12 · Restoration = 15 years after the deduction started</p>
<p>The commutation factor is taken from the commutation table for the age next birthday (8.194 at 61, the usual case for retirement at 60). DR is paid on the full pension. For the 8th CPC estimate we assume, as in the 7th CPC revision (OM 04.08.2016 para 4.3), that the deduction stays at the same rupee amount until restoration.</p>
<h2>Found an error?</h2>""")
extend("/how-we-calculate/", faqs=[
    ("How is the commuted value of pension calculated?", "Commuted value = commuted monthly pension × commutation factor for age next birthday × 12. For a ₹12,000 monthly commutation at 8.194, that is ₹11,79,936."),
    ("Do you use any data that is not official?", "Union demands (such as 3.833) and media estimates appear only as labelled scenarios. Every current rule comes from an official order linked on this page."),
], sources=["pib_tor", "om_dr", "om_0816", "om_0517", "portal_rb", "portal_faq", "comm_table", "pm_dr"], related_add=("/editorial-policy/",))

_p = page_by_path("/about/")
_p["body"] = f"""
<h2>Who runs this site</h2>
<p>This website is run by the <strong>8CPC Pension Calculator team</strong>, a small independent team in India that builds free, privacy-friendly tools. We are not connected with any government body, union, bank or political party, and we do not sell financial products. We publish no personal names or phone numbers for the team on purpose: questions and corrections are handled through the <a href="/contact/">contact page</a>, and the work speaks through its sources and its corrections record.</p>

<h2>Why this site exists</h2>
<p>Every pay commission brings a flood of headlines, WhatsApp forwards and YouTube thumbnails promising a "confirmed" new pension. Most of them mix up demands, estimates and actual orders, and very few explain the arithmetic. Pensioners — many of them in their seventies, eighties and nineties — deserve a clear, honest way to see what different outcomes would mean for their own monthly pension, without signing up, downloading an app or sharing personal details.</p>
<p>So we built fast calculators that run entirely in your browser, written in plain English and simple Hindi, with every assumption shown on screen. Every page exists in both languages.</p>

<h2>What we do</h2>
<ul>
<li><strong>Calculate transparently.</strong> Each result shows the step-by-step formula, so you can check it with a pen and paper.</li>
<li><strong>Label everything.</strong> Every 8th CPC result is marked "Estimate — not official". Figures on the <a href="/latest-update/">latest update</a> page are labelled Official, Demand or Estimate.</li>
<li><strong>Use primary sources.</strong> Current rules come from the CCS (Pension) Rules, DoPPW office memoranda and Cabinet releases on pib.gov.in, linked in a Sources box on every tool page with the date we last checked them.</li>
<li><strong>Correct quickly and openly.</strong> Our <a href="/editorial-policy/">editorial policy</a> explains how we verify and correct; every change is dated on the <a href="/changelog/">changelog</a>.</li>
<li><strong>Update on announcement day.</strong> All official numbers sit in one settings block, so a new DR or an official fitment factor can be reflected across the site within minutes.</li>
</ul>

<h2>What we don't do</h2>
<ul>
<li>We are <strong>not</strong> a government website and are not connected with the Government of India, DoPPW, CPAO, the Department of Ex-Servicemen Welfare, any bank or the 8th Central Pay Commission. We do not use the State Emblem or any ministry logo.</li>
<li>We never ask for your name, PPO number, bank account, Aadhaar, PAN or OTP. Anyone who asks for these in our name is a fraud.</li>
<li>We do not store the numbers you type. The calculation happens on your own device.</li>
<li>We do not predict the final fitment factor. We let you test scenarios.</li>
<li>We do not accept payment to change any figure, ranking or wording.</li>
</ul>

<h2>How the calculation works</h2>
<p>The method follows the way the 7th Pay Commission revised pensions in 2016: your basic pension is multiplied by a fitment factor and rounded up to the next rupee; additional pension for age is applied at the same percentage; and Dearness Relief is assumed to restart at zero on the new pension. Arrears are estimated as the monthly increase multiplied by the number of months between the assumed date of effect and the month the revised pension is first paid. Full details are on <a href="/how-we-calculate/">How we calculate</a>.</p>

<h2>Accessibility and languages</h2>
<p>The site is designed to work on low-cost phones and slow connections: no external fonts, only a lightweight analytics tag and no heavy images. Text can be enlarged with your browser's zoom, form fields have clear labels, and every page has a full Hindi version — tap "हिंदी" at the top of any page.</p>
<p>Data last updated: {LAST_UPDATED_HUMAN}.</p>
"""
_p["faqs"] = [
    ("Is this a government website?", "No. It is an independent website run by the 8CPC Pension Calculator team and is not affiliated with any government body."),
    ("Who writes and checks the content?", "The 8CPC Pension Calculator team. Every rule is checked against the official order linked on the page, and the date of the last check is shown at the top of each tool page."),
    ("Is the calculator free?", "Yes. It is free to use and needs no registration."),
    ("How often is the data updated?", "Whenever a relevant official order or announcement appears, such as a DR instalment or an 8th CPC decision. The last update date is shown on every page."),
    ("Why don't you publish a name or phone number?", "To keep the focus on verifiable sources and to avoid fraudsters impersonating a person. All queries go through the contact page by email."),
]
_p["sources"] = ["doppw", "pib_tor", "om_dr", "portal_rb"]
_p["title"] = "About Us – 8CPC Pension Calculator Team"
_p["desc"] = "Who runs this independent 8th Pay Commission pension calculator (the 8CPC Pension Calculator team), why it exists, how numbers are checked and how the site stays independent."
_p["related"] = rel("/", "/editorial-policy/", "/how-we-calculate/", "/changelog/", "/latest-update/")

_p = page_by_path("/contact/")
_p["body"] = _p["body"].replace("because the site is run by one person, replies can take a few working days", "because the site is run by a small team, replies can take a few working days")
_p["body"] = _p["body"].replace("<h2>Our commitment</h2>", '<h2>Our commitment</h2>\n<p>Corrections follow our <a href="/editorial-policy/">editorial policy</a>.</p>')
page_by_path("/disclaimer/")["related"] = rel("/", "/latest-update/", "/editorial-policy/")
page_by_path("/changelog/")["related"] = rel("/", "/how-we-calculate/", "/editorial-policy/", "/latest-update/", "/da-dr-calculator/")

# ------------------------------------------------------------------ NEW: commutation calculator
CM_EX = [(20000, 40), (30000, 40), (45000, 40), (30000, 20)]
_cm_rows = []
for b, pc in CM_EX:
    c = round(b * pc / 100); v = round(c * 8.194 * 12)
    _cm_rows.append([inr(b), f"{pc}%", inr(c), inr(v), inr(b + up(Decimal(b) * 60 / 100) - c), inr(b + up(Decimal(b) * 60 / 100))])
_cm_cols_en = ["Basic pension", "Commuted", "Monthly deduction", "Lump sum at 8.194", "Credit now (60% DR)", "Credit after restoration"]

PAGES.append(dict(
    path="/commutation-calculator/", crumb="Commutation Calculator", webapp=True, widget=commutation_widget("en"),
    title="Pension Commutation & Restoration Calculator – 15 Years, 8th CPC",
    desc="Work out your monthly commutation deduction, approximate lump sum (commutation factor 8.194 at 61), the month your full pension is restored after 15 years, and the 8th CPC effect. DR stays on full pension.",
    h1="Pension Commutation & Restoration Calculator",
    lead="If you commuted part of your pension, a fixed amount is deducted every month until it is restored after 15 years. See the deduction, the lump sum, your restoration month and how the 8th Pay Commission could change your credit.",
    body=f"""
<h2>What commutation of pension means</h2>
<p>At retirement a central government servant may "commute" — sell back — up to <strong>40% of the pension</strong> for a one-time lump sum. The Pensioners' Portal of the Department of Pension &amp; Pensioners' Welfare explains the three rules that matter: the lump sum is calculated from the Commutation Table, the monthly pension stands reduced by the portion commuted, and "the commuted portion will be restored on the expiry of 15 years". Dearness Relief, however, "will continue to be calculated on the basis of the original pension (i.e. without reduction of commuted portion)".</p>
<p class="note">Commuted value of pension (CVP) = commuted monthly pension × commutation factor × 12. The factor depends on the age next birthday on the date commutation becomes absolute — 8.194 at age next birthday 61, which is the usual case for retirement at 60.</p>

<h2>Who this calculator is for</h2>
<ul>
<li>Central civil pensioners who commuted part of their pension and want to know when the deduction stops.</li>
<li>Pensioners checking whether the bank is deducting the right amount and paying DR on the full pension.</li>
<li>Anyone estimating what the 8th Pay Commission would mean while a commutation deduction is still running.</li>
<li>Employees close to retirement deciding how much to commute (the decision needs the exact factor and your own circumstances; this tool shows the arithmetic).</li>
</ul>

<h2>How to use it</h2>
<ol>
<li>Enter your <strong>full basic pension</strong> — the figure before the deduction.</li>
<li>Enter the commuted part as a percentage, or better, as the exact rupee amount printed on your PPO.</li>
<li>Choose the month the deduction started. The 15 years run from the date the reduction became operative (from retirement itself if the lump sum was paid in the first month).</li>
<li>Keep 8.194 as the factor unless your sanction letter shows another one. Enter your age and a fitment factor, then calculate.</li>
</ol>

<h2>Worked examples</h2>
{ex_table("en", _cm_rows, _cm_cols_en)}
<p>For ₹30,000 basic with 40% commuted, the deduction is ₹12,000 a month and the lump sum about ₹11,79,936. Over 15 years ₹21,60,000 is deducted in total. In exchange the pensioner received the lump sum up front, and the 15-year restoration rule means the deduction ends even though it has already recovered the lump sum in about 8.2 years at this factor (8.194 × 12 = about 98 months), ignoring interest.</p>

<h2>Commutation and the 8th Pay Commission</h2>
<p>When the 7th CPC revised pre-2016 pensions, the revised (consolidated) pension included the commuted portion and "the commuted portion will be deducted from the said amount while making monthly disbursements" (DoPPW OM dated 04.08.2016, para 4.3). In practice the full basic pension was multiplied by 2.57 and the deduction stayed at the same rupee amount. If the 8th CPC follows the same approach, a pensioner still under deduction gains more than the plain factor suggests on the net credit. Example: ₹30,000 basic, ₹12,000 deduction, factor 2.57 — new basic ₹77,100, credit ₹65,100 until restoration against ₹36,000 today. This is an estimate, not an order.</p>
<p>Under the 6th and 7th CPC, employees who retired on or after the date of effect and got arrears of pension could commute the additional pension using the revised table; the Pensioners' Portal FAQ says the age at the original commutation is used but the factor from the revised table applies. A similar provision may come with the 8th CPC; nothing has been announced.</p>

<h2>Restoration: what you need to do</h2>
<p>Nothing, usually. The Pensioners' Portal FAQ says restoration after 15 years "is to be made automatically by bank"; where the date of commutation is not in the PPO, the bank obtains it from the Pay and Accounts Office through CPAO. Check your first credit after the restoration month. If it has not gone up, write to your pension paying branch with your PPO number, and if needed file a grievance on CPENGRAMS (pgportal.gov.in).</p>

<h2>Common mistakes</h2>
<ul>
<li><strong>Counting 15 years from retirement when the lump sum came later.</strong> The period runs from the date the reduction became operative.</li>
<li><strong>Calculating DR on the reduced pension.</strong> DR is on the original pension.</li>
<li><strong>Using today's age for the factor.</strong> The factor is fixed by your age next birthday when commutation became absolute.</li>
<li><strong>Thinking you can commute more later.</strong> The FAQ says there is no second option after the first becomes absolute.</li>
</ul>
""",
    faqs=[
        ("How much pension can I commute?", "Up to 40% of the pension, under the CCS (Commutation of Pension) Rules, 1981. No medical examination is needed if you opt within one year of retirement."),
        ("When is commuted pension restored?", "On completion of 15 years from the date the reduction in pension became operative. If the lump sum was paid in the first month after retirement, the 15 years count from retirement itself."),
        ("Is DR paid on the full pension or on the reduced pension?", "On the full (original) pension, without reduction for the commuted portion."),
        ("What is the commutation factor at age 60?", "For retirement at 60, commutation becomes absolute on the next day and the age next birthday is 61, so the factor is 8.194 in the present table."),
        ("How is the lump sum calculated?", "Commuted monthly pension × commutation factor × 12. For ₹12,000 at 8.194, the lump sum is ₹11,79,936."),
        ("Do I need to apply for restoration?", "No. The bank restores the commuted portion automatically after 15 years. If it doesn't, contact your pension paying branch and then CPENGRAMS."),
        ("Will the commutation deduction increase after the 8th Pay Commission?", "In the 7th CPC revision the commuted portion continued to be deducted from the revised pension in rupees. The calculator assumes the same for the 8th CPC; the actual orders will decide."),
        ("Is the commuted value of pension taxable?", "The Pensioners' Portal FAQ says death/retirement gratuity and commuted value of pension are fully exempt from income tax for central government servants."),
        ("Can a family pensioner commute family pension?", "No. Commutation applies to the retiring government servant's pension, not to family pension."),
        ("Can I commute a further part of my pension later?", "No. There is no second option once the first commutation has become absolute."),
    ],
    sources=["portal_rb", "portal_faq", "comm_table", "om_0816", "om_0517", "om_dr", "pgportal", "pib_tor"],
    related=rel("/", "/basic-pension-finder/", "/da-dr-calculator/", "/pre-2016-pensioners/", "/how-we-calculate/"),
))

# ------------------------------------------------------------------ NEW: minimum pension
_mn = [[f"×{f}", n, inr(ceil_mul(9000, f)), inr(ceil_mul(9000, f) - 14400)] for f, n in
       [("1.92", "Media estimate"), ("2.28", "Media estimate"), ("2.57", "7th CPC factor"), ("2.86", "Media estimate"), ("3.0", "Round-number estimate"), ("3.833", "NC-JCM staff-side demand")]]
PAGES.append(dict(
    path="/minimum-pension-8th-pay-commission/", crumb="Minimum Pension", webapp=True, calc=True,
    title="8th Pay Commission Minimum Pension – ₹9,000 at Each Fitment Factor",
    desc="Minimum pension and minimum family pension under the 8th Pay Commission: ₹9,000 today (raised from ₹3,500 in 2016), what it would become at 1.92–3.833, the real gain after DR resets, and who is on the minimum.",
    h1="Minimum Pension under the 8th Pay Commission",
    lead="Central government pensioners and family pensioners on the minimum get ₹9,000 basic plus DR today. See how the minimum has moved in past pay commissions and what each 8th CPC fitment factor would make it.",
    body=f"""
<h2>The minimum pension today</h2>
<p>Since 1 January 2016 the minimum pension and minimum family pension for central government civil pensioners is <strong>₹9,000 a month</strong>, excluding the additional pension paid to pensioners aged 80 and above (DoPPW OM dated 04.08.2016, para 4.4). The 7th CPC orders raised it from ₹3,500 — PIB listed the increase "from Rs.3500/- per month to Rs.9000/- per month" among DoPPW's reforms. With Dearness Relief at 60% from 1 January 2026, a pensioner on the minimum receives ₹14,400 a month (₹9,000 + ₹5,400 DR), plus additional pension if 80 or older and Fixed Medical Allowance of ₹1,000 if living outside a CGHS area.</p>
<p>The maximum, for comparison, is 50% of the highest pay in the Government — ₹1,25,000 — and ₹75,000 for normal family pension.</p>

<h2>What the minimum could become (estimates)</h2>
<p>In 2016 the minimum went up by exactly the fitment factor: ₹3,500 × 2.57 = ₹8,995, rounded to ₹9,000. If the 8th CPC again applies one factor across the board, the new minimum would be ₹9,000 × factor. None of these factors is official.</p>
{ex_table("en", _mn, ["Factor", "Where it comes from", "New minimum basic", "Real gain vs ₹14,400 today"])}
<p>The 7th CPC also set the minimum by first fixing minimum pay (₹18,000) and taking 50% of it. Staff-side bodies have proposed a minimum pay of ₹69,000 for the 8th CPC; 50% of that would be ₹34,500, close to ₹9,000 × 3.833 = ₹34,497. That is a demand, not a decision.</p>

<h2>Who is on the minimum pension?</h2>
<ul>
<li>Many family pensioners — 30% of a low last pay is often below ₹9,000, so the minimum applies.</li>
<li>Pensioners who retired from lower pay levels long ago, whose 2.57 revision fell below ₹9,000 and was stepped up.</li>
<li>Some armed forces pensioners and family pensioners of lower ranks (the ₹9,000 minimum applied to them under the 7th CPC too).</li>
</ul>

<h2>How to use the calculator above</h2>
<ol>
<li>Enter ₹9,000 (or your basic pension) and your age.</li>
<li>Choose a pension type — family pension uses the same ₹9,000 minimum.</li>
<li>Pick a factor and calculate. The result shows whether the estimated new minimum (₹9,000 × factor) lifted your pension.</li>
</ol>

<h2>Common mistakes</h2>
<ul>
<li><strong>Comparing the new minimum with ₹9,000.</strong> Compare it with ₹14,400 — what you receive today with DR.</li>
<li><strong>Including additional pension in the minimum.</strong> The minimum excludes it; additional pension is paid on top.</li>
<li><strong>Assuming the minimum is announced.</strong> The 8th CPC has not recommended a minimum as of {LAST_UPDATED_HUMAN}.</li>
</ul>
""",
    faqs=[
        ("What is the minimum pension for central government pensioners now?", "₹9,000 a month from 1 January 2016, excluding additional pension for age, plus DR (60% from 1 January 2026) — a total of ₹14,400 for a pensioner below 80."),
        ("What will the minimum pension be under the 8th Pay Commission?", "Not announced. If a single factor is applied as in 2016, it would be ₹9,000 × factor: ₹17,280 at 1.92, ₹23,130 at 2.57, ₹25,740 at 2.86 or ₹34,497 at 3.833."),
        ("Is the minimum family pension also ₹9,000?", "Yes. Minimum family pension is ₹9,000 a month, plus DR."),
        ("What was the minimum pension under the 6th CPC?", "₹3,500 a month. The 7th CPC orders raised it to ₹9,000 from 1 January 2016."),
        ("Does additional pension at 80+ count towards the minimum?", "No. The ₹9,000 minimum excludes additional pension, which is paid on top of the basic."),
        ("Do armed forces pensioners get the same minimum?", "Under the 7th CPC the ₹9,000 minimum pension applied to armed forces pensioners as well, through Ministry of Defence orders."),
        ("Is the ₹69,000 minimum pay demand official?", "No. It is the reported demand of the NC-JCM staff side, which gives the 3.833 factor. It has no official status."),
        ("Do minimum pensioners get Fixed Medical Allowance?", "If they live in a non-CGHS area and do not use CGHS for OPD, yes — ₹1,000 a month, without DR."),
    ],
    sources=["om_0816", "om_0517", "pib_min", "portal_rb", "om_dr", "pm_dr", "pib_tor", "cpc8_comp"],
    related=rel("/", "/pension-chart/", "/family-pension-calculator/", "/fitment-factor-calculator/", "/commutation-calculator/"),
))

# ------------------------------------------------------------------ NEW: life certificate
PAGES.append(dict(
    path="/life-certificate/", crumb="Life Certificate Guide",
    title="Life Certificate November 2026 – Jeevan Pramaan Guide for Pensioners",
    desc="When and how central government pensioners submit the annual life certificate: November (80+ from 1 October), Jeevan Pramaan face authentication, doorstep options, what happens if you miss it. Verified 28 Oct 2026.",
    h1="Life Certificate 2026: Jeevan Pramaan Guide for Pensioners",
    lead="Every central government pensioner and family pensioner must submit a life certificate each year to keep pension flowing. Here is when, how — including from home with a smartphone — and what to do if something goes wrong.",
    body="""
<h2>When to submit</h2>
<ul>
<li><strong>Pensioners aged 80 and above:</strong> from <strong>1 October</strong>.</li>
<li><strong>All other pensioners:</strong> in <strong>November</strong> (1–30 November).</li>
<li>A certificate submitted in this window is valid until 30 November of the following year.</li>
</ul>
<p>UIDAI's life certificate FAQ states that "every Central Government pensioner has to submit an Annual Life Certificate in the month of November", and that pensioners aged 80 and above may submit from 1 October. The Government told Parliament on 1 April 2026 that nationwide Digital Life Certificate campaigns have been held from 1 to 30 November every year since 2022, and that "pensioners above 80 years can submit their DLCs in the month of October also".</p>

<h2>What happens if you miss it</h2>
<p>According to the same FAQ, pension for December onwards is not paid until the certificate is received. Once it is updated, pension is paid with arrears in the next payment. If no certificate is submitted for three years or more, pension restarts only after sanction by the competent authority through CPAO.</p>

<h2>Five ways to submit</h2>
<ol>
<li><strong>From home with a smartphone (face authentication):</strong> install UIDAI's Aadhaar Face RD app and the Jeevan Pramaan app on an Android phone (version 9 or above, 13 MP camera, about 500 MB free). Authenticate the operator once with OTP, then scan the pensioner's face. You receive a Pramaan ID by SMS.</li>
<li><strong>Doorstep by postman (India Post Payments Bank):</strong> through the Postinfo app, for a nominal fee of ₹70.</li>
<li><strong>Doorstep banking by public sector banks:</strong> nominal fee of ₹75, through the Doorstep Banking app, website or toll-free number.</li>
<li><strong>At a Jeevan Pramaan centre / CSC:</strong> find one through "Locate a Centre" on jeevanpramaan.gov.in or by SMS "JPL &lt;pincode&gt;" to 7738299899.</li>
<li><strong>In person on paper:</strong> at your pension paying bank branch, post office or a designated government office, in the form in Annexure XIII of the CPAO scheme booklet.</li>
</ol>

<h2>What you need for a digital life certificate</h2>
<ul>
<li>Aadhaar number, linked to the pension account at your bank or post office.</li>
<li>PPO number, pension account number, sanctioning authority and disbursing agency (auto-filled if you generated a DLC last year).</li>
<li>A mobile number for the SMS acknowledgement.</li>
</ul>
<p>Face authentication is not available for re-employed pensioners and in cases of remarriage; they must submit the certificate in the conventional way.</p>

<h2>Common reasons a face scan fails</h2>
<ul>
<li>Poor light, a busy background, or more than one person in the frame.</li>
<li>Moving or not blinking during the scan, or holding the phone too close or too far.</li>
<li>Aadhaar or biometrics locked, or a slow internet connection.</li>
<li>Not wearing glasses if the Aadhaar photo shows glasses.</li>
</ul>
<p>For help, the FAQ lists UIDAI's helpline 1947 and the Jeevan Pramaan FAQ page; the Jeevan Pramaan portal lists 1800 111 555.</p>

<h2>If the pensioner is ill or bedridden</h2>
<p>A medical certificate from a registered medical practitioner can be sent to the bank's pension branch, which may nominate an officer to visit the home or hospital. A paper certificate signed by specified officers (for example a gazetted officer, a magistrate, a postmaster or a bank officer) is also accepted.</p>

<h2>Defence and family pensioners</h2>
<p>Defence pensioners can submit through SPARSH, including Jeevan Pramaan face authentication, or at a SPARSH Service Centre. Family pensioners follow the same November rule.</p>

<h2>Beware of fraud</h2>
<p>Banks and the Government do not ask for OTPs by phone to "update" your life certificate. Generate the certificate yourself through the official apps or a known centre, and report fraud to 1930 or cybercrime.gov.in.</p>
<p>While your pension is safe for another year, see what the 8th CPC could mean for it with the <a href="/">pension calculator</a>, or check the DR in your credit with the <a href="/da-dr-calculator/">DA/DR calculator</a>.</p>
""",
    faqs=[
        ("When should central government pensioners submit the life certificate in 2026?", "In November 2026. Pensioners aged 80 and above can submit from 1 October 2026."),
        ("Can I submit the life certificate from home?", "Yes. With an Android smartphone you can generate a Digital Life Certificate using the Jeevan Pramaan app with Aadhaar face authentication. IPPB postmen and bank doorstep services also come home for a small fee."),
        ("What if I miss the November deadline?", "Pension for December onwards is held until the certificate is received; it is then paid with arrears. After three years without a certificate, pension restarts only after sanction through CPAO."),
        ("How do I know my digital life certificate was accepted?", "You get an SMS with a Pramaan ID. You can download the certificate from jeevanpramaan.gov.in with that ID; the bank can access it after a few days."),
        ("Is the digital life certificate compulsory?", "No. Jeevan Pramaan is in addition to the existing paper method at the bank, post office or government office."),
        ("Does the mobile number need to be linked to the bank account?", "No. Any working mobile number can receive the SMS; Aadhaar must be linked to the pension account."),
        ("Can defence pensioners use Jeevan Pramaan?", "Yes. UIDAI's FAQ confirms defence pensioners can submit a DLC, and SPARSH accepts identification through the Jeevan Pramaan face app."),
        ("What does the IPPB doorstep service cost?", "A nominal ₹70, booked through the Postinfo app, according to the UIDAI FAQ. Public sector banks' doorstep banking charges ₹75."),
        ("Who can sign a paper life certificate?", "Among others: a gazetted government officer, a magistrate, a registrar or sub-registrar, a police officer of SI rank in charge of a station, a postmaster, an RBI Class-I officer, a tehsildar or BDO, a gram panchayat head, or an MP/MLA."),
        ("Is the life certificate needed for family pension too?", "Yes. Family pensioners also submit an annual life certificate in November."),
    ],
    sources=["uidai_lc", "pib_dlc", "jeevan", "doppw_lc", "sparsh", "cyber"],
    related=rel("/", "/da-dr-calculator/", "/family-pension-calculator/", "/defence-pension-calculator/", "/latest-update/"),
))

# ------------------------------------------------------------------ NEW: editorial policy
PAGES.append(dict(
    path="/editorial-policy/", crumb="Editorial Policy",
    title="Editorial Policy – Sources, Verification & Corrections",
    desc="How the 8CPC Pension Calculator team chooses sources, verifies every rate, labels estimates, updates the site on announcement days and corrects mistakes. Independent, not a government website.",
    h1="Editorial Policy",
    lead="Pension information affects real household budgets. This page explains exactly how we decide what to publish, how we check it and how we fix mistakes.",
    body=f"""
<h2>1. Who we are</h2>
<p>This site is published by the 8CPC Pension Calculator team, an independent team in India. We are not a government website and have no link with the Government of India, the 8th Central Pay Commission, DoPPW, CPAO, DESW, any union, bank or political party. We do not use the State Emblem or any ministry logo.</p>

<h2>2. Sources we use</h2>
<ul>
<li><strong>Primary (official):</strong> Cabinet decisions on pib.gov.in; office memoranda of the Department of Pension &amp; Pensioners' Welfare and the Department of Expenditure; the CCS (Pension) Rules and the CCS (Commutation of Pension) Rules; the Pensioners' Portal; the 8th CPC's own website (8cpc.gov.in); SPARSH and DESW for defence pensioners; Labour Bureau for CPI-IW; replies in Parliament.</li>
<li><strong>Secondary (reported):</strong> major newspapers and agencies, used <em>only</em> for demands by unions and associations and for news of events — always labelled "Demand" or "as reported".</li>
<li><strong>Not used:</strong> WhatsApp forwards, YouTube thumbnails, screenshots without a source, and other calculator sites.</li>
</ul>

<h2>3. How rates are verified</h2>
<ol>
<li>Every figure used in a calculation (DR rate, minimum and maximum pension, family pension rates, additional pension slabs, FMA, commutation rules) is checked against the official document itself, not a summary.</li>
<li>The document is linked in the Sources box of each tool page, and the date we last opened it is shown as "Last verified".</li>
<li>Calculations are tested against official worked examples where they exist — for instance all four pension examples in Annexure I of the DoPPW OM dated 12.05.2017 — and against automated tests before every release.</li>
<li>Anything not yet decided — the 8th CPC fitment factor, new minimum, date of effect, a DR instalment not yet ordered — is labelled "Estimate — not official" wherever it appears.</li>
</ol>

<h2>4. Update process</h2>
<ul>
<li>We check pib.gov.in, doppw.gov.in, doe.gov.in and 8cpc.gov.in for new decisions, with extra attention on Cabinet days.</li>
<li>When an official decision appears (for example a DR instalment), we update the single settings block that drives every calculator, re-run the tests, and publish the change the same day where possible.</li>
<li>A Cabinet decision and the later DoPPW order are logged separately; we wait for the order before treating rules of detail as final.</li>
<li>Every change is recorded with its date and source on the <a href="/changelog/">changelog</a>.</li>
</ul>

<h2>5. Corrections policy</h2>
<ul>
<li>Anyone can report an error through the <a href="/contact/">contact page</a>; a link to the official order helps.</li>
<li>We check each report against the primary source. Verified errors in a rule or calculation are fixed promptly and logged on the changelog with what changed.</li>
<li>We do not silently change figures. If a past estimate is overtaken by an official decision, the page says so.</li>
<li>If we disagree with a report, we reply with the source we relied on.</li>
</ul>

<h2>6. Independence and money</h2>
<ul>
<li>The site is free. It may show advertising in future to cover costs; ads will never be placed inside calculators, and no advertiser can influence content.</li>
<li>We do not accept payment for links, rankings or wording, and we do not sell financial products.</li>
<li>We collect no personal data through the calculators — see the <a href="/privacy/">privacy policy</a>.</li>
</ul>

<h2>7. Language</h2>
<p>Every page is published in English and in simple Hindi with the same facts, examples and sources. If the two versions ever differ, the version that matches the official order is correct, and we fix the other.</p>

<h2>8. Limits</h2>
<p>We explain rules and show estimates; we do not give individual financial, legal or tax advice, and we cannot access anyone's pension records. Your Pension Disbursing Authority fixes your actual pension under official orders. See the <a href="/disclaimer/">disclaimer</a>.</p>
<p>Policy last reviewed: {LAST_UPDATED_HUMAN}.</p>
""",
    faqs=[
        ("Is this an official government website?", "No. It is published by the independent 8CPC Pension Calculator team."),
        ("How do you make sure the DR rate is correct?", "We read the DoPPW office memorandum itself (currently No. 42/02/2024-P&PW(D)/E-9475 dated 24.04.2026), link it on every tool page and show the date we last checked it."),
        ("How quickly are mistakes corrected?", "Verified errors in rules or calculations are fixed promptly and logged on the changelog with the date."),
        ("Do you accept paid content?", "No. No one can pay to change figures, rankings or wording."),
    ],
    sources=["pib_tor", "om_dr", "om_0517", "doppw", "doe", "cpc8"],
    related=rel("/about/", "/how-we-calculate/", "/changelog/", "/contact/"),
))

CHANGELOG.insert(0, ("2026-10-28", "28 October 2026 (evening)", [
    "Every page now has a full Hindi version at /hi/…, with its own address, Hindi navigation, breadcrumbs and hreflang links between the English and Hindi pages.",
    "Tool pages expanded with step-by-step instructions, worked-example tables, common mistakes, more FAQs and a Sources box showing \"Last verified: 28 Oct 2026\".",
    "New: <a href=\"/commutation-calculator/\">commutation &amp; restoration calculator</a>, <a href=\"/minimum-pension-8th-pay-commission/\">minimum pension under the 8th CPC</a>, <a href=\"/life-certificate/\">life certificate (Jeevan Pramaan) guide</a> and our <a href=\"/editorial-policy/\">editorial policy</a>.",
    "Sources re-checked on 28.10.2026: DoPPW DR OM of 24.04.2026, DoPPW OMs of 04.08.2016 and 12.05.2017, Pensioners' Portal retirement benefits and FAQs, UIDAI life certificate FAQs, PIB releases of 01.04.2026 and 19.03.2020. The Rajya Sabha FMA link is no longer used (the page returned an error); FMA is now sourced to the Pensioners' Portal FAQ.",
    "About page rewritten: the site is run by the 8CPC Pension Calculator team.",
]))
cl_html = "".join(
    f'<li><time datetime="{d}">{h}</time><ul>' + "".join(f"<li>{e}</li>" for e in items) + "</ul></li>" for d, h, items in CHANGELOG)
page_by_path("/changelog/")["body"] = f"""
<ol class="timeline">{cl_html}</ol>
<h2>How we log changes</h2>
<p>An entry is added whenever a rate changes (for example a new DR instalment), an official order is checked, a calculation is corrected or a page is added. Each rate change names the order it comes from, and the "data last updated" date at the top of every page changes with it. Formulas and sources are on <a href="/how-we-calculate/">How we calculate</a>; our verification and corrections rules are in the <a href="/editorial-policy/">editorial policy</a>; announcements by the Government and the Commission are tracked on the <a href="/latest-update/">latest update</a> page.</p>
"""
