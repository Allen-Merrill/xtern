import type { Metadata } from 'next';
import './globals.css';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Supply Chain PO Automation',
  description: 'Multi-Agent Purchase Order System',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen bg-gray-50">
        <aside className="w-64 bg-slate-800 text-white p-6">
          <h1 className="text-xl font-bold mb-8">SC-PO System</h1>
          <nav className="space-y-2">
            <Link href="/" className="block px-4 py-2 rounded hover:bg-slate-700">
              Dashboard
            </Link>
            <Link href="/pipeline" className="block px-4 py-2 rounded hover:bg-slate-700">
              Run Pipeline
            </Link>
            <Link href="/approvals" className="block px-4 py-2 rounded hover:bg-slate-700">
              Approval Queue
            </Link>
            <Link href="/logs" className="block px-4 py-2 rounded hover:bg-slate-700">
              Decision Log
            </Link>
          </nav>
        </aside>
        <main className="flex-1 p-8">{children}</main>
      </body>
    </html>
  );
}