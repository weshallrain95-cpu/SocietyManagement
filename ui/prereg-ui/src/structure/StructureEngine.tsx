import { useStructureEngine } from "./hooks/useStructureEngine"
import { QuestionRenderer } from "./components/QuestionRenderer"
import { SummaryCard } from "./components/SummaryCard"
import { CTASection } from "./components/CTASection"

export default function StructureEngine() {
  const { state, dispatch, currentStep } = useStructureEngine()

  return (
    <div
      style={{
        background: "white",
        padding: 30,
        borderRadius: 14,
        border: "1px solid #e5e7eb",
      }}
    >
      <SummaryCard state={state} />

      <QuestionRenderer
        step={currentStep}
        state={state}
        dispatch={dispatch}
      />

      {state.is_complete && <CTASection state={state} />}
    </div>
  )
}