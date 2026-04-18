import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

export interface TaskSession {
  id: string;
  taskName: string;
  startTime: number;
  endTime?: number;
  duration?: number;
}

export interface TaskData {
  sessions: TaskSession[];
  activeSessionId?: string;
}

export class FileStore {
  private filePath: string;

  constructor() {
    const dir = join(homedir(), '.task-timer');
    this.filePath = join(dir, 'tasks.json');
  }

  load(): TaskData {
    if (!existsSync(this.filePath)) {
      return { sessions: [] };
    }
    try {
      const content = readFileSync(this.filePath, 'utf-8');
      return JSON.parse(content);
    } catch {
      return { sessions: [] };
    }
  }

  save(data: TaskData): void {
    const dir = this.filePath.substring(0, this.filePath.lastIndexOf('/'));
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }
    writeFileSync(this.filePath, JSON.stringify(data, null, 2));
  }
}
