#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const logFile = path.join(process.cwd(), 'sample.log');
const stream = fs.createWriteStream(logFile);

const logTypes = ['INFO', 'WARN', 'ERROR', 'DEBUG'];
const services = ['auth-svc', 'billing-api', 'web-gateway', 'db-worker'];
const numLines = 1_000_000;

console.log(`Generating ${numLines.toLocaleString()} log lines to ${logFile}...`);

for (let i = 0; i < numLines; i++) {
  const now = new Date().toISOString();
  const level = logTypes[Math.floor(Math.random() * logTypes.length)];
  const svc = services[Math.floor(Math.random() * services.length)];
  const msg = `Random log message ${Math.random().toString(36).substring(7)}`;

  if (!stream.write(`${now} ${level} [${svc}] ${msg}\n`)) {
    await new Promise(resolve => stream.once('drain', resolve));
  }

  if (i % 100_000 === 0 && i > 0) {
    console.log(`- Progress: ${i.toLocaleString()} lines written`);
  }
}

stream.end(() => {
  console.log('Done generating logs.');
});
