import "./globals.css";

export const metadata = {
  title: "Noetfield Admin",
  description: "Enterprise administration for governed intelligence.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
