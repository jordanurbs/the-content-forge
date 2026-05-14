#!/usr/bin/env node
/**
 * Creates section folders in Skool classroom via camofox-browser API.
 * Run: node scripts/skool-create-folders.js
 */

const fs = require('fs');
const BASE = 'http://localhost:9377';
const USER = 'skool-agent';
const API_KEY = process.env.CAMOFOX_API_KEY;

const FOLDERS = [
  'Context Foundations',
  'Skills',
  'Agentic Harnesses',
  'Autonomous Agent Architectures',
  'Ship It',
];

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  return res.json();
}

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function screenshot(tabId, label) {
  const res = await fetch(`${BASE}/tabs/${tabId}/screenshot?userId=${USER}`);
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(`/tmp/skool-${label}.png`, buf);
  console.log(`  📸 /tmp/skool-${label}.png`);
}

async function importCookies() {
  const raw = fs.readFileSync(`${process.env.HOME}/.camofox/cookies/skool.txt`, 'utf8');
  const lines = raw.split('\n').filter(l => !l.startsWith('#') && l.trim());
  const cookies = [];
  const seen = new Set();
  for (const line of lines) {
    const parts = line.split('\t');
    if (parts.length < 7) continue;
    const [domain, , path, secure, expires, name, value] = parts;
    if (!domain.includes('skool.com')) continue;
    const key = `${domain}|${name}`;
    if (seen.has(key)) continue;
    seen.add(key);
    cookies.push({
      name: name.trim(), value: value.trim(), domain: domain.trim(),
      path: path.trim(), secure: secure.trim() === 'TRUE',
      httpOnly: false, expires: parseInt(expires) > 0 ? parseInt(expires) : -1
    });
  }
  const result = await fetch(`${BASE}/sessions/${USER}/cookies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${API_KEY}` },
    body: JSON.stringify({ cookies })
  }).then(r => r.json());
  console.log(`Imported ${result.count} cookies`);
}

async function createFolder(tabId, name) {
  console.log(`\n📁 Creating folder: ${name}`);

  // Open ... menu
  let r = await api('POST', `/tabs/${tabId}/click`, {
    userId: USER,
    selector: 'text=Knowledge Infrastructure >> .. >> button >> nth=0'
  });
  if (r.error) { console.log('  Menu click error:', r.error.slice(0, 100)); return false; }
  await sleep(1500);

  // Click "Add folder"
  r = await api('POST', `/tabs/${tabId}/click`, {
    userId: USER, selector: 'text=Add folder'
  });
  if (r.error) { console.log('  Add folder click error:', r.error.slice(0, 100)); return false; }
  await sleep(1500);

  // Screenshot to see dialog state
  await screenshot(tabId, `pre-type-${name.replace(/\s+/g, '-').toLowerCase()}`);

  // Click directly on the input field in the dialog
  // The dialog uses a specific structure - try clicking the input with maxlength=50
  r = await api('POST', `/tabs/${tabId}/click`, {
    userId: USER, selector: 'input[maxlength="50"], input[max="50"]'
  });
  if (r.error) {
    console.log('  Input click failed, trying alternative selectors...');
    // Try other selectors
    r = await api('POST', `/tabs/${tabId}/click`, {
      userId: USER, selector: '[class*="ModalContent"] input, [class*="modal-content"] input'
    });
  }
  await sleep(500);

  // Type the folder name
  r = await api('POST', `/tabs/${tabId}/type`, {
    userId: USER,
    selector: 'input[maxlength="50"], input[max="50"]',
    text: name
  });
  if (r.error) {
    console.log('  Type error with maxlength selector, trying alternatives...');
    // Try keyboard-based approach: just type after clicking
    r = await api('POST', `/tabs/${tabId}/press`, {
      userId: USER, key: 'Tab'
    });
    await sleep(300);
  }
  await sleep(500);

  await screenshot(tabId, `typed-${name.replace(/\s+/g, '-').toLowerCase()}`);

  // Click ADD button
  r = await api('POST', `/tabs/${tabId}/click`, {
    userId: USER, selector: 'button:text-is("ADD")'
  });
  if (r.error) {
    console.log('  ADD click error, trying alternatives...');
    r = await api('POST', `/tabs/${tabId}/click`, {
      userId: USER, selector: ':text("ADD") >> nth=-1'
    });
  }
  await sleep(2000);

  await screenshot(tabId, `after-${name.replace(/\s+/g, '-').toLowerCase()}`);
  return true;
}

async function main() {
  console.log('=== Skool Folder Creator ===\n');

  // Import cookies first
  await importCookies();

  // Create tab
  const tab = await api('POST', '/tabs', {
    userId: USER,
    sessionKey: 'folder-create',
    url: process.env.SKOOL_COURSE_URL || 'https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID'
  });

  if (tab.error) {
    console.error('Failed to create tab:', tab.error.slice(0, 200));
    process.exit(1);
  }

  const tabId = tab.tabId;
  console.log(`Tab: ${tabId}`);
  console.log(`URL: ${tab.url}`);
  await sleep(3000);
  await screenshot(tabId, 'start');

  for (const folder of FOLDERS) {
    const ok = await createFolder(tabId, folder);
    if (!ok) {
      console.log(`  ⚠️  Failed to create ${folder}, continuing...`);
    }
    await sleep(1000);
  }

  await screenshot(tabId, 'final');
  console.log('\n✅ Done! Check /tmp/skool-*.png for screenshots');
}

main().catch(e => { console.error(e); process.exit(1); });
