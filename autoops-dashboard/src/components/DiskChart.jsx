import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function DiskChart({ disk }) {
  const [data, setData] = useState([]);

  if (data.length === 0 || data[data.length - 1].disk !== disk) {
    const newData = [
      ...data.slice(-20),
      {
        time: new Date().toLocaleTimeString(),
        disk: disk,
      },
    ];
    setData(newData);
  }

  return (
    <div>
      <h3>Disk Usage</h3>
      <LineChart width={300} height={200} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" hide />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line type="monotone" dataKey="disk" stroke="#ff7300" dot={false} />
      </LineChart>
    </div>
  );
}

export default DiskChart;