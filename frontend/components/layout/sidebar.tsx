"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import {
  Database,
  LayoutDashboard,
  Lock,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { StatusDot } from "@/components/ui/status-dot";

const NAV = [
  { href: "/admin", label: "Genel Bakış", icon: LayoutDashboard },
  { href: "/admin/dataset", label: "Veri Seti", icon: Database },
  { href: "/", label: "Şifre Analizi", icon: ScanSearch },
] as const;

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-border/60 glass lg:flex">
      {/* Marka */}
      <div className="flex items-center gap-3 px-6 py-6">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg shadow-primary/30">
          <ShieldCheck className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight">sifrekontrol</div>
          <div className="text-[11px] text-muted-foreground">Yönetim Paneli</div>
        </div>
      </div>

      {/* Navigasyon */}
      <nav className="mt-2 flex-1 space-y-1 px-3">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors",
                active
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              {active && (
                <motion.span
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl bg-secondary/80 ring-1 ring-primary/25"
                  transition={{ type: "spring", stiffness: 400, damping: 32 }}
                />
              )}
              <Icon
                className={cn(
                  "relative z-10 h-4 w-4 transition-transform duration-200 group-hover:scale-110",
                  active && "text-primary"
                )}
              />
              <span className="relative z-10 font-medium">{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Gizlilik rozeti */}
      <div className="m-4 rounded-2xl gradient-border glass p-4">
        <div className="flex items-center gap-2 text-xs font-semibold">
          <Lock className="h-3.5 w-3.5 text-accent" />
          %100 Lokal Çalışır
        </div>
        <p className="mt-1.5 text-[11px] leading-relaxed text-muted-foreground">
          Şifreler saklanmaz, loglanmaz, internete gönderilmez.
        </p>
        <div className="mt-3 flex items-center gap-2 text-[11px] text-muted-foreground">
          <StatusDot tone="success" />
          Çevrimdışı analiz motoru aktif
        </div>
      </div>
    </aside>
  );
}
