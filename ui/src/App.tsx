// App.tsx
import React, { useState, useEffect } from 'react';
import './style.css';

const CENTRES = ["Papamoa Beach", "Livingstone Drive", "The Bach", "Terrace Views", "The Boulevard"];

export default function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [messages, setMessages] = useState([{ sender: 'agent', text: 'Kia ora! How can I help you today?' }]);
  const [input, setInput] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [occupancyData, setOccupancyData] = useState({});

  useEffect(() => {
    if (loggedIn) {
      fetch('http://localhost:8000/occupancy')
        .then(res => res.json())
        .then(data => setOccupancyData(data))
        .catch(err => console.error('Failed to fetch occupancy data:', err));
    }
  }, [loggedIn]);

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

  const handleGetStaffHours = async () => {
    const res = await fetch('http://localhost:8000/staff-hours-this-week/all');
    const data = await res.json();
    const formatted = Object.entries(data)
      .map(([centre, value]) =>
        value.staff_hours ? `${centre}: ${value.staff_hours}` : `${centre}: ❌ ${value.error}`
      )
      .join('\n');
    setMessages(prev => [...prev, { sender: 'agent', text: `📊 Staff Hours:\n${formatted}` }]);
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
        <img src="logo.png" alt="Future Focus Logo" className="logo" style={{ width: '80px', height: 'auto' }} />
        <h1>FutureFocus<span className="highlight">AI</span></h1>
        <button className="logout-button" onClick={handleLogout}>Logout</button>
      </div>

      <div className="main-content">
        <div className="occupancy-section">
          <h2 className="occupancy-title">Occupancy</h2>
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
          </div>
        </div>

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
                placeholder="Ask something like 'What's the staff % this month?'"
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
              />
              <button className="send-btn" onClick={handleSend}>⚡ Ask FutureFocus</button>
            </div>
          </div>

          <div className="utility-buttons">
            <button onClick={handleGetStaffHours}>📊 Staff Hours This Week</button>
          </div>
        </div>
      </div>
    </div>
  );
}
