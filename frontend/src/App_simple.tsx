import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🧠 CogniFlow</h1>
        <h2>AI-Powered Learning Platform</h2>
        <p>Frontend is now running successfully!</p>
        
        <div className="service-status">
          <h3>Service Status</h3>
          <div>
            <span className="status-indicator">🟢</span> Frontend (React): Running on port 3000
          </div>
          <div>
            <span className="status-indicator">🟢</span> Courses Service: Running on port 8003
          </div>
        </div>
        
        <div className="quick-test">
          <h3>Quick Test</h3>
          <button onClick={() => {
            fetch('http://localhost:8003/')
              .then(response => response.json())
              .then(data => alert(JSON.stringify(data)))
              .catch(error => alert('Error: ' + error));
          }}>
            Test Courses Service
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;
