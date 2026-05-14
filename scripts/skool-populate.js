#!/usr/bin/env node
/**
 * Populate Skool classroom with context-engineering course content.
 * Uses camofox-browser REST API on localhost:9377.
 */

const fs = require('fs');
const path = require('path');

const BASE = 'http://localhost:9377';
const USER = 'skool-agent';
const SESSION = 'skool-populate';

// Course structure: sections -> lessons
const SECTIONS = [
  {
    name: 'Context Foundations',
    lessons: [
      { id: '3.1.1', slug: 'from-prompt-to-context', title: 'From Prompt Engineering to Context Engineering' },
      { id: '3.1.2', slug: 'claudemd-persistent-memory', title: 'ClaudeMD — Your AI\'s Persistent Memory' },
      { id: '3.1.3', slug: 'context-hygiene', title: 'Context Hygiene — Keeping Your AI Sharp' },
    ]
  },
  {
    name: 'Skills',
    lessons: [
      { id: '3.2.1', slug: 'what-are-skills', title: 'What Are Skills? The Universal Context Module' },
      { id: '3.2.2', slug: 'building-first-skill', title: 'Building Your First Skill — The Launch Skill' },
      { id: '3.2.3', slug: 'marketing-skills-full-campaign', title: 'Marketing Skills — Full Campaign Pipeline' },
      { id: '3.2.4', slug: 'skills-across-frameworks', title: 'Skills Across Frameworks — Universal Patterns' },
    ]
  },
  {
    name: 'Agentic Harnesses',
    lessons: [
      { id: '3.3.1', slug: 'what-is-agentic-harness', title: 'What Is an Agentic Harness?' },
      { id: '3.3.2', slug: 'safe-agentic-workflow', title: 'The Safe Agentic Workflow — Your Harness Template' },
      { id: '3.3.3', slug: 'building-your-harness', title: 'Building Your Own Harness — The Harness Builder Skill' },
    ]
  },
  {
    name: 'Autonomous Agent Architectures',
    lessons: [
      { id: '3.4.1', slug: 'autonomous-agents-beyond-harness', title: 'What Are Autonomous Agents? — Beyond the Harness' },
      { id: '3.4.2', slug: 'openclaw-heartbeat-bootstrap', title: 'OpenClaw — The Heartbeat Pattern & Bootstrap Context' },
      { id: '3.4.3', slug: 'agent-zero-local-first', title: 'Agent Zero — The Local-First Autonomous Framework' },
    ]
  },
  {
    name: 'Ship It',
    lessons: [
      { id: '3.5.1', slug: 'context-engineering-stack', title: 'Your Context Engineering Stack' },
      { id: '3.5.2', slug: 'capstone-deploy-campaign', title: 'Capstone — Deploy Your Marketing Campaign' },
      { id: '3.5.3', slug: 'congratulations-whats-next', title: 'Congratulations — What\'s Next?' },
    ]
  }
];

const LESSONS_DIR = path.join(__dirname, '..', 'context-engineering', 'lessons');

async function api(method, endpoint, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);
  const url = `${BASE}${endpoint}`;
  const res = await fetch(url, opts);
  const data = await res.json();
  if (data.error) {
    console.error(`  ERROR: ${data.error.slice(0, 200)}`);
  }
  return data;
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function screenshot(tabId, name) {
  const res = await fetch(`${BASE}/tabs/${tabId}/screenshot?userId=${USER}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const outPath = `/tmp/skool-${name}.png`;
  fs.writeFileSync(outPath, buf);
  console.log(`  Screenshot: ${outPath}`);
}

async function snapshot(tabId) {
  const data = await api('GET', `/tabs/${tabId}/snapshot?userId=${USER}`);
  return data.snapshot || '';
}

async function click(tabId, selector) {
  return api('POST', `/tabs/${tabId}/click`, { userId: USER, selector });
}

async function type(tabId, selector, text) {
  return api('POST', `/tabs/${tabId}/type`, { userId: USER, selector, text });
}

async function navigate(tabId, url) {
  return api('POST', `/tabs/${tabId}/navigate`, { userId: USER, url });
}

async function pressKey(tabId, key) {
  return api('POST', `/tabs/${tabId}/press`, { userId: USER, key });
}

async function createFolder(tabId, name) {
  console.log(`\nCreating folder: ${name}`);

  // Click the ... menu next to Knowledge Infrastructure
  await click(tabId, 'text=Knowledge Infrastructure >> .. >> button >> nth=0');
  await sleep(1000);

  // Click "Add folder"
  await click(tabId, 'text=Add folder');
  await sleep(1000);

  // Type name into dialog input
  await type(tabId, 'dialog input, [role=dialog] input, form input', name);
  await sleep(500);

  // Click ADD button
  await click(tabId, '[role=dialog] button:has-text("ADD"), form button:has-text("ADD")');
  await sleep(2000);

  await screenshot(tabId, `folder-${name.replace(/\s+/g, '-').toLowerCase()}`);
}

async function addPageToFolder(tabId, folderName, pageName) {
  console.log(`  Adding page: ${pageName} to ${folderName}`);

  // Find and right-click/hover over the folder to get its menu
  // First, click the folder's ... menu
  const folderSelector = `text="${folderName}" >> .. >> button >> nth=-1`;

  // Try clicking the folder's three-dot menu
  await click(tabId, folderSelector);
  await sleep(1000);

  // Click "Add page"
  await click(tabId, 'text=Add page');
  await sleep(1000);

  // Type page name
  await type(tabId, 'dialog input, [role=dialog] input, form input', pageName);
  await sleep(500);

  // Click ADD
  await click(tabId, '[role=dialog] button:has-text("ADD"), form button:has-text("ADD")');
  await sleep(2000);
}

async function pasteHTMLContent(tabId, htmlFilePath) {
  if (!fs.existsSync(htmlFilePath)) {
    console.log(`  WARNING: HTML file not found: ${htmlFilePath}`);
    return;
  }

  const html = fs.readFileSync(htmlFilePath, 'utf8');
  console.log(`  Pasting content from ${path.basename(htmlFilePath)} (${html.length} chars)`);

  // Click the edit button (pencil icon) on the lesson page
  await click(tabId, '[aria-label="edit"], button:has(svg):near(h1)');
  await sleep(1000);

  // Find the content editor and paste HTML
  // Skool uses a rich text editor — we need to paste HTML content
  // This is the tricky part — we may need to use the keyboard shortcut approach

  // For now, log what we'd paste
  console.log(`  Content length: ${html.length} chars`);
}

async function main() {
  console.log('=== Skool Course Populator ===');
  console.log(`Lessons dir: ${LESSONS_DIR}`);
  console.log(`Sections: ${SECTIONS.length}`);
  console.log(`Total lessons: ${SECTIONS.reduce((s, sec) => s + sec.lessons.length, 0)}`);
  console.log();

  // Check server health
  const health = await api('GET', '/health');
  console.log('Server health:', health.ok ? 'OK' : 'DOWN');
  if (!health.ok) process.exit(1);

  // Check for existing tab
  const tabs = await api('GET', `/tabs?userId=${USER}`);
  let tabId;

  if (tabs.tabs && tabs.tabs.length > 0) {
    tabId = tabs.tabs[0].tabId;
    console.log(`Reusing existing tab: ${tabId}`);
  } else {
    // Create new tab
    const tab = await api('POST', '/tabs', {
      userId: USER,
      sessionKey: SESSION,
      url: process.env.SKOOL_COURSE_URL || 'https://www.skool.com/YOUR_COMMUNITY/classroom/YOUR_COURSE_ID'
    });
    tabId = tab.tabId;
    console.log(`Created new tab: ${tabId}`);
  }

  await sleep(3000);
  await screenshot(tabId, 'start');

  // Create folders for each section
  for (const section of SECTIONS) {
    await createFolder(tabId, section.name);
  }

  console.log('\n=== Folder creation complete ===');
  await screenshot(tabId, 'folders-done');

  // TODO: Add pages within each folder and populate content
  // This will be Phase 2 once we confirm folders are created

  console.log('\nDone! Check screenshots in /tmp/skool-*.png');
}

main().catch(console.error);
