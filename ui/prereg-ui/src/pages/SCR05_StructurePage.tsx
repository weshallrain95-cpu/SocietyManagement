import AppShell from "../components/layout/AppShell";
import { useSociety } from "../context/SocietyContext";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

/* ================= MAIN ================= */

export default function StructurePage() {
  const { society } = useSociety();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [structureType, setStructureType] = useState<"SINGLE" | "MULTI" | "">("");

  const [wingCount, setWingCount] = useState(2);

  const [wings, setWings] = useState<
    { display_name: string; code: string }[]
  >([]);

  const [floors, setFloors] = useState(1);
  const [uniformFloors, setUniformFloors] = useState<boolean | null>(null);

  const [flatConfig, setFlatConfig] = useState<
    { type: string; area: number; count: number }[]
  >([]);

  const [flatsPerFloor, setFlatsPerFloor] = useState(1);
  const [baseFlats, setBaseFlats] = useState<any[]>([]);

  useEffect(() => {
    if (!society) navigate("/login");
  }, [society, navigate]);

  const totalSteps = structureType === "MULTI" ? 8 : 6;

  /* ================= HELPERS ================= */

  // 🔥 ONLY ADDITION (NON-GROUP FIX SUPPORT)
  const buildFlatStructure = (baseFlats: any[]) => {
    const map: Record<string, { type: string; area: number; count: number }> = {};

    baseFlats.forEach((flat) => {
      const key = `${flat.type}_${flat.area}`;

      if (!map[key]) {
        map[key] = {
          type: flat.type,
          area: flat.area,
          count: 0,
        };
      }

      map[key].count += 1;
    });

    return Object.values(map);
  };

  const generateFlatNumber = (index: number) => {
    const floor = 1;
    const suffix = String(index).padStart(2, "0");

    if (structureType === "SINGLE") {
      return `${floor}${suffix}`;
    }

    const wingCode = wings[0]?.code || "A";
    return `${wingCode}-${floor}${suffix}`;
  };

  const next = () => {
    if (step >= totalSteps) return;
    console.log("structureType:", structureType);
    if (step === 1 && !structureType) return;

    // 🔥 GROUP FLOW REDIRECT (CRITICAL FIX)
    if (
      uniformFloors === false &&
      (
        (structureType === "SINGLE" && step === 3) ||
        (structureType === "MULTI" && step === 5)
      )
    ) {
      navigate("/structure-groups", {
        state: {
          structureType,
          floors,
          wings: structureType === "MULTI" ? wings : [{ display_name: "Main", code: "A" }],
        },
      });
      return;
    }
    
    if (structureType === "MULTI") {

      // Step 2 → Wing count
      if (step === 2 && wingCount < 2) return;

      // Step 3 → Wing naming
      if (step === 3) {
        if (
          wings.length !== wingCount ||
          wings.some((w) => !w.display_name || !w.code)
        ) return;
      }

      // ✅ Step 4 → Floors (shifted, no uniformWings)
      if (step === 4 && floors < 1) return;

      // ✅ Step 5 → Uniform floors decision
      if (step === 5 && uniformFloors === null) return;

      // ✅ Step 6 → Flats per floor
      if (step === 6 && flatsPerFloor < 1) return;

      // ✅ Step 7 → Base config
      if (step === 7 && baseFlats.length === 0) return;
    }

    setStep(step + 1);
  };

  const back = () => setStep(step - 1);

  /* ================= RENDER ================= */

  return (
    <AppShell>
      <div style={pageWrapper}>
        <div style={container}>
          <div style={header}>
            <h1 style={title}>Society Structure Setup</h1>
            <p style={subtitle}>
              We’ll generate your entire building structure automatically
            </p>
          </div>

          <div style={stepIndicator}>
            Step {step} of {totalSteps}
          </div>

          <div style={card}>
            
          {step === 1 && (
            <OptionGroup
              title="Select Structure Type"
              options={[
                { label: "Single Building", value: "SINGLE" },
                { label: "Multiple Wings", value: "MULTI" },
              ]}
              value={structureType}
              onChange={setStructureType}
            />
          )}

          {step === 2 && structureType === "MULTI" && (
            <InputBlock
              title="Number of Wings"
              value={wingCount}
              onChange={setWingCount}
            />
          )}

          {step === 3 && structureType === "MULTI" && (
            <WingNamingBlock
              count={wingCount}
              values={wings}
              setValues={setWings}
            />
          )}

          {((structureType === "SINGLE" && step === 2) ||
            (structureType === "MULTI" && step === 4)) && (
            <InputBlock
              title="Number of Floors"
              value={floors}
              onChange={setFloors}
            />
          )}

          {((structureType === "SINGLE" && step === 3) ||
            (structureType === "MULTI" && step === 5)) && (
            <OptionGroup
              title="Same configuration on all floors?"
              options={[
                { label: "Yes", value: true },
                { label: "No", value: false },
              ]}
              value={uniformFloors}
              onChange={setUniformFloors}
            />
          )}

          {((structureType === "SINGLE" && step === 4) ||
            (structureType === "MULTI" && step === 6)) && (
            <InputBlock
              title="Flats per Floor"
              value={flatsPerFloor}
              onChange={(val: number) => {
                setFlatsPerFloor(val);

                const generated = Array.from({ length: val }, (_, i) => ({
                  flat_number: generateFlatNumber(i + 1),
                  type: "",
                  area: 0,
                }));

                setBaseFlats(generated);
              }}
            />
          )}

          {((structureType === "SINGLE" && step === 5) ||
            (structureType === "MULTI" && step === 7)) && (
            <BaseFloorConfigBlock
              values={baseFlats}
              setValues={setBaseFlats}
            />
          )}
            {/* CTA */}
            <div style={cta}>
              {step > 1 && (
                <button style={secondaryBtn} onClick={back}>
                  Back
                </button>
              )}

              <button
                style={primaryBtn}
                onClick={() => {
                  if (step === totalSteps) {

                    // 🔥 ONLY FIX — NON-GROUP API CALL
                    if (structureType === "SINGLE" && uniformFloors === true) {

                      const flat_structure = buildFlatStructure(baseFlats);

                      const payload = {
                        society_id: society?.id,
                        structure_type: "SINGLE",
                        total_wings: 1,   // ✅ FIXED
                        floors,
                        flat_structure,
                        flat_numbering_style: "A-101",
                      };

                      console.log("🚀 NON-GROUP PAYLOAD:", payload);

                      fetch("/api/society/structure/generate/", {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify(payload),
                      })
                        .then(res => res.json())
                        .then(data => {
                          console.log("✅ STRUCTURE RESPONSE:", data);

                          if (data.status === "success") {
                            navigate("/structure-preview", {
                              state: {
                                mode: "STANDARD",
                                floors,
                                flatsPerFloor,
                                baseFlats,
                                wings: [{ display_name: "Main", code: "A" }],
                              },
                            });
                          } else {
                            alert("Structure generation failed");
                          }
                        })
                        .catch(err => {
                          console.error("❌ STRUCTURE ERROR:", err);
                          alert("Something went wrong");
                        });

                      return;
                    }
                    
                    if (structureType === "MULTI" && uniformFloors === true) {

                      const flat_structure = buildFlatStructure(baseFlats);

                      const payload = {
                        society_id: society?.id,
                        structure_type: "SINGLE",   // ✅ still SINGLE engine
                        total_wings: wingCount,
                        floors,
                        flat_structure,
                        flat_numbering_style: "A-101",
                      };

                      console.log("🚀 MULTI NON-GROUP PAYLOAD:", payload);

                      fetch("/api/society/structure/generate/", {
                        method: "POST",
                        headers: {
                          "Content-Type": "application/json",
                        },
                        body: JSON.stringify(payload),
                      })
                        .then(res => res.json())
                        .then(data => {
                          console.log("✅ STRUCTURE RESPONSE:", data);

                          if (data.status === "success") {
                            navigate("/structure-preview", {
                              state: {
                                mode: "STANDARD",
                                floors,
                                flatsPerFloor,
                                baseFlats,
                                wings,
                              },
                            });
                          } else {
                            alert("Structure generation failed");
                          }
                        })
                        .catch(err => {
                          console.error("❌ STRUCTURE ERROR:", err);
                          alert("Something went wrong");
                        });

                      return;
                    }
                    
                    // 🔁 ORIGINAL FLOW (UNCHANGED)
                    let nextRoute = "/structure-preview";

                    if (uniformFloors === false) {
                      nextRoute = "/structure-groups";
                    }

                    navigate(nextRoute, {
                      state: {
                        mode: "STANDARD",
                        floors,
                        flatsPerFloor,
                        baseFlats,
                        wings:
                          structureType === "SINGLE"
                            ? [{ display_name: "Main", code: "A" }]
                            : wings,
                      },
                    });

                    return;
                  }

                  next();
                }}
              >
                {step === totalSteps ? "Confirm & Generate" : "Continue"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* ================= COMPONENTS ================= */

function BaseFloorConfigBlock({ values, setValues }: any) {
  const types = ["1RK", "1BHK", "2BHK", "3BHK", "4BHK", "Studio"];

  const update = (i: number, key: string, val: any) => {
    const updated = [...values];
    updated[i] = { ...updated[i], [key]: val };
    setValues(updated);
  };

  return (
    <div>
      <h3 style={label}>Configure Base Floor (Floor 1)</h3>

      {/* ✅ HEADER ROW */}
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
            placeholder="Area"
            value={v.area}
            onChange={(e) => update(i, "area", Number(e.target.value))}
            style={input}
          />
        </div>
      ))}
    </div>
  );
}

/* ===== REST UNCHANGED ===== */

function WingNamingBlock({ count, values, setValues }: any) {
  const update = (i: number, key: string, val: string) => {
    const updated = [...values];
    updated[i] = { ...updated[i], [key]: val };
    setValues(updated);
  };

  useEffect(() => {
    if (values.length !== count) {
      const newArr = Array.from({ length: count }, (_, i) => ({
        display_name: values[i]?.display_name || "",
        code: values[i]?.code || String.fromCharCode(65 + i),
      }));
      setValues(newArr);
    }
  }, [count]);

  return (
    <div>
      <h3 style={label}>Define Wing Names</h3>
      {values.map((wing: any, i: number) => (
        <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10 }}>
          <input
            placeholder="Display Name"
            value={wing.display_name}
            onChange={(e) => update(i, "display_name", e.target.value)}
            style={input}
          />
          <input
            placeholder="Code"
            value={wing.code}
            onChange={(e) => update(i, "code", e.target.value)}
            style={input}
          />
        </div>
      ))}
    </div>
  );
}

function OptionGroup({ title, options, value, onChange }: any) {
  return (
    <div>
      <h3 style={label}>{title}</h3>
      {options.map((o: any) => (
        <div
          key={o.label}
          onClick={() => onChange(o.value)}
          style={{
            ...option,
            border: value === o.value ? "2px solid #f97316" : "1px solid #e5e7eb",
            background: value === o.value ? "#fff7ed" : "white",
          }}
        >
          {o.label}
        </div>
      ))}
    </div>
  );
}

function InputBlock({ title, value, onChange }: any) {
  return (
    <div>
      <h3 style={label}>{title}</h3>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={input}
      />
    </div>
  );
}

/* ================= STYLES ================= */

const pageWrapper = { padding: 20 };
const container = { maxWidth: 700, margin: "0 auto" };
const header = { marginBottom: 20 };
const title = { fontSize: 26, fontWeight: 600 };
const subtitle = { color: "#6b7280" };
const stepIndicator = { marginBottom: 15, fontSize: 14, color: "#6b7280" };
const card = { background: "white", padding: 25, borderRadius: 14, border: "1px solid #e5e7eb" };
const label = { marginBottom: 10, fontWeight: 500 };
const option = { padding: 12, borderRadius: 10, marginBottom: 10, cursor: "pointer" };
const input = { width: "100%", padding: "10px", borderRadius: 8, border: "1px solid #d1d5db" };
const cta = { display: "flex", justifyContent: "space-between", marginTop: 20 };
const primaryBtn = { background: "#f97316", color: "white", border: "none", padding: "12px 18px", borderRadius: 8, cursor: "pointer" };
const secondaryBtn = { background: "white", border: "1px solid #d1d5db", padding: "12px 18px", borderRadius: 8, cursor: "pointer" };