import { useEffect } from "react";
import { useSociety } from "../context/SocietyContext";
import { fetchSocieties } from "../api/societies";

export function SocietySelector() {
  const { society, setSociety } = useSociety();

  useEffect(() => {
    fetchSocieties().then((data) => {
      if (!society && data.societies.length > 0) {
        setSociety(data.societies[0]); // fallback A
      }
    });
  }, []);

  const onChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = Number(e.target.value);

    fetchSocieties().then((data) => {
      const found = data.societies.find((s: any) => s.id === selectedId);
      if (found) setSociety(found);
    });
  };

  return (
    <div style={{ marginBottom: "16px" }}>
      <label>Society: </label>

      <select value={society?.id || ""} onChange={onChange}>
        <option value="">Select society</option>
        {/* dynamic options */}
      </select>
    </div>
  );
}
