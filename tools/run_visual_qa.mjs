#!/usr/bin/env node
import fs from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';

const DEFAULT_BASE_URL = 'http://localhost:8000/';
const DEFAULT_OUTPUT_DIR = 'qa-screenshots';
const PAGES = [
  'index.html',
  'services.html',
  'pricing.html',
  'free-guide.html',
  'single-decision-maker.html',
  'out-of-state-executor.html',
  'founder-plan.html',
];
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 1100, mobile: false },
  { name: 'mobile', width: 390, height: 1200, mobile: true },
];

function fail(message) {
  console.error(message);
  process.exit(1);
}

function parseArgs(args) {
  let baseUrl = DEFAULT_BASE_URL;
  let outputDir = DEFAULT_OUTPUT_DIR;

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    const next = args[index + 1];

    if (arg === '--help' || arg === '-h') {
      console.log('Usage: node tools/run_visual_qa.mjs [--base-url url] [--out dir]');
      process.exit(0);
    }

    if (arg === '--base-url') {
      if (!next || next.startsWith('--')) fail('Missing value for --base-url');
      baseUrl = next;
      index += 1;
      continue;
    }

    if (arg === '--out') {
      if (!next || next.startsWith('--')) fail('Missing value for --out');
      outputDir = next;
      index += 1;
      continue;
    }

    fail(`Unknown option: ${arg}`);
  }

  return { baseUrl: baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`, outputDir };
}

function chromeCandidates() {
  if (process.platform === 'win32') {
    return [
      process.env.CHROME_PATH,
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      path.join(process.env.LOCALAPPDATA || '', 'Google\\Chrome\\Application\\chrome.exe'),
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    ].filter(Boolean);
  }

  if (process.platform === 'darwin') {
    return ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'];
  }

  return [
    process.env.CHROME_PATH,
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
  ].filter(Boolean);
}

function findChrome() {
  const chromePath = chromeCandidates().find((candidate) => fs.existsSync(candidate));
  if (!chromePath) fail('Could not find Chrome or Edge. Set CHROME_PATH to a Chromium-based browser executable.');
  return chromePath;
}

function freePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      server.close(() => resolve(address.port));
    });
  });
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (response) => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', (chunk) => {
        body += chunk;
      });
      response.on('end', () => {
        if (response.statusCode < 200 || response.statusCode >= 300) {
          reject(new Error(`${url} returned ${response.statusCode}: ${body}`));
          return;
        }
        resolve(JSON.parse(body));
      });
    }).on('error', reject);
  });
}

async function waitForChrome(port) {
  const deadline = Date.now() + 15000;
  let lastError;
  while (Date.now() < deadline) {
    try {
      return await getJson(`http://127.0.0.1:${port}/json/version`);
    } catch (error) {
      lastError = error;
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
  throw lastError || new Error('Chrome did not start');
}

async function newTarget(port) {
  const response = await fetch(`http://127.0.0.1:${port}/json/new`, { method: 'PUT' });
  if (!response.ok) throw new Error(`Could not create Chrome target: ${response.status}`);
  return response.json();
}

async function closeTarget(port, targetId) {
  await fetch(`http://127.0.0.1:${port}/json/close/${targetId}`).catch(() => {});
}

function cdpClient(webSocketDebuggerUrl) {
  const socket = new WebSocket(webSocketDebuggerUrl);
  let nextId = 1;
  const callbacks = new Map();
  const listeners = new Map();

  socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (message.id && callbacks.has(message.id)) {
      const { resolve, reject } = callbacks.get(message.id);
      callbacks.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result || {});
      return;
    }

    const eventListeners = listeners.get(message.method) || [];
    eventListeners.forEach((listener) => listener(message.params || {}));
  });

  return {
    open: () => new Promise((resolve, reject) => {
      socket.addEventListener('open', resolve, { once: true });
      socket.addEventListener('error', reject, { once: true });
    }),
    send: (method, params = {}) => new Promise((resolve, reject) => {
      const id = nextId++;
      callbacks.set(id, { resolve, reject });
      socket.send(JSON.stringify({ id, method, params }));
    }),
    once: (method) => new Promise((resolve) => {
      const eventListeners = listeners.get(method) || [];
      eventListeners.push(resolve);
      listeners.set(method, eventListeners);
    }),
    close: () => socket.close(),
  };
}

async function capturePage({ port, url, viewport, outputPath }) {
  const target = await newTarget(port);
  const client = cdpClient(target.webSocketDebuggerUrl);
  await client.open();

  await client.send('Page.enable');
  await client.send('Runtime.enable');
  await client.send('Emulation.setDeviceMetricsOverride', {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: 1,
    mobile: viewport.mobile,
  });

  const loaded = client.once('Page.loadEventFired');
  await client.send('Page.navigate', { url });
  await loaded;
  await new Promise((resolve) => setTimeout(resolve, 700));

  const screenshot = await client.send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: true,
  });
  fs.writeFileSync(outputPath, Buffer.from(screenshot.data, 'base64'));
  client.close();
  await closeTarget(port, target.id);
}

const { baseUrl, outputDir } = parseArgs(process.argv.slice(2));
fs.mkdirSync(outputDir, { recursive: true });

const chromePath = findChrome();
const port = await freePort();
const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'visual-qa-chrome-'));
const chrome = spawn(chromePath, [
  '--headless=new',
  '--disable-gpu',
  '--disable-dev-shm-usage',
  '--hide-scrollbars',
  '--no-first-run',
  '--no-default-browser-check',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${userDataDir}`,
  'about:blank',
], { stdio: 'ignore' });

let failed = false;
try {
  await waitForChrome(port);
  for (const page of PAGES) {
    const pageName = page.replace(/\.html$/, '').replace(/[^a-z0-9-]/gi, '-');
    for (const viewport of VIEWPORTS) {
      const url = new URL(page, baseUrl).toString();
      const outputPath = path.join(outputDir, `${pageName}-${viewport.name}.png`);
      console.log(`Capturing ${url} (${viewport.name}) -> ${outputPath}`);
      await capturePage({ port, url, viewport, outputPath });

      const stats = fs.statSync(outputPath);
      if (stats.size < 20000) {
        console.error(`Screenshot looks suspiciously small: ${outputPath}`);
        failed = true;
      }
    }
  }
} catch (error) {
  console.error(error.message);
  failed = true;
} finally {
  chrome.kill();
  await new Promise((resolve) => {
    chrome.once('exit', resolve);
    setTimeout(resolve, 3000);
  });
  try {
    fs.rmSync(userDataDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 250 });
  } catch (error) {
    console.warn(`Could not remove temporary Chrome profile: ${error.message}`);
  }
}

if (failed) process.exit(1);
console.log(`OK visual QA screenshots captured in ${outputDir}`);
