import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import {
  FileText,
  Eye,
  Scale,
  Building,
  User
} from "lucide-react";

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div style={{ background: "#f5f7fb", minHeight: "100vh" }}>

      {/* HEADER */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 40px",
          background: "white",
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        {/* LEFT */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <img
            src={logo}
            alt="ShiftIT"
            style={{ height: 42, objectFit: "contain" }}
          />
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            Delivering a paradigm shift
          </div>
        </div>

        {/* RIGHT */}
        <div style={{ display: "flex", gap: 12 }}>
          <button onClick={() => navigate("/onboarding")} style={primaryBtn}>
            Create Society
          </button>
          <button
            style={secondaryBtn}
            onClick={() => navigate("/login")}
          >
            Sign In
          </button>
        </div>
      </div>

      {/* HERO */}
      <div
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "70px 20px",
          textAlign: "center",
        }}
      >
        <h1 style={{ fontSize: 40, marginBottom: 20, fontWeight: 600 }}>
          A complete system to build and manage your housing society
        </h1>

        <p
          style={{
            color: "#6b7280",
            maxWidth: 650,
            margin: "0 auto",
            fontSize: 16,
          }}
        >
          From formation to registration, governance, and daily operations —
          ShiftIT provides a structured, transparent and legally aligned system
          to run your society.
        </p>

        <div
          style={{
            marginTop: 35,
            display: "flex",
            gap: 15,
            justifyContent: "center",
          }}
        >
          <button
            onClick={() => navigate("/onboarding")}
            style={primaryBtnLarge}
          >
            Create Your Society
          </button>

          <button style={secondaryBtnLarge}>
            Already Registered? Sign In
          </button>
        </div>
      </div>

      {/* USP SECTION */}
      <div
        style={{
          maxWidth: 1100,
          margin: "0 auto",
          padding: "20px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
          gap: 20,
        }}
      >
        <USPCard
          icon={<FileText size={20} />}
          title="Automated By-Laws"
          desc="Generate legally aligned by-laws tailored to your society."
        />

        <USPCard
          icon={<Eye size={20} />}
          title="Complete Transparency"
          desc="Every member gets visibility into decisions and finances."
        />

        <USPCard
          icon={<Scale size={20} />}
          title="Legal & Governance Engine"
          desc="Built-in workflows to ensure compliance and structure."
        />

        <USPCard
          icon={<Building size={20} />}
          title="Registration Assistance"
          desc="Guided journey from formation to official registration."
        />

        <USPCard
          icon={<User size={20} />}
          title="Single Admin Friendly"
          desc="Operate your entire society efficiently from one dashboard."
        />
      </div>

      {/* FOOTER */}
      <div
        style={{
          textAlign: "center",
          padding: 30,
          fontSize: 12,
          color: "#6b7280",
        }}
      >
        © ShiftIT
      </div>
    </div>
  );
}

/* ================= COMPONENT ================= */

function USPCard({ icon, title, desc }: any) {
  return (
    <div
      style={{
        background: "white",
        padding: 22,
        borderRadius: 14,
        boxShadow: "0 6px 20px rgba(0,0,0,0.05)",
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-4px)";
        e.currentTarget.style.boxShadow = "0 10px 30px rgba(0,0,0,0.08)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0px)";
        e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,0.05)";
      }}
    >
      <div style={{ marginBottom: 10, color: "#f97316" }}>
        {icon}
      </div>

      <div style={{ fontWeight: 600, marginBottom: 6 }}>
        {title}
      </div>

      <div style={{ fontSize: 14, color: "#6b7280" }}>
        {desc}
      </div>
    </div>
  );
}

/* ================= BUTTONS ================= */

const primaryBtn = {
  background: "#f97316",
  color: "white",
  border: "none",
  padding: "10px 16px",
  borderRadius: 8,
  cursor: "pointer",
};

const secondaryBtn = {
  background: "white",
  border: "1px solid #d1d5db",
  padding: "10px 16px",
  borderRadius: 8,
  cursor: "pointer",
};

const primaryBtnLarge = {
  ...primaryBtn,
  padding: "14px 24px",
  fontSize: 16,
};

const secondaryBtnLarge = {
  ...secondaryBtn,
  padding: "14px 24px",
  fontSize: 16,
};