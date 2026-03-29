import AppShell from "../components/layout/AppShell";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSociety } from "../context/SocietyContext";

export default function OwnershipRefinementPage() {
  const { society } = useSociety();
  const navigate = useNavigate();

  const [flats, setFlats] = useState<any[]>([]);
  const [selectedFlat, setSelectedFlat] = useState<any>(null);
  const [owners, setOwners] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  /* ================= LOAD FLATS ================= */

  useEffect(() => {
    if (!society?.id) return;

    fetch(`/api/society/flats/?society_id=${society.id}`)
      .then((res) => res.json())
      .then((data) => setFlats(data))
      .catch(() => alert("Failed to load flats"));
  }, [society]);

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

  /* ================= ADD OWNER ================= */

  const addOwner = () => {
    setOwners([
      ...owners,
      { name: "", phone: "", percentage: "" },
    ]);
  };

  /* ================= UPDATE OWNER ================= */

  const updateOwner = (index: number, field: string, value: any) => {
    const updated = [...owners];
    updated[index][field] = value;
    setOwners(updated);
  };

  /* ================= SAVE ================= */

  const handleSave = async () => {
    if (!selectedFlat) {
      alert("Please select a flat");
      return;
    }

    const total = owners.reduce(
      (sum, o) => sum + Number(o.percentage || 0),
      0
    );

    if (total !== 100) {
      alert("Total ownership must be 100%");
      return;
    }

    try {
      setLoading(true);

      // 🔍 DEBUG (VERY IMPORTANT)
      console.log("SENDING:", {
        flat_id: selectedFlat,
        owners,
      });

      const res = await fetch("/api/society/ownership/update/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          flat_id: selectedFlat,
          owners,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Server error");
      }

      alert("Ownership updated");

      // 🔥 RESET FORM CLEANLY
      setSelectedFlat(null);
      setOwners([]);

    } catch (err: any) {
      console.error(err);
      alert(err.message || "Failed to update ownership");
    } finally {
      setLoading(false);
    }
  };

  /* ================= COMPLETE ================= */

  const handleComplete = async () => {
    try {
      const res = await fetch("/api/society/onboarding/complete/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          society_id: society.id,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to complete onboarding");
      }

      // 🔥 HARD REDIRECT (ENSURES GUARD RELOAD)
      window.location.href = "/dashboard";

    } catch (err: any) {
      alert(err.message);
    }
  };

  /* ================= UI ================= */

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>Ownership Refinement</h2>

        {/* SELECT FLAT */}
        <select
          style={input}
          value={selectedFlat || ""}
          onChange={(e) => loadOwners(Number(e.target.value))}
        >
          <option value="">Select Flat</option>
          {flats.map((f) => (
            <option key={f.id} value={f.id}>
              {f.flat_number}
            </option>
          ))}
        </select>

        {/* OWNERS */}
        {owners.map((o, i) => (
          <div key={i} style={row}>
            <input
              style={field}
              placeholder="Name"
              value={o.name}
              onChange={(e) =>
                updateOwner(i, "name", e.target.value)
              }
            />

            <input
              style={field}
              placeholder="Phone"
              value={o.phone}
              onChange={(e) =>
                updateOwner(i, "phone", e.target.value)
              }
            />

            <input
              style={field}
              placeholder="%"
              value={o.percentage}
              onChange={(e) =>
                updateOwner(i, "percentage", e.target.value)
              }
            />
          </div>
        ))}

        {/* ADD OWNER */}
        <button style={secondaryBtn} onClick={addOwner}>
          + Add Owner
        </button>

        {/* ACTIONS */}
        <div style={cta}>
          <button
            style={primaryBtn}
            onClick={handleSave}
            disabled={!selectedFlat || loading}
          >
            {loading ? "Saving..." : "Save Flat"}
          </button>

          <button style={successBtn} onClick={handleComplete}>
            Finish & Complete
          </button>
        </div>
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

const input = {
  width: "100%",
  padding: 10,
  marginBottom: 20,
  borderRadius: 8,
  border: "1px solid #d1d5db",
};

const row = {
  display: "flex",
  gap: 10,
  marginBottom: 10,
};

const field = {
  flex: 1,
  padding: 10,
  borderRadius: 8,
  border: "1px solid #d1d5db",
};

const cta = {
  marginTop: 20,
  display: "flex",
  gap: 10,
};

const primaryBtn = {
  padding: "10px 16px",
  backgroundColor: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};

const secondaryBtn = {
  marginTop: 10,
  marginBottom: 10,
  padding: "8px 14px",
  backgroundColor: "#f3f4f6",
  border: "1px solid #d1d5db",
  borderRadius: "8px",
  cursor: "pointer",
};

const successBtn = {
  padding: "10px 16px",
  backgroundColor: "#16a34a",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
};