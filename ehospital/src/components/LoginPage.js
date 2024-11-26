import React, { useState } from 'react';
import './LoginPage.css'; 

function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username === 'testuser' && password === 'password') {
      onLoginSuccess();
    } else {
      alert('Invalid login credentials');
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h2>Welcome Back!</h2>
          <p>Please log in to continue</p>
        </div>
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input 
              id="username" 
              type="text" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)} 
              placeholder="Enter your username" 
              required 
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input 
              id="password" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="Enter your password" 
              required 
            />
          </div>
          <button type="submit" className="login-button">Log In</button>
        </form>
        <div className="forgot-password">
          <a href="#">Forgot your password?</a>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
