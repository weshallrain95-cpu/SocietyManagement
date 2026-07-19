import { useEffect, useMemo, useState } from "react";
import AppShell from "../components/layout/AppShell";

/* ==========================================================
   TYPES
========================================================== */

type KnowledgeItem = {
    id: string;
    title: string;
    status?: string;
    summary?: string;
    details?: string;
};

type KnowledgePayload = {
    architecture_decisions: KnowledgeItem[];
    architecture_notes: KnowledgeItem[];
    product_principles: KnowledgeItem[];
    future_engines: KnowledgeItem[];
    current_reconstruction: KnowledgeItem[];
};

type SectionKey =
    | "architecture_decisions"
    | "architecture_notes"
    | "product_principles"
    | "future_engines"
    | "current_reconstruction";

/* ==========================================================
   CONSTANTS
========================================================== */

const SECTION_CONFIG = [
    {
        key: "architecture_decisions" as SectionKey,
        short: "AD",
        title: "Architecture Decisions",
        subtitle: "Platform decisions frozen forever",
    },
    {
        key: "architecture_notes" as SectionKey,
        short: "AN",
        title: "Architecture Notes",
        subtitle: "Ideas waiting for implementation",
    },
    {
        key: "product_principles" as SectionKey,
        short: "PP",
        title: "Product Doctrine",
        subtitle: "Core principles of SocietyOS",
    },
    {
        key: "future_engines" as SectionKey,
        short: "FE",
        title: "Future Engines",
        subtitle: "Operating models yet to be built",
    },
    {
        key: "current_reconstruction" as SectionKey,
        short: "CR",
        title: "Current Reconstruction",
        subtitle: "Current engineering milestone",
    },
];

/* ==========================================================
   MAIN COMPONENT
========================================================== */

export default function KnowledgeCenter() {

    const [, setLoading] = useState(true);

    const [knowledge, setKnowledge] =
        useState<KnowledgePayload>({
            architecture_decisions: [],
            architecture_notes: [],
            product_principles: [],
            future_engines: [],
            current_reconstruction: [],
        });

    const [selectedSection, setSelectedSection] =
        useState<SectionKey>("architecture_decisions");

    const [showEditor, setShowEditor] = useState(false);

    const [newNote, setNewNote] = useState({

        category: "architecture_decisions",

        title: "",

        summary: "",

        details: "",

        status: "FROZEN",

        makeCurrentFocus: false,

    });

    useEffect(() => {
        hydrate();
    }, []);

    async function hydrate() {

        try {

            const response = await fetch(
                "/api/society/knowledge-center/"
            );

            const payload =
                await response.json();

            setKnowledge(payload);

        } catch (err) {

            console.error(err);

        } finally {

            setLoading(false);

        }

    }
    
    
    const selectedItems = useMemo(() => {

        return knowledge[selectedSection] || [];

    }, [knowledge, selectedSection]);

    async function saveKnowledgeNote() {

        try {

            const response = await fetch(

                "/api/society/knowledge-center/save/",

                {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json",

                    },

                    body: JSON.stringify(newNote),

                }

            );

            if (!response.ok) {

                throw new Error("Unable to save note.");

            }

            await hydrate();

            setShowEditor(false);

            setNewNote({

                category: selectedSection,

                title: "",

                summary: "",

                details: "",

                status: "FROZEN",

                makeCurrentFocus: false,

            });

        }

        catch (error) {

            console.error(error);

            alert("Unable to save note.");

        }

    }
    
    async function removeFocus(noteId: string) {

        try {

            const response = await fetch(

                "/api/society/knowledge-center/remove-focus/",

                {

                    method: "POST",

                    headers: {

                        "Content-Type": "application/json",

                    },

                    body: JSON.stringify({

                        note_id: noteId,

                    }),

                }

            );

            if (!response.ok) {

                throw new Error(
                    "Unable to remove focus."
                );

            }

            await hydrate();

        }

        catch (error) {

            console.error(error);

            alert(
                "Unable to remove focus."
            );

        }

    }   
    
    return (

        <AppShell>

            <div style={styles.page}>

                {/* ==========================================
                    PAGE HEADER
                ========================================== */}

                <div style={styles.header}>

                    <div>

                        <div style={styles.pageTitle}>
                            SocietyOS Knowledge Center
                        </div>

                        <div style={styles.pageSubtitle}>
                            Institutional Memory of the Platform
                        </div>

                    </div>

                    <div style={styles.newNoteBar}>

                        <button

                            style={styles.newButton}

                            onClick={() => {

                                setNewNote({

                                    category: selectedSection,

                                    title: "",

                                    summary: "",

                                    details: "",

                                    status: "FROZEN",

                                    makeCurrentFocus: false,

                                });

                                setShowEditor(true);

                            }}

                        >

                            + New Knowledge Note

                        </button>

                    </div>
                    
                    {

                        showEditor && (

                            <div style={styles.editorCard}>

                                <div style={styles.editorTitle}>

                                    New Knowledge Note

                                </div>

                                <div style={styles.formGroup}>

                                    <label>Category</label>

                                    <select

                                        value={newNote.category}

                                        onChange={(e) =>

                                            setNewNote({

                                                ...newNote,

                                                category: e.target.value,

                                            })

                                        }

                                    >

                                        {

                                            SECTION_CONFIG.map(section => (

                                                <option

                                                    key={section.key}

                                                    value={section.key}

                                                >

                                                    {section.title}

                                                </option>

                                            ))

                                        }

                                    </select>

                                </div>

                                <div style={styles.formGroup}>

                                    <label>Title</label>

                                    <input

                                        value={newNote.title}

                                        onChange={(e) =>

                                            setNewNote({

                                                ...newNote,

                                                title: e.target.value,

                                            })

                                        }

                                    />

                                </div>

                                <div style={styles.formGroup}>

                                    <label>Summary</label>

                                    <textarea

                                        rows={2}

                                        value={newNote.summary}

                                        onChange={(e) =>

                                            setNewNote({

                                                ...newNote,

                                                summary: e.target.value,

                                            })

                                        }

                                    />

                                </div>

                                <div style={styles.formGroup}>

                                    <label>Details</label>

                                    <textarea

                                        rows={10}

                                        value={newNote.details}

                                        onChange={(e) =>

                                            setNewNote({

                                                ...newNote,

                                                details: e.target.value,

                                            })

                                        }

                                    />

                                </div>
                                
                                <div style={styles.focusCheckbox}>

                                    <input

                                        type="checkbox"

                                        checked={newNote.makeCurrentFocus}

                                        onChange={(e) =>

                                            setNewNote({

                                                ...newNote,

                                                makeCurrentFocus: e.target.checked,

                                            })

                                        }

                                    />

                                    <span>

                                        Make this the Active Focus

                                    </span>

                                </div>

                                <div style={styles.buttonRow}>

                                    <button

                                        style={styles.cancelButton}

                                        onClick={() =>

                                            setShowEditor(false)

                                        }

                                    >

                                        Cancel

                                    </button>

                                    <button

                                        style={styles.saveButton}

                                        onClick={saveKnowledgeNote}

                                    >

                                        Save Knowledge Note

                                    </button>

                                </div>
                            </div>

                        )

                    }
                    <div style={styles.liveBadge}>

                        <span style={styles.liveDot} />

                        Live Knowledge Base

                    </div>

                </div>

                {/* ==========================================
                    DASHBOARD
                ========================================== */}

                

                <div style={styles.dashboardGrid}>

                    {SECTION_CONFIG.map((section) => (

                        <DashboardCard
                            key={section.key}
                            short={section.short}
                            title={section.title}
                            subtitle={section.subtitle}
                            count={knowledge[section.key].length}
                            active={selectedSection === section.key}
                            onClick={() => setSelectedSection(section.key)}
                        />

                    ))}

                </div>

                <div style={styles.topPanels}>

                    <CurrentFocusPanel
                        items={(knowledge as any).current_focus || []}
                        onRemove={removeFocus}
                    />

                    <RecentlyFrozenPanel />

                </div>

                <KnowledgeSection
                    title={
                        SECTION_CONFIG.find(
                            s => s.key === selectedSection
                        )?.title || ""
                    }
                    items={selectedItems}
                />
                
               
                </div>

                </AppShell>

                );

                }

/* ==========================================================
   DASHBOARD CARD
========================================================== */

type DashboardCardProps = {

    short: string;

    title: string;

    subtitle: string;

    count: number;

    active: boolean;

    onClick: () => void;

};

function DashboardCard({

    short,

    title,

    subtitle,

    count,

    active,

    onClick,

}: DashboardCardProps) {

    return (

        <div
            onClick={onClick}
            style={{
                ...styles.metricCard,
                ...(active ? styles.metricCardActive : {}),
            }}
        >

            <div style={styles.metricTopRow}>

                <div style={styles.metricIcon}>

                    {short}

                </div>

                <div style={styles.metricCount}>

                    {count}

                </div>

            </div>

            <div style={styles.metricTitle}>

                {title}

            </div>

            <div style={styles.metricSubtitle}>

                {subtitle}

            </div>

        </div>

    );

}


/* ==========================================================
   CURRENT FOCUS
========================================================== */

function CurrentFocusPanel({
    items,
    onRemove,
}: {
    items: any[];
    onRemove: (noteId: string) => void;
}) {

    return (

        <div style={styles.panel}>

            <div style={styles.panelTitle}>

                Current Focus

            </div>

            {

                items.length === 0 ? (

                    <div style={styles.emptyState}>

                        No active focus items.

                    </div>

                ) : (

                    <div style={styles.timeline}>

                        {

                            items.map((item) => (

                                <div
                                    key={item.note_id}
                                    style={styles.timelineItem}
                                >

                                    <span>

                                        {item.title}

                                    </span>

                                    <button

                                        style={styles.removeFocusButton}

                                        onClick={() =>
                                            onRemove(item.note_id)
                                        }

                                    >

                                        −

                                    </button>

                                </div>

                            ))

                        }

                    </div>

                )

            }

        </div>

    );

}


/* ==========================================================
   RECENTLY FROZEN
========================================================== */

function RecentlyFrozenPanel() {

    return (

        <div style={styles.panel}>

            <div style={styles.panelTitle}>

                Recently Frozen

            </div>

            <div style={styles.emptyState}>

                No recent architecture decisions yet.

            </div>

        </div>

    );

}

/* ==========================================================
   KNOWLEDGE SECTION
========================================================== */

type KnowledgeSectionProps = {

    title: string;

    items: KnowledgeItem[];

};

function KnowledgeSection({

    title,

    items,

}: KnowledgeSectionProps) {

    return (

        <div style={styles.sectionContainer}>

            <div style={styles.sectionHeader}>

                <div style={styles.sectionTitle}>

                    {title}

                </div>

                <div style={styles.sectionCount}>

                    {items.length} Items

                </div>

            </div>

            {

                items.length === 0 ? (

                    <div style={styles.emptyKnowledge}>

                        No knowledge has been captured yet.

                    </div>

                ) : (

                    items.map((item) => (

                        <KnowledgeCard
                            key={item.id}
                            item={item}
                        />

                    ))

                )

            }

        </div>

    );

}


/* ==========================================================
   KNOWLEDGE CARD
========================================================== */

type KnowledgeCardProps = {

    item: KnowledgeItem;

};

function KnowledgeCard({

    item,

}: KnowledgeCardProps) {

    const [

        expanded,

        setExpanded,

    ] = useState(false);

    return (

        <div style={styles.knowledgeCard}>

            <div
                style={styles.knowledgeHeader}
                onClick={() =>
                    setExpanded(!expanded)
                }
            >

                <div>

                    <div style={styles.knowledgeId}>

                        {item.id}

                    </div>

                    <div style={styles.knowledgeTitle}>

                        {item.title}

                    </div>

                </div>

                <div style={styles.expandButton}>

                    {

                        expanded

                            ? "−"

                            : "+"

                    }

                </div>

            </div>

            {

                expanded && (

                    <div style={styles.knowledgeBody}>

                        {

                            item.summary && (

                                <>

                                    <div style={styles.label}>

                                        Summary

                                    </div>

                                    <div style={styles.bodyText}>

                                        {item.summary}

                                    </div>

                                </>

                            )

                        }

                        {

                            item.details && (

                                <>

                                    <div style={styles.label}>

                                        Details

                                    </div>

                                    <div style={styles.bodyText}>

                                        {item.details}

                                    </div>

                                </>

                            )

                        }

                    </div>

                )

            }

        </div>

    );

}

/* ==========================================================
   STYLES
========================================================== */

const styles: any = {

    page: {

        padding: 36,

        background: "#F6F8FB",

        minHeight: "100vh",

    },

    header: {

        display: "flex",

        justifyContent: "space-between",

        alignItems: "center",

        marginBottom: 36,

    },

    pageTitle: {

        fontSize: 34,

        fontWeight: 700,

        color: "#1F2937",

        marginBottom: 8,

    },

    pageSubtitle: {

        fontSize: 16,

        color: "#6B7280",

    },

    liveBadge: {

        display: "flex",

        alignItems: "center",

        gap: 10,

        padding: "10px 18px",

        borderRadius: 30,

        background: "#FFFFFF",

        boxShadow: "0 10px 25px rgba(0,0,0,.05)",

        fontWeight: 600,

    },

    liveDot: {

        width: 10,

        height: 10,

        borderRadius: "50%",

        background: "#22C55E",

    },

    dashboardGrid: {

        display: "grid",

        gridTemplateColumns: "repeat(5,1fr)",

        gap: 20,

        marginBottom: 30,

    },

    metricCard: {

        background: "#FFFFFF",

        borderRadius: 18,

        padding: 22,

        cursor: "pointer",

        transition: ".25s",

        border: "1px solid #ECECEC",

        boxShadow: "0 8px 24px rgba(0,0,0,.05)",

    },

    metricCardActive: {

        border: "2px solid #F97316",

        transform: "translateY(-2px)",

    },

    metricTopRow: {

        display: "flex",

        justifyContent: "space-between",

        alignItems: "center",

        marginBottom: 20,

    },

    metricIcon: {

        width: 52,

        height: 52,

        borderRadius: 14,

        background: "#FFF7ED",

        color: "#F97316",

        display: "flex",

        justifyContent: "center",

        alignItems: "center",

        fontWeight: 700,

        fontSize: 18,

    },

    metricCount: {

        fontSize: 36,

        fontWeight: 700,

        color: "#111827",

    },

    metricTitle: {

        fontSize: 18,

        fontWeight: 600,

        color: "#1F2937",

        marginBottom: 6,

    },

    metricSubtitle: {

        fontSize: 13,

        lineHeight: 1.5,

        color: "#6B7280",

    },

    topPanels: {

        display: "grid",

        gridTemplateColumns: "1fr 1fr",

        gap: 24,

        marginBottom: 30,

    },

    panel: {

        background: "#FFFFFF",

        borderRadius: 18,

        padding: 26,

        border: "1px solid #ECECEC",

        boxShadow: "0 8px 24px rgba(0,0,0,.05)",

    },

    panelTitle: {

        fontSize: 20,

        fontWeight: 700,

        marginBottom: 24,

        color: "#1F2937",

    },

    timeline: {

        display: "flex",

        flexDirection: "column",

        gap: 12,

    },

    timelineItem: {

        fontWeight: 600,

        color: "#374151",

    },

    timelineArrow: {

        marginLeft: 10,

        color: "#F97316",

        fontSize: 20,

    },

    currentMilestone: {

        display: "inline-flex",

        width: "fit-content",

        padding: "10px 18px",

        background: "#FFF7ED",

        color: "#EA580C",

        borderRadius: 25,

        fontWeight: 700,

    },

    emptyState: {

        color: "#6B7280",

        lineHeight: 1.8,

    },

    sectionContainer: {

        background: "#FFFFFF",

        borderRadius: 18,

        padding: 28,

        border: "1px solid #ECECEC",

        boxShadow: "0 8px 24px rgba(0,0,0,.05)",

    },

    sectionHeader: {

        display: "flex",

        justifyContent: "space-between",

        alignItems: "center",

        marginBottom: 24,

    },

    sectionTitle: {

        fontSize: 24,

        fontWeight: 700,

        color: "#1F2937",

    },

    sectionCount: {

        background: "#FFF7ED",

        color: "#EA580C",

        padding: "8px 16px",

        borderRadius: 20,

        fontWeight: 600,

    },

    emptyKnowledge: {

        color: "#6B7280",

        padding: 20,

    },

    knowledgeCard: {

        border: "1px solid #ECECEC",

        borderRadius: 14,

        marginBottom: 18,

        overflow: "hidden",

    },

    knowledgeHeader: {

        display: "flex",

        justifyContent: "space-between",

        alignItems: "center",

        padding: 22,

        cursor: "pointer",

        background: "#FFFFFF",

    },

    knowledgeId: {

        fontSize: 12,

        color: "#9CA3AF",

        fontWeight: 700,

        marginBottom: 6,

    },

    knowledgeTitle: {

        fontSize: 18,

        fontWeight: 600,

        color: "#111827",

    },

    expandButton: {

        width: 40,

        height: 40,

        borderRadius: 20,

        background: "#FFF7ED",

        color: "#F97316",

        display: "flex",

        justifyContent: "center",

        alignItems: "center",

        fontSize: 24,

        fontWeight: 700,

    },

    knowledgeBody: {

        padding: 22,

        borderTop: "1px solid #ECECEC",

        background: "#FCFCFC",

    },

    label: {

        fontSize: 13,

        fontWeight: 700,

        color: "#6B7280",

        marginBottom: 8,

        marginTop: 18,

    },

    bodyText: {

        color: "#374151",

        lineHeight: 1.8,

        whiteSpace: "pre-wrap",

    },

    newNoteBar: {

        display: "flex",

        justifyContent: "flex-end",

        marginBottom: 24,

    },

    newButton: {

        background: "#F97316",

        color: "#FFFFFF",

        border: "none",

        padding: "12px 24px",

        borderRadius: 10,

        cursor: "pointer",

        fontSize: 15,

        fontWeight: 600,

    },

    editorCard: {

        background: "#FFFFFF",

        padding: 28,

        borderRadius: 18,

        marginBottom: 28,

        border: "1px solid #ECECEC",

        boxShadow: "0 8px 24px rgba(0,0,0,.05)",

    },

    editorTitle: {

        fontSize: 22,

        fontWeight: 700,

        marginBottom: 24,

    },

    formGroup: {

        display: "flex",

        flexDirection: "column",

        marginBottom: 18,

    },

    buttonRow: {

        display: "flex",

        justifyContent: "flex-end",

        gap: 14,

        marginTop: 24,

    },

    cancelButton: {

        background: "#FFFFFF",

        border: "1px solid #D1D5DB",

        color: "#374151",

        borderRadius: 10,

        padding: "12px 20px",

        cursor: "pointer",

        fontWeight: 600,

    },

    saveButton: {

        background: "#F97316",

        color: "#FFFFFF",

        border: "none",

        borderRadius: 10,

        padding: "12px 24px",

        cursor: "pointer",

        fontWeight: 700,

    },

    focusCheckbox: {

        display: "flex",

        alignItems: "center",

        gap: 12,

        marginTop: 10,

        marginBottom: 22,

        fontWeight: 600,

        color: "#374151",

    },

    removeFocusButton: {

        border: "none",

        background: "#F97316",

        color: "#FFFFFF",

        width: 24,

        height: 24,

        borderRadius: 12,

        cursor: "pointer",

        fontWeight: 700,

        fontSize: 16,

    },

};