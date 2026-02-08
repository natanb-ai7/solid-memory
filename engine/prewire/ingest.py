from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from prewire.schemas import (
    PortfolioPosition,
    FundingTerm,
    HedgePosition,
    MarketIndicator,
    MATarget,
    SourcePointer,
)

REQUIRED_COLUMNS = {
    "portfolio_positions": [
        "asof_date",
        "cusip",
        "deal_name",
        "tranche",
        "rating",
        "original_balance",
        "current_balance",
        "price",
        "spread",
        "wal",
        "property_type_mix",
        "top_msas",
        "servicer",
        "special_servicing_flag",
        "watchlist_flag",
        "ara_flag",
        "maturity_bucket",
    ],
    "funding_terms": [
        "counterparty",
        "asof_date",
        "haircut",
        "spread",
        "advance_rate",
        "margin_call_terms",
        "eligible_assets_rules",
    ],
    "hedge_book": [
        "instrument",
        "notional",
        "dv01",
        "cs01_proxy",
        "reference_index",
        "entry_level",
        "current_level",
    ],
    "market_indicators": [
        "indicator",
        "asof_date",
        "value",
        "unit",
    ],
    "ma_targets": [
        "company",
        "segment",
        "last_touch_date",
        "signal_score_components",
        "notes",
        "owner",
        "next_action",
        "status",
    ],
}


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported file type: {path.suffix}")


def validate_schema(path: Path, required_columns: List[str]) -> List[str]:
    df = _read_table(path)
    missing = [col for col in required_columns if col not in df.columns]
    return missing


def resolve_dataset_path(base_dir: Path, name: str) -> Path:
    candidates = [base_dir / f"{name}.csv", base_dir / f"{name}.xlsx", base_dir / f"{name}.xls"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Dataset {name} not found in {base_dir}")


def _source_for(path: Path, row_idx: int, column: str) -> SourcePointer:
    return SourcePointer(
        reference=f"{path.name}#row={row_idx + 2},col={column}",
        timestamp=datetime.utcnow(),
    )


def ingest_portfolio(path: Path) -> List[PortfolioPosition]:
    df = _read_table(path)
    records: List[PortfolioPosition] = []
    for idx, row in df.iterrows():
        sources = {col: _source_for(path, idx, col) for col in df.columns}
        records.append(
            PortfolioPosition(
                asof_date=row["asof_date"],
                cusip=row["cusip"],
                deal_name=row["deal_name"],
                tranche=row["tranche"],
                rating=row["rating"],
                original_balance=row["original_balance"],
                current_balance=row["current_balance"],
                price=row["price"],
                spread=row["spread"],
                wal=row["wal"],
                property_type_mix=row["property_type_mix"],
                top_msas=row["top_msas"],
                servicer=row["servicer"],
                special_servicing_flag=bool(row["special_servicing_flag"]),
                watchlist_flag=bool(row["watchlist_flag"]),
                ara_flag=bool(row["ara_flag"]),
                maturity_bucket=row["maturity_bucket"],
                comments=row.get("comments", None),
                sources=sources,
            )
        )
    return records


def ingest_funding(path: Path) -> List[FundingTerm]:
    df = _read_table(path)
    records: List[FundingTerm] = []
    for idx, row in df.iterrows():
        sources = {col: _source_for(path, idx, col) for col in df.columns}
        records.append(
            FundingTerm(
                counterparty=row["counterparty"],
                asof_date=row["asof_date"],
                haircut=row["haircut"],
                spread=row["spread"],
                advance_rate=row["advance_rate"],
                margin_call_terms=row["margin_call_terms"],
                eligible_assets_rules=row["eligible_assets_rules"],
                sources=sources,
            )
        )
    return records


def ingest_hedges(path: Path) -> List[HedgePosition]:
    df = _read_table(path)
    records: List[HedgePosition] = []
    for idx, row in df.iterrows():
        sources = {col: _source_for(path, idx, col) for col in df.columns}
        records.append(
            HedgePosition(
                instrument=row["instrument"],
                notional=row["notional"],
                dv01=row["dv01"],
                cs01_proxy=row["cs01_proxy"],
                reference_index=row["reference_index"],
                entry_level=row["entry_level"],
                current_level=row["current_level"],
                sources=sources,
            )
        )
    return records


def ingest_market(path: Path) -> List[MarketIndicator]:
    df = _read_table(path)
    records: List[MarketIndicator] = []
    for idx, row in df.iterrows():
        sources = {col: _source_for(path, idx, col) for col in df.columns}
        records.append(
            MarketIndicator(
                indicator=row["indicator"],
                asof_date=row["asof_date"],
                value=row["value"],
                unit=row["unit"],
                sources=sources,
            )
        )
    return records


def ingest_ma_targets(path: Path) -> List[MATarget]:
    df = _read_table(path)
    records: List[MATarget] = []
    for idx, row in df.iterrows():
        sources = {col: _source_for(path, idx, col) for col in df.columns}
        records.append(
            MATarget(
                company=row["company"],
                segment=row["segment"],
                last_touch_date=row["last_touch_date"],
                signal_score_components=row["signal_score_components"],
                notes=row["notes"],
                owner=row["owner"],
                next_action=row["next_action"],
                status=row["status"],
                sources=sources,
            )
        )
    return records
