import { LineChart, Line, XAxis, YAxis, Tooltip } from "recharts";
import { useEffect, useState } from "react";

function DiskChart({ disk }) {

  const [data, setData] = useState([]);

  useEffect(() => {

    const updateChart = () => {
      setData((prev) => [
        ...prev.slice(-20),
        { time: new Date().toLocaleTimeString(), disk }
      ]);
    };

    const timer = setTimeout(updateChart, 0);

    return () => clearTimeout(timer);

  }, [disk]);

  return (
    <div>
      <h3>Disk Usage</h3>

      <LineChart width={400} height={200} data={data}>
        <XAxis dataKey="time"/>
        <YAxis/>
        <Tooltip/>
        <Line type="monotone" dataKey="disk"/>
      </LineChart>
    </div>
  );
}

export default DiskChart;