import "../styles/globals.css";

export const metadata = {
  title: "i7 Loaner Deal Scanner",
  description: "Scan BMW i7 loaner listings across the Southeast.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
