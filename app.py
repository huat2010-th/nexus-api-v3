"use client"

import { useState, useMemo } from "react"
import {
  Activity, Database, Droplets, Gauge, Settings2, Users, Waves, Zap,
  TrendingUp, TrendingDown, ChevronDown, Play, Search, Filter, Download,
  Upload, Plus, CircleCheck, CircleAlert, Wifi, Cpu, Info
} from "lucide-react"
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis, Legend
} from "recharts"

type Method = "A" | "B"

// --- RESTORED DEFAULT PLACEHOLDERS ---
const defaultConsumption = [
  { month: "Jan", flow: 0, demand: 0 }, { month: "Feb", flow: 0, demand: 0 },
  { month: "Mar", flow: 0, demand: 0 }, { month: "Apr", flow: 0, demand: 0 },
  { month: "May", flow: 0, demand: 0 }, { month: "Jun", flow: 0, demand: 0 },
  { month: "Jul", flow: 0, demand: 0 }, { month: "Aug", flow: 0, demand: 0 },
  { month: "Sep", flow: 0, demand: 0 }, { month: "Oct", flow: 0, demand: 0 },
  { month: "Nov", flow: 0, demand: 0 }, { month: "Dec", flow: 0, demand: 0 },
]

const defaultBreakdown = [
  { category: "Domestic", value: 0 },
  { category: "F&B / Dining", value: 0 },
  { category: "Staff & Cooling", value: 0 },
  { category: "Pools", value: 0 },
  { category: "Irrigation", value: 0 }
]

const sparklineData = [{ v: 30 }, { v: 45 }, { v: 38 }, { v: 52 }, { v: 48 }, { v: 60 }, { v: 55 }, { v: 70 }, { v: 65 }, { v: 80 }]

/* --- Helpers --- */
function GlassPanel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`relative rounded-xl border border-cyan-400/15 bg-slate-900/40 backdrop-blur-xl shadow-[0_0_0_1px_rgba(0,210,255,0.04),0_8px_40px_-12px_rgba(0,210,255,0.15)] ${className}`}>
      {children}
    </div>
  )
}

function Slider({ label, value, onChange, min = 0, max = 100, step = 1, unit = "" }: any) {
  const pct = ((value - min) / (max - min)) * 100
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <span className="font-mono uppercase tracking-wider text-slate-400">{label}</span>
        <span className="font-mono font-semibold text-cyan-300">{value}{unit}</span>
      </div>
      <div className="relative h-2">
        <div className="absolute inset-0 rounded-full bg-slate-800/80 border border-cyan-400/10" />
        <div className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-cyan-500/60 to-cyan-300 shadow-[0_0_10px_rgba(0,210,255,0.6)]" style={{ width: `${pct}%` }} />
        <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className="absolute inset-0 w-full h-full cursor-pointer opacity-0" />
        <div className="pointer-events-none absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-cyan-300 ring-2 ring-cyan-400/40 shadow-[0_0_12px_rgba(0,210,255,0.9)]" style={{ left: `${pct}%` }} />
      </div>
    </div>
  )
}

function Accordion({ title, icon, children, defaultOpen = false }: any) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="rounded-lg border border-cyan-400/10 bg-slate-950/40 overflow-hidden">
      <button type="button" onClick={() => setOpen(!open)} className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-cyan-400/5 transition-colors">
        <div className="flex items-center gap-3">
          <span className="text-cyan-400">{icon}</span>
          <span className="font-mono text-xs uppercase tracking-wider text-slate-200">{title}</span>
        </div>
        <ChevronDown className={`h-4 w-4 text-cyan-400 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      {open && <div className="px-4 pb-4 pt-2 space-y-4 border-t border-cyan-400/10">{children}</div>}
    </div>
  )
}

function KpiCard({ label, value, unit, icon }: any) {
  return (
    <GlassPanel className="p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="rounded-md border border-cyan-400/20 bg-cyan-400/5 p-1.5 text-cyan-300">{icon}</div>
          <span className="font-mono text-[10px] uppercase tracking-widest text-slate-400">{label}</span>
        </div>
      </div>
      <div className="flex items-baseline gap-1 mb-2">
        <span className="font-mono text-3xl font-bold text-slate-50 tracking-tight">{value}</span>
        <span className="font-mono text-xs text-slate-400">{unit}</span>
      </div>
      <div className="h-10 -mx-2">
        <ResponsiveContainer width="100%" height={40}>
          <LineChart data={sparklineData}><Line type="monotone" dataKey="v" stroke="#00d2ff" strokeWidth={2} dot={false} /></LineChart>
        </ResponsiveContainer>
      </div>
    </GlassPanel>
  )
}

/* --- Main Dashboard --- */
export default function NexusDashboard() {
  const [method, setMethod] = useState<Method>("A")
  const [tab, setTab] = useState<"dashboard" | "matrix">("dashboard")
  const [subTabA, setSubTabA] = useState("hotel") 
  const [isLoading, setIsLoading] = useState(false)

  // KPI States
  const [kpiPeakDemand, setKpiPeakDemand] = useState("---")
  const [kpiAvgDemand, setKpiAvgDemand] = useState("---")
  const [kpiAnnualDemand, setKpiAnnualDemand] = useState("---")
  const [statusText, setStatusText] = useState("Awaiting Input")

  // CHART States
  const [chartCons_A, setChartCons_A] = useState<any[]>([])
  const [chartBreak_A, setChartBreak_A] = useState<any[]>([])
  const [chartCum_B, setChartCum_B] = useState<any[]>([])
  const [chartType_B, setChartType_B] = useState<any[]>([])

  // --- METHOD A SLIDERS ---
  const [h_shower, setH_shower] = useState(120); const [h_toilet, setH_toilet] = useState(45); const [h_misc, setH_misc] = useState(40); const [h_laundry, setH_laundry] = useState(60); const [h_meals, setH_meals] = useState(2.5); const [h_water_meal, setH_water_meal] = useState(25); const [h_pool_evap, setH_pool_evap] = useState(10); const [h_pool_bw, setH_pool_bw] = useState(5);
  const [n_shower, setN_shower] = useState(90); const [n_toilet, setN_toilet] = useState(40); const [n_misc, setN_misc] = useState(30); const [n_laundry, setN_laundry] = useState(25); const [n_meals, setN_meals] = useState(0.2); const [n_water_meal, setN_water_meal] = useState(20); const [n_pool_evap, setN_pool_evap] = useState(10); const [n_pool_bw, setN_pool_bw] = useState(5);
  const [b_cooling, setB_cooling] = useState(2.0); const [b_irrigation, setB_irrigation] = useState(5.0); const [b_staff, setB_staff] = useState(100.0); const [ratio_hotel, setRatio_hotel] = useState(1.2); const [ratio_non, setRatio_non] = useState(0.2); const [inf_pool, setInf_pool] = useState(3.0); const [inf_land, setInf_land] = useState(20.0); const [inf_gfa, setInf_gfa] = useState(120.0);
  const [peak_occ, setPeak_occ] = useState(90); const [avg_occ, setAvg_occ] = useState(65); const [irr_peak_mult, setIrr_peak_mult] = useState(1.5); const [growth_rate, setGrowth_rate] = useState(3.5); const [nrw_loss, setNrw_loss] = useState(10.0);

  // --- METHOD B WEIGHTS ---
  const [w_1bed, setW_1bed] = useState(1.0)
  const [w_2bed, setW_2bed] = useState(1.5)
  const [w_3bed, setW_3bed] = useState(2.0)
  const [w_4bed, setW_4bed] = useState(2.5)
  const [w_unspec, setW_unspec] = useState(1.5)
  const [w_sh_pool, setW_sh_pool] = useState(20.0)
  const [w_pr_pool, setW_pr_pool] = useState(3.0)

  // Matrix State
  const [matrixA, setMatrixA] = useState<any[]>([])
  const [matrixB, setMatrixB] = useState<any[]>([])

  const handleEngage = async () => {
    setIsLoading(true);
    setStatusText("Calculating...");
    
    try {
      const payload = method === "A" 
        ? { method: "A", h_shower, h_toilet, h_misc, h_laundry, h_meals, h_water_meal, h_pool_evap, h_pool_bw, n_shower, n_toilet, n_misc, n_laundry, n_meals, n_water_meal, n_pool_evap, n_pool_bw, b_cooling, b_irrigation, b_staff, ratio_hotel, ratio_non, inf_pool, inf_land, inf_gfa, peak_occ, avg_occ, irr_peak_mult, growth_rate, nrw_loss }
        : { method: "B", w_1bed, w_2bed, w_3bed, w_4bed, w_unspec, w_sh_pool, w_pr_pool };

      const response = await fetch("https://nexus-api-v3-njc2.onrender.com/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      setKpiPeakDemand(data.peak_demand.toLocaleString());
      setKpiAvgDemand(data.avg_daily.toLocaleString());
      setKpiAnnualDemand((data.annual_demand / 1000000).toFixed(2)); 
      
      if (method === "A") {
        setChartCons_A(data.chart_consumption);
        setChartBreak_A(data.breakdown); 
        setMatrixA(data.matrix_data);
      } else {
        setChartCum_B(data.cum_chart);
        setChartType_B(data.type_chart);
        setMatrixB(data.matrix_data);
      }
      
      setStatusText(`Synced (Method ${data.method_used})`);
      
    } catch (error) {
      alert("Connection failed.");
      setStatusText("Error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#04101f] text-slate-200 font-sans relative overflow-x-hidden">
      {/* Background */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute -top-40 -left-40 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute top-1/3 -right-40 h-[600px] w-[600px] rounded-full bg-blue-600/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-[400px] w-[400px] rounded-full bg-cyan-400/5 blur-3xl" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "linear-gradient(rgba(0,210,255,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(0,210,255,0.6) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
      </div>

      <div className="relative z-10 flex flex-col lg:flex-row gap-6 p-6 max-w-[1600px] mx-auto">
        
        {/* --- SIDEBAR --- */}
        <aside className="lg:w-80 lg:sticky lg:top-6 lg:self-start space-y-4 shrink-0">
          <GlassPanel className="p-5">
            <div className="flex items-center gap-3 mb-1">
              <div className="relative"><div className="absolute inset-0 rounded-md bg-cyan-400/30 blur-md" /><div className="relative rounded-md bg-gradient-to-br from-cyan-300 to-cyan-500 p-1.5"><Waves className="h-5 w-5 text-slate-950" /></div></div>
              <div><h1 className="font-mono text-lg font-bold tracking-tight text-slate-50">NEXUS</h1><p className="font-mono text-[10px] uppercase tracking-[0.2em] text-cyan-300/80">Water Engine v3.4</p></div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-[10px] font-mono text-slate-400"><span className="relative flex h-2 w-2"><span className="absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75 animate-ping" /><span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-300" /></span><span className="uppercase tracking-widest">System Online</span></div>
          </GlassPanel>

          <GlassPanel className="p-4">
            <p className="font-mono text-[10px] uppercase tracking-widest text-slate-400 mb-3">Calculation Method</p>
            <div className="relative grid grid-cols-2 rounded-lg border border-cyan-400/15 bg-slate-950/60 p-1">
              <div className="absolute inset-y-1 w-[calc(50%-4px)] rounded-md bg-gradient-to-r from-cyan-500/30 to-cyan-400/20 border border-cyan-400/40 shadow-[0_0_20px_rgba(0,210,255,0.3)] transition-transform duration-300" style={{ transform: method === "A" ? "translateX(4px)" : "translateX(calc(100% + 4px))" }} />
              <button onClick={() => {setMethod("A"); setStatusText("Awaiting Input")}} className={`relative z-10 py-2 font-mono text-xs uppercase tracking-wider transition-colors ${method === "A" ? "text-cyan-200" : "text-slate-500"}`}>Method A</button>
              <button onClick={() => {setMethod("B"); setStatusText("Awaiting Input")}} className={`relative z-10 py-2 font-mono text-xs uppercase tracking-wider transition-colors ${method === "B" ? "text-cyan-200" : "text-slate-500"}`}>Method B</button>
            </div>
          </GlassPanel>

          {method === "A" && (
            <div className="space-y-3">
              <div className="flex rounded-md border border-cyan-400/20 bg-slate-900/50 p-1 mb-4">
                <button onClick={() => setSubTabA("hotel")} className={`flex-1 py-1.5 text-[10px] font-mono uppercase tracking-wider rounded transition-colors ${subTabA === "hotel" ? "bg-cyan-500/20 text-cyan-200" : "text-slate-500"}`}>Hotel</button>
                <button onClick={() => setSubTabA("nonHotel")} className={`flex-1 py-1.5 text-[10px] font-mono uppercase tracking-wider rounded transition-colors ${subTabA === "nonHotel" ? "bg-cyan-500/20 text-cyan-200" : "text-slate-500"}`}>Non-Hotel</button>
                <button onClick={() => setSubTabA("eng")} className={`flex-1 py-1.5 text-[10px] font-mono uppercase tracking-wider rounded transition-colors ${subTabA === "eng" ? "bg-cyan-500/20 text-cyan-200" : "text-slate-500"}`}>Global</button>
              </div>

              {subTabA === "hotel" && (
                <>
                  <Accordion title="Guest Behavior (Hotel)" icon={<Users className="h-4 w-4" />} defaultOpen>
                    <Slider label="Shower" value={h_shower} onChange={setH_shower} min={50} max={250} unit=" L" />
                    <Slider label="Toilet" value={h_toilet} onChange={setH_toilet} min={10} max={100} unit=" L" />
                    <Slider label="Faucet/Misc" value={h_misc} onChange={setH_misc} min={10} max={100} unit=" L" />
                    <Slider label="Laundry" value={h_laundry} onChange={setH_laundry} min={10} max={100} unit=" L" />
                  </Accordion>
                  <Accordion title="F&B and Pools (Hotel)" icon={<Droplets className="h-4 w-4" />}>
                    <Slider label="Meals/Guest" value={h_meals} onChange={setH_meals} min={0} max={5} step={0.1} />
                    <Slider label="Water/Meal" value={h_water_meal} onChange={setH_water_meal} min={10} max={50} unit=" L" />
                    <Slider label="Pool Evap" value={h_pool_evap} onChange={setH_pool_evap} min={0} max={30} unit=" L/m²" />
                    <Slider label="Pool Backwash" value={h_pool_bw} onChange={setH_pool_bw} min={0} max={20} unit=" L/m²" />
                  </Accordion>
                </>
              )}

              {subTabA === "nonHotel" && (
                <>
                  <Accordion title="Resident Behavior (Condo)" icon={<Users className="h-4 w-4" />} defaultOpen>
                    <Slider label="Shower" value={n_shower} onChange={setN_shower} min={50} max={250} unit=" L" />
                    <Slider label="Toilet" value={n_toilet} onChange={setN_toilet} min={10} max={100} unit=" L" />
                    <Slider label="Faucet/Misc" value={n_misc} onChange={setN_misc} min={10} max={100} unit=" L" />
                    <Slider label="Laundry" value={n_laundry} onChange={setN_laundry} min={10} max={100} unit=" L" />
                  </Accordion>
                  <Accordion title="F&B and Pools (Condo)" icon={<Droplets className="h-4 w-4" />}>
                    <Slider label="Dining Out/Cafe" value={n_meals} onChange={setN_meals} min={0} max={3} step={0.1} />
                    <Slider label="Water/Meal" value={n_water_meal} onChange={setN_water_meal} min={10} max={50} unit=" L" />
                    <Slider label="Pool Evap" value={n_pool_evap} onChange={setN_pool_evap} min={0} max={30} unit=" L/m²" />
                    <Slider label="Pool Backwash" value={n_pool_bw} onChange={setN_pool_bw} min={0} max={20} unit=" L/m²" />
                  </Accordion>
                </>
              )}

              {subTabA === "eng" && (
                <>
                  <Accordion title="Seasonality & Scenarios" icon={<Settings2 className="h-4 w-4" />} defaultOpen>
                    <Slider label="Peak Occ." value={peak_occ} onChange={setPeak_occ} min={50} max={100} unit="%" />
                    <Slider label="Avg Occ." value={avg_occ} onChange={setAvg_occ} min={30} max={100} unit="%" />
                    <Slider label="NRW Leakage" value={nrw_loss} onChange={setNrw_loss} min={0} max={30} unit="%" />
                    <Slider label="Growth Factor" value={growth_rate} onChange={setGrowth_rate} min={0} max={10} step={0.1} unit="%" />
                  </Accordion>
                  <Accordion title="Infrastructure Constants" icon={<Activity className="h-4 w-4" />}>
                    <Slider label="Irrigation" value={b_irrigation} onChange={setB_irrigation} min={1} max={15} step={0.5} unit=" L/m²" />
                    <Slider label="Cooling" value={b_cooling} onChange={setB_cooling} min={0} max={10} step={0.5} unit=" L/m²" />
                    <Slider label="Staff Usage" value={b_staff} onChange={setB_staff} min={50} max={200} unit=" L" />
                    <Slider label="Staff Ratio(H)" value={ratio_hotel} onChange={setRatio_hotel} min={0.1} max={3} step={0.1} />
                    <Slider label="Staff Ratio(NH)" value={ratio_non} onChange={setRatio_non} min={0} max={1} step={0.1} />
                  </Accordion>
                </>
              )}
            </div>
          )}

          {/* --- METHOD B SIDEBAR --- */}
          {method === "B" && (
            <div className="space-y-3">
              <Accordion title="Unit Multipliers (Inference)" icon={<Settings2 className="h-4 w-4" />} defaultOpen>
                <Slider label="1-Bed Weight" value={w_1bed} onChange={setW_1bed} max={5} step={0.1} />
                <Slider label="2-Bed Weight" value={w_2bed} onChange={setW_2bed} max={5} step={0.1} />
                <Slider label="3-Bed Weight" value={w_3bed} onChange={setW_3bed} max={5} step={0.1} />
                <Slider label="4-Bed Weight" value={w_4bed} onChange={setW_4bed} max={5} step={0.1} />
                <Slider label="Unspec. Weight" value={w_unspec} onChange={setW_unspec} max={5} step={0.1} />
              </Accordion>
              <Accordion title="Pool Multipliers (Inference)" icon={<Activity className="h-4 w-4" />}>
                <Slider label="Shared Pool" value={w_sh_pool} onChange={setW_sh_pool} max={50} step={1} />
                <Slider label="Private Pool" value={w_pr_pool} onChange={setW_pr_pool} max={10} step={0.5} />
              </Accordion>
              <div className="p-3 mt-4 rounded-md bg-cyan-500/10 border border-cyan-400/20 text-xs text-cyan-100 font-mono flex items-start gap-2">
                <Info className="h-4 w-4 shrink-0 text-cyan-400" />
                <p>Counts for 1-Bed, 2-Bed, etc., are drawn automatically from the Future Project Matrix.</p>
              </div>
            </div>
          )}

          <button onClick={handleEngage} disabled={isLoading} className={`group relative w-full overflow-hidden rounded-lg border border-cyan-400/40 py-3.5 font-mono text-sm uppercase tracking-widest transition-all ${isLoading ? "bg-cyan-500/10 text-cyan-300/50" : "bg-gradient-to-br from-cyan-500/20 via-cyan-400/10 to-transparent text-cyan-100 hover:border-cyan-300/70 hover:shadow-[0_0_30px_rgba(0,210,255,0.4)]"}`}>
            <span className="relative flex items-center justify-center gap-2"><Play className="h-4 w-4" />{isLoading ? "CALCULATING..." : "ENGAGE SIMULATION"}</span>
          </button>

          <div className="flex items-center justify-between px-2 font-mono text-[10px] text-slate-500">
            <div className="flex items-center gap-1.5"><Wifi className="h-3 w-3 text-cyan-400" /><span>Linked</span></div>
            <div className="flex items-center gap-1.5"><CircleCheck className="h-3 w-3 text-cyan-400" /><span>{statusText}</span></div>
          </div>
        </aside>

        {/* --- MAIN CONTENT --- */}
        <main className="flex-1 min-w-0 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1"><span className="rounded-full border border-cyan-400/30 bg-cyan-400/5 px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-widest text-cyan-300">Live Telemetry</span></div>
              <h2 className="font-mono text-2xl font-bold tracking-tight text-slate-50">Operations Command Center</h2>
            </div>
          </div>

          <div className="inline-flex rounded-lg border border-cyan-400/15 bg-slate-900/40 p-1">
            <button onClick={() => setTab("dashboard")} className={`px-4 py-2 rounded-md font-mono text-xs uppercase tracking-wider ${tab === "dashboard" ? "bg-cyan-400/15 text-cyan-200 border border-cyan-400/30" : "text-slate-400"}`}>Dashboard Insights</button>
            <button onClick={() => setTab("matrix")} className={`px-4 py-2 rounded-md font-mono text-xs uppercase tracking-wider ${tab === "matrix" ? "bg-cyan-400/15 text-cyan-200 border border-cyan-400/30" : "text-slate-400"}`}>Data Input Matrix</button>
          </div>

          {tab === "dashboard" ? (
            <>
              {/* KPIs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                <KpiCard label="Peak Day Demand" value={kpiPeakDemand} unit="m³/d" icon={<Gauge className="h-4 w-4" />} />
                <KpiCard label="Average Day Demand" value={kpiAvgDemand} unit="m³/d" icon={<Activity className="h-4 w-4" />} />
                <KpiCard label="Annual Projection" value={kpiAnnualDemand} unit="M m³/y" icon={<Droplets className="h-4 w-4" />} />
                <KpiCard label="NRW Leakage Ratio" value={method === "A" ? nrw_loss.toFixed(1) : "10.0"} unit="%" icon={<Settings2 className="h-4 w-4" />} />
              </div>

              {/* METHOD A CHARTS */}
              {method === "A" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <GlassPanel className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div><h3 className="font-mono text-sm font-semibold text-slate-100 uppercase tracking-wider">Flow vs Demand</h3><p className="text-xs text-slate-400 mt-0.5">12-month seasonal projection</p></div>
                    </div>
                    <div className="h-[280px] -ml-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartCons_A.length > 0 ? chartCons_A : defaultConsumption}>
                          <defs>
                            <linearGradient id="flowGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#00d2ff" stopOpacity={0.5} /><stop offset="100%" stopColor="#00d2ff" stopOpacity={0} /></linearGradient>
                            <linearGradient id="demandGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#3b82f6" stopOpacity={0.4} /><stop offset="100%" stopColor="#3b82f6" stopOpacity={0} /></linearGradient>
                          </defs>
                          <CartesianGrid stroke="rgba(0,210,255,0.08)" strokeDasharray="3 3" />
                          <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <Tooltip contentStyle={{ background: "rgba(4,16,31,0.95)", border: "1px solid rgba(0,210,255,0.3)", borderRadius: 8, fontFamily: "monospace", fontSize: 12 }} />
                          <Area type="monotone" dataKey="flow" stroke="#00d2ff" strokeWidth={2} fill="url(#flowGrad)" />
                          <Area type="monotone" dataKey="demand" stroke="#3b82f6" strokeWidth={2} fill="url(#demandGrad)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </GlassPanel>

                  <GlassPanel className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div><h3 className="font-mono text-sm font-semibold text-slate-100 uppercase tracking-wider">Demand Breakdown</h3><p className="text-xs text-slate-400 mt-0.5">Component-level volume analysis</p></div>
                    </div>
                    <div className="h-[280px] -ml-4">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartBreak_A.length > 0 ? chartBreak_A : defaultBreakdown} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                          <CartesianGrid stroke="rgba(0,210,255,0.08)" strokeDasharray="3 3" horizontal={false} />
                          <XAxis type="number" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} unit="%" />
                          <YAxis dataKey="category" type="category" stroke="#cbd5e1" fontSize={11} tickLine={false} axisLine={false} width={120} />
                          <Tooltip cursor={{ fill: "rgba(0,210,255,0.05)" }} contentStyle={{ background: "rgba(4,16,31,0.95)", border: "1px solid rgba(0,210,255,0.3)", borderRadius: 8, fontFamily: "monospace", fontSize: 12 }} formatter={(value: any) => [`${value}%`, "Volume"]} />
                          <Bar dataKey="value" fill="#00d2ff" radius={[0, 4, 4, 0]} barSize={24} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </GlassPanel>
                </div>
              )}

              {/* METHOD B CHARTS */}
              {method === "B" && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <GlassPanel className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div><h3 className="font-mono text-sm font-semibold text-slate-100 uppercase tracking-wider">Cumulative Future Demand</h3><p className="text-xs text-slate-400 mt-0.5">2026 - 2050 Master Plan Growth</p></div>
                    </div>
                    <div className="h-[280px] -ml-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartCum_B.length > 0 ? chartCum_B : defaultLine}>
                          <CartesianGrid stroke="rgba(0,210,255,0.08)" strokeDasharray="3 3" />
                          <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <Tooltip contentStyle={{ background: "rgba(4,16,31,0.95)", border: "1px solid rgba(0,210,255,0.3)", borderRadius: 8, fontFamily: "monospace", fontSize: 12 }} />
                          <Legend wrapperStyle={{ fontSize: '12px', fontFamily: 'monospace' }} />
                          <Line type="monotone" dataKey="New Peak" stroke="#e74c3c" strokeWidth={3} dot={false} />
                          <Line type="monotone" dataKey="New Avg" stroke="#3498db" strokeWidth={3} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </GlassPanel>

                  <GlassPanel className="p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div><h3 className="font-mono text-sm font-semibold text-slate-100 uppercase tracking-wider">Demand By Asset Type</h3><p className="text-xs text-slate-400 mt-0.5">Condo vs Villa accumulation</p></div>
                    </div>
                    <div className="h-[280px] -ml-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartType_B.length > 0 ? chartType_B : defaultLine}>
                          <CartesianGrid stroke="rgba(0,210,255,0.08)" strokeDasharray="3 3" />
                          <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                          <Tooltip cursor={{ fill: "rgba(0,210,255,0.05)" }} contentStyle={{ background: "rgba(4,16,31,0.95)", border: "1px solid rgba(0,210,255,0.3)", borderRadius: 8, fontFamily: "monospace", fontSize: 12 }} />
                          <Legend wrapperStyle={{ fontSize: '12px', fontFamily: 'monospace' }} />
                          <Bar dataKey="Condo" stackId="a" fill="#0891b2" />
                          <Bar dataKey="Villa" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </GlassPanel>
                </div>
              )}
            </>
          ) : (
            /* ============================== MATRIX ============================== */
            <GlassPanel className="p-5">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4">
                <div><h3 className="font-mono text-sm font-semibold text-slate-100 uppercase tracking-wider">Data Input Matrix</h3><p className="text-xs text-slate-400 mt-0.5">Live Database Grid from Python Engine</p></div>
                <div className="flex flex-wrap items-center gap-2">
                  <button type="button" className="flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-cyan-400/15 bg-slate-950/60 font-mono text-[10px] uppercase tracking-wider text-slate-300 hover:border-cyan-400/40 hover:text-cyan-200"><Download className="h-3 w-3" />Export</button>
                </div>
              </div>
              <div className="overflow-x-auto rounded-lg border border-cyan-400/10">
                {method === "A" ? (
                  <table className="w-full text-sm">
                    <thead><tr className="bg-slate-950/60 border-b border-cyan-400/15 text-left font-mono text-[10px] uppercase tracking-widest text-slate-400"><th className="px-4 py-3">ID</th><th className="px-4 py-3">Project Zone</th><th className="px-4 py-3">Category</th><th className="px-4 py-3">Units</th><th className="px-4 py-3">Status</th></tr></thead>
                    <tbody className="font-mono text-xs">
                      {matrixA.map((row, i) => (
                        <tr key={i} className="border-b border-cyan-400/5 hover:bg-cyan-400/5 transition-colors">
                          <td className="px-4 py-2.5 text-slate-500">#{String(i+1).padStart(3, "0")}</td>
                          <td className="px-4 py-2.5 text-cyan-300 font-semibold">{row.zone}</td>
                          <td className="px-4 py-2.5"><span className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-2 py-0.5 text-[10px] text-slate-300">{row.category}</span></td>
                          <td className="px-4 py-2.5 text-slate-200">{row.actual}</td>
                          <td className="px-4 py-2.5"><span className="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] uppercase tracking-wider border border-cyan-400/30 bg-cyan-400/10 text-cyan-300"><span className="h-1 w-1 rounded-full bg-cyan-400"/>Optimal</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <table className="w-full text-sm whitespace-nowrap">
                    <thead><tr className="bg-slate-950/60 border-b border-cyan-400/15 text-left font-mono text-[10px] uppercase tracking-widest text-slate-400">
                      <th className="px-4 py-3">Year</th><th className="px-4 py-3">Project Zone</th><th className="px-4 py-3">Type</th>
                      <th className="px-4 py-3">1-Bed</th><th className="px-4 py-3">2-Bed</th><th className="px-4 py-3">3-Bed</th><th className="px-4 py-3">4+ Bed</th>
                      <th className="px-4 py-3">Unspec.</th><th className="px-4 py-3">Sh. Pool</th><th className="px-4 py-3">Pr. Pool</th>
                    </tr></thead>
                    <tbody className="font-mono text-xs">
                      {matrixB.map((row, i) => (
                        <tr key={i} className="border-b border-cyan-400/5 hover:bg-cyan-400/5 transition-colors">
                          <td className="px-4 py-2.5 text-cyan-300 font-semibold">{row.Year}</td>
                          <td className="px-4 py-2.5 text-slate-200">{row["Project Name"]}</td>
                          <td className="px-4 py-2.5"><span className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-2 py-0.5 text-[10px] text-slate-300">{row.Type}</span></td>
                          <td className="px-4 py-2.5 text-slate-400">{row["1-Bed"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["2-Bed"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["3-Bed"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["4+ Bed"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["Unspec"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["Shared Pools"]}</td>
                          <td className="px-4 py-2.5 text-slate-400">{row["Private Pools"]}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </GlassPanel>
          )}
        </main>
      </div>
    </div>
  )
}
