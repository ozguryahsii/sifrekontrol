"use client";

import { RefreshCw, ServerOff, TerminalSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

/** Backend'e ulaşılamadığında gösterilen hata durumu. */
export function ApiOfflineCard({ onRetry }: { onRetry: () => void }) {
  return (
    <Card className="gradient-border flex flex-col items-center gap-4 p-10 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-danger/10">
        <ServerOff className="h-7 w-7 text-danger" />
      </div>
      <div>
        <h3 className="text-base font-semibold">Analiz motoruna ulaşılamadı</h3>
        <p className="mx-auto mt-1.5 max-w-sm text-xs leading-relaxed text-muted-foreground">
          Python backend&apos;i çalışmıyor görünüyor. Bir terminalde aşağıdaki komutu
          çalıştırıp tekrar deneyin:
        </p>
      </div>
      <code className="flex items-center gap-2 rounded-xl bg-secondary/70 px-4 py-2.5 font-mono text-xs">
        <TerminalSquare className="h-4 w-4 text-accent" />
        sifrekontrol serve --port 3002
      </code>
      <Button variant="outline" size="sm" onClick={onRetry}>
        <RefreshCw /> Tekrar dene
      </Button>
    </Card>
  );
}
