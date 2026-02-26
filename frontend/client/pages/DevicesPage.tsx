import { Sidebar } from "@/components/cyber/Sidebar";
import { Header } from "@/components/cyber/Header";
import { DeviceGrid } from "@/components/cyber/DeviceGrid";
import { MOCK_DEVICES } from "@/lib/mock-data";
import { motion } from "framer-motion";
import { Search, Filter, Monitor, Plus } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function DevicesPage() {
  return (
    <div className="flex min-h-screen bg-background text-foreground subtle-grid overflow-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header />
        
        <div className="flex-1 overflow-y-auto p-10 space-y-10 scrollbar-hide">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row md:items-center justify-between gap-6"
          >
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                <span className="w-1 h-8 bg-primary rounded-full" />
                Infrastructure Asset Management
              </h1>
              <p className="text-muted-foreground text-[11px] font-medium mt-1 uppercase tracking-widest opacity-80">
                Centralized Node Inventory & Health Telemetry — {MOCK_DEVICES.length} Registered Assets
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button className="h-10 px-6 rounded-md bg-primary text-primary-foreground text-[11px] font-bold uppercase tracking-widest transition-all hover:bg-primary/90 shadow-sm active:scale-[0.98]">
                <Plus className="w-4 h-4 mr-2" />
                Add New Asset
              </Button>
            </div>
          </motion.div>

          <div className="flex flex-col md:flex-row md:items-center gap-4 py-4 border-y border-border/40 bg-muted/5 px-6 rounded-lg">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search by ID, Hostname, or Location..."
                className="pl-10 h-9 bg-background/50 border-border/40 rounded-md focus:border-primary/40 transition-all text-sm"
              />
            </div>
            
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide">
              {["All Assets", "Production", "Staging", "Edge Nodes", "End-points"].map((label, i) => (
                <button
                  key={label}
                  className={cn(
                    "px-4 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-widest transition-all",
                    i === 0 ? "bg-primary text-primary-foreground shadow-sm" : "bg-muted/30 text-muted-foreground hover:bg-muted/50 border border-border/40"
                  )}
                >
                  {label}
                </button>
              ))}
            </div>
            
            <button className="p-2 h-9 rounded-md bg-muted/30 border border-border/40 text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-all flex items-center gap-2 text-[10px] font-bold uppercase ml-auto">
              <Filter className="w-3.5 h-3.5" />
              Filter Matrix
            </button>
          </div>

          <div className="pb-12">
            <DeviceGrid devices={MOCK_DEVICES} />
          </div>
        </div>
      </main>
    </div>
  );
}
