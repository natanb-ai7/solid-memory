"use client";

import { useEffect, useMemo, useState } from "react";
import DealsTable from "./DealsTable";
import DetailDrawer from "./DetailDrawer";

const fallbackDeals = [
  {
    listing_id: "seed-1",
    dealer_name: "Atlanta BMW",
    dealer_state: "GA",
    miles: 4200,
    msrp: 124995,
    advertised_price: 109995,
    dealer_vdp_url: "https://dealer.example.com/i7",
    score: { score: 0.82, discount_percent: 12.0 },
  },
];

const modelOptions = [
  { label: "BMW i7", value: "BMW i7" },
  { label: "BMW i5", value: "BMW i5" },
  { label: "BMW i4", value: "BMW i4" },
  { label: "BMW iX", value: "BMW iX" },
  { label: "BMW iX1", value: "BMW iX1" },
  { label: "BMW iX2", value: "BMW iX2" },
];

export default function DashboardClient() {
  const [model, setModel] = useState("BMW i7");
  const [deals, setDeals] = useState(fallbackDeals);
  const [loading, setLoading] = useState(false);

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000",
    []
  );

  useEffect(() => {
    let ignore = false;
    const fetchDeals = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${apiBase}/listings?model=${encodeURIComponent(model)}`, {
          cache: "no-store",
        });
        if (!response.ok) {
          throw new Error("Bad response");
        }
        const data = await response.json();
        if (!ignore) {
          setDeals(data.length ? data : fallbackDeals);
        }
      } catch {
        if (!ignore) {
          setDeals(fallbackDeals);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchDeals();

    return () => {
      ignore = true;
    };
  }, [apiBase, model]);

  return (
    <main className="min-h-screen px-8 py-10">
      <header className="mb-8 space-y-3">
        <h1 className="text-3xl font-bold">i7 Loaner Deal Scanner</h1>
        <p className="text-slate-300">
          Scanning Southeast dealers for BMW EV loaners with top negotiation leverage.
        </p>
        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <span className="rounded-full border border-slate-700 px-3 py-1">Loaner only: ON</span>
          <span className="rounded-full border border-slate-700 px-3 py-1">Region: Southeast</span>
          <span className="rounded-full border border-slate-700 px-3 py-1">Updated just now</span>
          <label className="flex items-center gap-2 text-sm text-slate-200">
            Scan model:
            <select
              value={model}
              onChange={(event) => setModel(event.target.value)}
              className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
            >
              {modelOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          {loading && <span className="text-emerald-300">Loading deals…</span>}
        </div>
      </header>

      <DealsTable deals={deals.slice(0, 25)} />

      <section className="mt-10 grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold">Alert thresholds</h3>
          <p className="mt-2 text-sm text-slate-400">
            Configure Discount % &gt; 20%, Miles &lt; 8k, or Price &lt; $95k to get emails.
          </p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold">Negotiation playbook</h3>
          <p className="mt-2 text-sm text-slate-400">
            Each deal includes target pricing, incentive stacking, and lease structure guidance.
          </p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold">Comps view</h3>
          <p className="mt-2 text-sm text-slate-400">
            Compare each deal to 5 regional comps by trim and MSRP bucket.
          </p>
        </div>
      </section>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <DetailDrawer
          detail={{
            dealer_name: deals[0]?.dealer_name,
            dealer_state: deals[0]?.dealer_state,
            last_scraped_at: new Date().toISOString(),
            confidence_score: 0.78,
            raw_snippet: "Loaner, 4,200 miles, MSRP $124,995, Price $109,995",
          }}
        />
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold">Negotiation playbook</h3>
          <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-400">
            <li>Target discount: 14-16% with stacked incentives.</li>
            <li>Ask for MF/residual confirmation and fee disclosure.</li>
            <li>Structure $0 DAS with MSDs where allowed.</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
