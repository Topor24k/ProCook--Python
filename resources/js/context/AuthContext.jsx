import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const response = await api.get('/user');
            // Handle new API response format with success/data wrapper
            setUser(response.data.data || response.data);
        } catch (error) {
            // 401 is expected when user is not authenticated - handle silently
            if (error.response?.status === 401) {
                setUser(null);
            } else {
                // Log unexpected errors
                console.error('Auth check failed:', error);
                setUser(null);
            }
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        await api.post('/login', { email, password });
        await checkAuth();
    };

    const register = async (name, email, password, password_confirmation) => {
        await api.post('/register', { name, email, password, password_confirmation });
        await checkAuth();
    };

    const logout = async () => {
        await api.post('/logout');
        setUser(null);
    };

    // Force-clear user state (used after server-side account deletion)
    const clearUser = () => {
        setUser(null);
    };

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        clearUser,
        isAuthenticated: !!user,
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
}
