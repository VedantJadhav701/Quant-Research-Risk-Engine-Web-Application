import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Quantum Risk Engine | Quant Research Platform",
  description: "Advanced Volatility Modeling and Monte Carlo Risk Simulations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        {children}
        <Script 
          src="https://cdn.plot.ly/plotly-2.35.2.min.js" 
          strategy="beforeInteractive"
        />
      </body>
    </html>
  );
}
