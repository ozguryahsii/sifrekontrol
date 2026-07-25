"use client";

import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

/** Veri seti kapsama oranını (indirilen grup / toplam) donut olarak çizer. */
export function CoverageDonut({
  present,
  total,
  className,
}: {
  present: number;
  total: number;
  className?: string;
}) {
  const pct = total > 0 ? Math.round((present / total) * 100) : 0;
  const data = [
    { name: "İndirildi", value: present },
    { name: "Eksik", value: Math.max(0, total - present) },
  ];

  return (
    <div className={cn("relative h-44 w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            innerRadius="72%"
            outerRadius="92%"
            startAngle={90}
            endAngle={-270}
            paddingAngle={2}
            cornerRadius={8}
            stroke="none"
            isAnimationActive
            animationDuration={900}
          >
            <Cell fill="hsl(var(--chart-2))" />
            <Cell fill="hsl(var(--foreground) / 0.07)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-3xl font-bold tabular-nums">%{pct}</div>
        <div className="text-[11px] text-muted-foreground">kapsam</div>
      </div>
    </div>
  );
}
