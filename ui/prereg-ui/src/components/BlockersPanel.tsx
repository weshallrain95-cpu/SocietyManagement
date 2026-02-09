import type { PreregistrationChecklistItem } from "../types/preregistration";


export function BlockersPanel({ blockers }: { blockers: PreregistrationBlocker[] }) {
  if (!blockers.length) {
    return null;
  }

  return (
    <div style={{ marginTop: "24px", padding: "16px", border: "1px solid red" }}>
      <strong>What’s Missing</strong>
      <ul>
        {blockers.map((b, idx) => (
          <li key={idx}>{b.message}</li>
        ))}
      </ul>
    </div>
  );
}
