import AppShell from "../components/layout/AppShell";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const MIN_PROMOTERS = 10;

export default function SCR21FormA() {
  const navigate = useNavigate();
  const societyId = localStorage.getItem("society_id");
  if (!societyId) {
    return <div>Invalid session</div>;
  }

  const [form, setForm] = useState({
    chief_promoter_name: "",
    chief_promoter_address: "",
    chief_promoter_phone: "",

    registrar_district: "",
    society_address: "",
    society_type: "",
    area_of_operation: "",

    authorized_share_capital: "",
    share_value: "",

    bank_name: "",
    bank_branch: "",

    first_meeting_date: "",

    declaration_place: "",
    declaration_date: "",

    registration_office: "",
  });
  
  const today = new Date().toISOString().split("T")[0];
  const [members, setMembers] = useState<any[]>([]);
  const usedFlatIds = members
    .map((m) => m.flat_id)
    .filter((id) => id);
  const [promoterCount, setPromoterCount] = useState(10);
  const [showMembers, setShowMembers] = useState(false);
  const [loading, setLoading] = useState(false);
  const [flats, setFlats] = useState<any[]>([]);
  const [ownersMap, setOwnersMap] = useState<{ [key: number]: any[] }>({});
  
  const loadOwners = (flatId: number) => {
    if (ownersMap[flatId]) return; // already loaded

    fetch(`/api/society/ownership/?flat_id=${flatId}`)
        .then((res) => res.json())
        .then((data) => {
        setOwnersMap((prev) => ({
            ...prev,
            [flatId]: Array.isArray(data) ? data : [],
        }));
        })
        .catch(() => {
        alert("Failed to load owners");
        });
    };
  
  
  /* ================= PREFILL ================= */
  useEffect(() => {
    if (!societyId) return;

    fetch(`/api/society/details/?society_id=${societyId}`)
      .then((res) => res.json())
      .then((data) => {
        // ✅ MOVE HERE
        const addressParts = (data.address || "").split(",");
        const city = addressParts.length >= 2
        ? addressParts[addressParts.length - 2].trim()
        : "";
        setForm((p) => ({
          ...p,
          society_address: data.address || "",
          registrar_district: data.district || "",
          authorized_share_capital:
            data.authorized_share_capital || "",
          share_value: data.share_value || "",   // ✅ ADD THIS LINE
          society_type: data.society_type || "Co-operative Housing Society",
          registration_office: data.registrar_office || data.district || "",
          declaration_place: city && data.district && city !== data.district ? `${city}, ${data.district}`: city || data.district || "",
          area_of_operation: data.district ? `${data.district} District` : "",
          declaration_date: today,
        }));
      })
      .catch(() => {});
  }, [societyId]);

  /* ================= LOAD FLATS ================= */
  useEffect(() => {
    if (!societyId) return;

    fetch(`/api/society/flats/?society_id=${societyId}`)
        .then((res) => res.json())
        .then((data) => {
        setFlats(Array.isArray(data) ? data : []);
        })
        .catch(() => {
        alert("Failed to load flats");
        });
  }, [societyId]);
  
  const buildMemberTable = () =>
    members
        .filter((m) => m?.owner_name && m?.flat)
        .map(
        (m, i) =>
            `${i + 1} | ${m.owner_name} | Flat ${m.flat}, ${form.society_address} | __________`
        )
        .join("\n");

  useEffect(() => {
    if (!flats.length) return;

    // Only suggest if field is empty
    if (String(form.authorized_share_capital || "").trim()) return;

    const shareValue = Number(form.share_value);
    if (!shareValue || isNaN(shareValue)) return;


    const sharesPerMember = 10;

    const currentCapital =
        flats.length * sharesPerMember * shareValue;

    const suggested = currentCapital * 10;

    setForm((p) => ({
        ...p,
        authorized_share_capital: String(suggested),
    }));
  }, [flats, form.share_value]);
  
        /* ================= VALIDATION ================= */
  
  const isValid = () => {
    for (const key in form) {
        if (!form[key as keyof typeof form]) return false;
    }

    if (members.length !== promoterCount) return false;

    for (let i = 0; i < promoterCount; i++) {
        if (!members[i]?.owner_name || !members[i]?.flat) return false;
    }

    return true;
    };

  /* ================= GENERATE ================= */
  const handleGenerate = async () => {
    if (!showMembers) {
        alert("Please confirm promoter count first");
        return;
    }
    if (!isValid()) {
      alert("Please fill all fields and complete all promoter entries");
      return;
    }

    try {
        setLoading(true);

        const res = await fetch("/api/society/update/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
            society_id: societyId,
            authorized_share_capital: form.authorized_share_capital,
            }),
        });

        if (!res.ok) {
            alert("Failed to save authorized share capital");
            setLoading(false);   // ✅ move here
            return;
        }

        await fetch("/api/society/documents/generate/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
            society_id: societyId,
            artifact_code: "FORM_A_MH",
            data: {
                ...form,
                promoter_member_table: buildMemberTable(),
                total_members: members.length,
                number_of_promoters: members.length,
            },
            }),
        });

        alert("Form A generated");
        navigate("/registration-tracker");

    } catch (e) {
        console.error(e);
        alert("Something went wrong");
        setLoading(false);
      }
    };
try {
  return (
    <AppShell>
      <div style={container}>
        <h2 style={title}>Form A</h2>

        {/* SOCIETY */}
        <Section title="Society Details">
          <Field label="Registrar District" value={form.registrar_district} onChange={(v) => setForm((p) => ({ ...p, registrar_district: v }))} desc="District under which society is registered" />
          <Field label="Society Address" value={form.society_address} onChange={(v) => setForm((p) => ({ ...p, society_address: v }))} desc="Registered address of society" />
          <Field label="Society Type" value={form.society_type} onChange={(v) => setForm((p) => ({ ...p, society_type: v }))} desc="Type of cooperative society" />
          <Field label="City / Area of Operation" value={form.area_of_operation} onChange={(v) => setForm((p) => ({ ...p, area_of_operation: v }))} desc="Enter city where the society operates (e.g., Thane, Mumbai)" />
        </Section>

         
        <Section title="Promoter Members">
            <Field
                label="Number of Promoter Members"
                value={String(promoterCount)}
                onChange={(v) => {
                    const num = Math.max(MIN_PROMOTERS, Number(v) || MIN_PROMOTERS);
                    setPromoterCount(num);
                    setShowMembers(false);
                }}
                desc="Minimum 10 promoters required"
            />

            <button
                style={button}
                onClick={() => setShowMembers(true)}
            >
                Confirm Promoters
            </button>
        
        </Section>
        
        {/* MEMBERS */}
        
        {showMembers && (
        <Section title="Promoter Member Details">
            {Array.from({ length: promoterCount }).map((_, i) => {
            const member = members[i] ?? {};
            const owners =
                member && member.flat_id && ownersMap[member.flat_id]
                    ? ownersMap[member.flat_id]
                    : [];

            return (
                <div key={i} style={{ marginBottom: "16px" }}>
                <h4>Promoter {i + 1}</h4>

                {/* Flat Selection */}
                <select
                    style={input}
                    value={member.flat_id || ""}
                    onChange={(e) => {
                    const flatId = Number(e.target.value);

                    const updated = [...members];
                    while (updated.length < promoterCount) updated.push({});

                    const flat = flats.find((f) => f.id === flatId);

                    updated[i] = {
                        ...updated[i],
                        flat_id: flatId,
                        flat: flat?.flat_number || "",
                        owner_name: "", // reset owner
                    };

                    setMembers(updated);
                    loadOwners(flatId);
                    }}
                >
                    <option value="">Select Flat</option>
                    {flats
                        .filter((f) => {
                            // Allow current row's selected flat
                            if (f.id === member.flat_id) return true;

                            // Hide flats already used in other rows
                            return !usedFlatIds.includes(f.id);
                        })
                        .map((f) => (
                            <option key={f.id} value={f.id}>
                            Flat {f.flat_number}
                        </option>
                    ))}
                </select>

                {/* Owner Selection */}
                <select
                    style={input}
                    value={member.owner_name || ""}
                    onChange={(e) => {
                    const name = e.target.value;

                    const updated = [...members];
                    while (updated.length < promoterCount) updated.push({});

                    updated[i] = {
                        ...updated[i],
                        owner_name: name,
                    };

                    setMembers(updated);
                    }}
                    disabled={!member.flat_id}
                >
                    <option value="">Select Owner</option>
                    {Array.isArray(owners) && owners.map((o, idx) => (
                    <option key={idx} value={o.name || o.full_name}>
                        {o.name || o.full_name}
                    </option>
                    ))}
                </select>

                {/* READ ONLY FIELDS (NO USER INPUT) */}
                <div style={{ marginTop: "8px", fontSize: "14px" }}>
                    <div><b>Name:</b> {member.owner_name || "-"}</div>
                    <div><b>Flat:</b> {member.flat || "-"}</div>
                </div>
                </div>
            );
            })}
        </Section>
        )}
        
        {/* Chief Promoter Selection */}
        <Section title="Chief Promoter">
            <select
                style={input}
                value={form.chief_promoter_name}
                onChange={(e) => {
                    const name = e.target.value;

                    const selectedMember = members.find(
                        (m) => m.owner_name === name
                    );

                    if (!selectedMember) return;

                    const owners = ownersMap[selectedMember.flat_id] || [];

                    const owner = owners.find(
                        (o) => (o.name || o.full_name) === name
                    );

                    setForm((p) => ({
                        ...p,
                        chief_promoter_name: name,
                        chief_promoter_address: p.society_address,
                        chief_promoter_phone: owner?.phone || "",
                }));
            }}
            >
            <option value="">Select Chief Promoter</option>

            {members
            .filter((m) => m?.owner_name)
            .map((m, idx) => (
                <option key={idx} value={m.owner_name}>
                {m.owner_name} (Flat {m.flat})
                </option>
            ))}
        </select>

        {/* ✅ READ-ONLY DISPLAY */}
        <div style={{ marginTop: "12px", fontSize: "14px" }}>
            <div>
            <b>Name:</b> {form.chief_promoter_name || "-"}
            </div>
            <div>
            <b>Address:</b> {form.chief_promoter_address || "-"}
            </div>
            <div>
            <b>Phone:</b> {form.chief_promoter_phone || "-"}
            </div>
        </div>
        </Section>

        {/* FINANCIAL */}
        <Section title="Financial">
          <Field label="Share Value" value={form.share_value} onChange={() => {}}/>
          <Field label="Authorized Share Capital" value={form.authorized_share_capital} onChange={(v) => setForm((p) => ({ ...p, authorized_share_capital: v }))} />
        </Section>

        {/* BANK */}
        <Section title="Bank">
          <Field label="Bank Name" value={form.bank_name} onChange={(v) => setForm((p) => ({ ...p, bank_name: v }))} />
          <Field label="Bank Branch" value={form.bank_branch} onChange={(v) => setForm((p) => ({ ...p, bank_branch: v }))} />
        </Section>

        {/* MEETING */}
        <Section title="Meeting">
          <div> <label>First Meeting Date</label> <input type="date" value={form.first_meeting_date} onChange={(e) => setForm((p) => ({ ...p, first_meeting_date: e.target.value }))}/></div>
        </Section>

        {/* DECLARATION */}
        <Section title="Declaration">
          <Field label="Place" value={form.declaration_place} onChange={(v) => setForm((p) => ({ ...p, declaration_place: v }))} />
          <div> <label>Date</label> <input type="date" value={form.declaration_date} onChange={(e) => setForm((p) => ({ ...p, declaration_date: e.target.value }))}/>
        </div>
        </Section>

        <Field label="Registration Office" value={form.registration_office} onChange={(v) => setForm((p) => ({ ...p, registration_office: v }))} />

        <button style={button} onClick={handleGenerate}>
          {loading ? "Generating..." : "Generate Form A"}
        </button>
      </div>
    </AppShell>
  );
    
} catch (e) {
  console.error("🔥 SCR21 CRASH:", e);
  return <div>Crash detected — check console</div>;
}
}

/* ---------- COMPONENTS ---------- */

function Section({ title, children }: any) {
  return (
    <div style={{ marginTop: 20 }}>
      <h3>{title}</h3>
      {children}
    </div>
  );
}

type FieldProps = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  desc?: string;
};

function Field({ label, value, onChange, desc }: FieldProps) {
  return (
    <div style={{ marginBottom: "12px" }}>
      <div>{label} *</div>

      {desc && (
        <div style={{ fontSize: "12px", color: "#666" }}>
          {desc}
        </div>
      )}

      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={input}
      />
    </div>
  );
}

/* ---------- STYLES ---------- */

const container = { padding: 24 };
const title = { fontSize: 24 };
const input = { width: "100%", padding: 10, marginTop: 4 };
const button: React.CSSProperties = {
  marginTop: "20px",
  padding: "12px",
  width: "100%",
};