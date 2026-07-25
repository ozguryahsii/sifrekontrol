"use client";

import { useState } from "react";
import { Eye, EyeOff, Lock, ScanSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { BorderBeam } from "@/components/ui/border-beam";

export function CheckForm({
  onSubmit,
  loading,
}: {
  onSubmit: (password: string) => void;
  loading: boolean;
}) {
  const [password, setPassword] = useState("");
  const [visible, setVisible] = useState(false);

  return (
    <Card className="relative overflow-hidden p-6">
      <BorderBeam duration={11} />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (password) onSubmit(password);
        }}
        autoComplete="off"
        className="flex flex-col gap-3 sm:flex-row"
      >
        <div className="relative flex-1">
          <Lock className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            type={visible ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Analiz edilecek şifre…"
            autoComplete="new-password"
            className="pl-11 pr-11"
            aria-label="Analiz edilecek şifre"
          />
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            aria-label={visible ? "Şifreyi gizle" : "Şifreyi göster"}
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
          >
            {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        <Button type="submit" variant="gradient" size="lg" disabled={loading || !password}>
          <ScanSearch className={loading ? "animate-spin" : ""} />
          {loading ? "Analiz ediliyor…" : "Analiz et"}
        </Button>
      </form>
      <p className="mt-3 text-[11px] text-muted-foreground">
        Şifreniz yalnızca bu makinede analiz edilir; saklanmaz, loglanmaz, internete
        gönderilmez.
      </p>
    </Card>
  );
}
