import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

export default function SCR19FinancialControls() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id");

  const [form, setForm] = useState({
    max_spend_without_approval: "",
    committee_approval_limit: "",
    max_cash_spend_allowed: "",
  });

  const [loading, setLoading] = useState(false);

  const setValue = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const isValid = () =>
    Object.values(form).every((v) => v !== "" && !isNaN(Number(v)));

  const handleSubmit = async () => {
    if (!isValid()) {
      alert("Please fill all fields correctly");
      return;
    }

    try {
      setLoading(true);

      await fetch("/api/society/operational-rules/save/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          society_id: societyId,
          max_spend_without_approval: Number(form.max_spend_without_approval),
          committee_approval_limit: Number(form.committee_approval_limit),
          max_cash_spend_allowed: Number(form.max_cash_spend_allowed),

          // 🔥 completion flag
          financial_controls_configured: true,
        }),
      });

      navigate("/registration-tracker");
    } catch (e) {
      console.error(e);
      alert("Failed to save financial controls");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
        <div style={container}>
        <h2 style={title}>Financial Controls</h2>

        <div style={card}>
            <Field
            label="Spend Without Approval"
            desc="Transactions below this amount require no approval"
            value={form.max_spend_without_approval}
            onChange={(v) => setValue("max_spend_without_approval", v)}
            />

            <Field
            label="Committee Approval Limit"
            desc="Maximum amount committee can approve"
            value={form.committee_approval_limit}
            onChange={(v) => setValue("committee_approval_limit", v)}
            />

            <Field
            label="Maximum Cash Spend"
            desc="Maximum allowed amount for cash transactions"
            value={form.max_cash_spend_allowed}
            onChange={(v) => setValue("max_cash_spend_allowed", v)}
            />

            <button style={button} onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Complete Operations Setup"}
            </button>
        </div>
        </div>
        </AppShell>
    );
    }

    type FieldProps = {
    label: string
    desc: string;
    value: string;
    onChange: (v: string) => void;
    };


    function Field({ label, desc, value, onChange }: FieldProps) {
    return (
        <div style={fieldWrap}>
        <div style={labelStyle}>{label}</div>

        {/* 🔥 THIS LINE IS MISSING IN YOUR UI */}
        <div style={descStyle}>{desc}</div>

        <input
            type="number"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            style={input}
        />
        </div>
    );
    }
/* styles */

const descStyle = {
  fontSize: "13px",
  color: "#666",
  marginBottom: "6px",
};

const container = {
  padding: "32px",
  background: "#f9fafb",
  minHeight: "100vh",
};

const title = {
  fontSize: "24px",
  fontWeight: 600,
  marginBottom: "20px",
};

const card = {
  background: "#fff",
  padding: "24px",
  borderRadius: "10px",
  maxWidth: "600px",
};

const fieldWrap = {
  marginBottom: "18px",
};

const labelStyle = {
  fontWeight: 500,
};

const desc = {
  fontSize: "12px",
  color: "#666",
  marginBottom: "6px",
};

const input = {
  width: "100%",
  padding: "10px",
  borderRadius: "6px",
  border: "1px solid #ddd",
};

const button = {
  marginTop: "20px",
  background: "#f97316",
  color: "#fff",
  border: "none",
  padding: "12px",
  borderRadius: "8px",
  cursor: "pointer",
  width: "100%",
};