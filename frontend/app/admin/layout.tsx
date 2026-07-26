import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";

/**
 * Yönetim bölümü kabuğu: sol menü + üst çubuk yalnızca /admin altında görünür.
 * Ana sayfadan buraya bağlantı verilmez; adres manuel girilir.
 */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Sidebar />
      <div className="lg:pl-64">
        <Navbar />
        {children}
      </div>
    </>
  );
}
