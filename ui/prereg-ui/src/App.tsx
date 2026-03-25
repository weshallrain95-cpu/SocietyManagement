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

import { SocietyProvider } from "./context/SocietyContext";

function App() {
  return (
    <SocietyProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/verify" element={<OTPPage />} />
          <Route path="/select-society" element={<SelectSociety />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/structure" element={<StructurePage />} />
          <Route path="/structure-groups" element={<GroupEnginePage />} />
          <Route path="/structure-preview" element={<StructurePreviewPage />} />
          <Route path="/excel-upload-placeholder" element={<ExcelFlowPage />} />
        </Routes>
      </BrowserRouter>
    </SocietyProvider>
  );
}

export default App;
