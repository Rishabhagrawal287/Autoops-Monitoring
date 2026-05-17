import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function CPUChart({ cpu }) {
  const [data, setData] = useState([]);

  // ✅ SAFE STATE UPDATE (NO useEffect)
  if (data.length === 0 || data[data.length - 1].cpu !== cpu) {
    const newData = [
      ...data.slice(-20),
      {
        time: new Date().toLocaleTimeString(),
        cpu: cpu,
      },
    ];
    setData(newData);
  }

  return (
    <div>
      <h3>CPU Usage</h3>
      <LineChart width={300} height={200} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" hide />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line type="monotone" dataKey="cpu" stroke="#8884d8" dot={false} />
      </LineChart>
    </div>
  );
}

export default CPUChart;