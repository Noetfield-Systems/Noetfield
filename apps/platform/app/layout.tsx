import "./globals.css";

export const metadata = {
  title: "Noetfield Platform",
  description: "Governed intelligence operating system workspace.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
