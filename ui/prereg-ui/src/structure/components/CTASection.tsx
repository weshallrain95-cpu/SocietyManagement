export function CTASection({ state }: any) {
  const handleSubmit = async () => {
    const payload = {
      structure_type: state.structure_type,
      wing_count: state.wing_count,
      wing_naming: state.wing_naming,
      wing_names: state.wing_names,
      floors_per_wing: state.floors_per_wing,
      flats_per_floor: state.flats_per_floor,
      flat_numbering: state.flat_numbering,
      flat_area: state.flat_area,
      area_unit: state.area_unit,
    }

    await fetch("/api/onboarding/structure/generate/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })

    alert("Structure generated!")
  }

  return (
    <button onClick={handleSubmit} style={{ marginTop: 20 }}>
      Generate Structure
    </button>
  )
}