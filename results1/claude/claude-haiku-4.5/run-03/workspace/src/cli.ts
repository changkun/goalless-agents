import yargs from 'yargs/yargs';
import chalk from 'chalk';
import { Task } from './types';
import { loadTasks, saveTasks, generateId } from './storage';

function formatTask(task: Task): string {
  const status = task.completed ? chalk.green('✓') : chalk.gray('○');
  const priorityColor =
    task.priority === 'high'
      ? chalk.red
      : task.priority === 'medium'
        ? chalk.yellow
        : chalk.gray;
  const due = task.due ? ` [due: ${task.due}]` : '';
  return `${status} [${priorityColor(task.priority[0].toUpperCase())}] ${task.title}${due}`;
}

const argv = yargs(process.argv.slice(2))
  .command(
    'add <title>',
    'Add a new task',
    (yargs) =>
      yargs
        .positional('title', { type: 'string', describe: 'Task title' })
        .option('description', { type: 'string', alias: 'd', describe: 'Task description' })
        .option('priority', {
          type: 'string',
          alias: 'p',
          default: 'medium',
          choices: ['low', 'medium', 'high'],
          describe: 'Task priority',
        })
        .option('due', { type: 'string', alias: 'u', describe: 'Due date (YYYY-MM-DD)' }),
    (argv: any) => {
      const tasks = loadTasks();
      const newTask: Task = {
        id: generateId(),
        title: argv.title as string,
        description: argv.description as string | undefined,
        completed: false,
        priority: (argv.priority as 'low' | 'medium' | 'high') || 'medium',
        created: new Date().toISOString(),
        due: argv.due as string | undefined,
      };
      tasks.push(newTask);
      saveTasks(tasks);
      console.log(chalk.green('✓ Task added'));
    }
  )
  .command(
    'list',
    'List all tasks',
    (yargs) => yargs.option('all', { type: 'boolean', describe: 'Show completed tasks' }),
    (argv) => {
      const tasks = loadTasks();
      const filtered = argv.all ? tasks : tasks.filter((t) => !t.completed);
      if (filtered.length === 0) {
        console.log(chalk.gray('No tasks'));
        return;
      }
      filtered.forEach((task) => console.log(formatTask(task)));
    }
  )
  .command(
    'complete <id>',
    'Mark a task as complete',
    (yargs) => yargs.positional('id', { type: 'number', describe: 'Task index' }),
    (argv: any) => {
      const tasks = loadTasks();
      const id = argv.id as number;
      if (id < 0 || id >= tasks.length) {
        console.error(chalk.red('Invalid task index'));
        return;
      }
      tasks[id].completed = true;
      saveTasks(tasks);
      console.log(chalk.green('✓ Task completed'));
    }
  )
  .command(
    'delete <id>',
    'Delete a task',
    (yargs) => yargs.positional('id', { type: 'number', describe: 'Task index' }),
    (argv: any) => {
      const tasks = loadTasks();
      const id = argv.id as number;
      if (id < 0 || id >= tasks.length) {
        console.error(chalk.red('Invalid task index'));
        return;
      }
      tasks.splice(id, 1);
      saveTasks(tasks);
      console.log(chalk.green('✓ Task deleted'));
    }
  )
  .command(
    'clear',
    'Clear all completed tasks',
    {},
    () => {
      const tasks = loadTasks();
      const remaining = tasks.filter((t) => !t.completed);
      saveTasks(remaining);
      console.log(chalk.green('✓ Cleared completed tasks'));
    }
  )
  .help()
  .alias('h', 'help')
  .alias('v', 'version')
  .strict();

export default argv;
