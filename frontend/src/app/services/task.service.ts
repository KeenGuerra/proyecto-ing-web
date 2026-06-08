import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task } from '../models/task.model';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? (window.location.port === '4200' ? 'http://localhost:8000/api/tasks' : '/api/tasks')
    : ('API_URL_PLACEHOLDER' === 'API_URL_PLACEHOLDER' ? '/api/tasks' : 'API_URL_PLACEHOLDER');

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(this.apiUrl);
  }

  getTask(id: string): Observable<Task> {
    return this.http.get<Task>(`${this.apiUrl}/${id}`);
  }

  createTask(task: Task): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task);
  }

  updateTask(id: string, task: Partial<Task>): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${id}`, task);
  }

  deleteTask(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getHealth(): Observable<{ status: string; database_status: string }> {
    const healthUrl = this.apiUrl.replace('/tasks', '/health');
    return this.http.get<{ status: string; database_status: string }>(healthUrl);
  }
}
