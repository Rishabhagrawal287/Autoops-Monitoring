import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { useEffect, useState } from "react";

function MemoryChart({ memory }) {

  const [data, setData] = useState([]);

  useEffect(() => {

    const updateChart = () => {
      setData((prev) => [
        ...prev.slice(-20),
        { time: new Date().toLocaleTimeString(), memory }
      ]);
    };

    const timer = setTimeout(updateChart, 0);

    return () => clearTimeout(timer);

  }, [memory]);

  return (
    <div>
      <h3>Memory Usage</h3>

      <LineChart width={400} height={200} data={data}>
        <XAxis dataKey="time"/>
        <YAxis/>
        <Tooltip/>
        <Line type="monotone" dataKey="memory"/>
      </LineChart>
    </div>
  );
}

export default MemoryChart;