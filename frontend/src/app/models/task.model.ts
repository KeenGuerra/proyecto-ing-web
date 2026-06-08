export interface Task {
  id?: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  category?: string;
  due_date?: string;
  created_at?: string;
}
