import React from "react"
import { structureReducer } from "../structure.reducer"
import { getNextStep } from "../structure.engine"

export function useStructureEngine() {
  const [state, dispatch] = React.useReducer(structureReducer, {
    is_complete: false
  })

  const currentStep = getNextStep(state)

  React.useEffect(() => {
    if (currentStep === "COMPLETE") {
      dispatch({ type: "MARK_COMPLETE" })
    }
  }, [currentStep])

  return { state, dispatch, currentStep }
}