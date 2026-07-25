"use client";

import { Database, HardDrive, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { CoverageDonut } from "@/components/charts/coverage-donut";
import type { DatasetStatus } from "@/lib/types";
import { formatBytes, formatNumberTR } from "@/lib/utils";

export function DatasetStatusCard({
  status,
  loading,
}: {
  status: DatasetStatus | null;
  loading: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between space-y-0">
        <div>
          <CardTitle>HIBP Veri Seti</CardTitle>
          <CardDescription>Offline sızıntı veritabanı durumu</CardDescription>
        </div>
        {status &&
          (status.complete ? (
            <Badge variant="success">Tam kapsam</Badge>
          ) : (
            <Badge variant="warning">Eksik kapsam</Badge>
          ))}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-4">
            <Skeleton className="mx-auto h-40 w-40 rounded-full" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-2/3" />
          </div>
        ) : status ? (
          <>
            <CoverageDonut present={status.groups_present} total={status.groups_total} />
            <div className="mt-4 space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Database className="h-3.5 w-3.5" /> Grup dosyaları
                </span>
                <span className="font-medium tabular-nums">
                  {formatNumberTR(status.groups_present)} / {formatNumberTR(status.groups_total)}
                </span>
              </div>
              <Progress value={(status.groups_present / status.groups_total) * 100} />
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <HardDrive className="h-3.5 w-3.5" /> Disk kullanımı
                </span>
                <span className="font-medium">{formatBytes(status.size_bytes)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <RefreshCw className="h-3.5 w-3.5" /> Son senkron
                </span>
                <span className="font-medium">
                  {status.updated_at
                    ? new Date(status.updated_at).toLocaleString("tr-TR", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      })
                    : "Henüz yok"}
                </span>
              </div>
            </div>
          </>
        ) : (
          <p className="py-8 text-center text-xs text-muted-foreground">
            Veri seti bilgisi alınamadı.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
