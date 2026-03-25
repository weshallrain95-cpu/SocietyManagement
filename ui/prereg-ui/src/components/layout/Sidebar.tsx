import { useState } from "react";
import { useSociety } from "../../context/SocietyContext";

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { society } = useSociety();

  // ✅ EXISTING INTELLIGENCE (UNCHANGED)
  const stage = society?.onboarding?.stage || "SOCIETY_SETUP";

  // ✅ NEW: REGISTRATION LOGIC
  const isUnregistered = society?.legal_status === "NOT_REGISTERED";

  // 🔒 Prereg unlock ONLY after onboarding complete
  const onboardingComplete = stage === "FINANCE_READY";

  const Section = ({ title, children }: any) => (
    <div style={{ marginTop: 20 }}>
      {!collapsed && (
        <div
          style={{
            fontSize: 11,
            color: "#9ca3af",
            marginBottom: 8,
            fontWeight: 600,
            letterSpacing: 0.5,
          }}
        >
          {title}
        </div>
      )}
      {children}
    </div>
  );

  return (
    <div
      style={{
        width: collapsed ? 70 : 260,
        background: "#111827",
        color: "white",
        height: "100vh",
        transition: "width 0.25s ease",
        padding: "20px 14px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* TOP */}
      <div
        style={{
          display: "flex",
          justifyContent: collapsed ? "center" : "space-between",
          alignItems: "center",
          marginBottom: 25,
        }}
      >
        {!collapsed && <div style={{ fontWeight: 600 }}>ShiftIT</div>}

        <div
          onClick={() => setCollapsed(!collapsed)}
          style={{ cursor: "pointer", fontSize: 18 }}
        >
          ☰
        </div>
      </div>

      {/* DASHBOARD */}
      <SidebarItem label="Dashboard" active collapsed={collapsed} />

      {/* SETUP */}
      <Section title="SOCIETY SETUP">
        <SidebarItem label="Society Details" collapsed={collapsed} />

        <SidebarItem label="Structure" collapsed={collapsed} />

        <SidebarItem
          label="Members"
          collapsed={collapsed}
          locked={stage === "SOCIETY_SETUP"}
        />

        <SidebarItem
          label="Finance Setup"
          collapsed={collapsed}
          locked={stage !== "FINANCE_READY"}
        />

        <SidebarItem
          label="Governance"
          collapsed={collapsed}
          locked={stage !== "FINANCE_READY"}
        />
      </Section>

      {/* ✅ NEW: PREREGISTRATION (ONLY FOR UNREGISTERED) */}
      {isUnregistered && (
        <Section title="REGISTRATION">
          <SidebarItem
            label="Pre-Registration Process"
            collapsed={collapsed}
            locked={!onboardingComplete}
          />
        </Section>
      )}

      {/* MODULES */}
      <Section title="MODULES">
        <SidebarItem
          label="Members & Governance"
          collapsed={collapsed}
          locked={stage === "SOCIETY_SETUP"}
        />

        <SidebarItem
          label="Finance"
          collapsed={collapsed}
          locked={stage !== "FINANCE_READY"}
        />

        <SidebarItem label="Operations" collapsed={collapsed} locked />

        <SidebarItem label="Compliance" collapsed={collapsed} locked />
      </Section>
    </div>
  );
}

/* ITEM */

import { useNavigate } from "react-router-dom";

function SidebarItem({
  label,
  active = false,
  locked = false,
  collapsed = false,
}: any) {
  const navigate = useNavigate();

  const routeMap: any = {
    Dashboard: "/dashboard",
    "Society Details": "/dashboard",
    Structure: "/structure",
    Members: "/members",
    "Finance Setup": "/finance",
    Governance: "/governance",
    "Pre-Registration Process": "/prereg",
  };

  return (
    <div
      onClick={() => {
        if (locked) {
          alert("Complete onboarding to unlock this module");
          return;
        }

        const route = routeMap[label];
        if (route) navigate(route);
      }}
      style={{
        padding: collapsed ? "10px" : "10px 12px",
        borderRadius: 8,
        cursor: "pointer",
        background: active ? "#1f2937" : "transparent",
        opacity: locked ? 0.5 : 1,
        marginBottom: 6,
        fontSize: 14,
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.background = "#1f2937";
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.background = "transparent";
      }}
    >
      {collapsed ? "•" : `${label} ${locked ? "🔒" : ""}`}
    </div>
  );
}
