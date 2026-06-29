#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || 'docs');
const siteBasePath = '/legacy/';
const failures = [];
const warnings = [];

function listFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name);
    return entry.isDirectory() ? listFiles(fullPath) : [fullPath];
  });
}

function normalizeTarget(pageFile, rawValue) {
  const withoutHash = rawValue.split('#')[0];
  const withoutQuery = withoutHash.split('?')[0];

  if (!withoutQuery) return pageFile;

  if (withoutQuery.startsWith('/')) {
    if (!withoutQuery.startsWith(siteBasePath)) {
      failures.push(`${pageFile}: root-relative asset/link is not safe for GitHub Pages subpaths: ${rawValue}`);
      return null;
    }
    return withoutQuery.slice(siteBasePath.length) || 'index.html';
  }

  return path.posix.normalize(path.posix.join(path.posix.dirname(pageFile), withoutQuery));
}

function isExternal(rawValue) {
  return /^(?:https?:|mailto:|tel:|data:|javascript:)/i.test(rawValue);
}

if (!fs.existsSync(root)) {
  console.error(`Output directory does not exist: ${root}`);
  process.exit(1);
}

const allFiles = listFiles(root);
const existing = new Set(allFiles.map((file) => path.relative(root, file).split(path.sep).join('/')));
const htmlFiles = allFiles
  .filter((file) => file.endsWith('.html'))
  .map((file) => path.relative(root, file).split(path.sep).join('/'))
  .sort();

if (htmlFiles.length === 0) {
  failures.push('No generated HTML files found');
}

for (const pageFile of htmlFiles) {
  const html = fs.readFileSync(path.join(root, pageFile), 'utf8');

  for (const match of html.matchAll(/\b(?:href|src)=["']([^"']*)["']/gi)) {
    const rawValue = match[1].trim();

    if (!rawValue) {
      failures.push(`${pageFile}: empty ${match[0]}`);
      continue;
    }

    if (rawValue === '#') {
      failures.push(`${pageFile}: placeholder link href="#"`);
      continue;
    }

    if (isExternal(rawValue)) continue;
    if (rawValue.startsWith('#')) continue;

    const target = normalizeTarget(pageFile, rawValue);
    if (!target) continue;

    if (!existing.has(target)) {
      failures.push(`${pageFile}: missing local target ${rawValue} -> ${target}`);
    }
  }

  const titleMatch = html.match(/<title>(.*?)<\/title>/is);
  if (!titleMatch || !titleMatch[1].trim()) {
    failures.push(`${pageFile}: missing document title`);
  }

  const descriptionMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']*)["']/i);
  if (!descriptionMatch || !descriptionMatch[1].trim()) {
    failures.push(`${pageFile}: missing meta description`);
  } else if (descriptionMatch[1].length > 160) {
    warnings.push(`${pageFile}: meta description is ${descriptionMatch[1].length} characters`);
  }
}

for (const warning of warnings) {
  console.warn(`WARNING: ${warning}`);
}

if (failures.length > 0) {
  console.error('Generated site integrity check failed:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`OK generated site integrity passed: ${htmlFiles.length} pages`);
