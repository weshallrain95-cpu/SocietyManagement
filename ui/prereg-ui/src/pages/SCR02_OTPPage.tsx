import { useForm } from "react-hook-form";
import { useNavigate, useLocation } from "react-router-dom";
import logo from "../assets/logo.png";
import { useEffect } from "react";
import { useSociety } from "../context/SocietyContext";

export default function OTPPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { updateSociety } = useSociety();

  const mobile = location.state?.mobile;
  const flow = location.state?.flow;
  const formData = location.state?.formData;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  // 🚨 SAFETY
  useEffect(() => {
    if (!mobile || !flow) {
      navigate("/");
    }
  }, [mobile, flow, navigate]);

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

      if (!response.ok) {
        alert(result.error || "Invalid OTP");
        return;
      }

      const societies = result.societies || [];

      // =========================
      // 🟠 CREATE FLOW
      // =========================
      if (flow === "CREATE") {
        try {
          const signupRes = await fetch(
            "http://127.0.0.1:8000/api/society/signup/",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                ...formData,
                mobile,
              }),
            }
          );

          const signupResult = await signupRes.json();

          if (!signupRes.ok) {
            alert(signupResult.error || "Signup failed");
            return;
          }

          // Save society
          if (signupResult.society) {
            const s = signupResult.society;

            // 🔥 COMPLETE CONTEXT (MANDATORY)
            localStorage.setItem("society", JSON.stringify(s));
            localStorage.setItem("society_id", String(s.id));
          }
          
          // Continue onboarding
          window.location.href = "/structure";
          return;

        } catch (err) {
          console.error(err);
          alert("Signup failed");
          return;
        }
      }

      // =========================
      // 🔵 LOGIN FLOW (FINAL)
      // =========================
      if (flow === "LOGIN") {

        // 🔥 RESET SESSION (CRITICAL)
        localStorage.clear();
        sessionStorage.clear();
        
        if (societies.length === 0) {
          alert("No societies found. Please create one.");
          navigate("/");
          return;
        }

        if (societies.length === 1) {
          const s = societies[0];

          localStorage.setItem("society", JSON.stringify(s));
          localStorage.setItem("society_id", String(s.id));

          // 🔥 FETCH STAGE (MANDATORY)
        
          const updated = await updateSociety(s);

          const stage = updated?.onboarding?.stage;

          switch (stage) {
            case "STRUCTURE_PENDING":
              window.location.href = "/structure";
              return;

            case "OWNERSHIP_PENDING":
              navigate("/excel-upload-placeholder");
              return;

            case "OWNERSHIP_REFINEMENT_PENDING":
              navigate("/ownership-refinement");
              return;

            case "OPERATIONS_PENDING":
              navigate("/operations");
              return;

            case "BYLAWS_PENDING":
              navigate("/bylaws");
              return;

            case "SHARE_CERTIFICATES_PENDING":
              navigate("/operations");
              return;

            case "OPERATIONAL_RULES_PENDING":
              navigate("/operations");
              return;

            case "OPERATIONS_COMPLETE":
              navigate("/operations");
              return;

            case "ONBOARDING_COMPLETE":
              navigate("/dashboard");
              return;

            default:
              console.error("Unhandled stage:", stage);
              alert("Invalid onboarding state");
          }
        }

        if (societies.length > 1) {
          navigate("/select-society", {
            state: { societies },
          });
          return;
        }
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
          <div style={{ marginBottom: 10 }}>
            OTP <span style={{ color: "red" }}>*</span>
          </div>

          <input
            placeholder="Enter 6 digit OTP"
            maxLength={6}
            style={{
              width: "100%",
              padding: "12px",
              borderRadius: 8,
              border: "1px solid #d1d5db",
            }}
            {...register("otp", {
              required: "OTP is required",
              pattern: {
                value: /^[0-9]{4,6}$/,
                message: "Enter valid OTP",
              },
            })}
          />

          {errors.otp && (
            <p style={{ color: "red", fontSize: 13 }}>
              {errors.otp.message as string}
            </p>
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