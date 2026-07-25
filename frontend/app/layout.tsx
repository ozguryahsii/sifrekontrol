import type { Metadata } from "next";
import "./globals.css";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";

export const metadata: Metadata = {
  title: "sifrekontrol — Password Security Suite",
  description:
    "Tamamen lokal çalışan şifre güvenlik denetleyicisi: HIBP offline sızıntı kontrolü, güç analizi ve regülasyon uyumluluğu.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body className="min-h-screen">
        <ThemeProvider>
          <div className="bg-aurora bg-dot-grid fixed inset-0 -z-10" />
          <Sidebar />
          <div className="lg:pl-64">
            <Navbar />
            {children}
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
