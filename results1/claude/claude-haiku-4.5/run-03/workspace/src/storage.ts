import fs from 'fs';
import path from 'path';
import { TaskStore, Task } from './types';

const DATA_DIR = path.join(process.env.HOME || '/tmp', '.taskman');
const STORAGE_FILE = path.join(DATA_DIR, 'tasks.json');

export function ensureStorageDir(): void {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

export function loadTasks(): Task[] {
  ensureStorageDir();
  if (!fs.existsSync(STORAGE_FILE)) {
    return [];
  }
  try {
    const data = fs.readFileSync(STORAGE_FILE, 'utf-8');
    const store: TaskStore = JSON.parse(data);
    return store.tasks || [];
  } catch {
    return [];
  }
}

export function saveTasks(tasks: Task[]): void {
  ensureStorageDir();
  const store: TaskStore = { tasks };
  fs.writeFileSync(STORAGE_FILE, JSON.stringify(store, null, 2));
}

export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
