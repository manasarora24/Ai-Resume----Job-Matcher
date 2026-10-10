import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "CareerIQ AI — Find your next move", description: "Understand your strengths and discover opportunities with clear, evidence-based career matching." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
