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

  const [uniformWings, setUniformWings] = useState<boolean | null>(null);

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

  const totalSteps = structureType === "MULTI" ? 9 : 6;

  /* ================= NAVIGATION ================= */

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

    if (step === 1 && !structureType) return;

    if (structureType === "MULTI") {
      if (step === 2 && wingCount < 2) return;

      if (step === 3) {
        if (
          wings.length !== wingCount ||
          wings.some((w) => !w.display_name || !w.code)
        ) return;
      }

      if (step === 4 && uniformWings === null) return;
    }

    if (
      ((structureType === "SINGLE" && step === 2) ||
        (structureType === "MULTI" && step === 5))
    ) {
      if (floors < 1) return;
    }

    if (
      ((structureType === "SINGLE" && step === 3) ||
        (structureType === "MULTI" && step === 6))
    ) {
      if (uniformFloors === null) return;
    }

    if (
      ((structureType === "SINGLE" && step === 4) ||
        (structureType === "MULTI" && step === 7))
    ) {
      if (flatsPerFloor < 1) return;
    }

    if (
      ((structureType === "SINGLE" && step === 5) ||
        (structureType === "MULTI" && step === 8))
    ) {
      if (baseFlats.length === 0) return;
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
            {/* STEP 1 */}
            {step === 1 && (
              <OptionGroup
                title="How is your society structured?"
                options={[
                  { label: "Single Building", value: "SINGLE" },
                  { label: "Multiple Wings", value: "MULTI" },
                ]}
                value={structureType}
                onChange={setStructureType}
              />
            )}

            {/* MULTI FLOW */}
            {structureType === "MULTI" && step === 2 && (
              <InputBlock
                title="Number of Wings"
                value={wingCount}
                onChange={setWingCount}
              />
            )}

            {structureType === "MULTI" && step === 3 && (
              <WingNamingBlock
                count={wingCount}
                values={wings}
                setValues={setWings}
              />
            )}

            {structureType === "MULTI" && step === 4 && (
              <OptionGroup
                title="Is FLOOR + FLAT configuration identical across all wings?"
                options={[
                  { label: "Yes", value: true },
                  { label: "No (use advanced setup)", value: false },
                ]}
                value={uniformWings}
                onChange={(val: boolean) => {
                  if (val === false) {
                    alert(
                      "For a complex user journey, use Excel Structure Upload."
                    );
                    navigate("/excel-upload-placeholder");
                  } else {
                    setUniformWings(val);
                  }
                }}
              />
            )}

            {/* FLOORS */}
            {(
              (structureType === "SINGLE" && step === 2) ||
              (structureType === "MULTI" && step === 5)
            ) && (
              <InputBlock
                title="Number of Floors"
                value={floors}
                onChange={setFloors}
              />
            )}

            {/* UNIFORM FLOORS */}
            {(
              (structureType === "SINGLE" && step === 3) ||
              (structureType === "MULTI" && step === 6)
            ) && (
              <OptionGroup
                title="Are ALL flats identical across floors?"
                options={[
                  { label: "Yes", value: true },
                  { label: "No (use advanced setup)", value: false },
                ]}
                value={uniformFloors}
                onChange={(val: boolean) => {
                  if (val === false) {
                    navigate("/structure-groups", {
                      state: { floors, wings, structureType },
                    });
                  } else {
                    setUniformFloors(val);
                  }
                }}
              />
            )}

            {/* FLATS PER FLOOR */}
            {(
              (structureType === "SINGLE" && step === 4) ||
              (structureType === "MULTI" && step === 7)
            ) && (
              <InputBlock
                title="Number of Flats per Floor"
                value={flatsPerFloor}
                onChange={(val: number) => {
                  setFlatsPerFloor(val);

                  const generated = Array.from({ length: val }, (_, i) => ({
                    index: i + 1,
                    flat_number: generateFlatNumber(i + 1),
                    type: "",
                    area: 0,
                  }));

                  setBaseFlats(generated);
                }}
              />
            )}

            {/* BASE FLOOR CONFIG */}
            {(
              (structureType === "SINGLE" && step === 5) ||
              (structureType === "MULTI" && step === 8)
            ) && (
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
                    navigate("/structure-preview", {
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
                  } else {
                    next();
                  }
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