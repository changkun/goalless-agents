#!/usr/bin/env node

import { homedir } from "os";
import { join } from "path";
import { TodoCLI } from "./cli.js";

const storagePath = join(homedir(), ".todos", "todos.json");
const cli = new TodoCLI(storagePath);

const [, , command, ...args] = process.argv;

try {
  switch (command) {
    case "add":
      if (!args[0]) {
        console.error("✗ Please provide todo text");
        process.exit(1);
      }
      cli.add(args.join(" "));
      break;

    case "list":
      const filter = args[0];
      const normalizedFilter =
        filter === "done" ? "completed" : (filter as "pending" | "completed" | undefined);
      if (filter && !["pending", "completed", "done"].includes(filter)) {
        console.error("✗ Filter must be 'pending' or 'completed'");
        process.exit(1);
      }
      console.log();
      cli.list(normalizedFilter);
      console.log();
      break;

    case "done":
      if (!args[0]) {
        console.error("✗ Please provide a todo ID");
        process.exit(1);
      }
      cli.complete(args[0]);
      break;

    case "rm":
      if (!args[0]) {
        console.error("✗ Please provide a todo ID");
        process.exit(1);
      }
      cli.remove(args[0]);
      break;

    case "clear":
      cli.clear(args.includes("--confirm"));
      break;

    case "stats":
      cli.stats();
      break;

    case "help":
    case "--help":
    case "-h":
      cli.help();
      break;

    default:
      if (!command) {
        cli.list();
      } else {
        console.error(`✗ Unknown command: ${command}`);
        console.error(`Run 'todo help' for usage information`);
        process.exit(1);
      }
  }
} catch (error) {
  console.error("✗ Error:", error instanceof Error ? error.message : String(error));
  process.exit(1);
}
