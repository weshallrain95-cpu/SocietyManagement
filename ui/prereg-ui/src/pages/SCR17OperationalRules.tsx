import { useSociety } from "../context/SocietyContext";
import AppShell from "../components/layout/AppShell";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

/* ================= TYPES ================= */

type Charge = {
  name: string;
  type: "EQUAL" | "AREA";
  rate: number;
  description: string;
};

type Rules = {
  billing_cycle: "MONTHLY" | "QUARTERLY";
  billing_start_date?: string;
  generation_day: number;
  due_day: number;
  grace_days: number;
  charges: Charge[];
  interest_rules: {
    enabled: boolean;
    rate: number;
    after_days: number;
  };
  penalty_rules: {
    enabled: boolean;
    type: "FLAT" | "PERCENT";
    value: number;
    after_days: number;
  };
};

/* ================= MASTER DATA ================= */

const CHARGE_HEADS = [
  { label: "Maintenance", description: "Covers staff, cleaning, and daily operations", defaultRate: 2000 },
  { label: "Sinking Fund", description: "Reserve for long-term repairs", defaultRate: 500 },
  { label: "Water Charges", description: "Water usage and supply", defaultRate: 300 },
  { label: "Lift Maintenance", description: "Lift servicing and AMC", defaultRate: 250 },
  { label: "Parking Charges", description: "Parking allocation charges", defaultRate: 500 },
  { label: "Others", description: "Custom charge", defaultRate: 0 },
];

/* ================= MAIN ================= */

export default function SCR17OperationalRules() {
  const { society } = useSociety();
  const navigate = useNavigate();
  const [showPreview, setShowPreview] = useState(false);

  const [rules, setRules] = useState<Rules>({
    billing_cycle: "MONTHLY",
    generation_day: 1,
    due_day: 10,
    grace_days: 5,
    charges: [
      {
        name: "Maintenance",
        type: "EQUAL",
        rate: 2000,
        description: "Covers staff, cleaning, and daily operations",
      },
    ],
    interest_rules: { enabled: true, rate: 2, after_days: 10 },
    penalty_rules: { enabled: false, type: "FLAT", value: 500, after_days: 15 },
  });

  /* ================= FETCH ================= */

  useEffect(() => {
    if (!society?.id) return;

    const fetchRules = async () => {
      try {
        const res = await fetch(`/api/society/billing-rules/?society_id=${society.id}`);
        const data = await res.json();

        if (data && !data.message) {
          setRules((prev) => ({
            ...prev,
            ...data,
            interest_rules: {
              ...prev.interest_rules,
              ...data.interest_rules,
            },
            penalty_rules: {
              ...prev.penalty_rules,
              ...data.penalty_rules,
            },
          }));
        }
      } catch (err) {
        console.error("Failed to fetch billing rules", err);
      }
    };

    fetchRules();
  }, [society]);

  /* ================= HELPERS ================= */

  const updateCharge = <K extends keyof Charge>(
    i: number,
    field: K,
    value: Charge[K]
  ) => {
    const updated = [...rules.charges];
    updated[i] = { ...updated[i], [field]: value };
    setRules({ ...rules, charges: updated });
  };

  const handleChargeSelect = (i: number, label: string) => {
    const selected = CHARGE_HEADS.find((c) => c.label === label);

    const updated = [...rules.charges];
    updated[i] = {
      ...updated[i],
      name: label,
      description: selected?.description || "",
      rate: selected?.defaultRate || 0,
    };

    setRules({ ...rules, charges: updated });
  };

  /* ================= SAVE ================= */

  const handleSave = async () => {
    if (!society?.id) {
      alert("Society not found");
      return;
    }

    try {
      await fetch("/api/society/billing-rules/save/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          society_id: society.id,
          ...rules,
        }),
      });

      setShowPreview(true);
    } catch (err) {
      console.error("Save failed", err);
    }
  };

  /* ================= UI ================= */

  return (
    <AppShell>
            {showPreview ? (
                <div style={container}>
                <div style={card}>
                    <h3 style={sectionTitle}>Review Billing Rules</h3>

                    <p>Cycle: {rules.billing_cycle}</p>
                    <p>Generation Day: {rules.generation_day}</p>
                    <p>Due Day: {rules.due_day}</p>
                    <p>Grace: {rules.grace_days}</p>

                    <hr />

                    {rules.charges.map((c, i) => (
                    <div key={i} style={previewRow}>
                        <span>{c.name}</span>

                        <span>
                        ₹{c.rate}{" "}
                        <span style={{ fontSize: 12, color: "#6b7280" }}>
                            ({c.type === "AREA" ? "per sq ft" : "per flat"})
                        </span>
                        </span>
                    </div>
                    ))}

                    <div style={{ display: "flex", gap: 10 }}>
                    <button style={addBtn} onClick={() => setShowPreview(false)}>
                        Edit
                    </button>

                    <button
                        style={saveBtn}
                        onClick={() => navigate("/member-governance-rules")}
                    >
                        Continue →
                    </button>
                    </div>
                </div>
                </div>
            ) : (
                <div style={container}>

        {/* BILLING CONFIG */}
        <div style={card}>
          <h3 style={sectionTitle}>Billing Configuration</h3>

          <label style={label}>Billing Cycle</label>
          <select
            style={input}
            value={rules.billing_cycle}
            onChange={(e) =>
              setRules({
                ...rules,
                billing_cycle: e.target.value as "MONTHLY" | "QUARTERLY",
              })
            }
          >
            <option value="MONTHLY">Monthly</option>
            <option value="QUARTERLY">Quarterly</option>
          </select>

          <label style={label}>Billing Start Date</label>
            <input
            style={input}
            type="date"
            value={rules.billing_start_date || ""}
            onChange={(e) =>
                setRules({
                ...rules,
                billing_start_date: e.target.value,
                })
            }
            />

            <label style={label}>Billing Generation Day</label>
            <input
            style={input}
            type="number"
            value={rules.generation_day}
            onChange={(e) =>
                setRules({
                ...rules,
                generation_day: Math.max(1, Number(e.target.value)),
                })
            }
            />

          <label style={label}>Due Day</label>
          <input
            style={input}
            type="number"
            value={rules.due_day}
            onChange={(e) =>
              setRules({
                ...rules,
                due_day: Math.max(1, Number(e.target.value)),
              })
            }
          />

          <label style={label}>Grace Period</label>
          <input
            style={input}
            type="number"
            value={rules.grace_days}
            onChange={(e) =>
              setRules({
                ...rules,
                grace_days: Math.max(0, Number(e.target.value)),
              })
            }
          />
        </div>

        {/* CHARGES */}
        <div style={card}>
          <h3 style={sectionTitle}>Charge Heads</h3>

          {rules.charges.map((c, i) => (
            <div key={i} style={chargeBox}>
              <select
                style={input}
                value={c.name}
                onChange={(e) =>
                  handleChargeSelect(i, e.target.value)
                }
              >
                {CHARGE_HEADS.map((ch) => (
                  <option key={ch.label} value={ch.label}>
                    {ch.label}
                  </option>
                ))}
              </select>

              <p style={desc}>{c.description}</p>

              <div style={row}>
                <select
                  style={input}
                  value={c.type}
                  onChange={(e) =>
                    updateCharge(i, "type", e.target.value as "EQUAL" | "AREA")
                  }
                >
                  <option value="EQUAL">Equal</option>
                  <option value="AREA">Area</option>
                </select>

                <input
                  style={input}
                  type="number"
                  value={c.rate}
                  onChange={(e) =>
                    updateCharge(i, "rate", Math.max(0, Number(e.target.value)))
                  }
                />

                <button
                  style={removeBtn}
                  onClick={() =>
                    setRules({
                      ...rules,
                      charges: rules.charges.filter((_, idx) => idx !== i),
                    })
                  }
                >
                  ✕
                </button>
              </div>
            </div>
          ))}

          <button
            style={addBtn}
            onClick={() =>
              setRules({
                ...rules,
                charges: [
                  ...rules.charges,
                  { name: "Others", type: "EQUAL", rate: 0, description: "" },
                ],
              })
            }
          >
            + Add Charge Head
          </button>
        </div>

        {/* INTEREST */}
        <div style={card}>
          <h3 style={sectionTitle}>Late Payment Interest</h3>
            <p style={desc}>
            Applied as a percentage on overdue amounts after the due date
            </p>

          <label style={label}>
            <input
              type="checkbox"
              checked={rules.interest_rules.enabled}
              onChange={(e) =>
                setRules({
                  ...rules,
                  interest_rules: {
                    ...rules.interest_rules,
                    enabled: e.target.checked,
                  },
                })
              }
            />
            Apply Interest
          </label>

          {rules.interest_rules.enabled && (
            <div style={row}>
              <input
                style={input}
                type="number"
                value={rules.interest_rules.rate}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    interest_rules: {
                      ...rules.interest_rules,
                      rate: Number(e.target.value),
                    },
                  })
                }
              />
              <span>%</span>

              <input
                style={input}
                type="number"
                value={rules.interest_rules.after_days}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    interest_rules: {
                      ...rules.interest_rules,
                      after_days: Number(e.target.value),
                    },
                  })
                }
              />
              <span>days after due date</span>
            </div>
          )}
        </div>

        {/* PENALTY */}
        <div style={card}>
          <h3 style={sectionTitle}>Late Payment Penalty</h3>
          <p style={desc}>
               One-time charge applied when payment crosses a defined delay threshold
         </p>

          <label style={label}>
            <input
              type="checkbox"
              checked={rules.penalty_rules.enabled}
              onChange={(e) =>
                setRules({
                  ...rules,
                  penalty_rules: {
                    ...rules.penalty_rules,
                    enabled: e.target.checked,
                  },
                })
              }
            />
            Apply Penalty
          </label>

          {rules.penalty_rules.enabled && (
            <div style={row}>
              <select
                style={input}
                value={rules.penalty_rules.type}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    penalty_rules: {
                      ...rules.penalty_rules,
                      type: e.target.value as "FLAT" | "PERCENT",
                    },
                  })
                }
              >
                <option value="FLAT">Flat</option>
                <option value="PERCENT">%</option>
              </select>

              <input
                style={input}
                type="number"
                value={rules.penalty_rules.value}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    penalty_rules: {
                      ...rules.penalty_rules,
                      value: Number(e.target.value),
                    },
                  })
                }
              />

              <input
                style={input}
                type="number"
                value={rules.penalty_rules.after_days}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    penalty_rules: {
                      ...rules.penalty_rules,
                      after_days: Number(e.target.value),
                    },
                  })
                }
              />
            </div>
          )}
        </div>

        {/* FINAL SAVE */}
        <button style={saveBtn} onClick={handleSave}>
            
          Save Rules
        </button>

          </div>
        )}
    </AppShell>
  );
}

/* ================= STYLES ================= */

const container = { maxWidth: 800, margin: "0 auto", padding: 20 };
const header = { marginBottom: 20 };
const title = { fontSize: 26, fontWeight: 600 };
const subtitle = { color: "#6b7280" };
const card = { background: "white", padding: 24, borderRadius: 14, border: "1px solid #e5e7eb", marginBottom: 20 };
const sectionTitle = { fontSize: 16, fontWeight: 600, marginBottom: 12 };
const label = { display: "block", marginTop: 10, marginBottom: 6 };
const input = { width: "100%", padding: "10px", borderRadius: 8, border: "1px solid #d1d5db" };
const row = { display: "flex", gap: 10, marginTop: 10 };
const chargeBox = { border: "1px solid #e5e7eb", padding: 14, borderRadius: 10, marginBottom: 12 };
const desc = { fontSize: 12, color: "#6b7280" };
const previewRow = { display: "flex", justifyContent: "space-between" };
const addBtn = { background: "#fff7ed", border: "1px solid #f97316", padding: "10px 14px", borderRadius: 8 };
const removeBtn = { background: "#fee2e2", border: "none", padding: "6px 10px", borderRadius: 6 };
const saveBtn = { background: "#f97316", color: "white", padding: "12px 18px", borderRadius: 8, border: "none" };