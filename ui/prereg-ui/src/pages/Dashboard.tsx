import AppShell from "../components/layout/AppShell";
import { useSociety } from "../context/SocietyContext";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const { society } = useSociety();
  const navigate = useNavigate();

  if (!society) return null;
  
  // 🔴 FINAL COMPLETION OVERRIDE ONLY
  if (
    society.legal_status === "REGISTERED" &&
    society.registration_number &&
    society.registration_date &&
    society.registration_certificate &&
    society.oc_certificate
  ) {
    navigate("/financial-onboarding");
    return null;
  }

  const stage = society?.onboarding?.stage;

  const next = getNextStep(stage);

  const progressMap: any = {
    STRUCTURE_PENDING: 10,
    OWNERSHIP_PENDING: 25,
    OWNERSHIP_REFINEMENT_PENDING: 40,
    OPERATIONS_PENDING: 55,
    BYLAWS_PENDING: 70,
    SHARE_CERTIFICATES_PENDING: 80,
    OPERATIONAL_RULES_PENDING: 90,
    OPERATIONS_COMPLETE: 100,
  };

  const progress = progressMap[stage] || 0;

  const isRegistered = society?.legal_status === "REGISTERED";
  const onboarding = society?.onboarding;
  const canAccessFinance = false; // placeholder (until backend ready)

  return (
    <AppShell>
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        
        {/* HEADER */}
        <div style={header}>
          <div>
            <h1 style={title}>{society?.name}</h1>
            <p style={subtitle}>System control dashboard</p>
          </div>

          <div style={badge}>
            {progress === 100 ? "System Ready" : "Setup in Progress"}
          </div>
        </div>

        {/* HERO: PROGRESS */}
        <div style={heroCard}>
          <div>
            <h3>Onboarding Progress</h3>
            <p style={{ marginTop: 8 }}>
              Current Stage: <b>{stage}</b>
            </p>

            <div style={progressBar}>
              <div style={{ ...progressFill, width: `${progress}%` }} />
            </div>

            <button
              style={primaryBtn}
              onClick={() => navigate(next.route)}
            >
              {next.label}
            </button>
          </div>

          {/* SPEEDOMETER STYLE */}
          <div style={progressCircle}>
            <div style={circleInner}>{progress}%</div>
          </div>
        </div>

        {/* REGISTRATION */}
        <div style={card}>
          <h3>Registration Status</h3>

          {isRegistered ? (
            <div style={{ color: "#16a34a", fontWeight: 600 }}>
              Registered ✔ — {society?.registration_number || "—"}
            </div>
          ) : (
            <>
              <div style={{ color: "#ea580c" }}>
                Society Unregistered
              </div>
              <button
                style={secondaryBtn}
                onClick={() => navigate("/registration-tracker")}
              >
                Continue Registration
              </button>
            </>
          )}
        </div>

        {/* SNAPSHOT */}
        <div style={grid}>
          <StatCard title="Members Onboarding" value="—" />
          <StatCard title="Flats" value="—" />
          <StatCard title="Certificates" value="—" />
          <StatCard title="Rules" value="—" />
        </div>

        {/* MODULE GRID */}
        <div style={grid}>
          <ModuleCard
            title="Governance"
            enabled={onboarding?.can_create_committee}
            onClick={() => navigate("/committee/setup")}
          />

          <ModuleCard
            title="By-laws"
            enabled={onboarding?.can_generate_bylaws}
            onClick={() => navigate("/bylaws")}
          />

          <ModuleCard
            title="Share Certificates"
            enabled={onboarding?.can_generate_share_certificates}
            onClick={() => navigate("/operations")}
          />

          <ModuleCard
            title="Operational Rules"
            enabled={onboarding?.can_configure_operational_rules}
            onClick={() => navigate("/operations")}
          />

          <ModuleCard
            title="Finance Onboarding"
            enabled={canAccessFinance}
            onClick={() => navigate("/finance")}
          />

          <ModuleCard
            title="Members Onboarding"
            enabled={false}
            onClick={() => navigate("/members")}
          />
          
        </div>

      </div>
    </AppShell>
  );
}

/* ================= COMPONENTS ================= */

function ModuleCard({ title, enabled, onClick }: any) {
  return (
    <div
      onClick={() => {
        if (!enabled) return;
        onClick();
      }}
      style={{
        padding: 20,
        borderRadius: 14,
        background: "white",
        border: "1px solid #e5e7eb",
        cursor: enabled ? "pointer" : "not-allowed",
        opacity: enabled ? 1 : 0.5,
      }}
    >
      <div style={{ fontWeight: 600 }}>{title}</div>
      <div style={{ fontSize: 12, color: "#6b7280", marginTop: 5 }}>
        {enabled ? "Available" : "Locked"}
      </div>
    </div>
  );
}

function StatCard({ title, value }: any) {
  return (
    <div style={card}>
      <div style={{ fontSize: 13, color: "#6b7280" }}>{title}</div>
      <div style={{ fontSize: 22, fontWeight: 600 }}>{value}</div>
    </div>
  );
}

/* ================= HELPERS ================= */

function getNextStep(stage: string) {
  switch (stage) {
    case "STRUCTURE_PENDING":
      return { label: "Setup Structure", route: "/structure" };
    case "OWNERSHIP_PENDING":
      return { label: "Upload Ownership", route: "/excel-upload-placeholder" };
    case "OWNERSHIP_REFINEMENT_PENDING":
      return { label: "Fix Ownership", route: "/ownership-refinement" };
    case "OPERATIONS_PENDING":
      return { label: "Setup Committee", route: "/committee/setup" };
    case "BYLAWS_PENDING":
      return { label: "Generate By-laws", route: "/bylaws" };
    case "SHARE_CERTIFICATES_PENDING":
      return { label: "Manage Share Certificates", route: "/operations" };
    case "OPERATIONAL_RULES_PENDING":
      return { label: "Configure Operational Rules", route: "/operations" };
    case "OPERATIONS_COMPLETE":
      return { label: "Go to Operations Hub", route: "/operations" };
    default:
      return { label: "Dashboard", route: "/dashboard" };
  }
}

/* ================= STYLES ================= */

const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 25,
};

const title = { fontSize: 28, fontWeight: 700 };

const subtitle = { color: "#6b7280" };

const badge = {
  background: "#eef2ff",
  padding: "8px 14px",
  borderRadius: 20,
};

const heroCard = {
  display: "flex",
  justifyContent: "space-between",
  background: "white",
  padding: 24,
  borderRadius: 16,
  border: "1px solid #e5e7eb",
};

const progressBar = {
  height: 10,
  background: "#e5e7eb",
  borderRadius: 10,
  marginTop: 10,
};

const progressFill = {
  height: 10,
  background: "#22c55e",
  borderRadius: 10,
};

const progressCircle = {
  width: 100,
  height: 100,
  borderRadius: "50%",
  background: "#ecfdf5",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontWeight: 700,
};

const circleInner = { fontSize: 18 };

const card = {
  background: "white",
  padding: 20,
  borderRadius: 12,
  border: "1px solid #e5e7eb",
  marginTop: 20,
};

const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
  gap: 20,
  marginTop: 20,
};

const primaryBtn = {
  marginTop: 15,
  padding: "10px 16px",
  background: "#111827",
  color: "white",
  borderRadius: 8,
  border: "none",
};

const secondaryBtn = {
  marginTop: 10,
  padding: "8px 14px",
  background: "#2563eb",
  color: "white",
  borderRadius: 8,
  border: "none",
};