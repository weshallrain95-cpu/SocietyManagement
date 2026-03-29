import { BrowserRouter, Routes, Route } from "react-router-dom";

import { LandingPage } from "./pages/SCR00_LandingPage";
import OnboardingPage from "./pages/SCR01_OnboardingPage";
import LoginPage from "./pages/SCR03_LoginPage";
import OTPPage from "./pages/SCR02_OTPPage";
import SelectSociety from "./pages/SCR04_SelectSociety";
import Dashboard from "./pages/Dashboard";
import StructurePage from "./pages/SCR05_StructurePage";
import GroupEnginePage from "./pages/SCR06_GroupEngine";
import StructurePreviewPage from "./pages/SCR07_StructurePreviewPage";
import ExcelFlowPage from "./pages/SCR08_ExcelFlowPage";
import OwnershipRefinementPage from "./pages/SCR09_OwnershipRefinementPage";

import { SocietyProvider } from "./context/SocietyContext";

// ✅ NEW IMPORT
import OnboardingGuard from "./guards/OnboardingGuard";

function App() {
  return (
    <SocietyProvider>
      <BrowserRouter>
        <Routes>

          {/* 🌐 PUBLIC ROUTES (NO GUARD) */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/verify" element={<OTPPage />} />
          <Route path="/select-society" element={<SelectSociety />} />
          <Route path="/ownership-refinement" element={<OwnershipRefinementPage />} />
          {/* 🔒 PROTECTED ROUTES (WITH GUARD) */}
          <Route
            path="/dashboard"
            element={
              <OnboardingGuard>
                <Dashboard />
              </OnboardingGuard>
            }
          />

          <Route
            path="/structure"
            element={
              <OnboardingGuard>
                <StructurePage />
              </OnboardingGuard>
            }
          />

          <Route
            path="/structure-groups"
            element={
              <OnboardingGuard>
                <GroupEnginePage />
              </OnboardingGuard>
            }
          />

          <Route
            path="/structure-preview"
            element={
              <OnboardingGuard>
                <StructurePreviewPage />
              </OnboardingGuard>
            }
          />

          <Route
            path="/excel-upload-placeholder"
            element={
              <OnboardingGuard>
                <ExcelFlowPage />
              </OnboardingGuard>
            }
          />

        </Routes>
      </BrowserRouter>
    </SocietyProvider>
  );
}

export default App;