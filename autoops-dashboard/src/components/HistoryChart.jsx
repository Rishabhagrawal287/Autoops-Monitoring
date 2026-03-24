import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

function HistoryChart({ data, dataKey, color, title }) {
  return (
    <div style={{ marginBottom: "30px" }}>
      <h3>{title}</h3>

      <LineChart width={600} height={250} data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        {/* ✅ Better timestamp formatting */}
        <XAxis
          dataKey="timestamp"
          tickFormatter={(time) =>
            new Date(time).toLocaleTimeString()
          }
        />

        <YAxis />
        <Tooltip
          labelFormatter={(label) =>
            new Date(label).toLocaleString()
          }
        />

        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          dot={false}   // smoother chart
        />
      </LineChart>
    </div>
  );
}

export default HistoryChart;