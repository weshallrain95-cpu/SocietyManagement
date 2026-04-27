import { useSociety } from "../context/SocietyContext";
import AppShell from "../components/layout/AppShell";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

/* ================= TYPES ================= */

type Rules = {
  billing_target: "OWNER" | "TENANT" | "BOTH";

  vacant_type: "FULL" | "REDUCED" | "NONE";
  vacant_value?: number;

  dispute_enabled: boolean;
  dispute_hold_bill: boolean;
  dispute_apply_interest: boolean;

  waiver_authority: "COMMITTEE" | "CHAIRMAN" | "TREASURER";

  approval_mode: "SINGLE" | "DUAL";

  manager_enabled: boolean;
};

/* ================= MAIN ================= */

export default function SCR18MemberGovernanceRules() {
  const { society } = useSociety();
  const navigate = useNavigate();
  const [showPreview, setShowPreview] = useState(false);

  const [rules, setRules] = useState<Rules>({
    billing_target: "OWNER",

    vacant_type: "FULL",

    dispute_enabled: false,
    dispute_hold_bill: false,
    dispute_apply_interest: true,

    waiver_authority: "COMMITTEE",

    approval_mode: "SINGLE",

    manager_enabled: false,
  });

  /* ================= FETCH ================= */

  useEffect(() => {
    if (!society?.id) return;

    const fetchRules = async () => {
      try {
        const res = await fetch(`/api/society/operational-rules/?society_id=${society.id}`);
        const data = await res.json();

        if (data && !data.message) {
          setRules(data);
        }
      } catch (err) {
        console.error("Failed to fetch governance rules", err);
      }
    };

    fetchRules();
  }, [society]);

  /* ================= SAVE ================= */

  const handleSave = async () => {
    if (!society?.id) {
      alert("Society not found");
      return;
    }

    try {
      await fetch("/api/society/operational-rules/save/", {
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
            <h3 style={sectionTitle}>Review Governance Rules</h3>

            <p>Billing Target: {rules.billing_target}</p>
            <p>Vacant Rule: {rules.vacant_type} {rules.vacant_value ? `(${rules.vacant_value}%)` : ""}</p>

            <p>Disputes: {rules.dispute_enabled ? "Enabled" : "Disabled"}</p>

            <p>Waiver Authority: {rules.waiver_authority}</p>

            <p>Approval Mode: {rules.approval_mode}</p>

            <p>Manager Enabled: {rules.manager_enabled ? "Yes" : "No"}</p>

            <div style={{ display: "flex", gap: 10 }}>
              <button style={addBtn} onClick={() => setShowPreview(false)}>
                Edit
              </button>

              <button style={saveBtn} onClick={() => navigate("/financial-controls")}>
                Continue →
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div style={container}>

          {/* BILLING RESPONSIBILITY */}
          <div style={card}>
            <h3 style={sectionTitle}>Billing Responsibility</h3>
            <p style={desc}>
                Who will receive the maintenance bill — owner, tenant, or both. This only decides billing records, not who actually pays.
            </p>

            <select
              style={input}
              value={rules.billing_target}
              onChange={(e) =>
                setRules({ ...rules, billing_target: e.target.value as any })
              }
            >
              <option value="OWNER">Owner</option>
              <option value="TENANT">Tenant</option>
              <option value="BOTH">Owner + Tenant</option>
            </select>
          </div>

          {/* VACANT RULE */}
          <div style={card}>
            <h3 style={sectionTitle}>Vacant Flat Rules</h3>
            <p style={desc}>
                How maintenance should be charged when a flat is completely vacant (no resident). This is different from rented flats.
            </p>

            <select
              style={input}
              value={rules.vacant_type}
              onChange={(e) =>
                setRules({ ...rules, vacant_type: e.target.value as any })
              }
            >
              <option value="FULL">Full Charges</option>
              <option value="REDUCED">Reduced Charges</option>
              <option value="NONE">No Charges</option>
            </select>

            {rules.vacant_type === "REDUCED" && (
              <input
                style={input}
                type="number"
                placeholder="% reduction"
                value={rules.vacant_value || 0}
                onChange={(e) =>
                  setRules({
                    ...rules,
                    vacant_value: Number(e.target.value),
                  })
                }
              />
            )}
          </div>

          {/* DISPUTE */}
          <div style={card}>
            <h3 style={sectionTitle}>Dispute Handling</h3>
            <p style={desc}>
                Allow members to raise issues on bills. You can decide whether the bill pauses and whether interest continues during disputes.
            </p>

            <label style={label}>
              <input
                type="checkbox"
                checked={rules.dispute_enabled}
                onChange={(e) =>
                  setRules({ ...rules, dispute_enabled: e.target.checked })
                }
              />
              Allow Disputes
            </label>
            <p style={desc}>
                Members can challenge a bill before payment.
            </p>

            {rules.dispute_enabled && (
              <>
                <label style={label}>
                  <input
                    type="checkbox"
                    checked={rules.dispute_hold_bill}
                    onChange={(e) =>
                      setRules({ ...rules, dispute_hold_bill: e.target.checked })
                    }
                  />
                  Put Bill on Hold
                </label>
                <p style={desc}>
                    The bill will be paused until the dispute is resolved.
                </p>

                <label style={label}>
                  <input
                    type="checkbox"
                    checked={rules.dispute_apply_interest}
                    onChange={(e) =>
                      setRules({ ...rules, dispute_apply_interest: e.target.checked })
                    }
                  />
                  Apply Interest During Dispute
                </label>
                <p style={desc}>
                    If disabled, no late payment interest will be charged while dispute is active.
                </p>
              </>
            )}
          </div>

          {/* WAIVER */}
          <div style={card}>
            <h3 style={sectionTitle}>Waiver Control</h3>
            <p style={desc}>
                Decide who can reduce or remove charges such as penalties, interest, or special adjustments.
            </p>
            <select
              style={input}
              value={rules.waiver_authority}
              onChange={(e) =>
                setRules({ ...rules, waiver_authority: e.target.value as any })
              }
            >
              <option value="COMMITTEE">Committee</option>
              <option value="CHAIRMAN">Chairman</option>
              <option value="TREASURER">Treasurer</option>
            </select>
          </div>

          {/* APPROVAL ENGINE */}
          <div style={card}>
            <h3 style={sectionTitle}>Approval Flow</h3>
            <p style={desc}>
                Defines who can create transactions (makers) and who must approve them (checkers).
            </p>

            <p style={desc}>Makers: Committee Members {rules.manager_enabled && "+ Manager"}</p>
            <p style={desc}>Checkers: Chairman, Treasurer</p>

            <select
              style={input}
              value={rules.approval_mode}
              onChange={(e) =>
                setRules({ ...rules, approval_mode: e.target.value as any })
              }
            >
              <option value="SINGLE">Single Approval</option>
              <option value="DUAL">Dual Approval</option>
            </select>
          </div>

          {/* MANAGER */}
          <div style={card}>
            <h3 style={sectionTitle}>Society Manager</h3>
            <p style={desc}>
                Enable a manager role with permission to create transactions, but not approve them.
            </p>

            <label style={label}>
              <input
                type="checkbox"
                checked={rules.manager_enabled}
                onChange={(e) =>
                  setRules({ ...rules, manager_enabled: e.target.checked })
                }
              />
              Enable Manager Role (Maker Only)
            </label>
          </div>

          {/* SAVE */}
          <button style={saveBtn} onClick={handleSave}>
            Save Governance Rules
          </button>

        </div>
      )}
    </AppShell>
  );
}

/* ================= STYLES ================= */

const container = { maxWidth: 800, margin: "0 auto", padding: 20 };
const card = { background: "white", padding: 24, borderRadius: 14, border: "1px solid #e5e7eb", marginBottom: 20 };
const sectionTitle = { fontSize: 16, fontWeight: 600, marginBottom: 12 };
const label = { display: "block", marginTop: 10, marginBottom: 6 };
const input = { width: "100%", padding: "10px", borderRadius: 8, border: "1px solid #d1d5db" };
const desc = { fontSize: 12, color: "#6b7280" };
const addBtn = { background: "#fff7ed", border: "1px solid #f97316", padding: "10px 14px", borderRadius: 8 };
const saveBtn = { background: "#f97316", color: "white", padding: "12px 18px", borderRadius: 8, border: "none" };