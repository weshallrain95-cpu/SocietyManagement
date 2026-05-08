import AppShell from "../components/layout/AppShell";
import { useNavigate } from "react-router-dom";
import { useSociety } from "../context/SocietyContext";
import { useEffect, useState } from "react";

export default function SCR28FinancialOnboarding() {
  const navigate = useNavigate();
  const { society } = useSociety();

  // 🔹 SESSION CONTEXT (RESTORED)
  const societyId = localStorage.getItem("society_id");

  // 🔹 STATE LAYER (RESTORED ORIGINAL INTENT)
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // 🔹 INIT PATTERN (RESTORED + FIXED)
  useEffect(() => {
    const init = async () => {
      try {
        // 🔥 BACKEND HOOK POINT (DO NOT REMOVE)
        // This is where COA initialization + onboarding state will come
        // TEMP: fallback until backend is ready

        const fallback = society?.financial_onboarding || {
          can_setup_bank: true,
          bank_completed: false,

          can_setup_income: false,
          income_completed: false,

          can_setup_expense: false,
          expense_completed: false,

          can_setup_investments: false,
          investments_completed: false,

          can_setup_opening: false,
          opening_completed: false,

          can_activate: false,
          is_active: false,
        };

        setState(fallback);
      } catch (err) {
        console.error("Failed to load onboarding state", err);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [societyId, society]);

  // 🔒 LOADING STATE (UNCHANGED)
  if (loading || !state) {
    return (
      <AppShell>
        <div style={{ padding: 20 }}>
          Initializing financial system...
        </div>
      </AppShell>
    );
  }

  // 🔹 DERIVED LAYER (RESTORED)
  const onboarding = state;

  const steps = [
    {
      label: "1. Bank Accounts",
      route: "/financial-onboarding/bank-accounts",
      canAccess: onboarding.can_setup_bank,
      isComplete: onboarding.bank_completed,
      desc: onboarding.bank_completed
        ? "Bank accounts configured"
        : "Add society bank accounts",
    },
    {
      label: "2. Income Sources",
      route: "/financial-onboarding/income",
      canAccess: onboarding.can_setup_income,
      isComplete: onboarding.income_completed,
      desc: onboarding.income_completed
        ? "Income sources configured"
        : "Define how your society earns money",
    },
    {
      label: "3. Expense Structure",
      route: "/financial-onboarding/expense",
      canAccess: onboarding.can_setup_expense,
      isComplete: onboarding.expense_completed,
      desc: onboarding.expense_completed
        ? "Expense heads configured"
        : "Define how your society spends",
    },
    {
      label: "4. Investments & Funds",
      route: "/financial-onboarding/investments",
      canAccess: onboarding.can_setup_investments,
      isComplete: onboarding.investments_completed,
      desc: onboarding.investments_completed
        ? "Investments recorded"
        : "Capture FDs and funds",
    },
    {
      label: "5. Opening & Closing Balances",
      route: "/financial-onboarding/opening-balances",
      canAccess: onboarding.can_setup_opening,
      isComplete: onboarding.opening_completed,
      desc: onboarding.opening_completed
        ? "Balances initialized"
        : "Set your financial starting point",
    },
    {
      label: "6. Activate Financial System",
      route: "/financial-onboarding/activate",
      canAccess: onboarding.can_activate,
      isComplete: onboarding.is_active,
      desc: onboarding.is_active
        ? "System is active"
        : "Finalize setup and go live",
    },
  ];

  return (
    <AppShell>
      <div style={{ padding: 20 }}>
        <h2 style={{ fontSize: 24, fontWeight: 600, marginBottom: 6 }}>
          Financial Onboarding
        </h2>

        <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 20 }}>
          Complete these steps to activate your society’s financial system.
        </p>

        {steps.map((step, index) => {
          const clickable = step.canAccess && !step.isComplete;

          let borderColor = "transparent";
          let statusText = "Locked";

          if (step.isComplete) {
            borderColor = "#16a34a";
            statusText = "Completed";
          } else if (clickable) {
            borderColor = "#f97316";
            statusText = "Start";
          }

          return (
            <div
              key={index}
              style={{
                padding: 16,
                border: "1px solid #e5e7eb",
                borderRadius: 10,
                marginBottom: 12,
                opacity: step.canAccess ? 1 : 0.6,
                cursor: clickable ? "pointer" : "not-allowed",
                borderLeft: `4px solid ${borderColor}`,
              }}
              onClick={() => {
                if (!clickable) return;
                navigate(step.route);
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <h3 style={{ fontSize: 16, fontWeight: 600 }}>
                  {step.label}
                </h3>

                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                    color:
                      step.isComplete
                        ? "#16a34a"
                        : clickable
                        ? "#f97316"
                        : "#9ca3af",
                  }}
                >
                  {statusText}
                </span>
              </div>

              <p style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
                {step.desc}
              </p>
            </div>
          );
        })}
      </div>
    </AppShell>
  );
}