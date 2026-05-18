"use client";
import { useEffect, useState } from "react";
import {
  getSummary,
  getLeads,
  getOutreach,
  getScoreDistribution,
  getModelMetadata,
  Lead,
  AnalyticsSummary,
  Outreach,
} from "@/lib/api";
import StatsCard from "@/components/StatsCard";
import LeadsTable from "@/components/LeadsTable";
import OutreachTable from "@/components/OutreachTable";
import ScoreChart from "@/components/ScoreChart";

export default function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [outreach, setOutreach] = useState<Outreach[]>([]);
  const [distribution, setDistribution] = useState<any[]>([]);
  const [modelMeta, setModelMeta] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"leads" | "outreach" | "model">(
    "leads"
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, l, o, d, m] = await Promise.all([
          getSummary(),
          getLeads(),
          getOutreach(),
          getScoreDistribution(),
          getModelMetadata(),
        ]);
        setSummary(s);
        setLeads(l);
        setOutreach(o);
        setDistribution(d);
        setModelMeta(m);
      } catch (e) {
        console.error("Failed to load data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          background: "#0f172a",
          color: "#60a5fa",
          fontSize: "16px",
          gap: "12px",
        }}
      >
        <div
          style={{
            width: "24px",
            height: "24px",
            border: "3px solid #1e293b",
            borderTop: "3px solid #60a5fa",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }}
        />
        Loading Intelligence Data...
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a" }}>
      {/* Header */}
      <div
        style={{
          background: "#1e293b",
          borderBottom: "1px solid #334155",
          padding: "16px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
              borderRadius: "8px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
            }}
          >
            🎯
          </div>
          <div>
            <h1 style={{ color: "#f1f5f9", fontSize: "18px", fontWeight: "700" }}>
              Contractor Intelligence
            </h1>
            <p style={{ color: "#64748b", fontSize: "12px" }}>
              Agentic Lead Intelligence System
            </p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              width: "8px",
              height: "8px",
              background: "#10b981",
              borderRadius: "50%",
            }}
          />
          <span style={{ color: "#10b981", fontSize: "13px" }}>
            System Active
          </span>
        </div>
      </div>

      <div style={{ padding: "32px", maxWidth: "1400px", margin: "0 auto" }}>
        {/* Stats Grid */}
        {summary && (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "16px",
              marginBottom: "32px",
            }}
          >
            <StatsCard
              title="Total Businesses"
              value={summary.total_businesses}
              subtitle="Discovered & indexed"
              color="#3b82f6"
              icon="🏢"
            />
            <StatsCard
              title="Hot Leads"
              value={summary.hot_leads}
              subtitle="Score ≥ 0.70"
              color="#ef4444"
              icon="🔥"
            />
            <StatsCard
              title="Warm Leads"
              value={summary.warm_leads}
              subtitle="Score 0.40–0.70"
              color="#f59e0b"
              icon="🌤"
            />
            <StatsCard
              title="Avg Score"
              value={summary.avg_score?.toFixed(3)}
              subtitle="Across all leads"
              color="#8b5cf6"
              icon="📊"
            />
            <StatsCard
              title="Outreach Sent"
              value={summary.total_outreach}
              subtitle={`${summary.replied_outreach} replied`}
              color="#10b981"
              icon="📧"
            />
          </div>
        )}

        {/* Chart */}
        {distribution.length > 0 && (
          <div style={{ marginBottom: "32px" }}>
            <ScoreChart data={distribution} />
          </div>
        )}

        {/* Tabs */}
        <div
          style={{
            display: "flex",
            gap: "4px",
            marginBottom: "16px",
            background: "#1e293b",
            padding: "4px",
            borderRadius: "10px",
            width: "fit-content",
          }}
        >
          {(["leads", "outreach", "model"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: "8px 20px",
                borderRadius: "8px",
                border: "none",
                cursor: "pointer",
                fontSize: "13px",
                fontWeight: "600",
                background: activeTab === tab ? "#3b82f6" : "transparent",
                color: activeTab === tab ? "#fff" : "#64748b",
                transition: "all 0.2s",
              }}
            >
              {tab === "leads" && `🏢 Leads (${leads.length})`}
              {tab === "outreach" && `📧 Outreach (${outreach.length})`}
              {tab === "model" && "🤖 Model"}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "leads" && <LeadsTable leads={leads} />}
        {activeTab === "outreach" && <OutreachTable outreach={outreach} />}
        {activeTab === "model" && modelMeta && (
          <div
            style={{
              background: "#1e293b",
              borderRadius: "12px",
              padding: "24px",
              border: "1px solid #334155",
            }}
          >
            <h3
              style={{
                color: "#f1f5f9",
                fontSize: "15px",
                marginBottom: "20px",
              }}
            >
              🤖 Model Performance
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: "16px",
                marginBottom: "24px",
              }}
            >
              {Object.entries(modelMeta.metrics || {}).map(([k, v]) => (
                <div
                  key={k}
                  style={{
                    background: "#0f172a",
                    padding: "16px",
                    borderRadius: "8px",
                    border: "1px solid #334155",
                  }}
                >
                  <p
                    style={{
                      color: "#64748b",
                      fontSize: "12px",
                      marginBottom: "4px",
                      textTransform: "uppercase",
                    }}
                  >
                    {k.replace("_", " ")}
                  </p>
                  <p
                    style={{
                      color: "#f1f5f9",
                      fontSize: "24px",
                      fontWeight: "700",
                    }}
                  >
                    {typeof v === "number" ? v.toFixed(4) : String(v)}
                  </p>
                </div>
              ))}
            </div>
            <h4
              style={{
                color: "#94a3b8",
                fontSize: "13px",
                marginBottom: "12px",
              }}
            >
              Top SHAP Features
            </h4>
            {(modelMeta.shap_importance || [])
              .slice(0, 8)
              .map((f: any, i: number) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    marginBottom: "8px",
                  }}
                >
                  <span
                    style={{
                      color: "#64748b",
                      fontSize: "12px",
                      width: "180px",
                    }}
                  >
                    {f.feature}
                  </span>
                  <div
                    style={{
                      flex: 1,
                      height: "6px",
                      background: "#334155",
                      borderRadius: "3px",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${(f.importance / (modelMeta.shap_importance[0]?.importance || 1)) * 100}%`,
                        height: "100%",
                        background: "linear-gradient(90deg, #3b82f6, #8b5cf6)",
                        borderRadius: "3px",
                      }}
                    />
                  </div>
                  <span style={{ color: "#94a3b8", fontSize: "12px" }}>
                    {f.importance.toFixed(4)}
                  </span>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}