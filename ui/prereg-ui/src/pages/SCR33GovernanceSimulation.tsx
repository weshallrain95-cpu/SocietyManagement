import React, {
  useEffect,
  useState,
} from "react";

import AppShell from "../components/layout/AppShell";

import {
  useNavigate,
} from "react-router-dom";


/* =====================================================
   TYPES
===================================================== */

type MaintenanceHead = {

  code: string;

  name: string;

  basis: string;

  rate: number | string;

  is_active: boolean;

  applicability?: string;

  editable_basis?: boolean;

  editable_rate?: boolean;

  custom?: boolean;

  category?: string;

  children?: any[];

};

type PreviewBreakdown = {

  code: string;

  name: string;

  amount: string;
};

type SampleFlat = {

  flat_id: number;

  flat_number: string;

  wing: string;

  total: string;

  breakdown: PreviewBreakdown[];
};

type PreviewPayload = {

  society_total: string;

  average_bill: string;

  highest_bill: string;

  lowest_bill: string;

  headwise_summary: any[];

  sample_flats: SampleFlat[];
};

type RuntimeOverrides = {

  edited_heads: any[];

  disabled_heads: string[];

  new_heads: any[];
};


/* =====================================================
   COMPONENT
===================================================== */

export default function SCR33GovernanceSimulation() {

  const societyId =
    localStorage.getItem(
      "society_id"
    );
  const navigate =
    useNavigate();
  const [hydrating, setHydrating] =
    useState(true);

  const [simulating, setSimulating] =
    useState(false);

  const [effectiveHeads, setEffectiveHeads] =
    useState<MaintenanceHead[]>([]);

  const [preview, setPreview] =
    useState<PreviewPayload | null>(
      null
    );

  const [
    runtimeOverrides,

    setRuntimeOverrides,
  ] = useState<RuntimeOverrides>({

    edited_heads: [],

    disabled_heads: [],

    new_heads: [],
  });

  const [
    expandedSections,

    setExpandedSections,
    ] = useState<any>({

    CORE: true,

    OPTIONAL: false,

    CUSTOM: false,
    });

  /* =====================================================
     HYDRATE SCR33
  ===================================================== */

  useEffect(() => {

    hydrateSCR33();

  }, []);

  const hydrateSCR33 =
    async (
      overrides: RuntimeOverrides | null = null
    ) => {

      try {

        if (overrides) {

          setSimulating(true);

        } else {

          setHydrating(true);
        }

        const response =
          await fetch(

            "/api/society/scr33-context/",

            {
              method: "POST",

              headers: {

                "Content-Type":
                  "application/json",
              },

              body: JSON.stringify({

                society_id:
                  societyId,

                runtime_overrides:
                  overrides || {},
              }),
            }
          );

        const data =
          await response.json();

        console.log(
          "SCR33 CONTEXT",
          data
        );
        console.log(
            "NON OCC HYDRATED",
            data?.effective_heads?.find(
                (x: any) =>
                x.code === "NON_OCCUPANCY"
            )
        );

            console.log(
            "NON OCC PREVIEW",
            data?.preview?.headwise_summary?.find(
                (x: any) =>
                x.code === "NON_OCCUPANCY"
            )
        );

        setEffectiveHeads(

          data?.effective_heads || []
        );

        setPreview(

          data?.preview || null
        );

      } catch (e) {

        console.error(e);

      } finally {

        setHydrating(false);

        setSimulating(false);
      }
    };

  /* =====================================================
     LIVE HEAD EDIT
  ===================================================== */

  const updateHead = (

    code: string,

    field: string,

    value: any
  ) => {

    const nextEdited = [

      ...runtimeOverrides.edited_heads
    ];

    const existingIndex =

      nextEdited.findIndex(
        (x: any) =>
          x.code === code
      );

    if (existingIndex >= 0) {

      nextEdited[
        existingIndex
      ] = {

        ...nextEdited[
          existingIndex
        ],

        [field]: value,
      };

    } else {

      nextEdited.push({

        code,

        [field]: value,
      });
    }

    const nextOverrides = {

      ...runtimeOverrides,

      edited_heads: nextEdited,
    };

    setRuntimeOverrides(
      nextOverrides
    );

    hydrateSCR33(
      nextOverrides
    );
  };

    const handleSaveAndContinue =
        async () => {

        try {

        const maintenanceHeads = (

            effectiveHeads.filter(
            (head: any) =>

                head.code !==
                "PARKING_CHARGES"
            )
        );

        const parkingHead = (

            effectiveHeads.find(
            (head: any) =>

                head.code ===
                "PARKING_CHARGES"
            )
        );

        const parkingChildren = (

            parkingHead?.children || []

        ).map((child: any) => ({

            parking_type:

            child.code ===
            "FOUR_WHEELER"

            ? "CAR"

            : child.code ===
                "TWO_WHEELER"

            ? "BIKE"

            : child.code,

            rate: child.rate,

            is_active:
            child.is_active,
        }));

        const response =
            await fetch(

            "/api/society/scr33-save/",

            {

            method: "POST",

            headers: {

                "Content-Type":
                "application/json",
            },

            body: JSON.stringify({

                society_id:
                societyId,

                maintenance_heads:
                maintenanceHeads,

                parking_children:
                parkingChildren,
            }),
            }
        );

        const data =
            await response.json();

        if (
            data.status !==
            "success"
        ) {

            alert(
            "SCR33 save failed"
            );

            return;
        }

        navigate(
            `/scr34/${societyId}`
        );

        } catch (e) {

        console.error(e);

        alert(
            "SCR33 save failed"
        );
        }
    };
  const groupedHeads = {

    CORE: effectiveHeads.filter(
        (h: any) =>
        h.category === "CORE"
    ),

    OPTIONAL: effectiveHeads.filter(
        (h: any) =>
        h.category !== "CORE"
        &&
        !h.custom
    ),

    CUSTOM: effectiveHeads.filter(
        (h: any) =>
        h.custom
    ),
    };

    const sectionTitles: any = {

    CORE:
        "Core Operational Heads",

    OPTIONAL:
        "Additional Operational Heads",

    CUSTOM:
        "Society-Specific Heads",
    };

    const toggleSection = (
    key: string
    ) => {

    setExpandedSections(
        (prev: any) => ({

        ...prev,

        [key]:
            !prev[key],
        })
    );
    };
  /* =====================================================
     LOADING
  ===================================================== */

  if (hydrating) {

  return (

    <AppShell>

      <div style={styles.loading}>

        Hydrating Financial Simulation...

      </div>

    </AppShell>
  );
}

  return (

    <AppShell>

        {/* =========================================
            HEADER
        ========================================= */}

        <div style={styles.headerRow}>

            <div>

            <div style={styles.title}>

                Maintenance Billing Simulation

            </div>

            <div style={styles.subtitle}>

                Finalize billing heads and
                review live financial impact
                before activating monthly billing.

            </div>

            </div>

            <div style={styles.liveBadge}>

            {simulating
                ? "Simulating..."
                : "Live Simulation"}

            </div>

        </div>
        
        <div style={styles.metricsStrip}>

            <div style={styles.metricInline}>

                <div style={styles.metricInlineLabel}>
                Society Collection
                </div>

                <div style={styles.metricInlineValue}>

                ₹ {preview?.society_total}

                </div>

            </div>

            <div style={styles.metricInline}>

                <div style={styles.metricInlineLabel}>
                Average Bill
                </div>

                <div style={styles.metricInlineValue}>

                ₹ {preview?.average_bill}

                </div>

            </div>

            <div style={styles.metricInline}>

                <div style={styles.metricInlineLabel}>
                Highest Bill
                </div>

                <div style={styles.metricInlineValue}>

                ₹ {preview?.highest_bill}

                </div>

            </div>

            <div style={styles.metricInline}>

                <div style={styles.metricInlineLabel}>
                Lowest Bill
                </div>

                <div style={styles.metricInlineValue}>

                ₹ {preview?.lowest_bill}

                </div>

            </div>

            </div>
        {/* =========================================
            MAIN GRID
        ========================================= */}

        <div style={styles.mainGrid}>

            {/* =====================================
                LEFT PANEL
            ===================================== */}

            <div style={styles.leftPanel}>

            <div style={styles.sectionTitle}>

                Maintenance Decisions

            </div>

            <div style={styles.tableWrapper}>

                <table style={styles.table}>

                <thead>

                    <tr>

                    <th style={styles.thHead}>
                        Head
                        </th>

                        <th style={styles.th}>
                        Basis
                        </th>

                        <th style={styles.th}>
                        Rate
                        </th>

                        <th style={styles.th}>
                        Flat Impact
                        </th>

                        <th style={styles.th}>
                        Society Total
                        </th>

                        <th style={styles.th}>
                        Active
                        </th>

                    </tr>

                </thead>

                <tbody>

                {Object.entries(
                    groupedHeads
                ).map(

                    ([section, heads]: any) => (

                    <React.Fragment
                    key={section}
                    >

                    <tr>

                        <td
                        colSpan={6}
                        style={styles.categoryRow}
                        onClick={() =>
                            toggleSection(section)
                        }
                        >

                        <div
                            style={styles.categoryTitle}
                        >

                            <span>

                            {
                                sectionTitles[
                                section
                                ]
                            }

                            </span>

                            <span>

                            {
                                expandedSections[
                                section
                                ]
                                ? "−"
                                : "+"
                            }

                            </span>

                        </div>

                        

                        </td>

                    </tr>

                    {
                        expandedSections[
                        section
                        ]
                        &&

                        heads.map(
                        (head: any) => {

                            
                            const financial =
                            preview
                            ?.headwise_summary
                            ?.find(
                                (x: any) =>
                                x.code
                                === head.code
                            );
                        
                            return (

                                <React.Fragment
                                key={head.code}
                                >
                            
                            <tr
                            key={head.code}
                            style={styles.row}
                            >

                            <td
                                style={styles.headName}
                            >

                                {head.name}

                            </td>

                            <td style={styles.td}>

                                <select
                                value={head.basis}
                                onChange={(e) =>
                                    updateHead(
                                    head.code,
                                    "basis",
                                    e.target.value
                                    )
                                }
                                style={styles.select}
                                >

                                <option value="EQUAL">
                                    Equal
                                </option>

                                <option value="AREA">
                                    Per Sq.ft
                                </option>

                                <option value="PER_SLOT">
                                    Per Slot
                                </option>

                                <option value="PER_INLET">
                                    Per Inlet
                                </option>

                                <option value="PERCENT_MAINT">
                                    % of Maintenance
                                </option>

                                </select>

                            </td>

                            <td style={styles.td}>

                                <input
                                type="number"
                                value={head.rate}
                                onChange={(e) =>
                                    updateHead(
                                    head.code,
                                    "rate",
                                    e.target.value
                                    )
                                }
                                style={styles.rateInput}
                                />

                            </td>

                            <td style={styles.td}>

                                {
                                head.code ===
                                "PARKING_CHARGES"

                                ? "—"

                                : `₹ ${
                                    financial
                                    ?.per_flat || "0"
                                }`
                                }

                            </td>

                            <td style={styles.td}>

                                {
                                head.code ===
                                "PARKING_CHARGES"

                                ? "—"

                                : `₹ ${
                                    financial
                                    ?.total || "0"
                                }`
                                }

                            </td>

                            <td style={styles.td}>

                                <input
                                type="checkbox"
                                checked={
                                    head.is_active
                                }
                                onChange={(e) =>
                                    updateHead(
                                    head.code,
                                    "is_active",
                                    e.target.checked
                                    )
                                }
                                />

                            </td>

                            </tr>

{
  head.code ===
    "PARKING_CHARGES"

  &&

  head.children?.length > 0

  &&

  head.children.map(
    (child: any) => (

      <tr
        key={child.code}
        style={styles.childRow}
      >

        <td
            style={
                styles.childHeadName
            }
        >

            ↳ {child.label}

        </td>

        <td>

          {child.basis}

        </td>

        <td style={styles.td}>

            <input
                type="number"
                value={child.rate}
                onChange={(e) => {

                    const nextHeads = [
                        ...effectiveHeads
                    ];

                    const parkingHead =
                        nextHeads.find(
                            (h: any) =>
                                h.code ===
                                "PARKING_CHARGES"
                        );

                    if (!parkingHead) {
                        return;
                    }

                    parkingHead.children =
                        (
                            parkingHead.children
                            || []
                        ).map(
                            (c: any) =>

                                c.code ===
                                child.code

                                ? {
                                    ...c,
                                    rate:
                                        e.target.value,
                                }

                                : c
                        );

                    setEffectiveHeads(
                        nextHeads
                    );
                }}
                style={
                    styles.childRateInput
                }
            />

        </td>

        <td style={styles.td}>

            ₹ {
                Number(
                    child.rate || 0
                )
            }

        </td>

            <td style={styles.td}>

                ₹ {
                    (
                    Number(child.rate)
                    *
                    Number(
                        child.count || 0
                    )
                    )
                }

            </td>

            <td style={styles.td}>

                <input
                    type="checkbox"
                    checked={
                        child.is_active
                    }
                    onChange={(e) => {

                        const nextHeads = [
                            ...effectiveHeads
                        ];

                        const parkingHead =
                            nextHeads.find(
                                (h: any) =>
                                    h.code ===
                                    "PARKING_CHARGES"
                            );

                        if (!parkingHead) {
                            return;
                        }

                        parkingHead.children =
                            (parkingHead.children || []).map(
                                (c: any) =>

                                    c.code ===
                                    child.code

                                    ? {
                                        ...c,

                                        is_active:
                                            e.target.checked,

                                        rate:
                                            e.target.checked

                                            ? c.rate

                                            : 0,
                                    }

                                    : c
                            );

                        setEffectiveHeads(
                            nextHeads
                        );
                    }}
                />

            </td>

      </tr>
    )
  )
}

</React.Fragment>

);
                        }
                        )
                    }

                    </React.Fragment>
                ))}

                </tbody>

                </table>

            </div>

            </div>

            </div>
        
        <button

            style={styles.saveButton}

            onClick={
                handleSaveAndContinue
            }
            >

            SAVE & CONTINUE

            </button>

    </AppShell>
    );
}


/* =====================================================
   STYLES
===================================================== */

const styles: any = {

  container: {

    padding: "24px 28px",

    background: "#f4f6f8",

    minHeight: "100vh",
  },

  loading: {

    padding: 40,

    fontSize: 16,

    color: "#666",
  },

  headerRow: {

    display: "flex",

    justifyContent: "space-between",

    alignItems: "flex-start",

    marginBottom: 24,
  },

  title: {

    fontSize: 28,

    fontWeight: 700,

    color: "#1f2937",

    marginBottom: 6,
  },

  subtitle: {

    fontSize: 13,

    color: "#6b7280",

    lineHeight: 1.5,
  },

  liveBadge: {

    background:
        "rgba(255,247,237,0.75)",

    backdropFilter:
        "blur(14px)",

    WebkitBackdropFilter:
        "blur(14px)",

    color: "#ea580c",

    border:
        "1px solid rgba(251,191,36,0.35)",

    boxShadow:
        "0 4px 12px rgba(234,88,12,0.08)",

    padding: "8px 14px",

    borderRadius: 999,

    fontSize: 12,

    fontWeight: 600,
    },

  mainGrid: {

    width: "100%",
  },
  
  leftPanel: {

    width: "100%",

    background:
        "rgba(255,255,255,0.82)",

    backdropFilter:
        "blur(20px)",

    WebkitBackdropFilter:
        "blur(20px)",

    border:
        "1px solid rgba(255,255,255,0.55)",

    boxShadow:
        "0 12px 32px rgba(15,23,42,0.08)",

    borderRadius: 16,

    overflow: "hidden",
  },

  rightPanel: {

    position: "sticky",

    top: 20,

    display: "flex",

    flexDirection: "column",

    gap: 18,
  },

  sectionTitle: {

    fontSize: 15,

    fontWeight: 700,

    color: "#374151",

    padding: "18px 20px",

    borderBottom: "1px solid #f1f5f9",

    background: "#fafafa",
  },

  sectionSubTitle: {

    fontSize: 13,

    fontWeight: 700,

    marginBottom: 16,

    color: "#374151",
  },

  tableWrapper: {

    overflowX: "auto",
  },

  table: {

    width: "100%",

    borderCollapse: "collapse",
  },

  thHead: {

    textAlign: "left",

    fontSize: 11,

    fontWeight: 700,

    color: "#6b7280",

    padding: "14px 18px",

    borderBottom: "1px solid #f3f4f6",

    background: "#fafafa",

    width: "42%",
  },

  th: {

    textAlign: "left",

    fontSize: 11,

    fontWeight: 700,

    color: "#6b7280",

    padding: "14px 12px",

    borderBottom: "1px solid #f3f4f6",

    background: "#fafafa",

    minWidth: 120,
  },

  row: {

    borderBottom: "1px solid #f3f4f6",
  },

childRow: {

  background: "#fafafa",

  borderBottom:
    "1px solid #f3f4f6",
},

childHeadName: {

  paddingLeft: 42,

  fontSize: 12,

  color: "#6b7280",

  fontWeight: 500,
},

childRateInput: {

  width: 90,

  height: 30,

  borderRadius: 6,

  border:
    "1px solid #d1d5db",

  paddingLeft: 10,

  fontSize: 12,

  outline: "none",

  background: "#ffffff",
},

  headName: {

    fontSize: 13,

    fontWeight: 500,

    color: "#111827",

    padding: "12px 18px",
  },

  td: {

    padding: "10px 12px",
  },

  select: {

    width: 120,

    height: 40,

    borderRadius: 8,

    border: "1px solid #d1d5db",

    fontSize: 13,

    lineHeight: "40px",

    background: "#fff",

    paddingLeft: 10,

    color: "#374151",

    outline: "none",
},

  rateInput: {

    width: 100,

    height: 34,

    borderRadius: 8,

    border: "1px solid #d1d5db",

    paddingLeft: 12,

    fontSize: 12,

    color: "#111827",

    outline: "none",
  },

  metricsGrid: {

    display: "grid",

    gridTemplateColumns: "1fr 1fr",

    gap: 14,
  },

  metricCard: {

    background: "#ffffff",

    border: "1px solid #e5e7eb",

    borderRadius: 14,

    padding: 18,
  },

  metricLabel: {

    fontSize: 11,

    color: "#6b7280",

    marginBottom: 10,

    textTransform: "uppercase",

    letterSpacing: 0.5,
  },

  metricValue: {

    fontSize: 24,

    fontWeight: 700,

    color: "#111827",

    lineHeight: 1.1,
  },

  wingCard: {

    background: "#ffffff",

    border: "1px solid #e5e7eb",

    borderRadius: 14,

    padding: 18,
  },

  metricsStrip: {

  display: "grid",

  gridTemplateColumns:
    "repeat(4, 1fr)",

  gap: 12,

  marginBottom: 18,
},

metricInline: {

  background:
    "rgba(255,255,255,0.72)",

  backdropFilter:
    "blur(18px)",

  WebkitBackdropFilter:
    "blur(18px)",

  border:
    "1px solid rgba(255,255,255,0.45)",

  boxShadow:
    "0 8px 24px rgba(15,23,42,0.08)",

  borderRadius: 14,

  padding: "14px 18px",
},

metricInlineLabel: {

  fontSize: 10,

  fontWeight: 700,

  letterSpacing: 0.6,

  textTransform: "uppercase",

  color: "#9ca3af",

  marginBottom: 8,
},

metricInlineValue: {

  fontSize: 22,

  fontWeight: 700,

  color: "#111827",
},

categoryRow: {

  background: "#f8fafc",

  borderTop: "1px solid #e5e7eb",
},

categoryTitle: {

  display: "flex",

  justifyContent: "space-between",

  alignItems: "center",

  padding: "14px 18px",

  fontSize: 11,

  fontWeight: 800,

  letterSpacing: 0.6,

  textTransform: "uppercase",

  color: "#6b7280",
},

saveButton: {

  marginTop: 22,

  width: "100%",

  height: 52,

  border: "none",

  borderRadius: 14,

  background: "#ea580c",

  color: "#fff",

  fontWeight: 700,

  fontSize: 14,

  cursor: "pointer",

  transition: "0.2s",
},
}
