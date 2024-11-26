// src/App.js
import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import LoginPage from './components/LoginPage'; 
import HomePage from './pages/HomePage'; 

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Define handleLogin function
  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <div>
      <Header />
      <main style={{ minHeight: '80vh', padding: '20px' }}>
        {isLoggedIn ? (
          <HomePage />
        ) : (
          <LoginPage onLoginSuccess={handleLogin} />
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;
