// src/pages/SCR23PromoterConsent.tsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

/* ================= STYLES ================= */

const container: React.CSSProperties = {
  padding: 24,
};

const card: React.CSSProperties = {
  background: "#fff",
  padding: 20,
  borderRadius: 12,
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
  marginBottom: 20,
};

const title: React.CSSProperties = {
  fontSize: 18,
  fontWeight: 600,
  marginBottom: 10,
};

const row: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  padding: "6px 0",
  borderBottom: "1px solid #eee",
};

const label: React.CSSProperties = {
  color: "#666",
};

const value: React.CSSProperties = {
  fontWeight: 500,
};

const primaryBtn: React.CSSProperties = {
  background: "#ff7a00",
  color: "#fff",
  padding: "12px 18px",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
};

/* ================= COMPONENT ================= */

export default function SCR23PromoterConsent() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id") || "";

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  /* ================= FETCH ================= */

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `/api/society/test-forma-access/?society_id=${societyId}`
        );

        const json = await res.json();
        setData(json);
      } catch (e) {
        console.error(e);
      }
    };

    fetchData();
  }, [societyId]);

  /* ================= GENERATE ================= */

  const handleGenerate = async () => {
    try {
      setLoading(true);

      const payload = {
        society_id: societyId,
        artifact_code: "PROMOTER_CONSENT_LETTER_MH",
      };

      const res = await fetch("/api/society/documents/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Generation failed");
        return;
      }

      alert("Consent Letters Generated");

      navigate("/registration-tracker");
    } catch (e) {
      console.error(e);
      alert("Error");
    } finally {
      setLoading(false);
    }
  };

  /* ================= UI ================= */

  if (!data) {
    return (
      <AppShell>
        <div style={container}>Loading...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div style={container}>
        {/* SUMMARY */}
        <div style={card}>
          <div style={title}>Consent Letters Summary</div>

          <div style={row}>
            <div style={label}>Project</div>
            <div style={value}>{data.project_name}</div>
          </div>

          <div style={row}>
            <div style={label}>Address</div>
            <div style={value}>{data.project_address}</div>
          </div>

          <div style={row}>
            <div style={label}>Total Members</div>
            <div style={value}>
              {data.committee_members?.length || 0}
            </div>
          </div>
        </div>

        {/* ACTION */}
        <div style={card}>
          <button
            style={primaryBtn}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Consent Letters"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}