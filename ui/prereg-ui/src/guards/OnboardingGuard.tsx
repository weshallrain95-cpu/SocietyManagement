import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const OnboardingGuard = ({ children }: { children: React.ReactNode }) => {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);

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

        // 🔥 CENTRALIZED ROUTING RULES

        if (stage === "STRUCTURE_PENDING") {
          const allowedPaths = [
            "/structure",
            "/structure-groups"
          ];

          const isAllowed = allowedPaths.some((p) => path.startsWith(p));

          if (!isAllowed) {
            navigate("/structure", { replace: true });
            return;
          }

          setReady(true);
          return;
        }

        // STRUCTURE_CREATED → /excel-upload-placeholder
        if (
          stage === "STRUCTURE_CREATED" &&
          !path.includes("/excel-upload-placeholder")
        ) {
          navigate("/excel-upload-placeholder");
          return;
        }

        // 🔥 OWNERSHIP UPLOAD (DATA-DRIVEN)
        if (data.allowed_actions.can_upload_ownership) {
          if (!path.includes("/excel-upload-placeholder")) {
            navigate("/excel-upload-placeholder");
            return;
          }

          setReady(true);
          return;
        }

        if (stage === "OWNERSHIP_REFINEMENT_PENDING") {
            if (!path.includes("/ownership-refinement")) {
                navigate("/ownership-refinement");
                return;
            }
       }
        
        if (data.allowed_actions.needs_refinement) {
            if (!path.includes("/ownership-refinement")) {
                navigate("/ownership-refinement");
                return;
            }
        }
       
        // ONBOARDING_COMPLETE → /dashboard
        if (stage === "ONBOARDING_COMPLETE") {
          const blockedPaths = [
            "/structure",
            "/structure-groups",
            "/structure-preview",
            "/excel-upload-placeholder",
            "/onboarding/excel",
            "/ownership"
          ];

          if (blockedPaths.some((p) => path.includes(p))) {
            navigate("/dashboard");
            return;
          }
        }

        // ✅ Allow access if already on correct page
        setReady(true);

      } catch (err) {
        console.error("Onboarding guard error:", err);
        setReady(true); // fail-safe
      }
    };

    runGuard();
  }, [navigate]);

  // ⛔ Prevent flicker while checking
  if (!ready) return null;

  return <>{children}</>;
};

export default OnboardingGuard;