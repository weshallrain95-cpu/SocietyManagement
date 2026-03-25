export function getNextStep(state: any) {
  if (!state.structure_type) return "STRUCTURE_TYPE"

  if (state.structure_type === "MULTI" && !state.wing_count)
    return "WING_COUNT"

  if (state.structure_type === "MULTI" && !state.wing_naming)
    return "WING_NAMING"

  if (
    state.structure_type === "MULTI" &&
    state.wing_naming === "CUSTOM" &&
    !state.wing_names
  )
    return "WING_NAMES"

  if (state.uniform_wings === undefined) return "UNIFORM_WINGS"

  if (!state.floors_per_wing) return "FLOORS"

  if (state.uniform_flats === undefined) return "UNIFORM_FLATS"

  if (!state.flats_per_floor) return "FLATS_PER_FLOOR"

  if (!state.flat_numbering) return "FLAT_NUMBERING"

  if (!state.flat_area) return "AREA"

  return "COMPLETE"
}