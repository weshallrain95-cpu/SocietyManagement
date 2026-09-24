// Only Broker — founder presentation deck (pptxgenjs). Run: node build.js
const pptxgen = require('pptxgenjs');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const sharp = require('sharp');
const fa = require('react-icons/fa6');

const TEAL = '0E3B43', INK = '15201F', MUTED = '5B6866', LIGHT = 'F4F6F5', WHITE = 'FFFFFF', MINT = 'DCEBE8', SAFF = 'E8A33D', OK = '1E7A46';
const HEAD = 'Cambria', BODY = 'Calibri';
const IMG = __dirname + '/img/';

async function icon(Comp, color) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: '#' + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return 'image/png;base64,' + buf.toString('base64');
}

(async () => {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9'; // 10 x 5.625 in
  pres.title = 'Only Broker';
  pres.company = 'Only Broker';

  const ic = {};
  const want = {
    handshake: fa.FaHandshake, book: fa.FaBookOpen, clone: fa.FaClone, userslash: fa.FaUserSlash, route: fa.FaRoute,
    phone: fa.FaMobileScreen, home: fa.FaHouseChimney, users: fa.FaUsers, shield: fa.FaShieldHalved, building: fa.FaBuilding,
    lock: fa.FaLock, key: fa.FaKey, whatsapp: fa.FaWhatsapp, compass: fa.FaCompass, scale: fa.FaScaleBalanced, check: fa.FaCheck,
    bullhorn: fa.FaBullhorn, camera: fa.FaCamera, database: fa.FaDatabase, seedling: fa.FaSeedling, rupee: fa.FaIndianRupeeSign,
    chart: fa.FaChartLine, link: fa.FaLink, arrow: fa.FaArrowRight, star: fa.FaStar,
  };
  for (const [k, C] of Object.entries(want)) {
    ic[k] = await icon(C, WHITE);
    ic[k + '_t'] = await icon(C, TEAL);
  }

  // --- helpers -------------------------------------------------------------------------------
  const bg = (s, color) => { s.background = { color }; };
  function title(s, text, { dark = false, y = 0.32, size = 25, w = 9 } = {}) {
    s.addText(text, { x: 0.5, y, w, h: 0.75, fontFace: HEAD, fontSize: size, bold: true, color: dark ? WHITE : INK, margin: 0, valign: 'top', isTextBox: true });
  }
  function tag(s, text, { dark = false } = {}) {
    // USP / MOAT marker, top-right
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.35, y: 0.34, w: 1.15, h: 0.34, rectRadius: 0.17, fill: { color: text === 'MOAT' ? SAFF : (dark ? WHITE : TEAL) }, line: { type: 'none' } });
    s.addText(text, { x: 8.35, y: 0.34, w: 1.15, h: 0.34, align: 'center', valign: 'middle', fontFace: BODY, fontSize: 11, bold: true, charSpacing: 2, color: text === 'MOAT' ? INK : (dark ? TEAL : WHITE), margin: 0, isTextBox: true });
  }
  function phone(s, img, x, y, h, caption, dark = false) {
    const w = h / 2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x - 0.06, y: y - 0.06, w: w + 0.12, h: h + 0.12, rectRadius: 0.14, fill: { color: INK }, line: { type: 'none' },
      shadow: { type: 'outer', color: '000000', opacity: 0.25, blur: 8, offset: 3, angle: 90 } });
    s.addImage({ path: IMG + img + '.jpg', x, y, w, h });
    if (caption) s.addText(caption, { x: x - 0.3, y: y + h + 0.1, w: w + 0.6, h: 0.3, align: 'center', fontFace: BODY, fontSize: 10.5, color: dark ? MINT : MUTED, margin: 0, isTextBox: true });
  }
  function points(s, items, x, y, w, h, { dark = false, size = 13, gap = 7 } = {}) {
    const runs = [];
    items.forEach((it, i) => {
      const last = i === items.length - 1;
      if (Array.isArray(it)) {
        runs.push({ text: it[0] + ' ', options: { bold: true, color: dark ? WHITE : INK, bullet: { indent: 14 }, paraSpaceAfter: gap } });
        runs.push({ text: it[1], options: { color: dark ? MINT : MUTED, breakLine: !last } });
      } else {
        runs.push({ text: it, options: { color: dark ? MINT : INK, bullet: { indent: 14 }, paraSpaceAfter: gap, breakLine: !last } });
      }
    });
    s.addText(runs, { x, y, w, h, fontFace: BODY, fontSize: size, valign: 'top', margin: 0, isTextBox: true });
  }
  function iconCircle(s, key, x, y, d = 0.5, fill = TEAL) {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: 'none' } });
    s.addImage({ data: ic[fill === WHITE || fill === MINT ? key + '_t' : key], x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52 });
  }
  function card(s, x, y, w, h, fill = WHITE) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: 'DCE2DF', width: 0.75 } });
  }

  // 1 — Title --------------------------------------------------------------------------------------
  let s = pres.addSlide(); bg(s, TEAL);
  s.addText('Only Broker', { x: 0.6, y: 1.25, w: 4.8, h: 0.9, fontFace: HEAD, fontSize: 46, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText('The broker’s operating system for India’s metro rental and resale market', { x: 0.6, y: 2.2, w: 4.6, h: 0.9, fontFace: BODY, fontSize: 18, color: MINT, margin: 0, isTextBox: true });
  s.addText([
    { text: 'Flats · Customers · Site visits · Owners — in one app', options: { breakLine: true } },
    { text: 'Rentals first, sales built in · Pilot: Thane West, MMR' },
  ], { x: 0.6, y: 3.35, w: 4.6, h: 0.7, fontFace: BODY, fontSize: 13, color: WHITE, margin: 0, isTextBox: true });
  s.addText('September 2026', { x: 0.6, y: 4.75, w: 3, h: 0.3, fontFace: BODY, fontSize: 11, color: SAFF, margin: 0, isTextBox: true });
  phone(s, 'today', 5.55, 0.55, 4.5);
  phone(s, 'oflat', 7.75, 0.55, 4.5);
  s.addNotes('Only Broker is a broker-first real-estate platform. Unlike portals that are built around listings or around cutting the broker out, we give the broker the tools to run their whole business — flats, customers, site visits, staff — and we bring owners and customers to them. We start with rentals in Thane West; sales (new and resale) are already in the data model.');

  // 2 — Problem ---------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Brokers run rentals on notebooks and WhatsApp');
  const probs = [
    ['userslash', 'Portals work against brokers', 'Built around listings or around cutting the broker out. The person who actually closes the deal is an afterthought.'],
    ['clone', 'One flat, five spellings', '“Hiranandani Est.”, “HE Thane”, “Hira Nandani”… Duplicates everywhere, and “available” is often weeks out of date.'],
    ['book', 'Customers live in notebooks', 'Walk-ins and phone calls live in a notebook. No follow-up, no history, no way to reach them all at once.'],
    ['route', 'Site visits are wasted', 'Flats already rented get shown, keys go missing, owners aren’t told, routes are guessed.'],
  ];
  probs.forEach(([k, h, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.35 + Math.floor(i / 2) * 1.95;
    card(s, x, y, 4.4, 1.75);
    iconCircle(s, k, x + 0.25, y + 0.3, 0.6);
    s.addText(h, { x: x + 1.05, y: y + 0.25, w: 3.15, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 1.05, y: y + 0.68, w: 3.15, h: 0.95, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addNotes('Four everyday pains. Brokers are the ones who close deals, yet portals treat them as a cost to remove. Their inventory is scattered and duplicated, their customers mostly offline, and site visits are inefficient. Every one of these is what Only Broker is designed to fix.');

  // 3 — Answer ----------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Built like ride-hailing: the broker is the driver');
  const sides = [
    ['phone', 'Broker app', 'Flats, customers, matching, visit plans, field staff, broadcasts'],
    ['home', 'Owners', 'Register the flat, choose which brokers may handle it, add photos, see status'],
    ['whatsapp', 'Customers', 'Shortlists, visit plans, consent and reviews by WhatsApp link — or the app'],
    ['shield', 'Ops console', 'Verify brokers, keep buildings clean, check the audit trail'],
  ];
  sides.forEach(([k, h, t], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.35, 2.1, 2.45);
    iconCircle(s, k, x + 0.75, 1.55, 0.6);
    s.addText(h, { x: x + 0.15, y: 2.3, w: 1.8, h: 0.4, align: 'center', fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.15, y: 2.72, w: 1.8, h: 1.0, align: 'center', fontFace: BODY, fontSize: 11.5, color: MUTED, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.05, w: 9.0, h: 1.05, rectRadius: 0.08, fill: { color: TEAL }, line: { type: 'none' } });
  iconCircle(s, 'building', 0.75, 4.27, 0.6, WHITE);
  s.addText([
    { text: 'Foundation: one clean universe of real buildings', options: { bold: true, color: WHITE, breakLine: true } },
    { text: 'Every flat is tied to exactly one real society, wing and floor — Thane West first, then the rest of MMR.', options: { color: MINT } },
  ], { x: 1.55, y: 4.13, w: 7.8, h: 0.9, fontFace: BODY, fontSize: 13, valign: 'middle', margin: 0, isTextBox: true });
  s.addNotes('Think of ride-hailing, where the driver is the hero. Here the broker is the driver. Owners and customers are brought to brokers, and a small ops team keeps the data clean. Everything sits on one clean universe of real buildings — that is the foundation competitors don\'t have.');

  // 4 — Rules we don't bend ------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, TEAL);
  title(s, 'Six rules we never bend', { dark: true });
  const rules = [
    ['lock', 'Flats & customers belong to the broker', 'Never shown, offered, moved or swapped between brokers. Enforced by the database itself.'],
    ['building', 'Closed universe of buildings', 'Nobody invents a building. Typos become matches, not duplicates.'],
    ['key', 'The owner decides who handles the flat', 'A broker gets it only after the owner ticks “Allow this broker”. Unticking is final.'],
    ['whatsapp', 'Offline customers are first-class', 'Everything a customer or owner does in the app also works from a WhatsApp link.'],
    ['compass', 'Meet brokers where they are', 'Pick flats their own way (“HE A-1203”); the matching engine earns trust, it is never forced.'],
    ['scale', 'Conduct-based house rules only', 'Pets, cooking, smoking, occupancy — never religion, caste, community or gender.'],
  ];
  rules.forEach(([k, h, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.3 + Math.floor(i / 2) * 1.35;
    iconCircle(s, k, x, y + 0.05, 0.55, SAFF);
    s.addText(h, { x: x + 0.75, y, w: 3.7, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: WHITE, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.75, y: y + 0.42, w: 3.7, h: 0.75, fontFace: BODY, fontSize: 11.5, color: MINT, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addNotes('These rules came from founder decisions and they are built into the product, not just policy. The first one matters most for broker trust: the platform never takes a flat or a customer from one broker and gives it to another.');

  // 5 — Broker app overview ----------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'One app for the broker’s whole day', { w: 7.6 }); tag(s, 'USP');
  points(s, [
    ['Today:', 'new leads, today’s visits, flats to reconfirm.'],
    ['Flats:', 'status, keys, owner contact, stale reminders.'],
    ['Customers:', 'walk-ins and calls, consent, requirements, full history.'],
    ['Add a flat in ~10 taps', 'or upload an Excel sheet — messy spellings are matched automatically.'],
    ['Android & iPhone', 'one codebase; Android test app installable today.'],
  ], 0.5, 1.35, 2.95, 3.9, { size: 12.5 });
  phone(s, 'today', 3.75, 1.2, 3.75, 'Today');
  phone(s, 'flats', 5.7, 1.2, 3.75, 'Flats');
  phone(s, 'customers', 7.65, 1.2, 3.75, 'Customers');
  s.addNotes('This is the broker\'s daily home. Everything is in one place: leads, visits, their own flats and their own customers. Adding a flat takes about ten taps; brokers with Excel sheets can upload them and we match their spellings to real buildings.');

  // 6 — Closed universe (MOAT) -------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'A closed universe of buildings = clean data', { w: 7.6 }); tag(s, 'MOAT');
  phone(s, 'addflat', 0.6, 1.2, 3.75, 'Impossible flat refused at entry');
  s.addImage({ path: IMG + 'ops_queue.jpg', x: 2.85, y: 1.25, w: 6.65, h: 6.65 * 624 / 1920 });
  s.addShape(pres.shapes.RECTANGLE, { x: 2.85, y: 1.25, w: 6.65, h: 6.65 * 624 / 1920, fill: { type: 'none' }, line: { color: 'C9D2CF', width: 0.75 } });
  s.addText('Ops review queue: a misspelled new society is matched to the real one (96%)', { x: 2.85, y: 3.47, w: 6.65, h: 0.28, fontFace: BODY, fontSize: 10.5, color: MUTED, margin: 0, isTextBox: true });
  points(s, [
    ['Every flat → one real society, wing and floor.', 'Wing layouts (floors, flats per floor, refuge floors) refuse “2504” in a 20-floor wing.'],
    ['Spellings and nicknames are learned.', '“Hiranandni Estates”, “HE” → Hiranandani Estate. Each confirmed spelling makes the next upload cleaner.'],
    ['Unknown names never create buildings', '— they become a request our team approves or merges.'],
  ], 2.85, 3.9, 6.65, 1.5, { size: 12, gap: 4 });
  s.addNotes('This is our first moat. Portals let anyone type anything, so the same building exists many times and data rots. We keep a closed universe: every flat belongs to one real building, wing and floor. Mistakes are caught at entry, and every correction teaches the system. The longer we run, the cleaner the data gets — hard for a competitor to copy.');

  // 7 — One flat, one truth (MOAT) ---------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'One flat, one truth — confirmed by the owner', { w: 7.6 }); tag(s, 'MOAT');
  phone(s, 'flat', 0.6, 1.2, 3.75, 'Broker’s flat page');
  phone(s, 'l_owner', 2.75, 1.2, 3.75, 'Owner’s WhatsApp link');
  points(s, [
    ['Owner confirms availability', 'with one tap from a WhatsApp link — no app, no login.'],
    ['Rented by one broker?', 'Every other broker holding that flat is alerted (without saying who).'],
    ['Stale flats', 'get reminders at 21 days and are marked “unverified” — customers stop seeing ghost listings.'],
    ['200-attribute dictionary, only 17 essential.', 'Owner answers override broker answers; distances to station, schools and autos are computed from the map.'],
  ], 5.05, 1.3, 4.45, 3.9, { size: 12.5 });
  s.addNotes('Many brokers may hold the same flat, but there is one physical flat and one truth about it. The owner confirms status from a WhatsApp link. When any broker marks it rented, the others are warned so nobody wastes a visit. Our attribute dictionary has 200 fields but a broker only needs 17 to list a flat.');

  // 8 — Matching ------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Matching that explains itself', { w: 7.6 }); tag(s, 'USP');
  points(s, [
    ['Searches only the broker’s own flats.', 'Never another broker’s inventory.'],
    ['Every match shows why:', '✓ fits, ✗ doesn’t fit, ? not confirmed — budget, BHK, pets, gas stove, availability…'],
    ['“Show why others don’t fit”', 'so the broker can talk the customer through trade-offs.'],
    ['One tap to a WhatsApp shortlist', '— the customer taps “Interested”, and it lands in their history.'],
  ], 0.5, 1.3, 4.45, 3.9, { size: 12.5 });
  phone(s, 'customer', 5.25, 1.2, 3.75, 'Customer & requirement');
  phone(s, 'matches', 7.4, 1.2, 3.75, 'Explained matches');
  s.addNotes('Matching respects the broker\'s ownership: it only looks at their own flats. Each result explains itself with green, red and amber chips, so a broker can trust it and explain it to the customer.');

  // 9 — Pick flats yourself + visits ------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Site visits: plan your way, run them like a fleet', { w: 7.6 }); tag(s, 'USP');
  phone(s, 'vsearch', 0.6, 1.2, 3.75, '“rodas 802” → add to route');
  phone(s, 'visit', 2.75, 1.2, 3.75, 'Optimised route');
  phone(s, 'staff', 4.9, 1.2, 3.75, 'Field staff — works offline');
  points(s, [
    ['Pick flats yourself:', 'type the society and flat you have in mind (“HE A-1203”).'],
    ['Shortest route', 'and time slots worked out automatically.'],
    ['Customer confirms', 'the plan from a WhatsApp link; owners are notified.'],
    ['Field staff', 'see only their route; check-ins and outcomes work without network and sync later.'],
    ['Keys', 'always known: office, owner, staff, lock-box.'],
  ], 7.15, 1.3, 2.4, 3.95, { size: 11.5, gap: 5 });
  s.addNotes('Brokers keep using their own judgement — they can type a society and flat number and add it straight to the route. The system then does the boring work: routing, notifying owners, sending the customer a confirmation link, and assigning field staff, whose app works even without network.');

  // 10 — Offline customers first-class ---------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'No app needed: WhatsApp links do it all', { w: 7.6 }); tag(s, 'USP');
  [['l_short', 'Shortlist — tap Interested'], ['l_plan', 'Visit plan — confirm'], ['l_consent', 'Consent — DPDP-ready'], ['l_review', 'Review after the visit']]
    .forEach(([img, cap], i) => phone(s, img, 0.75 + i * 2.25, 1.25, 3.5, cap));
  s.addText('Walk-in and phone customers become real, reachable customers — without installing anything. Flat numbers stay hidden until the visit.', { x: 0.5, y: 5.08, w: 9, h: 0.35, fontFace: BODY, fontSize: 11, italic: true, color: TEAL, margin: 0, isTextBox: true });
  s.addNotes('Most customers are offline. We don\'t force an app on them: every step — shortlist, visit confirmation, consent, review — works from a private link on WhatsApp or SMS. Their responses flow straight into the broker\'s customer history.');

  // 11 — Two assets & broadcasts (MOAT) ------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'A broker’s second asset: their customer list', { w: 7.6 }); tag(s, 'MOAT');
  points(s, [
    ['Private, like their flats.', 'Never visible to any other broker.'],
    ['Broadcast in one tap:', 'new flat, price drop in an area, or news — to all customers or those looking in one area.'],
    ['Customers not on the app yet', 'get a WhatsApp invite with the same news.'],
    ['Growth loop:', 'every broadcast pulls more offline customers onto the platform.'],
    ['Customers stay in control:', '“Stop updates from this broker”. Free in the pilot, credits later.'],
  ], 0.5, 1.3, 3.2, 3.95, { size: 12, gap: 5 });
  phone(s, 'bcast', 3.85, 1.2, 3.75, 'Compose');
  phone(s, 'bsent', 5.75, 1.2, 3.75, 'Invite the rest');
  phone(s, 'cupd', 7.65, 1.2, 3.75, 'Customer’s updates');
  s.addNotes('Brokers have two assets: flats and customers. Broadcasts make the customer list valuable — one message reaches everyone. Customers who aren\'t on the app yet get a WhatsApp invite, so the more a broker broadcasts, the more of their offline customers join. That\'s a built-in growth engine, and it makes brokers stay.');

  // 12 — Owners in control ---------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Owners in control — without extra work', { w: 7.6 }); tag(s, 'USP');
  phone(s, 'oflat', 0.6, 1.2, 3.75, 'Who handles my flat');
  phone(s, 'oremove', 2.75, 1.2, 3.75, 'Untick = remove, final');
  phone(s, 'onear', 4.9, 1.2, 3.75, 'Invite needs the tick');
  points(s, [
    ['Register with proof', '(index II / share certificate / bill) — kept, not checked: a deterrent.'],
    ['“Allow this broker to handle my property”', '— no flat reaches a broker without the tick.'],
    ['Untick any broker:', 'they lose the flat and can’t re-add it; they may ask to be added back.'],
    ['Read-only status:', '“currently serviced by … · number · review”.'],
  ], 7.15, 1.3, 2.4, 3.95, { size: 11.5, gap: 5 });
  s.addNotes('Owners get a simple, powerful control: a tick box. A broker only receives an owner\'s flat after the owner ticks "Allow this broker to handle my property", and unticking removes them — the owner\'s decision is final. Owners can also see who is handling the flat, call them, and review them.');

  // 13 — Shared media with owner approval ------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Photos & videos: one good set per flat', { w: 7.6 });
  phone(s, 'flat2', 0.6, 1.2, 3.75, 'Flat photos on the broker’s page');
  const steps = [
    ['camera', 'Owner or broker uploads', 'Customers never can. Photos are straightened, resized, and location details removed.'],
    ['check', 'Owner approves', 'A broker’s upload stays “waiting” until the owner approves. Max 5 photos + 1 video per flat.'],
    ['users', 'Live everywhere it helps', 'Every broker holding the flat, and the customer’s shortlist page — never the flat number.'],
  ];
  steps.forEach(([k, h, t], i) => {
    const y = 1.3 + i * 1.3;
    card(s, 3.0, y, 6.5, 1.1);
    iconCircle(s, k, 3.2, y + 0.25, 0.6);
    s.addText(`${i + 1}. ${h}`, { x: 4.0, y: y + 0.14, w: 5.3, h: 0.35, fontFace: BODY, fontSize: 14, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(t, { x: 4.0, y: y + 0.5, w: 5.3, h: 0.55, fontFace: BODY, fontSize: 11.5, color: MUTED, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addNotes('Photos belong to the flat, not to one broker, so there\'s one good set instead of ten bad ones. Owners and the brokers they allow can upload; nothing a broker uploads goes live until the owner approves. Customers see live photos on their shortlist, but never the flat number.');

  // 13a — Selling ready inventory: three routes (USP) -----------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Selling ready flats: all three routes, one app', { w: 7.6 }); tag(s, 'USP');
  phone(s, 'thub', 0.6, 1.2, 3.75, 'Offers from brokers');
  phone(s, 'tblast', 2.75, 1.2, 3.75, 'Share with brokers nearby');
  points(s, [
    ['A. Fellow brokers (co-broking):', 'the broker’s own list of channel partners, imported from Excel or phone contacts. Blast ready flats to brokers in and around the flat — widen the distance, send to all, or tick names.'],
    ['B. Walk-ins and customers we send:', 'matching against the broker’s own flats, visit plans, field staff.'],
    ['C. The whole customer list:', 'import it once, then one message with several new flats reaches everyone — in the app, or a one-tap WhatsApp.'],
    ['Trade-level only:', 'society, area, BHK, price. Never the flat number, owner, customer or commission.'],
  ], 5.05, 1.25, 4.5, 4.1, { size: 12, gap: 5 });
  s.addNotes('In the meeting, brokers told us ready inventory moves three ways: through fellow brokers, through walk-in customers, and by blasting the whole customer list. All three now live in one app. Co-broking uses the broker’s own list of fellow brokers and the flat’s location, so the right brokers nearby hear first. Nothing that lets anyone go around the listing broker ever leaves: no flat number, no owner, no customer, no commission. The owner is not asked; it is a trade agreement between brokers.');

  // 13b — Building structure from official records (MOAT) -----------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Every building, floor by floor — officially', { w: 7.6 }); tag(s, 'MOAT');
  phone(s, 'struct', 0.6, 1.2, 3.75, 'The building picture: my flats marked');
  points(s, [
    ['Our own source, never brokers:', 'TMC property-tax register (requested formally — there is no public API), MahaRERA for newer towers, IGR registrations to fill gaps.'],
    ['From each wing’s flat list we work out the layout:', 'floors, flats per floor, refuge floors, odd flats like 2001A.'],
    ['A flat that isn’t on the list cannot be added —', 'by any broker or owner. The universe is closed down to the flat.'],
    ['Owner names are never stored,', 'even when the source file has them.'],
    ['Built and ready:', 'upload page in the ops console; waiting on the TMC data request.'],
  ], 3.0, 1.25, 6.5, 4.1, { size: 12.5, gap: 6 });
  s.addNotes('The foundation is a correct list of every flat in every building. That has to come from official records, not from brokers, whose lists are fragmentary. TMC has no public API, so we are requesting the register formally, under RTI and a data-sharing letter. MahaRERA covers the newer towers. Once a wing’s list is loaded, the system works out its layout and refuses any flat number that does not exist. This is slow, careful work — which is exactly why it is hard to copy.');

  // 14 — Marketplace -----------------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Next: one enquiry, every relevant broker', { w: 7.6 }); tag(s, 'MOAT');
  phone(s, 'leads', 0.6, 1.2, 3.75, 'Broker’s leads');
  points(s, [
    ['One enquiry, every nearby broker:', 'the customer posts once; brokers who work in that area get it instantly.'],
    ['Brokers see how many of THEIR flats match', 'before they respond — and reply with their terms and rating.'],
    ['Owners invite brokers', 'from a list of verified brokers near their flat, ranked by rating.'],
    ['Anonymous supply map:', 'customers see where flats are, never whose — small clusters are hidden.'],
    ['Status:', 'built and tested in the backend; switched on after the pilot proves the broker app.'],
  ], 3.0, 1.3, 6.5, 3.95, { size: 13, gap: 6 });
  s.addNotes('Once brokers depend on the app, we switch on the marketplace. A customer posts one enquiry and every relevant broker nearby gets it — like a ride request. Brokers compete on terms, rating and response time. The pieces are already built; we switch them on after the pilot.');

  // 15 — Trust, privacy, compliance (MOAT) -------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Trust by design: privacy, audit, compliance', { w: 7.6 }); tag(s, 'MOAT');
  s.addImage({ path: IMG + 'ops_brokers.jpg', x: 0.5, y: 1.3, w: 4.4, h: 4.4 * 624 / 1920 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.4, h: 4.4 * 624 / 1920, fill: { type: 'none' }, line: { color: 'C9D2CF', width: 0.75 } });
  s.addImage({ path: IMG + 'ops_audit.jpg', x: 0.5, y: 3.0, w: 4.4, h: 4.4 * 624 / 1920 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 4.4, h: 4.4 * 624 / 1920, fill: { type: 'none' }, line: { color: 'C9D2CF', width: 0.75 } });
  s.addText('Ops console: broker verification (RERA) and tamper check', { x: 0.5, y: 4.5, w: 4.4, h: 0.3, fontFace: BODY, fontSize: 10.5, color: MUTED, margin: 0, isTextBox: true });
  points(s, [
    ['Each broker’s data is walled off by the database itself', '— checked by automated tests on every change.'],
    ['Tamper-evident audit trail', 'and flat-status history: any altered record is detected.'],
    ['Phone numbers encrypted;', 'owner numbers never reach customers or field staff.'],
    ['Customer consent recorded', '(OTP, link or verbal) — ready for India’s DPDP Act.'],
    ['Brokers verified', 'by our team, with MahaRERA number check.'],
  ], 5.2, 1.3, 4.3, 3.95, { size: 12, gap: 5 });
  s.addNotes('Brokers will only put their business on a platform they trust. Isolation between brokers is enforced by the database, not just the app, and it is tested automatically. Every change is audited in a tamper-evident log. Consent and encryption keep us ready for the DPDP Act.');

  // 16 — Moats summary (dark) ----------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, TEAL);
  title(s, 'Why this is hard to copy', { dark: true });
  const moats = [
    ['database', 'Official building data', 'Every wing’s flats from TMC / MahaRERA records, plus learned spellings — the universe is closed down to the flat.'],
    ['lock', 'Brokers’ two assets live here', 'Flats and customers, with their full history — switching away means leaving the business behind.'],
    ['key', 'Owners trust the tick', 'Owner control and reviews make owners send flats to brokers through us.'],
    ['whatsapp', 'Network loops', 'Co-broking pulls fellow brokers in; broadcasts pull offline customers in — broker by broker.'],
    ['shield', 'Trust by design', 'Isolation, audit and consent built in from day one — slow and costly to retrofit.'],
  ];
  moats.forEach(([k, h, t], i) => {
    const x = 0.5 + i * 1.84;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.35, w: 1.7, h: 3.7, rectRadius: 0.08, fill: { color: '15505A' }, line: { type: 'none' } });
    iconCircle(s, k, x + 0.55, 1.6, 0.6, SAFF);
    s.addText(h, { x: x + 0.12, y: 2.4, w: 1.46, h: 0.75, align: 'center', fontFace: BODY, fontSize: 13, bold: true, color: WHITE, margin: 0, valign: 'top', isTextBox: true });
    s.addText(t, { x: x + 0.12, y: 3.2, w: 1.46, h: 1.75, align: 'center', fontFace: BODY, fontSize: 11, color: MINT, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addNotes('Five moats. Clean data that compounds with use. Lock-in, because brokers\' flats and customers live here. Owner trust through the tick and reviews. A growth loop through WhatsApp links and broadcasts. And trust built in from the start — isolation, audit and consent — which is expensive for anyone else to retrofit.');

  // 17 — Business model --------------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'How we make money (to be tested in the pilot)', { w: 8.5 });
  const rev = [
    ['users', 'Broker subscription', 'Monthly plan per firm, with seats for managers and field staff. The core revenue line.'],
    ['bullhorn', 'Message credits', 'Plans include a number of broadcasts and WhatsApp messages; brokers top up. Free in the pilot.'],
    ['chart', 'Marketplace leads', 'After the pilot: credits to respond to customer enquiries and owner invitations.'],
  ];
  rev.forEach(([k, h, t], i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.35, 2.85, 2.9);
    iconCircle(s, k, x + 0.25, 1.6, 0.6);
    s.addText(h, { x: x + 0.25, y: 2.35, w: 2.4, h: 0.45, fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: 2.85, w: 2.4, h: 1.3, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.5, w: 9.0, h: 0.65, rectRadius: 0.08, fill: { color: MINT }, line: { type: 'none' } });
  s.addText('Pilot: free for Thane West brokers. We measure time saved per flat, stale-listing rate, visits per customer — and what brokers would pay.', { x: 0.7, y: 4.5, w: 8.6, h: 0.65, fontFace: BODY, fontSize: 12.5, color: TEAL, valign: 'middle', margin: 0, isTextBox: true });
  s.addNotes('Brokers pay because the app saves them time and makes them money. Subscription is the core; broadcasts and messages are a natural usage-based add-on; marketplace leads come later. Pricing is still to be decided — the pilot is free and will tell us willingness to pay.');

  // 18 — Where we are --------------------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Where we are today');
  const stats = [['225+', 'automated tests, all passing'], ['4', 'app modes: broker, field staff, owner, customer'], ['200', 'flat attributes — only 17 essential'], ['Live', 'Android test app & online demo']];
  stats.forEach(([n, l], i) => {
    const x = 0.5 + i * 2.3;
    s.addText(n, { x, y: 1.25, w: 2.1, h: 0.85, fontFace: HEAD, fontSize: 40, bold: true, color: TEAL, margin: 0, isTextBox: true });
    s.addText(l, { x, y: 2.1, w: 2.1, h: 0.55, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, valign: 'top', isTextBox: true });
  });
  const stages = [['Build the core', 'Done', OK], ['Clean Thane West data', 'Now', SAFF], ['Pilot broker on the real app', 'Next', TEAL], ['Measure the pilot', 'Then', MUTED], ['More brokers → marketplace', 'Later', MUTED]];
  s.addShape(pres.shapes.LINE, { x: 0.8, y: 3.55, w: 8.4, h: 0, line: { color: 'C9D2CF', width: 2 } });
  stages.forEach(([h, st, c], i) => {
    const x = 0.5 + i * 1.8;
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: 3.4, w: 0.3, h: 0.3, fill: { color: c }, line: { color: WHITE, width: 2 } });
    s.addText(st, { x, y: 3.8, w: 1.7, h: 0.3, fontFace: BODY, fontSize: 11, bold: true, color: c, margin: 0, isTextBox: true });
    s.addText(h, { x, y: 4.1, w: 1.7, h: 0.8, fontFace: BODY, fontSize: 12.5, color: INK, margin: 0, valign: 'top', isTextBox: true });
  });
  s.addNotes('The core is built and tested: broker, field staff, owner and customer modes, the link pages, the ops console and the data checks. We are now cleaning Thane West data with the pilot broker. Next, the pilot broker moves onto the real app on a server with real SMS and WhatsApp.');

  // 19 — Next steps --------------------------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, LIGHT);
  title(s, 'Next 90 days');
  const next = [
    ['building', 'Thane West data', 'Pilot broker confirms map pins; official flat lists loaded — TMC register request (RTI), MahaRERA for newer towers.'],
    ['phone', 'Pilot broker live', 'Server in the cloud, real logins, Android app; iPhone via TestFlight.'],
    ['whatsapp', 'Real messages', 'DLT sender ID and templates, WhatsApp Business, Google Maps accounts.'],
    ['chart', 'Measure & price', 'Time per flat, stale listings, visits per deal, willingness to pay → pricing decision.'],
  ];
  next.forEach(([k, h, t], i) => {
    const y = 1.3 + i * 0.98;
    iconCircle(s, k, 0.5, y + 0.05, 0.6);
    s.addText(h, { x: 1.3, y, w: 2.6, h: 0.7, fontFace: BODY, fontSize: 15, bold: true, color: INK, valign: 'middle', margin: 0, isTextBox: true });
    s.addText(t, { x: 3.9, y, w: 5.6, h: 0.7, fontFace: BODY, fontSize: 12.5, color: MUTED, valign: 'middle', margin: 0, isTextBox: true });
  });
  s.addNotes('Four workstreams for the next 90 days: clean Thane West data, put the pilot broker on the live app, switch on real SMS and WhatsApp, and measure the pilot so we can set pricing.');

  // 20 — Closing ----------------------------------------------------------------------------------------------------------------------------
  s = pres.addSlide(); bg(s, TEAL);
  s.addText('See it working', { x: 0.6, y: 0.9, w: 5, h: 0.8, fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, margin: 0, isTextBox: true });
  s.addText([
    { text: 'Online demo (any phone or laptop)', options: { bold: true, color: WHITE, breakLine: true } },
    { text: 'claude.ai/artifact/3ibs72K1zjuPdY2dF5rbXZ', options: { color: SAFF, breakLine: true } },
    { text: ' ', options: { breakLine: true, fontSize: 6 } },
    { text: 'Demo logins — OTP 123456', options: { bold: true, color: WHITE, breakLine: true } },
    { text: 'Broker 98200 00001 · Field staff 98200 10000', options: { color: MINT, breakLine: true } },
    { text: 'Owner 98200 20000 · Customer 98765 43210', options: { color: MINT } },
  ], { x: 0.6, y: 1.9, w: 5.2, h: 2.4, fontFace: BODY, fontSize: 15, valign: 'top', margin: 0, isTextBox: true });
  s.addText('Only Broker — the broker is the driver.', { x: 0.6, y: 4.6, w: 5.2, h: 0.4, fontFace: BODY, fontSize: 14, italic: true, color: MINT, margin: 0, isTextBox: true });
  phone(s, 'login', 6.5, 0.55, 4.5);
  s.addNotes('Now let me show you the app itself. Every login uses OTP 123456 in the demo. I\'ll start as the broker, then switch to the owner and the customer.');

  await pres.writeFile({ fileName: __dirname + '/Only-Broker-presentation.pptx' });
  console.log('written');
})();
