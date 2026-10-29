# Extra depth for the shorter guides, EN + HI with identical facts (28 Oct 2026). Executed inside tools/build.py.

_AGE = [(80, 20), (85, 30), (90, 40), (95, 50), (100, 100)]
_age_rows = []
for _a, _pc in _AGE:
    _ad = up(Decimal(9000) * _pc / 100); _d = up(Decimal(9000 + _ad) * 60 / 100)
    _nb = ceil_mul(9000, "2.57"); _na = up(Decimal(_nb) * _pc / 100)
    _age_rows.append([str(_a), f"{_pc}%", inr(9000 + _ad + _d), inr(_nb + _na)])

extend("/minimum-pension-8th-pay-commission/", body=f"""
<h2>Minimum pensioners aged 80 and above</h2>
<p>Additional pension is paid on top of the ₹9,000 minimum, so very old pensioners on the minimum receive more than ₹14,400 today, and the additional pension would rise with any new minimum. The table assumes DR at 60% today and a new minimum of ₹9,000 × 2.57 with DR restarting at zero — an estimate only.</p>
{ex_table("en", _age_rows, ["Age", "Additional pension", "Total today (₹9,000 + additional + 60% DR)", "Estimated at ×2.57 (basic + additional, DR 0%)"])}
<p>For a 100-year-old pensioner on the minimum, additional pension doubles the basic: ₹9,000 + ₹9,000 + 60% DR = ₹28,800 today. At 2.57 the estimate is ₹46,260 before any new DR.</p>
<h2>How to check whether you are on the minimum</h2>
<ul>
<li>Look at the basic pension on your PPO or pension slip. If it is exactly ₹9,000, you are on the minimum.</li>
<li>If you only know the bank credit, use the <a href="/basic-pension-finder/">basic pension finder</a>: ₹14,400 for a pensioner below 80 with no deductions points to ₹9,000 basic.</li>
<li>Family pensioners: if 30% of the employee's last pay was less than ₹9,000, the minimum applies.</li>
</ul>
""")
extend("/hi/minimum-pension-8th-pay-commission/", body=f"""
<h2>80 साल और उससे ज़्यादा उम्र के न्यूनतम पेंशनभोगी</h2>
<p>अतिरिक्त पेंशन ₹9,000 की न्यूनतम सीमा के ऊपर मिलती है, इसलिए बहुत बुज़ुर्ग न्यूनतम पेंशनभोगियों को आज ₹14,400 से ज़्यादा मिलता है, और कोई भी नई न्यूनतम सीमा आने पर अतिरिक्त पेंशन भी बढ़ेगी। तालिका में आज 60% DR और नई न्यूनतम ₹9,000 × 2.57 मानी गई है, DR शून्य से शुरू — केवल अनुमान।</p>
{ex_table("hi", _age_rows, ["उम्र", "अतिरिक्त पेंशन", "आज कुल (₹9,000 + अतिरिक्त + 60% DR)", "×2.57 पर अनुमान (मूल + अतिरिक्त, DR 0%)"])}
<p>100 साल के न्यूनतम पेंशनभोगी के लिए अतिरिक्त पेंशन मूल पेंशन को दोगुना कर देती है: ₹9,000 + ₹9,000 + 60% DR = आज ₹28,800। 2.57 पर अनुमान ₹46,260 है, किसी नई DR से पहले।</p>
<h2>कैसे जाँचें कि आपको न्यूनतम पेंशन मिल रही है</h2>
<ul>
<li>PPO या पेंशन स्लिप में मूल पेंशन देखें। अगर ठीक ₹9,000 है, तो आप न्यूनतम पर हैं।</li>
<li>अगर सिर्फ़ बैंक की रकम पता है, तो <a href="/hi/basic-pension-finder/">मूल पेंशन पता करें</a> इस्तेमाल करें: 80 से कम उम्र और बिना कटौती के ₹14,400 का मतलब ₹9,000 मूल पेंशन है।</li>
<li>पारिवारिक पेंशनभोगी: अगर कर्मचारी के अंतिम वेतन का 30% ₹9,000 से कम था, तो न्यूनतम सीमा लागू है।</li>
</ul>
""")

extend("/life-certificate/", body="""
<h2>Face authentication, step by step</h2>
<ol>
<li>From the Google Play Store, install UIDAI's <strong>Aadhaar Face RD</strong> app. It runs in the background and must be installed first.</li>
<li>Install the <strong>Jeevan Pramaan</strong> app and open "Operator Authentication". Enter the operator's Aadhaar number, mobile number and email, then the OTP. The operator can be the pensioner or a family member, and this is a one-time step.</li>
<li>Enter the name as on Aadhaar, tick the consent box and tap Scan. Allow the camera, read the instructions and capture the operator's face.</li>
<li>On the "Pensioner Authentication" screen, fill in the pensioner's name as on Aadhaar, type of pension, sanctioning authority, disbursing agency, PPO number and pension account number.</li>
<li>Scan the pensioner's face. When it succeeds, the screen shows the Pramaan ID and PPO number, and an SMS follows. One phone can be used to generate certificates for many pensioners.</li>
</ol>
<h2>A checklist before you start</h2>
<ul>
<li>Is Aadhaar linked to the pension account at the bank or post office? If not, ask the branch to seed it first.</li>
<li>Keep the PPO number and pension account number handy.</li>
<li>Choose a well-lit room, a plain background and a steady hand; remove a mask, and wear glasses only if the Aadhaar photo has them.</li>
<li>After submitting, download the certificate with the Pramaan ID after a few days to confirm the status.</li>
</ul>
""")
extend("/hi/life-certificate/", body="""
<h2>चेहरे से प्रमाणीकरण, चरण-दर-चरण</h2>
<ol>
<li>Google Play Store से UIDAI का <strong>Aadhaar Face RD</strong> ऐप इंस्टॉल करें। यह पीछे से चलता है और पहले इंस्टॉल होना ज़रूरी है।</li>
<li><strong>जीवन प्रमाण</strong> ऐप इंस्टॉल करके "Operator Authentication" खोलें। ऑपरेटर का आधार नंबर, मोबाइल नंबर और ईमेल भरें, फिर OTP। ऑपरेटर ख़ुद पेंशनभोगी या परिवार का कोई सदस्य हो सकता है, और यह एक बार का काम है।</li>
<li>आधार के अनुसार नाम भरें, सहमति वाले बॉक्स पर निशान लगाएँ और Scan दबाएँ। कैमरे की अनुमति दें, निर्देश पढ़ें और ऑपरेटर का चेहरा स्कैन करें।</li>
<li>"Pensioner Authentication" स्क्रीन पर पेंशनभोगी का आधार वाला नाम, पेंशन का प्रकार, स्वीकृति प्राधिकारी, भुगतान एजेंसी, PPO नंबर और पेंशन खाता नंबर भरें।</li>
<li>पेंशनभोगी का चेहरा स्कैन करें। सफल होने पर स्क्रीन पर प्रमाण ID और PPO नंबर दिखते हैं, और SMS आता है। एक फ़ोन से कई पेंशनभोगियों के प्रमाण पत्र बन सकते हैं।</li>
</ol>
<h2>शुरू करने से पहले जाँच-सूची</h2>
<ul>
<li>क्या आधार बैंक या डाकघर के पेंशन खाते से जुड़ा है? नहीं तो पहले शाखा से जुड़वाएँ।</li>
<li>PPO नंबर और पेंशन खाता नंबर पास रखें।</li>
<li>अच्छी रोशनी वाला कमरा, सादा पीछे का दृश्य और स्थिर हाथ चुनें; मास्क हटाएँ, और चश्मा तभी पहनें जब आधार फ़ोटो में हो।</li>
<li>जमा करने के कुछ दिन बाद प्रमाण ID से प्रमाण पत्र डाउनलोड करके स्थिति पक्की करें।</li>
</ul>
""")

extend("/da-dr-calculator/", body="""
<h2>Worked example: a pensioner aged 85</h2>
<p>Additional pension also attracts DR, so older pensioners gain a little more from each instalment. For a basic pension of ₹20,000 at age 85, additional pension is 30% (₹6,000). DR at 60% on ₹26,000 is ₹15,600; at a hypothetical 63% it would be ₹16,380 — ₹780 more a month, or ₹3,120 for four months of arrears. The same pensioner below 80 would gain ₹600 a month. Only the 60% rate is official.</p>
""")
extend("/hi/da-dr-calculator/", body="""
<h2>उदाहरण: 85 साल के पेंशनभोगी</h2>
<p>अतिरिक्त पेंशन पर भी DR मिलती है, इसलिए बुज़ुर्ग पेंशनभोगियों को हर किस्त से थोड़ा ज़्यादा लाभ होता है। 85 साल की उम्र में ₹20,000 मूल पेंशन पर अतिरिक्त पेंशन 30% (₹6,000) है। ₹26,000 पर 60% DR = ₹15,600; काल्पनिक 63% पर ₹16,380 — हर महीने ₹780 ज़्यादा, यानी चार महीने का एरियर ₹3,120। यही पेंशनभोगी 80 से कम उम्र के होते तो ₹600 महीना ज़्यादा पाते। आधिकारिक केवल 60% दर है।</p>
""")
