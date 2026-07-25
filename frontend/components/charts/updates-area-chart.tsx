"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface UpdatePoint {
  day: string;
  changed: number;
}

/** Günlük artımlı güncellemede değişen aralık sayısı (alan grafiği). */
export function UpdatesAreaChart({ data }: { data: UpdatePoint[] }) {
  return (
    <div className="h-56 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -14, bottom: 0 }}>
          <defs>
            <linearGradient id="updatesFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(var(--chart-1))" stopOpacity={0.35} />
              <stop offset="100%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--foreground) / 0.06)" vertical={false} />
          <XAxis
            dataKey="day"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickLine={false}
            axisLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
            tickLine={false}
            axisLine={false}
            width={54}
            tickFormatter={(v: number) => new Intl.NumberFormat("tr-TR", { notation: "compact" }).format(v)}
          />
          <Tooltip
            cursor={{ stroke: "hsl(var(--primary) / 0.3)" }}
            contentStyle={{
              background: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: 12,
              fontSize: 12,
              color: "hsl(var(--foreground))",
            }}
            formatter={(value) => [
              new Intl.NumberFormat("tr-TR").format(Number(value)) + " aralık",
              "Değişen",
            ]}
          />
          <Area
            type="monotone"
            dataKey="changed"
            stroke="hsl(var(--chart-1))"
            strokeWidth={2}
            fill="url(#updatesFill)"
            animationDuration={900}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
