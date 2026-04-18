import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { dirname } from "path";

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: string;
  completedAt?: string;
}

export class TodoStorage {
  private filePath: string;
  private todos: Todo[] = [];

  constructor(filePath: string) {
    this.filePath = filePath;
    this.load();
  }

  private load(): void {
    try {
      const data = readFileSync(this.filePath, "utf-8");
      this.todos = JSON.parse(data);
    } catch {
      this.todos = [];
    }
  }

  private save(): void {
    mkdirSync(dirname(this.filePath), { recursive: true });
    writeFileSync(this.filePath, JSON.stringify(this.todos, null, 2));
  }

  add(text: string): Todo {
    const todo: Todo = {
      id: Date.now().toString(),
      text,
      completed: false,
      createdAt: new Date().toISOString(),
    };
    this.todos.push(todo);
    this.save();
    return todo;
  }

  complete(id: string): Todo | null {
    const todo = this.todos.find((t) => t.id === id);
    if (todo) {
      todo.completed = true;
      todo.completedAt = new Date().toISOString();
      this.save();
    }
    return todo || null;
  }

  remove(id: string): boolean {
    const index = this.todos.findIndex((t) => t.id === id);
    if (index !== -1) {
      this.todos.splice(index, 1);
      this.save();
      return true;
    }
    return false;
  }

  list(filter?: "pending" | "completed"): Todo[] {
    if (filter === "pending") return this.todos.filter((t) => !t.completed);
    if (filter === "completed") return this.todos.filter((t) => t.completed);
    return this.todos;
  }

  clear(completed: boolean = true): number {
    const before = this.todos.length;
    this.todos = completed
      ? this.todos.filter((t) => !t.completed)
      : [];
    this.save();
    return before - this.todos.length;
  }
}
