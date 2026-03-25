export function structureReducer(state: any, action: any) {
  switch (action.type) {
    case "SET_STRUCTURE_TYPE":
      return {
        ...state,
        structure_type: action.payload,
        wing_count: action.payload === "SINGLE" ? 1 : undefined,
        wing_names: action.payload === "SINGLE" ? ["A"] : undefined
      }

    case "SET_WING_COUNT":
      return { ...state, wing_count: action.payload }

    case "SET_WING_NAMING":
      return { ...state, wing_naming: action.payload }

    case "SET_WING_NAMES":
      return { ...state, wing_names: action.payload }

    case "SET_UNIFORM_WINGS":
      return { ...state, uniform_wings: action.payload }

    case "SET_FLOORS":
      return { ...state, floors_per_wing: action.payload }

    case "SET_UNIFORM_FLATS":
      return { ...state, uniform_flats: action.payload }

    case "SET_FLATS_PER_FLOOR":
      return { ...state, flats_per_floor: action.payload }

    case "SET_FLAT_NUMBERING":
      return { ...state, flat_numbering: action.payload }

    case "SET_AREA":
      return {
        ...state,
        flat_area: action.payload.area,
        area_unit: action.payload.unit
      }

    case "MARK_COMPLETE":
      return { ...state, is_complete: true }

    default:
      return state
  }
}