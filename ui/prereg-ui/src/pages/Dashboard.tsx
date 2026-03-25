import AppShell from "../components/layout/AppShell";
import { useSociety } from "../context/SocietyContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

export default function Dashboard() {
  const { society } = useSociety();
  const navigate = useNavigate();
  const [status, setStatus] = useState<any>(null);

  // ✅ SAFETY REDIRECT
  useEffect(() => {
    if (!society) {
      navigate("/login");
      return;
    }

    fetch(
      `http://127.0.0.1:8000/api/society/onboarding-status/${society.id}/`
    )
      .then((res) => res.json())
      .then((data) => setStatus(data))
      .catch(() => console.warn("Status fetch failed"));
  }, [society, navigate]);

  return (
    <AppShell>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        
        {/* HEADER */}
        <div style={{ marginBottom: 20 }}>
          <h1 style={{ fontSize: 26, fontWeight: 600 }}>
            {society?.name || "Your Society"}
          </h1>

          <p style={{ color: "#6b7280" }}>
            Manage your society operations, governance and compliance
          </p>
        </div>

        {/* 🚨 REGISTRATION STATUS BANNER */}
        {society?.legal_status === "NOT_REGISTERED" && (
            <div
                style={{
                background: "#fff7ed",
                border: "1px solid #fdba74",
                padding: 15,
                borderRadius: 10,
                marginBottom: 25,
                color: "#9a3412",
                fontSize: 14,
                fontWeight: 500,
                }}
            >
                ⚠ Your Society is not yet registered — complete setup to unlock the registration process
            </div>
            )}

        {/* ✅ ONBOARDING STATUS */}
        <div
          style={{
            background: "white",
            padding: 20,
            borderRadius: 12,
            border: "1px solid #e5e7eb",
            marginBottom: 30,
          }}
        >
          <div style={{ fontWeight: 600 }}>System Readiness</div>

          <div style={{ marginTop: 10, fontSize: 14, color: "#6b7280" }}>
            Structure: {status?.structure_ready ? "Ready" : "Pending"}
          </div>

          <div style={{ fontSize: 14, color: "#6b7280" }}>
            Finance: {status?.finance_ready ? "Ready" : "Pending"}
          </div>
        </div>

        {/* QUICK CARDS */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))",
            gap: 20,
          }}
        >
          <StatCard title="Members" value="—" />
          <StatCard title="Flats" value="—" />
          <StatCard title="Pending Tasks" value="—" />
        </div>

        {/* MODULE GRID */}
        <div
          style={{
            marginTop: 30,
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
            gap: 20,
          }}
        >
          <ModuleCard
            title="Society Setup"
            active={!status?.structure_ready}
          />

          <ModuleCard
            title="Members & Governance"
            locked={!status?.structure_ready}
          />

          <ModuleCard
            title="Finance"
            locked={!status?.finance_ready}
          />

          <ModuleCard title="Operations" locked />
          <ModuleCard title="Compliance" locked />
        </div>

      </div>
    </AppShell>
  );
}

/* COMPONENTS */

function ModuleCard({ title, active = false, locked = false }: any) {
  return (
    <div
      onClick={() => {
        if (locked) {
          alert("Complete previous steps to unlock this module");
        }
      }}
      style={{
        padding: 20,
        borderRadius: 14,
        background: "white",
        border: "1px solid #e5e7eb",
        cursor: "pointer",
        opacity: locked ? 0.5 : 1,
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        if (!locked) e.currentTarget.style.transform = "translateY(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0px)";
      }}
    >
      <div style={{ fontWeight: 600 }}>{title}</div>

      <div style={{ fontSize: 13, color: "#6b7280", marginTop: 5 }}>
        {locked && "Locked"}
        {!locked && active && "Continue setup"}
        {!locked && !active && "Available"}
      </div>
    </div>
  );
}

function StatCard({ title, value }: any) {
  return (
    <div
      style={{
        background: "white",
        padding: 20,
        borderRadius: 14,
        border: "1px solid #e5e7eb",
      }}
    >
      <div style={{ fontSize: 13, color: "#6b7280" }}>{title}</div>
      <div style={{ fontSize: 20, fontWeight: 600 }}>{value}</div>
    </div>
  );
}