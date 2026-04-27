// src/pages/SCR24BuilderNotice.tsx

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

export default function SCR24BuilderNotice() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id") || "";

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // UX Inputs
  const [noticeDate, setNoticeDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [builderName, setBuilderName] = useState("");
  const [builderAddress, setBuilderAddress] = useState("");
  const [reraNumber, setReraNumber] = useState("");

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
        artifact_code: "BUILDER_DOCUMENT_NOTICE_MH",
        data: {
            notice_date: noticeDate,
            builder_name: builderName,
            builder_address: builderAddress,
            rera_number: reraNumber,

            // 🔥 ADD THESE
            project_name: data.project_name,
            project_address: data.project_address,
            chief_promoter_name: data.chief_promoter_name,
          }
      };

      const res = await fetch("/api/society/documents/generate/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const json = await res.json();

      if (!res.ok) {
        alert(json?.error || "Generation failed");
        return;
      }

      

      alert("Builder Notice Generated");

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
          <div style={title}>Builder Notice Summary</div>

          <div style={row}>
            <div style={label}>Project</div>
            <div style={value}>{data.project_name}</div>
          </div>

          <div style={row}>
            <div style={label}>Address</div>
            <div style={value}>{data.project_address}</div>
          </div>

          <div style={row}>
            <div style={label}>Chief Promoter</div>
            <div style={value}>{data.chief_promoter_name}</div>
          </div>
        </div>

        {/* INPUTS */}
        <div style={card}>
          <div style={title}>Builder Details</div>

          <input
            type="date"
            style={input}
            value={noticeDate}
            onChange={(e) => setNoticeDate(e.target.value)}
          />

          <input
            type="text"
            placeholder="Builder Name"
            style={input}
            value={builderName}
            onChange={(e) => setBuilderName(e.target.value)}
          />

          <textarea
            placeholder="Builder Address"
            style={input}
            value={builderAddress}
            onChange={(e) => setBuilderAddress(e.target.value)}
          />

          <input
            type="text"
            placeholder="RERA Number (Optional)"
            style={input}
            value={reraNumber}
            onChange={(e) => setReraNumber(e.target.value)}
          />
        </div>

        {/* ACTION */}
        <div style={card}>
          <button
            style={primaryBtn}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Builder Notice"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}