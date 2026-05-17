import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function ServerGrid({ token, onSelectServer }) {
  const [servers, setServers]   = useState([]);
  const [metrics, setMetrics]   = useState({});
  const [loading, setLoading]   = useState(true);

  // Fetch server list
  useEffect(() => {
    if (!token) return;
    fetch(`${API_BASE}/servers`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setServers(data.servers || []))
      .catch(console.error);
  }, [token]);

  // Fetch latest metrics for each server
  useEffect(() => {
    if (!servers.length) return;
    const fetchAll = async () => {
      const results = {};
      for (const server of servers) {
        try {
          const res = await fetch(
            `${API_BASE}/server/${server.name}?limit=1`,
            { headers: { Authorization: `Bearer ${token}` } }
          );
          const data = await res.json();
          if (data.length > 0) results[server.name] = data[0];
        } catch (e) {
          console.error(e);
        }
      }
      setMetrics(results);
      setLoading(false);
    };
    fetchAll();
    const interval = setInterval(fetchAll, 5000);
    return () => clearInterval(interval);
  }, [servers, token]);

  function getColor(value, warn, danger) {
    if (value >= danger) return "#f85149";
    if (value >= warn)   return "#e3b341";
    return "#3fb950";
  }

  if (loading) return (
    <div style={{ textAlign:"center", padding:"40px", color:"var(--text-secondary)", fontFamily:"var(--font-mono)" }}>
      Loading servers...
    </div>
  );

  return (
    <div style={{ padding:"24px" }}>
      <h2 style={{ color:"var(--text-primary)", fontFamily:"var(--font-display)", marginBottom:"20px", fontSize:"1.2rem" }}>
        All Servers — Overview
      </h2>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(280px, 1fr))", gap:"16px" }}>
        {servers.map(server => {
          const m = metrics[server.name];
          const cpu    = m?.cpu    ?? 0;
          const memory = m?.memory ?? 0;
          const disk   = m?.disk   ?? 0;

          return (
            <div
              key={server.name}
              onClick={() => onSelectServer(server.name)}
              style={{
                background: "var(--bg-surface)",
                border: `1px solid ${server.online ? "rgba(56,139,253,0.3)" : "rgba(248,81,73,0.3)"}`,
                borderRadius: "12px",
                padding: "20px",
                cursor: "pointer",
                transition: "transform 0.2s, box-shadow 0.2s",
              }}
              onMouseEnter={e => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.3)";
              }}
              onMouseLeave={e => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              {/* Server name + status */}
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"16px" }}>
                <span style={{ color:"var(--text-primary)", fontFamily:"var(--font-mono)", fontWeight:600, fontSize:"0.9rem" }}>
                  {server.name}
                </span>
                <span style={{
                  fontSize:"0.7rem",
                  fontFamily:"var(--font-mono)",
                  padding:"3px 8px",
                  borderRadius:"20px",
                  background: server.online ? "rgba(63,185,80,0.1)" : "rgba(248,81,73,0.1)",
                  color: server.online ? "#3fb950" : "#f85149",
                  border: `1px solid ${server.online ? "rgba(63,185,80,0.3)" : "rgba(248,81,73,0.3)"}`,
                }}>
                  {server.online ? "● Online" : "● Offline"}
                </span>
              </div>

              {/* Metric bars */}
              {[
                { label:"CPU",    value:cpu,    warn:70, danger:90  },
                { label:"Memory", value:memory, warn:80, danger:92  },
                { label:"Disk",   value:disk,   warn:75, danger:90  },
              ].map(({ label, value, warn, danger }) => (
                <div key={label} style={{ marginBottom:"10px" }}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:"4px" }}>
                    <span style={{ fontSize:"0.72rem", color:"var(--text-secondary)", fontFamily:"var(--font-mono)" }}>{label}</span>
                    <span style={{ fontSize:"0.72rem", color: getColor(value, warn, danger), fontFamily:"var(--font-mono)", fontWeight:600 }}>
                      {value.toFixed(1)}%
                    </span>
                  </div>
                  <div style={{ height:"4px", background:"var(--bg-elevated)", borderRadius:"2px", overflow:"hidden" }}>
                    <div style={{
                      height:"100%",
                      width:`${Math.min(value, 100)}%`,
                      background: getColor(value, warn, danger),
                      borderRadius:"2px",
                      transition:"width 0.5s ease"
                    }} />
                  </div>
                </div>
              ))}

              <div style={{ marginTop:"12px", fontSize:"0.72rem", color:"var(--text-muted)", fontFamily:"var(--font-mono)" }}>
                Click to view details →
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}