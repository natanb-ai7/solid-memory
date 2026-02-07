import DealsTable from "../components/DealsTable";
import DetailDrawer from "../components/DetailDrawer";

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

async function fetchDeals() {
  const base = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
  try {
    const response = await fetch(`${base}/listings`, { cache: "no-store" });
    if (!response.ok) {
      return fallbackDeals;
    }
    return response.json();
  } catch {
    return fallbackDeals;
  }
}

export default async function HomePage() {
  const deals = await fetchDeals();

  return (
    <main className="min-h-screen px-8 py-10">
      <header className="mb-8 space-y-3">
        <h1 className="text-3xl font-bold">i7 Loaner Deal Scanner</h1>
        <p className="text-slate-300">
          Scanning Southeast dealers for BMW i7 loaners with top negotiation leverage.
        </p>
        <div className="flex flex-wrap gap-3 text-xs text-slate-400">
          <span className="rounded-full border border-slate-700 px-3 py-1">Loaner only: ON</span>
          <span className="rounded-full border border-slate-700 px-3 py-1">Region: Southeast</span>
          <span className="rounded-full border border-slate-700 px-3 py-1">Updated just now</span>
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
