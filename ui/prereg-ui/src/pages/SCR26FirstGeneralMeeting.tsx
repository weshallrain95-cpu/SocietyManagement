import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

/* ================= STYLES ================= */

const container: React.CSSProperties = { padding: 24 };

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

const label: React.CSSProperties = { color: "#666" };
const value: React.CSSProperties = { fontWeight: 500 };

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

export default function SCR26FirstGeneralMeeting() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id") || "";

  const [data, setData] = useState<any>(null);
  const [flats, setFlats] = useState<any[]>([]);
  const [ownersMap, setOwnersMap] = useState<{ [key: number]: any[] }>({});
  const [selected, setSelected] = useState<{ [key: number]: boolean }>({});

  const [meetingDate, setMeetingDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [meetingPlace, setMeetingPlace] = useState("");

  const [loading, setLoading] = useState(false);

  /* ================= LOAD FORMA DATA ================= */

  useEffect(() => {
    fetch(`/api/society/test-forma-access/?society_id=${societyId}`)
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setMeetingPlace(json.project_address || "");
      })
      .catch(console.error);
  }, [societyId]);

  /* ================= LOAD FLATS ================= */

  useEffect(() => {
    fetch(`/api/society/flats/?society_id=${societyId}`)
      .then((res) => res.json())
      .then((data) => {
        setFlats(Array.isArray(data) ? data : []);
      })
      .catch(() => alert("Failed to load flats"));
  }, [societyId]);

  /* ================= LOAD OWNERS ================= */

  const loadOwners = (flatId: number) => {
    if (ownersMap[flatId]) return;

    fetch(`/api/society/ownership/?flat_id=${flatId}`)
      .then((res) => res.json())
      .then((data) => {
        setOwnersMap((prev) => ({
          ...prev,
          [flatId]: Array.isArray(data) ? data : [],
        }));
      })
      .catch(() => alert("Failed to load owners"));
  };

  /* preload owners */
  useEffect(() => {
    flats.forEach((f) => loadOwners(f.id));
  }, [flats]);

  /* ================= FORMAT DATE ================= */

  const formatDate = (iso: string) => {
    const [y, m, d] = iso.split("-");
    return `${d}/${m}/${y}`;
  };

  /* ================= BUILD MEMBERS ================= */

  const buildMembers = () => {
    const selectedMembers = flats
      .filter((f) => selected[f.id])
      .map((f) => {
        const owners = ownersMap[f.id] || [];
        const owner = owners[0]; // FIRST OWNER ONLY

        return {
          flat: f.flat_number,
          name: owner?.name || owner?.full_name || "—",
          phone: owner?.phone || "",
        };
      });

    return selectedMembers
      .map(
        (m, i) =>
          `${i + 1}. ${m.name} (Flat ${m.flat}${m.phone ? `, ${m.phone}` : ""})`
      )
      .join("\n");
  };

  /* ================= GENERATE ================= */

  const handleGenerate = async () => {
    try {
      setLoading(true);

      const members_present = buildMembers();

      if (!members_present) {
        alert("Please select at least one member");
        return;
      }

      const payload = {
        society_id: societyId,
        artifact_code: "FIRST_GENERAL_MEETING_MINUTES_MH",
        data: {
          meeting_date: formatDate(meetingDate),
          meeting_place: meetingPlace,
          members_present,

          // 🔥 REQUIRED
          society_name: data.project_name,
          project_address: data.project_address,
          chief_promoter_name: data.chief_promoter_name,
        },
      };

      const res = await fetch("/api/society/documents/generate/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        alert("Generation failed");
        return;
      }

      alert("First General Meeting Minutes Generated");
      navigate("/registration-tracker");
    } catch (e) {
      console.error(e);
      alert("Error");
    } finally {
      setLoading(false);
    }
  };
      const allSelected = flats.length > 0 && flats.every((f) => selected[f.id]);

      const toggleSelectAll = () => {
        if (allSelected) {
            setSelected({});
        } else {
            const newSelected: { [key: number]: boolean } = {};
            flats.forEach((f) => {
            newSelected[f.id] = true;
            });
            setSelected(newSelected);
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
          <div style={title}>Meeting Summary</div>

          <div style={row}>
            <div style={label}>Society</div>
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

        {/* MEETING DETAILS */}
        <div style={card}>
          <div style={title}>Meeting Details</div>

          <input
            type="date"
            style={input}
            value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
          />

          <input
            type="text"
            style={input}
            value={meetingPlace}
            onChange={(e) => setMeetingPlace(e.target.value)}
          />
        </div>

        {/* MEMBERS */}
        <div style={card}>
          <div style={title}>Select Members Present</div>

          <div style={{ maxHeight: 300, overflowY: "auto" }}>
            {flats.map((f) => {
              const owners = ownersMap[f.id] || [];
              const owner = owners[0];

              return (
                <div key={f.id} style={{ padding: "6px 0" }}>
                  <label>
                    <input
                      type="checkbox"
                      checked={!!selected[f.id]}
                      onChange={(e) =>
                        setSelected((prev) => ({
                          ...prev,
                          [f.id]: e.target.checked,
                        }))
                      }
                    />{" "}
                    Flat {f.flat_number} |{" "}
                    {owner?.name || owner?.full_name || "—"}{" "}
                    {owner?.phone ? `| ${owner.phone}` : ""}
                  </label>
                </div>
              );
            })}
          </div>
        </div>
        </div>

        <div style={card}>
            <div style={title}>Select Members Present</div>

            {/* 🔥 ADD THIS */}
            <div style={{ marginBottom: 10 }}>
                <button
                style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    border: "1px solid #ccc",
                    cursor: "pointer",
                    background: "#f5f5f5",
                }}
                onClick={toggleSelectAll}
                >
                {allSelected ? "Clear All" : "Select All"}
                </button>
        </div>

        {/* ACTION */}
        <div style={card}>
          <button
            style={primaryBtn}
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Meeting Minutes"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}