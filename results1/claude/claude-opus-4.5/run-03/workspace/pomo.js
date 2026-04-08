#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { homedir } from 'os';
import readline from 'readline';

const DATA_DIR = path.join(homedir(), '.pomo');
const HISTORY_FILE = path.join(DATA_DIR, 'history.json');

const DURATIONS = {
  work: 25 * 60,
  short: 5 * 60,
  long: 15 * 60,
};

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

function loadHistory() {
  ensureDataDir();
  if (fs.existsSync(HISTORY_FILE)) {
    return JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
  }
  return { sessions: [], totalMinutes: 0 };
}

function saveSession(type, duration, completed) {
  const history = loadHistory();
  history.sessions.push({
    type,
    duration,
    completed,
    timestamp: new Date().toISOString(),
  });
  if (completed && type === 'work') {
    history.totalMinutes += Math.floor(duration / 60);
  }
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = (seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function progressBar(current, total, width = 30) {
  const filled = Math.round((current / total) * width);
  const empty = width - filled;
  return `[${'█'.repeat(filled)}${'░'.repeat(empty)}]`;
}

async function runTimer(type, seconds) {
  const total = seconds;
  let remaining = seconds;
  const startTime = Date.now();

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  readline.emitKeypressEvents(process.stdin, rl);
  if (process.stdin.isTTY) process.stdin.setRawMode(true);

  let cancelled = false;

  process.stdin.on('keypress', (str, key) => {
    if (key.ctrl && key.name === 'c') {
      cancelled = true;
    }
    if (key.name === 'q') {
      cancelled = true;
    }
  });

  const typeLabel = type === 'work' ? '🍅 WORK' : type === 'short' ? '☕ SHORT BREAK' : '🌴 LONG BREAK';
  console.log(`\n${typeLabel} - ${Math.floor(total / 60)} minutes`);
  console.log('Press q or Ctrl+C to cancel\n');

  while (remaining > 0 && !cancelled) {
    const elapsed = total - remaining;
    const bar = progressBar(elapsed, total);
    process.stdout.write(`\r  ${bar} ${formatTime(remaining)} remaining  `);

    await new Promise(r => setTimeout(r, 1000));
    remaining = Math.max(0, seconds - Math.floor((Date.now() - startTime) / 1000));
  }

  if (process.stdin.isTTY) process.stdin.setRawMode(false);
  rl.close();

  if (cancelled) {
    console.log('\n\n⏹  Session cancelled');
    saveSession(type, total - remaining, false);
    return false;
  }

  console.log('\n\n✅ Session complete!');
  if (type === 'work') {
    console.log('   Time for a break!');
  } else {
    console.log('   Ready for another pomodoro?');
  }

  // Bell sound
  process.stdout.write('\x07');

  saveSession(type, total, true);
  return true;
}

function showStats() {
  const history = loadHistory();
  const today = new Date().toISOString().split('T')[0];

  const todaySessions = history.sessions.filter(s =>
    s.timestamp.startsWith(today) && s.type === 'work' && s.completed
  );

  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  const weekSessions = history.sessions.filter(s =>
    s.timestamp >= weekAgo && s.type === 'work' && s.completed
  );

  console.log('\n📊 Pomodoro Stats\n');
  console.log(`  Today:     ${todaySessions.length} pomodoros (${todaySessions.length * 25} min)`);
  console.log(`  This week: ${weekSessions.length} pomodoros (${weekSessions.length * 25} min)`);
  console.log(`  All time:  ${history.totalMinutes} minutes focused`);

  if (history.sessions.length > 0) {
    const last = history.sessions[history.sessions.length - 1];
    const lastDate = new Date(last.timestamp);
    console.log(`\n  Last session: ${lastDate.toLocaleString()}`);
  }
  console.log();
}

function showHelp() {
  console.log(`
pomo - CLI pomodoro timer

USAGE:
  pomo [command] [options]

COMMANDS:
  work, w         Start 25-minute work session (default)
  short, s        Start 5-minute break
  long, l         Start 15-minute break
  stats           Show session history
  clear           Clear all history
  help            Show this help

OPTIONS:
  --minutes, -m   Custom duration in minutes

EXAMPLES:
  pomo            Start work session
  pomo short      Take a short break
  pomo -m 45      45-minute custom session
  pomo stats      View your stats
`);
}

async function main() {
  const args = process.argv.slice(2);
  const cmd = args[0] || 'work';

  if (cmd === 'help' || cmd === '-h' || cmd === '--help') {
    showHelp();
    return;
  }

  if (cmd === 'stats') {
    showStats();
    return;
  }

  if (cmd === 'clear') {
    ensureDataDir();
    fs.writeFileSync(HISTORY_FILE, JSON.stringify({ sessions: [], totalMinutes: 0 }));
    console.log('History cleared.');
    return;
  }

  let type = 'work';
  let duration = DURATIONS.work;

  if (cmd === 'work' || cmd === 'w') {
    type = 'work';
    duration = DURATIONS.work;
  } else if (cmd === 'short' || cmd === 's') {
    type = 'short';
    duration = DURATIONS.short;
  } else if (cmd === 'long' || cmd === 'l') {
    type = 'long';
    duration = DURATIONS.long;
  }

  const minutesIdx = args.findIndex(a => a === '-m' || a === '--minutes');
  if (minutesIdx !== -1 && args[minutesIdx + 1]) {
    const m = parseInt(args[minutesIdx + 1], 10);
    if (!isNaN(m) && m > 0) {
      duration = m * 60;
    }
  }

  await runTimer(type, duration);
}

main().catch(console.error);
