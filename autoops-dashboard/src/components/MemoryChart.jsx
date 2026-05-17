import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function MemoryChart({ memory }) {
  const [data, setData] = useState([]);

  if (data.length === 0 || data[data.length - 1].memory !== memory) {
    const newData = [
      ...data.slice(-20),
      {
        time: new Date().toLocaleTimeString(),
        memory: memory,
      },
    ];
    setData(newData);
  }

  return (
    <div>
      <h3>Memory Usage</h3>
      <LineChart width={300} height={200} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" hide />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line type="monotone" dataKey="memory" stroke="#82ca9d" dot={false} />
      </LineChart>
    </div>
  );
}

export default MemoryChart;