"use client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface ScoreChartProps {
  data: Array<{
    city: string;
    tier: string;
    count: number;
    avg_score: number;
  }>;
}

const TIER_COLORS: Record<string, string> = {
  hot: "#ef4444",
  warm: "#f59e0b",
  cold: "#3b82f6",
};

export default function ScoreChart({ data }: ScoreChartProps) {
  const cityData = data.reduce((acc: Record<string, any>, row) => {
    if (!acc[row.city]) {
      acc[row.city] = { city: row.city, hot: 0, warm: 0, cold: 0 };
    }
    acc[row.city][row.tier] = row.count;
    return acc;
  }, {});

  const chartData = Object.values(cityData);

  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: "12px",
        padding: "20px",
        border: "1px solid #334155",
      }}
    >
      <h3 style={{ color: "#f1f5f9", marginBottom: "16px", fontSize: "15px" }}>
        Lead Distribution by City
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={chartData}>
          <XAxis dataKey="city" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "8px",
              color: "#f1f5f9",
            }}
          />
          <Bar dataKey="hot" name="Hot" fill="#ef4444" radius={[4, 4, 0, 0]} />
          <Bar
            dataKey="warm"
            name="Warm"
            fill="#f59e0b"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="cold"
            name="Cold"
            fill="#3b82f6"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}