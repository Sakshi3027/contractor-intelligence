"use client";
import { Lead } from "@/lib/api";

interface LeadsTableProps {
  leads: Lead[];
}

const tierConfig: Record<string, { color: string; bg: string; emoji: string }> =
  {
    hot: { color: "#ef4444", bg: "#450a0a", emoji: "🔥" },
    warm: { color: "#f59e0b", bg: "#451a03", emoji: "🌤" },
    cold: { color: "#3b82f6", bg: "#172554", emoji: "❄️" },
  };

export default function LeadsTable({ leads }: LeadsTableProps) {
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
          All Leads ({leads.length})
        </h3>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "#0f172a" }}>
              {["Company", "City", "Score", "Tier", "Rating", "Email"].map(
                (h) => (
                  <th
                    key={h}
                    style={{
                      padding: "10px 16px",
                      textAlign: "left",
                      color: "#64748b",
                      fontSize: "12px",
                      fontWeight: "600",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}
                  >
                    {h}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {leads.map((lead, i) => {
              const tier = tierConfig[lead.tier] || tierConfig.cold;
              return (
                <tr
                  key={lead.id}
                  style={{
                    borderTop: "1px solid #1e293b",
                    background: i % 2 === 0 ? "#1e293b" : "#172033",
                    transition: "background 0.15s",
                  }}
                >
                  <td style={{ padding: "12px 16px" }}>
                    <p
                      style={{
                        color: "#f1f5f9",
                        fontSize: "13px",
                        fontWeight: "500",
                        maxWidth: "280px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {lead.name}
                    </p>
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "#94a3b8",
                      fontSize: "13px",
                    }}
                  >
                    {lead.city}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      <div
                        style={{
                          width: "60px",
                          height: "6px",
                          background: "#334155",
                          borderRadius: "3px",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${(lead.score || 0) * 100}%`,
                            height: "100%",
                            background: tier.color,
                            borderRadius: "3px",
                          }}
                        />
                      </div>
                      <span style={{ color: "#f1f5f9", fontSize: "13px" }}>
                        {lead.score?.toFixed(3)}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <span
                      style={{
                        background: tier.bg,
                        color: tier.color,
                        padding: "2px 10px",
                        borderRadius: "20px",
                        fontSize: "12px",
                        fontWeight: "600",
                      }}
                    >
                      {tier.emoji} {lead.tier}
                    </span>
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "#94a3b8",
                      fontSize: "13px",
                    }}
                  >
                    ⭐ {lead.google_rating} ({lead.google_review_count})
                  </td>
                  <td
                    style={{
                      padding: "12px 16px",
                      color: "#60a5fa",
                      fontSize: "12px",
                    }}
                  >
                    {lead.email || "—"}
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