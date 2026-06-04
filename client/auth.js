// Module-level token storage
let authToken = null;

export function setToken(token) {
    authToken = token;
}

export function getToken() {
    return authToken;
}

export function isAuthenticated() {
    return authToken !== null;
}

export async function login(username, password) {
    try {
        const response = await fetch('http://localhost:8000/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        setToken(data.access_token);
        return { success: true, username };
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: error.message };
    }
}

export function logout() {
    authToken = null;
}
