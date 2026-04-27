import AppShell from "../components/layout/AppShell";
import { useForm, useWatch } from "react-hook-form";
import { useNavigate } from "react-router-dom";

/* ================= STYLES ================= */

const pageWrapper = { padding: 20 };
const container = { maxWidth: 700, margin: "0 auto" };
const header = { marginBottom: 20 };
const title = { fontSize: 26, fontWeight: 600 };
const subtitle = { color: "#6b7280" };
const card = {
  background: "white",
  padding: 25,
  borderRadius: 14,
  border: "1px solid #e5e7eb",
};
const fieldBlock = { marginBottom: 16 };
const input = {
  width: "100%",
  padding: "10px",
  borderRadius: 8,
  border: "1px solid #d1d5db",
};
const primaryBtn = {
  background: "#f97316",
  color: "white",
  border: "none",
  padding: "12px 18px",
  borderRadius: 8,
  cursor: "pointer",
};

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

  // ✅ CLEAN SUBMIT (NO FETCH, NO RESPONSE)
  const onSubmit = (data: any) => {
    navigate("/verify", {
      state: {
        mobile: data.mobile,
        flow: "CREATE",
        formData: data,
      },
    });
  };


  return (
    <AppShell>
  <div style={pageWrapper}>
    <div style={container}>
      <div style={card}>

        {/* HEADER */}
        <div style={header}>
          <h1 style={title}>Create Your Society on SocietyOS</h1>
          <p style={subtitle}>
            Set up your society and start managing it digitally.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>

          {/* YOUR DETAILS */}
          <div style={{ marginBottom: 30 }}>
            <h3>Your Details</h3>

            <div style={fieldBlock}>
              <div>Full Name *</div>
              <input style={input} {...register("name", { required: "Name is required" })} />
              {errors.name && <p className="error">{errors.name.message as string}</p>}
            </div>

            <div style={fieldBlock}>
              <div>Mobile Number *</div>
              <input
                style={input}
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
              <input style={input} {...register("email", { required: "Email required" })} />
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
                <div key={item.value} style={{ display: "flex", gap: 10, marginTop: 8 }}>
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
                style={input}
                placeholder="Society Name"
                {...register("society_name", { required: "Required" })}
              />
              {errors.society_name && <p className="error">{errors.society_name.message as string}</p>}
            </div>

            <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
              <select style={input} {...register("state")}>
                <option>Maharashtra</option>
              </select>

              <select style={input} {...register("district", { required: "Select district" })}>
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
                <div key={item.value} style={{ display: "flex", gap: 10, marginTop: 8 }}>
                  <input
                    type="radio"
                    value={item.value}
                    {...register("society_status", { required: true })}
                  />
                  <span>{item.label}</span>
                </div>
              ))}
            </div>

            {(societyStatus === "REGISTERED_NOT_OPERATIONAL" ||
              societyStatus === "REGISTERED_OPERATIONAL") && (
              <div style={{ marginTop: 20 }}>
                <div style={fieldBlock}>
                  <div>Registration Number</div>
                  <input style={input} {...register("registration_number")} />
                </div>

                <div style={fieldBlock}>
                  <div>Registration Date</div>
                  <input style={input} type="date" {...register("registration_date")} />
                </div>
              </div>
            )}
          </div>

          {/* RESIDENCE */}
          <div style={{ marginBottom: 30 }}>
            <h3>Residence Details</h3>

            <div style={fieldBlock}>
              <select style={input} {...register("wing")}>
                <option value="">Select Wing</option>
                <option>Single Building</option>
                <option>Wing A</option>
              </select>
            </div>

            <div style={{ display: "flex", gap: 10, marginBottom: 16 }}>
              <input style={input} placeholder="Floor" {...register("floor")} />
              <input style={input} placeholder="Flat Number" {...register("flat_number")} />
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <select style={input} {...register("flat_type")}>
                <option value="">Type</option>
                <option>1BHK</option>
                <option>2BHK</option>
              </select>

              <input style={input} placeholder="Area" {...register("flat_area")} />
            </div>
          </div>

          {/* CTA */}
          <button type="submit" style={primaryBtn}>
            Continue →
          </button>

        </form>
      </div>
    </div>
  </div>
</AppShell>
  );
}
