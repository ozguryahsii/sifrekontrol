"use client";

import { motion } from "motion/react";

/** Sayfa içeriği kabuğu: giriş animasyonu + tutarlı boşluklar. */
export function PageShell({ children }: { children: React.ReactNode }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="mx-auto w-full max-w-6xl px-6 py-8 lg:px-10"
    >
      {children}
    </motion.main>
  );
}
