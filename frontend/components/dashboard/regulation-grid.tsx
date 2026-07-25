"use client";

import { CheckCircle2, HelpCircle, XCircle } from "lucide-react";
import { motion } from "motion/react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { RegulationResult, Requirement } from "@/lib/types";
import { cn } from "@/lib/utils";

function StateIcon({ passed, className }: { passed: boolean | null; className?: string }) {
  if (passed === true) return <CheckCircle2 className={cn("text-success", className)} />;
  if (passed === false) return <XCircle className={cn("text-danger", className)} />;
  return <HelpCircle className={cn("text-warning", className)} />;
}

function RequirementRow({ req }: { req: Requirement }) {
  return (
    <li className="flex items-start gap-2.5 text-xs">
      <StateIcon passed={req.passed} className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span className="leading-relaxed text-foreground/90">
        {req.description}
        {req.detail && <span className="text-muted-foreground"> — {req.detail}</span>}
      </span>
    </li>
  );
}

/** Standart bazlı uyumluluk kartları (kademeli giriş animasyonlu). */
export function RegulationGrid({ regulations }: { regulations: RegulationResult[] }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {regulations.map((reg, i) => (
        <motion.div
          key={reg.id}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.25 + i * 0.07, ease: [0.22, 1, 0.36, 1] }}
        >
          <Card
            className={cn(
              "h-full transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl",
              reg.passed === true && "hover:shadow-success/10",
              reg.passed === false && "hover:shadow-danger/10"
            )}
          >
            <CardHeader className="flex-row items-start justify-between gap-3 space-y-0">
              <div className="min-w-0">
                <CardTitle className="text-[13px] leading-snug">{reg.name}</CardTitle>
                <CardDescription className="mt-1 line-clamp-2">{reg.scope}</CardDescription>
              </div>
              {reg.passed === true ? (
                <Badge variant="success">Uyumlu</Badge>
              ) : reg.passed === false ? (
                <Badge variant="danger">Uyumsuz</Badge>
              ) : (
                <Badge variant="warning">Belirsiz</Badge>
              )}
            </CardHeader>
            <CardContent>
              <Separator className="mb-4" />
              <ul className="space-y-2.5">
                {reg.requirements.map((req, j) => (
                  <RequirementRow key={j} req={req} />
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
