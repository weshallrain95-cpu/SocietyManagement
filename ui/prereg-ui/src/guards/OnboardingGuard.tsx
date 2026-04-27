import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

const OnboardingGuard = ({ children }: { children: React.ReactNode }) => {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const runGuard = async () => {
      try {
        const societyId = localStorage.getItem("society_id");

        // ✅ Allow public flow if no society selected
        if (!societyId) {
          setReady(true);
          return;
        }

        const res = await fetch(
          `/api/society/onboarding/status/?society_id=${societyId}`
        );
        
        const data = await res.json();
        const stage = data.stage;

        const path = window.location.pathname;


        // ===============================
        // 🔥 LAYER 2 — ACCESS CONTROL
        // ===============================

        // Governance
        if (!data.allowed_actions.can_create_committee) {
          if (path.startsWith("/committee")) {
            navigate("/operations", { replace: true });
            return;
          }
        }

        // Bylaws
        if (!data.allowed_actions.can_generate_bylaws) {
          if (path.startsWith("/bylaws")) {
            navigate("/operations", { replace: true });
            return;
          }
        }

        // Share Certificates
        if (
          !data.allowed_actions.can_access_share_certificates &&
          path.startsWith("/share-certificates")
        ) {
          navigate("/operations", { replace: true });
          return;
        }

        // Operational Rules
        if (
          !data.allowed_actions.can_configure_operational_rules &&
          path.startsWith("/operational-rules")
        ) {
          navigate("/operations", { replace: true });
          return;
        }

        // ===============================
        // 🔥 LAYER 1 — ENTRY ROUTING
        // ===============================

        if (stage === "STRUCTURE_PENDING") {
          if (!path.startsWith("/structure")) {
            navigate("/structure", { replace: true });
            return;
          }
        }

        if (stage === "OWNERSHIP_PENDING") {
          if (!path.includes("/excel-upload-placeholder")) {
            navigate("/excel-upload-placeholder", { replace: true });
            return;
          }
        }

        if (stage === "OWNERSHIP_REFINEMENT_PENDING") {
          if (!path.includes("/ownership-refinement")) {
            navigate("/ownership-refinement", { replace: true });
            return;
          }
        }

        // 🔥 Operations entry (covers everything post-committee)
        if (
          stage === "OPERATIONS_PENDING" ||
          stage === "BYLAWS_PENDING" ||
          stage === "SHARE_CERTIFICATES_PENDING" ||
          stage === "OPERATIONAL_RULES_PENDING" ||
          stage === "OPERATIONS_COMPLETE"
        ) {
          if (!path.startsWith("/operations")) {
            navigate("/operations", { replace: true });
            return;
          }
        }


        // ===============================
        // ✅ FINAL ALLOW
        // ===============================

        setReady(true);

            } catch (err) {
              console.error("Onboarding guard error:", err);
              setReady(true);
            }
          };

          runGuard();
        }, [navigate, location.pathname]);

  // ⛔ Prevent flicker while checking
  if (!ready) return null;

  return <>{children}</>;
};

export default OnboardingGuard;