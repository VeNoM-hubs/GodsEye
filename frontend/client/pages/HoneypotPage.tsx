import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { HoneypotFeed } from "@/components/cyber/HoneypotFeed";
import { useHoneypotFeed } from "@/hooks/useHoneypotFeed";
import { motion } from "framer-motion";

export default function HoneypotPage() {
  const events = useHoneypotFeed();

  return (
    <div className="flex min-h-screen bg-background text-foreground subtle-grid overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto p-10 space-y-8 scrollbar-hide">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              <span className="w-1 h-8 bg-primary rounded-full" />
              Threat Intelligence
            </h1>
            <p className="text-muted-foreground text-[11px] font-medium mt-1 uppercase tracking-widest opacity-80">
              Live Honeypot Ingestion — {events.length} Events Captured
            </p>
          </motion.div>
          <HoneypotFeed events={events} />
        </div>
      </main>
    </div>
  );
}
