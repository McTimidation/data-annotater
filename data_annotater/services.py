from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .models import RetailRow


@dataclass
class IngestStats:
    created: int = 0
    skipped: int = 0
    invalid: int = 0
    errors: int = 0
    error_samples: Optional[List[str]] = None


def ingest_csv(uploaded_file) -> Dict[str, Any]:
    stats = IngestStats(error_samples=[])

    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except Exception as e:
        stats.errors += 1
        stats.error_samples.append(f"Failed to read/decode file: {e}")
        return _stats_to_dict(stats)

    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        try:
            merchant = (row.get("merchant") or "").strip()
            sku = (row.get("sku") or "").strip()
            country = (row.get("productcountry") or "").strip()

            if not merchant or not sku or not country:
                stats.invalid += 1
                continue

            if RetailRow.objects.filter(
                merchant=merchant,
                sku=sku,
                country=country,
            ).exists():
                stats.skipped += 1
                continue

            RetailRow.objects.create(
                merchant=merchant,
                sku=sku,
                country=country,
            )
            stats.created += 1
        except Exception as e:
            stats.errors += 1
            if stats.error_samples is not None and len(stats.error_samples) < 10:
                stats.error_samples.append(f"Row error: {e}")

    return _stats_to_dict(stats)


def _stats_to_dict(stats: IngestStats) -> Dict[str, Any]:
    return {
        "created": stats.created,
        "skipped": stats.skipped,
        "invalid": stats.invalid,
        "errors": stats.errors,
        "error_samples": stats.error_samples or [],
    }
