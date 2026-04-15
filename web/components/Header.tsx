"use client";
import React from 'react';
import { Shield } from 'lucide-react';

export default function Header() {
  return (
    <header className="flex justify-between items-center mb-12 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/40">
          <Shield className="text-white" size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Quantum <span className="gradient-text">Risk Engine</span>
          </h1>
          <p className="text-xs text-slate-500 font-medium">MODULAR QUANTITATIVE RESEARCH PLATFORM</p>
        </div>
      </div>

      <div className="hidden md:flex items-center gap-6">
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-slate-500 uppercase font-bold">Engine Status</span>
          <span className="text-sm text-emerald-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
            Operational
          </span>
        </div>
      </div>
    </header>
  );
}
