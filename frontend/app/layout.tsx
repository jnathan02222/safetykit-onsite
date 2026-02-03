import type { Metadata } from "next";
import { Noto_Serif } from "next/font/google";
import "./globals.css";

const noto_serif = Noto_Serif({
  variable: "--font-noto_serif",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Atlas",
  description: "Musicians mapped!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${noto_serif.variable} antialiased`}>{children}</body>
    </html>
  );
}
