import { createContext, useContext, useEffect, useState } from "react";

const SocietyContext = createContext<any>(null);

export function SocietyProvider({ children }: any) {
  const [society, setSociety] = useState<any>(null);

  // 🔁 Load from localStorage (SAFE) + 🔄 Refresh from API (NEW)
  useEffect(() => {
    const loadSociety = async () => {
      try {
        const stored = localStorage.getItem("society");

        if (stored && stored !== "undefined" && stored !== "null") {
          const parsed = JSON.parse(stored);

          if (parsed && parsed.id) {
            // ✅ Step 1 — initial load from localStorage
            setSociety(parsed);
            localStorage.setItem("society_id", parsed.id);

            // ✅ Step 2 — fetch latest onboarding status from backend
            try {
              const res = await fetch(
                `/api/society/onboarding/status/?society_id=${parsed.id}`
              );

              const status = await res.json();

              // ✅ Step 3 — merge updated stage into context
              const updatedSociety = {
                ...parsed,
                onboarding: {
                  ...parsed.onboarding,
                  stage: status.stage,
                },
              };

              setSociety(updatedSociety);
              localStorage.setItem("society", JSON.stringify(updatedSociety));
            } catch (err) {
              console.error("Failed to refresh onboarding status", err);
            }
          }
        }
      } catch (err) {
        console.error("Society parse error:", err);

        // 🔥 CLEAN CORRUPTED DATA
        localStorage.removeItem("society");
        localStorage.removeItem("society_id");
      }
    };

    loadSociety();
  }, []);

  // 💾 Save (UNCHANGED)
  const updateSociety = async (data: any) => {
    try {
      if (!data?.id) return;

      // 🔄 Fetch latest onboarding stage from backend
      const res = await fetch(
        `/api/society/onboarding/status/?society_id=${data.id}`
      );

      const status = await res.json();

      // 🔥 Override stage with backend truth
      const updatedSociety = {
        ...data,
        onboarding: {
          ...data.onboarding,
          stage: status.stage,
        },
      };

      setSociety(updatedSociety);
      localStorage.setItem("society", JSON.stringify(updatedSociety));
      localStorage.setItem("society_id", data.id);

    } catch (err) {
      console.error("Society save error:", err);

      // fallback (do not block login)
      setSociety(data);
      localStorage.setItem("society", JSON.stringify(data));
      localStorage.setItem("society_id", data?.id);
    }
  };

  return (
    <SocietyContext.Provider value={{ society, updateSociety }}>
      {children}
    </SocietyContext.Provider>
  );
}

// HOOK
export function useSociety() {
  return useContext(SocietyContext);
}
