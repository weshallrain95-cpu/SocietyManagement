export function SummaryCard({ state }: any) {
  if (!state.structure_type) return null

  return (
    <div style={{ background: "#eee", padding: 10, marginBottom: 10 }}>
      <div>✔ Structure: {state.structure_type}</div>
      {state.wing_count && <div>✔ Wings: {state.wing_count}</div>}
      {state.floors_per_wing && <div>✔ Floors: {state.floors_per_wing}</div>}
      {state.flats_per_floor && <div>✔ Flats/Floor: {state.flats_per_floor}</div>}
    </div>
  )
}