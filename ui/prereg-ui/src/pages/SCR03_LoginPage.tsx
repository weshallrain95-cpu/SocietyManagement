import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";

/* ================= STYLES ================= */

const wrapper = {
  minHeight: "100vh",
  background: "#f5f7fb",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: 20,
};

const card = {
  width: "100%",
  maxWidth: 420,
  background: "white",
  padding: 30,
  borderRadius: 14,
  boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
};

const input = {
  width: "100%",
  padding: "12px",
  borderRadius: 8,
  border: "1px solid #d1d5db",
};

const button = {
  width: "100%",
  marginTop: 20,
  padding: "12px",
  background: "#f97316",
  color: "white",
  border: "none",
  borderRadius: 8,
  cursor: "pointer",
  fontWeight: 500,
};

export default function LoginPage() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // ✅ CLEAN SUBMIT (NO API CALL)
  const onSubmit = (data: any) => {
    navigate("/verify", {
      state: {
        mobile: data.mobile,
        flow: "LOGIN",
      },
    });
  };

  return (
    <div style={wrapper}>
      <div style={card}>

        {/* LOGO */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <img src={logo} style={{ height: 42 }} />
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            Delivering a paradigm shift
          </div>
        </div>

        {/* TITLE */}
        <h2 style={{ textAlign: "center", marginBottom: 10 }}>
          Sign In
        </h2>

        <p
          style={{
            textAlign: "center",
            color: "#6b7280",
            marginBottom: 25,
            fontSize: 14,
          }}
        >
          Enter your mobile number to continue
        </p>

        {/* FORM */}
        <form onSubmit={handleSubmit(onSubmit)}>

          <div style={{ marginBottom: 10 }}>
            Mobile Number <span style={{ color: "red" }}>*</span>
          </div>

          <input
            style={input}
            placeholder="Enter 10 digit mobile number"
            {...register("mobile", {
              required: "Mobile number is required",
              pattern: {
                value: /^[0-9]{10}$/,
                message: "Enter valid 10 digit mobile number",
              },
            })}
          />

          {errors.mobile && (
            <p style={{ color: "red", fontSize: 13 }}>
              {errors.mobile.message as string}
            </p>
          )}

          <button type="submit" style={button}>
            Continue →
          </button>

        </form>

        {/* FOOT NOTE */}
        <div
          style={{
            marginTop: 20,
            textAlign: "center",
            fontSize: 13,
            color: "#6b7280",
          }}
        >
          New here? Create your society first.
        </div>

      </div>
    </div>
  );
}