"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { PublicHeader } from "@/components/layout/public-header";
import { CheckForm } from "@/components/dashboard/check-form";
import { PrivacyStrip } from "@/components/dashboard/privacy-strip";
import { ResultSummary } from "@/components/dashboard/result-summary";
import { RegulationGrid } from "@/components/dashboard/regulation-grid";
import { CheckEmptyState, CheckSkeleton } from "@/components/dashboard/check-states";
import { ApiOfflineCard } from "@/components/dashboard/api-offline-card";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RegulationBar } from "@/components/charts/regulation-bar";
import { checkPassword } from "@/lib/api";
import type { CheckResult } from "@/lib/types";

type ViewState =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "error" }
  | { kind: "result"; data: CheckResult };

/** Ana sayfa: son kullanıcı için sadeleştirilmiş şifre analizi ekranı. */
export default function HomePage() {
  const [state, setState] = useState<ViewState>({ kind: "idle" });

  const runCheck = (password: string) => {
    setState({ kind: "loading" });
    checkPassword(password)
      .then((data) => setState({ kind: "result", data }))
      .catch(() => setState({ kind: "error" }));
  };

  return (
    <>
      <PublicHeader />
      <motion.main
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="mx-auto w-full max-w-6xl px-6 py-8 lg:px-10"
      >
        <div className="space-y-5">
          <CheckForm onSubmit={runCheck} loading={state.kind === "loading"} />
          <PrivacyStrip />

          <AnimatePresence mode="wait">
            {state.kind === "idle" && (
              <motion.div key="idle" exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.2 }}>
                <CheckEmptyState />
              </motion.div>
            )}

            {state.kind === "loading" && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <CheckSkeleton />
              </motion.div>
            )}

            {state.kind === "error" && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
              >
                <ApiOfflineCard onRetry={() => setState({ kind: "idle" })} />
              </motion.div>
            )}

            {state.kind === "result" && (
              <motion.div
                key="result"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25 }}
                className="space-y-6"
              >
                <ResultSummary result={state.data} />

                <Card>
                  <CardHeader>
                    <CardTitle>Uyumluluk Özeti</CardTitle>
                    <CardDescription>Standart başına karşılanan gereksinim oranı</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <RegulationBar regulations={state.data.regulations} />
                  </CardContent>
                </Card>

                <RegulationGrid regulations={state.data.regulations} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.main>
    </>
  );
}
