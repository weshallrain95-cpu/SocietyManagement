import AppShell from "../components/layout/AppShell";
import { useLocation } from "react-router-dom";
import { useState } from "react";

/* ================= MAIN ================= */

export default function ExcelFlowPage() {
  const location = useLocation();
  const structureData = location.state || {};

  const hasStructure =
    structureData?.wings?.length > 0 &&
    structureData?.floors > 0;

  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  /* ================= HANDLERS ================= */

  const handleDownload = () => {
    try {
      setLoading(true);

      const societyId = structureData?.society_id;

      const url = `http://localhost:8000/api/society/structure/download-excel/?society_id=${societyId}`;

      console.log("DOWNLOAD URL:", url);

      // ✅ FIX — direct browser download (NO fetch)
      window.open(url, "_blank");

    } catch (err) {
      console.error(err);
      alert("Download failed");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setLoading(true);

      const society = JSON.parse(localStorage.getItem("society") || "{}");

      const formData = new FormData();
      formData.append("file", file);
      formData.append("society_id", society.id);

      const res = await fetch(
        "http://localhost:8000/api/society/structure/upload-ownership/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.message || "Upload failed");
      }

      alert("Structure + ownership successfully created");

      console.log("UPLOAD SUCCESS", data);

    } catch (err: any) {
      console.error(err);
      alert(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  /* ================= RENDER ================= */

  return (
    <AppShell>
      <div style={pageWrapper}>
        <div style={container}>

          {/* HEADER */}
          <div style={header}>
            <h1 style={title}>Advanced Structure Setup</h1>
            <p style={subtitle}>
              {hasStructure
                ? "Complete ownership details using Excel"
                : "Upload complete structure using Excel"}
            </p>
          </div>

          <div style={card}>

            {/* MODE MESSAGE */}
            <div style={infoBox}>
              {hasStructure ? (
                <>
                  Your structure has been generated. Download the template,
                  fill ownership details, and upload to complete setup.
                </>
              ) : (
                <>
                  Please download the template and define your full structure
                  including wings, floors, flat numbering and ownership.
                </>
              )}
            </div>

            {/* DOWNLOAD */}
            <div style={section}>
              <h3 style={label}>
                Step 1: {hasStructure ? "Download Generated Structure" : "Download Template"}
              </h3>

              <button style={primaryBtn} onClick={handleDownload}>
                {loading
                  ? "Preparing..."
                  : hasStructure
                  ? "Download Pre-Filled Excel"
                  : "Download Blank Template"}
              </button>
            </div>

            {/* INSTRUCTIONS */}
            <div style={section}>
              <h3 style={label}>Step 2: Fill Excel</h3>

              <p style={hint}>
                {hasStructure
                  ? "Fill ownership details (name, contact, share %)"
                  : "Define full structure + ownership details"}
              </p>
            </div>

            {/* UPLOAD */}
            <div style={section}>
              <h3 style={label}>Step 3: Upload Completed File</h3>

              <input
                type="file"
                accept=".xlsx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />

              <button
                style={primaryBtn}
                onClick={handleUpload}
                disabled={!file || loading}
              >
                {loading ? "Processing..." : "Upload & Create Structure"}
              </button>
            </div>

          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* ================= STYLES ================= */

const pageWrapper = { padding: 20 };
const container = { maxWidth: 700, margin: "0 auto" };

const header = { marginBottom: 20 };
const title = { fontSize: 26, fontWeight: 600 };
const subtitle = { color: "#6b7280" };

const card = {
  background: "white",
  padding: 25,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
};

const section = { marginTop: 25 };

const label = { fontWeight: 600, marginBottom: 10 };

const hint = { fontSize: 13, color: "#6b7280" };

const infoBox = {
  background: "#fff7ed",
  border: "1px solid #fed7aa",
  padding: 15,
  borderRadius: 10,
  marginBottom: 20,
};

const primaryBtn = {
  background: "#f97316",
  color: "white",
  border: "none",
  padding: "12px 18px",
  borderRadius: 8,
  cursor: "pointer",
};