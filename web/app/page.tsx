"use client";
import React, { useState } from 'react';
import Header from '@/components/Header';
import ControlPanel from '@/components/ControlPanel';
import GlassCard from '@/components/GlassCard';
import PlotlyChart from '@/components/PlotlyChart';
import { TrendingUp, AlertTriangle, Activity, BarChart3, Info } from 'lucide-react';
import { runAnalysis } from '@/lib/api';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async (ticker: string, start: string, end: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runAnalysis({ ticker, start_date: start, end_date: end });
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-[1400px] mx-auto px-6 py-8">
      <Header />
      
      <ControlPanel onRun={handleRun} isLoading={loading} />

      {error && (
        <GlassCard className="border-red-500/30 bg-red-500/5 mb-8 text-red-400 flex items-center gap-3">
          <AlertTriangle size={20} /> {error}
        </GlassCard>
      )}

      {data ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Market Overview */}
          <div className="lg:col-span-2 space-y-8">
            <GlassCard>
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Activity className="text-blue-400" /> Volatility Surface (Term Structure & Skew)
                </h2>
                <span className="text-xs text-slate-500 flex items-center gap-1">
                  <Info size={12} /> Interactive 3D Mesh
                </span>
              </div>
              <PlotlyChart 
                className="h-[500px]"
                data={[{
                  x: data.volatility.surface.x,
                  y: data.volatility.surface.y,
                  z: data.volatility.surface.z,
                  type: 'mesh3d',
                  colorscale: 'Viridis',
                  opacity: 0.8,
                }]}
                layout={{
                  scene: {
                    xaxis: { title: 'Strike' },
                    yaxis: { title: 'Days to Expiry' },
                    zaxis: { title: 'Implied Vol' },
                  }
                }}
              />
            </GlassCard>

            <GlassCard>
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <BarChart3 className="text-blue-400" /> Monte Carlo Simulation (10,000 Paths)
              </h2>
              <PlotlyChart 
                className="h-[400px]"
                data={data.risk.simulation.paths.map((path: any, i: number) => ({
                  y: path,
                  type: 'scatter',
                  mode: 'lines',
                  line: { width: 1, color: `rgba(59, 130, 246, ${i === 0 ? 0.8 : 0.1})` },
                  showlegend: false,
                }))}
                layout={{
                  xaxis: { title: 'Horizon (Days)' },
                  yaxis: { title: 'Price' },
                }}
              />
            </GlassCard>
          </div>

          {/* Risk Metrics Sidebar */}
          <div className="space-y-8">
            <GlassCard className="bg-blue-600/10 border-blue-500/20">
              <h3 className="text-sm font-semibold text-blue-300 uppercase tracking-wider mb-4">Detected Regime</h3>
              <div className="text-3xl font-bold text-white mb-2">{data.metadata.regime}</div>
              <div className="text-sm text-slate-400">
                System adjusted degrees of freedom (ν = {data.risk.metrics.Estimated_Nu?.toFixed(2) || 'N/A'}) for fat-tail handling.
              </div>
            </GlassCard>

            <div className="grid grid-cols-1 gap-4">
              <MetricCard 
                label="Value at Risk (95%)" 
                value={`${(data.risk.metrics.VaR_95 * 100).toFixed(2)}%`}
                icon={<AlertTriangle className="text-rose-400" />}
                sub="Max expected loss over 1 day"
              />
              <MetricCard 
                label="Conditional VaR (CVaR)" 
                value={`${(data.risk.metrics.CVaR_95 * 100).toFixed(2)}%`}
                icon={<AlertTriangle className="text-red-500" />}
                sub="Average loss in tail scenarios"
              />
              <MetricCard 
                label="Expected Return" 
                value={`${(data.risk.metrics.Expected_Return * 100).toFixed(2)}%`}
                icon={<TrendingUp className="text-emerald-400" />}
                sub="Drift parameter (μ)"
              />
            </div>
            
            <GlassCard>
              <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Market Stats</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-slate-500">Sharpe Ratio</span>
                  <span className="font-mono">{data.risk.metrics.Sharpe_Ratio?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Max Drawdown</span>
                  <span className="font-mono text-rose-400">{(data.risk.metrics.Max_Drawdown * 100).toFixed(2)}%</span>
                </div>
              </div>
            </GlassCard>
          </div>

        </div>
      ) : (
        <div className="h-[60vh] flex flex-col items-center justify-center opacity-40">
          <Activity size={64} className="animate-pulse mb-4 text-blue-500" />
          <p className="text-xl">Enter a ticker to start the Quantum Analysis</p>
        </div>
      )}
    </main>
  );
}

function MetricCard({ label, value, icon, sub }: any) {
  return (
    <GlassCard className="!p-5">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-2xl font-bold mb-1">{value}</div>
      <div className="text-[10px] text-slate-500">{sub}</div>
    </GlassCard>
  );
}
