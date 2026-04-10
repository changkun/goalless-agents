#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { reviewCode } from './reviewer.js';
import { reviewGitDiff } from './diff-reviewer.js';
import { formatAsJSON, formatAsText } from './formatter.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    printHelp();
    process.exit(0);
  }

  // Parse flags
  const jsonOutput = args.includes('--json');
  const isDiff = args.includes('--diff');
  const filePath = args.find(arg => !arg.startsWith('--'));

  try {
    if (isDiff) {
      const review = await reviewGitDiff();
      if (jsonOutput) {
        const output = await formatAsJSON(review, null, true);
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log(formatAsText(review, 'DIFF REVIEW'));
      }
    } else if (filePath) {
      if (!fs.existsSync(filePath)) {
        console.error(`Error: File not found: ${filePath}`);
        process.exit(1);
      }

      const content = fs.readFileSync(filePath, 'utf-8');
      const review = await reviewCode(content, filePath);
      if (jsonOutput) {
        const output = await formatAsJSON(review, filePath, false);
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log(formatAsText(review, 'CODE REVIEW'));
      }
    } else {
      console.error('Error: No file or mode specified');
      printHelp();
      process.exit(1);
    }
  } catch (error) {
    if (error.message.includes('API key')) {
      console.error('Error: ANTHROPIC_API_KEY environment variable not set');
      process.exit(1);
    }
    console.error('Error:', error.message);
    process.exit(1);
  }
}

function printHelp() {
  console.log(`
Claude Code Reviewer - AI-powered code review assistant

Usage:
  reviewer <file>              Review a specific file
  reviewer --diff              Review changes in current git repo
  reviewer --help              Show this help message

Options:
  --json                       Output review as JSON for programmatic access
  --diff                       Review git diff instead of a file

Examples:
  reviewer app.js              Review a JavaScript file
  reviewer src/utils.py        Review a Python file
  reviewer main.go             Review a Go file
  reviewer --diff              Review git diff of current changes
  reviewer app.js --json       Get review output as JSON
  reviewer --diff --json       Get diff review as JSON

Environment:
  ANTHROPIC_API_KEY - Required. Your Anthropic API key

The tool will analyze the code and provide constructive feedback on:
  - Code quality and readability
  - Potential bugs or issues
  - Performance considerations
  - Best practices
  - Security concerns
`);
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
