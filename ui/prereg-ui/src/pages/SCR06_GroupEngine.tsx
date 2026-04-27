import AppShell from "../components/layout/AppShell";
import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";

/* ================= MAIN ================= */

export default function GroupEnginePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { wings = [] } = location.state || {};
  const incomingFloors = location.state?.floors;
  const structureType = location.state?.structureType;

  const unsupportedMultiWing =
    structureType === "MULTI" && (!incomingFloors || incomingFloors < 1);

  const [floors, setFloors] = useState(incomingFloors || 1);
  const [floorsLocked, setFloorsLocked] = useState(!!incomingFloors);

  const [groups, setGroups] = useState<any[]>([]);
  const [selectedFloors, setSelectedFloors] = useState<number[]>([]);
  const [activeGroup, setActiveGroup] = useState<number | null>(null);

  /* ================= HELPERS ================= */

  const assignedFloors = groups.flatMap((g) => g.floors);

  const isFloorTaken = (f: number) => assignedFloors.includes(f);

  const toggleFloor = (f: number) => {
    if (isFloorTaken(f)) return;

    setSelectedFloors((prev) =>
      prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]
    );
  };

  const addGroup = () => {
    if (selectedFloors.length === 0) return;

    setGroups([
      ...groups,
      {
        floors: [...selectedFloors].sort((a, b) => a - b),
        flats: [],
        maxFlats: 0,
      },
    ]);

    setSelectedFloors([]);
  };

  const deleteGroup = (index: number) => {
    const updated = groups.filter((_, i) => i !== index);
    setGroups(updated);
    setActiveGroup(null);
  };

  const allFloorsCovered =
    assignedFloors.length === floors &&
    new Set(assignedFloors).size === floors;

  /* ================= COMPRESS ================= */

  const compressLayout = (flats: any[]) => {
    const map: any = {};

    flats.forEach((f) => {
      const key = `${f.type}_${f.area}`;

      if (!map[key]) {
        map[key] = {
          type: f.type,
          area: f.area,
          count: 0,
        };
      }

      map[key].count += 1;
    });

    return Object.values(map);
  };

  // ================= FINAL ACTION =================

  const handleSubmit = async () => {
    if (!allFloorsCovered) return;

    try {
      const society = JSON.parse(localStorage.getItem("society") || "{}");

      const payload = {
        society_id: society?.id,

        // ✅ REQUIRED FIX
        structure_type: "GROUP",

        mode: "GROUP",
        total_wings: structureType === "MULTI" ? wings.length : 1,
        floors_per_wing: floors,

        groups: groups.map((g) => ({
          floors: g.floors,
          layout: compressLayout(g.flats),
        })),

        flat_numbering_style: "A-101",
      };

      const isInvalid = groups.some((g: any) =>
        g.flats.some((f: any) => !f.type || !f.area)
      );

      if (isInvalid) {
        alert("Please complete all flat details before proceeding");
        return;
      }

      const res = await axios.post(
        "http://localhost:8000/api/society/structure/generate/",
        payload
      );

      navigate("/structure-preview", {
        state: {
          result: res.data,
          source: "GROUP",
          mode: "GROUP",
          groups,
          floors,
          structureType,
          society_id: society?.id,
        },
      });

    } catch (err: any) {
      console.error(err);
      alert(err?.response?.data?.error || "Structure generation failed");
      return;
    }
  };

  /* ================= RENDER ================= */

  return (
    <AppShell>
      <div style={pageWrapper}>
        <div style={container}>

          <div style={header}>
            <h1 style={title}>Advanced Structure Setup</h1>
            <p style={subtitle}>
              Configure different floor groups intelligently
            </p>
          </div>

          <div style={card}>

            {unsupportedMultiWing && (
              <div style={warningBox}>
                For a complex user journey, where Floor AND Flat configurations
                are different across multiple wings, please use the Excel
                Structure Upload template.
              </div>
            )}

            {!floorsLocked && (
              <div style={{ marginBottom: 20 }}>
                <h3 style={label}>Enter Number of Floors</h3>

                <input
                  type="number"
                  value={floors}
                  onChange={(e) => setFloors(Number(e.target.value))}
                  style={input}
                />

                <button
                  style={primaryBtn}
                  onClick={() => {
                    if (floors < 1) return;
                    setFloorsLocked(true);
                  }}
                >
                  Confirm Floors
                </button>
              </div>
            )}

            {floorsLocked && (
              <>
                <h3 style={label}>Step 1: Select Floors for Group</h3>

                <div style={{ marginBottom: 10 }}>
                  {Array.from({ length: floors }, (_, i) => i + 1).map((f) => (
                    <button
                      key={f}
                      style={{
                        ...floorBtn,
                        background: selectedFloors.includes(f)
                          ? "#f97316"
                          : isFloorTaken(f)
                          ? "#d1d5db"
                          : "#e5e7eb",
                        color: selectedFloors.includes(f) ? "white" : "black",
                        cursor: isFloorTaken(f) ? "not-allowed" : "pointer",
                      }}
                      onClick={() => toggleFloor(f)}
                    >
                      {f}
                    </button>
                  ))}
                </div>

                <button style={secondaryBtn} onClick={addGroup}>
                  + Create Group
                </button>

                <div style={{ marginTop: 25 }}>
                  <h3 style={label}>Step 2: Configure Groups</h3>

                  {groups.length === 0 && (
                    <p style={{ color: "#6b7280" }}>
                      No groups created yet
                    </p>
                  )}

                  {groups.map((g, i) => (
                    <div key={i} style={groupCard}>
                      <div style={{ marginBottom: 10 }}>
                        <strong>Group {i + 1}</strong> — Floors:{" "}
                        {g.floors.join(", ")}
                      </div>

                      <div style={{ marginBottom: 10 }}>
                        <label style={{ fontWeight: 500 }}>
                          Flats per floor:
                        </label>
                        <input
                          type="number"
                          value={g.maxFlats}
                          min={1}
                          onChange={(e) => {
                            const updated = [...groups];
                            updated[i].maxFlats = Number(e.target.value);
                            setGroups(updated);
                          }}
                          style={{ ...input, marginTop: 5 }}
                        />
                      </div>

                      <div style={{ display: "flex", gap: 10 }}>
                        <button
                          style={secondaryBtn}
                          onClick={() => setActiveGroup(i)}
                        >
                          Configure
                        </button>

                        <button
                          style={dangerBtn}
                          onClick={() => deleteGroup(i)}
                        >
                          Delete
                        </button>
                      </div>

                      {activeGroup === i && (
                        <div style={{ marginTop: 15 }}>
                          <FlatConfigBlock
                            values={g.flats}
                            baseFloor={Math.min(...g.floors)}
                            maxFlats={g.maxFlats}
                            structureType={structureType}
                            setValues={(v: any) => {
                              const updated = [...groups];
                              updated[i].flats = v;
                              setGroups(updated);
                            }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div style={{ marginTop: 20 }}>
                  {!allFloorsCovered && (
                    <p style={{ color: "red" }}>
                      ⚠ All floors must be assigned to a group
                    </p>
                  )}

                  {allFloorsCovered && (
                    <p style={{ color: "green" }}>
                      ✔ All floors covered
                    </p>
                  )}
                </div>

                <div style={cta}>
                  <button
                    style={primaryBtn}
                    disabled={!allFloorsCovered}
                    onClick={handleSubmit}
                  >
                    Confirm & Generate Structure
                  </button>
                </div>
              </>
            )}

          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* ================= COMPONENT ================= */

function FlatConfigBlock({
  values,
  setValues,
  maxFlats,
  baseFloor,
  structureType,
}: any) {
  const types = ["1RK", "1BHK", "2BHK", "3BHK", "4BHK", "Studio"];

  const update = (i: number, key: string, val: any) => {
    const updated = [...values];
    updated[i] = { ...updated[i], [key]: val };
    setValues(updated);
  };

  return (
    <div>
      <h4 style={{ marginBottom: 10 }}>Flat Configuration</h4>

      <div style={{ display: "flex", gap: 10, marginBottom: 8 }}>
        <div style={{ ...input, fontWeight: 600 }}>Flat No</div>
        <div style={{ ...input, fontWeight: 600 }}>Type</div>
        <div style={{ ...input, fontWeight: 600 }}>Area (sqft)</div>
      </div>

      {values.map((v: any, i: number) => (
        <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10 }}>
          <input value={v.flat_number} disabled style={input} />

          <select
            value={v.type}
            onChange={(e) => update(i, "type", e.target.value)}
            style={input}
          >
            <option value="">Select Type</option>
            {types.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>

          <input
            type="number"
            value={v.area}
            onChange={(e) => update(i, "area", Number(e.target.value))}
            style={input}
          />
        </div>
      ))}

      <button
        style={secondaryBtn}
        disabled={values.length >= maxFlats || maxFlats === 0}
        onClick={() => {
          if (values.length >= maxFlats) return;

          const nextIndex = values.length + 1;
          const rawNumber = `${baseFloor}${String(nextIndex).padStart(2, "0")}`;

          const flatNumber =
            structureType === "MULTI"
              ? `A-${rawNumber}`
              : rawNumber;

          setValues([
            ...values,
            {
              flat_number: flatNumber,
              type: "",
              area: 0,
            },
          ]);
        }}
      >
        + Add Flat
      </button>
    </div>
  );
}

/* ================= STYLES ================= */

const warningBox = {
  background: "#fff7ed",
  border: "1px solid #fed7aa",
  padding: 15,
  borderRadius: 10,
  marginBottom: 20,
};

const pageWrapper = { padding: 20 };
const container = { maxWidth: 800, margin: "0 auto" };
const header = { marginBottom: 20 };
const title = { fontSize: 26, fontWeight: 600 };
const subtitle = { color: "#6b7280" };

const card = {
  background: "white",
  padding: 25,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
};

const label = { marginBottom: 10, fontWeight: 500 };

const groupCard = {
  border: "1px solid #e5e7eb",
  padding: 15,
  borderRadius: 10,
  marginBottom: 15,
};

const input = {
  width: "100%",
  padding: "10px",
  borderRadius: 8,
  border: "1px solid #d1d5db",
};

const floorBtn = {
  margin: 5,
  padding: 10,
  borderRadius: 8,
  border: "none",
};

const cta = {
  marginTop: 20,
  display: "flex",
  justifyContent: "flex-end",
};

const primaryBtn = {
  background: "#f97316",
  color: "white",
  border: "none",
  padding: "12px 18px",
  borderRadius: 8,
  cursor: "pointer",
};

const secondaryBtn = {
  background: "white",
  border: "1px solid #d1d5db",
  padding: "10px 14px",
  borderRadius: 8,
  cursor: "pointer",
};

const dangerBtn = {
  background: "#fee2e2",
  border: "1px solid #fecaca",
  padding: "10px 14px",
  borderRadius: 8,
  cursor: "pointer",
};