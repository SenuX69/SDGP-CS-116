import type { Metadata } from "next";
import Footer from "./components/layout/footer";
import "./globals.css";

export const metadata: Metadata = {
  title: "PathFinder+",
  description: "PathFinder+ career guidance platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen bg-white font-sans antialiased">
        <div className="flex flex-col min-h-screen">
          <main className="grow">
            {children}
          </main>

          <Footer />
        </div>
      </body>
    </html>
  );
}