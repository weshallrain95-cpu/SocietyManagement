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

/* ================= TYPES ================= */

type Member = {
  sr_no: number;
  name: string;
  flat_number: string;
};

type Data = {
  project_name: string;
  project_address: string;
  chief_promoter_name: string;
  meeting_date: string;
  meeting_place: string;
  committee_members: Member[];
};

/* ================= COMPONENT ================= */

export default function SCR22ProvisionalResolution() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id") || "";

  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(false);

  /* ================= FETCH PARSED DATA ================= */

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

  /* ================= DERIVED ================= */

  const resolutionNumber = data
    ? `${data.project_name.replace(/\s/g, "").toUpperCase()}-${societyId}-PCR-MH-V1`
    : "";

  /* ================= GENERATE ================= */

  const handleGenerate = async () => {
    if (!data) return;

    try {
      setLoading(true);

      const payload = {
        society_id: societyId,
        artifact_code: "PROVISIONAL_COMMITTEE_RESOLUTION_MH",
        data: {
          resolution_number: resolutionNumber,
          meeting_date: data.meeting_date,
          meeting_place: data.meeting_place,
          project_name: data.project_name,
          project_address: data.project_address,
          chief_promoter_name: data.chief_promoter_name,
          committee_members: data.committee_members
            .map((m) => `${m.sr_no} | ${m.name} | ${m.flat_number}`)
            .join("\n"),

          signatories: data.committee_members
            .map((m, i) => `${i + 1}. ${m.name}    __________________________`)
            .join("\n"),
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

      alert("Resolution Generated");

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
          <div style={title}>Resolution Summary</div>

          <div style={row}>
            <div style={label}>Resolution Number</div>
            <div style={value}>{resolutionNumber}</div>
          </div>

          <div style={row}>
            <div style={label}>Project</div>
            <div style={value}>{data.project_name}</div>
          </div>

          <div style={row}>
            <div style={label}>Address</div>
            <div style={value}>{data.project_address}</div>
          </div>

          <div style={row}>
            <div style={label}>Meeting Date</div>
            <div style={value}>{data.meeting_date}</div>
          </div>

          <div style={row}>
            <div style={label}>Meeting Place</div>
            <div style={value}>{data.meeting_place}</div>
          </div>

          <div style={row}>
            <div style={label}>Chief Promoter</div>
            <div style={value}>{data.chief_promoter_name}</div>
          </div>
        </div>

        {/* MEMBERS */}
        <div style={card}>
          <div style={title}>Committee Members</div>

          {data.committee_members.map((m) => (
            <div key={m.sr_no} style={row}>
              <div>{m.sr_no}. {m.name}</div>
              <div>{m.flat_number}</div>
            </div>
          ))}
        </div>

        {/* ACTION */}
        <div style={card}>
          <button
            style={primaryBtn}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Resolution"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}