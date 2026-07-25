"use client";

import {
  AlertTriangle,
  CloudOff,
  Lightbulb,
  ShieldAlert,
  ShieldCheck,
  Timer,
  Zap,
} from "lucide-react";
import { motion } from "motion/react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { NumberTicker } from "@/components/ui/number-ticker";
import { ScoreGauge } from "@/components/charts/score-gauge";
import type { CheckResult } from "@/lib/types";
import { cn } from "@/lib/utils";

const item = {
  hidden: { opacity: 0, y: 18 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

/** Analiz sonucunun üst bölümü: skor, sızıntı ve kırılma süreleri. */
export function ResultSummary({ result }: { result: CheckResult }) {
  const breached = (result.breach_count ?? 0) > 0;
  const datasetMissing = result.breach_count === null;

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {/* Güç skoru */}
      <motion.div variants={item} initial="hidden" animate="show" custom={0}>
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Güç Skoru</CardTitle>
            <CardDescription>zxcvbn analiz motoru · {result.length} karakter</CardDescription>
          </CardHeader>
          <CardContent>
            <ScoreGauge score={result.strength.score} />
          </CardContent>
        </Card>
      </motion.div>

      {/* Sızıntı durumu */}
      <motion.div variants={item} initial="hidden" animate="show" custom={1}>
        <Card
          className={cn(
            "h-full",
            breached && "glow-danger ring-1 ring-danger/30",
            !breached && !datasetMissing && "glow-success ring-1 ring-success/25"
          )}
        >
          <CardHeader>
            <CardTitle>Sızıntı Kontrolü</CardTitle>
            <CardDescription>HIBP offline veri seti · 850M+ kayıt</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-3 pb-8 pt-2 text-center">
            {datasetMissing ? (
              <>
                <CloudOff className="h-10 w-10 text-warning" />
                <p className="text-sm font-medium">Veri seti indirilmemiş</p>
                <p className="text-[11px] leading-relaxed text-muted-foreground">
                  <code className="rounded bg-secondary/70 px-1.5 py-0.5">sifrekontrol download</code>{" "}
                  ile offline sızıntı kontrolünü etkinleştirin.
                </p>
              </>
            ) : breached ? (
              <>
                <ShieldAlert className="h-10 w-10 text-danger" />
                <div className="text-3xl font-bold text-danger">
                  <NumberTicker value={result.breach_count ?? 0} />
                  <span className="ml-1 text-sm font-medium">kez</span>
                </div>
                <p className="text-xs font-medium text-danger">Bilinen sızıntılarda görüldü</p>
                <p className="text-[11px] leading-relaxed text-muted-foreground">
                  Veri seti hangi sitede sızdığını içermez (anonimleştirilmiştir);
                  yalnızca toplam görülme sayısı bilinir.
                </p>
              </>
            ) : (
              <>
                <ShieldCheck className="h-10 w-10 text-success" />
                <p className="text-sm font-semibold text-success">Sızıntılarda bulunamadı</p>
                <p className="text-[11px] text-muted-foreground">
                  Bilinen hiçbir sızıntı listesinde yer almıyor.
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Kırılma süreleri + uyarılar */}
      <motion.div variants={item} initial="hidden" animate="show" custom={2}>
        <Card className="h-full">
          <CardHeader>
            <CardTitle>Kırılma Süresi Tahmini</CardTitle>
            <CardDescription>Saldırı senaryolarına göre</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-xl bg-secondary/50 px-4 py-3">
              <span className="flex items-center gap-2 text-xs text-muted-foreground">
                <Zap className="h-4 w-4 text-warning" /> Hızlı offline saldırı
              </span>
              <span className="text-sm font-semibold">{result.strength.crack_time_offline_fast}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-secondary/50 px-4 py-3">
              <span className="flex items-center gap-2 text-xs text-muted-foreground">
                <Timer className="h-4 w-4 text-accent" /> Hız sınırlı online
              </span>
              <span className="text-sm font-semibold">{result.strength.crack_time_online}</span>
            </div>
            {(result.strength.warnings.length > 0 || result.strength.suggestions.length > 0) && (
              <div className="space-y-2 pt-1">
                {result.strength.warnings.map((w) => (
                  <Badge
                    key={w}
                    variant="warning"
                    className="w-full items-start justify-start rounded-xl py-1.5 text-left leading-snug [&_svg]:mt-0.5 [&_svg]:shrink-0"
                  >
                    <AlertTriangle /> <span>{w}</span>
                  </Badge>
                ))}
                {result.strength.suggestions.map((s) => (
                  <Badge
                    key={s}
                    variant="accent"
                    className="w-full items-start justify-start rounded-xl py-1.5 text-left leading-snug [&_svg]:mt-0.5 [&_svg]:shrink-0"
                  >
                    <Lightbulb /> <span>{s}</span>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
