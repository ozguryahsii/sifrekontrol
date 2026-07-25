"use client";

import { useCallback, useEffect, useState } from "react";
import { Database, FileDigit, HardDrive, ShieldCheck } from "lucide-react";
import { PageShell } from "@/components/layout/page-shell";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { QuickCheckCard } from "@/components/dashboard/quick-check-card";
import { DatasetStatusCard } from "@/components/dashboard/dataset-status-card";
import { ApiOfflineCard } from "@/components/dashboard/api-offline-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { UpdatesAreaChart, type UpdatePoint } from "@/components/charts/updates-area-chart";
import { getStatus } from "@/lib/api";
import type { DatasetStatus } from "@/lib/types";
import { formatBytes } from "@/lib/utils";

/**
 * Örnek senaryo verisi: günlük `sifrekontrol update` çalıştıran bir kurumda
 * değişen aralık sayısının tipik seyri. Gerçek geçmiş henüz loglanmadığı için
 * "örnek veri" rozetiyle işaretlenir.
 */
const DEMO_UPDATE_HISTORY: UpdatePoint[] = [
  { day: "12 Tem", changed: 18240 },
  { day: "13 Tem", changed: 9310 },
  { day: "14 Tem", changed: 11890 },
  { day: "15 Tem", changed: 46520 },
  { day: "16 Tem", changed: 22110 },
  { day: "17 Tem", changed: 8140 },
  { day: "18 Tem", changed: 7960 },
  { day: "19 Tem", changed: 31770 },
  { day: "20 Tem", changed: 15420 },
  { day: "21 Tem", changed: 12080 },
  { day: "22 Tem", changed: 9840 },
  { day: "23 Tem", changed: 27310 },
  { day: "24 Tem", changed: 13560 },
  { day: "25 Tem", changed: 10230 },
];

export default function DashboardPage() {
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
      <div className="space-y-6">
        <QuickCheckCard />

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            index={0}
            label="Sızmış şifre kaydı"
            icon={FileDigit}
            value={status?.records ?? 0}
            hint="HIBP offline veri setinde"
            tone="primary"
          />
          <KpiCard
            index={1}
            label="Grup dosyası"
            icon={Database}
            value={status?.groups_present ?? 0}
            hint={`${status?.groups_total ?? 4096} hedef`}
            tone="accent"
          />
          <KpiCard
            index={2}
            label="Disk kullanımı"
            icon={HardDrive}
            valueText={status ? formatBytes(status.size_bytes) : "—"}
            hint="Sıralı binary depo"
            tone="warning"
          />
          <KpiCard
            index={3}
            label="Denetlenen standart"
            icon={ShieldCheck}
            value={6}
            hint="NIST · PCI · OWASP · CIS · KVKK · ISO"
            tone="success"
          />
        </div>

        <div className="grid gap-5 lg:grid-cols-5">
          <Card className="lg:col-span-3">
            <CardHeader className="flex-row items-start justify-between space-y-0">
              <div>
                <CardTitle>Artımlı Güncelleme Aktivitesi</CardTitle>
                <CardDescription>Günlük değişen HIBP aralığı sayısı (son 14 gün)</CardDescription>
              </div>
              <Badge variant="outline">Örnek veri</Badge>
            </CardHeader>
            <CardContent>
              <UpdatesAreaChart data={DEMO_UPDATE_HISTORY} />
            </CardContent>
          </Card>
          <div className="lg:col-span-2">
            <DatasetStatusCard status={status} loading={loading} />
          </div>
        </div>
      </div>
    </PageShell>
  );
}
