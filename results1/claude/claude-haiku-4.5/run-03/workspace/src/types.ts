export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high';
  created: string;
  due?: string;
}

export interface TaskStore {
  tasks: Task[];
}
