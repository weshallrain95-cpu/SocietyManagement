import { createContext, useContext, useEffect, useState } from "react";

const SocietyContext = createContext<any>(null);

export function SocietyProvider({ children }: any) {
  const [society, setSociety] = useState<any>(null);

  // 🔁 Load from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("society");
    if (stored) {
      setSociety(JSON.parse(stored));
    }
  }, []);

  // 💾 Save to localStorage
  const updateSociety = (data: any) => {
    setSociety(data);
    localStorage.setItem("society", JSON.stringify(data));
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
