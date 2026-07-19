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
import CommitteeSetupPage from "./pages/SCR11CommitteeSetup";
import SCR10OperationsHub from "./pages/SCR10OperationsHub";
import SCR12_BylawsEngine from "./pages/SCR12_BylawsEngine";
import SCR13_BylawsPreview from "./pages/SCR13_BylawsPreview";
import SCR14_BylawsGenerate from "./pages/SCR14_BylawsGenerate";
import SCR15_BylawsUpload from "./pages/SCR15_BylawsUpload";
import SCR16_ShareCertificates from "./pages/SCR16_ShareCertificates";
import SCR17OperationalRules from "./pages/SCR17OperationalRules";
import SCR18MemberGovernanceRules from "./pages/SCR18MemberGovernanceRules";
import SCR19FinancialControls from "./pages/SCR19FinancialControls";
import SCR20RegistrationTracker from "./pages/SCR20RegistrationTracker";
import SCR21FormA from "./pages/SCR21FormA";
import SCR22ProvisionalResolution from "./pages/SCR22ProvisionalResolution";
import SCR23PromoterConsent from "./pages/SCR23PromoterConsent";
import SCR24BuilderNotice from "./pages/SCR24BuilderNotice";
import SCR25BankAccountLetter from "./pages/SCR25BankAccountLetter";
import SCR26FirstGeneralMeeting from "./pages/SCR26FirstGeneralMeeting";
import SCR27RegistrarSubmission from "./pages/SCR27RegistrarSubmission";
import SCR28FinancialOnboarding from "./pages/SCR28FinancialOnboarding";
import SCR29BankAccounts from "./pages/SCR29BankAccounts";
import SCR30RevenueReceivablesSetup from "./pages/SCR30RevenueReceivablesSetup";
import SCR31MaintenanceGovernanceSetup from "./pages/SCR31MaintenanceGovernanceSetup";
import SCR32GovernanceIntelligence from "./pages/SCR32GovernanceIntelligence";
import SCR33GovernanceSimulation from "./pages/SCR33GovernanceSimulation";
import SCR34MaintenanceBillingActivation from "./pages/SCR34MaintenanceBillingActivation";
import KnowledgeCenter from "./pages/KnowledgeCenter";

import { SocietyProvider } from "./context/SocietyContext";

// ✅ NEW IMPORT
import _OnboardingGuard from "./guards/OnboardingGuard";




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
          <Route path="/committee/setup" element={<CommitteeSetupPage />} />
          <Route path="/operations" element={<SCR10OperationsHub />} />
          <Route path="/bylaws-test" element={<SCR12_BylawsEngine />} />
          <Route path="/bylaws/preview" element={<SCR13_BylawsPreview />} />
          <Route path="/bylaws/generate" element={<SCR14_BylawsGenerate />} />
          <Route path="/bylaws-upload" element={<SCR15_BylawsUpload />} />
          <Route path="/share-certificates" element={<SCR16_ShareCertificates />} />
          <Route path="/operational-rules" element={<SCR17OperationalRules />} />
          <Route path="/member-governance-rules" element={<SCR18MemberGovernanceRules />} />
          <Route path="/financial-controls" element={<SCR19FinancialControls />} />
          <Route path="/registration-tracker" element={<SCR20RegistrationTracker />} />
          <Route path="/documents/FORM_A_MH" element={<SCR21FormA />} />
          <Route path="/provisional-resolution"element={<SCR22ProvisionalResolution />}/>
          <Route path="/documents/PROMOTER_CONSENT_LETTER_MH" element={<SCR23PromoterConsent />} />
          <Route path="/documents/BUILDER_DOCUMENT_NOTICE_MH" element={<SCR24BuilderNotice />}/>
          <Route path="/documents/BANK_ACCOUNT_LETTER_MH" element={<SCR25BankAccountLetter />}/>
          <Route path="/documents/FIRST_GENERAL_MEETING_MINUTES_MH" element={<SCR26FirstGeneralMeeting />}/> 
          <Route path="/documents/REGISTRAR_SUBMISSION_LETTER_MH" element={<SCR27RegistrarSubmission />}/>
          <Route path="/financial-onboarding" element={<SCR28FinancialOnboarding />}/>
          <Route path="/financial-onboarding/bank-accounts" element={<SCR29BankAccounts />}/>
          <Route path="/financial-onboarding/revenue-receivables" element={<SCR30RevenueReceivablesSetup />}/>
          <Route path="/financial-onboarding/maintenance-governance"element={<SCR31MaintenanceGovernanceSetup />}/>
          <Route path="/financial-onboarding/governance-intelligence"element={<SCR32GovernanceIntelligence />}/>
          <Route path="/financial-onboarding/governance-simulation"element={<SCR33GovernanceSimulation />}/>
          <Route path="/financial-onboarding/scr33"element={<SCR33GovernanceSimulation />}/>
          <Route path="/financial-onboarding/billing-activation"element={<SCR34MaintenanceBillingActivation />}/>
          <Route path="/financial-onboarding/scr34"element={<SCR34MaintenanceBillingActivation />}/>
          <Route path="/knowledge-center"element={<KnowledgeCenter />}/>

         {/* 🔒 PROTECTED ROUTES (GUARD REMOVED TEMPORARILY) */}

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