type DealDetail = {
  dealer_name?: string | null;
  dealer_state?: string | null;
  last_scraped_at?: string;
  confidence_score?: number;
  raw_snippet?: string;
};

export default function DetailDrawer({ detail }: { detail: DealDetail }) {
  return (
    <aside className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h3 className="text-lg font-semibold">Deal detail</h3>
      <div className="mt-3 space-y-2 text-sm text-slate-300">
        <p>
          <span className="text-slate-400">Dealer:</span> {detail.dealer_name ?? "Unknown"} ({detail.dealer_state ?? "—"})
        </p>
        <p>
          <span className="text-slate-400">Last scraped:</span> {detail.last_scraped_at ?? "—"}
        </p>
        <p>
          <span className="text-slate-400">Confidence:</span> {detail.confidence_score ?? 0}
        </p>
        <p className="text-xs text-slate-500">Raw snippet: {detail.raw_snippet ?? "—"}</p>
      </div>
    </aside>
  );
}
