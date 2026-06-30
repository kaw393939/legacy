#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const DEFAULT_URL = 'http://localhost:8000/index.html';

function fail(message) {
  console.error(message);
  process.exit(1);
}

function nextValue(args, index, option) {
  const value = args[index + 1];
  if (!value || value.startsWith('--')) {
    fail(`Missing value for ${option}`);
  }
  return value;
}

function parseArgs(args) {
  let url = DEFAULT_URL;
  let hasUrl = false;
  let minScore = 90;

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];

    if (arg === '--help' || arg === '-h') {
      console.log('Usage: node tools/run_lighthouse_budget.mjs [url] [--url url] [--min score]');
      process.exit(0);
    }

    if (arg === '--min') {
      minScore = Number(nextValue(args, index, arg));
      index += 1;
      continue;
    }

    if (arg === '--url') {
      url = nextValue(args, index, arg);
      hasUrl = true;
      index += 1;
      continue;
    }

    if (arg.startsWith('--')) {
      fail(`Unknown option: ${arg}`);
    }

    if (hasUrl) {
      fail(`Unexpected extra URL: ${arg}`);
    }

    url = arg;
    hasUrl = true;
  }

  return { url, minScore };
}

const { url, minScore } = parseArgs(process.argv.slice(2));
const reportDir = path.resolve('.lighthouse');
const reportPath = path.join(reportDir, 'homepage.json');
const npxCommand = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const lighthousePackage = process.env.LIGHTHOUSE_PACKAGE || 'lighthouse@13.4.0';

if (!Number.isFinite(minScore) || minScore < 0 || minScore > 100) {
  fail(`Invalid --min score: ${minScore}`);
}

fs.mkdirSync(reportDir, { recursive: true });

const lighthouse = spawnSync(
  npxCommand,
  [
    '--yes',
    lighthousePackage,
    url,
    '--quiet',
    '--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage',
    '--only-categories=performance,accessibility,best-practices,seo',
    '--output=json',
    `--output-path=${reportPath}`,
  ],
  { stdio: 'inherit', shell: process.platform === 'win32' },
);

if (lighthouse.error) {
  console.error(`Failed to start Lighthouse: ${lighthouse.error.message}`);
  process.exit(1);
}

if (lighthouse.status !== 0) {
  process.exit(lighthouse.status ?? 1);
}

const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
const categories = Object.entries(report.categories).map(([key, value]) => ({
  key,
  title: value.title,
  score: Math.round(value.score * 100),
}));

let failed = false;
for (const category of categories) {
  const line = `${category.title}: ${category.score}`;
  if (category.score < minScore) {
    console.error(`${line} below required ${minScore}`);
    failed = true;
  } else {
    console.log(line);
  }
}

if (failed) {
  process.exit(1);
}

console.log(`OK Lighthouse budgets passed at ${minScore}+`);
