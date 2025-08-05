import React, { useState } from 'react';
import api from '../services/api';

function Register({ onLogin }) {
  const [name, setName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await api.post('/users/', {
        name,
        phone_number: phoneNumber
      });
      onLogin(response.data);
    } catch (err) {
      if (err.response?.status === 400) {
        setError('Phone number already registered. Please login.');
        handleLogin();
      } else {
        setError('Failed to register. Please try again.');
      }
    }
  };

  const handleLogin = async () => {
    try {
      const response = await api.get(`/users/phone/${phoneNumber}`);
      onLogin(response.data);
    } catch (err) {
      setError('User not found. Please register first.');
    }
  };

  return (
    <div className="card">
      <h2>👋 Get Started</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Register with your name and phone number to join SMS group chats
      </p>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Your Name:</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter your full name"
            required
          />
        </div>
        <div className="form-group">
          <label>Phone Number:</label>
          <input
            type="tel"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="+1234567890 (with country code)"
            required
          />
          <small style={{ color: '#666', fontSize: '14px' }}>
            Include country code (e.g., +1 for US)
          </small>
        </div>
        
        <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
          <button type="submit" className="btn btn-primary">
            ✨ Register
          </button>
          <button type="button" className="btn btn-secondary" onClick={handleLogin}>
            🔑 Login (Existing User)
          </button>
        </div>
      </form>
      
      <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px', fontSize: '14px', color: '#666' }}>
        <strong>How it works:</strong>
        <ul style={{ margin: '10px 0', paddingLeft: '20px' }}>
          <li>Register with your phone number</li>
          <li>Browse and join group chats</li>
          <li>Receive SMS when you join a group</li>
          <li>Reply to SMS to send messages to the group</li>
        </ul>
      </div>
    </div>
  );
}

export default Register;