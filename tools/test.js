// Run: node tools/test.js
const A = require("../assets/app.js");
const assert = require("assert");
const cases = [
  { name: "9000 @2.57 superannuation, age 70", in: { basic: 9000, type: "sup", age: 70, factor: 2.57 } },
  { name: "20000 @2.86, age 65", in: { basic: 20000, type: "sup", age: 65, factor: 2.86 } },
  { name: "20000 @2.86, age 82 (20% additional)", in: { basic: 20000, type: "sup", age: 82, factor: 2.86 } },
  { name: "15000 family normal @1.92, age 87 (30%)", in: { basic: 15000, type: "fpn", age: 87, factor: 1.92 } },
  { name: "45000 family enhanced @3.833, age 60", in: { basic: 45000, type: "fpe", age: 60, factor: 3.833 } },
  { name: "125000 max @3.0, age 101 (100%)", in: { basic: 125000, type: "sup", age: 101, factor: 3.0 } },
  { name: "8000 below min @2.57", in: { basic: 8000, type: "sup", age: 70, factor: 2.57 } },
  { name: "90000 family normal (above 75000 cap) @2.57", in: { basic: 90000, type: "fpn", age: 70, factor: 2.57 } }
];
const F = A.formatINR;
for (const c of cases) {
  const r = A.calcPension(c.in);
  console.log(`\n${c.name}`);
  console.log(`  current: basic ${F(r.current.basic)} + add ${F(r.current.add)} (${r.addPct}%) + DR ${F(r.current.dr)} = ${F(r.current.total)}`);
  console.log(`  8th CPC: basic ${F(r.revised.basic)} + add ${F(r.revised.add)} + DR ${F(r.revised.dr)} = ${F(r.revised.total)}${r.floorApplied ? " [min floor]" : ""}${r.capApplied ? " [cap]" : ""}`);
  console.log(`  increase ${F(r.increase)} (${r.increasePct.toFixed(2)}%), arrears ${F(r.arrears)} over ${r.months} months; warnings: ${r.warnings.join(",") || "none"}`);
}
// assertions
let r = A.calcPension({ basic: 9000, type: "sup", age: 70, factor: 2.57 });
assert.strictEqual(r.revised.basic, 23130); assert.strictEqual(r.current.total, 14400); assert.strictEqual(r.months, 21);
assert.strictEqual(r.arrears, (23130 - 14400) * 21);
r = A.calcPension({ basic: 20000, type: "sup", age: 65, factor: 2.86 });
assert.strictEqual(r.revised.basic, 57200); assert.strictEqual(r.current.total, 32000);
r = A.calcPension({ basic: 20000, type: "sup", age: 82, factor: 2.86 });
assert.strictEqual(r.current.add, 4000); assert.strictEqual(r.current.dr, 14400); assert.strictEqual(r.current.total, 38400);
assert.strictEqual(r.revised.add, 11440); assert.strictEqual(r.revised.total, 68640);
assert.strictEqual(A.additionalPct(79), 0); assert.strictEqual(A.additionalPct(80), 20); assert.strictEqual(A.additionalPct(85), 30);
assert.strictEqual(A.additionalPct(90), 40); assert.strictEqual(A.additionalPct(95), 50); assert.strictEqual(A.additionalPct(100), 100);
assert.strictEqual(F(123456), "₹1,23,456"); assert.strictEqual(F(12345678), "₹1,23,45,678"); assert.strictEqual(F(999), "₹999"); assert.strictEqual(F(-8730), "-₹8,730");
r = A.calcPension({ basic: 8000, type: "sup", age: 70, factor: 2.57 });
assert.strictEqual(r.revised.basic, 23130); assert.ok(r.floorApplied);
r = A.calcPension({ basic: 90000, type: "fpn", age: 70, factor: 2.57 });
assert.strictEqual(r.current.basic, 75000); assert.ok(r.warnings.includes("warn_max"));
const fp = A.familyFromLastPay(50000); assert.deepStrictEqual(fp, { normal: 15000, enhanced: 25000 });
const fp2 = A.familyFromLastPay(20000); assert.strictEqual(fp2.normal, 9000);
// float edge cases: every preset × a range of basics must equal ceil of exact decimal product
for (const p of A.CONFIG.presetFactors) for (let b = 9000; b <= 125000; b += 500) {
  const exact = Math.ceil((b * Math.round(p.value * 1000)) / 1000 - 1e-9);
  assert.strictEqual(A.calcPension({ basic: b, type: "sup", age: 0, factor: p.value }).revised.basic, exact, `${b}x${p.value}`);
}
// i18n key parity
const en = Object.keys(A.I18N.en), hi = Object.keys(A.I18N.hi);
assert.deepStrictEqual(en.filter(k => !hi.includes(k)), []); assert.deepStrictEqual(hi.filter(k => !en.includes(k)), []);

/* ===== new calculators (28 Oct 2026) ===== */
// --- pre-2016: DoPPW OM 12.05.2017 Annexure I, all four cases (pension) + family cases
const OM = [ // [pre-revised pension, notional pay 1.1.2016, A (x2.57), B (50%), payable]
  [4191, 23100, 10771, 11550, 11550], [12600, 71800, 32382, 35900, 35900],
  [5424, 29600, 13940, 14800, 14800], [39500, 205100, 101515, 102550, 102550]];
for (const [pre, np, a, b, pay] of OM) {
  const r = A.pre2016Revision({ type: "sup", prePension: pre, notionalPay: np });
  assert.strictEqual(r.A, a, `A ${pre}`); assert.strictEqual(r.B, b, `B ${np}`); assert.strictEqual(r.payable, pay); assert.strictEqual(r.method, "B");
}
// family pension (normal 30%): OM rows 5/8/14/17
const FP = [[3500, 23100, 9000, 9000], [7560, 71800, 19430, 21540], [3500, 29600, 9000, 9000], [23700, 205100, 60909, 61530]];
for (const [pre, np, a, pay] of FP) {
  const r = A.pre2016Revision({ type: "fpn", prePension: pre, notionalPay: np });
  assert.strictEqual(r.A, a, `FP A ${pre}`); assert.strictEqual(r.payable, pay, `FP pay ${pre}`);
}
// enhanced family pension, case 4: 39500 -> A 101515, B 50% of 205100 = 102550
let p6 = A.pre2016Revision({ type: "fpe", prePension: 39500, notionalPay: 205100 });
assert.strictEqual(p6.A, 101515); assert.strictEqual(p6.payable, 102550);
// OM 04.08.2016 illustrations: 39500 -> 101515, 12600 -> 32382 (multiplier only, no notional pay)
assert.strictEqual(A.pre2016Revision({ type: "sup", prePension: 39500 }).payable, 101515);
assert.strictEqual(A.pre2016Revision({ type: "sup", prePension: 12600 }).payable, 32382);
assert.strictEqual(A.pre2016Revision({ type: "sup", prePension: 12600 }).B, null);
// cap: family normal capped at 75000
assert.strictEqual(A.pre2016Revision({ type: "fpn", prePension: 40000 }).payable, 75000);
console.log("\npre-2016: all OM 12.05.2017 Annexure-I examples reproduced");

// --- basic pension finder
let bf = A.basicFromCredit({ credit: 25000, age: 70, dr: 60, commMode: "amount", commValue: 8000, fma: 1000, other: 0 });
assert.strictEqual(bf.basic, 20000); assert.ok(bf.exact);
bf = A.basicFromCredit({ credit: 28800, age: 82, dr: 60, commMode: "none" });
assert.strictEqual(bf.basic, 15000); assert.ok(bf.exact); assert.strictEqual(bf.parts.add, 3000);
bf = A.basicFromCredit({ credit: 14400, age: 65, dr: 60, commMode: "none" });
assert.strictEqual(bf.basic, 9000);
bf = A.basicFromCredit({ credit: 25000, age: 70, dr: 60, commMode: "pct", commValue: 40, fma: 1000 });
assert.strictEqual(bf.basic, 20000);
// round-trip: credit(basic) -> basic for many values, ages, DRs, commutation
let rt = 0;
for (let b = 9000; b <= 125000; b += 777) for (const age of [65, 80, 86, 91, 96, 100]) for (const dr of [58, 60, 63]) {
  const c = A.creditFromBasic({ basic: b, age, dr, commMode: "amount", commValue: Math.round(b * 0.4), fma: 1000, other: 150 }).credit;
  const back = A.basicFromCredit({ credit: c, age, dr, commMode: "amount", commValue: Math.round(b * 0.4), fma: 1000, other: 150 });
  assert.ok(back.exact, `exact ${b}/${age}/${dr}`); assert.ok(back.matches.includes(b), `rt ${b}/${age}/${dr}`); rt++;
}
// a credit with no exact preimage reports nearest + diff
bf = A.basicFromCredit({ credit: 32001, age: 60, dr: 60, commMode: "none" });
assert.ok(!bf.exact); assert.strictEqual(bf.basic, 20000); assert.strictEqual(bf.diff, -1);
assert.ok(A.basicFromCredit({ credit: 8000, age: 60, dr: 60, commMode: "none" }).warnings.includes("warn_low_basic"));
// PPO modes
assert.strictEqual(A.basicFromPPO({ mode: "ppo7", value: 23130 }).basic, 23130);
assert.strictEqual(A.basicFromPPO({ mode: "ppo6", value: 12600 }).basic, 32382);
assert.strictEqual(A.basicFromPPO({ mode: "ppo6", value: 3000 }).basic, 9000);
assert.strictEqual(A.basicFromPPO({ mode: "lastpay", value: 56100, type: "sup" }).basic, 28050);
assert.strictEqual(A.basicFromPPO({ mode: "lastpay", value: 56100, type: "fpn" }).basic, 16830);
assert.strictEqual(A.basicFromPPO({ mode: "lastpay", value: 250000, type: "fpn" }).basic, 75000);
assert.strictEqual(A.basicFromPPO({ mode: "lastpay", value: 18000, type: "sup" }).basic, 9000);
console.log(`basic pension finder: ${rt} round-trips exact`);

// --- DA/DR
let d = A.calcDR({ basic: 20000, age: 70, oldDR: 60, newDR: 63, effFrom: "2026-07", payMonth: "2026-11" });
assert.strictEqual(d.oldDRAmt, 12000); assert.strictEqual(d.newDRAmt, 12600); assert.strictEqual(d.increase, 600);
assert.strictEqual(d.months, 4); assert.strictEqual(d.arrears, 2400);
d = A.calcDR({ basic: 15000, age: 82, oldDR: 60, newDR: 63, comm: 0, effFrom: "2026-07", payMonth: "2027-01" });
assert.strictEqual(d.add, 3000); assert.strictEqual(d.oldDRAmt, 10800); assert.strictEqual(d.newDRAmt, 11340); assert.strictEqual(d.arrears, 540 * 6);
d = A.calcDR({ basic: 9001, age: 60, oldDR: 60, newDR: 63, effFrom: "2026-07", payMonth: "2026-07" });
assert.strictEqual(d.oldDRAmt, 5401); assert.strictEqual(d.newDRAmt, 5671); assert.strictEqual(d.arrears, 0); // 5400.6 -> 5401; 5670.63 -> 5671
d = A.calcDR({ basic: 20000, age: 70, oldDR: 60, newDR: 63, comm: 8000, effFrom: "2026-07", payMonth: "2026-11" });
assert.strictEqual(d.netOld, 24000); assert.strictEqual(d.netNew, 24600);
// CONFIG consistency
const H = A.CONFIG.drHistory;
assert.strictEqual(H[H.length - 1].pct, A.CONFIG.currentDR, "last drHistory entry must equal currentDR");
const D = A.drDefaults();
if (A.CONFIG.drNextAssumed === null) assert.ok(D.official); else { assert.strictEqual(D.oldDR, A.CONFIG.currentDR); assert.ok(!D.official); }
// rates.json must mirror CONFIG
const fs = require("fs"), path = require("path");
const rates = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "assets", "rates.json"), "utf8"));
delete rates._note;
assert.deepStrictEqual(rates, JSON.parse(JSON.stringify(A.CONFIG)), "assets/rates.json is stale: run node tools/export-rates.js");
console.log("DA/DR: OK; rates.json in sync with CONFIG");

console.log("\nAll assertions passed. i18n keys:", en.length);
