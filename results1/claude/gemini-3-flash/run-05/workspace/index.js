#!/usr/bin/env node
import fs from 'fs';
import readline from 'readline';
import { program } from 'commander';
import chalk from 'chalk';
import SingleBar from 'cli-progress';

program
  .name('log-stats')
  .description('A fast CLI tool for analyzing log files and generating statistics')
  .version('1.0.0')
  .argument('<file>', 'The log file to analyze')
  .option('-p, --pattern <regex>', 'Regex pattern for matching log entries', '^\\S+\\s+(\\S+)')
  .option('-g, --group <index>', 'Index of the capture group to use for grouping (default: 1)', '1')
  .action(async (file, options) => {
    try {
      const groupIndex = parseInt(options.group, 10);
      if (!fs.existsSync(file)) {
        console.error(chalk.red(`Error: File "${file}" does not exist.`));
        process.exit(1);
      }

      const stats = {
        totalLines: 0,
        matches: 0,
        uniqueGroups: new Map(),
        startTime: Date.now(),
      };

      const { size } = fs.statSync(file);
      const progressBar = new SingleBar.SingleBar({
        format: 'Progress |' + chalk.cyan('{bar}') + '| {percentage}% | ETA: {eta}s | {value}/{total} bytes',
        barCompleteChar: '\u2588',
        barIncompleteChar: '\u2591',
        hideCursor: true,
      });

      console.log(chalk.blue(`Analyzing: ${file} (${(size / (1024 * 1024)).toFixed(2)} MB)`));
      progressBar.start(size, 0);

      const stream = fs.createReadStream(file);
      const rl = readline.createInterface({
        input: stream,
        terminal: false,
      });

      const pattern = new RegExp(options.pattern);

      let bytesProcessed = 0;
      for await (const line of rl) {
        stats.totalLines++;
        bytesProcessed += Buffer.byteLength(line) + 1; // +1 for newline character
        progressBar.update(Math.min(bytesProcessed, size));

        const match = line.match(pattern);
        if (match) {
          stats.matches++;
          // Use specified capture group, fallback to first group or full match
          const key = match[groupIndex] || match[0];
          stats.uniqueGroups.set(key, (stats.uniqueGroups.get(key) || 0) + 1);
        }
      }

      progressBar.stop();
      const duration = (Date.now() - stats.startTime) / 1000;

      console.log('\n' + chalk.green.bold('Analysis Results:'));
      console.log(`- Total Lines: ${chalk.yellow(stats.totalLines)}`);
      console.log(`- Matches:     ${chalk.yellow(stats.matches)} (${((stats.matches / stats.totalLines) * 100).toFixed(2)}%)`);
      console.log(`- Duration:    ${chalk.yellow(duration.toFixed(2))}s (${(stats.totalLines / duration).toFixed(0)} lines/sec)`);

      console.log('\n' + chalk.blue.bold('Top 10 Occurrences:'));
      const sorted = [...stats.uniqueGroups.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

      sorted.forEach(([key, count]) => {
        const barLength = Math.round((count / stats.matches) * 50);
        const bar = chalk.cyan('█'.repeat(barLength));
        console.log(`${key.padEnd(20)} | ${count.toString().padStart(8)} | ${bar}`);
      });

    } catch (err) {
      console.error(chalk.red(`Fatal Error: ${err.message}`));
      process.exit(1);
    }
  });

program.parse();
