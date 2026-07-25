"use client";

import type { LucideIcon } from "lucide-react";
import { motion } from "motion/react";
import { Card } from "@/components/ui/card";
import { NumberTicker } from "@/components/ui/number-ticker";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  icon: LucideIcon;
  value?: number;
  valueText?: string;
  hint?: string;
  tone?: "primary" | "accent" | "success" | "warning";
  index?: number;
}

const TONES = {
  primary: "from-violet-600/20 to-violet-600/5 text-primary",
  accent: "from-cyan-500/20 to-cyan-500/5 text-accent",
  success: "from-emerald-500/20 to-emerald-500/5 text-success",
  warning: "from-amber-500/20 to-amber-500/5 text-warning",
} as const;

export function KpiCard({
  label,
  icon: Icon,
  value,
  valueText,
  hint,
  tone = "primary",
  index = 0,
}: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
    >
      <Card className="group relative overflow-hidden p-5 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/10">
        <div className="flex items-start justify-between">
          <div className="min-w-0">
            <p className="text-xs font-medium text-muted-foreground">{label}</p>
            <div className="mt-2 text-2xl font-bold tracking-tight">
              {value !== undefined ? <NumberTicker value={value} delay={index * 0.07} /> : valueText}
            </div>
            {hint && <p className="mt-1 truncate text-[11px] text-muted-foreground">{hint}</p>}
          </div>
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br transition-transform duration-300 group-hover:scale-110",
              TONES[tone]
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
