"use client";

import { Fingerprint } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/** Analiz beklenirken gösterilen iskelet düzeni. */
export function CheckSkeleton() {
  return (
    <div className="space-y-5">
      <div className="grid gap-5 lg:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-3 w-40" />
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="mx-auto h-28 w-28 rounded-full" />
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-3/4" />
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-44" />
              <Skeleton className="h-3 w-32" />
            </CardHeader>
            <CardContent className="space-y-2.5">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-5/6" />
              <Skeleton className="h-3 w-2/3" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

/** Henüz analiz yapılmadığında gösterilen boş durum. */
export function CheckEmptyState() {
  return (
    <Card className="flex flex-col items-center gap-4 border-dashed p-14 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600/15 to-cyan-500/15">
        <Fingerprint className="h-8 w-8 text-primary" />
      </div>
      <div>
        <h3 className="text-sm font-semibold">Analize hazır</h3>
        <p className="mx-auto mt-1.5 max-w-sm text-xs leading-relaxed text-muted-foreground">
          Yukarıya bir şifre girin; güç skoru, sızıntı geçmişi ve regülasyon uyumluluğu
          saniyeler içinde burada görünsün.
        </p>
      </div>
    </Card>
  );
}
