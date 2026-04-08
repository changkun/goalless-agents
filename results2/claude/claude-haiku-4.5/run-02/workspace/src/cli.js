#!/usr/bin/env node

import { generateStandupFromGit } from './index.js';

async function main() {
  const args = process.argv.slice(2);
  let commitLimit = 10;

  // Parse --limit argument
  const limitIndex = args.indexOf('--limit');
  if (limitIndex !== -1 && args[limitIndex + 1]) {
    commitLimit = parseInt(args[limitIndex + 1], 10);
    if (isNaN(commitLimit) || commitLimit < 1) {
      console.error('Error: --limit must be a positive number');
      process.exit(1);
    }
  }

  // Check for help
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
standup - Generate daily standup summaries from git commits

USAGE:
  standup [OPTIONS]

OPTIONS:
  --limit N       Number of recent commits to summarize (default: 10)
  --help, -h      Show this help message

EXAMPLES:
  standup                    # Summarize last 10 commits
  standup --limit 20         # Summarize last 20 commits

REQUIRED:
  Set ANTHROPIC_API_KEY environment variable with your Claude API key.
    `);
    process.exit(0);
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable is not set');
    process.exit(1);
  }

  try {
    console.log(
      `Generating standup from your last ${commitLimit} commits...\n`
    );
    const { commits, summary } = await generateStandupFromGit(commitLimit);

    console.log('📝 Recent Commits:');
    commits.forEach(commit => console.log(`   ${commit}`));

    console.log('\n🎯 Standup Summary:\n');
    console.log(summary);
    console.log('');
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
