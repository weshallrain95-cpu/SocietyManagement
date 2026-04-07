import AppShell from "../components/layout/AppShell";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useSociety } from "../context/SocietyContext";

export default function OperationsHub() {
  const navigate = useNavigate();
  const { society } = useSociety();

  const [status, setStatus] = useState<any>(null);
  const [bylawsStatus, setBylawsStatus] = useState<string | null>(null);

  // ---------------- FETCH STATUS ----------------
  useEffect(() => {
    if (!society?.id) return;

    const fetchStatus = async () => {
      try {
        // 🔹 EXISTING
        const res = await fetch(
          `/api/society/onboarding/status/?society_id=${society.id}`
        );
        const data = await res.json();
        setStatus(data);

        // 🔥 NEW — BYLAWS STATUS
        const bylawsRes = await fetch(
          `/api/society/bylaws/status/?society_id=${society.id}`
        );
        const bylawsData = await bylawsRes.json();
        setBylawsStatus(bylawsData.status);

      } catch (err) {
        console.error("Failed to fetch onboarding status", err);
      }
    };

    fetchStatus();
  }, [society]);

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>Operations Onboarding</h2>

        {/* GOVERNANCE */}
        <div
          style={{
            ...card,
            opacity: status?.has_committee ? 0.6 : 1,
            cursor: status?.has_committee ? "not-allowed" : "pointer",
          }}
          onClick={() => {
            if (!status?.has_committee) {
              navigate("/committee/setup");
            }
          }}
        >
          <h3 style={cardTitle}>1. Governance (Committee)</h3>
          <p style={cardDesc}>
            {status?.has_committee
              ? "Society Management Committee is active"
              : "Setup managing committee, roles, and governance rules"}
          </p>
        </div>

        {/* BY-LAWS */}
        <div
          style={{
            ...card,
            opacity: bylawsStatus === "SIGNED" ? 0.6 : 1,
            cursor: bylawsStatus === "SIGNED" ? "not-allowed" : "pointer",
          }}
          onClick={() => {
            if (bylawsStatus === "SIGNED") return;

            navigate("/bylaws-test", {
              state: { society_id: society.id },
            });
          }}
        >
          <h3 style={cardTitle}>2. By-laws Engine</h3>

          <p style={cardDesc}>
            {bylawsStatus === "SIGNED"
              ? "By-laws completed and locked"
              : "Upload and configure society by-laws"}
          </p>
        </div>

        {/* SHARE CERTIFICATE */}
        <div style={card}>
          <h3 style={cardTitle}>3. Share Certificates</h3>
          <p style={cardDesc}>Manage ownership-linked certificates</p>
        </div>

        {/* REGISTRATION */}
        <div style={card}>
          <h3 style={cardTitle}>4. Registration Tracker</h3>
          <p style={cardDesc}>Track statutory registration process</p>
        </div>

        {/* DOCUMENT VAULT */}
        <div style={card}>
          <h3 style={cardTitle}>5. Document Vault</h3>
          <p style={cardDesc}>Centralized legal document storage</p>
        </div>

        {/* RULES */}
        <div style={card}>
          <h3 style={cardTitle}>6. Operational Rules</h3>
          <p style={cardDesc}>Configure society-level operational rules</p>
        </div>
      </div>
    </AppShell>
  );
}

/* ===== STYLES ===== */

const container = { padding: 20 };

const title = {
  fontSize: 24,
  fontWeight: 600,
  marginBottom: 20,
};

const card = {
  padding: 16,
  border: "1px solid #e5e7eb",
  borderRadius: 10,
  marginBottom: 12,
  cursor: "pointer",
};

const cardTitle = {
  fontSize: 16,
  fontWeight: 600,
};

const cardDesc = {
  fontSize: 13,
  color: "#6b7280",
};