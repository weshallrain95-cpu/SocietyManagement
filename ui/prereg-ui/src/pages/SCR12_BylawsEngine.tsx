import AppShell from "../components/layout/AppShell";
import { useEffect, useState } from "react";
import { useSociety } from "../context/SocietyContext";
import { useNavigate } from "react-router-dom";
import type { CSSProperties } from "react";

const API_BASE = "http://127.0.0.1:8000";

interface Decision {
  id: number;
  decision_code: string;
  category: string;
  question: string;
  description: string;
  legal_reference: string;
  allowed_values: any;
  default_value: any;
  sequence_order: number;
}

export default function SCR12_BylawsEngine() {
  const { society } = useSociety();
  const navigate = useNavigate();
  

  /* ================= NEW: SOCIETY DETAILS ================= */
  const [societyDetails, setSocietyDetails] = useState<any>(null);
  const [detailsLoading, setDetailsLoading] = useState(true);

  const [formData, setFormData] = useState<any>({
    society_name: "",
    registration_number: "",
    registration_date: "",
    registered_address: "",
    district: "",
    state_code: "",
    adoption_date: "",
  });

  /* ================= EXISTING STATE ================= */
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [values, setValues] = useState<Record<number, any>>({});
  const [loading, setLoading] = useState(true);
  const [adoptionDate, setAdoptionDate] = useState("");

  /* ================= FETCH SOCIETY DETAILS ================= */
  useEffect(() => {
    if (society === null) return; // wait for context

    if (!society?.id) {
      console.error("No society ID available");
      return;
    }

    const API_BASE = "http://127.0.0.1:8000";
    fetch(`${API_BASE}/api/society/details/?society_id=${society.id}`)

      .then(res => res.json())
      .then(data => {
        console.log("DETAILS API:", data);

        setSocietyDetails(data);

        setFormData({
          society_name: data.name || "",
          registration_number: data.registration_number || "",
          registration_date: data.registration_date || "",
          registered_address: data.registered_address || "",
          district: data.district || "",
          state_code: data.state_code || "",
          adoption_date: "",
        });
      })
      .catch(err => console.error(err))
      .finally(() => setDetailsLoading(false));
  }, [society]);

  /* ================= FETCH DECISIONS ================= */
  useEffect(() => {
    
    const API_BASE = "http://127.0.0.1:8000";
    fetch(`${API_BASE}/api/society/details/?society_id=${society.id}`)

      .then(res => res.json())
      .then(data => {
        const sorted = data.decisions.sort(
          (a: Decision, b: Decision) => a.sequence_order - b.sequence_order
        );

        setDecisions(sorted);

        const defaults: Record<number, any> = {};
        sorted.forEach((d: Decision) => {
          defaults[d.id] = d.default_value;
        });

        setValues(defaults);
      })
      .finally(() => setLoading(false));
  }, []);

  /* ================= UPDATE ================= */
  const updateValue = (id: number, value: any) => {
    setValues(prev => ({ ...prev, [id]: value }));
  };

  const updateField = (key: string, value: any) => {
    setFormData((prev: any) => ({
      ...prev,
      [key]: value,
    }));
  };

  /* ================= VALIDATION ================= */
  const validate = () => {
    if (formData.registration_number && !formData.adoption_date) {
      alert("Adoption date is required for registered societies");
      return false;
    }

    for (const d of decisions) {
      const value = values[d.id];

      if (value === undefined || value === "") {
        alert(`Value required for: ${d.question}`);
        return false;
      }

      if (d.allowed_values?.range) {
        const [min, max] = d.allowed_values.range;
        if (value < min || value > max) {
          alert(`${d.question} must be between ${min} and ${max}`);
          return false;
        }
      }

      if (d.decision_code === "INTEREST_DELAYED_PAYMENTS" && value > 21) {
        alert("Interest cannot exceed 21%");
        return false;
      }
    }

    return true;
  };

  /* ================= BUILD HOOKS ================= */
  const buildHooks = () => {
    const hooks: Record<string, any> = {};

    decisions.forEach(d => {
      hooks[d.decision_code.toLowerCase()] = values[d.id];
    });

    return hooks;
  };

  // ================= GENERATE =================
  const generateBylaws = async () => {
    if (!society) return;

    if (!validate()) return;

    const isRegistered = !!formData.registration_number;

    const society_data: any = {
      society_name: formData.society_name,
      registered_address: formData.registered_address,
      district: formData.district,
      adoption_date: formData.adoption_date,
    };

    if (isRegistered) {
      society_data.registration_number = formData.registration_number;
      society_data.registration_date = formData.registration_date;
    }

    const payload = {
      society_id: society.id,
      society_data,
      governance_hooks: buildHooks(),
    };

    try {
      const res = await fetch(`${API_BASE}/api/bylaws/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const text = await res.text();

      let data;

      try {
        data = JSON.parse(text);
      } catch {
        console.error("Invalid JSON response:", text);
        alert("Server error while fetching society details");
        return;
      }

      if (!res.ok) throw new Error(data.error || "Generation failed");

      navigate("/bylaws/preview", {
        state: {
          society_id: society.id,
          payload,
        },
      });

    } catch (err: any) {
      console.error(err);
      alert(err.message || "Something went wrong");
    }
  };
  /* ================= INPUT ENGINE ================= */
  const renderInput = (d: Decision) => {
    const av = d.allowed_values;
    const value = values[d.id] ?? "";

    if (av?.options) {
      return (
        <select
          value={value}
          onChange={e => updateValue(d.id, e.target.value)}
          style={input}
        >
          {av.options.map((opt: string) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      );
    }

    if (av?.range) {
      return (
        <input
          type="number"
          min={av.range[0]}
          max={av.range[1]}
          value={value}
          onChange={e => updateValue(d.id, Number(e.target.value))}
          style={input}
        />
      );
    }

    if (av?.type === "percent") {
      return (
        <div style={{ display: "flex", gap: 6 }}>
          <input
            type="number"
            value={value}
            onChange={e => updateValue(d.id, Number(e.target.value))}
            style={input}
          />
          <span>%</span>
        </div>
      );
    }

    if (av?.type === "currency") {
      return (
        <div style={{ display: "flex", gap: 6 }}>
          ₹
          <input
            type="number"
            value={value}
            onChange={e => updateValue(d.id, Number(e.target.value))}
            style={input}
          />
        </div>
      );
    }

    return (
      <input
        value={value}
        onChange={e => updateValue(d.id, e.target.value)}
        style={input}
      />
    );
  };

  const grouped = decisions.reduce((acc: any, d) => {
    if (!acc[d.category]) acc[d.category] = [];
    acc[d.category].push(d);
    return acc;
  }, {});

  if (loading || detailsLoading) {
    return (
      <AppShell>
        <div style={{ padding: 24 }}>Loading By-laws Engine...</div>
      </AppShell>
    );
  }

  const isRegistered = !!formData.registration_number;

  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>By-laws Configuration</h2>

        {/* ===== SECTION 1 ===== */}
        <div style={card}>
          <h3 style={sectionTitle}>1. Society Legal Identity</h3>

          <label style={label}>Society Name</label>
          <input style={input} value={formData.society_name} onChange={(e) => updateField("society_name", e.target.value)} />

          <label style={label}>
            {isRegistered
              ? "Registered Address"
              : "Proposed / Provisional Address"}
          </label>
          <input style={input} value={formData.registered_address} onChange={(e) => updateField("registered_address", e.target.value)} />

          <label style={label}>District</label>
          <input style={input} value={formData.district} onChange={(e) => updateField("district", e.target.value)} />

          <label style={label}>State</label>
          <input style={input} value={formData.state_code} onChange={(e) => updateField("state_code", e.target.value)} />

          {isRegistered && (
            <>
              <label style={label}>Registration Number</label>
              <input
                style={input}
                value={formData.registration_number}
                onChange={(e) =>
                  updateField("registration_number", e.target.value)
                }
              />
            </>
          )}

          {isRegistered && (
            <>
              <label style={label}>Registration Date</label>
              <input
                type="date"
                style={input}
                value={formData.registration_date || ""}
                disabled
              />
            </>
          )}
        </div>

        {!isRegistered && (
          <div style={warningBox}>
            Your society appears to be undergoing registration - use our registration services to get it registered.
          </div>
        )}

        {isRegistered && (
          <div style={card}>
            <h3 style={sectionTitle}>By-law Adoption</h3>

            <label style={label}>
              Adoption Date <span style={required}>*</span>
            </label>

            <input
              type="date"
              style={input}
              value={formData.adoption_date || ""}
              onChange={(e) => updateField("adoption_date", e.target.value)}
            />
          </div>
        )}

        {/* ===== DECISIONS ===== */}
        {Object.keys(grouped).map(category => (
          <div key={category} style={{ marginTop: 30 }}>
            <h3 style={sectionTitle}>{category}</h3>

            {grouped[category].map((d: Decision) => (
              <div key={d.id} style={card}>
                <div style={question}>{d.question}</div>
                <div style={description}>{d.description}</div>
                <div style={legal}>Legal reference: {d.legal_reference}</div>
                {renderInput(d)}
              </div>
            ))}
          </div>
        ))}

        <button
          style={primaryBtn}
          onClick={() => {
            if (!validate()) return;

            navigate("/bylaws/preview", {
              state: {
                society_id: society.id,
                formData,
                governance_hooks: buildHooks(),
              },
            });
          }}
        >
          Proceed to Next Step
        </button>
      </div>
    </AppShell>
  );
}

/* ===== STYLES ===== */

const container: CSSProperties = {
  padding: 24,
  maxWidth: 900,
  margin: "0 auto",
};

const title: CSSProperties = {
  fontSize: 24,
  marginBottom: 24,
  fontWeight: 600,
  color: "#111827",
};

const sectionTitle: CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  marginBottom: 14,
  color: "#1f2937",
};

const card: CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 14,
  padding: 20,
  marginTop: 18,
  backgroundColor: "#ffffff",
  boxShadow: "0 4px 12px rgba(0,0,0,0.04)",
};

const question: CSSProperties = {
  fontSize: 15,
  fontWeight: 600,
  color: "#111827",
};

const description: CSSProperties = {
  fontSize: 13,
  marginTop: 6,
  color: "#374151",
  lineHeight: "1.5",
};

const legal: CSSProperties = {
  fontSize: 12,
  color: "#6b7280",
  marginTop: 6,
};

const label: CSSProperties = {
  fontSize: 12,
  fontWeight: 500,
  marginTop: 14,
  marginBottom: 6,
  display: "block",
  color: "#374151",
};

const input: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid #e5e7eb",
  backgroundColor: "#f9fafb",
  fontSize: 14,
  outline: "none",
  boxSizing: "border-box",
};

const field: CSSProperties = {
  padding: 12,
  marginTop: 8,
  borderRadius: 10,
  backgroundColor: "#fff7ed",
  border: "1px solid #fed7aa",
  fontSize: 13,
};

const primaryBtn: CSSProperties = {
  marginTop: 36,
  padding: "14px 20px",
  backgroundColor: "#f97316",
  color: "#fff",
  border: "none",
  borderRadius: 10,
  fontWeight: 600,
  fontSize: 15,
  cursor: "pointer",
};

const warningBox: CSSProperties = {
  marginTop: 18,
  padding: 16,
  backgroundColor: "#fff7ed",
  border: "1px solid #fed7aa",
  borderRadius: 12,
  color: "#9a3412",
};

const required: CSSProperties = {
  color: "#f97316",
  marginLeft: 4,
};