#!/usr/bin/env node
import { checkFiles } from '../lib/checker.js';
import { parseArgs } from 'node:util';
import { glob } from '../lib/glob.js';

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    help: { type: 'boolean', short: 'h' },
    timeout: { type: 'string', short: 't', default: '5000' },
    concurrent: { type: 'string', short: 'c', default: '10' },
    verbose: { type: 'boolean', short: 'v' },
  }
});

if (values.help || positionals.length === 0) {
  console.log(`mdcheck - Markdown link checker

Usage: mdcheck [options] <files...>

Options:
  -h, --help        Show this help
  -t, --timeout     Request timeout in ms (default: 5000)
  -c, --concurrent  Max concurrent requests (default: 10)
  -v, --verbose     Show all links, not just broken

Examples:
  mdcheck README.md
  mdcheck "docs/**/*.md"
  mdcheck *.md --verbose`);
  process.exit(0);
}

const files = await glob(positionals);
if (files.length === 0) {
  console.error('No files found matching pattern(s)');
  process.exit(1);
}

const opts = {
  timeout: parseInt(values.timeout, 10),
  concurrent: parseInt(values.concurrent, 10),
  verbose: values.verbose,
};

const exitCode = await checkFiles(files, opts);
process.exit(exitCode);
