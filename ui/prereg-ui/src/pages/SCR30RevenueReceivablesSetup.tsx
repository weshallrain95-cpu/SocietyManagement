import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppShell from "../components/layout/AppShell";

// ==========================================================
// 🧠 SCR30 — REVENUE & RECEIVABLES SETUP
// ==========================================================
// Date: 2026-05-09
//
// Purpose:
// Operational activation layer for society revenue channels.
//
// IMPORTANT:
// - SCR30 activates receivable channels
// - SCR30 does NOT configure billing logic
// - SCR30 does NOT configure rates/formulas
// - SCR31 operationalizes maintenance billing
//
// UX Principle:
// “The system already understands my society —
// I am simply confirming and refining it.”
// ==========================================================

interface RevenueHead {
  code: string;
  name: string;
  helper: string;
  recoverableFrom: string;
  billingNature: string;
  enabled: boolean;

  autoConfigured?: boolean;

  hydrationReason?: string;

  notes?: string;

  customized?: boolean;

  // ======================================================
  // EXISTING RECOVERABLE MATRIX
  // ======================================================

  basis?: string;

  rate?: string | number;

  mandatory?: boolean;

  // ======================================================
  // COMMERCIAL MONETIZATION
  // ======================================================

  revenueModel?: string;

  monthlyValue?: string | number;

  agreementExists?: boolean;

  // ======================================================
  // AMENITIES
  // ======================================================

  accessType?: string;

  pricingModel?: string;

  usageFee?: string | number;

  bookingRequired?: boolean;

  // ======================================================
  // TREASURY / FINANCIAL INCOME
  // ======================================================

  instrumentType?: string;

  institution?: string;

  principalValue?: string | number;

  currentValue?: string | number;

  yieldPercent?: string | number;

  principalLinked?: boolean;

  depositDate?: string;

  maturityDate?: string;

  renewalMode?: string;

  payoutType?: string;

  prematureWithdrawalAllowed?: boolean;
}

type RevenueRowProps = {
  head: RevenueHead;
  onToggle: () => void;
  onNoteChange: (value: string) => void;
};

const CORE_RECURRING: RevenueHead[] = [
  
  {
    code: "SERVICE_CHARGES",
    name: "Service Charges",
    helper:
      "Recurring service-related operational recoveries.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: true,
    autoConfigured: true,
    hydrationReason: "Configured in SCR31",
  },
  {
    code: "REPAIR_FUND",
    name: "Repair Fund",
    helper:
      "Building repair and maintenance reserve contributions.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: true,
    autoConfigured: true,
    hydrationReason: "Configured in SCR31",
  },
  {
    code: "SINKING_FUND",
    name: "Sinking Fund",
    helper:
      "Long-term capital reserve collection for society infrastructure.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: true,
    autoConfigured: true,
    hydrationReason: "Configured in SCR31",
  },
  {
    code: "WATER_CHARGES",
    name: "Water Charges",
    helper:
      "Recurring operational water recovery charges.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: true,
    autoConfigured: true,
    hydrationReason: "Configured in SCR31",
  },
  {
    code: "COMMON_ELECTRICITY",
    name: "Common Electricity",
    helper:
      "Recovery of common electricity operational costs.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
];

const CORE_RECURRING_ADVANCED: RevenueHead[] = [
  {
    code: "LIFT_MAINTENANCE",
    name: "Lift Maintenance",
    helper:
      "Operational recovery for elevator maintenance.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "SECURITY_CHARGES",
    name: "Security Charges",
    helper:
      "Recurring recovery for security operations.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "HOUSEKEEPING",
    name: "Housekeeping Charges",
    helper:
      "Operational housekeeping and maintenance recoveries.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
];

const PARKING_MOBILITY: RevenueHead[] = [
  {
    code: "PARKING_CHARGES",
    name: "Parking Charges",
    helper:
      "Recover parking allocation and maintenance charges.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "VISITOR_PARKING",
    name: "Visitor Parking Charges",
    helper:
      "Operational visitor parking monetization.",
    recoverableFrom: "Members",
    billingNature: "Usage Based",
    enabled: false,
  },
  {
    code: "EV_CHARGING",
    name: "EV Charging Recovery",
    helper:
      "Recover electric vehicle charging operational expenses.",
    recoverableFrom: "Members",
    billingNature: "Usage Based",
    enabled: false,
  },
];

const OCCUPANCY_COMPLIANCE: RevenueHead[] = [
  {
    code: "NON_OCCUPANCY",
    name: "Non Occupancy Charges",
    helper:
      "Charges applicable for rented or non-owner occupied flats.",
    recoverableFrom: "Tenants",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "MOVE_IN_OUT",
    name: "Move-in / Move-out Charges",
    helper:
      "Operational movement and logistics charges.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
  {
    code: "TENANT_REGISTRATION",
    name: "Tenant Registration Charges",
    helper:
      "Tenant documentation and compliance processing charges.",
    recoverableFrom: "Tenants",
    billingNature: "On-Demand",
    enabled: false,
  },
];

const PENALTIES_RECOVERIES: RevenueHead[] = [
  {
    code: "INTEREST_ON_DUES",
    name: "Interest on Dues",
    helper:
      "Delayed payment interest recoveries.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "LATE_PAYMENT",
    name: "Late Payment Penalties",
    helper:
      "Penalty charges for overdue member dues.",
    recoverableFrom: "Members",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "CHEQUE_BOUNCE",
    name: "Cheque Bounce Charges",
    helper:
      "Penalty charges for cheque failures.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
];

const MEMBER_SERVICES: RevenueHead[] = [
  {
    code: "TRANSFER_FEES",
    name: "Transfer Fees",
    helper:
      "Membership and flat transfer charges.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
  {
    code: "TRANSFER_PREMIUM",
    name: "Transfer Premium",
    helper:
      "Premium transfer-related recoveries.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
  {
    code: "MEMBERSHIP_PROCESSING",
    name: "Membership Processing Fees",
    helper:
      "Operational membership onboarding recoveries.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
];

const AMENITIES: RevenueHead[] = [
  {
    code: "GYM",
    name: "Gym Fees",
    helper:
      "Collect membership or usage charges for fitness facilities.",
    recoverableFrom: "Members",
    billingNature: "Usage Based",
    enabled: false,
  },
  {
    code: "SWIMMING_POOL",
    name: "Swimming Pool Fees",
    helper:
      "Pool usage and operational recovery charges.",
    recoverableFrom: "Members",
    billingNature: "Usage Based",
    enabled: false,
  },
  {
    code: "CLUBHOUSE",
    name: "Clubhouse Charges",
    helper:
      "Community clubhouse access and monetization.",
    recoverableFrom: "Members",
    billingNature: "Booking Based",
    enabled: false,
  },
  {
    code: "PARTY_HALL",
    name: "Party Hall Booking",
    helper:
      "Booking-based event and hall monetization.",
    recoverableFrom: "Members",
    billingNature: "Booking Based",
    enabled: false,
  },
];

const EXTERNAL_MONETIZATION: RevenueHead[] = [
  {
    code: "TOWER_RENT",
    name: "Mobile Tower Rent",
    helper:
      "Commercial telecom infrastructure income.",
    recoverableFrom: "External Parties",
    billingNature: "Lease Based",
    enabled: false,
  },
  {
    code: "ADVERTISEMENT",
    name: "Advertisement Income",
    helper:
      "Commercial advertisement monetization.",
    recoverableFrom: "External Parties",
    billingNature: "Lease Based",
    enabled: false,
  },
  {
    code: "ATM_RENT",
    name: "ATM Rent",
    helper:
      "Commercial ATM lease recoveries.",
    recoverableFrom: "External Parties",
    billingNature: "Lease Based",
    enabled: false,
  },
];

const FINANCIAL_INCOME: RevenueHead[] = [
  {
    code: "BANK_INTEREST",
    name: "Bank Interest",
    helper:
      "Interest earned from operational banking balances.",
    recoverableFrom: "External Parties",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "FD_INTEREST",
    name: "FD Interest",
    helper:
      "Fixed deposit treasury interest income.",
    recoverableFrom: "External Parties",
    billingNature: "Recurring",
    enabled: false,
  },
  {
    code: "INVESTMENT_INCOME",
    name: "Investment Income",
    helper:
      "Treasury and investment income tracking.",
    recoverableFrom: "External Parties",
    billingNature: "Recurring",
    enabled: false,
  },
];

const MISCELLANEOUS: RevenueHead[] = [
  {
    code: "DONATIONS",
    name: "Donations",
    helper:
      "Voluntary contributions received by the society.",
    recoverableFrom: "Mixed",
    billingNature: "On-Demand",
    enabled: false,
  },
  {
    code: "SCRAP_SALE",
    name: "Scrap Sale",
    helper:
      "Scrap disposal operational recoveries.",
    recoverableFrom: "External Parties",
    billingNature: "On-Demand",
    enabled: false,
  },
  {
    code: "FESTIVAL_CONTRIBUTIONS",
    name: "Festival Contributions",
    helper:
      "Event and festival participation recoveries.",
    recoverableFrom: "Members",
    billingNature: "On-Demand",
    enabled: false,
  },
];

export default function SCR30RevenueReceivablesSetup() {
  const navigate = useNavigate();

  const societyId = localStorage.getItem("society_id");

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [internalHeads, setInternalHeads] =
    useState<RevenueHead[]>(CORE_RECURRING);
  
  const [internalAdvancedHeads, setInternalAdvancedHeads] =
    useState<RevenueHead[]>(CORE_RECURRING_ADVANCED);
  
  const [parkingHeads, setParkingHeads] =
    useState<RevenueHead[]>(PARKING_MOBILITY);

  const [occupancyHeads, setOccupancyHeads] =
    useState<RevenueHead[]>(OCCUPANCY_COMPLIANCE);
  
  const [penaltyHeads, setPenaltyHeads] =
    useState<RevenueHead[]>(PENALTIES_RECOVERIES);

  const [memberServiceHeads, setMemberServiceHeads] =
    useState<RevenueHead[]>(MEMBER_SERVICES);

  const [externalHeads, setExternalHeads] =
    useState<RevenueHead[]>(EXTERNAL_MONETIZATION);

  const [amenityHeads, setAmenityHeads] =
    useState<RevenueHead[]>(AMENITIES);

  const [financialHeads, setFinancialHeads] =
    useState<RevenueHead[]>(FINANCIAL_INCOME);

  const [miscHeads, setMiscHeads] =
    useState<RevenueHead[]>(MISCELLANEOUS);

  const [expandedSections, setExpandedSections] = useState({
  
  internal: true,
  parking: false,
  occupancy: false,
  penalties: false,
  memberServices: false,
  external: false,
  amenities: false,
  financial: false,
  misc: false,
});

const [showAdvancedRecurring, setShowAdvancedRecurring] =
  useState(false);

// ==========================================================
// 🧠 INTELLIGENT HYDRATION ENGINE
// ==========================================================

useEffect(() => {
  hydrateFinancialTruths();
}, []);

const hydrateFinancialTruths = async () => {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/society/financial-context/?society_id=${societyId}`
    );

    const data = await response.json();

    console.log(
      "SCR30 Financial Context",
      data
    );

    const hydrateSection = (
        heads: RevenueHead[]
        ) => {

        return heads.map((head) => {

            // ------------------------------------------
            // EXISTING CONFIGURATION
            // ------------------------------------------

            const hydrated =
            data.hydrated_heads?.find(
                (item: any) =>
                item.code === head.code
            );

            if (hydrated) {
            
            return {

                ...head,

                enabled:
                hydrated.auto_enabled ?? true,

                autoConfigured: true,

                hydrationReason:
                hydrated.source ===
                "MaintenanceCharge"
                    ? "Already configured in society billing setup"
                    : "Hydrated from operational configuration",

                // ==================================================
                // CORE
                // ==================================================

                basis:
                hydrated.basis ??
                head.basis,

                rate:
                hydrated.rate ??
                hydrated.amount ??
                head.rate,

                mandatory:
                hydrated.mandatory ??
                head.mandatory,

                // ==================================================
                // COMMERCIAL MONETIZATION
                // ==================================================

                revenueModel:
                hydrated.revenueModel ??
                head.revenueModel,

                monthlyValue:
                hydrated.monthlyValue ??
                head.monthlyValue,

                agreementExists:
                hydrated.agreementExists ??
                head.agreementExists,

                // ==================================================
                // AMENITIES
                // ==================================================

                accessType:
                hydrated.accessType ??
                head.accessType,

                pricingModel:
                hydrated.pricingModel ??
                head.pricingModel,

                usageFee:
                hydrated.usageFee ??
                head.usageFee,

                // ==================================================
                // TREASURY
                // ==================================================

                instrumentType:
                hydrated.instrumentType ??
                head.instrumentType,

                institution:
                hydrated.institution ??
                head.institution,

                principalValue:
                hydrated.principalValue ??
                head.principalValue,

                currentValue:
                hydrated.currentValue ??
                head.currentValue,

                yieldPercent:
                hydrated.yieldPercent ??
                head.yieldPercent,

                principalLinked:
                hydrated.principalLinked ??
                head.principalLinked,

                depositDate:
                hydrated.depositDate ??
                head.depositDate,

                maturityDate:
                hydrated.maturityDate ??
                head.maturityDate,

                renewalMode:
                hydrated.renewalMode ??
                head.renewalMode,

                payoutType:
                hydrated.payoutType ??
                head.payoutType,

                prematureWithdrawalAllowed:
                hydrated.prematureWithdrawalAllowed ??
                head.prematureWithdrawalAllowed,
            };
            }

            // ------------------------------------------
            // RECOMMENDED CONFIGURATION
            // ------------------------------------------

            const recommended =
            data.recommended_heads?.find(
                (item: any) =>
                item.code === head.code
            );

            if (recommended) {

            return {

                ...head,

                enabled: true,

                autoConfigured: true,

                hydrationReason:
                recommended.reason ||
                "Recommended from governance configuration",
            };
            }

            return head;
        });
        };
    // ======================================================
    // INTERNAL RECOVERIES
    // ======================================================

    setInternalHeads((prev) =>
    hydrateSection(prev)
    );

    setInternalAdvancedHeads((prev) =>
    hydrateSection(prev)
    );

    setParkingHeads((prev) =>
    hydrateSection(prev)
    );

    setOccupancyHeads((prev) =>
    hydrateSection(prev)
    );

    setPenaltyHeads((prev) =>
    hydrateSection(prev)
    );

    setMemberServiceHeads((prev) =>
    hydrateSection(prev)
    );

    setExternalHeads((prev) =>
    hydrateSection(prev)
    );

    setAmenityHeads((prev) =>
    hydrateSection(prev)
    );

    setFinancialHeads((prev) =>
    hydrateSection(prev)
    );

    setMiscHeads((prev) =>
    hydrateSection(prev)
    );


    // ======================================================
    // AMENITIES
    // ======================================================

    setAmenityHeads((prev) =>
      prev.map((head) => {

        if (
          data.amenities_detected
        ) {
          return {
            ...head,

            autoConfigured: true,

            hydrationReason:
              "Amenity infrastructure detected during onboarding",
          };
        }

        return head;
      })
    );

  } catch (error) {

    console.error(
      "SCR30 Hydration Error",
      error
    );

  } finally {

    setLoading(false);

  }
};
  // ==========================================================
  // 🧠 TOGGLE SECTION
  // ==========================================================
  const toggleSection = (
    key: keyof typeof expandedSections
  ) => {
    setExpandedSections((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // ==========================================================
  // 🧠 UPDATE HEAD
  // ==========================================================
  const updateHead = (
    list: RevenueHead[],
    setter: React.Dispatch<
      React.SetStateAction<RevenueHead[]>
    >,
    code: string,
    payload: Partial<RevenueHead>
  ) => {
    setter(
      list.map((head) => {
        if (head.code !== code) {
          return head;
        }

        return {
          ...head,
          ...payload,
        };
      })
    );
  };

  // ==========================================================
  // 🧠 ACTIVE COUNT
  // ==========================================================
  const totalActiveHeads = useMemo(() => {
    return [
      ...internalHeads,
      ...externalHeads,
      ...amenityHeads,
      ...financialHeads,
      ...miscHeads,
    ].filter((head) => head.enabled).length;
  }, [
    internalHeads,
    externalHeads,
    amenityHeads,
    financialHeads,
    miscHeads,
  ]);

  // ==========================================================
  // 🧠 SAVE CONFIGURATION
  // ==========================================================
  const saveConfiguration = async () => {
    try {
      setSaving(true);

      const heads = [

        ...internalHeads,
        ...internalAdvancedHeads,
        ...parkingHeads,
        ...occupancyHeads,
        ...penaltyHeads,
        ...memberServiceHeads,
        ...externalHeads,
        ...amenityHeads,
        ...financialHeads,
        ...miscHeads,

        ]
        .filter((head) => head.enabled)
        .map((head) => ({
        code: head.code,

        name: head.name,

        // ======================================================
        // RECOVERABLES
        // ======================================================

        basis: head.basis || "",

        rate: head.rate || "",

        mandatory:
            head.mandatory || false,

        // ======================================================
        // COMMERCIAL MONETIZATION
        // ======================================================

        revenueModel:
            head.revenueModel || "",

        monthlyValue:
            head.monthlyValue || "",

        agreementExists:
            head.agreementExists || false,

        // ======================================================
        // AMENITIES
        // ======================================================

        accessType:
            head.accessType || "",

        pricingModel:
            head.pricingModel || "",

        usageFee:
            head.usageFee || "",

        // ======================================================
        // TREASURY
        // ======================================================

        instrumentType:
            head.instrumentType || "",

        institution:
            head.institution || "",

        principalValue:
            head.principalValue || "",

        currentValue:
            head.currentValue || "",

        yieldPercent:
            head.yieldPercent || "",

        principalLinked:
            head.principalLinked || false,

        depositDate:
            head.depositDate || "",

        maturityDate:
            head.maturityDate || "",

        renewalMode:
            head.renewalMode || "",

        payoutType:
            head.payoutType || "",

        prematureWithdrawalAllowed:
            head.prematureWithdrawalAllowed || false,

        // ======================================================
        // COMMON
        // ======================================================

        enabled:
            head.enabled || false,
        }));

        const payload = {

        society_id: societyId,

        heads,

        billing: {

            billing_cycle: "MONTHLY",

            due_day: 10,

            grace_days: 5,

            billing_start_date:
            "2026-06-01",

            interest_rules: {
            enabled: true,
            rate: 21,
            },

            penalty_rules: {
            enabled: true,
            amount: 500,
            },
        },

        operational: {

            billing_target: "OWNER",

            vacant_type: "FULL",

            dispute_enabled: true,

            dispute_hold_bill: false,

            dispute_apply_interest: true,
        },
        };

      console.log("SCR30 CONFIGURATION", payload);

      await fetch(
        "http://127.0.0.1:8000/api/society/receivables/save/",
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

      navigate(
        "/financial-onboarding/maintenance-governance"
      );
      
    } catch (error) {
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div style={{ padding: 24 }}>
          Loading revenue configuration...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: 24,
        }}
      >
        {/* ====================================================== */}
        {/* HEADER */}
        {/* ====================================================== */}

        <div style={{ marginBottom: 32 }}>
          <div style={styles.pill}>
            Revenue Governance Layer
          </div>

          <h1 style={styles.title}>
            Revenue & Receivables Setup
          </h1>

          <p style={styles.subtitle}>
            Configure how your society collects
            maintenance, monetizes amenities, and
            manages recurring income sources.
          </p>
        </div>

        {/* ====================================================== */}
        {/* SUMMARY */}
        {/* ====================================================== */}

        <div style={styles.summaryCard}>
          <div>
            <div style={styles.summaryTitle}>
              Intelligent Financial Activation
            </div>

            <div style={styles.summarySubtitle}>
              Existing financial truths have already
              been detected and intelligently activated.
            </div>
          </div>

          <div style={styles.counterCard}>
            <div style={styles.counterValue}>
              {totalActiveHeads}
            </div>

            <div style={styles.counterLabel}>
              Active Revenue Channels
            </div>
          </div>
        </div>

        {/* ====================================================== */}
        {/* INTERNAL */}
        {/* ====================================================== */}

        <SectionCard
        title="Internal Recoveries"
        subtitle="Recurring and operational recoveries from members and occupants."
        expanded={expandedSections.internal}
        activeCount={
            internalHeads.filter((h) => h.enabled).length
        }
        onToggle={() => toggleSection("internal")}
        >
        {internalHeads.map((head) => (
            <RevenueRow
            key={head.code}
            head={head}
            onToggle={() =>
                updateHead(
                internalHeads,
                setInternalHeads,
                head.code,
                {
                    enabled: !head.enabled,
                    customized: true,
                }
                )
            }
            onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    internalHeads,
                    setInternalHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    internalHeads,
                    setInternalHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
           }}
            />
        ))}

        <div style={{ marginTop: 12 }}>
            <button
            onClick={() =>
                setShowAdvancedRecurring(
                !showAdvancedRecurring
                )
            }
            style={{
                border: "none",
                background: "transparent",
                color: "#f97316",
                fontWeight: 700,
                cursor: "pointer",
                padding: 0,
                fontSize: 14,
            }}
            >
            {showAdvancedRecurring
                ? "Hide Additional Revenue Heads"
                : "+ More Revenue Heads"}
            </button>
        </div>

        {showAdvancedRecurring && (
            <div
            style={{
                marginTop: 18,
                display: "grid",
                gap: 16,
            }}
            >
            {internalAdvancedHeads.map((head) => (
                <RevenueRow
                key={head.code}
                head={head}
                onToggle={() =>
                    updateHead(
                    internalAdvancedHeads,
                    setInternalAdvancedHeads,
                    head.code,
                    {
                        enabled: !head.enabled,
                        customized: true,
                    }
                    )
                }
                onNoteChange={(value: string) => {

                    try {

                        const parsed =
                        JSON.parse(value);

                        updateHead(
                        internalAdvancedHeads,
                        setInternalAdvancedHeads,
                        head.code,
                        {
                            [parsed.field]:
                            parsed.value,
                        }
                        );

                    } catch {

                        updateHead(
                        internalAdvancedHeads,
                        setInternalAdvancedHeads,
                        head.code,
                        {
                            notes: value,
                        }
                        );
                    }
                }}
                />
            ))}
            </div>
        )}
        </SectionCard>
        
        {/* ====================================================== */}
        {/* PARKING & MOBILITY */}
        {/* ====================================================== */}

        <SectionCard
        title="Parking & Mobility"
        subtitle="Parking recoveries and mobility-linked operational income."
        expanded={expandedSections.parking}
        activeCount={
            parkingHeads.filter((h) => h.enabled).length
        }
        onToggle={() => toggleSection("parking")}
        >
        {parkingHeads.map((head) => (
            <RevenueRow
            key={head.code}
            head={head}
            onToggle={() =>
                updateHead(
                parkingHeads,
                setParkingHeads,
                head.code,
                {
                    enabled: !head.enabled,
                    customized: true,
                }
                )
            }
            onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    parkingHeads,
                    setParkingHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    parkingHeads,
                    setParkingHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
        ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* OCCUPANCY & COMPLIANCE */}
        {/* ====================================================== */}

        <SectionCard
        title="Occupancy & Compliance"
        subtitle="Operational occupancy and compliance recoveries."
        expanded={expandedSections.occupancy}
        activeCount={
            occupancyHeads.filter((h) => h.enabled).length
        }
        onToggle={() => toggleSection("occupancy")}
        >
        {occupancyHeads.map((head) => (
            <RevenueRow
            key={head.code}
            head={head}
            onToggle={() =>
                updateHead(
                occupancyHeads,
                setOccupancyHeads,
                head.code,
                {
                    enabled: !head.enabled,
                    customized: true,
                }
                )
            }
            onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    occupancyHeads,
                    setOccupancyHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    occupancyHeads,
                    setOccupancyHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
        ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* PENALTIES & RECOVERIES */}
        {/* ====================================================== */}

        <SectionCard
        title="Penalties & Recoveries"
        subtitle="Delayed payment penalties and operational recoveries."
        expanded={expandedSections.penalties}
        activeCount={
            penaltyHeads.filter((h) => h.enabled).length
        }
        onToggle={() => toggleSection("penalties")}
        >
        {penaltyHeads.map((head) => (
            <RevenueRow
            key={head.code}
            head={head}
            onToggle={() =>
                updateHead(
                penaltyHeads,
                setPenaltyHeads,
                head.code,
                {
                    enabled: !head.enabled,
                    customized: true,
                }
                )
            }
            onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    penaltyHeads,
                    setPenaltyHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    penaltyHeads,
                    setPenaltyHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
        ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* TRANSFER & MEMBER SERVICES */}
        {/* ====================================================== */}

        <SectionCard
        title="Transfer & Member Services"
        subtitle="Membership transfer and operational service recoveries."
        expanded={expandedSections.memberServices}
        activeCount={
            memberServiceHeads.filter((h) => h.enabled)
            .length
        }
        onToggle={() =>
            toggleSection("memberServices")
        }
        >
        {memberServiceHeads.map((head) => (
            <RevenueRow
            key={head.code}
            head={head}
            onToggle={() =>
                updateHead(
                memberServiceHeads,
                setMemberServiceHeads,
                head.code,
                {
                    enabled: !head.enabled,
                    customized: true,
                }
                )
            }
            onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    memberServiceHeads,
                    setMemberServiceHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    memberServiceHeads,
                    setMemberServiceHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
        ))}
        </SectionCard>
        {/* ====================================================== */}
        {/* EXTERNAL */}
        {/* ====================================================== */}

        <SectionCard
          title="External Monetization"
          subtitle="Commercial and third-party revenue opportunities."
          headerLabels={{
            grid:
            "minmax(260px, 2fr) 160px 160px 140px 100px",

            labels: [
            "Revenue Head",
            "MODEL",
            "MONTHLY VALUE",
            "AGREEMENT",
            "Status",
            ],
        }}
          expanded={expandedSections.external}
          activeCount={
            externalHeads.filter((h) => h.enabled).length
          }
          onToggle={() => toggleSection("external")}
        >
          {externalHeads.map((head) => (
            <CommercialRevenueRow
              key={head.code}
              head={head}
              onToggle={() =>
                updateHead(
                  externalHeads,
                  setExternalHeads,
                  head.code,
                  {
                    enabled: !head.enabled,
                    customized: true,
                  }
                )
              }
              onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    externalHeads,
                    setExternalHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    externalHeads,
                    setExternalHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
          ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* AMENITIES */}
        {/* ====================================================== */}

        <SectionCard
          title="Amenities & Facilities"
          subtitle="Usage-based and booking-based monetization channels."
          headerLabels={{
            grid:
            "minmax(260px, 2fr) 160px 160px 160px 100px",

            labels: [
            "Revenue Head",
            "ACCESS TYPE",
            "PRICING MODEL",
            "USAGE FEE",
            "Status",
            ],
        }}
          expanded={expandedSections.amenities}
          activeCount={
            amenityHeads.filter((h) => h.enabled).length
          }
          onToggle={() => toggleSection("amenities")}
        >
          {amenityHeads.map((head) => (
            <AmenityRevenueRow
              key={head.code}
              head={head}
              onToggle={() =>
                updateHead(
                  amenityHeads,
                  setAmenityHeads,
                  head.code,
                  {
                    enabled: !head.enabled,
                    customized: true,
                  }
                )
              }
              onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    amenityHeads,
                    setAmenityHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    amenityHeads,
                    setAmenityHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
          ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* FINANCIAL */}
        {/* ====================================================== */}

        <SectionCard
          title="Financial Income"
          subtitle="Treasury and interest-generated income streams."
          headerLabels={{
            grid:
            "minmax(220px, 2fr) 140px 160px 140px 140px 120px 100px",

            labels: [
            "Revenue Head",
            "INSTRUMENT",
            "INSTITUTION",
            "PRINCIPAL",
            "CURRENT",
            "YIELD %",
            "Status",
            ],
        }}
          expanded={expandedSections.financial}
          activeCount={
            financialHeads.filter((h) => h.enabled).length
          }
          onToggle={() => toggleSection("financial")}
        >
          {financialHeads.map((head) => (
            <TreasuryRevenueRow
              key={head.code}
              head={head}
              onToggle={() =>
                updateHead(
                  financialHeads,
                  setFinancialHeads,
                  head.code,
                  {
                    enabled: !head.enabled,
                    customized: true,
                  }
                )
              }
              onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    financialHeads,
                    setFinancialHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    financialHeads,
                    setFinancialHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
          ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* MISC */}
        {/* ====================================================== */}

        <SectionCard
          title="Miscellaneous"
          subtitle="Incidental and non-operational income channels."
          expanded={expandedSections.misc}
          activeCount={
            miscHeads.filter((h) => h.enabled).length
          }
          onToggle={() => toggleSection("misc")}
        >
          {miscHeads.map((head) => (
            <RevenueRow
              key={head.code}
              head={head}
              onToggle={() =>
                updateHead(
                  miscHeads,
                  setMiscHeads,
                  head.code,
                  {
                    enabled: !head.enabled,
                    customized: true,
                  }
                )
              }
              onNoteChange={(value: string) => {

                try {

                    const parsed =
                    JSON.parse(value);

                    updateHead(
                    miscHeads,
                    setMiscHeads,
                    head.code,
                    {
                        [parsed.field]:
                        parsed.value,
                    }
                    );

                } catch {

                    updateHead(
                    miscHeads,
                    setMiscHeads,
                    head.code,
                    {
                        notes: value,
                    }
                    );
                }
            }}
            />
          ))}
        </SectionCard>

        {/* ====================================================== */}
        {/* FOOTER */}
        {/* ====================================================== */}

        <div style={styles.footer}>
          <div>
            <div style={styles.footerTitle}>
              Revenue activation ready.
            </div>

            <div style={styles.footerSubtitle}>
              Active channels will be operationalized
              during maintenance and billing setup.
            </div>
          </div>

          <button
            onClick={saveConfiguration}
            disabled={saving}
            style={styles.saveButton}
          >
            {saving
              ? "Saving Configuration..."
              : "Save & Continue"}
          </button>
        </div>
      </div>
    </AppShell>
  );
}

// ==========================================================
// 🧠 SECTION CARD
// ==========================================================

function SectionCard({
  title,
  subtitle,
  expanded,
  activeCount,
  onToggle,
  children,
  headerLabels,
}: any) {
  return (
    <div style={styles.sectionCard}>
      <div
        style={styles.sectionHeader}
        onClick={onToggle}
      >
        <div>
          <div style={styles.sectionTitle}>
            {title}
          </div>

          <div style={styles.sectionSubtitle}>
            {subtitle}
          </div>
        </div>

        <div style={styles.sectionRight}>
          <div style={styles.activeBadge}>
            {activeCount} Active
          </div>

          <div style={styles.expandIcon}>
            {expanded ? "−" : "+"}
          </div>
        </div>
      </div>

      {expanded && (
        <div style={styles.sectionBody}>

            <div
            style={{
                display: "grid",
                gridTemplateColumns:
                headerLabels?.grid ||
                "minmax(260px, 2fr) 160px 160px 160px 100px",
                gap: 16,
                padding: "0 0 10px 0",
                borderBottom: "1px solid #e5e7eb",
                marginBottom: 8,
            }}
            >
            {(
                headerLabels?.labels || [
                "Revenue Head",
                "BASIS",
                "RATE",
                "MANDATORY",
                "Status",
                ]
            ).map(
                (
                label: string,
                index: number
                ) => (
                <div
                    key={label}
                    style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#9ca3af",
                    textTransform: "uppercase",
                    textAlign:
                        index ===
                        (
                        headerLabels?.labels ||
                        []
                        ).length - 1
                        ? "right"
                        : "left",
                    }}
                >
                    {label}
                </div>
                )
            )}
            </div>

            {children}
        </div>
        )}
    </div>
  );
}

// ==========================================================
// 🧠 REVENUE ROW
// ==========================================================

function RevenueRow({
  head,
  onToggle,
  onNoteChange,
}: RevenueRowProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "minmax(260px, 2fr) 160px 160px 160px 100px",
        gap: 16,
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      {/* HEAD */}
      <div>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#111827",
            marginBottom: 4,
          }}
        >
          {head.name}
        </div>

        {head.hydrationReason && (
          <div
            style={{
              fontSize: 11,
              color: "#f97316",
              fontWeight: 600,
            }}
          >
            {head.hydrationReason}
          </div>
        )}
      </div>

      {/* BASIS */}
        <div>
        <select
            value={head.basis || ""}
            onChange={(e) =>
            onNoteChange(
                JSON.stringify({
                field: "basis",
                value: e.target.value,
                })
            )
            }
            style={styles.matrixSelect}
        >
            <option value="">
            Select
            </option>

            <option value="EQUAL">
            Equal
            </option>

            <option value="AREA">
            Area
            </option>

            <option value="PER_UNIT">
            Per Unit
            </option>

            <option value="PER_SLOT">
            Per Slot
            </option>

            <option value="PERCENT">
            Percent
            </option>
        </select>
        </div>

        {/* RATE */}
        <div>
        <input
            value={head.rate || ""}
            onChange={(e) =>
                onNoteChange(
                JSON.stringify({
                    field: "rate",
                    value: e.target.value.replace(
                        /[^0-9.]/g,
                        ""
                    ),
                })
                )
            }
            placeholder="Enter"
            style={styles.matrixInput}
        />
        </div>

        {/* MANDATORY */}
        <div>
        <select
            value={
                head.mandatory
                ? "YES"
                : "NO"
            }
            onChange={(e) =>
                onNoteChange(
                JSON.stringify({
                    field: "mandatory",
                    value:
                    e.target.value ===
                    "YES",
                })
                )
            }
            style={styles.matrixSelect}
            >
            <option value="YES">
            Yes
            </option>

            <option value="NO">
            No
            </option>
        </select>
        </div>
      
      {/* ENABLE */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <button
          onClick={onToggle}
          style={{
            border: "none",
            borderRadius: 999,
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 12,
            padding: "8px 14px",
            minWidth: 74,
            background: head.enabled
              ? "#f97316"
              : "#e5e7eb",
            color: head.enabled
              ? "#fff"
              : "#374151",
          }}
        >
          {head.enabled ? "ON" : "OFF"}
        </button>
      </div>
    </div>
  );
}
// ==========================================================
// 🧠 COMMERCIAL REVENUE ROW
// ==========================================================

function CommercialRevenueRow({
  head,
  onToggle,
  onNoteChange,
}: RevenueRowProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "minmax(260px, 2fr) 160px 160px 140px 100px",
        gap: 16,
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      {/* HEAD */}
      <div>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#111827",
            marginBottom: 4,
          }}
        >
          {head.name}
        </div>

        {head.hydrationReason && (
          <div
            style={{
              fontSize: 11,
              color: "#f97316",
              fontWeight: 600,
            }}
          >
            {head.hydrationReason}
          </div>
        )}
      </div>

      {/* REVENUE MODEL */}
      <select
        value={head.revenueModel || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "revenueModel",
              value: e.target.value,
            })
          )
        }
        style={styles.matrixSelect}
      >
        <option value="">
          Select
        </option>

        <option value="LEASE">
          Lease
        </option>

        <option value="FIXED">
          Fixed Revenue
        </option>

        <option value="REV_SHARE">
          Revenue Share
        </option>
      </select>

      {/* MONTHLY VALUE */}
      <input
        type="number"
        value={head.monthlyValue || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "monthlyValue",
              value: e.target.value.replace(
                /[^0-9.]/g,
                ""
              ),
            })
          )
        }
        placeholder="Amount"
        style={styles.matrixInput}
      />

      {/* AGREEMENT */}
      <select
        value={
          head.agreementExists
            ? "YES"
            : "NO"
        }
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "agreementExists",
              value:
                e.target.value ===
                "YES",
            })
          )
        }
        style={styles.matrixInput}
      >
        <option value="YES">
          Yes
        </option>

        <option value="NO">
          No
        </option>
      </select>

      {/* ENABLE */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <button
          onClick={onToggle}
          style={{
            border: "none",
            borderRadius: 999,
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 12,
            padding: "8px 14px",
            minWidth: 74,
            background: head.enabled
              ? "#f97316"
              : "#e5e7eb",
            color: head.enabled
              ? "#fff"
              : "#374151",
          }}
        >
          {head.enabled ? "ON" : "OFF"}
        </button>
      </div>
    </div>
  );
}

// ==========================================================
// 🧠 AMENITY REVENUE ROW
// ==========================================================

function AmenityRevenueRow({
  head,
  onToggle,
  onNoteChange,
}: RevenueRowProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "minmax(260px, 2fr) 160px 160px 160px 100px",
        gap: 16,
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      {/* HEAD */}
      <div>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#111827",
            marginBottom: 4,
          }}
        >
          {head.name}
        </div>

        {head.hydrationReason && (
          <div
            style={{
              fontSize: 11,
              color: "#f97316",
              fontWeight: 600,
            }}
          >
            {head.hydrationReason}
          </div>
        )}
      </div>

      {/* ACCESS TYPE */}
      <select
        value={head.accessType || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "accessType",
              value: e.target.value,
            })
          )
        }
        style={styles.matrixSelect}
      >
        <option value="">
          Select
        </option>

        <option value="SUBSCRIPTION">
          Subscription
        </option>

        <option value="BOOKING">
          Booking
        </option>

        <option value="DEPOSIT">
          Deposit
        </option>
      </select>

      {/* PRICING MODEL */}
      <select
        value={head.pricingModel || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "pricingModel",
              value: e.target.value,
            })
          )
        }
        style={styles.matrixSelect}
      >
        <option value="">
          Select
        </option>

        <option value="MONTHLY">
          Monthly
        </option>

        <option value="PER_HOUR">
          Per Hour
        </option>

        <option value="PER_BOOKING">
          Per Booking
        </option>
      </select>

      {/* USAGE FEE */}
      <input
        type="number"
        value={head.usageFee || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "usageFee",
              value: e.target.value.replace(
                /[^0-9.]/g,
                ""
              ),
            })
          )
        }
        placeholder="Amount"
        style={styles.matrixInput}
      />

      {/* ENABLE */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <button
          onClick={onToggle}
          style={{
            border: "none",
            borderRadius: 999,
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 12,
            padding: "8px 14px",
            minWidth: 74,
            background: head.enabled
              ? "#f97316"
              : "#e5e7eb",
            color: head.enabled
              ? "#fff"
              : "#374151",
          }}
        >
          {head.enabled ? "ON" : "OFF"}
        </button>
      </div>
    </div>
  );
}
// ==========================================================
// 🧠 TREASURY REVENUE ROW
// ==========================================================

function TreasuryRevenueRow({
  head,
  onToggle,
  onNoteChange,
}: RevenueRowProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "minmax(220px, 2fr) 140px 160px 140px 140px 120px 100px",
        gap: 12,
        alignItems: "center",
        padding: "14px 0",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      {/* HEAD */}
      <div>
        <div
          style={{
            fontSize: 14,
            fontWeight: 700,
            color: "#111827",
            marginBottom: 4,
          }}
        >
          {head.name}
        </div>

        {head.hydrationReason && (
          <div
            style={{
              fontSize: 11,
              color: "#f97316",
              fontWeight: 600,
            }}
          >
            {head.hydrationReason}
          </div>
        )}
      </div>

      {/* INSTRUMENT TYPE */}
      <select
        value={head.instrumentType || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "instrumentType",
              value: e.target.value,
            })
          )
        }
        style={styles.matrixSelect}
      >
        <option value="">
          Select
        </option>

        <option value="FD">
          Fixed Deposit
        </option>

        <option value="SAVINGS">
          Savings
        </option>

        <option value="LIQUID_FUND">
          Liquid Fund
        </option>
      </select>

      {/* INSTITUTION */}
      <input
        value={head.institution || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "institution",
              value: e.target.value,
            })
          )
        }
        placeholder="Institution"
        style={styles.matrixInput}
      />

      {/* PRINCIPAL */}
      <input
        type="number"
        value={head.principalValue || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "principalValue",
              value: e.target.value.replace(
                /[^0-9.]/g,
                ""
              ),
            })
          )
        }
        placeholder="Principal"
        style={styles.matrixInput}
      />

      {/* CURRENT VALUE */}
      <input
        type="number"
        value={head.currentValue || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "currentValue",
              value: e.target.value.replace(
                /[^0-9.]/g,
                ""
              ),
            })
          )
        }
        placeholder="Current"
        style={styles.matrixInput}
      />

      {/* YIELD */}
      <input
        type="number"
        value={head.yieldPercent || ""}
        onChange={(e) =>
          onNoteChange(
            JSON.stringify({
              field: "yieldPercent",
              value: e.target.value.replace(
                /[^0-9.]/g,
                ""
              ),
            })
          )
        }
        placeholder="Yield %"
        style={styles.matrixInput}
      />

      {/* ENABLE */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
        }}
      >
        <button
          onClick={onToggle}
          style={{
            border: "none",
            borderRadius: 999,
            cursor: "pointer",
            fontWeight: 700,
            fontSize: 12,
            padding: "8px 14px",
            minWidth: 74,
            background: head.enabled
              ? "#f97316"
              : "#e5e7eb",
            color: head.enabled
              ? "#fff"
              : "#374151",
          }}
        >
          {head.enabled ? "ON" : "OFF"}
        </button>
      </div>
    </div>
  );
}
// ==========================================================
// 🧠 STYLES
// ==========================================================

const styles: any = {
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
    maxWidth: 920,
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
    marginBottom: 22,
    overflow: "hidden",
  },

  sectionHeader: {
    padding: 24,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 20,
    cursor: "pointer",
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: 700,
    color: "#111827",
    marginBottom: 6,
  },

  sectionSubtitle: {
    fontSize: 14,
    lineHeight: 1.6,
    color: "#6b7280",
  },

  sectionRight: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },

  activeBadge: {
    padding: "8px 12px",
    borderRadius: 999,
    background: "#f3f4f6",
    fontSize: 12,
    fontWeight: 700,
    color: "#374151",
  },

  expandIcon: {
    fontSize: 20,
    color: "#6b7280",
  },

  sectionBody: {
    padding: "0 24px 24px 24px",
    display: "grid",
    gap: 16,
  },
  
  matrixCell: {
    fontSize: 13,
    fontWeight: 600,
    color: "#374151",
    },
  matrixInput: {
    width: "100%",
    border: "1px solid #d1d5db",
    borderRadius: 8,
    padding: "8px 10px",
    fontSize: 13,
    outline: "none",
    boxSizing: "border-box",
    },

  matrixSelect: {
    width: "100%",
    border: "1px solid #d1d5db",
    borderRadius: 8,
    padding: "8px 10px",
    fontSize: 13,
    outline: "none",
    background: "#ffffff",
    },

    rowCard: {
    borderRadius: 18,
    padding: 20,
  },

  rowHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: 20,
    flexWrap: "wrap",
  },

  rowTitleWrap: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    flexWrap: "wrap",
    marginBottom: 8,
  },

  rowTitle: {
    fontSize: 17,
    fontWeight: 700,
    color: "#111827",
  },

  autoConfigured: {
    padding: "4px 10px",
    borderRadius: 999,
    background: "#dcfce7",
    color: "#166534",
    fontSize: 11,
    fontWeight: 700,
  },

  rowHelper: {
    fontSize: 14,
    lineHeight: 1.6,
    color: "#6b7280",
    marginBottom: 14,
  },

  hydrationBadge: {
    display: "inline-flex",
    padding: "6px 10px",
    borderRadius: 999,
    background: "#f3f4f6",
    color: "#4b5563",
    fontSize: 12,
    marginBottom: 12,
  },

  tagContainer: {
    display: "flex",
    gap: 10,
    flexWrap: "wrap",
    marginBottom: 14,
  },

  tag: {
    padding: "6px 12px",
    borderRadius: 999,
    background: "#f9fafb",
    border: "1px solid #e5e7eb",
    fontSize: 12,
    fontWeight: 600,
    color: "#4b5563",
  },

  customizedTag: {
    padding: "6px 12px",
    borderRadius: 999,
    background: "#fff7ed",
    border: "1px solid #fed7aa",
    fontSize: 12,
    fontWeight: 600,
    color: "#ea580c",
  },

  textarea: {
    width: "100%",
    borderRadius: 12,
    border: "1px solid #d1d5db",
    padding: 12,
    fontSize: 14,
    resize: "vertical",
    outline: "none",
    boxSizing: "border-box",
  },

  toggleButton: {
    minWidth: 96,
    padding: "10px 14px",
    borderRadius: 999,
    border: "none",
    fontWeight: 700,
    fontSize: 12,
    cursor: "pointer",
    height: 42,
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
