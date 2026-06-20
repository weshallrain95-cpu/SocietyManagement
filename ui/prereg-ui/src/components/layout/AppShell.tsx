import Sidebar from "./Sidebar";
import logo from "../../assets/logo.png";
import { useSociety } from "../../context/SocietyContext";
import { useNavigate } from "react-router-dom";

export default function AppShell({ children }: any) {
  const { society, updateSociety } = useSociety();
  const navigate = useNavigate();

  const handleLogout = () => {
    // 🔥 Clear React state
    updateSociety(null);

    // 🔥 Clear ALL persistent storage
    localStorage.clear();

    // 🔥 Clear tab storage (future-proof)
    sessionStorage.clear();

    // 🔥 Hard reset app
    window.location.href = "/";
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div
        style={{
          flex: 1,
          background:
            `
            radial-gradient(
              circle at top left,
              rgba(251,191,36,0.12),
              transparent 35%
            ),

            radial-gradient(
              circle at top right,
              rgba(59,130,246,0.10),
              transparent 35%
            ),

            linear-gradient(
              180deg,
              #f8fafc 0%,
              #eef2ff 100%
            )
            `,
          minHeight: "100vh",
        }}
      >
        {/* TOP BAR */}
        <div
          style={{
            height: 60,
            background: "white",
            borderBottom: "1px solid #e5e7eb",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 20px",
          }}
        >
          {/* LEFT — UNCHANGED */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <img src={logo} style={{ height: 30 }} />
            <span style={{ fontSize: 13, color: "#6b7280" }}>
              Delivering a paradigm shift
            </span>
          </div>

          {/* RIGHT — UPGRADED */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ fontSize: 13, color: "#6b7280" }}>
              {society?.name || "Logged in"}
            </div>

            {console.log("FULL SOCIETY OBJECT", society)}
            {society && (
              <div style={{ fontSize: 12 }}>
                {society.is_registered ? (
                  <span style={{ color: "#374151" }}>
                    Reg No: {society.registration_number || "-"}
                  </span>
                ) : (
                  <span style={{ color: "#dc2626" }}>
                    Your society is unregistered!
                  </span>
                )}
              </div>
            )}

            <div
              onClick={handleLogout}
              style={{
                fontSize: 13,
                color: "#ef4444",
                cursor: "pointer",
                fontWeight: 500,
              }}
            >
              Logout
            </div>
          </div>
        </div>

        {/* CONTENT — UNCHANGED */}
        <div style={{ padding: 30 }}>{children}</div>
      </div>
    </div>
  );
}