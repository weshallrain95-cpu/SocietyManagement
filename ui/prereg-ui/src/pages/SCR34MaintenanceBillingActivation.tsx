import React, {

    useEffect,

    useState,

} from "react";

import { useNavigate } from "react-router-dom";

import AppShell from "../components/layout/AppShell";

const API_BASE =
    "http://127.0.0.1:8000/api/society";

type ReviewRowProps = {

    label: string;

    value: React.ReactNode;

};

function ReviewRow({

    label,

    value,

}: ReviewRowProps) {

    return (

        <div
            style={{
                maxWidth: "620px",
                margin: "0 auto 16px auto",
                background: "#ffffff",
                border: "1px solid #e5e7eb",
                borderRadius: "10px",
                padding: "18px 22px",
                boxShadow:
                    "0 1px 3px rgba(0,0,0,.04)",
            }}
        >

            <div
                style={{
                    fontSize: "12px",
                    fontWeight: 700,
                    color: "#6b7280",
                    textTransform: "uppercase",
                    letterSpacing: ".08em",
                    marginBottom: "8px",
                }}
            >

                {label}

            </div>

            <div
                style={{
                    fontSize: "18px",
                    fontWeight: 600,
                    color: "#111827",
                    lineHeight: 1.5,
                }}
            >

                {value}

            </div>

        </div>

    );

}

export default function SCR34MaintenanceBillingActivation() {

    

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [context, setContext] =
        useState<any>(null);

    const [

        selectedAccountId,

        setSelectedAccountId,

    ] = useState<number | null>(null);

    const [

        previewGenerated,

        setPreviewGenerated,

    ] = useState(false);

    const [

        currentStep,

        setCurrentStep,

    ] = useState(1);

    const [

        activationComplete,

        setActivationComplete,

    ] = useState(false);

    const [

        officialEmail,

        setOfficialEmail,

    ] = useState("");

    const societyId =
        localStorage.getItem("society_id");

    const navigate = useNavigate();

    useEffect(() => {

        hydrateSCR34();

    }, []);

    async function hydrateSCR34() {

        if (!societyId) {

            setError(
                "Society not selected."
            );

            setLoading(false);

            return;

        }

        try {

            const response =
                await fetch(

                    `${API_BASE}/scr34-context/?society_id=${societyId}`

                );

            const data =
                await response.json();

            setContext(data);

            setOfficialEmail(

                data.communications
                    ?.official_email || ""

            );

            if (

                data.selected_account
                    ?.selection_required === false

                &&

                data.selected_account
                    ?.account

            ) {

                setSelectedAccountId(

                    data.selected_account.account.id

                );

            }

        }

        catch (err) {

            console.error(err);

            setError(

                "Unable to load activation details."

            );

        }

        finally {

            setLoading(false);

        }

    }

    if (loading) {

        return (

            <AppShell>

                <div className="scr34-loading">

                    Loading Billing Activation...

                </div>

            </AppShell>

        );

    }

    if (error) {

        return (

            <AppShell>

                <div className="scr34-error">

                    {error}

                </div>

            </AppShell>

        );

    }

    return (

        <AppShell>

            <div className="scr34-page">

                <div
                    className="scr34-card"
                    style={{
                        background: "rgba(255,255,255,0.72)",
                        backdropFilter: "blur(16px)",
                        WebkitBackdropFilter: "blur(16px)",
                        border: "1px solid rgba(255,255,255,0.55)",
                        boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                    }}
                >

                    <div
                        style={{
                            textAlign: "center",
                            padding: "12px 0 8px",
                        }}
                    >

                        <div
                            style={{
                                fontSize: 30,
                                fontWeight: 700,
                                color: "#1f2937",
                                marginBottom: 10,
                            }}
                        >

                            Maintenance Billing Activation

                        </div>

                        <div
                            style={{
                                fontSize: 15,
                                color: "#6b7280",
                                lineHeight: 1.7,
                                maxWidth: 760,
                                margin: "0 auto",
                            }}
                        >

                            You have successfully on-boarded your Society 
                            receivables / "money earned" so far.

                            <br />

                            Only one final activation remains before
                            SocietyOS begins generating monthly
                            maintenance bills automatically.

                        </div>

                    </div>

                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginTop: 30,
                            gap: 10,
                        }}
                    >

                        {[
                            "Review",
                            "Collection",
                            "Verification",
                            "Activation",
                        ].map((step, index) => {

                            const stepNumber =
                                index + 1;

                            const completed =
                                currentStep > stepNumber;

                            const active =
                                currentStep === stepNumber;

                            return (

                                <div
                                    key={step}
                                    style={{
                                        flex: 1,
                                        textAlign: "center",
                                    }}
                                >

                                    <div
                                        style={{
                                            width: 42,
                                            height: 42,
                                            margin: "0 auto",
                                            borderRadius: "50%",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            fontWeight: 700,
                                            color: "#fff",
                                            background:

                                                completed

                                                    ? "#16a34a"

                                                    : active

                                                    ? "#ea580c"

                                                    : "#d1d5db",
                                        }}
                                    >

                                        {

                                            completed

                                                ? "✓"

                                                : stepNumber

                                        }

                                    </div>

                                    <div
                                        style={{
                                            marginTop: 10,
                                            fontSize: 13,
                                            fontWeight: active
                                                ? 700
                                                : 500,
                                            color:
                                                active
                                                    ? "#111827"
                                                    : "#6b7280",
                                        }}
                                    >

                                        {step}

                                    </div>

                                </div>

                            );

                        })}

                    </div>

                </div>  

            {

                activationComplete && (

                    <div
                        className="scr34-card"
                        style={{
                            background: "rgba(255,255,255,0.72)",
                            backdropFilter: "blur(16px)",
                            WebkitBackdropFilter: "blur(16px)",
                            border: "1px solid rgba(255,255,255,0.55)",
                            boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                        }}
                    >

                        <h2>

                            🎉 Monthly Billing Activated

                        </h2>

                        <p>

                            Congratulations.

                        </p>

                        <p>

                            Your Society is now fully
                            configured for automated
                            Monthly Maintenance Billing.

                        </p>

                        <p>

                            Future maintenance bills
                            will be generated using
                            your approved billing
                            configuration and
                            designated maintenance
                            collection account.

                        </p>

                        <div
                            className="scr34-preview-note"
                        >

                            Returning to Financial
                            Onboarding...

                        </div>

                    </div>

                )

            }
            
            {currentStep === 1 && (

                <div
                    className="scr34-card"
                    style={{
                        background: "rgba(255,255,255,0.72)",
                        backdropFilter: "blur(16px)",
                        WebkitBackdropFilter: "blur(16px)",
                        border: "1px solid rgba(255,255,255,0.55)",
                        boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                    }}
                >

                    <h2>

                        Step 1 · Review Billing Policy

                    </h2>

                    <p>

                        Please review your maintenance
                        billing policy before proceeding.
                        This configuration has already
                        been finalized during Financial
                        Onboarding and is shown here for
                        confirmation only.

                    </p>

                    <div
                        style={{
                            marginTop: 28,
                        }}
                    >

                        <ReviewRow
                            label="Billing Frequency"
                            value="Monthly"
                        />

                        <ReviewRow
                            label="Billing Starts"
                            value={
                                context.billing_policy
                                    .billing_start_date
                            }
                        />

                        <ReviewRow
                            label="Payment Due"
                            value={`Day ${
                                context.billing_policy
                                    .due_day
                            } of every month`}
                        />

                        <ReviewRow
                            label="Grace Period"
                            value={`${
                                context.billing_policy
                                    .grace_days
                            } Days`}
                        />

                        <ReviewRow
                            label="Interest on Delay"
                            value={`${
                                context.billing_policy
                                    .interest_rules.rate
                            }% per annum`}
                        />

                        <ReviewRow
                            label="Late Payment Penalty"
                            value={`₹${
                                context.billing_policy
                                    .penalty_rules.amount
                            } after ${
                                context.billing_policy
                                    .penalty_rules.after_days
                            } days`}
                        />

                    </div>

                    <div
                        style={{
                            marginTop: "24px",
                            textAlign: "right",
                        }}
                    >

                        <button

                            style={{

                                minWidth: 128,

                                height: 34,

                                padding: "0 20px",

                                border: "none",

                                borderRadius: 10,

                                background: "#ea580c",

                                color: "#ffffff",

                                fontSize: 13,

                                fontWeight: 800,

                                cursor: "pointer",

                                boxShadow:
                                    "0 6px 12px rgba(234,88,12,.14)",

                            }}

                            onClick={() => {

                                setCurrentStep(2);

                            }}

                        >

                            Continue

                        </button>

                    </div>

                </div>

            )}

            {currentStep === 2 && (

                <div
                    className="scr34-card"
                    style={{
                        background: "rgba(255,255,255,0.72)",
                        backdropFilter: "blur(16px)",
                        WebkitBackdropFilter: "blur(16px)",
                        border: "1px solid rgba(255,255,255,0.55)",
                        boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                    }}
                >

                    <h2>

                        Step 2 · Confirm Maintenance Collection Account

                    </h2>

                    <p>

                        Select the bank account whose
                        details should appear on every
                        maintenance bill. Members will
                        use this account for all future
                        maintenance payments.

                    </p>

                    {

                        context.selected_account.selection_required ? (

                            <>

                                <select

                                    className="scr34-select"

                                    value={
                                        selectedAccountId ?? ""
                                    }

                                    onChange={(event) => {

                                        setSelectedAccountId(

                                            Number(
                                                event.target.value
                                            )

                                        );

                                    }}

                                >

                                    <option value="">

                                        Select Bank Account

                                    </option>

                                    {

                                        context.bank_accounts.map(

                                            (account: any) => (

                                                <option

                                                    key={account.id}

                                                    value={account.id}

                                                >

                                                    {account.name}

                                                    {" — "}

                                                    {account.bank_name}

                                                </option>

                                            )

                                        )

                                    }

                                </select>

                            </>

                        ) : (

                            <>

                                <strong>

                                    {

                                        context.selected_account
                                            .account.name

                                    }

                                </strong>

                                <br />

                                {

                                    context.selected_account
                                        .account.bank_name

                                }

                                <br />

                                A/c No.

                                {

                                    context.selected_account
                                        .account.account_number

                                }

                                <br />

                                IFSC :

                                {

                                    context.selected_account
                                        .account.ifsc

                                }

                                <br />

                                UPI :

                                {

                                    context.selected_account
                                        .account.upi_id

                                }

                            </>

                        )

                    }

                    <div
                        style={{
                            marginTop: "24px",
                            display: "flex",
                            justifyContent: "space-between",
                        }}
                    >

                        <button

                            style={{

                                minWidth: 128,

                                height: 34,

                                padding: "0 20px",

                                border: "1px solid #d1d5db",

                                borderRadius: 10,

                                background: "#ffffff",

                                color: "#374151",

                                fontSize: 13,

                                fontWeight: 700,

                                cursor: "pointer",

                            }}

                            onClick={() => {

                                setCurrentStep(1);

                            }}

                        >

                            ← Back

                        </button>

                        <button

                            style={{

                                minWidth: 128,

                                height: 34,

                                padding: "0 20px",

                                border: "none",

                                borderRadius: 10,

                                background: "#ea580c",

                                color: "#ffffff",

                                fontSize: 13,

                                fontWeight: 800,

                                cursor: "pointer",

                                boxShadow:
                                    "0 6px 12px rgba(234,88,12,.14)",

                            }}

                            onClick={() => {

                                if (

                                    context.selected_account.selection_required

                                    &&

                                    !selectedAccountId

                                ) {

                                    return;

                                }

                                setCurrentStep(3);

                            }}

                        >

                            Continue

                        </button>

                    </div>

                </div>

            )}

        {currentStep === 3 && (

            <div
                className="scr34-card"
                style={{
                    background: "rgba(255,255,255,0.72)",
                    backdropFilter: "blur(16px)",
                    WebkitBackdropFilter: "blur(16px)",
                    border: "1px solid rgba(255,255,255,0.55)",
                    boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                }}
            >

                <h2>

                    Step 3 · Verify Production Maintenance Bill

                </h2>

                <p
                    style={{
                        maxWidth: "620px",
                        margin: "0 auto 24px auto",
                        textAlign: "center",
                        color: "#6b7280",
                        lineHeight: 1.7,
                    }}
                >

                    Review the exact maintenance bill
                    that your members will receive
                    every month before activating
                    Monthly Billing.

                </p>

                <div
                    style={{
                        maxWidth: "620px",
                        margin: "0 auto 28px auto",
                        background: "#f8fafc",
                        border: "1px solid #e5e7eb",
                        borderRadius: "10px",
                        padding: "22px",
                    }}
                >

                    <div
                        style={{
                            fontWeight: 700,
                            marginBottom: "18px",
                            color: "#111827",
                        }}
                    >

                        Verify the following

                    </div>

                    <ReviewRow
                        label="Billing Calculations"
                        value="Ready"
                    />

                    <ReviewRow
                        label="Collection Bank Account"
                        value="Verified"
                    />

                    <ReviewRow
                        label="UPI QR Code"
                        value="Included"
                    />

                    <ReviewRow
                        label="Member Information"
                        value="Verified"
                    />

                    <ReviewRow
                        label="Bill Presentation"
                        value="Production Ready"
                    />

                </div>

                <br />

                <div
                    style={{
                        maxWidth: "620px",
                        margin: "0 auto 24px auto",
                        textAlign: "center",
                    }}
                >

                    <div
                        style={{
                            fontSize: "15px",
                            color: "#6b7280",
                            marginBottom: "8px",
                        }}
                    >

                        Preview Status

                    </div>

                    <div
                        style={{
                            fontSize: "20px",
                            fontWeight: 700,
                            color: previewGenerated
                                ? "#16a34a"
                                : "#ea580c",
                        }}
                    >

                        {

                            previewGenerated

                                ? "✓ Latest Production Preview Ready"

                                : "Preview Not Generated"

                        }

                    </div>

                </div>

                <button

                    style={{

                        minWidth: 128,

                        height: 34,

                        padding: "0 20px",

                        border: "none",

                        borderRadius: 10,

                        background: "#ea580c",

                        color: "#ffffff",

                        fontSize: 13,

                        fontWeight: 800,

                        cursor: "pointer",

                        boxShadow:
                            "0 6px 12px rgba(234,88,12,.14)",

                    }}

                    onClick={async () => {

                        if (!societyId) {

                            return;

                        }

                        const response =
                            await fetch(

                                `${API_BASE}/maintenance-bill-preview/`,

                                {

                                    method: "POST",

                                    headers: {

                                        "Content-Type":
                                            "application/json",

                                    },

                                    body: JSON.stringify({

                                        society_id:
                                            Number(
                                                societyId,
                                            ),

                                    }),

                                },

                            );

                        const data =
                            await response.json();

                        if (

                            data.status === "success"

                        ) {

                            setPreviewGenerated(
                                true,
                            );


                            window.open(

                                `http://127.0.0.1:8000${data.pdf_url}`,

                                "_blank",

                            );

                        }

                    }}

                >

                    Generate Latest Production Preview

                </button>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginTop: "24px",
                    }}
                >

                    <button

                        style={{

                            minWidth: 128,

                            height: 34,

                            padding: "0 20px",

                            border: "1px solid #d1d5db",

                            borderRadius: 10,

                            background: "#ffffff",

                            color: "#374151",

                            fontSize: 13,

                            fontWeight: 700,

                            cursor: "pointer",

                        }}

                        onClick={() => {

                            setCurrentStep(2);

                        }}

                    >

                        ← Back

                    </button>

                    <button

                        style={{

                            minWidth: 128,

                            height: 34,

                            padding: "0 20px",

                            border: "none",

                            borderRadius: 10,

                            background: "#ea580c",

                            color: "#ffffff",

                            fontSize: 13,

                            fontWeight: 800,

                            cursor: "pointer",

                            boxShadow:
                                "0 6px 12px rgba(234,88,12,.14)",

                        }}

                        disabled={!previewGenerated}

                        onClick={() => {

                            setCurrentStep(4);

                        }}

                    >

                        Continue

                    </button>

                </div>

            </div>

        )}

        {currentStep === 4 && (

            <div
                className="scr34-card"
                style={{
                    background: "rgba(255,255,255,0.72)",
                    backdropFilter: "blur(16px)",
                    WebkitBackdropFilter: "blur(16px)",
                    border: "1px solid rgba(255,255,255,0.55)",
                    boxShadow: "0 14px 40px rgba(15,23,42,.08)",
                }}
            >

                <h2>

                    Step 4 · Activate Monthly Billing

                </h2>

                <p>

                    You have successfully reviewed the
                    billing configuration, confirmed the
                    maintenance collection account and
                    verified the production maintenance
                    bill.

                </p>

                <div className="scr34-preview-note">

                    <strong>

                        Activation Declaration

                    </strong>

                    <p>

                        By activating Monthly Billing,
                        you confirm that the billing
                        policy, payment instructions,
                        maintenance collection account
                        and production maintenance bill
                        have been reviewed and approved.

                    </p>

                </div>

                <div
                    style={{
                        marginTop: 24,
                        padding: 18,
                        border: "1px solid #fde68a",
                        borderRadius: 10,
                        background: "#fffbeb",
                    }}
                >

                    <strong>

                        Society Communications

                    </strong>

                    <p
                        style={{
                            marginTop: 8,
                            color: "#6b7280",
                            lineHeight: 1.6,
                        }}
                    >

                        SocietyOS requires one official
                        Society Email Address before the
                        Communications Engine can be
                        activated.

                    </p>

                    {

                        officialEmail ? (

                            <div
                                style={{
                                    marginTop: 14,
                                    fontWeight: 700,
                                    color: "#15803d",
                                }}
                            >

                                ✓ Official Email

                                <br />

                                {officialEmail}

                            </div>

                        ) : (

                            <div
                                style={{
                                    marginTop: 16,
                                }}
                            >

                                <input

                                    type="email"

                                    value={officialEmail}

                                    placeholder="Enter Official Society Email"

                                    onChange={(e) => {

                                        setOfficialEmail(
                                            e.target.value
                                        );

                                    }}

                                />

                            </div>

                        )

                    }

                </div>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginTop: "24px",
                    }}
                >

                    <button

                       style={{

                        minWidth: 128,

                        height: 34,

                        padding: "0 20px",

                        border: "1px solid #d1d5db",

                        borderRadius: 10,

                        background: "#ffffff",

                        color: "#374151",

                        fontSize: 13,

                        fontWeight: 700,

                        cursor: "pointer",

                    }}

                        onClick={() => {

                            setCurrentStep(3);

                        }}

                    >

                        ← Back

                    </button>

                    <button

                        style={{

                            minWidth: 128,

                            height: 34,

                            padding: "0 20px",

                            border: "none",

                            borderRadius: 10,

                            background: "#ea580c",

                            color: "#ffffff",

                            fontSize: 13,

                            fontWeight: 800,

                            cursor: "pointer",

                            boxShadow:
                                "0 6px 12px rgba(234,88,12,.14)",

                        }}

                        onClick={async () => {

                            if (!societyId) {

                                return;

                            }

                            const response =
                                await fetch(

                                    `${API_BASE}/scr34-save/`,

                                    {

                                        method: "POST",

                                        headers: {

                                            "Content-Type":
                                                "application/json",

                                        },

                                        body: JSON.stringify({

                                            society_id:
                                                Number(
                                                    societyId,
                                                ),

                                            bank_account_id:
                                                selectedAccountId,

                                            official_email:
                                                officialEmail,

                                        }),

                                    },

                                );

                            const data =
                                await response.json();

                            if (

                                data.status === "success"

                            ) {

                                setActivationComplete(
                                    true,
                                );

                                setTimeout(() => {

                                    navigate(
                                        "/financial-onboarding"
                                    );

                                }, 2500);

                            }

                        }}

                    >

                        Activate Monthly Billing

                    </button>

                </div>

            </div>

        )} 
            </div>

        </AppShell>

    );

}
