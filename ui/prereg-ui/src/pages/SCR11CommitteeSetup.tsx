import AppShell from "../components/layout/AppShell";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSociety } from "../context/SocietyContext";


export default function CommitteeSetupPage() {
  const { society } = useSociety();
  const navigate = useNavigate();

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [loading, setLoading] = useState(false);

  const [flats, setFlats] = useState<any[]>([]);
  const [selectedFlat, setSelectedFlat] = useState<any>(null);
  const [owners, setOwners] = useState<any[]>([]);
  const [committee, setCommittee] = useState<any[]>([]);
  const [successMessage, setSuccessMessage] = useState("");

  console.log("CURRENT SOCIETY:", society);
  console.log(committee);


  /* ================= LOAD FLATS ================= */
  useEffect(() => {
    if (!society?.id) return;

    fetch(`/api/society/flats/?society_id=${society.id}`)
      .then((res) => res.json())
      .then((data) => setFlats(data))
      .catch(() => alert("Failed to load flats"));
  }, [society]);

  /* ================= AUTO TENURE ================= */
  useEffect(() => {
    if (startDate && !endDate) {
      const start = new Date(startDate);
      const end = new Date(start);

      end.setFullYear(end.getFullYear() + 1);
      end.setDate(end.getDate() - 1);

      const formatted = end.toISOString().split("T")[0];
      setEndDate(formatted);
    }
  }, [startDate]);

  /* ================= LOAD OWNERS ================= */
  const loadOwners = (flatId: number) => {
    fetch(`/api/society/ownership/?flat_id=${flatId}`)
      .then((res) => res.json())
      .then((data) => {
        setOwners(data);
        setSelectedFlat(flatId);
      })
      .catch(() => alert("Failed to load owners"));
  };

  /* ================= ADD ================= */
  const addMember = (owner: any) => {
    if (committee.some((c) => c.flat_id === selectedFlat)) {
      alert("Flat already added");
      return;
    }

    setCommittee([
      ...committee,
      {
        flat_id: selectedFlat,
        flat_number: flats.find((f) => f.id === selectedFlat)?.flat_number,
        owner_name: owner.name,
        
        person_id: owner.person_id, // ✅ CRITICAL ADD
        
        role: "MEMBER",
        maker: true,
        checker: false,
      },
    ]);

    setOwners([]);
    setSelectedFlat(null);
  };

  /* ================= ROLE ================= */
  const updateRole = (index: number, role: string) => {
    const updated = [...committee];
    updated[index].role = role;
    updated[index].checker =
      role === "CHAIRMAN" || role === "SECRETARY";
    setCommittee(updated);
  };

  /* ================= REMOVE ================= */
  const removeMember = (index: number) => {
    const updated = [...committee];
    updated.splice(index, 1);
    setCommittee(updated);
  };

  /* ================= CREATE ================= */
  const handleCreate = async () => {
    if (!startDate) {
      alert("Start Date is mandatory");
      return;
    }setSuccessMessage("Society Management Committee formed successfully and is active");

    setTimeout(() => {
      navigate("/operations");
    }, 1500);

    if (committee.length < 3) {
      alert("Minimum 3 committee members are required");
      return;
    }

    const roles = committee.map((c) => c.role);

    if (!roles.includes("CHAIRMAN")) {
      alert("Chairman is mandatory");
      return;
    }

    if (!roles.includes("SECRETARY")) {
      alert("Secretary is mandatory");
      return;
    }

    if (!roles.includes("TREASURER")) {
      alert("Treasurer is mandatory");
      return;
    }

    try {
      setLoading(true);

      // ================= CREATE COMMITTEE =================
      const res = await fetch("/api/society/committee/full-create/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          society_id: society.id,
          start_date: startDate,
          end_date: endDate || null,
          members: committee.map((c) => ({
            person_id: c.person_id,
            role: c.role,
          })),
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error);

      console.log("FULL RESPONSE:", data);

      // ================= MARK GOVERNANCE COMPLETE =================
      const stageRes = await fetch(
        "/api/society/onboarding/governance-complete/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            society_id: society.id,
          }),
        }
      );

      const stageData = await stageRes.json();

      if (!stageRes.ok) throw new Error(stageData.error);

      console.log("STAGE UPDATED:", stageData);

      // ================= REDIRECT =================
      navigate("/operations");

    } catch (err: any) {
      console.error(err);
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };
      {successMessage && (
        <div style={{
          marginBottom: 20,
          padding: "10px 14px",
          borderRadius: 8,
          backgroundColor: "#ecfdf5",
          color: "#065f46",
          fontWeight: 500
        }}>
          {successMessage}
        </div>
      )}
  /* ================= UI ================= */

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>
          Society Management Committee Setup{" "}
          <span style={required}>*</span>
        </h2>

        {/* TENURE */}
        <h3 style={sectionTitle}>Committee Tenure</h3>

        <label style={label}>
          Start Date <span style={required}>*</span>
        </label>
        <input
          type="date"
          style={input}
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />

        <label style={label}>End Date</label>
        <input
          type="date"
          style={input}
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        />

        {/* FLAT */}
        <h3 style={sectionTitle}>Select Flat</h3>

        <label style={label}>
          Flat Number <span style={required}>*</span>
        </label>
        <select
          style={input}
          value={selectedFlat || ""}
          onChange={(e) => loadOwners(Number(e.target.value))}
        >
          <option value="">Select Flat</option>
          {flats.map((f) => (
            <option key={f.id} value={f.id}>
              Flat {f.flat_number}
            </option>
          ))}
        </select>

        {/* OWNERS */}
        {owners.map((o, i) => {
          console.log("OWNER:", o);

          return (
            <div key={i} style={rowSoft}>
              <div style={fieldSoft}>
                {o.name} ({o.percentage}% ownership)
              </div>

              <button style={addBtn} onClick={() => addMember(o)}>
                Add
              </button>
            </div>
          );
        })}

        {/* INFO */}
        <div style={infoBox}>
          Minimum Requirements:
          <br />
          • Minimum 3 members
          <br />
          • Chairman, Secretary, Treasurer mandatory
        </div>

        {/* HEADER */}
        <div style={headerRow}>
          <div style={headerField}>Flat No</div>
          <div style={headerField}>Owner</div>
          <div style={headerField}>Designation</div>
          <div style={headerField}>Maker</div>
          <div style={headerField}>Checker</div>
          <div style={headerField}>Action</div>
        </div>

        {/* DATA */}
        {committee.map((c, i) => (
          <div key={i} style={row}>
            <div style={field}>{c.flat_number}</div>
            <div style={field}>{c.owner_name}</div>

            <select
              style={field}
              value={c.role}
              onChange={(e) => updateRole(i, e.target.value)}
            >
              <option value="CHAIRMAN">Chairman</option>
              <option value="SECRETARY">Secretary</option>
              <option value="TREASURER">Treasurer</option>
              <option value="VICE_CHAIRMAN">Vice Chairman</option>
              <option value="JOINT_SECRETARY">Joint Secretary</option>
              <option value="MEMBER">Committee Member</option>
              <option value="ADVISOR">Advisor</option>
            </select>

            <div style={field}>Yes</div>
            <div style={field}>{c.checker ? "Yes" : "No"}</div>

            <button style={removeBtn} onClick={() => removeMember(i)}>
              Remove
            </button>
          </div>
        ))}

        {/* CTA */}
        <button style={primaryBtn} onClick={handleCreate}>
          {loading ? "Creating..." : "Create Committee"}
        </button>
      </div>
    </AppShell>
  );
}

/* ===== STYLES ===== */

const container = { padding: 20 };

const title = {
  fontSize: 22,
  marginBottom: 20,
  fontWeight: 600,
};

const required = {
  color: "#f97316",
};

const label = {
  fontSize: 13,
  marginBottom: 4,
  display: "block",
};

const input = {
  width: "100%",
  padding: 10,
  marginBottom: 16,
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  backgroundColor: "#fafafa",
};

const sectionTitle = {
  fontSize: 16,
  marginTop: 20,
  marginBottom: 8,
  fontWeight: 600,
};

const headerRow = {
  display: "grid",
  gridTemplateColumns: "1fr 1.5fr 1.5fr 0.8fr 0.8fr 0.8fr",
  gap: 10,
  marginTop: 20,
  marginBottom: 10,
  fontWeight: 600,
};

const row = {
  display: "grid",
  gridTemplateColumns: "1fr 1.5fr 1.5fr 0.8fr 0.8fr 0.8fr",
  gap: 10,
  marginBottom: 10,
};

const headerField = {
  fontSize: 13,
  color: "#6b7280",
};

const field = {
  padding: 10,
  border: "1px solid #e5e7eb",
  borderRadius: 8,
};

const rowSoft = {
  display: "flex",
  gap: 10,
  marginBottom: 10,
  backgroundColor: "#fff7ed",
  padding: 10,
  borderRadius: 8,
};

const fieldSoft = {
  flex: 1,
  padding: 10,
};

const addBtn = {
  backgroundColor: "#f97316",
  color: "#fff",
  padding: "6px 12px",
  border: "none",
  borderRadius: 6,
};

const removeBtn = {
  backgroundColor: "#ef4444",
  color: "#fff",
  padding: "6px 10px",
  border: "none",
  borderRadius: 6,
};

const primaryBtn = {
  marginTop: 20,
  padding: "12px 18px",
  backgroundColor: "#f97316",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  fontWeight: 600,
};

const infoBox = {
  marginTop: 16,
  padding: 12,
  backgroundColor: "#fff7ed",
  borderRadius: 8,
  fontSize: 13,
};