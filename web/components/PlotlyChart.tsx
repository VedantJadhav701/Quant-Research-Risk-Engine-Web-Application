"use client";
import dynamic from 'next/dynamic';
import React from 'react';

// Dynamically import Plot with SSR disabled as it requires 'window'
const Plot = dynamic(() => import('react-plotly.js'), { 
  ssr: false,
  loading: () => <div className="animate-pulse bg-slate-800 rounded-lg h-[400px] w-full" />
});

interface PlotlyChartProps {
  data: any[];
  layout: any;
  className?: string;
}

export default function PlotlyChart({ data, layout, className }: PlotlyChartProps) {
  return (
    <div className={className}>
      <Plot
        data={data}
        layout={{
          ...layout,
          autosize: true,
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          font: { color: '#94a3b8', family: 'Inter, sans-serif' },
          margin: { t: 40, b: 40, l: 40, r: 40 },
          scene: {
            ...layout.scene,
            xaxis: { ...layout.scene?.xaxis, gridcolor: '#334155', zerolinecolor: '#334155' },
            yaxis: { ...layout.scene?.yaxis, gridcolor: '#334155', zerolinecolor: '#334155' },
            zaxis: { ...layout.scene?.zaxis, gridcolor: '#334155', zerolinecolor: '#334155' },
          }
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        config={{ responsive: true, displayModeBar: false }}
      />
    </div>
  );
}
