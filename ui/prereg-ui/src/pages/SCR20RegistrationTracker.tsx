import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

type Artifact = {
  code: string;
  name: string;
  desc: string;
};

export default function SCR20RegistrationTracker() {
  const navigate = useNavigate();
  const [society, setSociety] = useState<any>(null);
  const [statusMap, setStatusMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [packGenerated, setPackGenerated] = useState(false);
  const [fileMap, setFileMap] = useState<Record<string, string>>({});
  const artifacts: Artifact[] = [
  {
    code: "BYLAW_DRAFT_MH",
    name: "By-laws Draft",
    desc: "Society rules and structure",
  },
  {
    code: "FORM_A_MH",
    name: "Form A",
    desc: "Registrar application form",
  },
  {
    code: "PROVISIONAL_COMMITTEE_RESOLUTION_MH",
    name: "Provisional Committee Resolution",
    desc: "Define committee and appoint chief promoter",
  },
  {
    code: "PROMOTER_CONSENT_LETTER_MH",
    name: "Promoter Consent Letters",
    desc: "Collect owner approvals",
  },
  {
    code: "BUILDER_DOCUMENT_NOTICE_MH",
    name: "Builder Notice",
    desc: "Request documents from builder",
  },
  {
    code: "BANK_ACCOUNT_LETTER_MH",
    name: "Bank Account Letter",
    desc: "Open society bank account",
  },
  {
    code: "FIRST_GENERAL_MEETING_MINUTES_MH",
    name: "First General Meeting",
    desc: "Record first meeting decisions",
  },
  {
    code: "REGISTRAR_SUBMISSION_LETTER_MH",
    name: "Registrar Submission Letter",
    desc: "Final submission cover letter",
  },
];

  useEffect(() => {
    fetchSociety();
    fetchStatus();

    const timer = setTimeout(() => {
        fetchStatus();
    }, 500);

    return () => clearTimeout(timer);
    }, []);

  
  const fetchStatus = async () => {
    try {
        const societyId = localStorage.getItem("society_id");

        const res = await fetch(
            `/api/society/artifacts/status/?society_id=${societyId}`,
            {
                method: "GET",
                headers: {
                "Content-Type": "application/json",
                },
            }
        );
        
      const data = await res.json();

      const map: Record<string, string> = {};
      const fileMap: Record<string, string> = {};

      (data.documents || []).forEach((doc: any) => {
      map[doc.artifact_code] = doc.status || "NOT_STARTED";
      fileMap[doc.artifact_code] = doc.file || "";
      });

      setStatusMap(map);
      setFileMap(fileMap);
      
    } catch (e) {
      console.error(e);
      alert("Failed to load registration status");
    } finally {
      setLoading(false);
    }
  };
  
  const fetchSociety = async () => {
    try {
        const societyId = localStorage.getItem("society_id");

        const res = await fetch(
        `/api/society/details/?society_id=${societyId}`,
        {
            method: "GET",
            headers: {
            "Content-Type": "application/json",
            },
        }
    );

        const data = await res.json();
        setSociety(data);
    } catch (e) {
        console.error(e);
    }
    };

  useEffect(() => {
    const handleFocus = () => {
        fetchStatus();
    };

    window.addEventListener("focus", handleFocus);

    return () => window.removeEventListener("focus", handleFocus);
    }, []);

    const completedCount = Object.values(statusMap).filter(
    (s) => s === "GENERATED" || s === "UPLOADED"
    ).length;

    const allDone = completedCount === artifacts.length;

    const handleOpen = (code: string) => {
        const routeMap: Record<string, string> = {
            PROVISIONAL_COMMITTEE_RESOLUTION_MH: "/provisional-resolution",
            FORM_A_MH: "/form-a",
        };

        const route = routeMap[code];

        if (route) {
            navigate(route);
            return;
        }

        // fallback (keep system stable)
        navigate(`/documents/${code}`);
    };

  if (!society) {
    return (
        <AppShell>
        <div style={container}>Loading...</div>
        </AppShell>
    );
    }

  if (society.is_registered) {
  const [docs, setDocs] = useState<{
    registration_certificate: File | null;
    oc_certificate: File | null;
  }>({
    registration_certificate: null,
    oc_certificate: null,
  });

  const allUploaded =
    docs.registration_certificate && docs.oc_certificate;

  return (
    <AppShell>
      <div style={container}>
        <div style={card}>
          <div style={title}>Society Registered ✔</div>

          <div style={field}>
            <div style={label}>Society Name</div>
            <div>{society.name}</div>
          </div>

          <div style={field}>
            <div style={label}>Registration Number</div>
            <div>{society.registration_number || "-"}</div>
          </div>

          <div style={field}>
            <div style={label}>Registration Date</div>
            <div>{society.registration_date || "-"}</div>
          </div>

          {/* UPLOAD SECTION */}

          <div style={{ marginTop: "20px" }}>
            <div style={label}>Registration Certificate</div>
            <input
              type="file"
              onChange={(e) =>
                setDocs((p) => ({
                  ...p,
                  registration_certificate: e.target.files?.[0] || null,
                }))
              }
            />
          </div>

          <div style={{ marginTop: "16px" }}>
            <div style={label}>Occupancy Certificate (OC)</div>
            <input
              type="file"
              onChange={(e) =>
                setDocs((p) => ({
                  ...p,
                  oc_certificate: e.target.files?.[0] || null,
                }))
              }
            />
          </div>

          {!allUploaded && (
            <div style={warning}>
              Upload required documents to proceed
            </div>
          )}

          {allUploaded && (
            <button
                style={primaryBtn}
                onClick={() => navigate("/financial-controls")}
            >
                Proceed to Financial Onboarding
            </button>
            )}
        </div>
      </div>
    </AppShell>
  );
}
  const handleDownload = (code: string) => {
    const societyId = localStorage.getItem("society_id");

    // 🔥 BYLAWS SPECIAL CASE (only this line changes behavior)
    if (code === "BYLAW_DRAFT_MH") {
        window.open(
        `http://127.0.0.1:8000/api/society/bylaws/download/?society_id=${societyId}`
        );
        return;
    }

    // 🔹 EXISTING LOGIC (UNCHANGED)
    const file = fileMap[code];

    if (!file) {
        alert("No file available yet");
        return;
    }

    window.open(
        `http://127.0.0.1:8000/api/society/artifacts/download/?society_id=${societyId}&artifact_code=${code}`
    );
  };
  
  return (
    <AppShell>
      <div style={container}>
        {/* HEADER */}
        <div style={header}>
          <div style={title}>Society Registration</div>
          <div style={sub}>Status: <b>{allDone ? "Ready" : "In Progress"}</b></div>
          <div style={progress}>
            {completedCount} / {artifacts.length} Documents Completed
          </div>
        </div>

        {/* GRID */}
        {loading ? (
            <div>Loading...</div>
       ) : (
            <div style={tableWrap}>
                <table style={table}>
                <thead>
                    <tr>
                    <th style={th}>Artifact</th>
                    <th style={th}>Generate</th>
                    <th style={th}>Download</th>
                    <th style={th}>Upload</th>
                    <th style={th}>Extra Upload</th>
                    <th style={th}>Status</th>
                    </tr>
                </thead>

                <tbody>
                    {artifacts.map((a) => {
                    const status = statusMap[a.code] || "Not Started";
                    const hasFile = !!fileMap[a.code];
                    const isBylaws = a.code === "BYLAW_DRAFT_MH";
                    const index = artifacts.findIndex((x) => x.code === a.code);
                    const prev = artifacts[index - 1];
                    const prevHasFile = index <= 1 ? true : !!fileMap[prev?.code];
                    const canUpload = !isBylaws && status === "GENERATED" && !!fileMap[a.code];
                    
                    
                    const handleUpload = async (code: string, file: File | null) => {
                        if (!file) return;

                        try {
                            const formData = new FormData();
                            formData.append("file", file);
                            formData.append("artifact_code", code);
                            formData.append("society_id", localStorage.getItem("society_id") || "");

                            await fetch("/api/society/artifacts/upload/", {
                            method: "POST",
                            body: formData,
                            });

                            alert("Upload successful");

                            // refresh status
                            fetchStatus();
                     } catch (e) {
                            console.error(e);
                            alert("Upload failed");
                     }
                    };

                    const handleExtraUpload = async (code: string, file: File | null) => {
                        if (!file) return;

                        const formData = new FormData();
                        formData.append("file", file);
                        formData.append("artifact_code", code);
                        formData.append("society_id", localStorage.getItem("society_id") || "");

                        await fetch("/api/society/document-upload/", {
                            method: "POST",
                            body: formData,
                        });

                        fetchStatus(); // refresh
                    };
                    return (
                        <tr key={a.code}>
                        <td style={td}>
                            <div style={artifactTitle}>{a.name}</div>
                            <div style={artifactDesc}>{a.desc}</div>
                        </td>

                        <td style={td}>
                            <button
                                style={{
                                    ...miniBtn,
                                    opacity: hasFile || isBylaws || !prevHasFile ? 0.5 : 1,
                                    cursor: hasFile || isBylaws || !prevHasFile ? "not-allowed" : "pointer",
                                }}
                                disabled={hasFile || isBylaws || !prevHasFile}
                                onClick={() => handleOpen(a.code)}
                                >
                                Generate
                            </button>
                        </td>

                        <td style={td}>
                            <button
                                style={{
                                    ...miniBtn,
                                    opacity: isBylaws ? 0.5 : fileMap[a.code] ? 1 : 0.5,
                                    cursor: isBylaws ? "not-allowed" : fileMap[a.code] ? "pointer" : "not-allowed",
                                }}
                                disabled={isBylaws || !fileMap[a.code]}
                                onClick={() => {
                                    if (isBylaws) return;
                                    handleDownload(a.code);
                                }}
                                >
                                Download
                            </button>
                        </td>

                        <td style={td}>
                        

                                <input
                                type="file"
                                disabled={!canUpload}
                                style={{
                                    opacity: canUpload ? 1 : 0.5,
                                    cursor: canUpload ? "pointer" : "not-allowed",
                                }}
                                onChange={(e) =>
                                    handleUpload(a.code, e.target.files?.[0] || null)
                                }
                                />
                        </td>

                        <td style={td}>
                            <input
                                type="file"
                                accept="application/pdf"
                                disabled={status === "UPLOADED"}
                                onChange={(e) =>
                                    handleUpload(a.code, e.target.files?.[0] || null)
                              }
                            />
                        </td>
                        
                        <td style={td}>
                            {a.code === "BUILDER_DOCUMENT_NOTICE_MH" && status === "UPLOADED" ? (
                                <input
                                type="file"
                                accept="application/pdf"
                                onChange={(e) =>
                                    handleExtraUpload(a.code, e.target.files?.[0] || null)
                                }
                                />
                            ) : (
                                <span style={{ opacity: 0.4 }}>—</span>
                            )}
                        </td>

                        <td style={td}>
                            <b>{status}</b>
                        </td>
                        </tr>
                    );
                    })}
                </tbody>
                </table>
            </div>
            )}

        {/* FINAL ACTION PANEL */}
        <div style={actionCard}>
          <>
            {allDone && !packGenerated && (
                <>
                <div style={success}>All documents ready ✔</div>

                <button
                    style={primaryBtn}
                    onClick={() => setPackGenerated(true)}
                >
                    Generate Registrar Pack
                </button>
                </>
            )}

            {packGenerated && (
                <>
                <div style={success}>Registrar Pack Generated ✔</div>

                <div style={question}>
                    Have you submitted to Registrar?
                </div>

                <div>
                    <button
                    style={{
                        ...yesBtn,
                        background: submitted ? "#16a34a" : "#eee",
                        color: submitted ? "#fff" : "#000",
                    }}
                    onClick={() => setSubmitted(true)}
                    >
                    Yes
                    </button>

                    <button
                    style={{
                        ...noBtn,
                        background: !submitted ? "#dc2626" : "#eee",
                        color: !submitted ? "#fff" : "#000",
                    }}
                    onClick={() => setSubmitted(false)}
                    >
                    No
                    </button>
                </div>

                {submitted && (
                    <button
                    style={primaryBtn}
                    onClick={() => navigate("/financial-controls")}
                    >
                    Proceed to Financial Onboarding
                    </button>
                )}
                </>
            )}
            </>
        </div>
      </div>
    </AppShell>
  );
}


/* ---------------- STYLES ---------------- */

const tableWrap: React.CSSProperties = {
  overflowX: "auto",
};

const table = {
  width: "100%",
  borderCollapse: "collapse" as const,
  background: "#fff",
};

const th = {
  textAlign: "left" as const,
  padding: "12px",
  borderBottom: "1px solid #eee",
  fontSize: "13px",
  color: "#666",
};

const td = {
  padding: "12px",
  borderBottom: "1px solid #f1f1f1",
  verticalAlign: "top" as const,
};

const miniBtn = {
  background: "#f97316",
  color: "#fff",
  border: "none",
  padding: "6px 10px",
  borderRadius: "6px",
  cursor: "pointer",
  fontSize: "12px",
};

const warning = {
  marginTop: "10px",
  color: "#dc2626",
  fontSize: "13px",
};

const card = {
  background: "#fff",
  padding: "24px",
  borderRadius: "10px",
  maxWidth: "600px",
};

const field = {
  marginBottom: "16px",
};

const label = {
  fontSize: "13px",
  color: "#666",
  marginBottom: "4px",
};

const container = {
  padding: "32px",
  background: "#f9fafb",
  minHeight: "100vh",
};

const header = {
  marginBottom: "24px",
};

const title = {
  fontSize: "24px",
  fontWeight: 600,
};

const sub = {
  color: "#666",
  marginTop: "4px",
};

const progress = {
  marginTop: "6px",
  fontSize: "14px",
  color: "#333",
};


const artifactTitle = {
  fontWeight: 600,
  marginBottom: "6px",
};

const artifactDesc = {
  fontSize: "13px",
  color: "#666",
  marginBottom: "10px",
};


const actionCard = {
  marginTop: "28px",
  background: "#fff",
  padding: "20px",
  borderRadius: "10px",
};

const primaryBtn = {
  marginTop: "12px",
  background: "#16a34a",
  color: "#fff",
  padding: "12px",
  borderRadius: "8px",
  border: "none",
  cursor: "pointer",
};

const success = {
  color: "#16a34a",
  fontWeight: 600,
};

const question = {
  marginTop: "12px",
};

const yesBtn = {
  marginRight: "10px",
  padding: "10px",
};

const noBtn = {
  padding: "10px",
};