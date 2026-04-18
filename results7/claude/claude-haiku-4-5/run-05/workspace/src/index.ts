import { TaskManager } from './manager.js';
import { formatDuration, formatTime } from './format.js';
import chalk from 'chalk';

const manager = new TaskManager();
const command = process.argv[2];
const args = process.argv.slice(3);

function showHelp(): void {
  console.log(`
${chalk.bold('Task Timer CLI')}

${chalk.cyan('Commands:')}
  start <name>      Start a new task
  stop              Stop the currently running task
  status            Show the currently running task
  stats             Show statistics for all tasks
  list              Show all completed sessions
  help              Show this help message
`);
}

function printHeader(text: string): void {
  console.log(`\n${chalk.bold.blue(text)}`);
}

function printSuccess(text: string): void {
  console.log(chalk.green(`✓ ${text}`));
}

function printInfo(text: string): void {
  console.log(chalk.cyan(`ℹ ${text}`));
}

async function main(): Promise<void> {
  try {
    switch (command) {
      case 'start': {
        const taskName = args.join(' ');
        if (!taskName) {
          console.error(chalk.red('Error: Task name required'));
          process.exit(1);
        }
        const id = manager.start(taskName);
        printSuccess(`Started task: ${chalk.yellow(taskName)}`);
        printInfo(`Task ID: ${id}`);
        break;
      }

      case 'stop': {
        const session = manager.stop();
        printSuccess(`Stopped task: ${chalk.yellow(session.taskName)}`);
        printInfo(`Duration: ${chalk.yellow(formatDuration(session.duration || 0))}`);
        break;
      }

      case 'status': {
        const active = manager.getActive();
        if (!active) {
          printInfo('No task is currently running');
          break;
        }
        const elapsed = Date.now() - active.startTime;
        printHeader('Active Task');
        console.log(`  Name:    ${chalk.yellow(active.taskName)}`);
        console.log(`  Started: ${formatTime(active.startTime)}`);
        console.log(`  Elapsed: ${chalk.cyan(formatDuration(elapsed))}`);
        break;
      }

      case 'stats': {
        const stats = manager.getStats();
        if (Object.keys(stats).length === 0) {
          printInfo('No completed tasks yet');
          break;
        }
        printHeader('Task Statistics');
        const sorted = Object.entries(stats).sort((a, b) => b[1].totalTime - a[1].totalTime);
        for (const [name, data] of sorted) {
          console.log(`\n  ${chalk.yellow(name)}`);
          console.log(`    Sessions: ${chalk.cyan(data.count)}`);
          console.log(`    Total:    ${chalk.cyan(formatDuration(data.totalTime))}`);
          console.log(`    Average:  ${chalk.cyan(formatDuration(data.avgTime))}`);
        }
        break;
      }

      case 'list': {
        const sessions = manager.getAllSessions();
        if (sessions.length === 0) {
          printInfo('No sessions recorded');
          break;
        }
        printHeader('All Sessions');
        for (const session of sessions.slice(-10)) {
          const status = session.duration ? chalk.green('✓') : chalk.yellow('⏱');
          const duration = session.duration ? formatDuration(session.duration) : 'ongoing';
          console.log(`  ${status} ${chalk.yellow(session.taskName)} - ${chalk.gray(duration)}`);
        }
        if (sessions.length > 10) {
          console.log(chalk.gray(`  ... and ${sessions.length - 10} more`));
        }
        break;
      }

      case 'help':
      case '--help':
      case '-h':
        showHelp();
        break;

      default:
        if (!command) {
          showHelp();
        } else {
          console.error(chalk.red(`Unknown command: ${command}`));
          process.exit(1);
        }
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error(chalk.red(`Error: ${error.message}`));
    }
    process.exit(1);
  }
}

main();
