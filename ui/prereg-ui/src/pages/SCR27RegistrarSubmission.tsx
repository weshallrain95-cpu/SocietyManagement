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

const input: React.CSSProperties = {
  width: "100%",
  padding: "10px",
  marginBottom: 12,
  borderRadius: 6,
  border: "1px solid #ddd",
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

export default function SCR27RegistrarSubmission() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id") || "";

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [submissionDate, setSubmissionDate] = useState(
    new Date().toISOString().split("T")[0]
  );

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

  /* ================= FORMAT DATE ================= */

  const formatDate = (iso: string) => {
    const [y, m, d] = iso.split("-");
    return `${d}/${m}/${y}`;
  };

  /* ================= GENERATE ================= */

  const handleGenerate = async () => {
    try {
      setLoading(true);

      const payload = {
        society_id: societyId,
        artifact_code: "REGISTRAR_SUBMISSION_LETTER_MH",
        data: {
          submission_date: formatDate(submissionDate),

          // 🔥 SAME PATTERN AS SCR24
          registrar_office: data.registrar_office,
          society_name: data.project_name,
          project_address: data.project_address,
          chief_promoter_name: data.chief_promoter_name,
        },
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

      alert("Registrar Submission Letter Generated");

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
          <div style={title}>Submission Summary</div>

          <div style={row}>
            <div style={label}>Society</div>
            <div style={value}>{data.project_name}</div>
          </div>

          <div style={row}>
            <div style={label}>Address</div>
            <div style={value}>{data.project_address}</div>
          </div>

          <div style={row}>
            <div style={label}>Registrar Office</div>
            <div style={value}>{data.registrar_office}</div>
          </div>

          <div style={row}>
            <div style={label}>Chief Promoter</div>
            <div style={value}>{data.chief_promoter_name}</div>
          </div>
        </div>

        {/* DATE */}
        <div style={card}>
          <div style={title}>Submission Date</div>

          <input
            type="date"
            style={input}
            value={submissionDate}
            onChange={(e) => setSubmissionDate(e.target.value)}
          />
        </div>

        {/* ACTION */}
        <div style={card}>
          <button
            style={primaryBtn}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Submission Letter"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}