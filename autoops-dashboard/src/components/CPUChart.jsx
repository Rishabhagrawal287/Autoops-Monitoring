import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { useEffect, useState } from "react";

function CPUChart({ cpu }) {

  const [data, setData] = useState([]);

  useEffect(() => {

    const updateChart = () => {
      setData((prev) => [
        ...prev.slice(-20),
        { time: new Date().toLocaleTimeString(), cpu }
      ]);
    };

    const timer = setTimeout(updateChart, 0);

    return () => clearTimeout(timer);

  }, [cpu]);

  return (
    <div>
      <h3>CPU Usage</h3>

      <LineChart width={400} height={200} data={data}>
        <XAxis dataKey="time"/>
        <YAxis/>
        <Tooltip/>
        <Line type="monotone" dataKey="cpu"/>
      </LineChart>
    </div>
  );
}

export default CPUChart;