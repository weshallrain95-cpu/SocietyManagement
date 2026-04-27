import AppShell from "../components/layout/AppShell";
import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function SCR13_BylawsPreview() {
  const location = useLocation();
  const navigate = useNavigate();

  const { society_id, formData, governance_hooks } = location.state || {};

  const [fields, setFields] = useState<any[]>([]);
  const [values, setValues] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [openInfo, setOpenInfo] = useState<number | null>(null);

  useEffect(() => {
    if (!society_id || !formData) {
      navigate("/dashboard");
    }
  }, [society_id, formData, navigate]);

  useEffect(() => {
    fetch(`${API_BASE}/api/society/bylaws/schema/`)
      .then(res => res.json())
      .then(data => {
        const schemaFields = data.fields || [];

        setFields(schemaFields);

        const defaults: Record<string, any> = {};

        schemaFields.forEach((f: any) => {
          defaults[f.key] = governance_hooks?.[f.key] ?? f.default ?? "";
        });

        setValues(defaults);
      })
      .catch(() => console.error("Schema fetch failed"))
      .finally(() => setLoading(false));
  }, []);

  const updateValue = (key: string, value: any) => {
    setValues(prev => ({ ...prev, [key]: value }));
  };

  const proceed = () => {
    console.log("STEP 1: proceed started");

    const mappedHooks: Record<string, any> = {};

    fields.forEach((f: any) => {
      const value = values[f.key];

      if (value !== "" && value !== undefined && value !== null) {
        mappedHooks[f.key] = value;
      }
    });

    // 🔥 CREATE CLEAN COPY FOR BACKEND ONLY
    const normalizedHooks = { ...mappedHooks };

    if (normalizedHooks["non_occupancy_mode"] === "fixed") {
      normalizedHooks["non_occupancy_charge_percent"] =
        normalizedHooks["non_occupancy_charge_fixed"] || 0;
    }

    // ❌ DO NOT DELETE ORIGINAL KEYS

    console.log("STEP 2: mappedHooks", mappedHooks);

    console.log("STEP 3: navigating...");

    navigate("/bylaws/generate", {
      state: {
        society_id,
        formData,
        governance_hooks: mappedHooks,        // 👈 UI truth
        normalized_hooks: normalizedHooks,    // 👈 backend truth
      },
    });

    console.log("STEP 4: navigation called");
  };

  const getGuidance = (key: string) => {
    const guide: any = {

      // ================= FINANCIAL =================
      share_value: {
        what: "Face value of each share held by a member.",
        why: "Defines ownership units and capital structure.",
        legal: "Typically fixed in bye-laws; cannot be arbitrarily changed.",
        default: "₹50 is the widely adopted standard in Maharashtra."
      },

      minimum_shares: {
        what: "Minimum number of shares a member must hold.",
        why: "Ensures minimum capital contribution from each member.",
        legal: "Must align with share capital rules defined in bye-laws.",
        default: "10 shares ensures ₹500 base contribution (₹50 x 10)."
      },

      entrance_fee: {
        what: "One-time fee charged when a member joins the society.",
        why: "Covers administrative onboarding and documentation costs.",
        legal: "Cannot be excessive; must be reasonable and justifiable.",
        default: "₹100 is commonly accepted across housing societies."
      },

      // ================= MAINTENANCE =================
      maintenance_basis: {
        what: "Method used to calculate maintenance charges.",
        why: "Determines fairness of cost distribution among members.",
        legal: "Model bye-laws support area-based or equal distribution.",
        default: "Flat area basis is most equitable and widely accepted."
      },

      sinking_fund_percent: {
        what: "Reserve fund for long-term structural repairs and rebuilding.",
        why: "Prepares society financially for major future expenses.",
        legal: "Registrar encourages structured accumulation.",
        default: "0.25% is conservative but safe for long-term stability."
      },

      repair_fund_percent: {
        what: "Fund for routine repairs and maintenance.",
        why: "Ensures regular upkeep without financial strain.",
        legal: "Must be proportionate to maintenance needs.",
        default: "0.75% complements sinking fund for balanced coverage."
      },

      // ================= PENALTIES =================
      late_payment_interest_percent: {
        what: "Interest charged on delayed maintenance payments.",
        why: "Encourages timely payments and financial discipline.",
        legal: "Typically capped around 18–21% annually.",
        default: "18% is standard and legally acceptable."
      },

      non_occupancy_mode: {
        what: "Defines how non-occupancy charges are calculated.",
        why: "Impacts fairness and legal compliance.",
        legal: "Maharashtra Govt caps at 10% of service charges (if percentage-based).",
        default: "Percentage-based model ensures compliance."
      },

      non_occupancy_charge_percent: {
        what: "Percentage charged when flat is not occupied by owner.",
        why: "Compensates society for additional usage.",
        legal: "CANNOT exceed 10% of service charges.",
        default: "10% is the legal maximum allowed."
      },

      non_occupancy_charge_fixed: {
        what: "Flat monthly charge for non-occupied units.",
        why: "Simplifies billing but may create inequality.",
        legal: "Not explicitly recommended; may be challenged.",
        default: "₹2000 is commonly used but should be justified."
      },

      // ================= GOVERNANCE =================
      committee_size: {
        what: "Total number of managing committee members.",
        why: "Defines governance strength and representation.",
        legal: "Minimum 3 members required under Maharashtra Cooperative Societies Act.",
        default: "11 is widely accepted and operationally efficient."
      },

      committee_term_years: {
        what: "Duration for which committee is elected.",
        why: "Balances continuity with accountability.",
        legal: "Generally fixed at 5 years under cooperative norms.",
        default: "5 years aligns with standard governance cycles."
      },

      // ================= VOTING =================
      quorum_general_body_percent: {
        what: "Minimum percentage of members required to conduct a meeting.",
        why: "Ensures decisions are representative and valid.",
        legal: "Usually between 20–25% depending on bye-laws.",
        default: "25% ensures strong participation."
      },

      redevelopment_consent_percent: {
        what: "Minimum member consent required for redevelopment decisions.",
        why: "Protects collective ownership rights.",
        legal: "Minimum 75% consent required as per redevelopment norms.",
        default: "75% ensures legal compliance and fairness."
      }
    };

    return guide[key] || null;
  };

  if (loading) {
    return (
      <AppShell>
        <div style={container}>Loading governance configuration...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>By-laws Governance Configuration</h2>

        {fields.map((f: any, index: number) => {
          const guide = getGuidance(f.key);

          return (
            <div key={f.key} style={card}>
              
              {/* HEADER */}
              <div style={questionRow}>
                <div style={question}>{f.label}</div>

                <div
                  style={tooltip}
                  onClick={() =>
                    setOpenInfo(openInfo === index ? null : index)
                  }
                >
                  ⓘ
                </div>
              </div>

              {/* EXPANDABLE EDUCATION */}
              {openInfo === index && guide && (
                <div style={infoBox}>
                  <div><b>What:</b> {guide.what}</div>
                  <div><b>Why:</b> {guide.why}</div>
                  <div><b>Legal:</b> {guide.legal}</div>
                  <div><b>Default Logic:</b> {guide.default}</div>
                </div>
              )}

              {/* INPUT */}
              {f.type === "select" ? (
                <select
                  value={values[f.key]}
                  onChange={(e) => updateValue(f.key, e.target.value)}
                  style={input}
                >
                  {(f.options || []).map((opt: any) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type={f.type === "number" ? "number" : "text"}
                  value={values[f.key]}
                  onChange={(e) => updateValue(f.key, e.target.value)}
                  style={input}
                />
              )}
            </div>
          );
        })}

        <div style={actions}>
          <button style={secondaryBtn} onClick={() => navigate(-1)}>
            Back
          </button>

          <button
            style={primaryBtn}
            onClick={() => {
              console.log("BUTTON CLICKED");
              proceed();
            }}
          >
            Continue to Preview
          </button>
        </div>
      </div>
    </AppShell>
  );
}

/* ===== STYLES ===== */

const container: CSSProperties = {
  padding: 24,
  maxWidth: 1000,
  margin: "0 auto",
};

const title: CSSProperties = {
  fontSize: 24,
  fontWeight: 600,
  marginBottom: 20,
};

const card: CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 20,
  backgroundColor: "#fff",
  marginBottom: 16,
};

const questionRow: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
};

const question: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
};

const tooltip: CSSProperties = {
  cursor: "pointer",
  color: "#6b7280",
};

const infoBox: CSSProperties = {
  marginTop: 12,
  padding: 12,
  backgroundColor: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: 8,
  fontSize: 13,
  lineHeight: 1.5,
};

const input: CSSProperties = {
  width: "100%",
  padding: "10px",
  marginTop: 12,
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  backgroundColor: "#fafafa",
};

const actions: CSSProperties = {
  marginTop: 20,
  display: "flex",
  justifyContent: "space-between",
};

const primaryBtn: CSSProperties = {
  padding: "12px 18px",
  backgroundColor: "#f97316",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  fontWeight: 600,
  cursor: "pointer",
};

const secondaryBtn: CSSProperties = {
  padding: "12px 18px",
  backgroundColor: "#e5e7eb",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};