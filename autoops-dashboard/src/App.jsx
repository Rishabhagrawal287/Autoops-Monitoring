import { useEffect, useState } from "react";
import CPUChart from "./components/CPUChart";
import MemoryChart from "./components/MemoryChart";
import DiskChart from "./components/DiskChart";
import HistoryChart from "./components/HistoryChart";
import "./App.css";

function App() {
  const [metrics, setMetrics] = useState(null);
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState("");
  const [history, setHistory] = useState([]);

  // ✅ FETCH SERVERS
  useEffect(() => {
    fetch("http://127.0.0.1:8000/servers")
      .then((res) => res.json())
      .then((data) => {
        const serverList = data.servers || []; // ✅ FIXED
        setServers(serverList);

        if (serverList.length > 0) {
          setSelectedServer(serverList[0]);
        }
      })
      .catch((err) => console.error("Error fetching servers:", err));
  }, []);

  // ✅ FETCH HISTORY WHEN SERVER CHANGES
  useEffect(() => {
    if (!selectedServer) return;

    fetch(`http://127.0.0.1:8000/server/${selectedServer}`)
      .then((res) => res.json())
      .then((data) => setHistory(data))
      .catch((err) => console.error("History error:", err));
  }, [selectedServer]);

  // ✅ WEBSOCKET (SERVER-SPECIFIC)
  useEffect(() => {
    if (!selectedServer) return;

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/${selectedServer}`
    );

    socket.onopen = () => {
      console.log("Connected to:", selectedServer);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMetrics(data);
    };

    socket.onclose = () => {
      console.log("Disconnected from:", selectedServer);
    };

    return () => {
      socket.close();
    };
  }, [selectedServer]);

  // ✅ LOADING STATE
  if (!metrics || !selectedServer) {
    return <h2 style={{ textAlign: "center" }}>Connecting to AutoOps...</h2>;
  }

  return (
    <div className="dashboard">
      <h1>AutoOps Monitoring Dashboard</h1>

      {/* ✅ SERVER SELECT */}
      <div className="server-select">
        <h3>Select Server:</h3>
        <select
          value={selectedServer}
          onChange={(e) => setSelectedServer(e.target.value)}
        >
          {servers.map((server, index) => (
            <option key={index} value={server}>
              {server}
            </option>
          ))}
        </select>
      </div>

      {/* ✅ LIVE CHARTS */}
      <div className="charts">
        <CPUChart cpu={metrics.cpu_percent} />
        <MemoryChart memory={metrics.memory_percent} />
        <DiskChart disk={metrics.disk_percent} />
      </div>

      {/* ✅ HISTORY CHARTS (NEW 🔥) */}
      <div className="history">
        <h2>Historical Trends</h2>

        <HistoryChart
          data={history}
          dataKey="cpu"
          color="#8884d8"
          title="CPU History"
        />

        <HistoryChart
          data={history}
          dataKey="memory"
          color="#82ca9d"
          title="Memory History"
        />

        <HistoryChart
          data={history}
          dataKey="disk"
          color="#ff7300"
          title="Disk History"
        />
      </div>

      {/* ✅ ALERTS */}
      <div className="alerts">
        <h2>AI Alerts</h2>

        {!metrics.alerts || metrics.alerts.length === 0 ? (
          <p>No alerts detected</p>
        ) : (
          metrics.alerts.map((alert, index) => (
            <div key={index} className="alert-box">
              <b>{alert.time}</b> — {alert.message}
            </div>
          ))
        )}
      </div>

      {/* ✅ HEALING */}
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
    </div>
  );
}

export default App;