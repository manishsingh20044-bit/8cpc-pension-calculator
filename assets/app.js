/* =====================================================================
   8th Pay Commission Pension Calculator — app.js (vanilla JS, no deps)
   =====================================================================
   >>> UPDATE EVERYTHING IN THIS ONE CONFIG OBJECT <<<
   When the Government announces official numbers (fitment factor, new
   minimum pension, a new DR rate, date of effect), change the values
   below, bump `lastUpdated`, and redeploy. Nothing else needs editing.
   ===================================================================== */
var CONFIG = {
  lastUpdated: "2026-10-28",            // shown on every page (YYYY-MM-DD)

  /* ---- Official fitment factor ----
     null = not announced (as of 28 Oct 2026). When announced, put the
     number here (e.g. 2.86). It becomes the default selection, is marked
     "Official" in the dropdown and comparison table, and a banner appears. */
  officialFitmentFactor: null,
  officialNoticeUrl: "",                // link to the PIB/DoPPW order when official

  /* ---- Fitment factor presets (multiplier on 7th CPC basic pension) ----
     None of these is official. `note` keys are translated in I18N below. */
  presetFactors: [
    { value: 1.92,  note: "f_est" },     // low-end media estimate
    { value: 2.28,  note: "f_est" },
    { value: 2.57,  note: "f_7cpc" },    // factor used by the 7th CPC (2016)
    { value: 2.86,  note: "f_est" },
    { value: 3.00,  note: "f_est" },
    { value: 3.25,  note: "f_est" },
    { value: 3.68,  note: "f_est" },
    { value: 3.833, note: "f_demand" }   // NC-JCM staff side / pensioner bodies' demand
  ],
  defaultFactor: 2.57,

  /* ---- Dearness Relief ----
     60% of basic pension (incl. additional pension) from 01.01.2026:
     Cabinet decision, PIB 18.04.2026; DoPPW OM No.42/02/2024-P&PW(D)/E-9475 dt 24.04.2026.
     July 2026 instalment NOT announced as of 28.10.2026. */
  currentDR: 60,
  drNote: "DR 60% from 1 Jan 2026 (PIB 18.04.2026; DoPPW OM 24.04.2026). July 2026 DR not announced as of 28 Oct 2026.",
  /* DR history (official instalments only), oldest first. The LAST entry
     must equal currentDR (checked by tools/test.js). When a new DR order is
     issued: append it here, set currentDR to it, and set drNextAssumed to null
     (the DA/DR calculator then shows the arrears of that latest official hike). */
  drHistory: [
    { from: "2025-07", pct: 58, ref: "DoPPW OM No.42/02/2024-P&PW(D) dt 08.10.2025" },
    { from: "2026-01", pct: 60, ref: "DoPPW OM No.42/02/2024-P&PW(D)/E-9475 dt 24.04.2026" }
  ],
  /* Next instalment, NOT announced. Used only as the pre-filled "new DR" in the
     DA/DR calculator, always labelled as an estimate. Set drNextAssumed: null
     once the real order is out (see above). 63 = press / CPI-IW formula estimate. */
  drNextFrom: "2026-07",
  drNextAssumed: 63,

  /* Fixed Medical Allowance for pensioners in non-CGHS areas: Rs 1,000/month
     from 01.07.2017 (DoPPW OM 4/34/2017-P&PW(D) dt 19.07.2017; Rajya Sabha
     USQ 1086, 15.12.2022). Used only by the basic-pension finder. */
  fixedMedicalAllowance: 1000,

  /* Pre-2016 pensioners, 7th CPC (DoPPW OMs 04.08.2016 and 12.05.2017):
     revised pension = higher of (pension on 31.12.2015 x 2.57) and
     (50% / 30% of notional pay on 01.01.2016). */
  pre2016Factor: 2.57,

  /* DR on the revised pension right after revision. Past pay commissions
     restarted DA/DR at 0% on the new basic. Assumption, not official. */
  newDRPercent: 0,

  /* ---- 7th CPC limits (CCS (Pension) Rules, 2021; 7th CPC orders) ---- */
  minPension: 9000,                      // minimum pension & minimum family pension
  maxPension: 125000,                    // 50% of highest pay (₹2,50,000)
  maxFamilyNormal: 75000,                // 30% of ₹2,50,000
  maxFamilyEnhanced: 125000,             // 50% of ₹2,50,000
  familyNormalRate: 30,                  // % of last pay (normal family pension)
  familyEnhancedRate: 50,                // % of last pay (enhanced family pension)

  /* ---- 8th CPC limits ----
     null = estimate as (7th CPC limit × chosen fitment factor). When the
     8th CPC announces actual figures, enter them here (₹ per month). */
  newMinPension: null,
  newMaxPension: null,
  newMaxFamilyNormal: null,
  newMaxFamilyEnhanced: null,

  /* ---- Additional pension for old pensioners / family pensioners ----
     Rule 44(6) & Rule 50(3) CCS (Pension) Rules, 2021: from the 1st of the
     month in which the age is reached. */
  additionalPension: [
    { age: 100, pct: 100 },
    { age: 95,  pct: 50 },
    { age: 90,  pct: 40 },
    { age: 85,  pct: 30 },
    { age: 80,  pct: 20 }
  ],

  /* ---- Dates for the arrears estimate ----
     PIB 28.10.2025: effect "would normally be expected from 01.01.2026"
     (past practice, NOT a decision). Payment month is a user choice. */
  effectiveFrom: "2026-01",
  defaultPaymentMonth: "2027-10",
  monthRangeStart: "2026-01",
  monthRangeEnd: "2029-12",

  /* ---- Status text (shown in the status strip) ---- */
  status: {
    constituted: "2025-11-03",           // Resolution F.No.01-01/2025-E.III(A)
    chair: "Justice Ranjana Prakash Desai",
    reportDue: "about May 2027 (18 months from constitution)"
  },

  /* ---- Sources (for the owner; also listed on /latest-update/) ---- */
  sources: [
    "https://pib.gov.in/PressReleasePage.aspx?PRID=2183289 (8th CPC ToR, 28.10.2025)",
    "https://www.pmindia.gov.in/en/news_updates/cabinet-approves-additional-instalment-of-dearness-allowance-to-central-government-employees-and-dearness-relief-dr-to-pensioners-w-e-f-01-01-2026/ (DR 60%, 18.04.2026)",
    "https://pensionersportal.gov.in/Document/CCS-Pension-Rules%202021-English.pdf (min/max pension, additional pension, family pension)",
    "https://8cpc.gov.in/composition/ (Commission composition)",
    "https://8thpaycalculator.in/official-status-board (status board, checked 23.10.2026)"
  ]
};
/* ======================= END OF CONFIG ============================== */


/* ---------------------- Pure calculation helpers -------------------- */
// Round UP to the next rupee (pension/DR fractions go to the next higher rupee),
// after trimming floating-point noise such as 23129.999999999996.
function up(x) { return Math.ceil(Math.round(x * 100) / 100); }

function formatINR(n) {
  n = Math.round(Number(n) || 0);
  var neg = n < 0; n = Math.abs(n);
  var s = String(n);
  if (s.length > 3) {
    var last3 = s.slice(-3), rest = s.slice(0, -3);
    rest = rest.replace(/\B(?=(\d{2})+(?!\d))/g, ",");
    s = rest + "," + last3;
  }
  return (neg ? "-₹" : "₹") + s;
}

function additionalPct(age) {
  age = Number(age) || 0;
  for (var i = 0; i < CONFIG.additionalPension.length; i++) {
    if (age >= CONFIG.additionalPension[i].age) return CONFIG.additionalPension[i].pct;
  }
  return 0;
}

function limitsFor(type, factor) {
  var max7 = type === "fpn" ? CONFIG.maxFamilyNormal : type === "fpe" ? CONFIG.maxFamilyEnhanced : CONFIG.maxPension;
  var newMaxCfg = type === "fpn" ? CONFIG.newMaxFamilyNormal : type === "fpe" ? CONFIG.newMaxFamilyEnhanced : CONFIG.newMaxPension;
  return {
    min7: CONFIG.minPension,
    max7: max7,
    newMin: CONFIG.newMinPension || up(CONFIG.minPension * factor),
    newMax: newMaxCfg || up(max7 * factor),
    newMinIsEstimate: !CONFIG.newMinPension,
    newMaxIsEstimate: !newMaxCfg
  };
}

function monthsBetween(fromYM, toYM) { // months from fromYM (incl.) to toYM (excl.)
  var a = fromYM.split("-"), b = toYM.split("-");
  return (Number(b[0]) - Number(a[0])) * 12 + (Number(b[1]) - Number(a[1]));
}

/* Main calculation. input = {basic, type: sup|fpn|fpe, age, factor, dr, effFrom, payMonth} */
function calcPension(input) {
  var factor = Number(input.factor);
  var type = input.type || "sup";
  var dr = (input.dr === undefined || input.dr === null || input.dr === "") ? CONFIG.currentDR : Number(input.dr);
  var entered = Math.round(Number(input.basic) || 0);
  var lim = limitsFor(type, factor);
  var warnings = [];
  var basic = entered;
  if (basic > lim.max7) { warnings.push("warn_max"); basic = lim.max7; }
  if (basic > 0 && basic < lim.min7) warnings.push("warn_min");

  var addPct = additionalPct(input.age);
  var cur = {};
  cur.basic = basic;
  cur.add = up(basic * addPct / 100);
  cur.dr = up((cur.basic + cur.add) * dr / 100);
  cur.total = cur.basic + cur.add + cur.dr;

  var raw = up(basic * factor);
  var nb = raw, floorApplied = false, capApplied = false;
  if (nb < lim.newMin) { nb = lim.newMin; floorApplied = true; }
  if (nb > lim.newMax) { nb = lim.newMax; capApplied = true; }
  var nw = {};
  nw.basic = nb;
  nw.add = up(nb * addPct / 100);
  nw.dr = up((nw.basic + nw.add) * CONFIG.newDRPercent / 100);
  nw.total = nw.basic + nw.add + nw.dr;

  var inc = nw.total - cur.total;
  var incPct = cur.total > 0 ? (inc / cur.total) * 100 : 0;
  var months = Math.max(0, monthsBetween(input.effFrom || CONFIG.effectiveFrom, input.payMonth || CONFIG.defaultPaymentMonth));
  var arrears = Math.max(0, inc) * months;

  return {
    input: { basic: entered, usedBasic: basic, type: type, age: Number(input.age) || 0, factor: factor, dr: dr,
             effFrom: input.effFrom || CONFIG.effectiveFrom, payMonth: input.payMonth || CONFIG.defaultPaymentMonth },
    addPct: addPct, current: cur, revised: nw, rawNewBasic: raw,
    floorApplied: floorApplied, capApplied: capApplied, limits: lim,
    increase: inc, increasePct: incPct, months: months, arrears: arrears, warnings: warnings
  };
}

function familyFromLastPay(lastPay) {
  lastPay = Number(lastPay) || 0;
  var normal = up(lastPay * CONFIG.familyNormalRate / 100);
  normal = Math.min(Math.max(normal, CONFIG.minPension), CONFIG.maxFamilyNormal);
  var enh = up(lastPay * CONFIG.familyEnhancedRate / 100);
  enh = Math.min(Math.max(enh, CONFIG.minPension), CONFIG.maxFamilyEnhanced);
  return { normal: normal, enhanced: enh };
}

/* ---- limits by pension type (7th CPC) ---- */
function maxFor(type) { return type === "fpn" ? CONFIG.maxFamilyNormal : type === "fpe" ? CONFIG.maxFamilyEnhanced : CONFIG.maxPension; }
function rateFor(type) { return type === "fpn" ? CONFIG.familyNormalRate : type === "fpe" ? CONFIG.familyEnhancedRate : 50; }

/* Pension pieces for a basic pension: additional pension for age and DR,
   each rounded up to the next rupee (DoPPW DR orders, para 3). DR is paid on
   the FULL basic pension, before commutation deduction. */
function pensionParts(basic, age, drPct) {
  basic = Math.round(Number(basic) || 0);
  var addPct = additionalPct(age);
  var add = up(basic * addPct / 100);
  var dr = up((basic + add) * (Number(drPct) || 0) / 100);
  return { basic: basic, addPct: addPct, add: add, dr: dr, gross: basic + add + dr };
}

/* Amount credited to the bank for one month.
   o = {basic, age, dr, commMode: none|amount|pct, commValue, fma (rupees), other} */
function commutedAmount(basic, mode, value) {
  value = Number(value) || 0;
  if (mode === "amount") return Math.round(value);
  if (mode === "pct") return Math.round(basic * value / 100); // approximation
  return 0;
}
function creditFromBasic(o) {
  var p = pensionParts(o.basic, o.age, o.dr);
  p.comm = commutedAmount(p.basic, o.commMode, o.commValue);
  p.fma = Math.round(Number(o.fma) || 0);
  p.other = Math.round(Number(o.other) || 0);
  p.credit = p.gross - p.comm + p.fma - p.other;
  return p;
}

/* Basic pension from the monthly bank credit (inverse of creditFromBasic).
   Rounding makes the inverse non-unique or empty, so every whole rupee near
   the analytic estimate is tried. Returns the exact match if one exists,
   otherwise the nearest value with the difference. */
function basicFromCredit(o) {
  var credit = Math.round(Number(o.credit) || 0);
  var a = additionalPct(o.age) / 100, d = (Number(o.dr) || 0) / 100;
  var fma = Math.round(Number(o.fma) || 0), other = Math.round(Number(o.other) || 0);
  var mult = (1 + a) * (1 + d), extra = 0;
  if (o.commMode === "amount") extra = Math.round(Number(o.commValue) || 0);
  if (o.commMode === "pct") mult -= (Number(o.commValue) || 0) / 100;
  var est = (credit - fma + other + extra) / mult;
  var lo = Math.max(1, Math.floor(est) - 60), hi = Math.ceil(est) + 60;
  var matches = [], best = null;
  for (var b = lo; b <= hi; b++) {
    var r = creditFromBasic({ basic: b, age: o.age, dr: o.dr, commMode: o.commMode, commValue: o.commValue, fma: fma, other: other });
    var diff = r.credit - credit;
    if (diff === 0) matches.push(b);
    if (!best || Math.abs(diff) < Math.abs(best.diff) || (Math.abs(diff) === Math.abs(best.diff) && diff < 0 && best.diff > 0)) best = { basic: b, diff: diff };
  }
  var basic = matches.length ? matches[0] : best.basic;
  var parts = creditFromBasic({ basic: basic, age: o.age, dr: o.dr, commMode: o.commMode, commValue: o.commValue, fma: fma, other: other });
  var warnings = [];
  if (basic < CONFIG.minPension) warnings.push("warn_low_basic");
  if (basic > CONFIG.maxPension) warnings.push("warn_high_basic");
  return { basic: basic, exact: matches.length > 0, matches: matches, diff: matches.length ? 0 : best.diff,
           credit: credit, estimate: est, parts: parts, warnings: warnings };
}

/* Basic pension from PPO figures.
   mode "ppo7": PPO already shows a 7th CPC basic pension -> as is.
   mode "ppo6": pension as on 31.12.2015 -> x 2.57, rounded up, min Rs 9,000 (OM 04.08.2016).
   mode "lastpay": 7th CPC last basic pay -> 50% (pension) / 30% / 50% (family), within limits. */
function basicFromPPO(o) {
  var v = Math.round(Number(o.value) || 0), type = o.type || "sup", max = maxFor(type);
  var basic, pct = null, stepped = false, capped = false;
  if (o.mode === "ppo6") { basic = up(v * CONFIG.pre2016Factor); }
  else if (o.mode === "lastpay") { pct = rateFor(type); basic = up(v * pct / 100); }
  else { basic = v; }
  if (o.mode !== "ppo7") {
    if (basic < CONFIG.minPension) { basic = CONFIG.minPension; stepped = true; }
    if (basic > max) { basic = max; capped = true; }
  }
  return { basic: basic, mode: o.mode, type: type, pct: pct, stepped: stepped, capped: capped, max: max };
}

/* Pre-2016 pensioners under the 7th CPC (DoPPW OM 12.05.2017 para 4-5):
   A = pension on 31.12.2015 x 2.57 (rounded up; stepped up to Rs 9,000)
   B = notional pay on 01.01.2016 x 50% (pension / enhanced FP) or 30% (normal FP), rounded up
   revised = higher of A and B, min Rs 9,000, max 50% / 30% of Rs 2,50,000. */
function pre2016Revision(o) {
  var type = o.type || "sup", pre = Math.round(Number(o.prePension) || 0);
  var np = Math.round(Number(o.notionalPay) || 0), max = maxFor(type), pct = rateFor(type);
  var A = up(pre * CONFIG.pre2016Factor), Araw = A;
  if (A < CONFIG.minPension) A = CONFIG.minPension;
  var B = np > 0 ? up(np * pct / 100) : null, Braw = B;
  if (B !== null && B < CONFIG.minPension) B = CONFIG.minPension;
  var payable = B !== null && B > A ? B : A, method = B !== null && B > A ? "B" : "A";
  var capped = false;
  if (payable > max) { payable = max; capped = true; }
  return { type: type, pre: pre, notionalPay: np || null, pct: pct, A: A, Araw: Araw, B: B, Braw: Braw,
           payable: payable, method: method, steppedA: Araw < CONFIG.minPension, capped: capped, max: max };
}

/* DR hike and its arrears.
   o = {basic, age, oldDR, newDR, comm, effFrom: "YYYY-MM", payMonth: "YYYY-MM"}
   Arrears = (DR at new rate - DR at old rate) x months from effFrom (incl.)
   to payMonth (excl.). Age slab assumed constant over the period. */
function calcDR(o) {
  var oldP = pensionParts(o.basic, o.age, o.oldDR), newP = pensionParts(o.basic, o.age, o.newDR);
  var comm = Math.round(Number(o.comm) || 0);
  var inc = newP.dr - oldP.dr;
  var months = Math.max(0, monthsBetween(o.effFrom, o.payMonth));
  return { basic: oldP.basic, addPct: oldP.addPct, add: oldP.add, oldDR: Number(o.oldDR), newDR: Number(o.newDR),
           oldDRAmt: oldP.dr, newDRAmt: newP.dr, increase: inc, months: months, arrears: Math.max(0, inc) * months,
           grossOld: oldP.gross, grossNew: newP.gross, comm: comm, netOld: oldP.gross - comm, netNew: newP.gross - comm,
           effFrom: o.effFrom, payMonth: o.payMonth };
}

/* Defaults for the DA/DR calculator, derived from CONFIG (see drHistory). */
function drDefaults() {
  var h = CONFIG.drHistory, last = h[h.length - 1];
  if (CONFIG.drNextAssumed !== null && CONFIG.drNextAssumed !== undefined)
    return { oldDR: CONFIG.currentDR, newDR: CONFIG.drNextAssumed, effFrom: CONFIG.drNextFrom, official: false };
  return { oldDR: h.length > 1 ? h[h.length - 2].pct : last.pct, newDR: last.pct, effFrom: last.from, official: true };
}

/* ------------------------------ i18n -------------------------------- */
var I18N = {
  en: {
    skip: "Skip to calculator",
    nav_home: "Pension Calculator", nav_fitment: "Fitment Factor", nav_family: "Family Pension",
    nav_defence: "Defence Pension", nav_chart: "Pension Chart", nav_updates: "Latest Update",
    nav_menu: "Menu", lang_btn: "हिंदी",
    est_banner: "Estimate — not official. The 8th Pay Commission has not announced a fitment factor.",
    status_label: "Status", status_text: "8th CPC constituted 3 Nov 2025 · Report due about May 2027 · No official fitment factor · DR 60% from 1 Jan 2026",
    updated: "Data last updated:",
    calc_title: "8th CPC pension calculator",
    lbl_basic: "Current basic pension (7th CPC), ₹ per month",
    hint_basic: "As shown in your PPO / bank pension slip — before DR and commutation deduction.",
    lbl_type: "Pension type",
    opt_sup: "Superannuation / retiring pension", opt_fpn: "Family pension — normal rate (30%)", opt_fpe: "Family pension — enhanced rate (50%)",
    lbl_age: "Age of pensioner / family pensioner (years)",
    hint_age: "Additional pension starts at 80 (20%), 85 (30%), 90 (40%), 95 (50%), 100 (100%).",
    lbl_factor: "Fitment factor", opt_custom: "Custom…", lbl_custom: "Custom fitment factor",
    f_est: "estimate", f_7cpc: "7th CPC used", f_demand: "staff/pensioner demand", f_official: "OFFICIAL",
    lbl_dr: "Current Dearness Relief (DR) %", hint_dr: "60% from 1 Jan 2026. Change it if a new DR is announced.",
    lbl_eff: "Assumed date of effect (arrears from)", hint_eff: "Widely expected 1 Jan 2026 — not official.",
    lbl_pay: "Month revised pension starts being paid", hint_pay: "Arrears are counted up to the month before this.",
    btn_calc: "Calculate", btn_reset: "Reset",
    res_title: "Your estimated 8th CPC pension", badge_est: "Estimate — not official",
    sec_current: "Current pension (7th CPC)", sec_new: "Estimated pension (8th CPC)",
    r_basic: "Basic pension", r_add: "Additional pension", r_dr: "Dearness Relief", r_total: "Total monthly pension",
    r_newbasic: "New basic pension", r_newdr: "DR after revision (assumed)",
    r_inc: "Monthly increase", r_arrears: "Estimated arrears", r_months: "months",
    cmp_title: "Comparison across fitment factors", cmp_factor: "Factor", cmp_newbasic: "New basic", cmp_newtotal: "New total", cmp_inc: "Change vs today",
    steps_title: "How this was calculated",
    s1: "Additional pension today = {basic} × {pct}% = {add}",
    s2: "DR today = ({basic} + {add}) × {dr}% = {drAmt}",
    s3: "Current total = {basic} + {add} + {drAmt} = {total}",
    s4: "New basic = {basic} × {factor} = {raw} (rounded up to the next rupee)",
    s4floor: "Raised to the estimated new minimum of {min} (= ₹9,000 × {factor})",
    s4cap: "Limited to the estimated new maximum of {max}",
    s5: "New additional pension = {nb} × {pct}% = {nadd}",
    s6: "DR on revised pension assumed {ndr}% at the start (past pay commissions reset DR to 0)",
    s7: "New total = {ntotal}; increase = {inc} ({incpct})",
    s8: "Arrears = {inc} × {months} months ({from} to month before {to}) = {arr}",
    btn_share: "Copy share link", btn_wa: "Share on WhatsApp", btn_print: "Print", btn_dl: "Download result",
    copied: "Link copied", wa_msg: "My estimated 8th Pay Commission pension (estimate, not official):",
    warn_min: "The amount entered is below the 7th CPC minimum pension of ₹9,000. Check your PPO; the new basic is raised to the estimated new minimum.",
    warn_max: "The amount entered is above the 7th CPC maximum for this pension type, so the maximum was used.",
    err_basic: "Please enter your current basic pension (₹1,000 to ₹2,50,000).",
    err_factor: "Please enter a fitment factor between 1 and 6.",
    official_banner: "Official fitment factor announced:",
    assume_title: "Assumptions",
    a1: "Fitment factor applied to basic pension, rounded up to the next rupee (method used by the 7th CPC).",
    a2: "New minimum pension estimated as ₹9,000 × fitment factor; new maximum as 7th CPC maximum × fitment factor.",
    a3: "DR restarts at 0% on the revised pension; additional pension percentages for age stay the same.",
    a4: "Arrears = monthly increase × months, using today's DR for the whole period. Actual arrears will use the DR actually drawn each month.",
    a5: "Commutation deduction, income tax and Fixed Medical Allowance are not included.",
    reverse_title: "Find the fitment factor from two amounts",
    lbl_rev_old: "Current basic pension (₹)", lbl_rev_new: "Expected new basic pension (₹)", btn_rev: "Find factor",
    rev_out: "Implied fitment factor: {f} (an increase of {pct} in basic pension)",
    fp_title: "Don't know your family pension? Work it out from last pay",
    lbl_lastpay: "Last basic pay drawn (7th CPC), ₹", btn_fp: "Work out",
    fp_out: "Normal rate (30%): {n} · Enhanced rate (50%): {e}", fp_use_n: "Use normal", fp_use_e: "Use enhanced",
    chart_note: "New basic pension only (no DR). Rounded up to the next rupee. Estimate — not official.",
    footer_disc: "Independent, unofficial calculator. Not affiliated with, endorsed by or part of the Government of India, DoPPW, CPAO or the 8th Central Pay Commission. All results are estimates for information only.",
    footer_links: "Site", ftr_about: "About", ftr_privacy: "Privacy", ftr_disclaimer: "Disclaimer", ftr_contact: "Contact",
    nav_finder: "Find Basic Pension", nav_pre2016: "Pre-2016 Pensioners", nav_dadr: "DA/DR Calculator",
    ftr_how: "How we calculate", ftr_changelog: "Changelog", ftr_tools: "More calculators",
    link_finder: "Don't know your basic pension? Work it out from your bank credit or PPO →",
    lnk_how: "How we calculate (formulas & sources)", lnk_changelog: "Changelog",
    bf_title: "Find your basic pension", bf_lbl_mode: "What figure do you have?",
    bf_mode_credit: "Monthly amount credited to my bank account", bf_mode_ppo7: "PPO showing basic pension from 2016 onwards (7th CPC)",
    bf_mode_ppo6: "Old PPO: pension as on 31.12.2015 (6th CPC)", bf_mode_lastpay: "Last basic pay drawn (7th CPC)",
    bf_lbl_credit: "Pension credited for one normal month, ₹", bf_hint_credit: "Pick a month with no arrears or extra payments (passbook / bank SMS).",
    bf_lbl_dr: "DR % included in that credit", bf_hint_dr: "60% now. If you use a credit from before the 60% rate reached your bank (around April–May 2026), use 58%.",
    bf_lbl_comm: "Commutation deduction", bf_comm_none: "None / already restored", bf_comm_amt: "I know the monthly deduction in ₹", bf_comm_pct: "I know the % commuted (approximate)",
    bf_lbl_commval: "Deduction (₹) or percentage commuted (%)", bf_hint_commval: "Shown as 'commuted pension' in the PPO or bank pension slip. It stops after 15 years.",
    bf_lbl_fma: "The credit includes Fixed Medical Allowance (₹1,000)", bf_hint_fma: "Paid to pensioners living outside CGHS areas who do not use CGHS OPD.",
    bf_lbl_other: "Other deductions (income tax TDS, recoveries), ₹", bf_hint_other: "Leave blank if none.",
    bf_lbl_ppo7: "Basic pension shown on the PPO, ₹", bf_hint_ppo7: "Before DR and commutation, without additional pension for age.",
    bf_lbl_ppo6: "Basic pension / family pension as on 31.12.2015, ₹", bf_hint_ppo6: "As fixed under the 6th CPC, including any commuted portion.",
    bf_lbl_lastpay: "Last basic pay drawn (7th CPC pay level), ₹", bf_hint_lastpay: "Pension = 50% of last pay; family pension = 30% (normal) or 50% (enhanced).",
    bf_btn: "Find my basic pension", bf_res: "Your basic pension (estimated)",
    bf_exact: "This basic pension reproduces your credit of {c} exactly.",
    bf_near: "No whole-rupee basic pension gives exactly {c}. The closest is {b}, which gives {c2} ({d}). Check the DR %, other deductions, or whether the month included arrears.",
    bf_multi: "Several basic pensions round to the same credit ({list}); the lowest is shown. Your PPO has the exact figure.",
    bf_tbl: "How your credit is made up", bf_r_comm: "Less: commutation deduction", bf_r_fma: "Plus: Fixed Medical Allowance",
    bf_r_other: "Less: other deductions", bf_r_credit: "Amount credited",
    bf_ppo6_note: "Revised under the 7th CPC as {pre} × 2.57 = {raw}. If your revised PPO shows a higher pension from notional pay fixation, use that figure instead.",
    bf_lastpay_note: "{pct}% of last pay {lp} = {raw}, within the 7th CPC limits ({min} to {max}).",
    bf_stepped: "Raised to the minimum pension of ₹9,000.", bf_capped: "Limited to the maximum of {max}.",
    bf_ppo7_note: "Used as entered. This is the figure to put in the 8th CPC calculator.",
    bf_use: "Use {b} in the 8th CPC calculator →", bf_use_dr: "See DR and arrears for {b} →", bf_use_pre: "Pre-2016? Compare both 7th CPC methods →",
    bf_err: "Please enter an amount between ₹1,000 and ₹5,00,000.",
    warn_low_basic: "The result is below the ₹9,000 minimum pension. Re-check the DR %, whether FMA is included, and any deductions.",
    warn_high_basic: "The result is above the ₹1,25,000 maximum pension. Re-check the figures.",
    bf_disc: "Estimate from the figures you entered. Your PPO and pension slip are the final authority.",
    p6_title: "Pre-2016 pensioner calculator",
    p6_lbl_pre: "Basic pension / family pension as on 31.12.2015 (6th CPC), ₹", p6_hint_pre: "Including any commuted portion; without additional pension for age.",
    p6_lbl_np: "Notional pay as on 01.01.2016 (optional), ₹", p6_hint_np: "From your revised PPO or revision authority (7th CPC pay matrix). Leave blank if you don't have it.",
    p6_btn: "Calculate", p6_res: "Your revised pension: both methods",
    p6_mA: "Method A (multiplier): {pre} × 2.57", p6_mB: "Method B (notional pay): {np} × {pct}%", p6_mB_na: "Method B (notional pay): enter notional pay to compare",
    p6_payable: "7th CPC basic pension (higher of A and B)", p6_stepped: "stepped up to ₹9,000", p6_capped: "limited to the maximum of {max}",
    p6_today: "Total pension today with {dr}% DR", p6_8th: "Estimated 8th CPC basic pension at ×{f}", p6_8th_total: "Estimated 8th CPC total (DR assumed to restart at 0%)",
    p6_note_b: "Method B is higher. The revision by notional pay fixation was done by your Head of Office through a revised authority, not automatically by the bank. If your pension slip still shows Method A, ask your Head of Office / PAO.",
    p6_note_a: "Method A is the amount every pre-2016 pensioner received automatically from 1.1.2016.",
    p6_8th_note: "The 8th CPC figure is an estimate: your 7th CPC basic pension × the chosen factor. Whether the 8th CPC will again offer a notional-pay option for older pensioners is not known.",
    p6_use: "Open the full 8th CPC calculator with {b} →",
    p6_err: "Please enter the 31.12.2015 pension (₹1,000 to ₹1,25,000). Notional pay, if entered, must be ₹7,000 to ₹2,50,000.",
    dr_title: "DA / DR calculator with arrears",
    dr_lbl_basic: "Basic pension / family pension, ₹", dr_hint_basic: "Before commutation deduction: DR is paid on the full pension.",
    dr_lbl_comm: "Commutation deduction (optional), ₹", dr_hint_comm: "Only to show the amount credited; it does not change DR.",
    dr_lbl_old: "Old DR %", dr_hint_old: "Rate before the hike.",
    dr_lbl_new: "New DR %", dr_hint_new_est: "{x}% is the press / CPI-IW formula estimate for {m}. Not announced — change it when the order comes.",
    dr_hint_new_off: "{x}% is the latest official rate (from {m}).",
    dr_lbl_from: "New DR effective from", dr_lbl_pay: "First month paid at the new rate", dr_hint_pay: "Arrears are counted up to the month before this.",
    dr_btn: "Calculate DR & arrears", dr_res: "Your Dearness Relief",
    dr_r_old: "DR at {p}%", dr_r_new: "DR at {p}%", dr_r_inc: "Increase per month", dr_r_arr: "Arrears", dr_r_gross: "Gross pension (basic + additional + DR)",
    dr_r_net: "Credited after commutation deduction", dr_before: "Before", dr_after: "After",
    dr_badge_hyp: "New rate not announced — estimate", dr_badge_off: "Official rates",
    dr_s1: "DR = (basic {b} + additional {a}) × DR%, rounded up to the next rupee.", dr_s2: "Arrears = {inc} × {m} months ({from} to month before {to}) = {arr}.",
    dr_s3: "Arrears assume the same basic pension and age slab for the whole period, and are before any income-tax deduction.",
    dr_err: "Please enter basic pension (₹1,000 to ₹2,50,000) and DR rates between 0 and 200.",
    dr_hist: "DR history used by this site"
  },
  hi: {
    skip: "कैलकुलेटर पर जाएँ",
    nav_home: "पेंशन कैलकुलेटर", nav_fitment: "फिटमेंट फैक्टर", nav_family: "पारिवारिक पेंशन",
    nav_defence: "रक्षा पेंशन", nav_chart: "पेंशन चार्ट", nav_updates: "ताज़ा अपडेट",
    nav_menu: "मेनू", lang_btn: "English",
    est_banner: "अनुमान — आधिकारिक नहीं। 8वें वेतन आयोग ने अभी कोई फिटमेंट फैक्टर घोषित नहीं किया है।",
    status_label: "स्थिति", status_text: "8वाँ वेतन आयोग 3 नवंबर 2025 को गठित · रिपोर्ट लगभग मई 2027 तक · कोई आधिकारिक फिटमेंट फैक्टर नहीं · 1 जनवरी 2026 से DR 60%",
    updated: "डेटा अंतिम बार अपडेट:",
    calc_title: "8वाँ वेतन आयोग पेंशन कैलकुलेटर",
    lbl_basic: "वर्तमान मूल पेंशन (7वाँ वेतन आयोग), ₹ प्रति माह",
    hint_basic: "PPO / बैंक पेंशन स्लिप में दी गई राशि — DR और कम्यूटेशन कटौती से पहले।",
    lbl_type: "पेंशन का प्रकार",
    opt_sup: "सेवानिवृत्ति पेंशन (सुपरएनुएशन / रिटायरिंग)", opt_fpn: "पारिवारिक पेंशन — सामान्य दर (30%)", opt_fpe: "पारिवारिक पेंशन — बढ़ी हुई दर (50%)",
    lbl_age: "पेंशनभोगी / पारिवारिक पेंशनभोगी की आयु (वर्ष)",
    hint_age: "अतिरिक्त पेंशन: 80 वर्ष पर 20%, 85 पर 30%, 90 पर 40%, 95 पर 50%, 100 पर 100%।",
    lbl_factor: "फिटमेंट फैक्टर", opt_custom: "अपना फैक्टर…", lbl_custom: "अपना फिटमेंट फैक्टर",
    f_est: "अनुमान", f_7cpc: "7वें आयोग में लागू", f_demand: "कर्मचारी/पेंशनभोगी माँग", f_official: "आधिकारिक",
    lbl_dr: "वर्तमान महंगाई राहत (DR) %", hint_dr: "1 जनवरी 2026 से 60%। नई DR घोषित हो तो बदलें।",
    lbl_eff: "मानी गई लागू तिथि (एरियर कब से)", hint_eff: "1 जनवरी 2026 की व्यापक उम्मीद — आधिकारिक नहीं।",
    lbl_pay: "नई पेंशन का भुगतान किस महीने से", hint_pay: "एरियर इससे पिछले महीने तक गिना जाता है।",
    btn_calc: "गणना करें", btn_reset: "रीसेट",
    res_title: "आपकी अनुमानित 8वें वेतन आयोग की पेंशन", badge_est: "अनुमान — आधिकारिक नहीं",
    sec_current: "वर्तमान पेंशन (7वाँ आयोग)", sec_new: "अनुमानित पेंशन (8वाँ आयोग)",
    r_basic: "मूल पेंशन", r_add: "अतिरिक्त पेंशन", r_dr: "महंगाई राहत (DR)", r_total: "कुल मासिक पेंशन",
    r_newbasic: "नई मूल पेंशन", r_newdr: "संशोधन के बाद DR (माना गया)",
    r_inc: "मासिक बढ़ोतरी", r_arrears: "अनुमानित एरियर", r_months: "महीने",
    cmp_title: "अलग-अलग फिटमेंट फैक्टर पर तुलना", cmp_factor: "फैक्टर", cmp_newbasic: "नई मूल", cmp_newtotal: "नई कुल", cmp_inc: "आज की तुलना में अंतर",
    steps_title: "गणना कैसे हुई",
    s1: "आज की अतिरिक्त पेंशन = {basic} × {pct}% = {add}",
    s2: "आज की DR = ({basic} + {add}) × {dr}% = {drAmt}",
    s3: "वर्तमान कुल = {basic} + {add} + {drAmt} = {total}",
    s4: "नई मूल पेंशन = {basic} × {factor} = {raw} (अगले पूरे रुपये तक)",
    s4floor: "अनुमानित नई न्यूनतम पेंशन {min} (= ₹9,000 × {factor}) तक बढ़ाई गई",
    s4cap: "अनुमानित नई अधिकतम सीमा {max} तक सीमित",
    s5: "नई अतिरिक्त पेंशन = {nb} × {pct}% = {nadd}",
    s6: "संशोधित पेंशन पर शुरुआत में DR {ndr}% माना गया (पिछले आयोगों में DR शून्य से शुरू हुई)",
    s7: "नई कुल = {ntotal}; बढ़ोतरी = {inc} ({incpct})",
    s8: "एरियर = {inc} × {months} महीने ({from} से {to} से पहले के महीने तक) = {arr}",
    btn_share: "शेयर लिंक कॉपी करें", btn_wa: "WhatsApp पर शेयर करें", btn_print: "प्रिंट", btn_dl: "रिज़ल्ट डाउनलोड",
    copied: "लिंक कॉपी हो गया", wa_msg: "8वें वेतन आयोग में मेरी अनुमानित पेंशन (अनुमान, आधिकारिक नहीं):",
    warn_min: "दर्ज राशि 7वें आयोग की न्यूनतम पेंशन ₹9,000 से कम है। PPO जाँचें; नई मूल पेंशन अनुमानित नई न्यूनतम तक बढ़ाई गई है।",
    warn_max: "दर्ज राशि इस पेंशन प्रकार की 7वें आयोग की अधिकतम सीमा से ज़्यादा है, इसलिए अधिकतम राशि ली गई।",
    err_basic: "कृपया वर्तमान मूल पेंशन दर्ज करें (₹1,000 से ₹2,50,000)।",
    err_factor: "कृपया 1 से 6 के बीच फिटमेंट फैक्टर दर्ज करें।",
    official_banner: "आधिकारिक फिटमेंट फैक्टर घोषित:",
    assume_title: "मान्यताएँ",
    a1: "फिटमेंट फैक्टर मूल पेंशन पर लगाया गया, अगले पूरे रुपये तक (7वें आयोग का तरीका)।",
    a2: "नई न्यूनतम पेंशन = ₹9,000 × फिटमेंट फैक्टर; नई अधिकतम = 7वें आयोग की अधिकतम × फैक्टर (अनुमान)।",
    a3: "संशोधित पेंशन पर DR 0% से शुरू; आयु आधारित अतिरिक्त पेंशन के प्रतिशत वही रहेंगे।",
    a4: "एरियर = मासिक बढ़ोतरी × महीने, पूरी अवधि के लिए आज की DR मानकर। असली एरियर हर महीने वास्तव में मिली DR से निकलेगा।",
    a5: "कम्यूटेशन कटौती, आयकर और फिक्स्ड मेडिकल अलाउंस शामिल नहीं हैं।",
    reverse_title: "दो राशियों से फिटमेंट फैक्टर निकालें",
    lbl_rev_old: "वर्तमान मूल पेंशन (₹)", lbl_rev_new: "अपेक्षित नई मूल पेंशन (₹)", btn_rev: "फैक्टर निकालें",
    rev_out: "निहित फिटमेंट फैक्टर: {f} (मूल पेंशन में {pct} की बढ़ोतरी)",
    fp_title: "पारिवारिक पेंशन नहीं पता? अंतिम वेतन से निकालें",
    lbl_lastpay: "अंतिम मूल वेतन (7वाँ आयोग), ₹", btn_fp: "निकालें",
    fp_out: "सामान्य दर (30%): {n} · बढ़ी हुई दर (50%): {e}", fp_use_n: "सामान्य लें", fp_use_e: "बढ़ी हुई लें",
    chart_note: "केवल नई मूल पेंशन (DR के बिना), अगले पूरे रुपये तक। अनुमान — आधिकारिक नहीं।",
    footer_disc: "स्वतंत्र, अनौपचारिक कैलकुलेटर। भारत सरकार, DoPPW, CPAO या 8वें केंद्रीय वेतन आयोग से कोई संबंध, समर्थन या हिस्सा नहीं। सभी परिणाम केवल जानकारी हेतु अनुमान हैं।",
    footer_links: "साइट", ftr_about: "हमारे बारे में", ftr_privacy: "गोपनीयता", ftr_disclaimer: "अस्वीकरण", ftr_contact: "संपर्क",
    nav_finder: "मूल पेंशन पता करें", nav_pre2016: "2016 से पहले के पेंशनर", nav_dadr: "DA/DR कैलकुलेटर",
    ftr_how: "हम गणना कैसे करते हैं", ftr_changelog: "बदलाव सूची", ftr_tools: "अन्य कैलकुलेटर",
    link_finder: "मूल पेंशन नहीं पता? बैंक में आई रकम या PPO से निकालें →",
    lnk_how: "हम गणना कैसे करते हैं (सूत्र और स्रोत)", lnk_changelog: "बदलाव सूची",
    bf_title: "अपनी मूल पेंशन पता करें", bf_lbl_mode: "आपके पास कौन-सी रकम है?",
    bf_mode_credit: "बैंक खाते में हर महीने आने वाली पेंशन", bf_mode_ppo7: "2016 या बाद का PPO जिसमें मूल पेंशन लिखी है (7वाँ आयोग)",
    bf_mode_ppo6: "पुराना PPO: 31.12.2015 की पेंशन (6ठा आयोग)", bf_mode_lastpay: "अंतिम मूल वेतन (7वाँ आयोग)",
    bf_lbl_credit: "किसी सामान्य महीने में आई पेंशन, ₹", bf_hint_credit: "ऐसा महीना चुनें जिसमें एरियर या कोई अतिरिक्त रकम न हो (पासबुक / बैंक SMS)।",
    bf_lbl_dr: "उस रकम में शामिल DR %", bf_hint_dr: "अभी 60%। अगर 60% की दर बैंक में लागू होने (लगभग अप्रैल–मई 2026) से पहले की रकम ले रहे हैं, तो 58% लें।",
    bf_lbl_comm: "कम्यूटेशन कटौती", bf_comm_none: "नहीं / बहाल हो चुकी", bf_comm_amt: "मासिक कटौती ₹ में पता है", bf_comm_pct: "कम्यूट किया गया % पता है (लगभग)",
    bf_lbl_commval: "कटौती (₹) या कम्यूट किया गया प्रतिशत (%)", bf_hint_commval: "PPO या बैंक पेंशन स्लिप में 'commuted pension' के रूप में लिखा होता है। 15 साल बाद बंद हो जाती है।",
    bf_lbl_fma: "रकम में फिक्स्ड मेडिकल अलाउंस (₹1,000) शामिल है", bf_hint_fma: "CGHS क्षेत्र से बाहर रहने वाले और CGHS OPD न लेने वाले पेंशनभोगियों को मिलता है।",
    bf_lbl_other: "अन्य कटौती (आयकर TDS, वसूली), ₹", bf_hint_other: "न हो तो खाली छोड़ें।",
    bf_lbl_ppo7: "PPO में लिखी मूल पेंशन, ₹", bf_hint_ppo7: "DR और कम्यूटेशन से पहले, आयु वाली अतिरिक्त पेंशन के बिना।",
    bf_lbl_ppo6: "31.12.2015 की मूल पेंशन / पारिवारिक पेंशन, ₹", bf_hint_ppo6: "6ठे आयोग में तय राशि, कम्यूट किए गए हिस्से सहित।",
    bf_lbl_lastpay: "अंतिम मूल वेतन (7वें आयोग का पे लेवल), ₹", bf_hint_lastpay: "पेंशन = अंतिम वेतन का 50%; पारिवारिक पेंशन = 30% (सामान्य) या 50% (बढ़ी हुई)।",
    bf_btn: "मेरी मूल पेंशन निकालें", bf_res: "आपकी मूल पेंशन (अनुमानित)",
    bf_exact: "यह मूल पेंशन आपकी {c} की रकम से बिल्कुल मेल खाती है।",
    bf_near: "किसी भी पूरे रुपये वाली मूल पेंशन से ठीक {c} नहीं बनता। सबसे नज़दीकी {b} है, जिससे {c2} बनता है ({d})। DR %, अन्य कटौती या उस महीने के एरियर की जाँच करें।",
    bf_multi: "कई मूल पेंशन राउंडिंग के बाद एक ही रकम देती हैं ({list}); सबसे कम दिखाई गई है। सही आँकड़ा आपके PPO में है।",
    bf_tbl: "आपकी रकम कैसे बनती है", bf_r_comm: "घटाएँ: कम्यूटेशन कटौती", bf_r_fma: "जोड़ें: फिक्स्ड मेडिकल अलाउंस",
    bf_r_other: "घटाएँ: अन्य कटौती", bf_r_credit: "खाते में आई रकम",
    bf_ppo6_note: "7वें आयोग में संशोधन: {pre} × 2.57 = {raw}। अगर आपके संशोधित PPO में नोशनल वेतन निर्धारण से ज़्यादा पेंशन लिखी है, तो वही राशि लें।",
    bf_lastpay_note: "अंतिम वेतन {lp} का {pct}% = {raw}, 7वें आयोग की सीमा ({min} से {max}) के भीतर।",
    bf_stepped: "न्यूनतम पेंशन ₹9,000 तक बढ़ाई गई।", bf_capped: "अधिकतम {max} तक सीमित।",
    bf_ppo7_note: "जैसी दर्ज की, वैसी ही ली गई। 8वें आयोग के कैलकुलेटर में यही राशि डालें।",
    bf_use: "{b} को 8वें आयोग के कैलकुलेटर में डालें →", bf_use_dr: "{b} पर DR और एरियर देखें →", bf_use_pre: "2016 से पहले रिटायर? 7वें आयोग के दोनों तरीके देखें →",
    bf_err: "कृपया ₹1,000 से ₹5,00,000 के बीच राशि दर्ज करें।",
    warn_low_basic: "परिणाम न्यूनतम पेंशन ₹9,000 से कम है। DR %, FMA शामिल है या नहीं, और कटौतियाँ दोबारा जाँचें।",
    warn_high_basic: "परिणाम अधिकतम पेंशन ₹1,25,000 से ज़्यादा है। आँकड़े दोबारा जाँचें।",
    bf_disc: "आपके दर्ज आँकड़ों पर आधारित अनुमान। अंतिम प्रमाण आपका PPO और पेंशन स्लिप है।",
    p6_title: "2016 से पहले के पेंशनभोगियों का कैलकुलेटर",
    p6_lbl_pre: "31.12.2015 की मूल पेंशन / पारिवारिक पेंशन (6ठा आयोग), ₹", p6_hint_pre: "कम्यूट किए गए हिस्से सहित; आयु वाली अतिरिक्त पेंशन के बिना।",
    p6_lbl_np: "01.01.2016 का नोशनल वेतन (वैकल्पिक), ₹", p6_hint_np: "संशोधित PPO या संशोधन प्राधिकार से (7वें आयोग का पे मैट्रिक्स)। न हो तो खाली छोड़ें।",
    p6_btn: "गणना करें", p6_res: "आपकी संशोधित पेंशन: दोनों तरीके",
    p6_mA: "तरीका A (गुणक): {pre} × 2.57", p6_mB: "तरीका B (नोशनल वेतन): {np} × {pct}%", p6_mB_na: "तरीका B (नोशनल वेतन): तुलना के लिए नोशनल वेतन दर्ज करें",
    p6_payable: "7वें आयोग की मूल पेंशन (A और B में जो ज़्यादा)", p6_stepped: "₹9,000 तक बढ़ाई गई", p6_capped: "अधिकतम {max} तक सीमित",
    p6_today: "{dr}% DR सहित आज की कुल पेंशन", p6_8th: "×{f} पर अनुमानित 8वें आयोग की मूल पेंशन", p6_8th_total: "अनुमानित 8वें आयोग की कुल पेंशन (DR 0% से शुरू मानी गई)",
    p6_note_b: "तरीका B ज़्यादा है। नोशनल वेतन निर्धारण से संशोधन आपके विभागाध्यक्ष ने संशोधित प्राधिकार से किया था, बैंक ने अपने-आप नहीं। अगर पेंशन स्लिप में अब भी तरीका A वाली राशि है, तो अपने विभागाध्यक्ष / PAO से पूछें।",
    p6_note_a: "तरीका A वाली राशि हर 2016-पूर्व पेंशनभोगी को 1.1.2016 से अपने-आप मिली थी।",
    p6_8th_note: "8वें आयोग वाला आँकड़ा अनुमान है: आपकी 7वें आयोग की मूल पेंशन × चुना गया फैक्टर। 8वाँ आयोग पुराने पेंशनभोगियों के लिए फिर नोशनल वेतन वाला विकल्प देगा या नहीं, यह अभी पता नहीं।",
    p6_use: "{b} के साथ पूरा 8वें आयोग का कैलकुलेटर खोलें →",
    p6_err: "कृपया 31.12.2015 की पेंशन दर्ज करें (₹1,000 से ₹1,25,000)। नोशनल वेतन दर्ज करें तो ₹7,000 से ₹2,50,000 के बीच हो।",
    dr_title: "DA / DR कैलकुलेटर (एरियर सहित)",
    dr_lbl_basic: "मूल पेंशन / पारिवारिक पेंशन, ₹", dr_hint_basic: "कम्यूटेशन कटौती से पहले: DR पूरी पेंशन पर मिलती है।",
    dr_lbl_comm: "कम्यूटेशन कटौती (वैकल्पिक), ₹", dr_hint_comm: "केवल खाते में आने वाली रकम दिखाने के लिए; इससे DR नहीं बदलती।",
    dr_lbl_old: "पुरानी DR %", dr_hint_old: "बढ़ोतरी से पहले की दर।",
    dr_lbl_new: "नई DR %", dr_hint_new_est: "{x}% {m} के लिए मीडिया / CPI-IW फ़ॉर्मूले का अनुमान है। घोषित नहीं — आदेश आने पर बदलें।",
    dr_hint_new_off: "{x}% नवीनतम आधिकारिक दर है ({m} से)।",
    dr_lbl_from: "नई DR कब से लागू", dr_lbl_pay: "नई दर पर भुगतान किस महीने से", dr_hint_pay: "एरियर इससे पिछले महीने तक गिना जाता है।",
    dr_btn: "DR और एरियर निकालें", dr_res: "आपकी महंगाई राहत (DR)",
    dr_r_old: "{p}% पर DR", dr_r_new: "{p}% पर DR", dr_r_inc: "मासिक बढ़ोतरी", dr_r_arr: "एरियर", dr_r_gross: "सकल पेंशन (मूल + अतिरिक्त + DR)",
    dr_r_net: "कम्यूटेशन कटौती के बाद खाते में", dr_before: "पहले", dr_after: "बाद में",
    dr_badge_hyp: "नई दर घोषित नहीं — अनुमान", dr_badge_off: "आधिकारिक दरें",
    dr_s1: "DR = (मूल {b} + अतिरिक्त {a}) × DR%, अगले पूरे रुपये तक।", dr_s2: "एरियर = {inc} × {m} महीने ({from} से {to} से पहले के महीने तक) = {arr}।",
    dr_s3: "एरियर में पूरी अवधि के लिए वही मूल पेंशन और आयु स्लैब माना गया है, और यह आयकर कटौती से पहले है।",
    dr_err: "कृपया मूल पेंशन (₹1,000 से ₹2,50,000) और 0 से 200 के बीच DR दरें दर्ज करें।",
    dr_hist: "इस साइट में इस्तेमाल DR का इतिहास"
  }
};
/* ---- strings added 28 Oct 2026 (bilingual pages, commutation calculator, new pages) ---- */
(function (X) { for (var lg in X) for (var k in X[lg]) I18N[lg][k] = X[lg][k]; })({
  en: {
    nav_commutation: "Commutation & Restoration", nav_lifecert: "Life Certificate Guide", nav_minpension: "Minimum Pension", nav_byamount: "Pension by Amount",
    ftr_editorial: "Editorial Policy",
    cm_title: "Commutation & restoration calculator",
    cm_lbl_basic: "Basic pension before commutation, ₹ per month", cm_hint_basic: "The full basic pension on your PPO (7th CPC), not the reduced amount.",
    cm_lbl_mode: "How do you know the commuted part?", cm_mode_pct: "As a percentage (up to 40%)", cm_mode_amt: "As a rupee amount (from PPO)",
    cm_lbl_pct: "Percentage commuted", cm_hint_pct: "Up to 40% of pension can be commuted.",
    cm_lbl_amt: "Commuted pension, ₹ per month", cm_hint_amt: "Printed on the PPO as the amount of monthly pension commuted. More accurate than a percentage.",
    cm_lbl_start: "Month the commutation deduction started", cm_hint_start: "Usually the month the lump sum was credited. Restoration is 15 years after this.",
    cm_lbl_cvf: "Commutation factor (optional)", cm_hint_cvf: "From the commutation table for your age next birthday. 8.194 applies at age next birthday 61 (retirement at 60).",
    cm_btn: "Calculate deduction & restoration", cm_res: "Your commutation at a glance",
    cm_r_ded: "Monthly deduction", cm_r_restore: "Full pension restored from", cm_r_left: "{m} months to go", cm_r_restored: "Already restored",
    cm_r_cvp: "Lump sum (commuted value), approx.", cm_col_now: "Now (until restoration)", cm_col_after: "After restoration",
    cm_r_credit: "Monthly credit (basic + additional + DR − deduction)", cm_r_8cpc: "8th CPC estimate at ×{f} (DR restarts at 0%)",
    cm_r_total: "Total deducted over 15 years",
    cm_s1: "Deduction = {b} × {p}% = {c} a month (rounded to the nearest rupee; the PPO amount is exact).",
    cm_s2: "Lump sum = {c} × {f} × 12 = {v} (approximate; the official figure is on your sanction).",
    cm_s3: "DR is paid on the full basic pension {b}, not on the reduced amount.",
    cm_s4: "Restoration: 15 years after {s} = {r}. The bank restores it automatically.",
    cm_s5: "8th CPC estimate assumes the deduction stays at the same rupee amount until restoration, as happened in the 7th CPC revision. Estimate — not official.",
    cm_err: "Please enter a basic pension (₹1,000 to ₹2,50,000) and a commuted part between 1% and 40% (or a rupee amount up to 40% of basic).",
    cm_badge: "Estimate — not official"
  },
  hi: {
    nav_commutation: "कम्यूटेशन और बहाली", nav_lifecert: "जीवन प्रमाण पत्र गाइड", nav_minpension: "न्यूनतम पेंशन", nav_byamount: "राशि के अनुसार पेंशन",
    ftr_editorial: "संपादकीय नीति",
    cm_title: "कम्यूटेशन और बहाली कैलकुलेटर",
    cm_lbl_basic: "कम्यूटेशन से पहले की मूल पेंशन, ₹ प्रति माह", cm_hint_basic: "PPO में लिखी पूरी मूल पेंशन (7वाँ आयोग), कटौती के बाद वाली रकम नहीं।",
    cm_lbl_mode: "कम्यूट किया हिस्सा कैसे पता है?", cm_mode_pct: "प्रतिशत में (40% तक)", cm_mode_amt: "रुपये में (PPO से)",
    cm_lbl_pct: "कम्यूट किया गया प्रतिशत", cm_hint_pct: "पेंशन का अधिकतम 40% कम्यूट हो सकता है।",
    cm_lbl_amt: "कम्यूट की गई पेंशन, ₹ प्रति माह", cm_hint_amt: "PPO में 'कम्यूट की गई मासिक पेंशन' के रूप में लिखी होती है। प्रतिशत से ज़्यादा सटीक।",
    cm_lbl_start: "कटौती किस महीने से शुरू हुई", cm_hint_start: "आमतौर पर वह महीना जब एकमुश्त राशि खाते में आई। बहाली इसके 15 साल बाद होती है।",
    cm_lbl_cvf: "कम्यूटेशन फैक्टर (वैकल्पिक)", cm_hint_cvf: "अगले जन्मदिन की आयु के हिसाब से कम्यूटेशन तालिका से। अगले जन्मदिन पर 61 वर्ष (60 पर रिटायरमेंट) के लिए 8.194।",
    cm_btn: "कटौती और बहाली निकालें", cm_res: "आपका कम्यूटेशन एक नज़र में",
    cm_r_ded: "मासिक कटौती", cm_r_restore: "पूरी पेंशन बहाल होगी", cm_r_left: "{m} महीने बाकी", cm_r_restored: "बहाली हो चुकी है",
    cm_r_cvp: "एकमुश्त राशि (कम्यूटेड वैल्यू), लगभग", cm_col_now: "अभी (बहाली तक)", cm_col_after: "बहाली के बाद",
    cm_r_credit: "मासिक रकम (मूल + अतिरिक्त + DR − कटौती)", cm_r_8cpc: "8वें आयोग का अनुमान ×{f} पर (DR 0% से शुरू)",
    cm_r_total: "15 साल में कुल कटौती",
    cm_s1: "कटौती = {b} × {p}% = {c} प्रति माह (नज़दीकी रुपये तक; PPO में लिखी रकम सटीक है)।",
    cm_s2: "एकमुश्त राशि = {c} × {f} × 12 = {v} (लगभग; असली रकम आपके स्वीकृति पत्र में है)।",
    cm_s3: "DR पूरी मूल पेंशन {b} पर मिलती है, कटौती के बाद वाली रकम पर नहीं।",
    cm_s4: "बहाली: {s} के 15 साल बाद = {r}। बैंक इसे अपने-आप बहाल करता है।",
    cm_s5: "8वें आयोग के अनुमान में माना गया है कि बहाली तक कटौती उतने ही रुपये रहेगी, जैसा 7वें आयोग के संशोधन में हुआ था। अनुमान — आधिकारिक नहीं।",
    cm_err: "कृपया मूल पेंशन (₹1,000 से ₹2,50,000) और 1% से 40% के बीच कम्यूट हिस्सा (या मूल पेंशन के 40% तक की रकम) दर्ज करें।",
    cm_badge: "अनुमान — आधिकारिक नहीं"
  }
});
var MONTHS = {
  en: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
  hi: ["जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]
};
function ymLabel(ym, lang) { var p = ym.split("-"); return MONTHS[lang || "en"][Number(p[1]) - 1] + " " + p[0]; }
function fmtPct(x) { return (x >= 0 ? "+" : "") + x.toFixed(1) + "%"; }
function fill(tpl, o) { return tpl.replace(/\{(\w+)\}/g, function (m, k) { return o[k] !== undefined ? o[k] : m; }); }

/* Commutation of pension: deduction, lump sum, restoration after 15 years, 8th CPC estimate.
   Pensioners' Portal (DoPPW): up to 40% may be commuted; CVP = commuted pension x commutation factor x 12;
   restored 15 years after the reduction became operative; DR on the original pension.
   OM 04.08.2016 para 4.3: on revision the commuted portion is deducted from the revised (consolidated) pension. */
function addMonthsYM(ym, n) {
  var p = String(ym).split("-").map(Number), t = p[0] * 12 + (p[1] - 1) + n, y = Math.floor(t / 12), m = t % 12 + 1;
  return y + "-" + (m < 10 ? "0" + m : m);
}
function calcCommutation(o) {
  var basic = Math.round(Number(o.basic) || 0);
  var dr = (o.dr === undefined || o.dr === null || o.dr === "") ? CONFIG.currentDR : Number(o.dr);
  var commuted = o.mode === "amount" ? Math.round(Number(o.amount) || 0) : Math.round(basic * Number(o.pct) / 100);
  var cvf = Number(o.cvFactor) || 8.194;
  var restoreYM = addMonthsYM(o.start, 180);
  var monthsLeft = Math.max(0, monthsBetween(o.nowYM, restoreYM));
  var restored = monthsLeft === 0;
  var addPct = additionalPct(o.age);
  var add = up(basic * addPct / 100), drAmt = up((basic + add) * dr / 100), gross = basic + add + drAmt;
  var rev = calcPension({ basic: basic, type: "sup", age: o.age, factor: o.fitment, dr: dr });
  var newGross = rev.revised.basic + rev.revised.add;
  return { basic: basic, commuted: commuted, pct: basic ? commuted / basic * 100 : 0, cvFactor: cvf,
    cvp: Math.round(commuted * cvf * 12), start: o.start, restoreYM: restoreYM, monthsLeft: monthsLeft, restored: restored,
    addPct: addPct, add: add, dr: dr, drAmt: drAmt, gross: gross, creditNow: gross - (restored ? 0 : commuted), creditAfter: gross,
    fitment: Number(o.fitment), newBasic: rev.revised.basic, newAdd: rev.revised.add,
    newCredit: newGross - (restored ? 0 : commuted), newCreditAfter: newGross, totalDeducted: commuted * 180 };
}

/* Node export for tests */
if (typeof module !== "undefined" && module.exports) {
  module.exports = { CONFIG: CONFIG, calcPension: calcPension, formatINR: formatINR, up: up,
    additionalPct: additionalPct, familyFromLastPay: familyFromLastPay, monthsBetween: monthsBetween, I18N: I18N,
    pensionParts: pensionParts, creditFromBasic: creditFromBasic, basicFromCredit: basicFromCredit, basicFromPPO: basicFromPPO,
    pre2016Revision: pre2016Revision, calcDR: calcDR, drDefaults: drDefaults,
    calcCommutation: calcCommutation, addMonthsYM: addMonthsYM };
}

/* ------------------------------ Browser UI -------------------------- */
(function () {
  if (typeof document === "undefined") return;
  var doc = document;
  var lang = "en";
  var lastResult = null;

  function $(id) { return doc.getElementById(id); }
  function t(k) { return (I18N[lang] && I18N[lang][k]) || I18N.en[k] || k; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function applyLang(l) {
    lang = I18N[l] ? l : "en";
    doc.documentElement.setAttribute("data-ui-lang", lang);
    var els = doc.querySelectorAll("[data-i18n]");
    for (var i = 0; i < els.length; i++) els[i].textContent = t(els[i].getAttribute("data-i18n"));
    var lb = $("langBtn"); if (lb) { lb.textContent = t("lang_btn"); lb.setAttribute("lang", lang === "en" ? "hi" : "en"); }
    try { localStorage.setItem("uiLang", lang); } catch (e) {}
    buildFactorOptions(); buildMonthOptions();
    if (lastResult) render(lastResult);
    renderChart();
    for (var r = 0; r < rerenders.length; r++) rerenders[r]();
  }

  /* ---- form setup ---- */
  function buildFactorOptions() {
    var sel = $("factor"); if (!sel) return;
    var cur = sel.getAttribute("data-ready") ? sel.value : "";
    sel.setAttribute("data-ready", "1");
    var html = "", list = CONFIG.presetFactors.slice();
    var off = CONFIG.officialFitmentFactor;
    if (off && !list.some(function (p) { return p.value === off; })) list.push({ value: off, note: "f_official" });
    list.sort(function (a, b) { return a.value - b.value; });
    list.forEach(function (p) {
      var note = (off && p.value === off) ? t("f_official") : t(p.note);
      html += '<option value="' + p.value + '">' + (p.value % 1 === 0 ? p.value.toFixed(2) : p.value) + " (" + esc(note) + ")</option>";
    });
    html += '<option value="custom">' + esc(t("opt_custom")) + "</option>";
    sel.innerHTML = html;
    sel.value = cur || String(off || CONFIG.defaultFactor);
    if (!sel.value) sel.value = String(CONFIG.defaultFactor);
    toggleCustom();
  }
  function buildMonthOptions() {
    ["effFrom", "payMonth"].forEach(function (id) {
      var sel = $(id); if (!sel) return;
      var cur = sel.value, html = "";
      var s = CONFIG.monthRangeStart.split("-").map(Number), e = CONFIG.monthRangeEnd.split("-").map(Number);
      for (var y = s[0], m = s[1]; y < e[0] || (y === e[0] && m <= e[1]); m++) {
        if (m > 12) { m = 1; y++; if (y > e[0]) break; }
        var ym = y + "-" + (m < 10 ? "0" + m : m);
        html += '<option value="' + ym + '">' + ymLabel(ym, lang) + "</option>";
      }
      sel.innerHTML = html;
      sel.value = cur || (id === "effFrom" ? CONFIG.effectiveFrom : CONFIG.defaultPaymentMonth);
    });
  }
  function toggleCustom() {
    var sel = $("factor"), wrap = $("customWrap"); if (!sel || !wrap) return;
    wrap.hidden = sel.value !== "custom";
  }

  function readForm() {
    var f = $("factor").value === "custom" ? $("customFactor").value : $("factor").value;
    return {
      basic: $("basic").value, type: $("ptype").value, age: $("age").value,
      factor: f, dr: $("dr").value === "" ? CONFIG.currentDR : $("dr").value,
      effFrom: $("effFrom").value, payMonth: $("payMonth").value
    };
  }

  function validate(inp) {
    var b = Number(inp.basic), f = Number(inp.factor);
    if (!(b >= 1000 && b <= 250000)) return "err_basic";
    if (!(f >= 1 && f <= 6)) return "err_factor";
    return null;
  }

  function onCalc(ev) {
    if (ev) ev.preventDefault();
    var inp = readForm();
    var err = validate(inp), box = $("formError");
    if (err) { box.textContent = t(err); box.hidden = false; $("results").hidden = true; return; }
    box.hidden = true;
    lastResult = calcPension(inp);
    render(lastResult);
    updateURL(inp);
    if (ev) $("results").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function row(label, val, cls) { return "<tr" + (cls ? ' class="' + cls + '"' : "") + "><th scope=\"row\">" + esc(label) + "</th><td>" + val + "</td></tr>"; }

  function render(r) {
    var R = $("results"); if (!R) return;
    var c = r.current, n = r.revised, I = r.input, F = formatINR;
    var addLabel = t("r_add") + " (" + r.addPct + "%)";
    var html = '<div class="res-head"><h2 data-i18n="res_title">' + esc(t("res_title")) + '</h2><span class="badge">' + esc(t("badge_est")) + "</span></div>";
    r.warnings.forEach(function (w) { html += '<p class="warn">' + esc(t(w)) + "</p>"; });
    html += '<div class="big"><div><span>' + esc(t("r_total")) + " (8th CPC)</span><strong>" + F(n.total) + "</strong></div>" +
            "<div><span>" + esc(t("r_inc")) + "</span><strong>" + F(r.increase) + ' <small>' + fmtPct(r.increasePct) + "</small></strong></div>" +
            "<div><span>" + esc(t("r_arrears")) + "</span><strong>" + F(r.arrears) + " <small>" + r.months + " " + esc(t("r_months")) + "</small></strong></div></div>";
    html += '<div class="two"><table class="kv"><caption>' + esc(t("sec_current")) + "</caption>" +
      row(t("r_basic"), F(c.basic)) + row(addLabel, F(c.add)) + row(t("r_dr") + " (" + I.dr + "%)", F(c.dr)) + row(t("r_total"), F(c.total), "tot") + "</table>";
    html += '<table class="kv"><caption>' + esc(t("sec_new")) + " · ×" + I.factor + "</caption>" +
      row(t("r_newbasic"), F(n.basic)) + row(addLabel, F(n.add)) + row(t("r_newdr") + " (" + CONFIG.newDRPercent + "%)", F(n.dr)) + row(t("r_total"), F(n.total), "tot") + "</table></div>";
    // steps
    var o = { basic: F(c.basic), pct: r.addPct, add: F(c.add), dr: I.dr, drAmt: F(c.dr), total: F(c.total), factor: I.factor,
      raw: F(r.rawNewBasic), min: F(r.limits.newMin), max: F(r.limits.newMax), nb: F(n.basic), nadd: F(n.add), ndr: CONFIG.newDRPercent,
      ntotal: F(n.total), inc: F(r.increase), incpct: fmtPct(r.increasePct), months: r.months,
      from: ymLabel(I.effFrom, lang), to: ymLabel(I.payMonth, lang), arr: F(r.arrears) };
    html += '<details class="steps" open><summary>' + esc(t("steps_title")) + "</summary><ol>";
    if (r.addPct > 0) html += "<li>" + esc(fill(t("s1"), o)) + "</li>";
    html += "<li>" + esc(fill(t("s2"), o)) + "</li><li>" + esc(fill(t("s3"), o)) + "</li><li>" + esc(fill(t("s4"), o));
    if (r.floorApplied) html += " → " + esc(fill(t("s4floor"), o));
    if (r.capApplied) html += " → " + esc(fill(t("s4cap"), o));
    html += "</li>";
    if (r.addPct > 0) html += "<li>" + esc(fill(t("s5"), o)) + "</li>";
    html += "<li>" + esc(fill(t("s6"), o)) + "</li><li>" + esc(fill(t("s7"), o)) + "</li><li>" + esc(fill(t("s8"), o)) + "</li></ol></details>";
    // comparison
    var list = CONFIG.presetFactors.map(function (p) { return p.value; });
    if (CONFIG.officialFitmentFactor && list.indexOf(CONFIG.officialFitmentFactor) < 0) list.push(CONFIG.officialFitmentFactor);
    if (list.indexOf(Number(I.factor)) < 0) list.push(Number(I.factor));
    list.sort(function (a, b) { return a - b; });
    html += '<div class="tbl-wrap"><table class="cmp"><caption>' + esc(t("cmp_title")) + "</caption><thead><tr><th scope=\"col\">" + esc(t("cmp_factor")) +
      "</th><th scope=\"col\">" + esc(t("cmp_newbasic")) + "</th><th scope=\"col\">" + esc(t("cmp_newtotal")) + "</th><th scope=\"col\">" + esc(t("cmp_inc")) + "</th></tr></thead><tbody>";
    list.forEach(function (f) {
      var x = calcPension({ basic: I.usedBasic, type: I.type, age: I.age, factor: f, dr: I.dr, effFrom: I.effFrom, payMonth: I.payMonth });
      var cls = f === Number(I.factor) ? ' class="sel"' : "";
      var tag = CONFIG.officialFitmentFactor === f ? " ★" : "";
      html += "<tr" + cls + "><td>" + f + tag + "</td><td>" + F(x.revised.basic) + "</td><td>" + F(x.revised.total) + "</td><td>" + F(x.increase) + " (" + fmtPct(x.increasePct) + ")</td></tr>";
    });
    html += "</tbody></table></div>";
    html += '<details class="assume"><summary>' + esc(t("assume_title")) + "</summary><ul><li>" + esc(t("a1")) + "</li><li>" + esc(t("a2")) +
      "</li><li>" + esc(t("a3")) + "</li><li>" + esc(t("a4")) + "</li><li>" + esc(t("a5")) + "</li></ul></details>";
    html += '<div class="actions no-print"><button type="button" id="btnShare" class="btn sec">' + esc(t("btn_share")) + '</button>' +
      '<a id="btnWa" class="btn wa" target="_blank" rel="noopener" href="#">' + esc(t("btn_wa")) + "</a>" +
      '<button type="button" id="btnPrint" class="btn sec">' + esc(t("btn_print")) + '</button>' +
      '<button type="button" id="btnDl" class="btn sec">' + esc(t("btn_dl")) + '</button><span id="copyMsg" class="copymsg" role="status" aria-live="polite"></span></div>';
    html += '<p class="fine">' + esc(t("est_banner")) + " " + esc(t("footer_disc")) + "</p>" + trustLinks();
    R.innerHTML = html;
    R.hidden = false;
    $("btnShare").addEventListener("click", copyLink);
    $("btnPrint").addEventListener("click", function () { window.print(); });
    $("btnDl").addEventListener("click", download);
    $("btnWa").href = "https://wa.me/?text=" + encodeURIComponent(shareText(r) + "\n" + shareURL());
  }

  function shareText(r) {
    var F = formatINR;
    return t("wa_msg") + "\n" + t("r_basic") + ": " + F(r.current.basic) + " → " + F(r.revised.basic) + " (×" + r.input.factor + ")\n" +
      t("r_total") + ": " + F(r.current.total) + " → " + F(r.revised.total) + " (" + fmtPct(r.increasePct) + ")\n" +
      t("r_arrears") + ": " + F(r.arrears);
  }
  function paramsFrom(inp) {
    var p = new URLSearchParams();
    p.set("bp", Math.round(Number(inp.basic))); p.set("type", inp.type);
    if (Number(inp.age)) p.set("age", inp.age);
    p.set("ff", inp.factor); p.set("dr", inp.dr); p.set("from", inp.effFrom); p.set("pay", inp.payMonth);
    return p;
  }
  function shareURL() { return location.origin + location.pathname + "?" + paramsFrom(readForm()).toString(); }
  function updateURL(inp) { try { history.replaceState(null, "", location.pathname + "?" + paramsFrom(inp).toString()); } catch (e) {} }
  function copyLink() {
    var url = shareURL(), msg = $("copyMsg");
    function done() { msg.textContent = t("copied"); setTimeout(function () { msg.textContent = ""; }, 2500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { prompt("", url); });
    else { prompt("", url); }
  }
  function download() {
    var r = lastResult; if (!r) return;
    var F = formatINR, L = [];
    L.push("8th Pay Commission Pension — " + t("badge_est"));
    L.push(t("updated") + " " + CONFIG.lastUpdated);
    L.push("");
    L.push(t("sec_current")); L.push("  " + t("r_basic") + ": " + F(r.current.basic)); L.push("  " + t("r_add") + " (" + r.addPct + "%): " + F(r.current.add));
    L.push("  " + t("r_dr") + " (" + r.input.dr + "%): " + F(r.current.dr)); L.push("  " + t("r_total") + ": " + F(r.current.total)); L.push("");
    L.push(t("sec_new") + " ×" + r.input.factor); L.push("  " + t("r_newbasic") + ": " + F(r.revised.basic)); L.push("  " + t("r_add") + ": " + F(r.revised.add));
    L.push("  " + t("r_newdr") + ": " + F(r.revised.dr)); L.push("  " + t("r_total") + ": " + F(r.revised.total)); L.push("");
    L.push(t("r_inc") + ": " + F(r.increase) + " (" + fmtPct(r.increasePct) + ")");
    L.push(t("r_arrears") + ": " + F(r.arrears) + " (" + r.months + " " + t("r_months") + ")"); L.push("");
    L.push(t("footer_disc")); L.push(shareURL());
    var blob = new Blob([L.join("\r\n")], { type: "text/plain;charset=utf-8" });
    var a = doc.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "8th-cpc-pension-estimate.txt";
    doc.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }

  function loadFromURL() {
    var p = new URLSearchParams(location.search), any = false;
    if (p.get("bp")) { $("basic").value = p.get("bp"); any = true; }
    if (p.get("type") && /^(sup|fpn|fpe)$/.test(p.get("type"))) $("ptype").value = p.get("type");
    if (p.get("age")) $("age").value = p.get("age");
    if (p.get("dr")) $("dr").value = p.get("dr");
    if (p.get("from")) $("effFrom").value = p.get("from");
    if (p.get("pay")) $("payMonth").value = p.get("pay");
    var ff = p.get("ff");
    if (ff) {
      var sel = $("factor"), found = false;
      for (var i = 0; i < sel.options.length; i++) if (Number(sel.options[i].value) === Number(ff)) { sel.selectedIndex = i; found = true; }
      if (!found) { sel.value = "custom"; $("customFactor").value = ff; }
      toggleCustom();
    }
    return any;
  }

  /* ---- extra widgets ---- */
  function setupReverse() {
    var b = $("revBtn"); if (!b) return;
    b.addEventListener("click", function () {
      var o = Number($("revOld").value), nn = Number($("revNew").value), out = $("revOut");
      if (!(o > 0 && nn > 0)) { out.textContent = t("err_basic"); return; }
      var f = nn / o;
      out.textContent = fill(t("rev_out"), { f: f.toFixed(3), pct: fmtPct((f - 1) * 100) });
    });
  }
  function setupFamily() {
    var b = $("fpBtn"); if (!b) return;
    b.addEventListener("click", function () {
      var lp = Number($("lastPay").value), out = $("fpOut");
      if (!(lp >= 18000)) { out.textContent = t("err_basic"); return; }
      var r = familyFromLastPay(lp);
      out.innerHTML = esc(fill(t("fp_out"), { n: formatINR(r.normal), e: formatINR(r.enhanced) })) +
        ' <button type="button" class="btn sm" id="useN">' + esc(t("fp_use_n")) + '</button> <button type="button" class="btn sm" id="useE">' + esc(t("fp_use_e")) + "</button>";
      $("useN").addEventListener("click", function () { $("basic").value = r.normal; $("ptype").value = "fpn"; onCalc(); $("calc").scrollIntoView({ behavior: "smooth" }); });
      $("useE").addEventListener("click", function () { $("basic").value = r.enhanced; $("ptype").value = "fpe"; onCalc(); $("calc").scrollIntoView({ behavior: "smooth" }); });
    });
  }
  function renderChart() {
    var tb = $("chartTable"); if (!tb) return;
    var factors = (tb.getAttribute("data-factors") || "").split(",").map(Number);
    if (CONFIG.officialFitmentFactor && factors.indexOf(CONFIG.officialFitmentFactor) < 0) factors.push(CONFIG.officialFitmentFactor);
    var rows = (tb.getAttribute("data-rows") || "").split(",").map(Number);
    var h = "<caption>" + esc(t("chart_note")) + "</caption><thead><tr><th scope=\"col\">" + esc(t("r_basic")) + " (7th CPC)</th>";
    factors.forEach(function (f) { h += '<th scope="col">×' + f + (f === CONFIG.officialFitmentFactor ? " ★" : "") + "</th>"; });
    h += "</tr></thead><tbody>";
    rows.forEach(function (b) {
      h += '<tr><th scope="row">' + formatINR(b) + "</th>";
      factors.forEach(function (f) { h += "<td>" + formatINR(calcPension({ basic: b, type: "sup", age: 0, factor: f }).revised.basic) + "</td>"; });
      h += "</tr>";
    });
    tb.innerHTML = h + "</tbody>";
  }

  /* ---------------- shared helpers for the extra calculators ---------------- */
  var rerenders = [];          // called after a language switch
  function num(id) { var e = $(id); return e ? Number(e.value) : NaN; }
  function trustLinks() {
    return '<p class="fine"><a href="' + L("/how-we-calculate/") + '">' + esc(t("lnk_how")) + '</a> · <a href="' + L("/changelog/") + '">' + esc(t("lnk_changelog")) + "</a></p>";
  }
  function L(p) { return lang === "hi" ? (p === "/" ? "/hi/" : "/hi" + p) : p; }   // same page in the current language
  function calcHref(b, type, age) {
    var q = "?bp=" + b + "&type=" + (type || "sup") + (Number(age) ? "&age=" + Number(age) : "");
    return (lang === "hi" ? "/hi/" : "/") + q;
  }
  function fillMonths(sel, start, end, def) {
    if (!sel) return;
    var cur = sel.value, html = "";
    var s = start.split("-").map(Number), e = end.split("-").map(Number);
    for (var y = s[0], m = s[1]; y < e[0] || (y === e[0] && m <= e[1]); ) {
      var ym = y + "-" + (m < 10 ? "0" + m : m);
      html += '<option value="' + ym + '">' + ymLabel(ym, lang) + "</option>";
      m++; if (m > 12) { m = 1; y++; }
    }
    sel.innerHTML = html;
    sel.value = cur || def;
    if (!sel.value) sel.selectedIndex = 0;
  }
  function factorOptions(sel) {
    if (!sel) return;
    var cur = sel.value, list = CONFIG.presetFactors.slice(), off = CONFIG.officialFitmentFactor, html = "";
    if (off && !list.some(function (p) { return p.value === off; })) list.push({ value: off, note: "f_official" });
    list.sort(function (a, b) { return a.value - b.value; });
    list.forEach(function (p) {
      var note = (off && p.value === off) ? t("f_official") : t(p.note);
      html += '<option value="' + p.value + '">' + (p.value % 1 === 0 ? p.value.toFixed(2) : p.value) + " (" + esc(note) + ")</option>";
    });
    sel.innerHTML = html;
    sel.value = cur || String(off || CONFIG.defaultFactor);
  }
  function showErr(id, key) { var b = $(id); if (!b) return; if (key) { b.textContent = t(key); b.hidden = false; } else b.hidden = true; }

  /* ---------------- basic pension finder ---------------- */
  function setupFinder() {
    var btn = $("bfBtn"); if (!btn) return;
    var last = null;
    function sync() {
      var m = $("bfMode").value;
      ["credit", "ppo7", "ppo6", "lastpay"].forEach(function (k) { var w = $("bfWrap_" + k); if (w) w.hidden = k !== m; });
      $("bfCommValWrap").hidden = $("bfCommMode").value === "none";
    }
    $("bfMode").addEventListener("change", sync); $("bfCommMode").addEventListener("change", sync);
    $("bfDR").value = CONFIG.currentDR;
    sync();
    function run(scroll) {
      var mode = $("bfMode").value, type = $("bfType").value, age = num("bfAge") || 0, r;
      if (mode === "credit") {
        var c = num("bfCredit");
        var dr = $("bfDR").value === "" ? CONFIG.currentDR : num("bfDR");
        if (!(c >= 1000 && c <= 500000) || !(dr >= 0 && dr <= 200)) { showErr("bfErr", "bf_err"); $("bfOut").hidden = true; return; }
        r = basicFromCredit({ credit: c, age: age, dr: dr, commMode: $("bfCommMode").value, commValue: $("bfCommVal").value,
                              fma: $("bfFma").checked ? CONFIG.fixedMedicalAllowance : 0, other: $("bfOther").value });
        r.mode = "credit"; r.dr = dr;
      } else {
        var id = { ppo7: "bfPpo7", ppo6: "bfPpo6", lastpay: "bfLastPay" }[mode], v = num(id);
        if (!(v >= 1000 && v <= 500000)) { showErr("bfErr", "bf_err"); $("bfOut").hidden = true; return; }
        r = basicFromPPO({ mode: mode, value: v, type: type }); r.value = v;
        r.warnings = r.basic < CONFIG.minPension ? ["warn_low_basic"] : (r.basic > maxFor(type) ? ["warn_high_basic"] : []);
      }
      showErr("bfErr", null);
      r.type = type; r.age = age; last = r;
      renderFinder(r);
      if (scroll) $("bfOut").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function renderFinder(r) {
      var F = formatINR, out = $("bfOut"), h = "";
      h += '<div class="res-head"><h2>' + esc(t("bf_res")) + '</h2><span class="badge">' + esc(t("badge_est")) + "</span></div>";
      h += '<div class="big"><div><span>' + esc(t("r_basic")) + "</span><strong>" + F(r.basic) + "</strong></div></div>";
      if (r.mode === "credit") {
        if (r.exact) {
          h += '<p class="note">' + esc(fill(t("bf_exact"), { c: F(r.credit) })) + "</p>";
          if (r.matches.length > 1) h += '<p class="note">' + esc(fill(t("bf_multi"), { list: r.matches.map(F).join(", ") })) + "</p>";
        } else {
          h += '<p class="warn">' + esc(fill(t("bf_near"), { c: F(r.credit), b: F(r.basic), c2: F(r.parts.credit), d: (r.diff > 0 ? "+" : "") + F(r.diff) })) + "</p>";
        }
        var P = r.parts;
        h += '<table class="kv"><caption>' + esc(t("bf_tbl")) + "</caption>" + row(t("r_basic"), F(P.basic));
        if (P.addPct) h += row(t("r_add") + " (" + P.addPct + "%)", F(P.add));
        h += row(t("r_dr") + " (" + r.dr + "%)", F(P.dr));
        if (P.comm) h += row(t("bf_r_comm"), "−" + F(P.comm));
        if (P.fma) h += row(t("bf_r_fma"), "+" + F(P.fma));
        if (P.other) h += row(t("bf_r_other"), "−" + F(P.other));
        h += row(t("bf_r_credit"), F(P.credit), "tot") + "</table>";
      } else {
        var note = r.mode === "ppo7" ? t("bf_ppo7_note")
          : r.mode === "ppo6" ? fill(t("bf_ppo6_note"), { pre: F(r.value), raw: F(up(r.value * CONFIG.pre2016Factor)) })
          : fill(t("bf_lastpay_note"), { pct: r.pct, lp: F(r.value), raw: F(up(r.value * r.pct / 100)), min: F(CONFIG.minPension), max: F(r.max) });
        h += '<p class="note">' + esc(note) + (r.stepped ? " " + esc(t("bf_stepped")) : "") + (r.capped ? " " + esc(fill(t("bf_capped"), { max: F(r.max) })) : "") + "</p>";
      }
      r.warnings.forEach(function (w) { h += '<p class="warn">' + esc(t(w)) + "</p>"; });
      h += '<div class="actions"><a class="btn" id="bfUse" href="' + esc(calcHref(r.basic, r.type, r.age)) + '">' + esc(fill(t("bf_use"), { b: F(r.basic) })) + "</a>" +
           '<a class="btn sec" href="' + L("/da-dr-calculator/") + '?bp=' + r.basic + (r.age ? "&age=" + r.age : "") + '">' + esc(fill(t("bf_use_dr"), { b: F(r.basic) })) + "</a>";
      if (r.mode === "ppo6") h += '<a class="btn sec" href="' + L("/pre-2016-pensioners/") + '?pre=' + r.value + "&type=" + r.type + '">' + esc(t("bf_use_pre")) + "</a>";
      h += "</div>";
      h += '<p class="fine">' + esc(t("bf_disc")) + "</p>" + trustLinks();
      out.innerHTML = h; out.hidden = false;
    }
    btn.addEventListener("click", function () { run(true); });
    rerenders.push(function () { if (last) renderFinder(last); });
  }

  /* ---------------- pre-2016 pensioners ---------------- */
  function setupPre2016() {
    var btn = $("p6Btn"); if (!btn) return;
    var last = null;
    factorOptions($("p6Factor"));
    function run(scroll) {
      var pre = num("p6Pre"), np = $("p6Np").value === "" ? 0 : num("p6Np");
      if (!(pre >= 1000 && pre <= 125000) || !(np === 0 || (np >= 7000 && np <= 250000))) { showErr("p6Err", "p6_err"); $("p6Out").hidden = true; return; }
      showErr("p6Err", null);
      var type = $("p6Type").value, age = num("p6Age") || 0, f = Number($("p6Factor").value);
      var rev = pre2016Revision({ type: type, prePension: pre, notionalPay: np });
      var est = calcPension({ basic: rev.payable, type: type, age: age, factor: f, dr: CONFIG.currentDR });
      last = { rev: rev, est: est, type: type, age: age, f: f };
      renderPre(last);
      if (scroll) $("p6Out").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function renderPre(o) {
      var F = formatINR, r = o.rev, e = o.est, h = "";
      h += '<div class="res-head"><h2>' + esc(t("p6_res")) + '</h2><span class="badge">' + esc(t("badge_est")) + "</span></div>";
      h += '<table class="kv"><caption>' + esc(t("sec_current")) + "</caption>";
      h += row(fill(t("p6_mA"), { pre: F(r.pre) }), F(r.Araw) + (r.steppedA ? " → " + F(r.A) + " (" + esc(t("p6_stepped")) + ")" : ""), r.method === "A" && r.B !== null ? "sel" : "");
      h += r.B !== null ? row(fill(t("p6_mB"), { np: F(r.notionalPay), pct: r.pct }), F(r.Braw) + (r.Braw < CONFIG.minPension ? " → " + F(r.B) : ""))
                        : row(t("p6_mB_na"), "—");
      h += row(t("p6_payable") + (r.capped ? " (" + fill(t("p6_capped"), { max: F(r.max) }) + ")" : ""), F(r.payable), "tot") + "</table>";
      if (r.B !== null) h += '<p class="note">' + esc(r.method === "B" ? t("p6_note_b") : t("p6_note_a")) + "</p>";
      h += '<div class="big"><div><span>' + esc(fill(t("p6_today"), { dr: CONFIG.currentDR })) + "</span><strong>" + F(e.current.total) + "</strong></div>" +
           "<div><span>" + esc(fill(t("p6_8th"), { f: o.f })) + "</span><strong>" + F(e.revised.basic) + "</strong></div>" +
           "<div><span>" + esc(t("p6_8th_total")) + "</span><strong>" + F(e.revised.total) + " <small>" + fmtPct(e.increasePct) + "</small></strong></div></div>";
      h += '<p class="fine">' + esc(t("p6_8th_note")) + "</p>";
      h += '<div class="actions"><a class="btn" href="' + esc(calcHref(r.payable, o.type, o.age) + "&ff=" + o.f) + '">' + esc(fill(t("p6_use"), { b: F(r.payable) })) + "</a></div>";
      h += trustLinks();
      $("p6Out").innerHTML = h; $("p6Out").hidden = false;
    }
    btn.addEventListener("click", function () { run(true); });
    var q = new URLSearchParams(location.search);
    if (q.get("pre")) { $("p6Pre").value = q.get("pre"); if (/^(sup|fpn|fpe)$/.test(q.get("type") || "")) $("p6Type").value = q.get("type"); run(false); }
    rerenders.push(function () { factorOptions($("p6Factor")); if (last) renderPre(last); });
  }

  /* ---------------- DA / DR calculator ---------------- */
  function setupDR() {
    var btn = $("drBtn"); if (!btn) return;
    var last = null, D = drDefaults();
    var now = new Date(), nm = new Date(now.getFullYear(), now.getMonth() + 1, 1);
    var nextYM = nm.getFullYear() + "-" + ("0" + (nm.getMonth() + 1)).slice(-2);
    var RANGE = ["2025-07", "2027-12"];
    if (nextYM < RANGE[0]) nextYM = RANGE[0]; if (nextYM > RANGE[1]) nextYM = RANGE[1];
    $("drOld").value = D.oldDR; $("drNew").value = D.newDR;
    function months() { fillMonths($("drFrom"), RANGE[0], RANGE[1], D.effFrom); fillMonths($("drPay"), RANGE[0], RANGE[1], nextYM); }
    function hint() {
      var hEl = $("drNewHint"); if (!hEl) return;
      hEl.textContent = fill(t(D.official ? "dr_hint_new_off" : "dr_hint_new_est"), { x: D.newDR, m: ymLabel(D.effFrom, lang) });
    }
    months(); hint();
    function run(scroll) {
      var b = num("drBasic"), o = num("drOld"), n = num("drNew");
      if (!(b >= 1000 && b <= 250000) || !(o >= 0 && o <= 200) || !(n >= 0 && n <= 200)) { showErr("drErr", "dr_err"); $("drOut").hidden = true; return; }
      showErr("drErr", null);
      last = calcDR({ basic: b, age: num("drAge") || 0, oldDR: o, newDR: n, comm: $("drComm").value, effFrom: $("drFrom").value, payMonth: $("drPay").value });
      renderDR(last);
      if (scroll) $("drOut").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function renderDR(r) {
      var F = formatINR, h = "", hyp = r.newDR > CONFIG.currentDR;
      h += '<div class="res-head"><h2>' + esc(t("dr_res")) + '</h2><span class="badge' + (hyp ? "" : " ok") + '">' + esc(t(hyp ? "dr_badge_hyp" : "dr_badge_off")) + "</span></div>";
      h += '<div class="big"><div><span>' + esc(t("dr_r_inc")) + "</span><strong>" + F(r.increase) + "</strong></div>" +
           "<div><span>" + esc(t("dr_r_arr")) + "</span><strong>" + F(r.arrears) + " <small>" + r.months + " " + esc(t("r_months")) + "</small></strong></div>" +
           "<div><span>" + esc(t("dr_r_gross")) + "</span><strong>" + F(r.grossNew) + "</strong></div></div>";
      h += '<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col"></th><th scope="col">' + esc(t("dr_before")) + " (" + r.oldDR + '%)</th><th scope="col">' + esc(t("dr_after")) + " (" + r.newDR + "%)</th></tr></thead><tbody>";
      h += "<tr><th scope=\"row\">" + esc(t("r_basic")) + "</th><td>" + F(r.basic) + "</td><td>" + F(r.basic) + "</td></tr>";
      if (r.addPct) h += "<tr><th scope=\"row\">" + esc(t("r_add")) + " (" + r.addPct + "%)</th><td>" + F(r.add) + "</td><td>" + F(r.add) + "</td></tr>";
      h += "<tr><th scope=\"row\">" + esc(t("r_dr")) + "</th><td>" + F(r.oldDRAmt) + "</td><td>" + F(r.newDRAmt) + "</td></tr>";
      h += "<tr><th scope=\"row\">" + esc(t("dr_r_gross")) + "</th><td>" + F(r.grossOld) + "</td><td>" + F(r.grossNew) + "</td></tr>";
      if (r.comm) h += "<tr><th scope=\"row\">" + esc(t("dr_r_net")) + "</th><td>" + F(r.netOld) + "</td><td>" + F(r.netNew) + "</td></tr>";
      h += "</tbody></table></div>";
      h += '<details class="steps" open><summary>' + esc(t("steps_title")) + "</summary><ol><li>" + esc(fill(t("dr_s1"), { b: F(r.basic), a: F(r.add) })) + "</li><li>" +
           esc(fill(t("dr_s2"), { inc: F(r.increase), m: r.months, from: ymLabel(r.effFrom, lang), to: ymLabel(r.payMonth, lang), arr: F(r.arrears) })) + "</li><li>" + esc(t("dr_s3")) + "</li></ol></details>";
      h += '<div class="actions"><a class="btn sec" href="' + esc(calcHref(r.basic, "sup", num("drAge") || 0)) + '">' + esc(fill(t("bf_use"), { b: F(r.basic) })) + "</a></div>";
      h += trustLinks();
      $("drOut").innerHTML = h; $("drOut").hidden = false;
    }
    btn.addEventListener("click", function () { run(true); });
    var q = new URLSearchParams(location.search);
    if (q.get("bp")) { $("drBasic").value = q.get("bp"); if (q.get("age")) $("drAge").value = q.get("age"); run(false); }
    rerenders.push(function () { months(); hint(); if (last) renderDR(last); });
  }

  /* ---------------- commutation & restoration ---------------- */
  function setupCommutation() {
    var btn = $("cmBtn"); if (!btn) return;
    var last = null, now = new Date(), nowYM = now.getFullYear() + "-" + ("0" + (now.getMonth() + 1)).slice(-2);
    function opts() { fillMonths($("cmStart"), "2005-01", nowYM, "2020-01"); factorOptions($("cmFit")); }
    function mode() { var a = $("cmMode").value === "amount"; $("cmPctWrap").hidden = a; $("cmAmtWrap").hidden = !a; }
    opts(); mode(); $("cmMode").addEventListener("change", mode);
    function run(scroll) {
      var b = num("cmBasic"), m = $("cmMode").value, pc = num("cmPct"), am = num("cmAmt");
      var ok = b >= 1000 && b <= 250000 && (m === "amount" ? (am >= 1 && am <= Math.ceil(b * 0.4)) : (pc >= 1 && pc <= 40));
      if (!ok) { showErr("cmErr", "cm_err"); $("cmOut").hidden = true; return; }
      showErr("cmErr", null);
      last = calcCommutation({ basic: b, mode: m, pct: pc, amount: am, cvFactor: $("cmCvf").value, start: $("cmStart").value,
        nowYM: nowYM, age: num("cmAge") || 0, dr: CONFIG.currentDR, fitment: Number($("cmFit").value) || CONFIG.defaultFactor });
      render(last);
      if (scroll) $("cmOut").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    function render(r) {
      var F = formatINR, h = "";
      h += '<div class="res-head"><h2>' + esc(t("cm_res")) + '</h2><span class="badge">' + esc(t("cm_badge")) + "</span></div>";
      h += '<div class="big"><div><span>' + esc(t("cm_r_ded")) + "</span><strong>" + F(r.restored ? 0 : r.commuted) + "</strong></div>" +
           "<div><span>" + esc(t("cm_r_restore")) + "</span><strong>" + esc(ymLabel(r.restoreYM, lang)) + " <small>" +
           esc(r.restored ? t("cm_r_restored") : fill(t("cm_r_left"), { m: r.monthsLeft })) + "</small></strong></div>" +
           "<div><span>" + esc(t("cm_r_cvp")) + "</span><strong>" + F(r.cvp) + "</strong></div></div>";
      h += '<div class="tbl-wrap"><table class="data"><thead><tr><th scope="col"></th><th scope="col">' + esc(t("cm_col_now")) + '</th><th scope="col">' + esc(t("cm_col_after")) + "</th></tr></thead><tbody>";
      h += '<tr><th scope="row">' + esc(t("cm_r_credit")) + "</th><td>" + F(r.creditNow) + "</td><td>" + F(r.creditAfter) + "</td></tr>";
      h += '<tr><th scope="row">' + esc(fill(t("cm_r_8cpc"), { f: r.fitment })) + "</th><td>" + F(r.newCredit) + "</td><td>" + F(r.newCreditAfter) + "</td></tr>";
      h += '<tr><th scope="row">' + esc(t("cm_r_total")) + "</th><td colspan=\"2\">" + F(r.totalDeducted) + "</td></tr>";
      h += "</tbody></table></div>";
      h += '<details class="steps" open><summary>' + esc(t("steps_title")) + "</summary><ol>" +
           "<li>" + esc(fill(t("cm_s1"), { b: F(r.basic), p: r.pct.toFixed(1), c: F(r.commuted) })) + "</li>" +
           "<li>" + esc(fill(t("cm_s2"), { c: F(r.commuted), f: r.cvFactor, v: F(r.cvp) })) + "</li>" +
           "<li>" + esc(fill(t("cm_s3"), { b: F(r.basic) })) + "</li>" +
           "<li>" + esc(fill(t("cm_s4"), { s: ymLabel(r.start, lang), r: ymLabel(r.restoreYM, lang) })) + "</li>" +
           "<li>" + esc(t("cm_s5")) + "</li></ol></details>";
      h += '<div class="actions"><a class="btn sec" href="' + esc(calcHref(r.basic, "sup", num("cmAge") || 0)) + '">' + esc(fill(t("bf_use"), { b: F(r.basic) })) + "</a></div>";
      h += trustLinks();
      $("cmOut").innerHTML = h; $("cmOut").hidden = false;
    }
    btn.addEventListener("click", function () { run(true); });
    rerenders.push(function () { opts(); if (last) render(last); });
    var q = new URLSearchParams(location.search);
    if (q.get("bp")) { $("cmBasic").value = q.get("bp"); if (q.get("age")) $("cmAge").value = q.get("age"); run(false); }
  }

  function init() {
    // Every page now exists in English and Hindi, so the page language decides the UI language.
    // Old share links with ?lang=xx are sent to the counterpart page (rel=alternate hreflang).
    var qs = new URLSearchParams(location.search), qp = qs.get("lang");
    var pageLang = doc.documentElement.getAttribute("lang") === "hi" ? "hi" : "en";
    lang = pageLang;
    if (qp && qp !== pageLang) {
      var alt = doc.querySelector('link[rel="alternate"][hreflang="' + (qp === "hi" ? "hi-IN" : "en-IN") + '"]');
      if (alt) { qs.delete("lang"); var rest = qs.toString(); try { location.replace(alt.getAttribute("href") + (rest ? "?" + rest : "")); return; } catch (e) {} }
    }
    // menu
    var mb = $("menuBtn");
    if (mb) mb.addEventListener("click", function () { var nav = $("mainNav"); var open = nav.classList.toggle("open"); mb.setAttribute("aria-expanded", open ? "true" : "false"); });
    var lb = $("langBtn"); if (lb) lb.addEventListener("click", function () { applyLang(lang === "en" ? "hi" : "en"); });
    var ll = $("langLink"); if (ll) ll.addEventListener("click", function () { try { localStorage.setItem("uiLang", lang === "en" ? "hi" : "en"); } catch (e) {} });
    var up1 = doc.querySelectorAll("[data-cfg='lastUpdated']"); for (var i = 0; i < up1.length; i++) up1[i].textContent = CONFIG.lastUpdated;
    var form = $("calcForm");
    if (form) {
      $("dr").value = CONFIG.currentDR;
      var dt = form.getAttribute("data-default-type"); if (dt) $("ptype").value = dt;
      applyLang(lang);
      $("factor").addEventListener("change", toggleCustom);
      form.addEventListener("submit", onCalc);
      form.addEventListener("reset", function () {
        setTimeout(function () { $("dr").value = CONFIG.currentDR; if (dt) $("ptype").value = dt; buildFactorOptions(); $("factor").value = String(CONFIG.officialFitmentFactor || CONFIG.defaultFactor); toggleCustom();
          $("effFrom").value = CONFIG.effectiveFrom; $("payMonth").value = CONFIG.defaultPaymentMonth; $("results").hidden = true; lastResult = null;
          try { history.replaceState(null, "", location.pathname); } catch (e) {} }, 0);
      });
      if (CONFIG.officialFitmentFactor) {
        var ob = $("officialBanner");
        if (ob) { ob.hidden = false; ob.textContent = t("official_banner") + " " + CONFIG.officialFitmentFactor + " ";
          if (CONFIG.officialNoticeUrl) { var oa = doc.createElement("a"); oa.href = CONFIG.officialNoticeUrl; oa.rel = "noopener"; oa.textContent = "↗"; ob.appendChild(oa); } }
      }
      if (loadFromURL()) onCalc();
    } else { applyLang(lang); }
    setupReverse(); setupFamily(); setupFinder(); setupPre2016(); setupDR(); setupCommutation();
  }
  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init); else init();
})();
