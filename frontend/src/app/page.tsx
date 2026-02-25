'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { fetchHealth } from '@/lib/api';

export default function DashboardPage() {
  const [backendOk, setBackendOk] = useState(false);
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchHealth()
      .then(d => setBackendOk(d.status === 'ok'))
      .catch(() => setBackendOk(false));

    // Fetch counts from Supabase directly
    async function loadCounts() {
      const tables = ['products', 'suppliers', 'forecasts', 'inventory'];
      const result: Record<string, number> = {};
      for (const t of tables) {
        const { count } = await supabase
          .from(t).select('*', { count: 'exact', head: true });
        result[t] = count ?? 0;
      }
      setCounts(result);
    }
    loadCounts();
  }, []);

  const cards = [
    { label: 'Products', value: counts.products },
    { label: 'Suppliers', value: counts.suppliers },
    { label: 'Forecast Rows', value: counts.forecasts },
    { label: 'Inventory Records', value: counts.inventory },
    { label: 'Backend API', value: backendOk ? 'Connected' : 'Offline' },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-5 gap-4">
        {cards.map(c => (
          <div key={c.label} className="bg-white rounded-lg shadow p-6">
            <h2 className="text-sm text-gray-500">{c.label}</h2>
            <p className="text-2xl font-bold mt-2">
              {c.value ?? '—'}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
