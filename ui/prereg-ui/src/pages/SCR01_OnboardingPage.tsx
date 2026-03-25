import AppShell from "../components/layout/AppShell";
import { useForm, useWatch } from "react-hook-form";
import { useNavigate } from "react-router-dom";

export default function OnboardingPage() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm();

  const societyStatus = useWatch({
    control,
    name: "society_status",
  });

  const onSubmit = async (data: any) => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/society/signup/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        }
      );

      let result: any = {};
      try {
        result = await response.json();
      } catch {}

      if (response.ok) {
        navigate("/verify");
      } else {
        alert(result.error || "Signup failed");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
  };

  const fieldBlock = { marginBottom: 16 };

  return (
    <AppShell>
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 20 }}>
        <div
          style={{
            background: "white",
            padding: 30,
            borderRadius: 14,
            boxShadow: "0 6px 20px rgba(0,0,0,0.05)",
          }}
        >
          <h1 style={{ fontSize: 26, fontWeight: 600 }}>
            Create Your Society on SocietyOS
          </h1>

          <p style={{ color: "#6b7280", marginBottom: 25 }}>
            Set up your society and start managing it digitally.
          </p>

          <form onSubmit={handleSubmit(onSubmit)}>

            {/* YOUR DETAILS */}
            <div style={{ marginBottom: 30 }}>
              <h3>Your Details</h3>

              <div style={fieldBlock}>
                <div>Full Name *</div>
                <input {...register("name", { required: "Name is required" })} />
                {errors.name && <p className="error">{errors.name.message as string}</p>}
              </div>

              <div style={fieldBlock}>
                <div>Mobile Number *</div>
                <input
                  {...register("mobile", {
                    required: "Mobile required",
                    pattern: {
                      value: /^[0-9]{10}$/,
                      message: "Enter valid 10 digit number",
                    },
                  })}
                />
                {errors.mobile && <p className="error">{errors.mobile.message as string}</p>}
              </div>

              <div style={fieldBlock}>
                <div>Email ID *</div>
                <input {...register("email", { required: "Email required" })} />
                {errors.email && <p className="error">{errors.email.message as string}</p>}
              </div>

              {/* DESIGNATION */}
              <div style={fieldBlock}>
                <div>Your Current Designation *</div>

                {[
                  { label: "Chairman", value: "CHAIRMAN" },
                  { label: "Committee Member", value: "COMMITTEE_MEMBER" },
                  { label: "Other", value: "OTHER" },
                ].map((item) => (
                  <div
                    key={item.value}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      marginTop: 8,
                    }}
                  >
                    <input
                      type="radio"
                      value={item.value}
                      {...register("designation", { required: true })}
                    />
                    <span>{item.label}</span>
                  </div>
                ))}

                {errors.designation && <p className="error">Select designation</p>}
              </div>
            </div>

            {/* SOCIETY DETAILS */}
            <div style={{ marginBottom: 30 }}>
              <h3>Society Details</h3>

              <div style={fieldBlock}>
                <input
                  placeholder="Society Name"
                  {...register("society_name", { required: "Required" })}
                />
                {errors.society_name && <p className="error">{errors.society_name.message as string}</p>}
              </div>

              <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
                <select {...register("state")}>
                  <option>Maharashtra</option>
                </select>

                <select {...register("district", { required: "Select district" })}>
                  <option value="">Select</option>
                  <option>Mumbai City</option>
                  <option>Thane</option>
                  <option>Pune</option>
                </select>
              </div>

              {/* STATUS */}
              <div style={fieldBlock}>
                <div>Current status of the society</div>

                {[
                  { label: "Not registered", value: "NOT_REGISTERED" },
                  { label: "Registered not operational", value: "REGISTERED_NOT_OPERATIONAL" },
                  { label: "Operational", value: "REGISTERED_OPERATIONAL" },
                ].map((item) => (
                  <div
                    key={item.value}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      marginTop: 8,
                    }}
                  >
                    <input
                      type="radio"
                      value={item.value}
                      {...register("society_status", { required: true })}
                    />
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>

              {/* CONDITIONAL */}
              {(societyStatus === "REGISTERED_NOT_OPERATIONAL" ||
                societyStatus === "REGISTERED_OPERATIONAL") && (
                <div style={{ marginTop: 20 }}>
                  <div style={fieldBlock}>
                    <div>Registration Number</div>
                    <input {...register("registration_number")} />
                  </div>

                  <div style={fieldBlock}>
                    <div>Registration Date</div>
                    <input type="date" {...register("registration_date")} />
                  </div>
                </div>
              )}
            </div>

            {/* RESIDENCE */}
            <div style={{ marginBottom: 30 }}>
              <h3>Residence Details</h3>

              <div style={fieldBlock}>
                <select {...register("wing")}>
                  <option value="">Select Wing</option>
                  <option>Single Building</option>
                  <option>Wing A</option>
                </select>
              </div>

              <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
                <input placeholder="Floor" {...register("floor")} />
                <input placeholder="Flat Number" {...register("flat_number")} />
              </div>

              <div style={{ display: "flex", gap: 10 }}>
                <select {...register("flat_type")}>
                  <option value="">Type</option>
                  <option>1BHK</option>
                  <option>2BHK</option>
                </select>

                <input placeholder="Area" {...register("flat_area")} />
              </div>
            </div>

            {/* CTA */}
            <button
              type="submit"
              style={{
                background: "#f97316",
                color: "white",
                padding: "12px 20px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
              }}
            >
              Continue →
            </button>
          </form>
        </div>
      </div>
    </AppShell>
  );
}
