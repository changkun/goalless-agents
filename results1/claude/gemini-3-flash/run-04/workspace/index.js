#!/usr/bin/env node
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const DB_PATH = join(homedir(), '.tt-tasks.json');

function loadTasks() {
  if (!existsSync(DB_PATH)) return [];
  try {
    return JSON.parse(readFileSync(DB_PATH, 'utf8'));
  } catch (e) {
    return [];
  }
}

function saveTasks(tasks) {
  writeFileSync(DB_PATH, JSON.stringify(tasks, null, 2));
}

const args = process.argv.slice(2);
const command = args[0];

const tasks = loadTasks();

switch (command) {
  case 'add':
    const text = args.slice(1).join(' ');
    if (!text) {
      console.error('Error: Task description required. Usage: tt add <task>');
      process.exit(1);
    }
    tasks.push({ id: Date.now(), text, done: false });
    saveTasks(tasks);
    console.log(`Added: "${text}"`);
    break;

  case 'ls':
    if (tasks.length === 0) {
      console.log('No tasks found.');
    } else {
      tasks.forEach((t, i) => {
        const mark = t.done ? '[x]' : '[ ]';
        console.log(`${i + 1}. ${mark} ${t.text} (id: ${t.id})`);
      });
    }
    break;

  case 'done':
    const index = parseInt(args[1], 10) - 1;
    if (tasks[index]) {
      tasks[index].done = true;
      saveTasks(tasks);
      console.log(`Completed: "${tasks[index].text}"`);
    } else {
      console.error('Error: Task not found.');
    }
    break;

  case 'rm':
    const rmIndex = parseInt(args[1], 10) - 1;
    if (tasks[rmIndex]) {
      const removed = tasks.splice(rmIndex, 1);
      saveTasks(tasks);
      console.log(`Removed: "${removed[0].text}"`);
    } else {
      console.error('Error: Task not found.');
    }
    break;

  default:
    console.log(`
Usage: tt <command> [args]

Commands:
  add <task>  Add a new task
  ls          List all tasks
  done <num>  Mark task as completed
  rm <num>    Remove task
    `);
}
