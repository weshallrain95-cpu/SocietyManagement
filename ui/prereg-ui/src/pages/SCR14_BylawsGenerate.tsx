import AppShell from "../components/layout/AppShell";
import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function SCR14_BylawsGenerate() {
  const location = useLocation();
  console.log("SCR14 STATE:", location.state);
  const navigate = useNavigate();

  const {
    society_id,
    formData,
    governance_hooks,
    normalized_hooks,
  } = location.state || {};

  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(false);

  /* ================= SAFETY ================= */

  useEffect(() => {
    if (!location.state) {
      navigate("/dashboard");
    }
  }, [location.state, navigate]);

  /* ================= GENERATE ================= */

  const handleGenerate = async () => {
    try {
      setLoading(true);

      const res = await fetch(
        `${API_BASE}/api/society/bylaws/generate/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            society_id,
            ...formData,
            ...(normalized_hooks || governance_hooks),
          }),
        }
      );

      const data = await res.json();

      console.log("BYLAWS GENERATED:", data);

      setGenerated(true);
      alert("By-laws generated successfully");

    } catch (err) {
      console.error("Generation failed", err);
      alert("Failed to generate by-laws");
    } finally {
      setLoading(false);
    }
  };

  /* ================= UI ================= */
  
  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>By-laws Preview & Generation</h2>

        {/* CONTEXT MESSAGE */}
        <div style={infoBox}>
          {formData?.legal_status === "REGISTERED"
            ? "These by-laws will be recreated for record purposes."
            : "These will be proposed by-laws for registration."}
        </div>

        {/* PREVIEW */}
        <div style={card}>
          <h3 style={sectionTitle}>Governance Configuration</h3>

          {Object.entries(normalized_hooks || governance_hooks || {}).map(([key, val]) => (
            <div key={key} style={row}>
              <div style={label}>
                {key.replaceAll("_", " ").toUpperCase()}
              </div>
              <div style={valueStyle}>{String(val)}</div>
            </div>
          ))}
        </div>

        {/* ACTIONS */}
        <div style={actions}>
          <button style={secondaryBtn} onClick={() => navigate(-1)}>
            Back
          </button>

          {!generated ? (
            <button
              style={primaryBtn}
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? "Generating..." : "Generate By-laws"}
            </button>
          ) : (
            <div style={{ display: "flex", gap: 10 }}>
              <button
                style={secondaryBtn}
                onClick={() => {
                  window.open(
                    `http://127.0.0.1:8000/api/society/bylaws/download/?society_id=${society_id}`
                  );
                }}
              >
                Download By-laws
              </button>

              <button
                style={primaryBtn}
                onClick={() =>
                  navigate("/bylaws-upload", {
                    state: { society_id },
                  })
                }
              >
                Upload Signed Copy
              </button>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

/* ================= STYLES ================= */

const container = {
  maxWidth: 900,
  margin: "0 auto",
  padding: 24,
};

const title = {
  fontSize: 24,
  fontWeight: 600,
  marginBottom: 20,
  color: "#111827",
};

const sectionTitle = {
  fontSize: 16,
  fontWeight: 600,
  marginBottom: 16,
  color: "#111827",
};

const card = {
  background: "#ffffff",
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 20,
  marginBottom: 20,
};

const row = {
  display: "flex",
  justifyContent: "space-between",
  padding: "10px 0",
  borderBottom: "1px solid #f3f4f6",
};

const label = {
  fontSize: 13,
  fontWeight: 500,
  color: "#6b7280",
  letterSpacing: "0.3px",
};

const valueStyle = {
  fontSize: 14,
  fontWeight: 600,
  color: "#111827",
};

const actions = {
  display: "flex",
  justifyContent: "space-between",
  marginTop: 10,
};

const primaryBtn = {
  padding: "10px 18px",
  background: "#f97316",
  color: "#ffffff",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
  fontWeight: 500,
};

const secondaryBtn = {
  padding: "10px 18px",
  background: "#f3f4f6",
  border: "1px solid #e5e7eb",
  borderRadius: 8,
  cursor: "pointer",
  fontWeight: 500,
};

const infoBox = {
  background: "#fff7ed",
  border: "1px solid #fed7aa",
  padding: 14,
  borderRadius: 10,
  marginBottom: 20,
  color: "#9a3412",
  fontSize: 14,
};
