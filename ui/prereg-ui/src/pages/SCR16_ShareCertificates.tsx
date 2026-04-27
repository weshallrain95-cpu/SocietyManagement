import AppShell from "../components/layout/AppShell";
import { useEffect, useState } from "react";
import { useSociety } from "../context/SocietyContext";
import { useNavigate } from "react-router-dom";
import type { CSSProperties } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function SCR16_ShareCertificates() {
  const { society } = useSociety();
  const navigate = useNavigate();

  const [preview, setPreview] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [issuing, setIssuing] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [issued, setIssued] = useState(false);

  // ================= FETCH PREVIEW =================
  useEffect(() => {
    if (!society?.id) return;

    fetch(`${API_BASE}/api/society/share-certificates/preview/?society_id=${society.id}`)
      .then(res => res.json())
      .then(data => {
        setPreview(data.preview || []);

        // ✅ AUTO DETECT GENERATED
        if (data.preview && data.preview.length > 0) {
          setGenerated(true);
        }
      })
      .catch(err => {
        console.error(err);
        alert("Failed to load preview");
      })
      .finally(() => setLoading(false));
  }, [society]);

  // ================= GENERATE =================
  const handleGenerate = async () => {
    if (!society?.id) return;

    try {
      setGenerating(true);

      const res = await fetch(
        `${API_BASE}/api/society/share-certificates/generate/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ society_id: society.id }),
        }
      );

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Generation failed");

      alert("Certificates Generated Successfully");
      setGenerated(true);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setGenerating(false);
    }
  };

  // ================= ISSUE =================
  const handleIssue = async () => {
    if (!society?.id) return;

    try {
      setIssuing(true);

      const res = await fetch(
        `${API_BASE}/api/society/share-certificates/issue/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ society_id: society.id }),
        }
      );

      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Issue failed");

      alert("Share Certificates Issed Successfully");

      setIssued(true);
      setGenerated(true);

      // 🔥 AUTO REDIRECT AFTER SUCCESS
      setTimeout(() => {
      navigate("/operations");
      }, 1500);


    } catch (err: any) {
      alert(err.message);
    } finally {
      setIssuing(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ padding: 24 }}>Loading Share Certificate Data...</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>Share Certificate Allocation</h2>

        {/* 🔹 STEP STATUS */}
        {!issued && (
          <div style={{ marginBottom: 10, fontWeight: 500 }}>
            {generated
              ? "Step 2 of 2 — Issue Certificates"
              : "Step 1 of 2 — Generate Certificates"}
          </div>
        )}

        {issued && (
          <div style={{ marginBottom: 10, color: "green", fontWeight: 600 }}>
            ✔ All Certificates Issued — Process Complete
          </div>
        )}

        {/* 🔹 PROGRESS BAR */}
        <div style={{
          width: "100%",
          height: 8,
          background: "#e5e7eb",
          borderRadius: 6,
          marginBottom: 20
        }}>
          <div style={{
            width: issued ? "100%" : generated ? "50%" : "0%",
            height: "100%",
            background: "#f97316",
            borderRadius: 6,
            transition: "0.3s"
          }} />
        </div>

        {/* ===== CONTEXT CARD ===== */}
        <div style={card}>
          <h3 style={sectionTitle}>Society Share Structure</h3>

          <div style={field}>Total Flats: {preview.length}</div>
          <div style={field}>Certificates to be issued: {preview.length}</div>
          <div style={field}>Shares per flat: 10</div>
          <div style={field}>Share value: ₹50</div>
        </div>

        {/* ===== DESCRIPTION ===== */}
        <div style={infoBox}>
          Each flat will receive a share certificate with a unique share number range.
        </div>

        {/* ===== PREVIEW ===== */}
        <div style={{ marginTop: 30 }}>
          <h3 style={sectionTitle}>Preview Allocation</h3>

          {preview.map((p, index) => (
            <div key={p.flat_id} style={card}>
              <div style={row}>
                <strong>{p.flat_number}</strong>
                <span>
                  Shares: {index * 10 + 1} – {(index + 1) * 10}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* ===== ACTION BUTTON ===== */}
        {!generated ? (
          <button style={primaryBtn} onClick={handleGenerate} disabled={generating}>
            {generating ? "Generating..." : "Generate Share Certificates"}
          </button>
        ) : !issued ? (
          <button style={primaryBtn} onClick={handleIssue} disabled={issuing}>
            {issuing ? "Issuing..." : "Issue Share Certificates"}
          </button>
        ) : (
          <div style={{ marginTop: 20, fontWeight: 600 }}>
            ✔ Process Complete
          </div>
        )}
      </div>
    </AppShell>
  );
}

/* ===== STYLES ===== */

const container: CSSProperties = {
  padding: 24,
  maxWidth: 900,
  margin: "0 auto",
};

const title: CSSProperties = {
  fontSize: 24,
  marginBottom: 24,
  fontWeight: 600,
};

const sectionTitle: CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  marginBottom: 12,
};

const card: CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 16,
  marginTop: 12,
  background: "#fff",
};

const field: CSSProperties = {
  marginTop: 6,
};

const row: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
};

const infoBox: CSSProperties = {
  marginTop: 18,
  padding: 14,
  background: "#f9fafb",
  borderRadius: 10,
};

const primaryBtn: CSSProperties = {
  marginTop: 30,
  padding: "14px 20px",
  backgroundColor: "#f97316",
  color: "#fff",
  border: "none",
  borderRadius: 10,
  fontWeight: 600,
  cursor: "pointer",
};