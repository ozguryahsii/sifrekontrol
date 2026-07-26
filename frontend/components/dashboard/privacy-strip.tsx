"use client";

import { Lock } from "lucide-react";
import { motion } from "motion/react";
import { StatusDot } from "@/components/ui/status-dot";

/** Ana sayfadaki gizlilik güvencesi şeridi. */
export function PrivacyStrip() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="glass gradient-border flex flex-col items-center justify-center gap-2 rounded-2xl px-5 py-3.5 text-center sm:flex-row sm:gap-5"
    >
      <div className="flex items-center gap-2 text-xs">
        <Lock className="h-3.5 w-3.5 shrink-0 text-accent" />
        <span className="font-semibold">%100 Lokal Çalışır</span>
        <span className="text-muted-foreground">
          — Şifreler saklanmaz, loglanmaz, internete gönderilmez.
        </span>
      </div>
      <div className="hidden h-4 w-px bg-border sm:block" />
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <StatusDot tone="success" />
        Çevrimdışı analiz motoru aktif
      </div>
    </motion.div>
  );
}
