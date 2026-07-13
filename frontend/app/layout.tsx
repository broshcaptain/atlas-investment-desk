import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Atlas — Yatırım Araştırma Masaüstü",
  description: "Tek kullanıcı için profesyonel yatırım araştırma masaüstü uygulaması.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
