import AppShell from "../components/layout/AppShell";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useSociety } from "../context/SocietyContext";


export default function OperationsHub() {
  const navigate = useNavigate();
  const { society } = useSociety();
  const onboarding = society?.onboarding;
  
  const canCreateCommittee = society?.onboarding?.can_create_committee;
  const canConfigureRules = society?.onboarding?.can_configure_operational_rules;
  const canAccessShareCertificates = society?.onboarding?.can_access_share_certificates;
  const canAccessRegistration = society?.onboarding?.is_complete;

  const status = society?.onboarding;   // ✅ from context
  const [bylawsStatus, setBylawsStatus] = useState<string | null>(null);


  // ---------------- FETCH BYLAWS ONLY ----------------
  useEffect(() => {
    if (!society?.id) return;

    const fetchStatus = async () => {
      try {
        const bylawsRes = await fetch(
          `/api/society/bylaws/status/?society_id=${society.id}`
        );
        const bylawsData = await bylawsRes.json();
        setBylawsStatus(bylawsData.status);
      } catch (err) {
        console.error("Failed to fetch bylaws status", err);
      }
    };

    fetchStatus();
  }, [society]);
  
  // 🔴 INSERT THIS EXACTLY HERE (NEXT LINE)

  useEffect(() => {
    if (!society) return;

    const isRegistered =
      society.legal_status === "REGISTERED" &&
      society.registration_number &&
      society.registration_date;

    const certificatesUploaded =
      society.registration_certificate && society.oc_certificate;

    if (isRegistered && certificatesUploaded) {
      navigate("/financial-onboarding");
    }

    if (isRegistered && !certificatesUploaded) {
      navigate("/registration-tracker");
    }
  }, [society]);
  
  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>Operations Onboarding</h2>

        {/* GOVERNANCE */}
        <div
          style={{
            ...card,
            opacity: canCreateCommittee ? 1 : 0.6,
            cursor: canCreateCommittee ? "not-allowed" : "pointer",
          }}
          onClick={() => {
            if (!canCreateCommittee) {
              navigate("/committee/setup");
            }
          }}
        >
          <h3 style={cardTitle}>1. Governance (Committee)</h3>
          <p style={cardDesc}>
            {society?.onboarding?.can_create_committee
              ? "Setup managing committee and assign roles"
              : "Society Management Committee is active"}
          </p>
        </div>

        {/* BY-LAWS */}
        <div
          style={{
            ...card,
            opacity: status?.allowed_actions?.can_generate_bylaws ? 1 : 0.6,
            cursor: status?.allowed_actions?.can_generate_bylaws
              ? "pointer"
              : "not-allowed",
          }}
          onClick={() => {
            if (!status?.allowed_actions?.can_generate_bylaws) return;

            navigate("/bylaws-test", {
              state: { society_id: society.id },
            });
          }}
        >
          <h3 style={cardTitle}>2. By-laws Engine</h3>

          <p style={cardDesc}>
            {status?.allowed_actions?.can_generate_bylaws
              ? "Upload and configure society by-laws"
              : "By-laws completed and locked"}
          </p>
        </div>

        {/* SHARE CERTIFICATE */}
        <div
          style={{
            ...card,
            opacity: canAccessShareCertificates ? 1 : 0.6,
            cursor: canAccessShareCertificates ? "pointer" : "not-allowed",
          }}
          onClick={() => {
            if (!canAccessShareCertificates) return;
            navigate("/share-certificates");
          }}
        >
          <h3 style={cardTitle}>3. Share Certificates</h3>
          <p style={cardDesc}>
            {canAccessShareCertificates
              ? "Manage ownership-linked certificates"
              : "Complete previous steps to unlock share certificates"}
          </p>
        </div>
        
        {/* REGISTRATION */}
        <div
          style={{
            ...card,
            opacity: canAccessRegistration ? 1 : 0.6,
            cursor: canAccessRegistration ? "pointer" : "not-allowed",
          }}
          onClick={() => {
            if (!canAccessRegistration) return;
            navigate("/registration-tracker");
          }}
        >
          <h3 style={cardTitle}>4. Registration Tracker</h3>
          <p style={cardDesc}>
            {canAccessRegistration
              ? "Track statutory registration process"
              : "Complete operational setup to unlock registration"}
          </p>
        </div>

        {/* DOCUMENT VAULT */}
        <div
          style={{
            ...card,
            opacity: 0.6,
            cursor: "not-allowed",
          }}
        >
          <h3 style={cardTitle}>5. Document Vault</h3>
          <p style={cardDesc}>
            Coming soon
          </p>
        </div>

        {/* RULES */}
        <div
          style={{
            ...card,
            opacity: canConfigureRules ? 1 : 0.6,
            cursor: canConfigureRules ? "pointer" : "not-allowed",
          }}
          onClick={() => {
            if (!canConfigureRules) return;

            navigate("/operational-rules");
          }}
        >
          <h3 style={cardTitle}>6. Operational Rules</h3>
          <p style={cardDesc}>
            {canConfigureRules
              ? "Configure society-level operational rules"
              : "Operational rules already configured"}
          </p>
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