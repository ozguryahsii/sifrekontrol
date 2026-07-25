"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RegulationResult } from "@/lib/types";

/** Standart başına karşılanan gereksinim oranı (yatay bar). */
export function RegulationBar({ regulations }: { regulations: RegulationResult[] }) {
  const data = regulations.map((r) => {
    const total = r.requirements.length;
    const passed = r.requirements.filter((q) => q.passed === true).length;
    return {
      name: r.name.split(" (")[0],
      pct: total ? Math.round((passed / total) * 100) : 0,
      ok: r.passed === true,
    };
  });

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 18, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--foreground) / 0.06)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis
            type="category"
            dataKey="name"
            width={150}
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            cursor={{ fill: "hsl(var(--foreground) / 0.04)" }}
            contentStyle={{
              background: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 12,
              fontSize: 12,
              color: "hsl(var(--foreground))",
            }}
            formatter={(value) => [`%${value} gereksinim karşılandı`, ""]}
          />
          <Bar
            dataKey="pct"
            radius={[6, 6, 6, 6]}
            barSize={14}
            animationDuration={900}
            background={{ fill: "hsl(var(--foreground) / 0.07)", radius: 6 }}
          >
            {data.map((d, i) => (
              <Cell
                key={i}
                fill={d.ok ? "hsl(var(--chart-3))" : d.pct >= 50 ? "hsl(var(--chart-4))" : "hsl(var(--chart-5))"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
