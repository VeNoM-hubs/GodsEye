import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import DevicesPage from "./pages/DevicesPage";
import HoneypotPage from "./pages/HoneypotPage";
import NotFound from "./pages/NotFound";
import { PlaceholderPage } from "./components/cyber/PlaceholderPage";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/threats" element={<HoneypotPage />} />
          <Route path="/logs" element={<PlaceholderPage title="System Log Stream" />} />
          <Route path="/access" element={<PlaceholderPage title="Access Permissions" />} />
          <Route path="/settings" element={<PlaceholderPage title="Core Configuration" />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")!).render(<App />);
