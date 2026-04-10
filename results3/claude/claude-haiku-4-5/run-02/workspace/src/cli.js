import chalk from 'chalk';
import {
  addNote,
  getAllNotes,
  searchNotes,
  deleteNote,
  getNoteById,
  updateNote,
  getNotesByTag,
  getAllTags
} from './db.js';
import readline from 'readline';

function formatNote(note) {
  const date = new Date(note.created_at).toLocaleString();
  const tags = note.tags ? note.tags.split(',').filter(t => t.trim()) : [];
  const tagStr = tags.length > 0 ? chalk.dim(`[${tags.join(', ')}]`) : '';

  return `
${chalk.bold.cyan(`#${note.id}`)} ${chalk.yellow(note.title)} ${chalk.dim(date)} ${tagStr}
${chalk.gray('─'.repeat(60))}
${note.content}
`;
}

export function handleCreate(args) {
  if (args.length < 2) {
    console.log(chalk.red('Error: noter create <title> <content> [tags...]'));
    process.exit(1);
  }

  const title = args[0];
  const content = args[1];
  const tags = args.slice(2);

  const id = addNote(title, content, tags);
  console.log(chalk.green(`✓ Note created with ID ${id}`));
}

export function handleList() {
  const notes = getAllNotes();
  if (notes.length === 0) {
    console.log(chalk.dim('No notes yet. Create one with: noter create "title" "content"'));
    return;
  }

  console.log(chalk.bold(`\n${notes.length} notes:\n`));
  notes.forEach(note => {
    console.log(formatNote(note));
  });
}

export function handleSearch(query) {
  if (!query) {
    console.log(chalk.red('Error: noter search <query>'));
    process.exit(1);
  }

  const results = searchNotes(query);
  if (results.length === 0) {
    console.log(chalk.dim(`No notes match "${query}"`));
    return;
  }

  console.log(chalk.bold(`\n${results.length} result(s) for "${query}":\n`));
  results.forEach(note => {
    console.log(formatNote(note));
  });
}

export function handleView(id) {
  const note = getNoteById(id);
  if (!note) {
    console.log(chalk.red(`Note #${id} not found`));
    process.exit(1);
  }
  console.log(formatNote(note));
}

export function handleDelete(id) {
  const note = getNoteById(id);
  if (!note) {
    console.log(chalk.red(`Note #${id} not found`));
    process.exit(1);
  }

  deleteNote(id);
  console.log(chalk.green(`✓ Note #${id} deleted`));
}

export function handleEdit(args) {
  if (args.length < 1) {
    console.log(chalk.red('Error: noter edit <id> [title] [content] [tags...]'));
    console.log(chalk.dim('Interactive mode: noter edit <id>'));
    process.exit(1);
  }

  const id = args[0];
  const note = getNoteById(id);
  if (!note) {
    console.log(chalk.red(`Note #${id} not found`));
    process.exit(1);
  }

  if (args.length > 1) {
    // Direct edit mode
    const title = args[1] || note.title;
    const content = args[2] || note.content;
    const tags = args.slice(3).length > 0 ? args.slice(3) : (note.tags ? note.tags.split(',') : []);

    updateNote(id, title, content, tags);
    console.log(chalk.green(`✓ Note #${id} updated`));
  } else {
    // Interactive mode
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log(chalk.cyan(`\nEditing note #${id}:`));
    console.log(chalk.gray('(Press Enter to keep current value)\n'));

    rl.question(`Title [${note.title}]: `, (title) => {
      rl.question(`Content [${note.content}]: `, (content) => {
        rl.question(`Tags [${note.tags || 'none'}]: `, (tags) => {
          const finalTitle = title || note.title;
          const finalContent = content || note.content;
          const finalTags = tags ? tags.split(/\s+/).filter(t => t.trim()) : (note.tags ? note.tags.split(',') : []);

          updateNote(id, finalTitle, finalContent, finalTags);
          console.log(chalk.green(`\n✓ Note #${id} updated`));
          rl.close();
        });
      });
    });
  }
}

export function handleTag(tag) {
  const notes = getNotesByTag(tag);
  if (notes.length === 0) {
    console.log(chalk.dim(`No notes with tag "${tag}"`));
    return;
  }

  console.log(chalk.bold(`\n${notes.length} note(s) tagged "${tag}":\n`));
  notes.forEach(note => {
    console.log(formatNote(note));
  });
}

export function handleTags() {
  const tags = getAllTags();
  if (tags.length === 0) {
    console.log(chalk.dim('No tags yet'));
    return;
  }

  console.log(chalk.bold(`\n${tags.length} tags:\n`));
  tags.forEach(tag => {
    const notes = getNotesByTag(tag);
    console.log(chalk.cyan(`  ${tag}`), chalk.dim(`(${notes.length} note${notes.length !== 1 ? 's' : ''})`));
  });
  console.log();
}

export function handleHelp() {
  console.log(chalk.bold.cyan(`
  noter - CLI Note Manager

${chalk.bold('Commands:')}
  create <title> <content> [tags...]    Create a new note
  list                                  List all notes
  search <query>                        Search notes (title, content, tags)
  view <id>                             View a specific note
  edit <id> [title] [content] [tags...] Edit a note (interactive if no args given)
  delete <id>                           Delete a note
  tag <name>                            View notes with a tag
  tags                                  List all tags
  help                                  Show this help

${chalk.bold('Examples:')}
  noter create "Shopping" "milk, eggs" grocery
  noter edit 1 "New title" "new content" work
  noter edit 1                          (interactive mode)
  noter search "milk"
  noter tag grocery
  noter delete 1
`));
}
