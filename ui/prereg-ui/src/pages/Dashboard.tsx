import AppShell from "../components/layout/AppShell";
import { useSociety } from "../context/SocietyContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

export default function Dashboard() {
  const { society } = useSociety();
  const navigate = useNavigate();
  const [status, setStatus] = useState<any>(null);

  /* ================= FETCH STATUS ================= */

  useEffect(() => {
    if (society === null) return; // wait for context to load

    if (!society?.id) {
      navigate("/login");
      return;
    }

    fetch(`/api/society/onboarding/status/?society_id=${society.id}`)
      .then((res) => res.json())
      .then((data) => setStatus(data))
      .catch(() => console.warn("Status fetch failed"));
  }, [society, navigate]);

  const isComplete = [
    "ONBOARDING_COMPLETE",
    "OPERATIONS_PENDING",
    "OPERATIONS_COMPLETE",
    "FINANCIAL_PENDING",
    "FINANCIAL_COMPLETE",
    "SYSTEM_LIVE",
  ].includes(status?.stage);

  // 🔥 ADD THIS (surgical fix)
  const structureLocked = status
    ? [
        "STRUCTURE_CREATED",
        "OWNERSHIP_PENDING",
        "ONBOARDING_COMPLETE",
        "OPERATIONS_PENDING",
        "OPERATIONS_COMPLETE",
        "FINANCIAL_PENDING",
        "FINANCIAL_COMPLETE",
        "SYSTEM_LIVE",
      ].includes(status.stage)
    : true; // default lock until status loads

  /* ================= UI ================= */

  return (
    <AppShell>
      <div style={container}>
        
        {/* HEADER */}
        <div style={header}>
          <div>
            <h1 style={title}>{society?.name || "Your Society"}</h1>
            <p style={subtitle}>
              Manage governance, operations and compliance seamlessly
            </p>
          </div>

          <div style={badge}>
            {isComplete ? "System Ready" : "Setup in Progress"}
          </div>
        </div>

        {/* ALERT */}
        {society?.legal_status === "NOT_REGISTERED" && (
          <div style={alert}>
            ⚠ Your society is not registered — complete setup to proceed with registration
          </div>
        )}

        {/* STATUS PANEL */}
        <div style={statusPanel}>
          <StatusItem
            label="Structure"
            value={isComplete ? "Complete" : "Pending"}
            success={isComplete}
          />
          <StatusItem
            label="Ownership"
            value={isComplete ? "Configured" : "Pending"}
            success={isComplete}
          />
          <StatusItem
            label="Finance"
            value="Pending"
            success={false}
          />
        </div>

        {/* STATS */}
        <div style={statsGrid}>
          <StatCard title="Members" value="—" />
          <StatCard title="Flats" value="—" />
          <StatCard title="Pending Tasks" value="—" />
        </div>

        {/* MODULES */}
        <div style={moduleGrid}>
          
          <ModuleCard
            title="Society Setup"
            status={isComplete ? "Completed" : "Continue Setup"}
            locked={structureLocked}
            onClick={() => {
              if (structureLocked) return;
              navigate("/structure");
            }}
          />

          <ModuleCard
            title="Members & Governance"
            status={status?.has_committee ? "Completed" : "Pending"}
            locked={!status?.has_committee}
          />

          <ModuleCard
            title="Finance"
            status="Locked"
            locked
          />

          <ModuleCard
            title="Start Operations Onboarding"
            status={isComplete ? "Next Step" : "Locked"}
            locked={!isComplete}
            highlight={isComplete}
            onClick={() => {
              if (!isComplete) return;
              navigate("/operations");
            }}
          />

          <ModuleCard
            title="Compliance"
            status="Locked"
            locked
          />

        </div>

      </div>
    </AppShell>
  );
}

/* ================= COMPONENTS ================= */

function ModuleCard({ title, status, locked = false, onClick, highlight = false }: any) {
  return (
    <div
      onClick={() => {
        if (locked) return;
        onClick && onClick();
      }}
      style={{
        padding: 22,
        borderRadius: 16,
        background: highlight ? "#ecfdf5" : "white",
        border: highlight ? "1px solid #10b981" : "1px solid #e5e7eb",
        cursor: locked ? "not-allowed" : "pointer",
        opacity: locked ? 0.5 : 1,
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        if (!locked) e.currentTarget.style.transform = "translateY(-4px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0px)";
      }}
    >
      <div style={{ fontWeight: 600, fontSize: 15 }}>{title}</div>

      <div style={{ fontSize: 13, marginTop: 6, color: "#6b7280" }}>
        {status}
      </div>
    </div>
  );
}

function StatCard({ title, value }: any) {
  return (
    <div style={statCard}>
      <div style={statTitle}>{title}</div>
      <div style={statValue}>{value}</div>
    </div>
  );
}

function StatusItem({ label, value, success }: any) {
  return (
    <div style={statusItem}>
      <div style={{ fontSize: 13, color: "#6b7280" }}>{label}</div>
      <div
        style={{
          fontWeight: 600,
          color: success ? "#16a34a" : "#ef4444",
        }}
      >
        {value}
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const container = {
  maxWidth: 1200,
  margin: "0 auto",
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 25,
};

const title = {
  fontSize: 28,
  fontWeight: 700,
};

const subtitle = {
  color: "#6b7280",
  marginTop: 5,
};

const badge = {
  background: "#eef2ff",
  padding: "8px 14px",
  borderRadius: 20,
  fontSize: 13,
  fontWeight: 500,
};

const alert = {
  background: "#fff7ed",
  border: "1px solid #fdba74",
  padding: 14,
  borderRadius: 10,
  marginBottom: 25,
  color: "#9a3412",
  fontSize: 14,
};

const statusPanel = {
  display: "flex",
  gap: 30,
  background: "white",
  padding: 18,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
  marginBottom: 30,
};

const statusItem = {
  display: "flex",
  flexDirection: "column" as const,
};

const statsGrid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
  gap: 20,
};

const statCard = {
  background: "white",
  padding: 20,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
};

const statTitle = {
  fontSize: 13,
  color: "#6b7280",
};

const statValue = {
  fontSize: 22,
  fontWeight: 600,
};

const moduleGrid = {
  marginTop: 30,
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
  gap: 20,
};