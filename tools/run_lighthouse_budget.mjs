#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const args = process.argv.slice(2);
const url = args.find((arg) => !arg.startsWith('--')) || 'http://localhost:8000/index.html';
const minIndex = args.indexOf('--min');
const minScore = minIndex >= 0 ? Number(args[minIndex + 1]) : 90;
const reportDir = path.resolve('.lighthouse');
const reportPath = path.join(reportDir, 'homepage.json');
const npxCommand = process.platform === 'win32' ? 'npx.cmd' : 'npx';

if (!Number.isFinite(minScore) || minScore < 0 || minScore > 100) {
  console.error(`Invalid --min score: ${args[minIndex + 1]}`);
  process.exit(1);
}

fs.mkdirSync(reportDir, { recursive: true });

const lighthouse = spawnSync(
  npxCommand,
  [
    '--yes',
    'lighthouse@latest',
    url,
    '--quiet',
    '--chrome-flags=--headless=new --no-sandbox',
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
