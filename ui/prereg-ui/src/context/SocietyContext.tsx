import { createContext, useContext, useEffect, useState } from "react";

const SocietyContext = createContext<any>(null);

export function SocietyProvider({ children }: any) {
  const [society, setSociety] = useState<any>(null);

  // 🔁 Load from localStorage (SAFE)
  useEffect(() => {
    try {
      const stored = localStorage.getItem("society");

      if (stored && stored !== "undefined" && stored !== "null") {
        const parsed = JSON.parse(stored);

        if (parsed && parsed.id) {
          setSociety(parsed);
          localStorage.setItem("society_id", parsed.id);
        }
      }
    } catch (err) {
      console.error("Society parse error:", err);

      // 🔥 CLEAN CORRUPTED DATA
      localStorage.removeItem("society");
      localStorage.removeItem("society_id");
    }
  }, []);

  // 💾 Save
  const updateSociety = (data: any) => {
    try {
      setSociety(data);
      localStorage.setItem("society", JSON.stringify(data));
      localStorage.setItem("society_id", data?.id);
    } catch (err) {
      console.error("Society save error:", err);
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
