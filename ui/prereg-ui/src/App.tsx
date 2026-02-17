import { BrowserRouter, Routes, Route } from "react-router-dom";

import { PreRegistrationReadinessPage } from "./pages/PreRegistrationReadinessPage";
import { BylawDecisionWorkspace } from "./pages/BylawDecisionWorkspace";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PreRegistrationReadinessPage />} />
        <Route path="/bylaws" element={<BylawDecisionWorkspace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
