import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import { MainLayout } from "./components/layout/MainLayout";
import { ConfigTokens } from "./pages/ConfigTokens";
import { ConfigPeriodo } from "./pages/ConfigPeriodo";
import { ConfigRateLimit } from "./pages/ConfigRateLimit";
import { ConfigEndpoints } from "./pages/ConfigEndpoints";
import { ConfigSaida } from "./pages/ConfigSaida";
import { ConfigIA } from "./pages/ConfigIA";
import { Execucao } from "./pages/Execucao";
import { MonitorTokens } from "./pages/MonitorTokens";
import { Logs } from "./pages/Logs";
import { Progresso } from "./pages/Progresso";
import { Retomada } from "./pages/Retomada";
import { ChatAuditoria } from "./pages/ChatAuditoria";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Navigate to="/progresso" replace />} />
          <Route path="/config/tokens" element={<ConfigTokens />} />
          <Route path="/config/periodo" element={<ConfigPeriodo />} />
          <Route path="/config/rate-limit" element={<ConfigRateLimit />} />
          <Route path="/config/endpoints" element={<ConfigEndpoints />} />
          <Route path="/config/saida" element={<ConfigSaida />} />
          <Route path="/config/ia" element={<ConfigIA />} />
          <Route path="/execucao" element={<Execucao />} />
          <Route path="/monitor/tokens" element={<MonitorTokens />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/progresso" element={<Progresso />} />
          <Route path="/retomada" element={<Retomada />} />
          <Route path="/chat" element={<ChatAuditoria />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
