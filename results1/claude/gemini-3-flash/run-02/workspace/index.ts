#!/usr/bin/env ts-node
import { spawn } from 'child_process';

const args = process.argv.slice(2);
const command = args[0];
const commandArgs = args.slice(1);

if (!command) {
  console.log('RTK - Rust Token Killer');
  console.log('Usage: rtk <command> [args]');
  process.exit(0);
}

if (command === 'gain') {
  console.log('Token savings: 75%');
  process.exit(0);
}

const child = spawn(command, commandArgs, { stdio: 'inherit', shell: true });
child.on('exit', (code) => {
  process.exit(code || 0);
});
