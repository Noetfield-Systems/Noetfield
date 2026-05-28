import "./globals.css";

export const metadata = {
  title: "Noetfield",
  description: "AI trust infrastructure for governed ambient intelligence.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
