import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Investigate from './pages/Investigate';

function NavBar() {
    const location = useLocation();
    return (
        <nav className="navbar">
            <div className="nav-brand">CyberTrace AI</div>
            <div className="nav-links">
                <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Dashboard</Link>
                <Link to="/investigate" className={location.pathname === '/investigate' ? 'active' : ''}>Investigation</Link>
            </div>
        </nav>
    );
}

function App() {
    return (
        <Router>
            <div className="app-bg">
                <NavBar />
                <main className="container">
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/investigate" element={<Investigate />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
