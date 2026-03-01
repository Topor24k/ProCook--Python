import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Recipes from './pages/Recipes';
import RecipeDetail from './pages/RecipeDetail';
import RecipeCreate from './pages/RecipeCreate';
import RecipeEdit from './pages/RecipeEdit';
import MyRecipes from './pages/MyRecipes';
import SavedRecipes from './pages/SavedRecipes';
import Login from './pages/Login';
import Register from './pages/Register';
import AboutUs from './pages/AboutUs';
import Profile from './pages/Profile';
import '../css/app.css';
import './index.css';

// Error Boundary Component
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('React Error Boundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '20px', textAlign: 'center' }}>
                    <h2>Something went wrong!</h2>
                    <p>Error: {this.state.error?.message}</p>
                    <button onClick={() => window.location.reload()}>Reload Page</button>
                </div>
            );
        }
        return this.props.children;
    }
}

function App() {
    console.log('App component is rendering...');
    
    return (
        <ErrorBoundary>
            <AuthProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Layout />}>
                            <Route index element={<Home />} />
                            
                            {/* Recipe Routes */}
                            <Route path="recipes" element={<Recipes />} />
                            <Route path="recipes/create" element={<RecipeCreate />} />
                            <Route path="recipes/my-recipes" element={<MyRecipes />} />
                            <Route path="recipes/saved" element={<SavedRecipes />} />
                            <Route path="recipes/:id" element={<RecipeDetail />} />
                            <Route path="recipes/:id/edit" element={<RecipeEdit />} />
                            
                            {/* Auth Routes */}
                            <Route path="login" element={<Login />} />
                            <Route path="register" element={<Register />} />
                            <Route path="profile" element={<Profile />} />
                            
                            {/* Info Routes */}
                            <Route path="about" element={<AboutUs />} />
                        </Route>
                    </Routes>
                </BrowserRouter>
            </AuthProvider>
        </ErrorBoundary>
    );
}

console.log('About to mount React app...');

ReactDOM.createRoot(document.getElementById('app')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);
