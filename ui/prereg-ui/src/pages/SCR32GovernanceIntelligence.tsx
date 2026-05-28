import React, {
  useEffect,
  useState,
} from "react";

import { useNavigate } from "react-router-dom";

import AppShell from "../components/layout/AppShell";

/* =====================================================
   TYPES
===================================================== */

type GovernanceForm = {

  billing_cycle: string;

  bill_generation_day: string;

  payable_within_days: string;

  due_within_days: string;

  penalty_enabled: boolean;

  penalty_amount: string;

  penalty_after_days: string;

  interest_enabled: boolean;

  interest_rate: string;

  auto_penalty: boolean;

  auto_interest: boolean;

  non_occupancy_enabled: boolean;

  non_occupancy_basis: string;

  non_occupancy_rate: string;

  parking_enabled: boolean;

  parking_basis: string;

  billing_mode: string;

  penalty_type: string;

  interest_type: string;

  water_basis: string;

  common_electricity_basis: string;

  tanker_basis: string;

  service_charge_basis: string;

  sinking_fund_basis: string;

  repairs_basis: string;

  insurance_basis: string;

  parking_rate: string;
  
  four_wheeler_rate: string;

  two_wheeler_rate: string;

  ev_vehicle_rate: string;

  visitor_parking_rate: string;

  service_charge_rate: string;

  sinking_fund_rate: string;

  repairs_rate: string;

  insurance_rate: string;

  water_rate: string;

  common_electricity_rate: string;

  auto_apply_non_occupancy: boolean;

  parking_matrix: any[];

};

/* =====================================================
   COMPONENT
===================================================== */

export default function SCR32GovernanceIntelligence() {

  const navigate = useNavigate();

  const societyId =
    localStorage.getItem("society_id");

  const [loading, setLoading] =
    useState(false);

  const [
    expandedWings,
    setExpandedWings,
  ] = useState<any>({
    A: true,
  });

  const [
    savingWing,
    setSavingWing,
  ] = useState<string | null>(
    null
  );

  const [hydrating, setHydrating] =
    useState(true);

  const [form, setForm] =
    useState<GovernanceForm>({

      billing_cycle: "MONTHLY",

      bill_generation_day: "1",

      payable_within_days: "3",

      due_within_days: "15",

      penalty_enabled: true,

      penalty_amount: "500",

      penalty_after_days: "30",

      interest_enabled: true,

      interest_rate: "21",

      auto_penalty: true,

      auto_interest: true,

      non_occupancy_enabled: true,

      non_occupancy_basis:
        "PERCENT_MAINT",

      non_occupancy_rate: "10",

      parking_enabled: false,

      parking_basis: "PER_SLOT",

      billing_mode: "ADVANCE",

      penalty_type: "FLAT",

      interest_type: "SIMPLE",

      water_basis: "EQUAL",

      common_electricity_basis:
        "EQUAL",

      service_charge_rate: "2500",

      sinking_fund_rate: "1",

      repairs_rate: "2",

      insurance_rate: "0.2",

      water_rate: "500",

      common_electricity_rate: "300",

      tanker_basis: "EQUAL",

      service_charge_basis:
        "EQUAL",

      sinking_fund_basis:
        "AREA",

      repairs_basis: "AREA",

      insurance_basis: "AREA",

      parking_rate: "0",

      four_wheeler_rate: "0",

      two_wheeler_rate: "0",

      ev_vehicle_rate: "0",

      visitor_parking_rate: "0",

      auto_apply_non_occupancy:
        true,

      parking_matrix: [],

    });

  /* =====================================================
     HYDRATE
  ===================================================== */

  useEffect(() => {

    const hydrate =
      async () => {

        try {

          const response =
            await fetch(
              `/api/society/scr31-context/?society_id=${societyId}`
            );

          const data =
            await response.json();

          const governance =
            data?.governance || {};

          const maintenanceHeads =
            data?.maintenance_heads || [];

          const headMap =
            Object.fromEntries(

                maintenanceHeads.map(
                    (head: any) => [

                        head.code,

                        head,
                    ]
                )
            );

          const hydratedFlats =
            (
                data?.occupancy_selection || []
            ).map(
                (flat: any) => ({

                flat_id:
                    flat.flat_id,

                flat_number:
                    flat.flat_number,

                wing:
                    flat.wing,

                four_wheeler: 0,

                two_wheeler: 0,

                ev_vehicle: 0,

                visitor: 0,

                value: 0,
                })
            );

          setForm({

            billing_cycle:
              governance
                ?.billing_cycle ||
              "MONTHLY",

            bill_generation_day:
              String(
                governance
                  ?.bill_generation_day ||
                  1
              ),

            payable_within_days:
              String(
                governance
                  ?.payable_within_days ||
                  3
              ),

            due_within_days:
              String(
                governance
                  ?.due_within_days ||
                  15
              ),

            penalty_enabled:
              governance
                ?.penalty_rules
                ?.enabled ?? true,

            penalty_amount:
              String(
                governance
                  ?.penalty_rules
                  ?.amount ||
                  500
              ),

            penalty_after_days:
              String(
                governance
                  ?.penalty_rules
                  ?.after_days ||
                  30
              ),

            interest_enabled:
              governance
                ?.interest_rules
                ?.enabled ?? true,

            interest_rate:
              String(
                governance
                  ?.interest_rules
                  ?.rate ||
                  21
              ),

            auto_penalty:
              governance
                ?.auto_penalty ??
              true,

            auto_interest:
              governance
                ?.auto_interest ??
              true,

            non_occupancy_enabled:
              governance
                ?.non_occupancy_enabled ??
              true,

            non_occupancy_basis:
              governance
                ?.non_occupancy_basis ||
              "PERCENT_MAINT",

            non_occupancy_rate:
              String(
                governance
                  ?.non_occupancy_rate ||
                  10
              ),

            parking_enabled:
              governance
                ?.parking_enabled ??
              false,

            parking_basis:
              governance
                ?.parking_basis ||
              "PER_SLOT",

            billing_mode:
                governance?.billing_mode ||
                "ADVANCE",

            penalty_type:
                governance?.penalty_rules
                    ?.type || "FLAT",

            interest_type:
                governance?.interest_rules
                    ?.type || "SIMPLE",

            water_basis:
                governance?.water_basis ||
                    "EQUAL",


            common_electricity_basis:
            governance
                ?.common_electricity_basis ||
            "EQUAL",
            
            service_charge_rate:
                String(

                    headMap[
                        "SERVICE_CHARGES"
                    ]?.rate ??

                    2500
                ),

                sinking_fund_rate:
                    String(

                        headMap[
                            "SINKING_FUND"
                        ]?.rate ??

                        1
                    ),

                repairs_rate:
                    String(

                        headMap[
                            "REPAIRS_MAINTENANCE"
                        ]?.rate ??

                        2
                    ),

                insurance_rate:
                    String(

                        headMap[
                            "BUILDING_INSURANCE"
                        ]?.rate ??

                        0.2
                    ),

                water_rate:
                    String(

                        headMap[
                            "WATER_CHARGES"
                        ]?.rate ??

                        500
                    ),

                common_electricity_rate:
                    String(

                        headMap[
                            "COMMON_ELECTRICITY"
                        ]?.rate ??

                        300
                    ),

            tanker_basis:
            governance?.tanker_basis ||
            "EQUAL",

            service_charge_basis:
            governance
                ?.service_charge_basis ||
            "EQUAL",

            sinking_fund_basis:
            governance
                ?.sinking_fund_basis ||
            "AREA",

            repairs_basis:
            governance?.repairs_basis ||
            "AREA",

            insurance_basis:
            governance
                ?.insurance_basis ||
            "AREA",

            parking_rate:
                String(
                    governance?.parking?.rate ||
                    0
                ),
            four_wheeler_rate:
                String(
                    governance
                    ?.four_wheeler_rate ||
                    0
            ),

                two_wheeler_rate:
                String(
                    governance
                    ?.two_wheeler_rate ||
                    0
            ),

                ev_vehicle_rate:
                String(
                    governance
                    ?.ev_vehicle_rate ||
                    0
            ),

                visitor_parking_rate:
                String(
                    governance
                    ?.visitor_parking_rate ||
                    0
            ),

            auto_apply_non_occupancy:
            governance
                ?.auto_apply_non_occupancy ??
            true,

            parking_matrix:
                hydratedFlats,

          });

        } catch (e) {

          console.error(e);

        } finally {

          setHydrating(false);

        }
      };

    hydrate();

  }, [societyId]);

  /* =====================================================
     SET VALUE
  ===================================================== */

  const setValue = (
    key: keyof GovernanceForm,
    value: any
  ) => {

    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  /* =====================================================
     SAVE
  ===================================================== */
  const groupedParkingMatrix =
  form.parking_matrix.reduce(

    (
      acc: any,
      row: any
    ) => {

      const wing =
        row.wing || "Unknown";

      if (!acc[wing]) {

        acc[wing] = [];
      }

      acc[wing].push(row);

      return acc;

    },

    {}
  );

  const updateParkingCell = (
    flatId: number,
    key: string,
    value: string
    ) => {

    const updated =
        form.parking_matrix.map(
        (row: any) => {

            if (
            row.flat_id !== flatId
            ) {
            return row;
            }

            const next = {

            ...row,

            [key]:
                Number(value) || 0,
            };

            const total =

            (
                next.four_wheeler *
                Number(
                form.four_wheeler_rate
                )
            )

            +

            (
                next.two_wheeler *
                Number(
                form.two_wheeler_rate
                )
            )

            +

            (
                next.ev_vehicle *
                Number(
                form.ev_vehicle_rate
                )
            )

            +

            (
                next.visitor *
                Number(
                form
                    .visitor_parking_rate
                )
            );

            next.value = total;

            return next;
        }
        );

    setValue(
        "parking_matrix",
        updated
    );
    };
  
    const saveWing = async (
        wing: string
    ) => {

        try {

            setSavingWing(wing);

            const wingRows =

            groupedParkingMatrix[
                wing
            ] || [];

            console.log(
            "SAVE WING",
            wing,
            wingRows
            );

            await new Promise(
            (resolve) =>
                setTimeout(
                resolve,
                800
                )
            );

            alert(
            `Wing ${wing} saved successfully`
            );

    } catch (e) {

            console.error(e);

            alert(
            `Failed to save Wing ${wing}`
            );

        } finally {

            setSavingWing(null);

        }
    };
  
    const saveGovernance =
    async () => {

      try {

        setLoading(true);

        console.log(
            "PARKING MATRIX",
            form.parking_matrix
        );
        
        const payload = {

          society_id: societyId,

          heads: [],

          occupancy_updates: [],
          
          parking_matrix:
            form.parking_matrix,
          
        governance: {

            billing_cycle:
              form.billing_cycle,

            bill_generation_day:
              Number(
                form.bill_generation_day
              ),

            payable_within_days:
              Number(
                form
                  .payable_within_days
              ),

            due_within_days:
              Number(
                form.due_within_days
              ),

            interest_rules: {

              enabled:
                form.interest_enabled,

              rate: Number(
                form.interest_rate
              ),
            },

            penalty_rules: {

              enabled:
                form.penalty_enabled,

              amount: Number(
                form.penalty_amount
              ),

              after_days:
                Number(
                  form
                    .penalty_after_days
                ),
            },

            auto_penalty:
              form.auto_penalty,

            auto_interest:
              form.auto_interest,

            non_occupancy_enabled:
              form
                .non_occupancy_enabled,

            non_occupancy_basis:
              form
                .non_occupancy_basis,

            non_occupancy_rate:
              Number(
                form
                  .non_occupancy_rate
              ),

            parking_enabled:
              form.parking_enabled,

            parking_basis:
              form.parking_basis,
            
            billing_mode:
                form.billing_mode,

            penalty_type:
                form.penalty_type,

            interest_type:
                form.interest_type,

            water_basis:
                form.water_basis,

            common_electricity_basis:
                form.common_electricity_basis,

            service_charge_rate:
                Number(
                    form.service_charge_rate
            ),

            sinking_fund_rate:
                Number(
                    form.sinking_fund_rate
            ),

            repairs_rate:
                Number(
                    form.repairs_rate
            ),

            insurance_rate:
                Number(
                    form.insurance_rate
            ),

            water_rate:
                Number(
                    form.water_rate
            ),

            common_electricity_rate:
                Number(
                    form.common_electricity_rate
            ),

            tanker_basis:
                form.tanker_basis,

            service_charge_basis:
                form.service_charge_basis,

            sinking_fund_basis:
                form.sinking_fund_basis,

            repairs_basis:
                form.repairs_basis,

            insurance_basis:
                form.insurance_basis,

            parking_rate:
                Number(form.parking_rate),

            four_wheeler_rate:
                Number(
                    form.four_wheeler_rate
            ),

                two_wheeler_rate:
                Number(
                    form.two_wheeler_rate
            ),

                ev_vehicle_rate:
                Number(
                    form.ev_vehicle_rate
            ),

                visitor_parking_rate:
                Number(
                    form.visitor_parking_rate
            ),

            auto_apply_non_occupancy:
                form.auto_apply_non_occupancy,
          },
        };

        console.log(
          "SCR32 SAVE",
          payload
        );

        const response =
          await fetch(
            "/api/society/scr31-save/",
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

        const data =
          await response.json();

        console.log(data);

        if (!response.ok) {

          throw new Error(
            data?.message ||
            "Failed to save governance"
          );
        }

        alert(
          "Governance finalized successfully"
        );

        navigate(
            "/financial-onboarding/scr33"
        );
        
      } catch (e: any) {

        console.error(e);

        alert(
          e.message ||
          "Failed to save governance"
        );

      } finally {

        setLoading(false);

      }
    };

  /* =====================================================
     LOADING
  ===================================================== */

  if (hydrating) {

    return (
      <AppShell>
        <div style={styles.loading}>
          Hydrating Governance Intelligence...
        </div>
      </AppShell>
    );
  }

  /* =====================================================
     UI
  ===================================================== */

  return (
    <AppShell>

      <div style={styles.container}>

        {/* HEADER */}

        <div style={styles.headerCard}>

          <div style={styles.pageTitle}>
            Governance Intelligence
          </div>

          <div style={styles.pageSubtitle}>
            Let us understand how your
            society intends to govern
            maintenance billing,
            recoveries and financial
            discipline.
          </div>

        </div>

        {/* QUESTIONS */}
        
        <GovernanceQuestion
            question="Should bills be generated in advance or arrears?"
            guidance="Most societies generate maintenance bills in advance."
            >

            <select
                value={form.billing_mode}
                onChange={(e) =>
                setValue(
                    "billing_mode",
                    e.target.value
                )
                }
                style={styles.select}
            >
                <option value="ADVANCE">
                Advance
                </option>

                <option value="ARREARS">
                Arrears
                </option>

            </select>

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Maintenance Bill to be generated every"
          guidance="Best practice dictates monthly billing."
        >
          <select
            value={
              form.billing_cycle
            }
            onChange={(e) =>
              setValue(
                "billing_cycle",
                e.target.value
              )
            }
            style={styles.select}
          >
            <option value="MONTHLY">
              Monthly
            </option>

            <option value="QUARTERLY">
              Quarterly
            </option>

            <option value="ANNUAL">
              Annual
            </option>

          </select>

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Maintenance bill shall be generated which day of the month"
          guidance="Best practice is 1st of every month."
        >

          <input
            value={
              form.bill_generation_day
            }
            onChange={(e) =>
              setValue(
                "bill_generation_day",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Maintenance bill shall become payable within how many days"
          guidance="Typically within 3 working days from bill generation."
        >

          <input
            value={
              form.payable_within_days
            }
            onChange={(e) =>
              setValue(
                "payable_within_days",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Maintenance Bill MUST be paid within how many days"
          guidance="Generally within 15 working days from the date of generation."
        >

          <input
            value={
              form.due_within_days
            }
            onChange={(e) =>
              setValue(
                "due_within_days",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="If unpaid, does the society levy penalty?"
          guidance="Generally societies do levy penalties."
        >

          <Toggle
            checked={
              form.penalty_enabled
            }
            onChange={(v) =>
              setValue(
                "penalty_enabled",
                v
              )
            }
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="What is the penalty levied for delay"
          guidance="Penalty may be a fixed operational charge."
        >

          <input
            value={
              form.penalty_amount
            }
            onChange={(e) =>
              setValue(
                "penalty_amount",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>
        <GovernanceQuestion
            question="How should penalty be calculated?"
            guidance="Most societies levy flat operational penalties."
            >

            <select
                value={form.penalty_type}
                onChange={(e) =>
                setValue(
                    "penalty_type",
                    e.target.value
                )
                }
                style={styles.select}
            >
                <option value="FLAT">
                Flat Amount
                </option>

                <option value="PERCENT">
                Percentage
                </option>

            </select>

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Penalty is levied after how many days of delay?"
          guidance="Generally 1 month from bill generation."
        >

          <input
            value={
              form.penalty_after_days
            }
            onChange={(e) =>
              setValue(
                "penalty_after_days",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Does Society levy Interest on delayed payments?"
          guidance="Generally societies levy interest for unreasonable delays."
        >

          <Toggle
            checked={
              form.interest_enabled
            }
            onChange={(v) =>
              setValue(
                "interest_enabled",
                v
              )
            }
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="What is the rate of interest levied?"
          guidance="Many societies levy 21% annual simple interest."
        >

          <input
            value={
              form.interest_rate
            }
            onChange={(e) =>
              setValue(
                "interest_rate",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>
        <GovernanceQuestion
            question="How should interest be calculated?"
            guidance="Most societies levy simple annual interest."
            >

            <select
                value={form.interest_type}
                onChange={(e) =>
                setValue(
                    "interest_type",
                    e.target.value
                )
                }
                style={styles.select}
            >
                <option value="SIMPLE">
                Simple Interest
                </option>

                <option value="COMPOUND">
                Compound Interest
                </option>

            </select>

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Do you want system to calculate penalties automatically every month of delay?"
          guidance="The platform can automate penalty calculations for operational consistency."
        >

          <Toggle
            checked={
              form.auto_penalty
            }
            onChange={(v) =>
              setValue(
                "auto_penalty",
                v
              )
            }
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="Do you want system to calculate interest automatically every month of delay?"
          guidance="The platform can automatically compute interest on overdue receivables."
        >

          <Toggle
            checked={
              form.auto_interest
            }
            onChange={(v) =>
              setValue(
                "auto_interest",
                v
              )
            }
          />

        </GovernanceQuestion>

        {/* NON OCCUPANCY */}

        <div style={styles.sectionDivider}>
          Non Occupancy Governance
        </div>

        <GovernanceQuestion
          question="Should non occupancy charges apply to rented flats?"
          guidance="Societies commonly levy non occupancy charges on tenant occupied homes."
        >

          <Toggle
            checked={
              form
                .non_occupancy_enabled
            }
            onChange={(v) =>
              setValue(
                "non_occupancy_enabled",
                v
              )
            }
          />

        </GovernanceQuestion>

        <GovernanceQuestion
          question="What basis should be used for non occupancy recovery?"
          guidance="Most societies recover non occupancy charges as a percentage of maintenance."
        >

          <select
            value={
              form
                .non_occupancy_basis
            }
            onChange={(e) =>
              setValue(
                "non_occupancy_basis",
                e.target.value
              )
            }
            style={styles.select}
          >
            <option value="PERCENT_MAINT">
              % Maintenance
            </option>

            <option value="FIXED_FLAT">
              Fixed Per Flat
            </option>

          </select>

        </GovernanceQuestion>

        <GovernanceQuestion
          question="What rate should apply for non occupancy charges?"
          guidance="Many societies recover 10% of maintenance as non occupancy recovery."
        >

          <input
            value={
              form
                .non_occupancy_rate
            }
            onChange={(e) =>
              setValue(
                "non_occupancy_rate",
                e.target.value
              )
            }
            style={styles.input}
          />

        </GovernanceQuestion>

        {/* PARKING */}
        <div style={styles.sectionDivider}>
            Billing Intelligence Defaults
            </div>

            <GovernanceQuestion
            question="How should Service Charges be distributed?"
            guidance="Most societies distribute service charges equally."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={form.service_charge_basis}
                    onChange={(e) =>
                    setValue(
                        "service_charge_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="EQUAL">
                    Equal
                    </option>

                    <option value="AREA">
                    Area
                    </option>

                </select>

                <div
                    style={{
                        width: 220,
                    }}
                    >

                    <input
                        type="number"

                        value={
                        form.service_charge_rate
                        }

                        onChange={(e) =>
                        setValue(
                            "service_charge_rate",
                            e.target.value
                        )
                        }

                        placeholder={
                            form.service_charge_basis ===
                            "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                        }
                        
                        style={{
                        ...styles.input,
                        width: "100%",
                        }}
                    />
                    </div>

                </div>

            </GovernanceQuestion>

            <GovernanceQuestion
            question="How should Sinking Fund be distributed?"
            guidance="Sinking fund is generally area based."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={form.sinking_fund_basis}
                    onChange={(e) =>
                    setValue(
                        "sinking_fund_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="AREA">
                    Area
                    </option>

                    <option value="EQUAL">
                    Equal
                    </option>

                </select>

                <input
                    type="number"

                    value={
                    form.sinking_fund_rate
                    }

                    onChange={(e) =>
                    setValue(
                        "sinking_fund_rate",
                        e.target.value
                    )
                    }

                    placeholder={
                        form.sinking_fund_basis ===
                        "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                    }

                    style={{
                    ...styles.input,
                    width: 180,
                    }}
                />

                </div>

            </GovernanceQuestion>

            <GovernanceQuestion
            question="How should Repairs & Maintenance be distributed?"
            guidance="Repairs are commonly recovered based on area."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={form.repairs_basis}
                    onChange={(e) =>
                    setValue(
                        "repairs_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="AREA">
                    Area
                    </option>

                    <option value="EQUAL">
                    Equal
                    </option>

                </select>

                <input
                    type="number"

                    value={
                    form.repairs_rate
                    }

                    onChange={(e) =>
                    setValue(
                        "repairs_rate",
                        e.target.value
                    )
                    }

                    placeholder={
                        form.repairs_basis ===
                        "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                    }

                    style={{
                    ...styles.input,
                    width: 180,
                    }}
                />

                </div>

            </GovernanceQuestion>

            <GovernanceQuestion
            question="How should Building Insurance recovery be distributed?"
            guidance="Insurance recoveries are usually linked to area."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={form.insurance_basis}
                    onChange={(e) =>
                    setValue(
                        "insurance_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="AREA">
                    Area
                    </option>

                    <option value="EQUAL">
                    Equal
                    </option>

                </select>

                <input
                    type="number"

                    value={
                    form.insurance_rate
                    }

                    onChange={(e) =>
                    setValue(
                        "insurance_rate",
                        e.target.value
                    )
                    }

                    placeholder={
                        form.insurance_basis ===
                        "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                    }

                    style={{
                    ...styles.input,
                    width: 180,
                    }}
                />

                </div>

        </GovernanceQuestion>
        
        <div style={styles.sectionDivider}>
            Utility Governance
            </div>

            <GovernanceQuestion
            question="How should water charges be distributed?"
            guidance="Many societies distribute water equally."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={form.water_basis}
                    onChange={(e) =>
                    setValue(
                        "water_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="EQUAL">
                    Equal
                    </option>

                    <option value="AREA">
                    Area
                    </option>

                </select>

                <input
                    type="number"

                    value={
                    form.water_rate
                    }

                    onChange={(e) =>
                    setValue(
                        "water_rate",
                        e.target.value
                    )
                    }

                    placeholder={
                        form.water_basis ===
                        "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                    }

                    style={{
                    ...styles.input,
                    width: 180,
                    }}
                />

                </div>

            </GovernanceQuestion>

            <GovernanceQuestion
            question="How should common electricity charges be distributed?"
            guidance="Most societies distribute common electricity equally."
            >

            <div
                style={{
                    display: "flex",
                    gap: 16,
                    alignItems: "center",
                }}
                >

                <select
                    value={
                    form.common_electricity_basis
                    }
                    onChange={(e) =>
                    setValue(
                        "common_electricity_basis",
                        e.target.value
                    )
                    }
                    style={{
                    ...styles.select,
                    flex: 1,
                    }}
                >
                    <option value="EQUAL">
                    Equal
                    </option>

                    <option value="AREA">
                    Area
                    </option>

                </select>

                <input
                    type="number"

                    value={
                    form.common_electricity_rate
                    }

                    onChange={(e) =>
                    setValue(
                        "common_electricity_rate",
                        e.target.value
                    )
                    }

                    placeholder={
                        form.common_electricity_basis ===
                        "AREA"

                            ? "₹ / sqft PM"

                            : "₹ / flat PM"
                    }

                    style={{
                    ...styles.input,
                    width: 180,
                    }}
                />

                </div>

            </GovernanceQuestion>
        <div style={styles.sectionDivider}>
          Parking Governance
        </div>

        <GovernanceQuestion
          question="Is parking chargeable in the society?"
          guidance="Some societies recover operational parking costs separately."
        >

          <Toggle
            checked={
              form.parking_enabled
            }
            onChange={(v) =>
              setValue(
                "parking_enabled",
                v
              )
            }
          />

        </GovernanceQuestion>
        
        {
            form.parking_enabled && (

                <div style={styles.questionCard}>

                <div style={styles.question}>
                    Parking Recovery Matrix
                </div>

                <div style={styles.guidance}>
                    Configure monthly parking
                    recovery by vehicle type.
                </div>

                <div style={styles.parkingGrid}>

                    <div style={styles.parkingGridRow}>

                    <div style={styles.parkingGridLabel}>
                        Four Wheeler
                    </div>

                    <input
                        value={
                        form.four_wheeler_rate
                        }
                        onChange={(e) =>
                        setValue(
                            "four_wheeler_rate",
                            e.target.value
                        )
                        }
                        style={styles.gridInput}
                    />

                    </div>

                    <div style={styles.parkingGridRow}>

                    <div style={styles.parkingGridLabel}>
                        Two Wheeler
                    </div>

                    <input
                        value={
                        form.two_wheeler_rate
                        }
                        onChange={(e) =>
                        setValue(
                            "two_wheeler_rate",
                            e.target.value
                        )
                        }
                        style={styles.gridInput}
                    />

                    </div>

                    <div style={styles.parkingGridRow}>

                    <div style={styles.parkingGridLabel}>
                        EV Vehicle
                    </div>

                    <input
                        value={
                        form.ev_vehicle_rate
                        }
                        onChange={(e) =>
                        setValue(
                            "ev_vehicle_rate",
                            e.target.value
                        )
                        }
                        style={styles.gridInput}
                    />

                    </div>

                    <div style={styles.parkingGridRow}>

                    <div style={styles.parkingGridLabel}>
                        Visitor Parking
                    </div>

                    <input
                        value={
                        form.visitor_parking_rate
                        }
                        onChange={(e) =>
                        setValue(
                            "visitor_parking_rate",
                            e.target.value
                        )
                        }
                        style={styles.gridInput}
                    />

                    </div>

                </div>

                </div>
            )
            }
        
        {
            form.parking_enabled && (

                <div style={styles.questionCard}>

                <div style={styles.question}>
                    Flat Wise Parking Matrix
                </div>

                <div style={styles.guidance}>
                    Configure vehicle quantities
                    applicable to each flat.
                </div>

                <div style={styles.matrixWrapper}>

                    <table style={styles.matrixTable}>

                    <thead>

                        <tr>

                        <th style={styles.matrixHead}>
                            Flat
                        </th>

                        <th style={styles.matrixHead}>
                            4W
                        </th>

                        <th style={styles.matrixHead}>
                            2W
                        </th>

                        <th style={styles.matrixHead}>
                            EV
                        </th>

                        <th style={styles.matrixHead}>
                            Visitor
                        </th>

                        <th style={styles.matrixHead}>
                            Value
                        </th>

                        </tr>

                    </thead>

                    <tbody>

                    {
                    Object.keys(
                        groupedParkingMatrix
                    ).map((wing) => (

                        <>

                        <tr>

                            <td
                            colSpan={6}
                            style={{
                                ...styles.matrixCell,
                                background: "#f3f4f6",
                                fontWeight: 700,
                                cursor: "pointer",
                            }}

                            onClick={() =>

                                setExpandedWings(
                                (
                                    prev: any
                                ) => ({

                                    ...prev,

                                    [wing]:
                                    !prev[wing],
                                })
                                )
                            }
                            >

                            {
                                expandedWings[wing]
                                ? "▼"
                                : "▶"
                            }

                            {" "}
                            Wing {wing}

                            <button

                                onClick={(e) => {

                                    e.stopPropagation();

                                    saveWing(wing);
                                }}

                                style={{

                                    marginLeft: 20,

                                    background: "#f97316",

                                    color: "#fff",

                                    border: "none",

                                    padding: "6px 12px",

                                    borderRadius: 8,

                                    cursor: "pointer",

                                    fontSize: 12,
                                }}
                                >

                                {
                                    savingWing === wing
                                    ? "Saving..."
                                    : "Save Wing"
                                }

                                </button>

                            </td>

                        </tr>

                        {
                            expandedWings[wing] &&

                            groupedParkingMatrix[
                            wing
                            ].map(
                            (
                                row: any
                            ) => (

                                <tr
                                key={
                                    row.flat_id
                                }
                                >

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >
                                    {
                                    row.flat_number
                                    }
                                </td>

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >

                                    <input
                                    value={
                                        row.four_wheeler
                                    }

                                    onChange={(e) =>
                                        updateParkingCell(
                                        row.flat_id,

                                        "four_wheeler",

                                        e.target.value
                                        )
                                    }

                                    style={
                                        styles.matrixInput
                                    }
                                    />

                                </td>

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >

                                    <input
                                    value={
                                        row.two_wheeler
                                    }

                                    onChange={(e) =>
                                        updateParkingCell(
                                        row.flat_id,

                                        "two_wheeler",

                                        e.target.value
                                        )
                                    }

                                    style={
                                        styles.matrixInput
                                    }
                                    />

                                </td>

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >

                                    <input
                                    value={
                                        row.ev_vehicle
                                    }

                                    onChange={(e) =>
                                        updateParkingCell(
                                        row.flat_id,

                                        "ev_vehicle",

                                        e.target.value
                                        )
                                    }

                                    style={
                                        styles.matrixInput
                                    }
                                    />

                                </td>

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >

                                    <input
                                    value={
                                        row.visitor
                                    }

                                    onChange={(e) =>
                                        updateParkingCell(
                                        row.flat_id,

                                        "visitor",

                                        e.target.value
                                        )
                                    }

                                    style={
                                        styles.matrixInput
                                    }
                                    />

                                </td>

                                <td
                                    style={
                                    styles.matrixCell
                                    }
                                >

                                    ₹
                                    {row.value}

                                </td>

                                </tr>
                            )
                            )
                        }

                        </>
                    ))
                    }

                    </tbody>

                    </table>

                </div>

                </div>
            )
            }
        {/* SYSTEM DISCLOSURE */}

        <div style={styles.systemCard}>

          <div style={styles.systemLine}>
            System is designed to
            automatically circulate
            maintenance bills to all
            members.
          </div>

          <div style={styles.systemLine}>
            System will also notify
            defaulters regarding
            penalties and interest
            levied by the society.
          </div>

        </div>

        {/* SUMMARY */}

        <div style={styles.summaryCard}>

          <div style={styles.summaryTitle}>
            Governance Summary
          </div>

          <ul style={styles.summaryList}>

            <li>
              Bills will be generated{" "}
              {
                form.billing_cycle
              }
            </li>

            <li>
              Members will receive{" "}
              {
                form.due_within_days
              }{" "}
              days to pay dues
            </li>

            <li>
              Interest recovery{" "}
              {form.interest_enabled
                ? "enabled"
                : "disabled"}
            </li>

            <li>
              Non occupancy recovery{" "}
              {form
                .non_occupancy_enabled
                ? "enabled"
                : "disabled"}
            </li>

            <li>
              Parking recovery{" "}
              {form.parking_enabled
                ? "enabled"
                : "disabled"}
            </li>

          </ul>

        </div>

        {/* SAVE */}

        <button
          style={styles.primaryButton}
          onClick={
            saveGovernance
          }
          disabled={loading}
        >
          {loading
            ? "Saving Governance..."
            : "Continue to Billing Activation"}
        </button>

      </div>

    </AppShell>
  );
}

/* =====================================================
   QUESTION BLOCK
===================================================== */

function GovernanceQuestion({
  question,
  guidance,
  children,
}: {
  question: string;
  guidance: string;
  children: React.ReactNode;
}) {

  return (
    <div style={styles.questionCard}>

      <div style={styles.question}>
        {question}
      </div>

      <div style={styles.guidance}>
        {guidance}
      </div>

      <div style={styles.answerArea}>
        {children}
      </div>

    </div>
  );
}

/* =====================================================
   TOGGLE
===================================================== */

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (
    value: boolean
  ) => void;
}) {

  return (
    <input
      type="checkbox"
      checked={checked}
      onChange={(e) =>
        onChange(
          e.target.checked
        )
      }
    />
  );
}

/* =====================================================
   STYLES
===================================================== */

const styles: any = {

  container: {
    padding: 32,
    background: "#f5f7fb",
    minHeight: "100vh",
  },

  loading: {
    padding: 40,
  },

  headerCard: {
    background: "#fff",
    padding: 28,
    borderRadius: 18,
    marginBottom: 24,
  },

  pageTitle: {
    fontSize: 32,
    fontWeight: 700,
    color: "#f97316",
    marginBottom: 12,
  },

  pageSubtitle: {
    color: "#666",
    lineHeight: 1.7,
    maxWidth: 850,
  },

  questionCard: {
    background: "#fff",
    padding: 24,
    borderRadius: 16,
    marginBottom: 18,
  },

  question: {
    fontSize: 17,
    fontWeight: 600,
    marginBottom: 10,
  },

  guidance: {
    fontSize: 14,
    color: "#777",
    marginBottom: 18,
    lineHeight: 1.6,
  },

  answerArea: {
    marginTop: 10,
  },

  input: {
    width: "100%",
    padding: 14,
    borderRadius: 10,
    border: "1px solid #ddd",
    fontSize: 15,
  },

  select: {
    width: "100%",
    padding: 14,
    borderRadius: 10,
    border: "1px solid #ddd",
    fontSize: 15,
  },

  sectionDivider: {
    fontSize: 22,
    fontWeight: 700,
    color: "#f97316",
    marginTop: 40,
    marginBottom: 20,
  },

  systemCard: {
    background: "#f3f4f6",
    borderRadius: 16,
    padding: 24,
    marginTop: 30,
    marginBottom: 30,
  },

  systemLine: {
    marginBottom: 12,
    color: "#444",
    lineHeight: 1.7,
  },

  summaryCard: {
    background: "#fff7ed",
    border: "1px solid #fdba74",
    padding: 24,
    borderRadius: 16,
    marginBottom: 24,
  },

  summaryTitle: {
    fontSize: 20,
    fontWeight: 700,
    marginBottom: 16,
  },

  summaryList: {
    lineHeight: 2,
    paddingLeft: 18,
  },

  primaryButton: {
    width: "100%",
    background: "#f97316",
    color: "#fff",
    border: "none",
    padding: 18,
    borderRadius: 14,
    fontSize: 16,
    fontWeight: 700,
    cursor: "pointer",
    },

    addButton: {
    background: "#f97316",
    color: "#fff",
    border: "none",
    padding: "12px 18px",
    borderRadius: 10,
    cursor: "pointer",
    },

    mappingCard: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "#f9fafb",
    padding: 14,
    borderRadius: 10,
    marginBottom: 12,
    },

    removeButton: {
    border: "none",
    background: "#ef4444",
    color: "#fff",
    padding: "8px 12px",
    borderRadius: 8,
    cursor: "pointer",
    },

    parkingGrid: {
    marginTop: 10,
    },

    parkingGridRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 14,
    gap: 20,
    },

    parkingGridLabel: {
    minWidth: 180,
    fontWeight: 500,
    },

    gridInput: {
    flex: 1,
    padding: 12,
    borderRadius: 10,
    border: "1px solid #ddd",
    fontSize: 14,
    },

    matrixWrapper: {
  overflowX: "auto",
},

matrixTable: {
  width: "100%",
  borderCollapse: "collapse",
},

matrixHead: {
  border: "1px solid #ddd",
  padding: 12,
  background: "#f3f4f6",
  textAlign: "left",
  fontSize: 14,
},

matrixCell: {
  border: "1px solid #ddd",
  padding: 10,
},

matrixInput: {
  width: 80,
  padding: 8,
  borderRadius: 6,
  border: "1px solid #ddd",
},
  }