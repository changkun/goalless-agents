import { initDb, addNote, getAllNotes, searchNotes, getNotesByTag, deleteNote } from './db.js';
import chalk from 'chalk';

console.log(chalk.bold.cyan('\n🧪 Running noter tests...\n'));

initDb();

// Test 1: Create notes
console.log(chalk.bold('Test 1: Creating notes'));
const id1 = addNote('JavaScript Tips', 'Use const for immutability', ['javascript', 'tips']);
const id2 = addNote('Database Design', 'Normalize your schemas', ['database', 'design']);
const id3 = addNote('JavaScript Performance', 'Optimize your loops', ['javascript', 'performance']);
console.log(chalk.green('✓ Created 3 notes\n'));

// Test 2: List all notes
console.log(chalk.bold('Test 2: Listing all notes'));
const allNotes = getAllNotes();
console.log(chalk.green(`✓ Found ${allNotes.length} notes\n`));

// Test 3: Search by content
console.log(chalk.bold('Test 3: Search for "javascript"'));
const jsNotes = searchNotes('javascript');
console.log(chalk.green(`✓ Found ${jsNotes.length} notes matching "javascript"\n`));

// Test 4: Search by tag
console.log(chalk.bold('Test 4: Get notes by tag "javascript"'));
const tagNotes = getNotesByTag('javascript');
console.log(chalk.green(`✓ Found ${tagNotes.length} notes with tag "javascript"\n`));

// Test 5: Delete a note
console.log(chalk.bold('Test 5: Delete note'));
deleteNote(id1);
const afterDelete = getAllNotes();
console.log(chalk.green(`✓ Deleted note, ${afterDelete.length} notes remaining\n`));

console.log(chalk.bold.green('✨ All tests passed!\n'));
