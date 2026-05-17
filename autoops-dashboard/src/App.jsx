import { useEffect, useState, useRef } from "react";
import CPUChart from "./components/CPUChart";
import MemoryChart from "./components/MemoryChart";
import DiskChart from "./components/DiskChart";
import HistoryChart from "./components/HistoryChart";
import ServerGrid from "./components/ServerGrid";
import "./App.css";

function App() {
  const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  const [metrics, setMetrics]               = useState(null);
  const [servers, setServers]               = useState([]);
  const [selectedServer, setSelectedServer] = useState("");
  const [theme, setTheme]                   = useState(localStorage.getItem("autoops_theme") || "dark");
  const [history, setHistory]               = useState([]);
  const [historyRange, setHistoryRange]     = useState("all");
  const [view, setView]                     = useState("dashboard");
  const [userInteracted, setUserInteracted] = useState(false);
  const [token, setToken]                   = useState(localStorage.getItem("autoops_token") || "");
  const [loggedIn, setLoggedIn]             = useState(!!localStorage.getItem("autoops_token"));
  const [loginError, setError]              = useState("");

  const alertAudioRef = useRef(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const res = await fetch(`${API_BASE}/token`, {
      method: "POST",
      body: new URLSearchParams({
        username: form.get("username"),
        password: form.get("password")
      })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("autoops_token", data.access_token);
      setToken(data.access_token);
      setLoggedIn(true);
    } else {
      setError("Invalid username or password");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("autoops_token");
    setToken("");
    setLoggedIn(false);
  };

  // THEME EFFECT
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("autoops_theme", theme);
  }, [theme]);

  // FETCH SERVERS
  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/servers`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => {
        if (res.status === 401) { handleLogout(); return null; }
        return res.json();
      })
      .then((data) => {
        if (!data) return;
        const serverList = data.servers || [];
        setServers(serverList);
        if (serverList.length > 0) setSelectedServer(serverList[0].name);
      })
      .catch((err) => console.error("Error fetching servers:", err));
  }, [token]);

  // FETCH HISTORY
  useEffect(() => {
    if (!selectedServer) return;
    fetch(`${API_BASE}/history?server=${selectedServer}&range=${historyRange}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => res.json())
      .then((data) => setHistory(data))
      .catch((err) => console.error("History error:", err));
  }, [selectedServer, historyRange]);

  // WEBSOCKET
  useEffect(() => {
    if (!selectedServer) return;
    const socket = new WebSocket(`${API_BASE.replace('http', 'ws')}/ws/${selectedServer}`);
    socket.onopen = () => console.log("Connected to:", selectedServer);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.alerts && data.alerts.length > 0 && alertAudioRef.current && userInteracted) {
        alertAudioRef.current.currentTime = 0;
        alertAudioRef.current.play().catch(() => {});
      }
      setMetrics(data);
    };
    socket.onclose = () => console.log("Disconnected from:", selectedServer);
    return () => socket.close();
  }, [selectedServer, userInteracted]);

  // LOGIN SCREEN
  if (!loggedIn) {
    return (
      <div className="dashboard" style={{ display:"flex", alignItems:"center", justifyContent:"center", minHeight:"100vh" }}>
        <div className="card" style={{ padding:"32px", minWidth:"320px" }}>
          <h2 style={{ marginBottom:"20px", color:"var(--text-primary)" }}>AutoOps Login</h2>
          <form onSubmit={handleLogin} style={{ display:"flex", flexDirection:"column", gap:"12px" }}>
            <input name="username" placeholder="Username" defaultValue="admin"
              style={{ background:"var(--bg-elevated)", border:"1px solid var(--border-subtle)", borderRadius:"6px", padding:"10px 14px", color:"var(--text-primary)", fontFamily:"monospace" }} />
            <input name="password" type="password" placeholder="Password"
              style={{ background:"var(--bg-elevated)", border:"1px solid var(--border-subtle)", borderRadius:"6px", padding:"10px 14px", color:"var(--text-primary)", fontFamily:"monospace" }} />
            {loginError && <span style={{ color:"#f85149", fontSize:"0.8rem" }}>{loginError}</span>}
            <button type="submit"
              style={{ background:"#3b82f6", color:"#fff", border:"none", borderRadius:"6px", padding:"10px", cursor:"pointer", fontWeight:600 }}>
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  // CONNECTING SCREEN
  if (!metrics || !selectedServer) {
    return (
      <div className="dashboard" style={{ display:"flex", alignItems:"center", justifyContent:"center", minHeight:"100vh" }}>
        <div style={{ textAlign:"center", color:"#94a3b8", fontFamily:"monospace" }}>
          <p>Connecting to {selectedServer || "AutoOps"}...</p>
          <p style={{ fontSize:"0.75rem", marginTop:"8px" }}>
            Make sure the backend is running at localhost:8000
          </p>
        </div>
      </div>
    );
  }

  // MAIN DASHBOARD
  return (
    <div className="dashboard" onClick={() => setUserInteracted(true)}>

      {/* ── Header ───────────────────────────────────────────── */}
      <h1 style={{ textAlign:"center", marginBottom:"8px", paddingRight:"120px", paddingLeft:"120px" }}>
        AutoOps Monitoring Dashboard
      </h1>

      {/* ── Header controls — top right, never overlapping ───── */}
      <div className="header-controls">
        <button
          className="btn-icon"
          onClick={(e) => { e.stopPropagation(); setTheme(theme === "dark" ? "light" : "dark"); }}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}>
          {theme === "dark" ? "☀" : "🌙"}
        </button>
        <button className="btn-signout" onClick={(e) => { e.stopPropagation(); handleLogout(); }}>
          Sign Out
        </button>
      </div>

      {/* ── View toggle ──────────────────────────────────────── */}
      <div style={{ display:"flex", gap:"8px", justifyContent:"center", marginBottom:"24px", marginTop:"8px" }}>
        <button onClick={() => setView("dashboard")}
          style={{ padding:"6px 16px", borderRadius:"6px", cursor:"pointer", background: view === "dashboard" ? "#3b82f6" : "var(--bg-elevated)", color: view === "dashboard" ? "#fff" : "var(--text-secondary)", border:"1px solid var(--border-subtle)", fontFamily:"monospace", fontSize:"0.8rem" }}>
          Single Server
        </button>
        <button onClick={() => setView("overview")}
          style={{ padding:"6px 16px", borderRadius:"6px", cursor:"pointer", background: view === "overview" ? "#3b82f6" : "var(--bg-elevated)", color: view === "overview" ? "#fff" : "var(--text-secondary)", border:"1px solid var(--border-subtle)", fontFamily:"monospace", fontSize:"0.8rem" }}>
          All Servers
        </button>
      </div>

      {/* ── View switch ──────────────────────────────────────── */}
      {view === "overview" ? (
        <ServerGrid
          token={token}
          onSelectServer={(name) => {
            setSelectedServer(name);
            setView("dashboard");
          }}
        />
      ) : (
        <>
          {/* SERVER SELECT */}
          <div className="server-select">
            <h3>Select Server:</h3>
            <select value={selectedServer} onChange={(e) => setSelectedServer(e.target.value)}>
              {servers.map((server, index) => (
                <option key={index} value={server.name}>
                  {server.name} {server.online ? "🟢" : "🔴"}
                </option>
              ))}
            </select>
          </div>

          {/* CARDS */}
          <div className="cards">
            <div className="card cpu"><h3>CPU</h3><p>{metrics.cpu_percent}%</p></div>
            <div className="card memory"><h3>Memory</h3><p>{metrics.memory_percent}%</p></div>
            <div className="card disk"><h3>Disk</h3><p>{metrics.disk_percent}%</p></div>
          </div>

          {/* LIVE CHARTS */}
          <div className="charts">
            <CPUChart cpu={metrics.cpu_percent} />
            <MemoryChart memory={metrics.memory_percent} />
            <DiskChart disk={metrics.disk_percent} />
          </div>

          {/* HISTORY */}
          <div className="history" style={{ paddingBottom:"20px" }}>
            <div style={{ display:"flex", gap:"8px", marginBottom:"12px" }}>
              {["1h","6h","24h","all"].map(r => (
                <button key={r} onClick={() => setHistoryRange(r)}
                  style={{ padding:"6px 14px", borderRadius:"6px", border:"1px solid var(--border-subtle)", background: historyRange === r ? "#3b82f6" : "var(--bg-elevated)", color: historyRange === r ? "#fff" : "var(--text-secondary)", cursor:"pointer", fontFamily:"monospace", fontSize:"0.8rem", fontWeight: historyRange === r ? 600 : 400 }}>
                  {r === "all" ? "All" : r.toUpperCase()}
                </button>
              ))}
            </div>
            <h2>Historical Trends</h2>
            <HistoryChart data={history} dataKey="cpu"    color="#8884d8" title="CPU History"    />
            <HistoryChart data={history} dataKey="memory" color="#82ca9d" title="Memory History" />
            <HistoryChart data={history} dataKey="disk"   color="#ff7300" title="Disk History"   />
          </div>

          {/* ALERTS */}
          <div className="alerts">
            <h2>🚨 Alerts</h2>
            <audio ref={alertAudioRef} src="./alert.mp3" />
            {!metrics.alerts || metrics.alerts.length === 0 ? (
              <p>No alerts detected</p>
            ) : (
              metrics.alerts.slice().reverse().map((alert, index) => (
                <div key={index} className="alert-box">
                  <b>{alert.time || "N/A"}</b> — {alert.message || "Unknown alert"}
                </div>
              ))
            )}
          </div>

          {/* HEALING */}
          <div className="healing">
            <h2>Auto-Healing Actions</h2>
            {!metrics.healing_actions || metrics.healing_actions.length === 0 ? (
              <p>No healing actions triggered</p>
            ) : (
              metrics.healing_actions.map((action, index) => (
                <div key={index} className="heal-box">
                  <b>{action.time}</b> — {action.action}
                </div>
              ))
            )}
          </div>
        </>
      )}

    </div>
  );
}

export default App;