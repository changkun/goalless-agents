#!/usr/bin/env node

import { TaskManager } from './taskManager.js';

const manager = new TaskManager();

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    switch (command) {
      case 'add':
        if (!args[1]) throw new Error('Task title required: taskly add "Task title" [--priority high|medium|low] [--due YYYY-MM-DD]');
        await manager.addTask(args[1], {
          priority: extractFlag(args, '--priority') || 'medium',
          dueDate: extractFlag(args, '--due')
        });
        console.log('✓ Task added');
        break;

      case 'list':
      case 'ls':
        const tasks = await manager.getTasks();
        if (tasks.length === 0) {
          console.log('No tasks');
          break;
        }
        console.log('\n' + formatTaskList(tasks) + '\n');
        break;

      case 'done':
      case 'complete':
        if (!args[1]) throw new Error('Task ID required: taskly done <id>');
        await manager.completeTask(parseInt(args[1]));
        console.log('✓ Task completed');
        break;

      case 'remove':
      case 'rm':
        if (!args[1]) throw new Error('Task ID required: taskly remove <id>');
        await manager.removeTask(parseInt(args[1]));
        console.log('✓ Task removed');
        break;

      case 'clear':
        await manager.clearCompleted();
        console.log('✓ Completed tasks cleared');
        break;

      case 'edit':
        if (!args[1]) throw new Error('Task ID required: taskly edit <id> [--title "..."] [--priority high|medium|low] [--due YYYY-MM-DD]');
        const updates = {};
        const titleIndex = args.indexOf('--title');
        if (titleIndex !== -1 && titleIndex < args.length - 1) updates.title = args[titleIndex + 1];

        const priorityValue = extractFlag(args, '--priority');
        if (priorityValue) updates.priority = priorityValue;

        const dueValue = extractFlag(args, '--due');
        if (dueValue) updates.dueDate = dueValue;

        if (Object.keys(updates).length === 0) {
          throw new Error('At least one field to update is required (--title, --priority, or --due)');
        }
        await manager.editTask(parseInt(args[1]), updates);
        console.log('✓ Task updated');
        break;

      case '--help':
      case '-h':
      case 'help':
        showHelp();
        break;

      default:
        if (!command) showHelp();
        else console.error(`Unknown command: ${command}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

function extractFlag(args, flag) {
  const index = args.indexOf(flag);
  return index !== -1 && index < args.length - 1 ? args[index + 1] : null;
}

function formatTaskList(tasks) {
  const priorityColors = {
    high: '\x1b[31m',     // red
    medium: '\x1b[33m',   // yellow
    low: '\x1b[32m'       // green
  };
  const reset = '\x1b[0m';

  let output = 'Tasks:\n';
  tasks.forEach(task => {
    const status = task.completed ? '✓' : ' ';
    const priorityColor = priorityColors[task.priority] || '';
    const dueStr = task.dueDate ? ` (due: ${task.dueDate})` : '';
    const strikethrough = task.completed ? '\x1b[9m' : '';
    output += `  [${status}] ${task.id}. ${strikethrough}${priorityColor}${task.title}${reset}${dueStr}\n`;
  });
  return output;
}

function showHelp() {
  console.log(`
Taskly - A lightweight task manager

Usage:
  taskly add "Task title" [--priority high|medium|low] [--due YYYY-MM-DD]
  taskly list                                           # Show all tasks
  taskly done <id>                                      # Mark task as complete
  taskly edit <id> [--title "..."] [--priority high|medium|low] [--due YYYY-MM-DD]
  taskly remove <id>                                    # Delete a task
  taskly clear                                          # Clear completed tasks
  taskly help                                           # Show this help

Examples:
  taskly add "Buy groceries" --priority high
  taskly add "Learn Go" --priority low --due 2026-12-31
  taskly list
  taskly done 1
  taskly edit 1 --title "Buy milk" --priority high
  taskly remove 2
  `);
}

main();
