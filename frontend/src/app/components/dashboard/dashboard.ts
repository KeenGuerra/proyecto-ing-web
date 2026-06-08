import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TaskService } from '../../services/task.service';
import { Task } from '../../models/task.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  private readonly taskService = inject(TaskService);

  // Core tasks state using Signals
  readonly tasks = signal<Task[]>([]);
  readonly loading = signal<boolean>(true);
  readonly errorMessage = signal<string | null>(null);

  // Filters & Search
  readonly searchQuery = signal<string>('');
  readonly selectedCategory = signal<string>('all');

  // Database Connection Status
  readonly databaseStatus = signal<'loading' | 'firestore' | 'mock' | 'error'>('loading');

  // Modal State
  readonly isModalOpen = signal<boolean>(false);
  readonly isEditing = signal<boolean>(false);
  
  // Active editing/creating task state
  readonly taskForm = signal<Task>({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    category: 'General',
    due_date: ''
  });

  // Unique categories computed from tasks
  readonly categories = computed(() => {
    const list = this.tasks().map(t => t.category || 'General');
    return ['all', ...Array.from(new Set(list))];
  });

  // Filtered tasks
  readonly filteredTasks = computed(() => {
    const query = this.searchQuery().toLowerCase().trim();
    const category = this.selectedCategory();
    
    return this.tasks().filter(task => {
      const matchesSearch = 
        task.title.toLowerCase().includes(query) || 
        (task.description || '').toLowerCase().includes(query);
        
      const matchesCategory = 
        category === 'all' || 
        (task.category || 'General') === category;
        
      return matchesSearch && matchesCategory;
    });
  });

  // Stats computed from tasks
  readonly stats = computed(() => {
    const all = this.tasks();
    const todo = all.filter(t => t.status === 'todo').length;
    const inProgress = all.filter(t => t.status === 'in_progress').length;
    const completed = all.filter(t => t.status === 'completed').length;
    
    const percentage = all.length > 0 ? Math.round((completed / all.length) * 100) : 0;
    
    return {
      total: all.length,
      todo,
      inProgress,
      completed,
      percentage
    };
  });

  // Dynamic counts for each Kanban column based on filtered tasks
  readonly todoCount = computed(() => this.filteredTasks().filter(t => t.status === 'todo').length);
  readonly inProgressCount = computed(() => this.filteredTasks().filter(t => t.status === 'in_progress').length);
  readonly completedCount = computed(() => this.filteredTasks().filter(t => t.status === 'completed').length);

  ngOnInit(): void {
    this.loadTasks();
    this.checkDatabaseStatus();
  }

  checkDatabaseStatus(): void {
    this.taskService.getHealth().subscribe({
      next: (res) => {
        if (res.database_status === 'Firebase Firestore') {
          this.databaseStatus.set('firestore');
        } else {
          this.databaseStatus.set('mock');
        }
      },
      error: (err) => {
        console.error('Error fetching database health status:', err);
        this.databaseStatus.set('error');
      }
    });
  }

  loadTasks(): void {
    this.loading.set(true);
    this.errorMessage.set(null);
    this.taskService.getTasks().subscribe({
      next: (data) => {
        this.tasks.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading tasks:', err);
        this.errorMessage.set('Error al conectar con la API del backend. Comprueba que el servidor esté corriendo.');
        this.loading.set(false);
      }
    });
  }

  // Modal Controls
  openAddModal(status: 'todo' | 'in_progress' | 'completed' = 'todo'): void {
    this.isEditing.set(false);
    this.taskForm.set({
      title: '',
      description: '',
      status: status,
      priority: 'medium',
      category: 'General',
      due_date: new Date().toISOString().split('T')[0]
    });
    this.isModalOpen.set(true);
  }

  openEditModal(task: Task): void {
    this.isEditing.set(true);
    // Clone task to edit form
    this.taskForm.set({ ...task });
    this.isModalOpen.set(true);
  }

  closeModal(): void {
    this.isModalOpen.set(false);
  }

  // Submit Handler
  onSubmit(): void {
    const form = this.taskForm();
    if (!form.title.trim()) return;

    this.loading.set(true);
    if (this.isEditing() && form.id) {
      // Update
      this.taskService.updateTask(form.id, form).subscribe({
        next: (updatedTask) => {
          this.tasks.update(all => all.map(t => t.id === updatedTask.id ? updatedTask : t));
          this.closeModal();
          this.loading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.errorMessage.set('Error al actualizar la tarea.');
          this.loading.set(false);
        }
      });
    } else {
      // Create
      this.taskService.createTask(form).subscribe({
        next: (newTask) => {
          this.tasks.update(all => [...all, newTask]);
          this.closeModal();
          this.loading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.errorMessage.set('Error al guardar la tarea.');
          this.loading.set(false);
        }
      });
    }
  }

  // Delete Handler
  deleteTask(id: string | undefined): void {
    if (!id) return;
    if (!confirm('¿Estás seguro de que deseas eliminar esta tarea?')) return;

    this.loading.set(true);
    this.taskService.deleteTask(id).subscribe({
      next: () => {
        this.tasks.update(all => all.filter(t => t.id !== id));
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.errorMessage.set('Error al eliminar la tarea.');
        this.loading.set(false);
      }
    });
  }

  // Drag and Drop (HTML5 native API)
  draggedTaskId: string | null = null;

  onDragStart(event: DragEvent, task: Task): void {
    if (task.id) {
      this.draggedTaskId = task.id;
      if (event.dataTransfer) {
        event.dataTransfer.setData('text/plain', task.id);
        event.dataTransfer.effectAllowed = 'move';
      }
    }
  }

  onDragOver(event: DragEvent): void {
    // Prevent default to allow drop
    event.preventDefault();
  }

  onDrop(event: DragEvent, targetStatus: 'todo' | 'in_progress' | 'completed'): void {
    event.preventDefault();
    const taskId = this.draggedTaskId || event.dataTransfer?.getData('text/plain');
    if (!taskId) return;

    const taskToUpdate = this.tasks().find(t => t.id === taskId);
    if (!taskToUpdate || taskToUpdate.status === targetStatus) return;

    // Optimistically update status
    this.tasks.update(all => 
      all.map(t => t.id === taskId ? { ...t, status: targetStatus } : t)
    );

    // Call API
    this.taskService.updateTask(taskId, { status: targetStatus }).subscribe({
      error: (err) => {
        console.error('Failed to update status on server:', err);
        // Rollback on error
        this.loadTasks();
      }
    });

    this.draggedTaskId = null;
  }

  // Quick State Toggles for Mobile/Buttons
  moveTask(task: Task, direction: 'forward' | 'backward'): void {
    if (!task.id) return;
    
    let nextStatus: 'todo' | 'in_progress' | 'completed' = task.status;
    if (direction === 'forward') {
      if (task.status === 'todo') nextStatus = 'in_progress';
      else if (task.status === 'in_progress') nextStatus = 'completed';
    } else {
      if (task.status === 'completed') nextStatus = 'in_progress';
      else if (task.status === 'in_progress') nextStatus = 'todo';
    }

    if (nextStatus === task.status) return;

    this.tasks.update(all => 
      all.map(t => t.id === task.id ? { ...t, status: nextStatus } : t)
    );

    this.taskService.updateTask(task.id, { status: nextStatus }).subscribe({
      error: (err) => {
        console.error(err);
        this.loadTasks();
      }
    });
  }
}
