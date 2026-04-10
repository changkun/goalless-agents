import fs from 'fs/promises';
import path from 'path';
import os from 'os';

const TASKS_FILE = path.join(os.homedir(), '.taskly_tasks.json');

export class TaskManager {
  async loadTasks() {
    try {
      const data = await fs.readFile(TASKS_FILE, 'utf-8');
      return JSON.parse(data);
    } catch {
      return [];
    }
  }

  async saveTasks(tasks) {
    await fs.writeFile(TASKS_FILE, JSON.stringify(tasks, null, 2), 'utf-8');
  }

  async addTask(title, { priority = 'medium', dueDate = null } = {}) {
    const tasks = await this.loadTasks();
    const id = tasks.length > 0 ? Math.max(...tasks.map(t => t.id)) + 1 : 1;

    tasks.push({
      id,
      title,
      priority: validatePriority(priority),
      dueDate,
      completed: false,
      createdAt: new Date().toISOString()
    });

    await this.saveTasks(tasks);
  }

  async getTasks(filter = {}) {
    const tasks = await this.loadTasks();

    let filtered = tasks;
    if (filter.completed !== undefined) {
      filtered = filtered.filter(t => t.completed === filter.completed);
    }
    if (filter.priority) {
      filtered = filtered.filter(t => t.priority === filter.priority);
    }

    return filtered.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const aPriority = priorityOrder[a.priority] ?? 1;
      const bPriority = priorityOrder[b.priority] ?? 1;
      return aPriority - bPriority;
    });
  }

  async completeTask(id) {
    const tasks = await this.loadTasks();
    const task = tasks.find(t => t.id === id);

    if (!task) throw new Error(`Task ${id} not found`);
    task.completed = true;
    task.completedAt = new Date().toISOString();

    await this.saveTasks(tasks);
  }

  async removeTask(id) {
    const tasks = await this.loadTasks();
    const index = tasks.findIndex(t => t.id === id);

    if (index === -1) throw new Error(`Task ${id} not found`);
    tasks.splice(index, 1);

    await this.saveTasks(tasks);
  }

  async clearCompleted() {
    const tasks = await this.loadTasks();
    const filtered = tasks.filter(t => !t.completed);
    await this.saveTasks(filtered);
  }

  async editTask(id, updates) {
    const tasks = await this.loadTasks();
    const task = tasks.find(t => t.id === id);

    if (!task) throw new Error(`Task ${id} not found`);

    if (updates.title !== undefined) task.title = updates.title;
    if (updates.priority !== undefined) task.priority = validatePriority(updates.priority);
    if (updates.dueDate !== undefined) task.dueDate = updates.dueDate;

    await this.saveTasks(tasks);
  }
}

function validatePriority(priority) {
  const valid = ['high', 'medium', 'low'];
  if (!valid.includes(priority)) {
    throw new Error(`Invalid priority: ${priority}. Must be one of: ${valid.join(', ')}`);
  }
  return priority;
}
