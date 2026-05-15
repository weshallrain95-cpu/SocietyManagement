import AppShell from "../components/layout/AppShell";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function SCR29BankAccounts() {

  const navigate = useNavigate();

  const societyId = localStorage.getItem("society_id");

  const [loading, setLoading] = useState(true);

  const [banks, setBanks] = useState<any[]>([]);

  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    name: "",
    bank_name: "",
    account_number: "",
    ifsc: "",
    treasury_role: "OPERATIONS",
    bank_address: "",
    upi_id: "",
    banking_phone: "",
    banking_email: "",
    is_active: true,
  });

  // ==========================================================
  // LOAD BANK ACCOUNTS
  // ==========================================================
  useEffect(() => {
    init();
  }, []);

  const init = async () => {
    try {

      const response = await fetch(
        `http://127.0.0.1:8000/api/society/bank-accounts/?society_id=${societyId}`
      );

      const data = await response.json();

      setBanks(data);

    } catch (err) {
      console.error("Failed to load bank accounts", err);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // CREATE BANK ACCOUNT
  // ==========================================================
  const createBankAccount = async () => {

    if (
      !form.name ||
      !form.bank_name ||
      !form.account_number ||
      !form.ifsc
    ) {
      alert("Please complete all required fields.");
      return;
    }

    try {

      setSaving(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/society/bank-accounts/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            society: Number(societyId),
            ...form,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create bank account");
      }

      const created = await response.json();

      setBanks((prev) => [created, ...prev]);

      setForm({
        name: "",
        bank_name: "",
        account_number: "",
        ifsc: "",
        treasury_role: "OPERATIONS",
        bank_address: "",
        upi_id: "",
        banking_phone: "",
        banking_email: "",
        is_active: true,
      });

    } catch (err) {
      console.error(err);
      alert("Failed to create bank account");
    } finally {
      setSaving(false);
    }
  };

  // ==========================================================
  // UPDATE EXISTING BANK
  // ==========================================================
  const updateBank = async (bank: any) => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/api/society/bank-accounts/",
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(bank),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update bank");
      }

      const updated = await response.json();

      setBanks((prev) =>
        prev.map((b) => (b.id === updated.id ? updated : b))
      );

      alert("Bank account updated.");

    } catch (err) {
      console.error(err);
      alert("Failed to update bank account.");
    }
  };

  // ==========================================================
  // TOGGLE ACTIVE
  // ==========================================================
  const toggleActive = async (bank: any) => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/api/society/bank-accounts/",
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            id: bank.id,
            is_active: !bank.is_active,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update bank");
      }

      const updated = await response.json();

      setBanks((prev) =>
        prev.map((b) => (b.id === updated.id ? updated : b))
      );

    } catch (err) {
      console.error(err);
      alert("Failed to update bank account");
    }
  };

  // ==========================================================
  // ACTIVE BANK CHECK
  // ==========================================================
  const hasActiveBank = useMemo(() => {
    return banks.some((b) => b.is_active);
  }, [banks]);

  // ==========================================================
  // LOADING
  // ==========================================================
  if (loading) {
    return (
      <AppShell>
        <div style={{ padding: 20 }}>
          Loading treasury configuration...
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div
        style={{
          padding: 20,
          maxWidth: 1100,
          margin: "0 auto",
        }}
      >

        {/* ====================================================== */}
        {/* HEADER */}
        {/* ====================================================== */}

        <div style={{ marginBottom: 28 }}>
          <h2
            style={{
              fontSize: 28,
              fontWeight: 700,
              marginBottom: 8,
              color: "#111827",
            }}
          >
            Society Bank Accounts
          </h2>

          <p
            style={{
              fontSize: 14,
              color: "#6b7280",
              lineHeight: 1.6,
              maxWidth: 800,
            }}
          >
            Configure and activate the bank accounts used by your
            society for operations, sinking funds, reserves, and
            fixed deposits.
          </p>
        </div>

        {/* ====================================================== */}
        {/* EXISTING BANK ACCOUNTS */}
        {/* ====================================================== */}

        {banks.length > 0 && (
          <div style={{ marginBottom: 40 }}>

            <h3
              style={{
                fontSize: 18,
                fontWeight: 600,
                marginBottom: 18,
              }}
            >
              Existing Bank Accounts
            </h3>

            <div
              style={{
                display: "grid",
                gap: 22,
              }}
            >

              {banks.map((bank, index) => {

                return (
                  <div
                    key={bank.id}
                    style={{
                      border: "1px solid #e5e7eb",
                      borderRadius: 18,
                      padding: 24,
                      background: "#fff",
                      boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
                    }}
                  >

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: 20,
                      }}
                    >

                      <div>
                        <div
                          style={{
                            fontSize: 18,
                            fontWeight: 600,
                            color: "#111827",
                          }}
                        >
                          Bank Account #{index + 1}
                        </div>

                        <div
                          style={{
                            fontSize: 13,
                            color: "#6b7280",
                            marginTop: 4,
                          }}
                        >
                          Review and complete treasury onboarding.
                        </div>
                      </div>

                      <div
                        style={{
                          padding: "6px 12px",
                          borderRadius: 999,
                          background:
                            bank.is_active
                              ? "#dcfce7"
                              : "#f3f4f6",
                          color:
                            bank.is_active
                              ? "#166534"
                              : "#6b7280",
                          fontSize: 12,
                          fontWeight: 600,
                        }}
                      >
                        {bank.is_active
                          ? "ACTIVE"
                          : "INACTIVE"}
                      </div>

                    </div>

                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "repeat(auto-fit, minmax(280px, 1fr))",
                        gap: 16,
                      }}
                    >

                      <input
                        value={bank.name || ""}
                        placeholder="Account Name"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? { ...b, name: e.target.value }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <input
                        value={bank.bank_name || ""}
                        placeholder="Bank Name"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    bank_name: e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <input
                        value={bank.account_number || ""}
                        placeholder="Account Number"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    account_number:
                                      e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <input
                        value={bank.ifsc || ""}
                        placeholder="IFSC"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    ifsc: e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <select
                        value={bank.treasury_role}
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    treasury_role:
                                      e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      >
                        <option value="OPERATIONS">
                          Operations
                        </option>

                        <option value="SINKING_FUND">
                          Sinking Fund
                        </option>

                        <option value="RESERVE">
                          Reserve
                        </option>

                        <option value="FD">
                          Fixed Deposit
                        </option>
                      </select>

                      <input
                        value={bank.upi_id || ""}
                        placeholder="UPI ID"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    upi_id: e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <input
                        value={bank.banking_phone || ""}
                        placeholder="Banking Phone"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    banking_phone:
                                      e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                      <input
                        value={bank.banking_email || ""}
                        placeholder="Banking Email"
                        onChange={(e) => {
                          setBanks((prev) =>
                            prev.map((b) =>
                              b.id === bank.id
                                ? {
                                    ...b,
                                    banking_email:
                                      e.target.value,
                                  }
                                : b
                            )
                          );
                        }}
                        style={inputStyle}
                      />

                    </div>

                    <textarea
                      rows={4}
                      value={bank.bank_address || ""}
                      placeholder="Bank Address"
                      onChange={(e) => {
                        setBanks((prev) =>
                          prev.map((b) =>
                            b.id === bank.id
                              ? {
                                  ...b,
                                  bank_address:
                                    e.target.value,
                                }
                              : b
                          )
                        );
                      }}
                      style={{
                        ...inputStyle,
                        width: "100%",
                        marginTop: 16,
                        resize: "vertical",
                      }}
                    />

                    <div
                      style={{
                        display: "flex",
                        gap: 12,
                        marginTop: 20,
                        flexWrap: "wrap",
                      }}
                    >

                      <button
                        onClick={() => updateBank(bank)}
                        style={{
                          padding: "12px 18px",
                          borderRadius: 10,
                          border: "none",
                          background: "#111827",
                          color: "#fff",
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        Save Changes
                      </button>

                      <button
                        onClick={() => toggleActive(bank)}
                        style={{
                          padding: "12px 18px",
                          borderRadius: 10,
                          border: "none",
                          background:
                            bank.is_active
                              ? "#ef4444"
                              : "#16a34a",
                          color: "#fff",
                          fontWeight: 600,
                          cursor: "pointer",
                        }}
                      >
                        {bank.is_active
                          ? "Deactivate Account"
                          : "Activate & Continue"}
                      </button>

                    </div>

                  </div>
                );
              })}

            </div>

          </div>
        )}

        {/* ====================================================== */}
        {/* ADD NEW BANK ACCOUNT */}
        {/* ====================================================== */}

        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 18,
            padding: 24,
            background: "#fff",
            marginBottom: 36,
          }}
        >

          <h3
            style={{
              fontSize: 20,
              fontWeight: 600,
              marginBottom: 20,
              color: "#111827",
            }}
          >
            Add New Bank Account
          </h3>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 16,
            }}
          >

            <input
              placeholder="Account Name *"
              value={form.name}
              onChange={(e) =>
                setForm({ ...form, name: e.target.value })
              }
              style={inputStyle}
            />

            <input
              placeholder="Bank Name *"
              value={form.bank_name}
              onChange={(e) =>
                setForm({
                  ...form,
                  bank_name: e.target.value,
                })
              }
              style={inputStyle}
            />

            <input
              placeholder="Account Number *"
              value={form.account_number}
              onChange={(e) =>
                setForm({
                  ...form,
                  account_number: e.target.value,
                })
              }
              style={inputStyle}
            />

            <input
              placeholder="IFSC *"
              value={form.ifsc}
              onChange={(e) =>
                setForm({
                  ...form,
                  ifsc: e.target.value,
                })
              }
              style={inputStyle}
            />

            <select
              value={form.treasury_role}
              onChange={(e) =>
                setForm({
                  ...form,
                  treasury_role: e.target.value,
                })
              }
              style={inputStyle}
            >
              <option value="OPERATIONS">
                Operations
              </option>

              <option value="SINKING_FUND">
                Sinking Fund
              </option>

              <option value="RESERVE">
                Reserve
              </option>

              <option value="FD">
                Fixed Deposit
              </option>
            </select>

            <input
              placeholder="UPI ID"
              value={form.upi_id}
              onChange={(e) =>
                setForm({
                  ...form,
                  upi_id: e.target.value,
                })
              }
              style={inputStyle}
            />

            <input
              placeholder="Banking Phone"
              value={form.banking_phone}
              onChange={(e) =>
                setForm({
                  ...form,
                  banking_phone: e.target.value,
                })
              }
              style={inputStyle}
            />

            <input
              placeholder="Banking Email"
              value={form.banking_email}
              onChange={(e) =>
                setForm({
                  ...form,
                  banking_email: e.target.value,
                })
              }
              style={inputStyle}
            />

          </div>

          <textarea
            placeholder="Bank Address"
            value={form.bank_address}
            onChange={(e) =>
              setForm({
                ...form,
                bank_address: e.target.value,
              })
            }
            rows={4}
            style={{
              ...inputStyle,
              width: "100%",
              marginTop: 16,
              resize: "vertical",
            }}
          />

          <button
            onClick={createBankAccount}
            disabled={saving}
            style={{
              marginTop: 20,
              padding: "12px 18px",
              borderRadius: 10,
              border: "none",
              background: "#f97316",
              color: "#fff",
              fontWeight: 600,
              cursor: "pointer",
              opacity: saving ? 0.7 : 1,
            }}
          >
            {saving
              ? "Saving..."
              : "Add Bank Account"}
          </button>

        </div>

        {/* ====================================================== */}
        {/* TREASURY GOVERNANCE */}
        {/* ====================================================== */}

        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 18,
            padding: 24,
            background: "#fff",
            marginBottom: 32,
          }}
        >

          <h3
            style={{
              fontSize: 18,
              fontWeight: 600,
              marginBottom: 18,
            }}
          >
            Treasury Governance
          </h3>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 16,
            }}
          >

            <input
              placeholder="Approval threshold amount"
              style={inputStyle}
            />

            <select style={inputStyle}>
              <option>
                Maker / Checker Disabled
              </option>

              <option>
                Maker / Checker Enabled
              </option>
            </select>

          </div>

          <p
            style={{
              marginTop: 14,
              fontSize: 12,
              color: "#6b7280",
              lineHeight: 1.6,
            }}
          >
            These governance rules will later control approval
            workflows and treasury authorization.
          </p>
        </div>

        {/* ====================================================== */}
        {/* CONTINUE */}
        {/* ====================================================== */}

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            borderTop: "1px solid #e5e7eb",
            paddingTop: 20,
          }}
        >

          <div
            style={{
              fontSize: 13,
              color: "#6b7280",
            }}
          >
            {hasActiveBank
              ? "Treasury onboarding ready."
              : "At least one active bank account is required."}
          </div>

          <button
            disabled={!hasActiveBank}
            onClick={() => {
              navigate("/financial-onboarding");
            }}
            style={{
              padding: "12px 20px",
              borderRadius: 10,
              border: "none",
              background:
                hasActiveBank
                  ? "#16a34a"
                  : "#d1d5db",
              color: "#fff",
              fontWeight: 600,
              cursor:
                hasActiveBank
                  ? "pointer"
                  : "not-allowed",
            }}
          >
            Save & Continue
          </button>

        </div>

      </div>
    </AppShell>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: 10,
  border: "1px solid #d1d5db",
  fontSize: 14,
  outline: "none",
  background: "#fff",
  boxSizing: "border-box",
};