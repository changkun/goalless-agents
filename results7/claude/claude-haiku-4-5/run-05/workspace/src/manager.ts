import { FileStore, TaskSession, TaskData } from './storage.js';
import { randomUUID } from 'crypto';

export class TaskManager {
  private store: FileStore;
  private data: TaskData;

  constructor() {
    this.store = new FileStore();
    this.data = this.store.load();
  }

  start(taskName: string): string {
    if (this.data.activeSessionId) {
      throw new Error('A task is already running. Stop it first.');
    }

    const session: TaskSession = {
      id: randomUUID(),
      taskName,
      startTime: Date.now(),
    };

    this.data.sessions.push(session);
    this.data.activeSessionId = session.id;
    this.store.save(this.data);
    return session.id;
  }

  stop(): TaskSession {
    if (!this.data.activeSessionId) {
      throw new Error('No task is currently running.');
    }

    const session = this.data.sessions.find(s => s.id === this.data.activeSessionId);
    if (!session) throw new Error('Session not found');

    session.endTime = Date.now();
    session.duration = session.endTime - session.startTime;
    this.data.activeSessionId = undefined;
    this.store.save(this.data);
    return session;
  }

  getActive(): TaskSession | undefined {
    if (!this.data.activeSessionId) return undefined;
    return this.data.sessions.find(s => s.id === this.data.activeSessionId);
  }

  getStats(): Record<string, { count: number; totalTime: number; avgTime: number }> {
    const stats: Record<string, { count: number; totalTime: number; avgTime: number }> = {};

    for (const session of this.data.sessions) {
      if (!session.duration) continue;

      if (!stats[session.taskName]) {
        stats[session.taskName] = { count: 0, totalTime: 0, avgTime: 0 };
      }

      stats[session.taskName].count++;
      stats[session.taskName].totalTime += session.duration;
      stats[session.taskName].avgTime = stats[session.taskName].totalTime / stats[session.taskName].count;
    }

    return stats;
  }

  getAllSessions(): TaskSession[] {
    return this.data.sessions;
  }
}
