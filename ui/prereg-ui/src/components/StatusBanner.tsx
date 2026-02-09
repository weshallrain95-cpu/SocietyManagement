export function StatusBanner({
  registrarReady,
  summary,
}: {
  registrarReady: boolean;
  summary: { total_mandatory: number; completed_mandatory: number };
}) {
  return (
    <div style={{ margin: "16px 0", padding: "12px", border: "1px solid #ccc" }}>
      <strong>
        {registrarReady ? "✅ Registrar-Ready" : "⏳ Not Ready for Registration"}
      </strong>
      <div>
        {summary.completed_mandatory} of {summary.total_mandatory} mandatory steps completed
      </div>
    </div>
  );
}
