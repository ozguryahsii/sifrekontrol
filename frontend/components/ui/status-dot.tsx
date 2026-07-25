import { cn } from "@/lib/utils";

/** Canlı durum noktası: renkli çekirdek + yumuşak ping halkası. */
export function StatusDot({
  tone = "success",
  className,
}: {
  tone?: "success" | "warning" | "danger";
  className?: string;
}) {
  const tones = {
    success: "bg-success",
    warning: "bg-warning",
    danger: "bg-danger",
  } as const;
  return (
    <span className={cn("relative inline-flex h-2 w-2", className)}>
      <span
        className={cn(
          "absolute inline-flex h-full w-full animate-ping rounded-full opacity-60",
          tones[tone]
        )}
      />
      <span className={cn("relative inline-flex h-2 w-2 rounded-full", tones[tone])} />
    </span>
  );
}
