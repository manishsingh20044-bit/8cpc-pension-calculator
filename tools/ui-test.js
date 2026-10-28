// UI smoke test in a simulated browser. Needs jsdom:  npm i --no-save jsdom  (or NODE_PATH=... )
// Run from the site root: node tools/ui-test.js
const { JSDOM, VirtualConsole } = require("jsdom");
const fs = require("fs"), path = require("path"), assert = require("assert");
const ROOT = path.join(__dirname, "..");
const appJs = fs.readFileSync(path.join(ROOT, "assets/app.js"), "utf8");
async function load(rel, query = "") {
  const vc = new VirtualConsole(), errors = [];
  vc.on("jsdomError", e => errors.push(e.message)); vc.on("error", e => errors.push(String(e)));
  const html = fs.readFileSync(path.join(ROOT, rel), "utf8").replace('<script src="/assets/app.js" defer></script>', "");
  const dom = new JSDOM(html, { url: "https://example.com/" + rel.replace(/index\.html$/, "").replace(/^404\.html$/, "404") + query,
                                runScripts: "outside-only", virtualConsole: vc, pretendToBeVisual: true });
  const w = dom.window; w.HTMLElement.prototype.scrollIntoView = function () {};
  try { w.eval(appJs); } catch (e) { errors.push("eval: " + e.message); }
  await new Promise(r => setTimeout(r, 30));
  return { w, d: w.document, errors };
}
const txt = (d, sel) => [...d.querySelectorAll(sel)].map(e => e.textContent.trim());
(async () => {
  let total = 0;
  // --- main calculator: prefill from finder link, trust links present
  let { w, d, errors } = await load("index.html", "?bp=20000&type=sup&age=70");
  assert.ok(!d.getElementById("results").hidden); assert.strictEqual(txt(d, "#results .big strong")[0], "₹51,400");
  assert.ok(d.querySelector('#results a[href="/how-we-calculate/"]') && d.querySelector('#results a[href="/changelog/"]'));
  assert.ok(d.querySelector('#calc a[href="/basic-pension-finder/"]'));
  assert.deepStrictEqual(errors, []); total++;
  console.log("index ?bp=20000 →", txt(d, "#results .big strong").join(" | "));

  // --- finder: credit mode
  ({ w, d, errors } = await load("basic-pension-finder/index.html"));
  d.getElementById("bfAge").value = "70"; d.getElementById("bfCredit").value = "25000";
  d.getElementById("bfCommMode").value = "amount"; d.getElementById("bfCommMode").dispatchEvent(new w.Event("change"));
  assert.ok(!d.getElementById("bfCommValWrap").hidden);
  d.getElementById("bfCommVal").value = "8000"; d.getElementById("bfFma").checked = true;
  d.getElementById("bfBtn").click();
  assert.strictEqual(txt(d, "#bfOut .big strong")[0], "₹20,000");
  const use = d.getElementById("bfUse").getAttribute("href");
  assert.strictEqual(use, "/?bp=20000&type=sup&age=70");
  console.log("finder credit 25000 →", txt(d, "#bfOut .big strong")[0], "| use link:", use, "|", txt(d, "#bfOut p.note")[0]);
  // Hindi toggle re-renders
  d.getElementById("langBtn").click();
  assert.strictEqual(d.querySelector("#bfOut h2").textContent, "आपकी मूल पेंशन (अनुमानित)");
  assert.strictEqual(d.getElementById("bfUse").getAttribute("href"), "/hi/?bp=20000&type=sup&age=70");
  assert.strictEqual(d.querySelector('[data-i18n="bf_btn"]').textContent, "मेरी मूल पेंशन निकालें");
  console.log("finder HI:", d.querySelector("#bfOut h2").textContent, "|", d.getElementById("bfUse").textContent);
  // ppo6 mode
  d.getElementById("langBtn").click();
  d.getElementById("bfMode").value = "ppo6"; d.getElementById("bfMode").dispatchEvent(new w.Event("change"));
  assert.ok(d.getElementById("bfWrap_credit").hidden && !d.getElementById("bfWrap_ppo6").hidden);
  d.getElementById("bfPpo6").value = "12600"; d.getElementById("bfBtn").click();
  assert.strictEqual(txt(d, "#bfOut .big strong")[0], "₹32,382");
  assert.ok(d.querySelector('#bfOut a[href^="/pre-2016-pensioners/?pre=12600"]'));
  // validation
  d.getElementById("bfPpo6").value = "5"; d.getElementById("bfBtn").click();
  assert.ok(!d.getElementById("bfErr").hidden && d.getElementById("bfOut").hidden);
  assert.deepStrictEqual(errors, []); total++;

  // --- pre-2016
  ({ w, d, errors } = await load("pre-2016-pensioners/index.html"));
  assert.ok(d.getElementById("p6Factor").options.length >= 8);
  d.getElementById("p6Pre").value = "12600"; d.getElementById("p6Np").value = "71800"; d.getElementById("p6Age").value = "86";
  d.getElementById("p6Btn").click();
  const kv = txt(d, "#p6Out table.kv td");
  assert.deepStrictEqual(kv.slice(0, 3), ["₹32,382", "₹35,900", "₹35,900"]);
  const big = txt(d, "#p6Out .big strong");
  // today: 35900 + 30% 10770 = 46670; DR 60% = 28002 → 74672. 8th @2.57: 92263; +30% 27679 → 119942
  assert.strictEqual(big[0], "₹74,672"); assert.strictEqual(big[1], "₹92,263");
  console.log("pre-2016 12600/71800 age 86 →", kv.slice(0, 3).join(" / "), "| big:", big.join(" | "));
  // prefill from URL
  ({ w, d, errors } = await load("pre-2016-pensioners/index.html", "?pre=39500&type=fpe"));
  assert.ok(!d.getElementById("p6Out").hidden); assert.strictEqual(txt(d, "#p6Out table.kv td")[2], "₹1,01,515");
  d.getElementById("langBtn").click();
  assert.strictEqual(d.querySelector("#p6Out h2").textContent, "आपकी संशोधित पेंशन: दोनों तरीके");
  assert.deepStrictEqual(errors, []); total++;

  // --- DA/DR
  ({ w, d, errors } = await load("da-dr-calculator/index.html", "?bp=20000&age=70"));
  assert.strictEqual(d.getElementById("drOld").value, "60"); assert.strictEqual(d.getElementById("drNew").value, "63");
  assert.strictEqual(d.getElementById("drFrom").value, "2026-07");
  assert.ok(/not announced/i.test(d.getElementById("drNewHint").textContent));
  d.getElementById("drPay").value = "2026-11"; d.getElementById("drBtn").click();
  const drBig = txt(d, "#drOut .big strong");
  assert.strictEqual(drBig[0], "₹600"); assert.ok(drBig[1].startsWith("₹2,400"));
  assert.ok(d.querySelector("#drOut .badge").textContent.includes("not announced"));
  console.log("DR 20000 60→63 Jul–Oct →", drBig.join(" | "), "| badge:", d.querySelector("#drOut .badge").textContent);
  d.getElementById("langBtn").click();
  assert.strictEqual(d.querySelector("#drOut h2").textContent, "आपकी महंगाई राहत (DR)");
  assert.ok(d.getElementById("drFrom").selectedOptions[0].textContent.includes("जुलाई"));
  assert.deepStrictEqual(errors, []); total++;

  // --- every page loads without JS errors, has nav + footer trust links
  const pages = fs.readFileSync(path.join(ROOT, "sitemap.xml"), "utf8").match(/<loc>[^<]+<\/loc>/g)
    .map(l => l.replace(/<\/?loc>/g, "").replace(/^https?:\/\/[^/]+\//, "")).map(p => (p ? p : "") + "index.html");
  pages.push("404.html");
  for (const p of pages) {
    const r = await load(p);
    assert.deepStrictEqual(r.errors, [], p);
    assert.ok(r.d.querySelector('footer a[href="/how-we-calculate/"]') && r.d.querySelector('footer a[href="/changelog/"]'), p + " footer");
    r.d.getElementById("langBtn").click();   // language switch must not throw
    assert.deepStrictEqual(r.errors, [], p + " after lang switch");
    total++;
  }
  console.log(`\nUI tests passed (${total} checks, ${pages.length} pages loaded with no JS errors).`);
})().catch(e => { console.error("UI TEST FAILED:", e.message); process.exit(1); });
