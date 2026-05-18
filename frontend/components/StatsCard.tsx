interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
  icon?: string;
}

export default function StatsCard({
  title,
  value,
  subtitle,
  color = "#3b82f6",
  icon,
}: StatsCardProps) {
  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: "12px",
        padding: "20px",
        border: "1px solid #334155",
        borderLeft: `4px solid ${color}`,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <p style={{ color: "#94a3b8", fontSize: "13px", marginBottom: "8px" }}>
          {title}
        </p>
        {icon && <span style={{ fontSize: "20px" }}>{icon}</span>}
      </div>
      <p
        style={{
          fontSize: "28px",
          fontWeight: "700",
          color: "#f1f5f9",
        }}
      >
        {value}
      </p>
      {subtitle && (
        <p style={{ color: "#64748b", fontSize: "12px", marginTop: "4px" }}>
          {subtitle}
        </p>
      )}
    </div>
  );
}