import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export function useAuthGuard() {
    const { isAuthenticated } = useAuth();
    const [showAuthPrompt, setShowAuthPrompt] = useState(false);

    const requireAuth = (callback, message = "Please register or login to continue") => {
        if (isAuthenticated) {
            // User is authenticated, execute the callback
            if (callback) callback();
            return true;
        } else {
            // User is not authenticated, show prompt
            setShowAuthPrompt(true);
            return false;
        }
    };

    const hideAuthPrompt = () => {
        setShowAuthPrompt(false);
    };

    return {
        requireAuth,
        showAuthPrompt,
        hideAuthPrompt,
        isAuthenticated
    };
}