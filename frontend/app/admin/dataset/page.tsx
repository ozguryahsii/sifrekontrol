"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CalendarClock,
  DownloadCloud,
  FolderTree,
  RefreshCw,
  TerminalSquare,
} from "lucide-react";
import { motion } from "motion/react";
import { PageShell } from "@/components/layout/page-shell";
import { ApiOfflineCard } from "@/components/dashboard/api-offline-card";
import { DatasetStatusCard } from "@/components/dashboard/dataset-status-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getStatus } from "@/lib/api";
import type { DatasetStatus } from "@/lib/types";

function CommandBlock({ label, command }: { label: string; command: string }) {
  return (
    <div>
      <p className="mb-1.5 text-[11px] font-medium text-muted-foreground">{label}</p>
      <code className="flex items-center gap-2 rounded-xl bg-secondary/70 px-4 py-2.5 font-mono text-xs">
        <TerminalSquare className="h-4 w-4 shrink-0 text-accent" />
        {command}
      </code>
    </div>
  );
}

const STEPS = [
  {
    icon: DownloadCloud,
    title: "İlk indirme",
    desc: "1.048.576 HIBP aralığı paralel indirilir, her aralığın ETag'i kaydedilir. Yarıda kesilirse aynı komut kaldığı yerden devam eder.",
  },
  {
    icon: RefreshCw,
    title: "Artımlı güncelleme",
    desc: "Her aralık If-None-Match ile sorulur; değişmeyenler 304 döner, yalnızca değişen aralıklar indirilir ve ilgili dosyalar yeniden yazılır.",
  },
  {
    icon: CalendarClock,
    title: "Zamanlanmış çalışma",
    desc: "Cron ile günlük veya haftalık güncelleme önerilir; bir tur tipik olarak 1 saatin altında tamamlanır.",
  },
] as const;

export default function DatasetPage() {
  const [status, setStatus] = useState<DatasetStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setOffline(false);
    getStatus()
      .then(setStatus)
      .catch(() => setOffline(true))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  if (offline) {
    return (
      <PageShell>
        <ApiOfflineCard onRetry={load} />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <div className="grid gap-5 lg:grid-cols-5">
        <div className="space-y-5 lg:col-span-3">
          {/* Yaşam döngüsü adımları */}
          <Card>
            <CardHeader>
              <CardTitle>Veri Seti Yaşam Döngüsü</CardTitle>
              <CardDescription>
                HIBP Pwned Passwords · ETag tabanlı artımlı senkronizasyon
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              {STEPS.map(({ icon: Icon, title, desc }, i) => (
                <motion.div
                  key={title}
                  initial={{ opacity: 0, x: -14 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.35, delay: i * 0.08 }}
                  className="flex gap-4"
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600/15 to-cyan-500/15">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{title}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">{desc}</p>
                  </div>
                </motion.div>
              ))}
            </CardContent>
          </Card>

          {/* Komutlar */}
          <Card>
            <CardHeader className="flex-row items-start justify-between space-y-0">
              <div>
                <CardTitle>Komutlar</CardTitle>
                <CardDescription>Veri setini terminalden yönetin</CardDescription>
              </div>
              <Badge variant="accent">CLI</Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <CommandBlock label="Tam veri setini indir (~25-30 GB, bir kerelik)" command="sifrekontrol download" />
              <CommandBlock label="Artımlı güncelle (yalnızca değişen aralıklar)" command="sifrekontrol update" />
              <CommandBlock label="Her gece 03:15'te otomatik güncelle (crontab)" command="15 3 * * * sifrekontrol update" />
              <Separator />
              <div className="flex items-start gap-2.5 text-[11px] leading-relaxed text-muted-foreground">
                <FolderTree className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" />
                <span>
                  Veri dizini: <code className="rounded bg-secondary/70 px-1 py-0.5">{status?.data_dir ?? "~/.local/share/sifrekontrol"}</code>{" "}
                  — 4096 sıralı binary grup dosyası; sorgular mmap + binary search ile milisaniyede tamamlanır.
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <DatasetStatusCard status={status} loading={loading} />
        </div>
      </div>
    </PageShell>
  );
}
