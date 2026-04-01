// Authentication UI Elements
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const authButtons = document.getElementById('authButtons');
const userInfo = document.getElementById('userInfo');
const usernameDisplay = document.getElementById('username');
const userRoleDisplay = document.getElementById('userRole');
const mainContent = document.getElementById('mainContent');
const switchToRegister = document.getElementById('switchToRegister');
const switchToLogin = document.getElementById('switchToLogin');

// Authentication Event Listeners
function setupAuthListeners() {
    loginBtn.addEventListener('click', () => openModal(loginModal));
    registerBtn.addEventListener('click', () => openModal(registerModal));
    logoutBtn.addEventListener('click', handleLogout);
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    switchToRegister.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal(loginModal);
        openModal(registerModal);
    });
    switchToLogin.addEventListener('click', (e) => {
        e.preventDefault();
        closeModal(registerModal);
        openModal(loginModal);
    });

    // Close modals when clicking outside or on close button
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            closeModal(loginModal);
            closeModal(registerModal);
        });
    });

    [loginModal, registerModal].forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal);
            }
        });
    });
}

function openModal(modal) {
    modal.style.display = 'block';
}

function closeModal(modal) {
    modal.style.display = 'none';
    // Clear error messages
    const errorDiv = modal.querySelector('.error-message');
    if (errorDiv) errorDiv.style.display = 'none';
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');

    try {
        await authManager.login(email, password);
        closeModal(loginModal);
        updateAuthUI();
        loginForm.reset();
        location.reload(); // Reload to show tasks
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const errorDiv = document.getElementById('registerError');

    try {
        await authManager.register(username, email, password);
        closeModal(registerModal);
        updateAuthUI();
        registerForm.reset();
        location.reload(); // Reload to show tasks
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

function handleLogout() {
    authManager.logout();
    updateAuthUI();
    location.reload();
}

function updateAuthUI() {
    if (authManager.isAuthenticated()) {
        const user = authManager.getUser();
        authButtons.style.display = 'none';
        userInfo.style.display = 'flex';
        usernameDisplay.textContent = user.username;
        
        if (authManager.isAdmin()) {
            userRoleDisplay.textContent = 'Admin';
            userRoleDisplay.classList.add('admin');
        } else {
            userRoleDisplay.textContent = 'User';
            userRoleDisplay.classList.remove('admin');
        }
        
        mainContent.style.display = 'block';
    } else {
        authButtons.style.display = 'flex';
        userInfo.style.display = 'none';
        mainContent.style.display = 'none';
    }
}

// Initialize authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    setupAuthListeners();
    updateAuthUI();
    
    if (authManager.isAuthenticated()) {
        // Existing app initialization
        loadStatistics();
        loadTasks();
        setupEventListeners();
    }
});
