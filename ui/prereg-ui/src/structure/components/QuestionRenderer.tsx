export function QuestionRenderer({ step, dispatch }: any) {
  switch (step) {
    case "STRUCTURE_TYPE":
      return (
        <div>
          <button onClick={() => dispatch({ type: "SET_STRUCTURE_TYPE", payload: "SINGLE" })}>
            Single Building
          </button>
          <button onClick={() => dispatch({ type: "SET_STRUCTURE_TYPE", payload: "MULTI" })}>
            Multiple Wings
          </button>
        </div>
      )

    case "WING_COUNT":
      return (
        <input
          type="number"
          placeholder="Number of wings"
          onBlur={(e) =>
            dispatch({ type: "SET_WING_COUNT", payload: Number(e.target.value) })
          }
        />
      )

    case "FLOORS":
      return (
        <input
          type="number"
          placeholder="Floors"
          onBlur={(e) =>
            dispatch({ type: "SET_FLOORS", payload: Number(e.target.value) })
          }
        />
      )

    case "FLATS_PER_FLOOR":
      return (
        <input
          type="number"
          placeholder="Flats per floor"
          onBlur={(e) =>
            dispatch({ type: "SET_FLATS_PER_FLOOR", payload: Number(e.target.value) })
          }
        />
      )

    case "AREA":
      return (
        <input
          type="number"
          placeholder="Flat area"
          onBlur={(e) =>
            dispatch({
              type: "SET_AREA",
              payload: { area: Number(e.target.value), unit: "SQFT" }
            })
          }
        />
      )

    default:
      return null
  }
}