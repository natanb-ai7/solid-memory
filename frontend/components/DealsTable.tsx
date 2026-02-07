type Deal = {
  listing_id: string;
  dealer_name?: string | null;
  dealer_state?: string | null;
  miles?: number | null;
  msrp?: number | null;
  advertised_price?: number | null;
  dealer_vdp_url: string;
  score: {
    score: number;
    discount_percent: number;
  };
};

const formatCurrency = (value?: number | null) => {
  if (!value) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
};

export default function DealsTable({ deals }: { deals: Deal[] }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60">
      <div className="px-6 py-4">
        <h2 className="text-xl font-semibold">Top 25 Negotiation Setups</h2>
        <p className="text-sm text-slate-400">
          Sorted by value score, discount %, and loaner mileage.
        </p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-900 text-slate-300">
            <tr>
              <th className="px-4 py-3 text-left">Score</th>
              <th className="px-4 py-3 text-left">Discount %</th>
              <th className="px-4 py-3 text-left">Miles</th>
              <th className="px-4 py-3 text-left">MSRP</th>
              <th className="px-4 py-3 text-left">Price</th>
              <th className="px-4 py-3 text-left">State</th>
              <th className="px-4 py-3 text-left">Dealer</th>
              <th className="px-4 py-3 text-left">Link</th>
            </tr>
          </thead>
          <tbody>
            {deals.map((deal) => (
              <tr key={deal.listing_id} className="border-t border-slate-800">
                <td className="px-4 py-3 font-semibold text-emerald-300">
                  {deal.score.score.toFixed(2)}
                </td>
                <td className="px-4 py-3 text-emerald-200">
                  {deal.score.discount_percent.toFixed(1)}%
                </td>
                <td className="px-4 py-3">{deal.miles ?? "—"}</td>
                <td className="px-4 py-3">{formatCurrency(deal.msrp)}</td>
                <td className="px-4 py-3">{formatCurrency(deal.advertised_price)}</td>
                <td className="px-4 py-3">{deal.dealer_state ?? "—"}</td>
                <td className="px-4 py-3">{deal.dealer_name ?? "Unknown"}</td>
                <td className="px-4 py-3">
                  <a
                    href={deal.dealer_vdp_url}
                    className="rounded bg-emerald-500 px-3 py-1 text-xs font-semibold text-slate-900"
                  >
                    Open Dealer Page
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
