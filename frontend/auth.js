// Authentication API Base URL
const API_BASE_URL = 'http://localhost:8000';
const TOKEN_KEY = 'access_token';

/**
 * Register a new user
 * @param {string} username - User's username
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} User data
 */
async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 422) {
                const errors = data.detail;
                if (Array.isArray(errors)) {
                    const errorMessages = errors.map(err => err.msg).join(', ');
                    throw new Error(`Validation error: ${errorMessages}`);
                }
                throw new Error(data.detail || 'Validation error');
            } else if (response.status === 409) {
                throw new Error('User with this email or username already exists');
            } else {
                throw new Error(data.detail || 'Registration failed');
            }
        }

        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            throw new Error('Unable to connect to the server. Please check if the API is running.');
        }
        throw error;
    }
}

/**
 * Login user and store JWT token
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Login response with access token
 */
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Invalid email or password');
            } else if (response.status === 422) {
                throw new Error('Please enter valid email and password');
            } else {
                throw new Error(data.detail || 'Login failed');
            }
        }

        // Store token in localStorage
        if (data.access_token) {
            localStorage.setItem(TOKEN_KEY, data.access_token);
        }

        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            throw new Error('Unable to connect to the server. Please check if the API is running.');
        }
        throw error;
    }
}

/**
 * Logout user by removing token from localStorage
 */
function logout() {
    localStorage.removeItem(TOKEN_KEY);
    window.location.href = '/static/login.html';
}

/**
 * Get authorization headers with Bearer token
 * @returns {Object} Headers object with Authorization
 */
function getAuthHeaders() {
    const token = localStorage.getItem(TOKEN_KEY);
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if user has valid token
 */
function isAuthenticated() {
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
        return false;
    }

    // Check if token is expired (basic check)
    try {
        const payload = parseJwt(token);
        if (payload.exp) {
            const expirationTime = payload.exp * 1000;
            if (Date.now() >= expirationTime) {
                localStorage.removeItem(TOKEN_KEY);
                return false;
            }
        }
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Parse JWT token to get payload
 * @param {string} token - JWT token
 * @returns {Object} Token payload
 */
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error parsing JWT:', error);
        return {};
    }
}

/**
 * Get current user information
 * @returns {Promise<Object>} User data
 */
async function getCurrentUser() {
    try {
        const token = localStorage.getItem(TOKEN_KEY);

        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            method: 'GET',
            headers: getAuthHeaders()
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem(TOKEN_KEY);
                throw new Error('Session expired. Please login again.');
            }
            throw new Error(data.detail || 'Failed to get user information');
        }

        return data;
    } catch (error) {
        if (error instanceof TypeError) {
            throw new Error('Unable to connect to the server. Please check if the API is running.');
        }
        throw error;
    }
}

/**
 * Make authenticated API request
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);

    if (!token) {
        window.location.href = '/static/login.html';
        throw new Error('Not authenticated');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        window.location.href = '/static/login.html';
        throw new Error('Session expired');
    }

    return response;
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        register,
        login,
        logout,
        getAuthHeaders,
        isAuthenticated,
        getCurrentUser,
        authenticatedFetch
    };
}
