import { useEffect, useState } from "react";
import { useSociety } from "../context/SocietyContext";

const API_BASE = "http://127.0.0.1:8000";

interface Decision {
  id: number;
  decision_code: string;
  question: string;
  description: string;
  default_value: string;
  legal_reference: string;
  sequence_order: number;
}

export function BylawDecisionWorkspace() {
  const { society } = useSociety();
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [values, setValues] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/bylaws/decisions`)
      .then(res => res.json())
      .then(data => {
        setDecisions(data.decisions);
        const defaults: Record<number, string> = {};
        data.decisions.forEach((d: Decision) => {
          defaults[d.id] = d.default_value;
        });
        setValues(defaults);
      })
      .finally(() => setLoading(false));
  }, []);

  const updateValue = (id: number, value: string) => {
    setValues(prev => ({ ...prev, [id]: value }));
  };

  const saveDecisions = async () => {
    if (!society) return;

    await fetch(`${API_BASE}/api/bylaws/save`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        society_id: society.id,
        decisions: values,
      }),
    });

    alert("By-law decisions saved.");
  };

  if (loading) {
    return <div style={{ padding: 24 }}>Loading by-law decisions…</div>;
  }

  return (
    <div style={{ padding: "24px", maxWidth: "900px", margin: "0 auto" }}>
      <h1>By-law Configuration</h1>
      <p style={{ color: "#666" }}>
        These decisions define how your society will function legally and operationally.
      </p>

      {decisions.map(decision => (
        <div
          key={decision.id}
          style={{
            border: "1px solid #ddd",
            borderRadius: "10px",
            padding: "18px",
            marginTop: "18px",
            background: "#fff",
          }}
        >
          <h3>{decision.question}</h3>

          <p style={{ marginTop: "6px" }}>{decision.description}</p>

          <p style={{ fontSize: "13px", color: "#888", marginTop: "8px" }}>
            Legal reference: {decision.legal_reference}
          </p>

          <input
            value={values[decision.id] || ""}
            onChange={e => updateValue(decision.id, e.target.value)}
            style={{
              marginTop: "12px",
              padding: "10px",
              width: "100%",
              borderRadius: "6px",
              border: "1px solid #ccc",
            }}
          />
        </div>
      ))}

      <button
        onClick={saveDecisions}
        style={{
          marginTop: "28px",
          padding: "12px 18px",
          fontSize: "16px",
          borderRadius: "8px",
          background: "#1e293b",
          color: "#fff",
          border: "none",
        }}
      >
        Save by-law decisions
      </button>
    </div>
  );
}
