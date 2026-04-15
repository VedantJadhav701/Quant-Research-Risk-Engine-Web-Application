"use client";
import React, { useState } from 'react';
import { Search, Play, Calendar } from 'lucide-react';
import GlassCard from './GlassCard';

interface ControlPanelProps {
  onRun: (ticker: string, start: string, end: string) => void;
  isLoading: boolean;
}

export default function ControlPanel({ onRun, isLoading }: ControlPanelProps) {
  const [ticker, setTicker] = useState('SPY');
  const [start, setStart] = useState('2023-01-01');
  const [end, setEnd] = useState(new Date().toISOString().split('T')[0]);

  return (
    <GlassCard className="flex flex-wrap items-end gap-6 mb-8">
      <div className="flex-1 min-w-[200px]">
        <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
          <Search size={14} /> Asset Ticker
        </label>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors"
          placeholder="e.g. BTC-USD"
        />
      </div>

      <div className="flex-1 min-w-[180px]">
        <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
          <Calendar size={14} /> Start Date
        </label>
        <input
          type="date"
          value={start}
          onChange={(e) => setStart(e.target.value)}
          className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors text-slate-200"
        />
      </div>

      <div className="flex-1 min-w-[180px]">
        <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
          <Calendar size={14} /> End Date
        </label>
        <input
          type="date"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          className="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors text-slate-200"
        />
      </div>

      <button
        onClick={() => onRun(ticker, start, end)}
        disabled={isLoading}
        className="h-[46px] px-8 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded-lg font-semibold flex items-center gap-2 transition-all active:scale-95 text-white"
      >
        <Play size={18} fill="white" />
        {isLoading ? 'Analyzing...' : 'Run Pipeline'}
      </button>
    </GlassCard>
  );
}
