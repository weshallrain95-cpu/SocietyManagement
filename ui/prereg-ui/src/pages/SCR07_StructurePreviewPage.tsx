import AppShell from "../components/layout/AppShell";
import { useLocation, useNavigate } from "react-router-dom";
import { useSociety } from "../context/SocietyContext";

/* ================= MAIN ================= */

export default function StructurePreviewPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { society } = useSociety();

  const mode = location.state?.mode || "STANDARD";
  const wings = location.state?.wings || [];
  const floors = location.state?.floors || 0;

  const flatConfig = location.state?.flatConfig || [];
  const groups = location.state?.groups || [];

  const structureType = location.state?.structureType || "SINGLE";

  /* ================= HELPERS ================= */

  const calculateStandardFlats = () => {
    const flatsPerFloor = flatConfig.reduce(
      (sum: number, c: any) => sum + c.count,
      0
    );
    return flatsPerFloor * floors * (wings.length || 1);
  };

  const calculateGroupFlats = () => {
    let total = 0;

    groups.forEach((g: any) => {
      total += (g.flats?.length || 0) * g.floors.length;
    });

    return total * (wings.length || 1);
  };

  const totalFlats =
    mode === "GROUP"
      ? calculateGroupFlats()
      : calculateStandardFlats();

  const resolvedWings =
    wings.length > 0 ? wings : [{ display_name: "Main", code: "A" }];

  const generateFlatNumber = (wing: string, floor: number, index: number) => {
    const base = `${floor}${String(index).padStart(2, "0")}`;

    return structureType === "MULTI"
      ? `${wing}-${base}`
      : base;
  };

  const expandStandardFloor = () => {
    let result: any[] = [];
    let index = 1;

    flatConfig.forEach((c: any) => {
      for (let i = 0; i < c.count; i++) {
        result.push({
          index,
          type: c.type,
          area: c.area,
        });
        index++;
      }
    });

    return result;
  };

  /* ================= CTA ================= */

  const handleProceed = () => {
    navigate("/excel-upload-placeholder", {
      state: {
        ...location.state,  // ✅ CRITICAL FIX
      },
    });
  };

  /* ================= RENDER ================= */

  return (
    <AppShell>
      <div style={pageWrapper}>
        <div style={container}>

          {/* HEADER */}
          <div style={header}>
            <h1 style={title}>Society Structure</h1>
            <p style={subtitle}>
              Final structure summary before proceeding
            </p>
          </div>

          <div style={card}>

            {/* ===== SUMMARY ===== */}
            <div style={summaryBox}>
              <div style={summaryItem}>
                <div style={summaryLabel}>Total Wings</div>
                <div style={summaryValue}>{resolvedWings.length}</div>
              </div>

              <div style={summaryItem}>
                <div style={summaryLabel}>Floors / Wing</div>
                <div style={summaryValue}>{floors}</div>
              </div>

              <div style={summaryItem}>
                <div style={summaryLabel}>Total Flats</div>
                <div style={summaryValueHighlight}>{totalFlats}</div>
              </div>
            </div>

            {/* ===== WINGS ===== */}
            <h3 style={label}>Wings</h3>
            <div style={section}>
              {resolvedWings.map((w: any, i: number) => (
                <div key={i} style={row}>
                  <span>{w.display_name}</span>
                  <span style={{ color: "#6b7280" }}>{w.code}</span>
                </div>
              ))}
            </div>

            {/* ===== STRUCTURE PREVIEW (NEW CORE ADDITION) ===== */}
            <h3 style={label}>Detailed Structure Preview</h3>

            {resolvedWings.map((w: any, wi: number) => (
              <div key={wi} style={groupCard}>
                <div style={groupHeader}>
                  Wing {w.code || "A"}
                </div>

                {/* STANDARD */}
                {mode === "STANDARD" &&
                  Array.from({ length: floors }, (_, fi) => {
                    const floorNumber = fi + 1;
                    const layout = expandStandardFloor();

                    return (
                      <div key={fi} style={{ marginBottom: 10 }}>
                        <strong>Floor {floorNumber}</strong>

                        {layout.map((f: any) => (
                          <div key={f.index} style={tableRow}>
                            <span>
                              {generateFlatNumber(
                                w.code || "A",
                                floorNumber,
                                f.index
                              )}
                            </span>
                            <span>{f.type}</span>
                            <span>{f.area} sqft</span>
                          </div>
                        ))}
                      </div>
                    );
                  })}

                {/* GROUP */}
                {mode === "GROUP" &&
                  groups.map((g: any, gi: number) => (
                    <div key={gi}>
                      {g.floors.map((floorNumber: number) => (
                        <div key={floorNumber} style={{ marginBottom: 10 }}>
                          <strong>Floor {floorNumber}</strong>

                          {(g.flats || []).map((f: any, i: number) => (
                            <div key={i} style={tableRow}>
                              <span>
                                {generateFlatNumber(
                                  w.code || "A",
                                  floorNumber,
                                  i + 1
                                )}
                              </span>
                              <span>{f.type}</span>
                              <span>{f.area} sqft</span>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  ))}
              </div>
            ))}

            {/* CTA */}
            <div style={cta}>
              <button style={secondaryBtn} onClick={() => navigate(-1)}>
                Back
              </button>

              <button style={primaryBtn} onClick={handleProceed}>
                Proceed to Excel Setup
              </button>
            </div>

          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* ================= STYLES ================= */
/* UNCHANGED */

const pageWrapper = { padding: 20 };
const container = { maxWidth: 800, margin: "0 auto" };

const header = { marginBottom: 20 };
const title = { fontSize: 28, fontWeight: 600 };
const subtitle = { color: "#6b7280" };

const card = {
  background: "white",
  padding: 25,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
};

const section = { marginBottom: 20 };

const label = {
  marginBottom: 10,
  fontWeight: 600,
  marginTop: 20,
};

const row = {
  display: "flex",
  justifyContent: "space-between",
  padding: "6px 0",
};

const tableRow = {
  display: "flex",
  justifyContent: "space-between",
  padding: "6px 0",
};

const groupCard = {
  border: "1px solid #e5e7eb",
  padding: 12,
  borderRadius: 10,
  marginTop: 10,
};

const groupHeader = {
  fontWeight: 600,
  marginBottom: 8,
};

const summaryBox = {
  display: "flex",
  justifyContent: "space-between",
  background: "#f9fafb",
  padding: 15,
  borderRadius: 10,
  marginBottom: 20,
};

const summaryItem = {
  textAlign: "center" as const,
};

const summaryLabel = {
  fontSize: 12,
  color: "#6b7280",
};

const summaryValue = {
  fontSize: 18,
  fontWeight: 600,
};

const summaryValueHighlight = {
  fontSize: 22,
  fontWeight: 700,
  color: "#f97316",
};

const cta = {
  display: "flex",
  justifyContent: "space-between",
  marginTop: 25,
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
  padding: "12px 18px",
  borderRadius: 8,
  cursor: "pointer",
};