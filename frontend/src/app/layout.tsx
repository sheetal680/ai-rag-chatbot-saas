import type { Metadata } from "next";
import "./globals.css";
import AuthHydrator from "@/components/AuthHydrator";
import Toaster from "@/components/ui/Toaster";

export const metadata: Metadata = {
  title: "RAGBot — AI Customer Support",
  description: "Train your own AI chatbot on your documents. Embed it anywhere in minutes.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <AuthHydrator />
        {children}
        <Toaster />
      </body>
    </html>
  );
}
