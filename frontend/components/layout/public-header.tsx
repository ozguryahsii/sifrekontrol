"use client";

import { ShieldCheck, WifiOff } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "./theme-toggle";

/** Son kullanıcı sayfasının sade üst çubuğu (menüsüz). */
export function PublicHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-border/60 glass">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between gap-4 px-6 lg:px-10">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg shadow-primary/30">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight">sifrekontrol</div>
            <div className="text-[11px] text-muted-foreground">Şifre Güvenlik Analizi</div>
          </div>
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
