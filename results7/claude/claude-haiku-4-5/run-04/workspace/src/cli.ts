import { TodoStorage, Todo } from "./storage.js";

export class TodoCLI {
  private storage: TodoStorage;

  constructor(storagePath: string) {
    this.storage = new TodoStorage(storagePath);
  }

  add(text: string): void {
    const todo = this.storage.add(text);
    console.log(`✓ Added: "${todo.text}" (${todo.id})`);
  }

  complete(id: string): void {
    const todo = this.storage.complete(id);
    if (todo) {
      console.log(`✓ Completed: "${todo.text}"`);
    } else {
      console.error(`✗ Todo ${id} not found`);
      process.exit(1);
    }
  }

  remove(id: string): void {
    if (this.storage.remove(id)) {
      console.log(`✓ Removed todo ${id}`);
    } else {
      console.error(`✗ Todo ${id} not found`);
      process.exit(1);
    }
  }

  list(filter?: "pending" | "completed"): void {
    const todos = this.storage.list(filter);

    if (todos.length === 0) {
      const msg = filter
        ? `No ${filter} todos`
        : "No todos yet";
      console.log(`  ${msg}`);
      return;
    }

    todos.forEach((todo) => {
      const checkbox = todo.completed ? "☑" : "☐";
      const status = todo.completed ? "\x1b[2m" : "";
      const reset = todo.completed ? "\x1b[0m" : "";
      console.log(`  ${checkbox} ${status}${todo.text}\x1b[0m (${todo.id})`);
    });
  }

  stats(): void {
    const all = this.storage.list();
    const pending = this.storage.list("pending");
    const completed = this.storage.list("completed");

    console.log(`\nStats:`);
    console.log(`  Total: ${all.length}`);
    console.log(`  Pending: ${pending.length}`);
    console.log(`  Completed: ${completed.length}`);
    if (all.length > 0) {
      const percent = Math.round((completed.length / all.length) * 100);
      console.log(`  Progress: ${percent}%`);
    }
  }

  clear(confirmed: boolean = false): void {
    if (!confirmed) {
      console.error("Use 'todo clear --confirm' to clear completed todos");
      process.exit(1);
    }
    const removed = this.storage.clear(true);
    console.log(`✓ Cleared ${removed} completed todo(s)`);
  }

  help(): void {
    console.log(`
Usage: todo <command> [args]

Commands:
  add <text>              Add a new todo
  list [pending|done]     List todos (optionally filtered)
  done <id>               Mark todo as completed
  rm <id>                 Remove a todo
  clear [--confirm]       Clear completed todos (requires --confirm)
  stats                   Show todo statistics
  help                    Show this help message

Examples:
  todo add "Buy milk"
  todo list
  todo list pending
  todo done 1234567890
  todo rm 1234567890
  todo stats
`);
  }
}
