import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";

export default function LoginPage() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data: any) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/society/mobile-exists/?mobile=${data.mobile}`
      );

      let result: any = {};

      try {
        result = await response.json();
      } catch {}

      if (!response.ok) {
        alert("Server error. Try again.");
        return;
      }

      if (!result.mobile_exists) {
        alert("No account found. Please create a society first.");
        return;
      }

      // ✅ PASS MOBILE TO OTP PAGE
      navigate("/verify", { state: { mobile: data.mobile } });

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
          Enter your registered mobile number to continue
        </p>

        {/* FORM */}
        <form onSubmit={handleSubmit(onSubmit)}>

          <div className="field-label">
            Mobile Number <span className="required">*</span>
          </div>

          <input
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
            <p className="error">{errors.mobile.message as string}</p>
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
