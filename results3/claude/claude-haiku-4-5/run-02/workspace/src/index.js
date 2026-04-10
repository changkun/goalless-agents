#!/usr/bin/env node

import { initDb } from './db.js';
import {
  handleCreate,
  handleList,
  handleSearch,
  handleView,
  handleEdit,
  handleDelete,
  handleTag,
  handleTags,
  handleHelp
} from './cli.js';

initDb();

const args = process.argv.slice(2);
const command = args[0];

if (!command || command === 'help') {
  handleHelp();
} else if (command === 'list') {
  handleList();
} else if (command === 'create') {
  handleCreate(args.slice(1));
} else if (command === 'search') {
  handleSearch(args.slice(1).join(' '));
} else if (command === 'view') {
  handleView(args[1]);
} else if (command === 'edit') {
  handleEdit(args.slice(1));
} else if (command === 'delete') {
  handleDelete(args[1]);
} else if (command === 'tag') {
  handleTag(args[1]);
} else if (command === 'tags') {
  handleTags();
} else {
  console.log(`Unknown command: ${command}`);
  console.log('Run: noter help');
  process.exit(1);
}
