"use client";

import { useRouter } from "next/navigation";
import { ArrowRight, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { BorderBeam } from "@/components/ui/border-beam";

/** Dashboard'dan analiz ekranına yönlendiren vitrin kartı. */
export function QuickCheckCard() {
  const router = useRouter();
  return (
    <Card className="relative overflow-hidden p-6">
      <BorderBeam />
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-cyan-500 shadow-lg shadow-primary/30">
            <ScanSearch className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-base font-semibold tracking-tight">Şifre güvenliğini şimdi test edin</h3>
            <p className="mt-1 max-w-md text-xs leading-relaxed text-muted-foreground">
              Güç analizi, 850M+ sızmış şifre içinde offline arama ve 6 uluslararası
              standarda göre uyumluluk raporu — tamamı bu makinede, saniyeler içinde.
            </p>
          </div>
        </div>
        <Button variant="gradient" size="lg" onClick={() => router.push("/check")}>
          Analize başla <ArrowRight />
        </Button>
      </div>
    </Card>
  );
}
