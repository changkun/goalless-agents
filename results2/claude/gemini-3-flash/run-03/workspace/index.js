#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

const DB_FILE = path.join(process.cwd(), 'tasks.json');

const loadTasks = () => {
  if (!fs.existsSync(DB_FILE)) return [];
  try {
    const data = fs.readFileSync(DB_FILE, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    return [];
  }
};

const saveTasks = (tasks) => {
  fs.writeFileSync(DB_FILE, JSON.stringify(tasks, null, 2));
};

const args = process.argv.slice(2);
const command = args[0];

const usage = () => {
  console.log('Usage: task [add|list|done|remove] [args]');
  console.log('  add "Task description"');
  console.log('  list');
  console.log('  done <id>');
  console.log('  remove <id>');
};

switch (command) {
  case 'add':
    const desc = args[1];
    if (!desc) {
      console.error('Error: Task description required');
      process.exit(1);
    }
    const tasks = loadTasks();
    const newTask = {
      id: tasks.length > 0 ? tasks[tasks.length - 1].id + 1 : 1,
      description: desc,
      status: 'pending',
      createdAt: new Date().toISOString()
    };
    tasks.push(newTask);
    saveTasks(tasks);
    console.log(`Added task ${newTask.id}: ${desc}`);
    break;

  case 'list':
    const allTasks = loadTasks();
    if (allTasks.length === 0) {
      console.log('No tasks found.');
    } else {
      allTasks.forEach(t => {
        const statusIcon = t.status === 'done' ? '[x]' : '[ ]';
        console.log(`${t.id}. ${statusIcon} ${t.description}`);
      });
    }
    break;

  case 'done':
    const doneId = parseInt(args[1]);
    const tasksToDone = loadTasks();
    const task = tasksToDone.find(t => t.id === doneId);
    if (task) {
      task.status = 'done';
      saveTasks(tasksToDone);
      console.log(`Marked task ${doneId} as done.`);
    } else {
      console.error(`Error: Task ${doneId} not found.`);
    }
    break;

  case 'remove':
    const removeId = parseInt(args[1]);
    const currentTasks = loadTasks();
    const filteredTasks = currentTasks.filter(t => t.id !== removeId);
    if (currentTasks.length !== filteredTasks.length) {
      saveTasks(filteredTasks);
      console.log(`Removed task ${removeId}.`);
    } else {
      console.error(`Error: Task ${removeId} not found.`);
    }
    break;

  default:
    usage();
    break;
}
