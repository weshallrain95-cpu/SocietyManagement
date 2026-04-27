import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useSociety } from "../../context/SocietyContext";
import { ChevronDown } from "lucide-react";

export default function Sidebar() {
  const { society } = useSociety();
  const navigate = useNavigate();
  const location = useLocation();

  const isUnlocked = society?.onboarding?.is_complete;

  const [openMain, setOpenMain] = useState<string | null>(null);
  const [openSub, setOpenSub] = useState<{ [key: string]: string | null }>({});

  const handleClick = (route?: string, always?: boolean) => {
    if (!isUnlocked && !always) {
      navigate("/dashboard");
      return;
    }
    if (route) navigate(route);
  };

  const isActive = (label: string) =>
    location.pathname.includes(label.toLowerCase().replace(/\s/g, "-"));

  const menu = [
    { label: "Dashboard", route: "/dashboard", always: true },
    { label: "Onboarding", route: "/dashboard", always: true },

    {
      label: "Structure & Assets",
      children: [
        {
          label: "Layout",
          children: ["Wings", "Floors", "Flats", "Parking"],
        },
        {
          label: "Assets",
          children: ["Asset Register", "Infrastructure", "Amenities"],
        },
        {
          label: "Asset Lifecycle",
          children: ["Maintenance", "Warranty", "Replacement"],
        },
      ],
    },

    {
      label: "Members",
      children: [
        {
          label: "Registry",
          children: ["Members", "Associate Members", "Tenants", "Nominees"],
        },
        {
          label: "Lifecycle",
          children: [
            "New Membership",
            "Transfers",
            "Nomination",
            "Exit / Death Transfer",
          ],
        },
        {
          label: "Records",
          children: ["Share Certificates", "KYC", "Voting Rights"],
        },
        {
          label: "Occupancy",
          children: [
            "Owner Occupied",
            "Tenant Occupied",
            "Vacancy",
            "Move-in",
            "Move-out",
          ],
        },
      ],
    },

    {
      label: "Governance",
      children: [
        {
          label: "Committee",
          children: ["Members", "Office Bearers"],
        },
        {
          label: "Lifecycle",
          children: ["Formation", "Dissolution", "Reconstitution"],
        },
        {
          label: "Meetings",
          children: ["AGM", "SGM", "Committee Meetings"],
        },
        {
          label: "Decisions",
          children: ["Resolutions", "Voting Records", "Minutes"],
        },
      ],
    },

    {
      label: "Finance & Accounting",
      children: [
        {
          label: "Accounting",
          children: ["Chart of Accounts", "Ledger", "Journals"],
        },
        {
          label: "Banking",
          children: ["Bank Accounts", "Reconciliation", "Petty Cash"],
        },
        {
          label: "Reports",
          children: [
            "Balance Sheet",
            "Income & Expenditure",
            "Cash Flow",
          ],
        },
        {
          label: "Year End",
          children: ["Closing", "Audit Preparation"],
        },
      ],
    },

    {
      label: "Billing & Collections",
      children: [
        {
          label: "Billing Engine",
          children: [
            "Maintenance Rules",
            "Charge Heads",
            "Interest Rules",
            "Bill Generation",
            "Adjustments",
            "Revisions",
            "Historical Bills",
          ],
        },
        {
          label: "Payments",
          children: [
            "Payment Entries",
            "Online Payments",
            "Reconciliation",
            "Receipts",
            "Refunds",
          ],
        },
        {
          label: "Recovery",
          children: [
            "Defaulters",
            "Notices",
            "Interest Calculation",
            "Recovery Actions",
          ],
        },
      ],
    },

    {
      label: "Compliance & Filings",
      children: [
        {
          label: "Filings",
          children: ["Registrar Forms", "Annual Returns"],
        },
        {
          label: "Audit",
          children: ["Audit Reports", "Rectifications"],
        },
        {
          label: "Calendar",
          children: ["Deadlines", "Notices"],
        },
      ],
    },

    {
      label: "Legal & Disputes",
      children: [
        {
          label: "Cases",
          children: ["Member", "Registrar", "Court"],
        },
        {
          label: "Management",
          children: ["Hearings", "Evidence", "Judgements"],
        },
      ],
    },

    {
      label: "Operations",
      children: [
        {
          label: "Work",
          children: ["Work Orders", "Service Requests", "Tasks"],
        },
        {
          label: "Issues",
          children: ["Complaints", "Tickets", "Escalations"],
        },
        {
          label: "Facilities",
          children: [
            "Water",
            "Electricity",
            "Lift",
            "Waste",
            "Security",
          ],
        },
        {
          label: "Maintenance",
          children: ["AMC", "Scheduled", "Inspections"],
        },
        {
          label: "Inventory",
          children: ["Stock", "Consumables", "Logs"],
        },
      ],
    },

    {
      label: "Projects",
      children: [
        {
          label: "Projects",
          children: ["Major Repairs", "Capex"],
        },
        {
          label: "Management",
          children: ["Budgets", "Vendors", "Timelines"],
        },
      ],
    },

    {
      label: "Vendors & Contracts",
      children: [
        {
          label: "Vendors",
          children: ["Vendor List", "Profiles"],
        },
        {
          label: "Procurement",
          children: [
            "Quotations",
            "Comparatives",
            "PO / Work Orders",
            "GRN / Completion",
            "Invoices",
            "Payments",
            "Closure",
          ],
        },
      ],
    },

    {
      label: "Member Services",
      children: [
        {
          label: "Requests",
          children: ["NOC", "Certificates", "Permissions"],
        },
        {
          label: "Services",
          children: [
            "Sale NOC",
            "Mortgage NOC",
            "Tenant NOC",
            "Renovation",
            "Vehicle",
          ],
        },
        {
          label: "Records",
          children: ["Statements", "Share Copies", "History"],
        },
        {
          label: "Tracking",
          children: ["Status", "Service History"],
        },
      ],
    },

    {
      label: "Communication",
      children: [
        {
          label: "Channels",
          children: ["Announcements", "Notices", "Broadcasts"],
        },
        {
          label: "Engagement",
          children: ["Discussions", "Threads", "Alerts"],
        },
      ],
    },

    {
      label: "Documents & Records",
      children: [
        {
          label: "Repository",
          children: ["Bylaws", "Contracts", "Audit Reports"],
        },
        {
          label: "Management",
          children: ["Versioning", "Access Control"],
        },
      ],
    },

    {
      label: "Administration",
      children: [
        {
          label: "System",
          children: ["Roles", "Permissions", "Policies"],
        },
        {
          label: "Logs",
          children: ["Audit Logs", "Activity"],
        },
        {
          label: "Workflow",
          children: ["Configuration"],
        },
      ],
    },
  ];

  return (
    <div style={sidebar}>
      {menu.map((main: any, i: number) => {
        const enabled = isUnlocked || main.always;

        return (
          <div key={i}>
            <div
              style={{
                ...mainItem,
                background:
                  openMain === main.label ? "#1f2937" : "transparent",
                opacity: enabled ? 1 : 0.5,
                cursor: enabled ? "pointer" : "not-allowed",
              }}
              onClick={() => {
                if (main.children) {
                  const isOpening = openMain !== main.label;

                  setOpenMain(isOpening ? main.label : null);

                  // 🔥 AUTO-OPEN FIRST SUBMENU
                  if (isOpening && main.children?.length) {
                    setOpenSub((prev) => ({
                      ...prev,
                      [main.label]: main.children[0].label,
                    }));
                  }
                } else {
                  handleClick(main.route, main.always);
                }
              }}
            >
              {main.label}
              {main.children && (
                <ChevronDown
                  size={16}
                  style={{
                    transform:
                      openMain === main.label ? "rotate(180deg)" : "rotate(0deg)",
                    transition: "0.2s",
                  }}
                />
              )}
            </div>

            {main.children && openMain === main.label && (
              <div style={subMenu}>
                {main.children.map((sub: any, j: number) => (
                  <div key={j}>
                    <div
                      style={subItem}
                      onClick={() =>
                        setOpenSub((prev) => ({
                          ...prev,
                          [main.label]:
                            prev[main.label] === sub.label ? null : sub.label,
                        }))
                      }
                    >
                      <span>{sub.label}</span>

                      <ChevronDown
                        size={14}
                        style={{
                          transform:
                            openSub[main.label] === sub.label
                              ? "rotate(180deg)"
                              : "rotate(0deg)",
                          transition: "0.2s",
                        }}
                      />
                    </div>
                      
                    {sub.children &&
                      openSub[main.label] === sub.label && (
                        <div style={subSubMenu}>
                          {sub.children.map((leaf: string, k: number) => (
                            <div
                              key={k}
                              style={{
                                ...leafItem,
                                background: isActive(leaf)
                                  ? "#2563eb"
                                  : "transparent",
                                color: isActive(leaf)
                                  ? "white"
                                  : "#cbd5f5",
                              }}
                              onMouseEnter={(e) => {
                                if (!isActive(leaf)) e.currentTarget.style.background = "#1f2937";
                              }}
                              onMouseLeave={(e) => {
                                if (!isActive(leaf)) e.currentTarget.style.background = "transparent";
                              }}
                              onClick={() =>
                                handleClick(
                                  `/${main.label
                                    .toLowerCase()
                                    .replace(/\s/g, "-")}/${leaf
                                    .toLowerCase()
                                    .replace(/\s/g, "-")}`
                                )
                              }
                            >
                              {leaf}
                            </div>
                          ))}
                        </div>
                      )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ================= STYLES ================= */

const sidebar = {
  width: 280,
  height: "100vh",
  background: "#111827",
  color: "#f9fafb",
  padding: 16,
  overflowY: "auto" as const,
};

const mainItem = {
  padding: "10px 12px",
  borderRadius: 8,
  fontWeight: 600,
  marginBottom: 4,
};

const subMenu = {
  paddingLeft: 10,
};

const subItem = {
  padding: "8px 10px",
  fontSize: 13,
  color: "#d1d5db",
};

const subSubMenu = {
  paddingLeft: 16,
  marginLeft: 6,
  borderLeft: "1px solid #374151",
};

const leafItem = {
  padding: "6px 10px",
  fontSize: 13,
  borderRadius: 6,
  transition: "all 0.15s ease",
};