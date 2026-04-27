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
          background: "#f5f7fb",
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
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            <div style={{ fontSize: 13, color: "#6b7280" }}>
              {society?.name || "Logged in"}
            </div>

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