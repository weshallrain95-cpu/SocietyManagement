import { createContext, useContext, useState, ReactNode } from "react";

type Society = {
  id: number;
  name: string;
};

type SocietyContextType = {
  society: Society | null;
  setSociety: (s: Society) => void;
};

const SocietyContext = createContext<SocietyContextType | undefined>(undefined);

export function SocietyProvider({ children }: { children: ReactNode }) {
  const [society, setSociety] = useState<Society | null>(null);

  return (
    <SocietyContext.Provider value={{ society, setSociety }}>
      {children}
    </SocietyContext.Provider>
  );
}

export function useSociety() {
  const ctx = useContext(SocietyContext);
  if (!ctx) throw new Error("useSociety must be used within SocietyProvider");
  return ctx;
}
