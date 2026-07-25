"use client";

import { PolarAngleAxis, RadialBar, RadialBarChart, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

const SCORE_META = [
  { label: "Çok Zayıf", color: "hsl(var(--danger))" },
  { label: "Zayıf", color: "hsl(var(--danger))" },
  { label: "Orta", color: "hsl(var(--warning))" },
  { label: "Güçlü", color: "hsl(var(--success))" },
  { label: "Çok Güçlü", color: "hsl(var(--success))" },
] as const;

/** 0-4 güç skorunu yarım daire gauge olarak çizer. */
export function ScoreGauge({ score, className }: { score: number; className?: string }) {
  const meta = SCORE_META[score] ?? SCORE_META[0];
  const pct = (score / 4) * 100;

  return (
    <div className={cn("relative h-44 w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart
          cx="50%"
          cy="72%"
          innerRadius="115%"
          outerRadius="150%"
          startAngle={180}
          endAngle={0}
          data={[{ value: pct }]}
          barSize={16}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar
            dataKey="value"
            angleAxisId={0}
            cornerRadius={10}
            fill={meta.color}
            background={{ fill: "hsl(var(--foreground) / 0.07)" }}
            isAnimationActive
            animationDuration={900}
          />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-x-0 bottom-3 text-center">
        <div className="text-4xl font-bold tabular-nums tracking-tight">
          {score}
          <span className="text-lg font-medium text-muted-foreground">/4</span>
        </div>
        <div className="mt-0.5 text-xs font-medium" style={{ color: meta.color }}>
          {meta.label}
        </div>
      </div>
    </div>
  );
}
