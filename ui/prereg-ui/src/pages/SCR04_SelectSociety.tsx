import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import { useSociety } from "../context/SocietyContext";

export default function SelectSociety() {
  const navigate = useNavigate();
  const location = useLocation();
  const { updateSociety } = useSociety();

  const societies = location.state?.societies || [];

  // 🚨 SAFETY — direct access protection
  useEffect(() => {
    if (!societies || societies.length === 0) {
      navigate("/");
    }

    // ✅ AUTO REDIRECT IF ONLY ONE (extra safety)
    if (societies.length === 1) {
      const s = societies[0];

      (async () => {
        try {
          const res = await fetch(
            `/api/society/onboarding/status/?society_id=${s.id}`
          );
          const status = await res.json();

          const updatedSociety = {
            ...s,
            onboarding: {
              ...s.onboarding,
              stage: status.stage,
            },
          };

          updateSociety(updatedSociety);
          navigate("/dashboard");
        } catch (err) {
          console.error("Failed to fetch onboarding status", err);

          // fallback (original behavior)
          updateSociety(s);
          navigate("/dashboard");
        }
      })();
    }
  }, [societies, navigate, updateSociety]);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: 500,
          background: "white",
          padding: 30,
          borderRadius: 14,
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
        }}
      >
        {/* LOGO */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <img src={logo} style={{ height: 40 }} />
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            Delivering a paradigm shift
          </div>
        </div>

        {/* TITLE */}
        <h2 style={{ textAlign: "center", marginBottom: 20 }}>
          Select Your Society
        </h2>

        {/* EMPTY STATE */}
        {societies.length === 0 && (
          <p style={{ textAlign: "center" }}>
            No societies found for this account.
          </p>
        )}

        {/* LIST */}
        {societies.map((s: any) => (
          <div
            key={s.id}
            onClick={async () => {
              try {
                const res = await fetch(
                  `/api/society/onboarding/status/?society_id=${s.id}`
                );
                const status = await res.json();

                const updatedSociety = {
                  ...s,
                  onboarding: {
                    ...s.onboarding,
                    stage: status.stage,
                  },
                };

                updateSociety(updatedSociety);
                navigate("/dashboard");
              } catch (err) {
                console.error("Failed to fetch onboarding status", err);

                // fallback (original behavior)
                updateSociety(s);
                navigate("/dashboard");
              }
            }}
            style={{
              padding: 15,
              border: "1px solid #e5e7eb",
              borderRadius: 10,
              marginBottom: 10,
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget.style.background = "#f9fafb");
            }}
            onMouseLeave={(e) => {
              (e.currentTarget.style.background = "white");
            }}
          >
            <div style={{ fontWeight: 600 }}>{s.name}</div>

            <div style={{ fontSize: 12, color: "#6b7280" }}>
              Stage: {s.onboarding?.stage || "—"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
