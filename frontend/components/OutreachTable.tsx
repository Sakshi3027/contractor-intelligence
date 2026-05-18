"use client";
import { Outreach } from "@/lib/api";

interface OutreachTableProps {
  outreach: Outreach[];
}

const statusConfig: Record<string, { color: string; bg: string }> = {
  pending: { color: "#f59e0b", bg: "#451a03" },
  sent: { color: "#3b82f6", bg: "#172554" },
  opened: { color: "#8b5cf6", bg: "#2e1065" },
  replied: { color: "#10b981", bg: "#022c22" },
  bounced: { color: "#ef4444", bg: "#450a0a" },
};

export default function OutreachTable({ outreach }: OutreachTableProps) {
  return (
    <div
      style={{
        background: "#1e293b",
        borderRadius: "12px",
        border: "1px solid #334155",
        overflow: "hidden",
      }}
    >
      <div style={{ padding: "20px 20px 12px" }}>
        <h3 style={{ color: "#f1f5f9", fontSize: "15px" }}>
          Outreach Campaigns ({outreach.length})
        </h3>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#0f172a" }}>
              {["To", "Subject", "Status", "Created"].map((h) => (
                <th
                  key={h}
                  style={{
                    padding: "10px 16px",
                    textAlign: "left",
                    color: "#64748b",
                    fontSize: "12px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {outreach.map((o, i) => {
              const status = statusConfig[o.status] || statusConfig.pending;
              return (
                <tr
                  key={o.id}
                  style={{
                    borderTop: "1px solid #0f172a",
                    background: i % 2 === 0 ? "#1e293b" : "#172033",
                  }}
                >
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "#60a5fa",
                      fontSize: "13px",
                    }}
                  >
                    {o.to_email}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <p
                      style={{
                        color: "#f1f5f9",
                        fontSize: "13px",
                        maxWidth: "300px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {o.subject}
                    </p>
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <span
                      style={{
                        background: status.bg,
                        color: status.color,
                        padding: "2px 10px",
                        borderRadius: "20px",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      {o.status}
                    </span>
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "#64748b",
                      fontSize: "12px",
                    }}
                  >
                    {new Date(o.created_at).toLocaleDateString()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}