import { useForm } from "react-hook-form";
import { useNavigate, useLocation } from "react-router-dom";
import logo from "../assets/logo.png";
import { useEffect } from "react";

export default function OTPPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const mobile = location.state?.mobile;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // 🚨 SAFETY: if user lands directly → redirect
  useEffect(() => {
    if (!mobile) {
      navigate("/login");
    }
  }, [mobile, navigate]);

  const onSubmit = async (data: any) => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/society/verify-otp/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            mobile,
            otp: data.otp,
          }),
        }
      );

      let result: any = {};
      try {
        result = await response.json();
      } catch {}

      if (response.ok) {
        const societies = result.societies || [];

        // ✅ SINGLE SOCIETY → DIRECT DASHBOARD
        if (societies.length === 1) {
          localStorage.setItem("society", JSON.stringify(societies[0]));
          navigate("/dashboard");
          return;
        }

        // ✅ MULTIPLE SOCIETIES → SELECT PAGE
        if (societies.length > 1) {
          navigate("/select-society", {
            state: { societies },
          });
          return;
        }

        // ⚠️ EDGE CASE
        alert("No societies found for this user");
      } else {
        alert(result.error || "Invalid OTP");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
  };

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
          maxWidth: 420,
          background: "white",
          padding: 30,
          borderRadius: 14,
          boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
        }}
      >
        {/* LOGO */}
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <img src={logo} style={{ height: 42 }} />
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            Delivering a paradigm shift
          </div>
        </div>

        {/* TITLE */}
        <h2 style={{ textAlign: "center", marginBottom: 10 }}>
          Verify OTP
        </h2>

        <p
          style={{
            textAlign: "center",
            color: "#6b7280",
            marginBottom: 25,
            fontSize: 14,
          }}
        >
          Enter the OTP sent to <b>{mobile}</b>
        </p>

        {/* FORM */}
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="field-label">
            OTP <span className="required">*</span>
          </div>

          <input
            placeholder="Enter 6 digit OTP"
            maxLength={6}
            {...register("otp", {
              required: "OTP is required",
              pattern: {
                value: /^[0-9]{4,6}$/,
                message: "Enter valid OTP",
              },
            })}
          />

          {errors.otp && (
            <p className="error">{errors.otp.message as string}</p>
          )}

          <button
            type="submit"
            style={{
              width: "100%",
              marginTop: 20,
              padding: "12px",
              background: "#f97316",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              fontWeight: 500,
            }}
          >
            Verify →
          </button>
        </form>

        {/* RESEND */}
        <div
          style={{
            marginTop: 20,
            textAlign: "center",
            fontSize: 13,
            color: "#6b7280",
          }}
        >
          Didn’t receive OTP?{" "}
          <span style={{ color: "#f97316", cursor: "pointer" }}>
            Resend
          </span>
        </div>
      </div>
    </div>
  );
}