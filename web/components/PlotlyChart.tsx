"use client";
import React, { useEffect, useRef } from 'react';

interface PlotlyChartProps {
  data: any[];
  layout: any;
  className?: string;
}

declare global {
  interface Window {
    Plotly: any;
  }
}

export default function PlotlyChart({ data, layout, className }: PlotlyChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chartRef.current && window.Plotly) {
      window.Plotly.newPlot(chartRef.current, data, {
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
      }, { responsive: true, displayModeBar: false });
    }

    return () => {
      if (chartRef.current && window.Plotly) {
        window.Plotly.purge(chartRef.current);
      }
    };
  }, [data, layout]);

  return (
    <div ref={chartRef} className={className} style={{ width: '100%', height: '100%' }} />
  );
}
