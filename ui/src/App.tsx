// App.tsx
import React, { useState, useEffect } from 'react';
import './style.css';

const currentMonthYear = new Date().toLocaleString('default', {
  month: 'long',
  year: 'numeric',
});

const CENTRES = ["Papamoa Beach", "Livingstone Drive", "The Bach", "Terrace Views", "The Boulevard", "West Dune"];

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [messages, setMessages] = useState([{ sender: 'agent', text: 'Kia ora! How can I help you today?' }]);
  const [input, setInput] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [occupancyData, setOccupancyData] = useState({});

  useEffect(() => {
    if (loggedIn && currentTab === 'dashboard') {
      fetch('http://localhost:8000/occupancy')
        .then(res => res.json())
        .then(data => setOccupancyData(data))
        .catch(err => console.error('Failed to fetch occupancy data:', err));
    }
  }, [loggedIn, currentTab]);

  const handleSend = () => {
    if (input.trim() === '') return;
    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);
    setInput('');
    setTimeout(() => {
      setMessages(prev => [...prev, { sender: 'agent', text: 'Thanks for your message!' }]);
    }, 600);
  };

  const handleLogout = () => {
    document.body.classList.add('logged-out');
    setLoggedIn(false);
  };

  const handleLogin = () => {
    if (email === 'courtney@futurefocus.co.nz' && password === 'futurefocus') {
      setLoggedIn(true);
      document.body.classList.remove('logged-out');
    } else {
      alert('Invalid login');
    }
  };

  if (!loggedIn) {
    return (
      <div className="chat-app">
        <h1>Login to FutureFocus</h1>
        <input type="text" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button onClick={handleLogin}>Log In</button>
      </div>
    );
  }

  return (
    <div className="chat-app">
      <div className="chat-header">
        <img src="logo.png" alt="Future Focus Logo" className="logo" style={{ width: '160px', height: 'auto' }} />
        <h1>Knowledge<span className="highlight">Base</span></h1>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>

      {/* 👇 Tabs */}
      <div className="tabs">
        <button onClick={() => setCurrentTab('dashboard')} className={currentTab === 'dashboard' ? 'active' : ''}>✨ Dashboard</button>
        <button onClick={() => setCurrentTab('ai')} className={currentTab === 'ai' ? 'active' : ''}>✨ Future Focus AI</button>
        <button onClick={() => setCurrentTab('coming')} className={currentTab === 'coming' ? 'active' : ''}>✨ Coming Soon</button>
        <button onClick={() => setCurrentTab('learning')} className={currentTab === 'learning' ? 'active' : ''}>✨ Learning Hub</button>
        <button onClick={() => setCurrentTab('resources')} className={currentTab === 'resources' ? 'active' : ''}>✨ Marketing</button>
      </div>

      {/* 👇 Dashboard Tab */}
      {currentTab === 'dashboard' && (
        <div className="main-content">
          <div className="occupancy-section">
            <h2 className="occupancy-title">{currentMonthYear} Occupancy</h2>
            <div className="occupancy-group">
              {CENTRES.map(centre => (
                <div className="occupancy-item" key={centre}>
                  <div className="occupancy-name">{centre}</div>
                  <div className="occupancy-donut" style={{ background: `conic-gradient(#7aaeff 0% ${occupancyData[centre]?.total || 0}%, #ddd ${occupancyData[centre]?.total || 0}% 100%)` }}>
                    {occupancyData[centre]?.total || 0}%
                  </div>
                  <div className="sub-donuts">
                    <div className="sub-donut" style={{ background: `conic-gradient(#a3d3ff 0% ${occupancyData[centre]?.u2 || 0}%, #ddd ${occupancyData[centre]?.u2 || 0}% 100%)` }}>
                      <div className="sub-label">U2</div>
                      <div className="sub-percent">{occupancyData[centre]?.u2 || 0}%</div>
                    </div>
                    <div className="sub-donut" style={{ background: `conic-gradient(#a3d3ff 0% ${occupancyData[centre]?.o2 || 0}%, #ddd ${occupancyData[centre]?.o2 || 0}% 100%)` }}>
                      <div className="sub-label">O2</div>
                      <div className="sub-percent">{occupancyData[centre]?.o2 || 0}%</div>
                    </div>
                  </div>
                </div>
              ))}

              {/* 👇 Group Occupancy block */}
              <div className="occupancy-item">
                <div className="occupancy-name">Group Occupancy</div>
                <div className="occupancy-donut" style={{ background: 'conic-gradient(#7aaeff 0% 0%, #ddd 0% 100%)' }}>
                  0%
                </div>
                <div className="sub-donuts">
                  <div className="sub-donut" style={{ background: 'conic-gradient(#a3d3ff 0% 0%, #ddd 0% 100%)' }}>
                    <div className="sub-label">U2</div>
                    <div className="sub-percent">0%</div>
                  </div>
                  <div className="sub-donut" style={{ background: 'conic-gradient(#a3d3ff 0% 0%, #ddd 0% 100%)' }}>
                    <div className="sub-label">O2</div>
                    <div className="sub-percent">0%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 👇 AI Tab */}
      {currentTab === 'ai' && (
        <div className="chat-section">
          <div className="chat-box">
            <div className="chat-history">
              {messages.map((msg, idx) => (
                <div key={idx} className={`chat-bubble ${msg.sender}`}>
                  <strong>{msg.sender === 'agent' ? 'Agent:' : 'You:'}</strong> {msg.text}
                </div>
              ))}
            </div>
            <div className="chat-input-area">
              <input
                type="text"
                value={input}
                placeholder="Ask something like 'What are the licensing rules?'"
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
              />
              <button className="send-btn" onClick={handleSend}>⚡ Ask</button>
            </div>
          </div>
        </div>
      )}

      {/* 👇 Coming Soon Tab */}
      {currentTab === 'coming' && (
        <div style={{ marginTop: '2rem', fontSize: '1.25rem', textAlign: 'center' }}>
          🚧 This feature is under construction!
        </div>
      )}
    </div>
  );
}
