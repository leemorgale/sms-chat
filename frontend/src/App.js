import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Register from './components/Register';
import GroupList from './components/GroupList';
import GroupDetail from './components/GroupDetail';
import api from './services/api';

function App() {
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogin = (user) => {
    setCurrentUser(user);
    localStorage.setItem('currentUser', JSON.stringify(user));
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('currentUser');
  };

  return (
    <Router>
      <div className="container">
        <div className="header">
          <h1>📱 Group SMS Chat</h1>
          <div className="subtitle">Connect with groups via SMS and web interface</div>
        </div>
        
        {!currentUser && (
          <div className="demo-banner">
            <strong>Demo Mode:</strong> Try with any phone number (SMS will be mocked)
          </div>
        )}
        
        {currentUser && (
          <div className="user-info">
            <div>
              <div className="welcome">Welcome, {currentUser.name}!</div>
              <div className="phone">{currentUser.phone_number}</div>
            </div>
            <button className="btn btn-secondary" onClick={handleLogout}>
              🚪 Logout
            </button>
          </div>
        )}
        
        <Routes>
          <Route 
            path="/" 
            element={currentUser ? <Navigate to="/groups" /> : <Register onLogin={handleLogin} />} 
          />
          <Route 
            path="/groups" 
            element={currentUser ? <GroupList currentUser={currentUser} /> : <Navigate to="/" />} 
          />
          <Route 
            path="/groups/:groupId" 
            element={currentUser ? <GroupDetail currentUser={currentUser} /> : <Navigate to="/" />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;