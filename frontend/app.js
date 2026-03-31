// API Configuration
const API_BASE_URL = window.location.origin + '/api/tasks';

// State Management
let tasks = [];
let currentStatusFilter = 'all';
let currentPriorityFilter = 'all';
let currentPage = 1;
let tasksPerPage = 20;
let isSearchMode = false;
let searchQuery = '';

// DOM Elements
const taskForm = document.getElementById('taskForm');
const taskList = document.getElementById('taskList');
const emptyState = document.getElementById('emptyState');
const totalTasksElement = document.getElementById('totalTasks');
const completedTasksElement = document.getElementById('completedTasks');
const pendingTasksElement = document.getElementById('pendingTasks');
const filterButtons = document.querySelectorAll('.btn-filter');
const editModal = document.getElementById('editModal');
const editTaskForm = document.getElementById('editTaskForm');
const closeModalBtn = document.querySelector('.close-modal');
const cancelEditBtn = document.querySelector('.cancel-edit');

// New DOM Elements
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearch');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const currentPageSpan = document.getElementById('currentPage');
const totalPagesSpan = document.getElementById('totalPages');
const paginationControls = document.getElementById('paginationControls');

// Statistics Elements
const statTotal = document.getElementById('statTotal');
const statCompleted = document.getElementById('statCompleted');
const statPending = document.getElementById('statPending');
const statHigh = document.getElementById('statHigh');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    loadTasks();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Task form submission
    taskForm.addEventListener('submit', handleTaskSubmit);

    // Filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filterType = button.getAttribute('data-filter-type');
            const filter = button.getAttribute('data-filter');
            setFilter(filterType, filter);
        });
    });

    // Search functionality
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    clearSearchBtn.addEventListener('click', clearSearch);

    // Pagination
    prevPageBtn.addEventListener('click', () => changePage(currentPage - 1));
    nextPageBtn.addEventListener('click', () => changePage(currentPage + 1));

    // Modal close events
    closeModalBtn.addEventListener('click', closeEditModal);
    cancelEditBtn.addEventListener('click', closeEditModal);
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) {
            closeEditModal();
        }
    });

    // Edit task form submission
    editTaskForm.addEventListener('submit', handleEditSubmit);
}

// API Functions
async function fetchTasks(page = 1) {
    try {
        let url = `${API_BASE_URL}/?page=${page}&limit=${tasksPerPage}`;

        if (currentPriorityFilter !== 'all') {
            url += `&priority=${currentPriorityFilter}`;
        }

        if (currentStatusFilter === 'active') {
            url += `&completed=false`;
        } else if (currentStatusFilter === 'completed') {
            url += `&completed=true`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch tasks');
        return await response.json();
    } catch (error) {
        console.error('Error fetching tasks:', error);
        showError('Failed to load tasks. Please check if the server is running.');
        return [];
    }
}

async function searchTasks(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}&limit=50`);
        if (!response.ok) throw new Error('Failed to search tasks');
        return await response.json();
    } catch (error) {
        console.error('Error searching tasks:', error);
        showError('Failed to search tasks.');
        return [];
    }
}

async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (!response.ok) throw new Error('Failed to fetch statistics');
        return await response.json();
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return null;
    }
}

async function createTask(taskData) {
    try {
        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData),
        });
        if (!response.ok) throw new Error('Failed to create task');
        return await response.json();
    } catch (error) {
        console.error('Error creating task:', error);
        showError('Failed to create task. Please try again.');
        return null;
    }
}

async function updateTask(taskId, taskData) {
    try {
        const response = await fetch(`${API_BASE_URL}/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(taskData),
        });
        if (!response.ok) throw new Error('Failed to update task');
        return await response.json();
    } catch (error) {
        console.error('Error updating task:', error);
        showError('Failed to update task. Please try again.');
        return null;
    }
}

async function deleteTask(taskId) {
    try {
        const response = await fetch(`${API_BASE_URL}/${taskId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete task');
        return true;
    } catch (error) {
        console.error('Error deleting task:', error);
        showError('Failed to delete task. Please try again.');
        return false;
    }
}

// Task Management Functions
async function loadTasks(page = 1) {
    if (isSearchMode && searchQuery) {
        tasks = await searchTasks(searchQuery);
        paginationControls.style.display = 'none';
    } else {
        tasks = await fetchTasks(page);
        currentPage = page;
        updatePaginationControls();
        paginationControls.style.display = 'flex';
    }
    renderTasks();
}

async function loadStatistics() {
    const stats = await fetchStatistics();
    if (stats) {
        statTotal.textContent = stats.total;
        statCompleted.textContent = stats.completed;
        statPending.textContent = stats.pending;
        statHigh.textContent = stats.by_priority.high;

        // Also update the task count section
        totalTasksElement.textContent = stats.total;
        completedTasksElement.textContent = stats.completed;
        pendingTasksElement.textContent = stats.pending;
    }
}

function renderTasks() {
    const filteredTasks = getFilteredTasks();

    // Show/hide empty state
    if (filteredTasks.length === 0) {
        taskList.classList.add('hidden');
        emptyState.classList.add('show');
        if (isSearchMode) {
            emptyState.querySelector('p').textContent = `No tasks found for "${searchQuery}"`;
        } else {
            emptyState.querySelector('p').textContent = 'No tasks yet. Add your first task above!';
        }
        return;
    }

    taskList.classList.remove('hidden');
    emptyState.classList.remove('show');

    // Render tasks
    taskList.innerHTML = filteredTasks.map(task => createTaskElement(task)).join('');

    // Add event listeners to dynamically created elements
    attachTaskEventListeners();
}

function createTaskElement(task) {
    const createdDate = task.created_at ? new Date(task.created_at).toLocaleDateString() : '';
    const completedClass = task.completed ? 'completed' : '';
    const priorityClass = `priority-${task.priority || 'medium'}`;

    // Format due date
    let dueDateHTML = '';
    if (task.due_date) {
        const dueDate = new Date(task.due_date);
        const now = new Date();
        const isOverdue = dueDate < now && !task.completed;
        const dueDateStr = dueDate.toLocaleString();
        dueDateHTML = `<span class="due-date ${isOverdue ? 'overdue' : ''}">📅 Due: ${dueDateStr}</span>`;
    }

    // Format tags
    let tagsHTML = '';
    if (task.tags) {
        const tagArray = task.tags.split(',').map(t => t.trim()).filter(t => t);
        if (tagArray.length > 0) {
            tagsHTML = `<div class="task-tags">${tagArray.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}</div>`;
        }
    }

    return `
        <div class="task-item ${completedClass} ${priorityClass}" data-task-id="${task.id}">
            <div class="task-content">
                <div class="task-header">
                    <input
                        type="checkbox"
                        class="task-checkbox"
                        ${task.completed ? 'checked' : ''}
                        data-task-id="${task.id}"
                    >
                    <h3 class="task-title ${completedClass}">${escapeHtml(task.title)}</h3>
                </div>
                ${task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : ''}
                <div class="task-meta">
                    <span class="priority-badge ${task.priority || 'medium'}">${task.priority || 'medium'}</span>
                    ${dueDateHTML}
                    ${tagsHTML}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn-icon btn-edit" data-task-id="${task.id}">Edit</button>
                <button class="btn-icon btn-delete" data-task-id="${task.id}">Delete</button>
            </div>
        </div>
    `;
}

function attachTaskEventListeners() {
    // Checkbox listeners
    document.querySelectorAll('.task-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });

    // Edit button listeners
    document.querySelectorAll('.btn-edit').forEach(button => {
        button.addEventListener('click', handleEditClick);
    });

    // Delete button listeners
    document.querySelectorAll('.btn-delete').forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });
}

// Event Handlers
async function handleTaskSubmit(e) {
    e.preventDefault();

    const formData = new FormData(taskForm);
    const dueDateValue = formData.get('due_date');

    const taskData = {
        title: formData.get('title').trim(),
        description: formData.get('description').trim() || null,
        priority: formData.get('priority') || 'medium',
        tags: formData.get('tags').trim() || null,
        due_date: dueDateValue ? new Date(dueDateValue).toISOString() : null,
        completed: false,
    };

    if (!taskData.title) {
        showError('Task title is required');
        return;
    }

    const newTask = await createTask(taskData);
    if (newTask) {
        taskForm.reset();
        showSuccess('Task created successfully!');
        await loadStatistics();
        await loadTasks(currentPage);
    }
}

async function handleCheckboxChange(e) {
    const taskId = parseInt(e.target.getAttribute('data-task-id'));
    const completed = e.target.checked;

    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const updatedTask = await updateTask(taskId, { completed });
    if (updatedTask) {
        task.completed = completed;
        await loadStatistics();
        renderTasks();
    }
}

function handleEditClick(e) {
    const taskId = parseInt(e.target.getAttribute('data-task-id'));
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    // Populate edit form
    document.getElementById('editTaskId').value = task.id;
    document.getElementById('editTaskTitle').value = task.title;
    document.getElementById('editTaskDescription').value = task.description || '';
    document.getElementById('editTaskPriority').value = task.priority || 'medium';
    document.getElementById('editTaskTags').value = task.tags || '';
    document.getElementById('editTaskCompleted').checked = task.completed;

    // Format due_date for datetime-local input
    if (task.due_date) {
        const date = new Date(task.due_date);
        const formattedDate = date.toISOString().slice(0, 16);
        document.getElementById('editTaskDueDate').value = formattedDate;
    } else {
        document.getElementById('editTaskDueDate').value = '';
    }

    // Show modal
    editModal.classList.add('show');
}

async function handleEditSubmit(e) {
    e.preventDefault();

    const taskId = parseInt(document.getElementById('editTaskId').value);
    const dueDateValue = document.getElementById('editTaskDueDate').value;

    const taskData = {
        title: document.getElementById('editTaskTitle').value.trim(),
        description: document.getElementById('editTaskDescription').value.trim() || null,
        priority: document.getElementById('editTaskPriority').value,
        tags: document.getElementById('editTaskTags').value.trim() || null,
        due_date: dueDateValue ? new Date(dueDateValue).toISOString() : null,
        completed: document.getElementById('editTaskCompleted').checked,
    };

    if (!taskData.title) {
        showError('Task title is required');
        return;
    }

    const updatedTask = await updateTask(taskId, taskData);
    if (updatedTask) {
        const taskIndex = tasks.findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
            tasks[taskIndex] = updatedTask;
        }
        closeEditModal();
        showSuccess('Task updated successfully!');
        await loadStatistics();
        await loadTasks(currentPage);
    }
}

async function handleDeleteClick(e) {
    const taskId = parseInt(e.target.getAttribute('data-task-id'));

    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    const success = await deleteTask(taskId);
    if (success) {
        showSuccess('Task deleted successfully!');
        await loadStatistics();
        await loadTasks(currentPage);
    }
}

// Search Functions
async function handleSearch(e) {
    searchQuery = e.target.value.trim();

    if (searchQuery.length > 0) {
        isSearchMode = true;
        clearSearchBtn.style.display = 'block';
        await loadTasks();
    } else {
        clearSearch();
    }
}

function clearSearch() {
    searchInput.value = '';
    searchQuery = '';
    isSearchMode = false;
    clearSearchBtn.style.display = 'none';
    loadTasks(currentPage);
}

// Pagination Functions
function changePage(newPage) {
    if (newPage < 1) return;
    currentPage = newPage;
    loadTasks(currentPage);
}

function updatePaginationControls() {
    currentPageSpan.textContent = currentPage;

    // Disable/enable buttons based on current page
    prevPageBtn.disabled = currentPage === 1;

    // Check if there are more pages (if we got full page of results, there might be more)
    nextPageBtn.disabled = tasks.length < tasksPerPage;

    // For now, we'll show "?" for total pages since we don't have total count
    // In a real app, you'd get this from the backend
    totalPagesSpan.textContent = '?';
}

// Filter Functions
function setFilter(filterType, filter) {
    // Update the appropriate filter
    if (filterType === 'status') {
        currentStatusFilter = filter;
    } else if (filterType === 'priority') {
        currentPriorityFilter = filter;
    }

    // Update active button for the specific filter type
    filterButtons.forEach(button => {
        const btnFilterType = button.getAttribute('data-filter-type');
        const btnFilter = button.getAttribute('data-filter');

        if (btnFilterType === filterType && btnFilter === filter) {
            button.classList.add('active');
        } else if (btnFilterType === filterType) {
            button.classList.remove('active');
        }
    });

    currentPage = 1;
    loadTasks(currentPage);
}

function getFilteredTasks() {
    // Note: Filtering is now done on the backend via API parameters
    // This function is kept for consistency but just returns all tasks
    return tasks;
}

// Modal Functions
function closeEditModal() {
    editModal.classList.remove('show');
    editTaskForm.reset();
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    console.log('Success:', message);
}
