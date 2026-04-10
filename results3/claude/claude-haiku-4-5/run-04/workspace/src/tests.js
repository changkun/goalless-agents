import test from 'node:test';
import assert from 'node:assert';
import { TaskManager } from './taskManager.js';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';

// Create a temporary test directory for tasks
const testDir = path.join(os.tmpdir(), `taskly-test-${Date.now()}`);
await fs.mkdir(testDir, { recursive: true, force: true });

// Mock TASKS_FILE by creating a custom TaskManager for testing
class TestTaskManager extends TaskManager {
  constructor(testFilePath) {
    super();
    this.testFilePath = testFilePath;
  }

  async loadTasks() {
    try {
      const data = await fs.readFile(this.testFilePath, 'utf-8');
      return JSON.parse(data);
    } catch {
      return [];
    }
  }

  async saveTasks(tasks) {
    await fs.mkdir(path.dirname(this.testFilePath), { recursive: true });
    await fs.writeFile(this.testFilePath, JSON.stringify(tasks, null, 2), 'utf-8');
  }
}

test('TaskManager - add task', async () => {
  const testFile = path.join(testDir, 'test1.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Buy milk', { priority: 'high' });
  const tasks = await manager.loadTasks();

  assert.strictEqual(tasks.length, 1);
  assert.strictEqual(tasks[0].title, 'Buy milk');
  assert.strictEqual(tasks[0].priority, 'high');
  assert.strictEqual(tasks[0].completed, false);
});

test('TaskManager - add multiple tasks with sequential IDs', async () => {
  const testFile = path.join(testDir, 'test2.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task 1');
  await manager.addTask('Task 2');
  await manager.addTask('Task 3');

  const tasks = await manager.getTasks();
  assert.strictEqual(tasks.length, 3);
  assert.strictEqual(tasks[0].id, 1);
  assert.strictEqual(tasks[1].id, 2);
  assert.strictEqual(tasks[2].id, 3);
});

test('TaskManager - complete task', async () => {
  const testFile = path.join(testDir, 'test3.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Buy milk');
  await manager.completeTask(1);

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks[0].completed, true);
  assert.ok(tasks[0].completedAt);
});

test('TaskManager - remove task', async () => {
  const testFile = path.join(testDir, 'test4.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task 1');
  await manager.addTask('Task 2');
  await manager.removeTask(1);

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks.length, 1);
  assert.strictEqual(tasks[0].id, 2);
});

test('TaskManager - clear completed tasks', async () => {
  const testFile = path.join(testDir, 'test5.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task 1');
  await manager.addTask('Task 2');
  await manager.addTask('Task 3');
  await manager.completeTask(1);
  await manager.completeTask(3);

  await manager.clearCompleted();
  const tasks = await manager.loadTasks();

  assert.strictEqual(tasks.length, 1);
  assert.strictEqual(tasks[0].id, 2);
});

test('TaskManager - sort by priority', async () => {
  const testFile = path.join(testDir, 'test6.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Low priority', { priority: 'low' });
  await manager.addTask('High priority', { priority: 'high' });
  await manager.addTask('Medium priority', { priority: 'medium' });

  const tasks = await manager.getTasks();

  assert.strictEqual(tasks[0].priority, 'high');
  assert.strictEqual(tasks[1].priority, 'medium');
  assert.strictEqual(tasks[2].priority, 'low');
});

test('TaskManager - with due date', async () => {
  const testFile = path.join(testDir, 'test7.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Project deadline', { dueDate: '2026-12-31' });
  const tasks = await manager.loadTasks();

  assert.strictEqual(tasks[0].dueDate, '2026-12-31');
});

test('TaskManager - error on invalid priority', async () => {
  const testFile = path.join(testDir, 'test8.json');
  const manager = new TestTaskManager(testFile);

  await assert.rejects(
    () => manager.addTask('Task', { priority: 'urgent' }),
    /Invalid priority/
  );
});

test('TaskManager - error on removing non-existent task', async () => {
  const testFile = path.join(testDir, 'test9.json');
  const manager = new TestTaskManager(testFile);

  await assert.rejects(
    () => manager.removeTask(999),
    /not found/
  );
});

test('TaskManager - edit task title', async () => {
  const testFile = path.join(testDir, 'test10.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Old title');
  await manager.editTask(1, { title: 'New title' });

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks[0].title, 'New title');
});

test('TaskManager - edit task priority', async () => {
  const testFile = path.join(testDir, 'test11.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task', { priority: 'low' });
  await manager.editTask(1, { priority: 'high' });

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks[0].priority, 'high');
});

test('TaskManager - edit task due date', async () => {
  const testFile = path.join(testDir, 'test12.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task');
  await manager.editTask(1, { dueDate: '2026-06-15' });

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks[0].dueDate, '2026-06-15');
});

test('TaskManager - edit multiple task fields', async () => {
  const testFile = path.join(testDir, 'test13.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Old title', { priority: 'low' });
  await manager.editTask(1, { title: 'New title', priority: 'high', dueDate: '2026-12-25' });

  const tasks = await manager.loadTasks();
  assert.strictEqual(tasks[0].title, 'New title');
  assert.strictEqual(tasks[0].priority, 'high');
  assert.strictEqual(tasks[0].dueDate, '2026-12-25');
});

test('TaskManager - error on editing non-existent task', async () => {
  const testFile = path.join(testDir, 'test14.json');
  const manager = new TestTaskManager(testFile);

  await assert.rejects(
    () => manager.editTask(999, { title: 'New title' }),
    /not found/
  );
});

test('TaskManager - error on editing with invalid priority', async () => {
  const testFile = path.join(testDir, 'test15.json');
  const manager = new TestTaskManager(testFile);

  await manager.addTask('Task', { priority: 'high' });

  await assert.rejects(
    () => manager.editTask(1, { priority: 'invalid' }),
    /Invalid priority/
  );
});

// Cleanup (with delay to ensure tests complete)
setTimeout(async () => {
  await fs.rm(testDir, { recursive: true, force: true }).catch(() => {});
}, 100);
