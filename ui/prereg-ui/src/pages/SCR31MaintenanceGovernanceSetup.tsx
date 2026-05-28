import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppShell from "../components/layout/AppShell";

/* ==========================================================
🧠 TYPES
========================================================== */

interface UploadSummary {
  flats_processed: number;
  receivables_created: number;
  initialization_rows: number;
  total_outstanding: string;
  total_advance: string;
  warning_count: number;
  warnings: string[];
}

/* ==========================================================
🧠 MAIN
========================================================== */

export default function SCR31MaintenanceGovernanceSetup() {

  const navigate = useNavigate();

  const societyId =
    localStorage.getItem("society_id");

  /* ==========================================================
  🧠 STATES
  ========================================================== */

  const [loading, setLoading] =
    useState(false);

  const [downloading, setDownloading] =
    useState(false);

  const [uploading, setUploading] =
    useState(false);

  const [savingOccupancy, setSavingOccupancy] =
    useState(false);

  const [file, setFile] =
    useState<File | null>(null);

  const [uploadComplete, setUploadComplete] =
    useState(false);

  const [summary, setSummary] =
    useState<UploadSummary | null>(null);

  const [flats, setFlats] =
    useState<any[]>([]);

  const [selectedRentalFlat, setSelectedRentalFlat] =
    useState<any>(null);

  const [rentedFlats, setRentedFlats] =
    useState<any[]>([]);
  
  /* ==========================================================
  🧠 INITIAL HYDRATION
  ========================================================== */

  useEffect(() => {

    hydrateContext();

    loadFlats();

  }, []);

  const hydrateContext = async () => {

    try {

      setLoading(true);

      const response = await fetch(
        `http://127.0.0.1:8000/api/society/scr31-context/?society_id=${societyId}`
      );

      const data = await response.json();

      console.log(
        "SCR31 CONTEXT",
        data
      );

      
    } catch (error) {

      console.error(
        "SCR31 CONTEXT ERROR",
        error
      );

    } finally {

      setLoading(false);

    }
  };
  
  const loadFlats = async () => {

    if (!societyId) {
        return;
    }

    try {

        const response = await fetch(
        `/api/society/flats/?society_id=${societyId}`
        );

        const data = await response.json();

        console.log(
        "SCR31 FLATS",
        data
        );

        setFlats(data || []);

    } catch (error) {

        console.error(
        "FAILED TO LOAD FLATS",
        error
        );
    }
};
  /* ==========================================================
  🧠 DOWNLOAD TEMPLATE
  ========================================================== */

  const handleDownloadTemplate = async () => {

    try {

      setDownloading(true);

      const url =
        `http://127.0.0.1:8000/api/society/maintenance-opening-balance/download/?society_id=${societyId}`;

      window.open(url, "_blank");

    } catch (error) {

      console.error(error);

      alert(
        "Unable to generate template"
      );

    } finally {

      setDownloading(false);

    }
  };

  /* ==========================================================
  🧠 UPLOAD FILE
  ========================================================== */

  const handleUpload = async () => {

    if (!file) {

      alert(
        "Please select completed Excel file"
      );

      return;
    }

    try {

      setUploading(true);

      const formData = new FormData();

      formData.append(
        "society_id",
        societyId || ""
      );

      formData.append(
        "file",
        file
      );

      const response = await fetch(
        "http://127.0.0.1:8000/api/society/maintenance-opening-balance/upload/",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      console.log(
        "SCR31 IMPORT RESPONSE",
        data
      );

      if (!response.ok) {

        if (
          data?.errors &&
          Array.isArray(data.errors)
        ) {

          throw new Error(
            data.errors.join("\n")
          );
        }

        throw new Error(
          data?.message ||
          "Upload failed"
        );
      }

      setSummary(data);

      setUploadComplete(true);

    } catch (error: any) {

      console.error(error);

      alert(
        "Upload Failed\n\n" +
        error.message
      );

    } finally {

      setUploading(false);

    }
  };

  /* ==========================================================
  🧠 RENTAL HELPERS
  ========================================================== */

  const addRentalFlat = () => {

    if (!selectedRentalFlat) {
        return;
    }

    const flatData =
     flats.find(
        (row: any) =>
            row.flat_number === selectedRentalFlat
        );

    if (!flatData) {
        return;
    }

    if (
        rentedFlats.some(
        (f) =>
            f.flat_number ===
            flatData.flat_number
        )
    ) {

        alert("Flat already added");

        return;
    }

    setRentedFlats([
        ...rentedFlats,
        flatData,
    ]);

    setSelectedRentalFlat(null);
    };

    const removeRentalFlat = (
        flatNumber: string
    ) => {

        setRentedFlats((prev) =>
            prev.filter(
            (item: any) =>
                item.flat_number !== flatNumber
            )
        );

    };
  /* ==========================================================
  🧠 RENTED COUNT
  ========================================================== */

  const activeTenancies = useMemo(() => {

    return rentedFlats.length;

  }, [rentedFlats]);

  /* ==========================================================
  🧠 CONTINUE
  ========================================================== */
  const saveOccupancyInitialization = async () => {

    try {

        setSavingOccupancy(true);

        const occupancy_updates =
        rentedFlats.map(
            (flat: any) => ({
            flat_id: flat.id,
            occupancy_type: "RENTED",
            })
        );

        const payload = {

        society_id: societyId,

        occupancy_updates,

        heads: [],

        governance: {},
        };

        console.log(
        "SCR31 OCCUPANCY SAVE",
        payload
        );

        const response = await fetch(
        "http://127.0.0.1:8000/api/society/scr31-save/",
        {
            method: "POST",

            headers: {
            "Content-Type":
                "application/json",
            },

            body: JSON.stringify(
            payload
            ),
        }
        );

        const data = await response.json();

        console.log(
        "SCR31 SAVE RESPONSE",
        data
        );

        if (!response.ok) {

        throw new Error(
            data?.message ||
            "Occupancy save failed"
        );
        }

        alert(
        `${data.occupancy_saved} flats marked as rented`
        );

    } catch (error: any) {

        console.error(error);

        alert(
        error.message ||
        "Occupancy save failed"
        );

    } finally {

        setSavingOccupancy(false);

    }
    };
  const continueToGovernance = () => {

    navigate(
      "/financial-onboarding/governance-intelligence"
    );
  };

  /* ==========================================================
  🧠 LOADING
  ========================================================== */

  if (loading) {

    return (
      <AppShell>
        <div style={{ padding: 24 }}>
          Initializing maintenance onboarding...
        </div>
      </AppShell>
    );
  }

  /* ==========================================================
  🧠 RENDER
  ========================================================== */

  return (
    <AppShell>

      <div style={styles.pageWrapper}>

        <div style={styles.container}>

          {/* ====================================================== */}
          {/* HERO */}
          {/* ====================================================== */}

          <div style={{ marginBottom: 30 }}>

            <div style={styles.pill}>
              Maintenance Initialization
            </div>

            <h1 style={styles.title}>
              Initialize Existing Maintenance Balances
            </h1>

            <p style={styles.subtitle}>
              Import your society’s existing maintenance dues,
              advance balances, and occupancy-linked operational
              data.
            </p>

          </div>

          {/* ====================================================== */}
          {/* SUMMARY */}
          {/* ====================================================== */}

          <div style={styles.summaryCard}>

            <div>

              <div style={styles.summaryTitle}>
                Intelligent Financial Initialization
              </div>

              <div style={styles.summarySubtitle}>
                The platform will initialize your
                society’s operational maintenance
                position using existing billing balances
                and occupancy truth.
              </div>

            </div>

            <div style={styles.counterCard}>

              <div style={styles.counterValue}>
                {summary?.flats_processed || 0}
              </div>

              <div style={styles.counterLabel}>
                Flats Initialized
              </div>

            </div>

          </div>

          {/* ====================================================== */}
          {/* STEP 1 */}
          {/* ====================================================== */}

          <div style={styles.sectionCard}>

            <div style={styles.sectionHeader}>

              <div>

                <div style={styles.sectionStep}>
                  STEP 1
                </div>

                <div style={styles.sectionTitle}>
                  Download Opening Balance Template
                </div>

                <div style={styles.sectionSubtitle}>
                  Download a pre-structured Excel template
                  to initialize outstanding dues,
                  advances and occupancy-linked
                  operational data.
                </div>

              </div>

            </div>

            <div style={styles.sectionBody}>

              <div style={styles.infoBox}>

                The template already understands
                your society structure and flat hierarchy.

                Simply fill:
                outstanding dues,
                advances,
                and occupancy details.

              </div>

              <button
                onClick={handleDownloadTemplate}
                disabled={downloading}
                style={styles.primaryButton}
              >
                {downloading
                  ? "Preparing Template..."
                  : "Download Excel Template"}
              </button>

            </div>

          </div>

          {/* ====================================================== */}
          {/* STEP 2 */}
          {/* ====================================================== */}

          <div style={styles.sectionCard}>

            <div style={styles.sectionHeader}>

              <div>

                <div style={styles.sectionStep}>
                  STEP 2
                </div>

                <div style={styles.sectionTitle}>
                  Upload Completed File
                </div>

                <div style={styles.sectionSubtitle}>
                  The platform will validate and initialize
                  operational maintenance balances.
                </div>

              </div>

            </div>

            <div style={styles.sectionBody}>

              <div style={styles.uploadCard}>

                <div style={styles.uploadIcon}>
                  ⬆
                </div>

                <div style={styles.uploadTitle}>
                  Upload Completed Excel File
                </div>

                <div style={styles.uploadSubtitle}>
                  Only .xlsx files supported
                </div>

                <input
                  type="file"
                  accept=".xlsx"
                  onChange={(e) =>
                    setFile(
                      e.target.files?.[0] || null
                    )
                  }
                  style={{ marginTop: 18 }}
                />

                {file && (

                  <div style={styles.fileBadge}>
                    {file.name}
                  </div>

                )}

                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  style={{
                    ...styles.primaryButton,
                    marginTop: 20,
                  }}
                >
                  {uploading
                    ? "Initializing Balances..."
                    : "Upload & Initialize"}
                </button>

              </div>

            </div>

          </div>

          {/* ====================================================== */}
          {/* STEP 3 */}
          {/* ====================================================== */}

          {uploadComplete && summary && (

            <div style={styles.sectionCard}>

              <div style={styles.sectionHeader}>

                <div>

                  <div style={styles.sectionStep}>
                    STEP 3
                  </div>

                  <div style={styles.sectionTitle}>
                    Financial Initialization Summary
                  </div>

                  <div style={styles.sectionSubtitle}>
                    Existing maintenance balances
                    have been initialized successfully.
                  </div>

                </div>

              </div>

              <div style={styles.sectionBody}>

                <div style={styles.metricsGrid}>

                  <MetricCard
                    label="Flats Initialized"
                    value={summary.flats_processed}
                  />

                  <MetricCard
                    label="Receivables Created"
                    value={summary.receivables_created}
                  />

                  <MetricCard
                    label="Outstanding Imported"
                    value={`₹${summary.total_outstanding}`}
                  />

                  <MetricCard
                    label="Advances Detected"
                    value={`₹${summary.total_advance}`}
                  />

                </div>

                {summary.warning_count > 0 && (

                  <div style={styles.warningBox}>

                    <div style={styles.warningTitle}>
                      Validation Warnings
                    </div>

                    {summary.warnings.map(
                      (warning, index) => (

                        <div
                          key={index}
                          style={styles.warningItem}
                        >
                          • {warning}
                        </div>

                      )
                    )}

                  </div>

                )}

              </div>

            </div>

          )}

          {/* ====================================================== */}
          {/* STEP 4 */}
          {/* ====================================================== */}

          <div style={styles.sectionCard}>

            <div style={styles.sectionHeader}>

              <div>

                <div style={styles.sectionStep}>
                  STEP 4
                </div>

                <div style={styles.sectionTitle}>
                  Identify Flats Given Out On Rent
                </div>

                <div style={styles.sectionSubtitle}>
                  Select flats currently occupied
                  by tenants or non-owner residents.
                </div>

              </div>

              <div style={styles.activeBadge}>
                {activeTenancies} Rented Flats
              </div>

            </div>

            <div style={styles.sectionBody}>

              <div style={styles.rentalSelectorRow}>

                <select
                  value={selectedRentalFlat || ""}
                  onChange={(e) =>
                    setSelectedRentalFlat(
                      e.target.value
                    )
                  }
                  style={styles.matrixSelect}
                >

                  <option value="">
                    Select Flat
                  </option>

                  {flats.map((flat) => (

                    <option
                        key={flat.id}
                        value={flat.flat_number}
                    >
                        Flat {flat.flat_number}
                    </option>

                  ))}

                </select>

                <button
                  onClick={addRentalFlat}
                  style={styles.primaryButton}
                >
                  Add Rented Flat
                </button>

              </div>

              {rentedFlats.length > 0 && (

                <div style={styles.rentedListWrap}>

                  {rentedFlats.map((flatData) => (

                    <div
                      key={flatData.flat_number}
                      style={styles.rentedFlatCard}
                    >

                      <div>

                        <div style={styles.rentedFlatTitle}>
                          Flat {flatData.flat_number}
                        </div>

                        <div style={styles.rentedFlatSubtitle}>
                          Marked as tenant occupied
                        </div>

                      </div>

                      <button
                        onClick={() =>
                          removeRentalFlat(
                            flatData.flat_number
                          )
                        }
                        style={styles.removeButton}
                      >
                        Remove
                      </button>

                    </div>

                  ))}

                </div>

              )}

              <div style={styles.rentalSummaryCard}>

                <div style={styles.rentalSummaryValue}>
                  {activeTenancies}
                </div>

                <div style={styles.rentalSummaryLabel}>
                  Flats marked as rented
                </div>

              </div>

            <button
                onClick={
                    saveOccupancyInitialization
                }
                disabled={savingOccupancy}
                style={{
                    ...styles.primaryButton,
                    marginTop: 20,
                }}
                >
                {savingOccupancy
                    ? "Saving Occupancy..."
                    : "Save Occupancy Initialization"}
                </button>
            </div>

          </div>
          
          {/* ====================================================== */}
          {/* FOOTER */}
          {/* ====================================================== */}

          <div style={styles.footer}>

            <div>

              <div style={styles.footerTitle}>
                Maintenance onboarding initialized.
              </div>

              <div style={styles.footerSubtitle}>
                Opening balances and occupancy
                initialization have been completed
                successfully.
              </div>

            </div>

            <button
              onClick={continueToGovernance}
              style={styles.saveButton}
            >
              Continue to Governance Intelligence
            </button>

          </div>

        </div>

      </div>

    </AppShell>
  );
}

/* ==========================================================
🧠 METRIC CARD
========================================================== */

function MetricCard({
  label,
  value,
}: any) {

  return (

    <div style={styles.metricCard}>

      <div style={styles.metricValue}>
        {value}
      </div>

      <div style={styles.metricLabel}>
        {label}
      </div>

    </div>

  );
}

/* ==========================================================
🧠 STYLES
========================================================== */

const styles: any = {

  pageWrapper: {
    padding: 24,
  },

  container: {
    maxWidth: 1180,
    margin: "0 auto",
  },

  pill: {
    display: "inline-flex",
    alignItems: "center",
    padding: "8px 14px",
    borderRadius: 999,
    background: "#fff7ed",
    border: "1px solid #fed7aa",
    color: "#ea580c",
    fontSize: 12,
    fontWeight: 700,
    marginBottom: 18,
  },

  title: {
    fontSize: 32,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 10,
  },

  subtitle: {
    fontSize: 15,
    lineHeight: 1.7,
    color: "#6b7280",
    maxWidth: 900,
  },

  summaryCard: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 20,
    flexWrap: "wrap",
    borderRadius: 22,
    padding: 24,
    marginBottom: 28,
    border: "1px solid #fed7aa",
    background:
      "linear-gradient(135deg, #fff7ed 0%, #ffffff 100%)",
  },

  summaryTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 6,
  },

  summarySubtitle: {
    fontSize: 14,
    lineHeight: 1.6,
    color: "#6b7280",
    maxWidth: 700,
  },

  counterCard: {
    minWidth: 180,
    padding: 18,
    borderRadius: 18,
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    textAlign: "center",
  },

  counterValue: {
    fontSize: 28,
    fontWeight: 700,
    color: "#f97316",
  },

  counterLabel: {
    fontSize: 13,
    color: "#6b7280",
    marginTop: 4,
  },

  sectionCard: {
    borderRadius: 22,
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    marginBottom: 24,
    overflow: "hidden",
  },

  sectionHeader: {
    padding: 24,
    borderBottom: "1px solid #f3f4f6",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 20,
    flexWrap: "wrap",
  },

  sectionBody: {
    padding: 24,
  },

  sectionStep: {
    fontSize: 11,
    fontWeight: 700,
    letterSpacing: 1,
    color: "#f97316",
    marginBottom: 8,
  },

  sectionTitle: {
    fontSize: 22,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 8,
  },

  sectionSubtitle: {
    fontSize: 14,
    lineHeight: 1.6,
    color: "#6b7280",
    maxWidth: 850,
  },

  infoBox: {
    background: "#fff7ed",
    border: "1px solid #fed7aa",
    padding: 18,
    borderRadius: 14,
    color: "#7c2d12",
    fontSize: 14,
    lineHeight: 1.7,
    marginBottom: 20,
  },

  uploadCard: {
    border: "2px dashed #fdba74",
    borderRadius: 22,
    padding: 40,
    textAlign: "center",
    background: "#fffdfb",
  },

  uploadIcon: {
    fontSize: 38,
    marginBottom: 14,
  },

  uploadTitle: {
    fontSize: 18,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 6,
  },

  uploadSubtitle: {
    fontSize: 13,
    color: "#6b7280",
  },

  fileBadge: {
    marginTop: 16,
    display: "inline-flex",
    padding: "8px 12px",
    borderRadius: 999,
    background: "#fff7ed",
    color: "#ea580c",
    fontSize: 12,
    fontWeight: 700,
  },

  primaryButton: {
    border: "none",
    background: "#f97316",
    color: "#ffffff",
    borderRadius: 12,
    padding: "14px 22px",
    fontWeight: 700,
    fontSize: 14,
    cursor: "pointer",
  },

  metricsGrid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(220px, 1fr))",
    gap: 18,
  },

  metricCard: {
    borderRadius: 18,
    border: "1px solid #e5e7eb",
    padding: 20,
    background: "#ffffff",
  },

  metricValue: {
    fontSize: 26,
    fontWeight: 700,
    color: "#f97316",
    marginBottom: 8,
  },

  metricLabel: {
    fontSize: 13,
    color: "#6b7280",
  },

  warningBox: {
    marginTop: 24,
    padding: 18,
    borderRadius: 16,
    border: "1px solid #fde68a",
    background: "#fffbeb",
  },

  warningTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#92400e",
    marginBottom: 12,
  },

  warningItem: {
    fontSize: 13,
    color: "#78350f",
    marginBottom: 6,
  },

  matrixSelect: {
    minWidth: 280,
    border: "1px solid #d1d5db",
    borderRadius: 12,
    padding: "12px 14px",
    fontSize: 14,
    background: "#ffffff",
    outline: "none",
  },

  rentalSelectorRow: {
    display: "flex",
    gap: 16,
    alignItems: "center",
    flexWrap: "wrap",
    marginBottom: 24,
  },

  rentedListWrap: {
    display: "grid",
    gap: 14,
    marginBottom: 24,
  },

  rentedFlatCard: {
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: 18,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 16,
    background: "#ffffff",
  },

  rentedFlatTitle: {
    fontSize: 15,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 4,
  },

  rentedFlatSubtitle: {
    fontSize: 13,
    color: "#6b7280",
  },

  removeButton: {
    border: "none",
    background: "#fee2e2",
    color: "#b91c1c",
    borderRadius: 10,
    padding: "10px 14px",
    fontWeight: 700,
    cursor: "pointer",
  },

  rentalSummaryCard: {
    borderRadius: 18,
    padding: 24,
    background:
      "linear-gradient(135deg, #fff7ed 0%, #ffffff 100%)",
    border: "1px solid #fed7aa",
    textAlign: "center",
  },

  rentalSummaryValue: {
    fontSize: 34,
    fontWeight: 700,
    color: "#f97316",
    marginBottom: 8,
  },

  rentalSummaryLabel: {
    fontSize: 14,
    color: "#6b7280",
  },

  activeBadge: {
    display: "inline-flex",
    padding: "8px 12px",
    borderRadius: 999,
    background: "#fff7ed",
    color: "#ea580c",
    fontSize: 12,
    fontWeight: 700,
  },

  footer: {
    marginTop: 36,
    paddingTop: 24,
    borderTop: "1px solid #e5e7eb",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 20,
    flexWrap: "wrap",
  },

  footerTitle: {
    fontSize: 14,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 6,
  },

  footerSubtitle: {
    fontSize: 13,
    color: "#6b7280",
  },

  saveButton: {
    padding: "14px 24px",
    borderRadius: 12,
    border: "none",
    background: "#f97316",
    color: "#ffffff",
    fontWeight: 700,
    fontSize: 14,
    cursor: "pointer",
  },
};