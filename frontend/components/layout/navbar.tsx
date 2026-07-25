"use client";

import { usePathname } from "next/navigation";
import { ShieldCheck, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "./theme-toggle";

const TITLES: Record<string, { title: string; subtitle: string }> = {
  "/": {
    title: "Genel Bakış",
    subtitle: "Veri seti durumu ve güvenlik özetiniz",
  },
  "/check": {
    title: "Şifre Analizi",
    subtitle: "Güç, sızıntı ve regülasyon uyumluluğu denetimi",
  },
  "/dataset": {
    title: "Veri Seti",
    subtitle: "HIBP offline veri seti yönetimi ve güncelleme",
  },
};

export function Navbar() {
  const pathname = usePathname();
  const { title, subtitle } = TITLES[pathname] ?? TITLES["/"];

  return (
    <header className="sticky top-0 z-30 border-b border-border/60 glass">
      <div className="flex h-16 items-center justify-between gap-4 px-6 lg:px-10">
        <div className="flex items-center gap-3 lg:hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-cyan-500">
            <ShieldCheck className="h-4 w-4 text-white" />
          </div>
          <span className="text-sm font-bold">sifrekontrol</span>
        </div>
        <div className="hidden lg:block">
          <h1 className="text-base font-semibold tracking-tight">{title}</h1>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="accent" className="hidden sm:inline-flex">
            <WifiOff /> Çevrimdışı mod
          </Badge>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
