# annotater/services.py
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from django.db import IntegrityError

from .models import RetailRow


@dataclass
class IngestStats:
    created: int = 0
    skipped: int = 0
    invalid: int = 0
    errors: int = 0
    error_samples: Optional[List[str]] = None


def ingest_csv(uploaded_file) -> Dict[str, Any]:
    """
    Parse the uploaded CSV and insert RetailRow records.
    - Skips duplicates via (merchant, sku, country) uniqueness
    - Does NOT overwrite retailer/segment if a record already exists
    Returns a stats dict safe to display in UI.
    """
    stats = IngestStats(error_samples=[])

    # 1) Read & decode
    try:
        raw = uploaded_file.read()
        text = raw.decode("utf-8-sig")  # handles BOM
    except Exception as e:
        stats.errors += 1
        stats.error_samples.append(f"Failed to read/decode file: {e}")
        return _stats_to_dict(stats)

    # 2) Parse CSV
    f = io.StringIO(text)
    reader = csv.DictReader(f)

    # Optional: defensive check for expected headers
    expected = {"merchant", "sku", "country"}
    if not reader.fieldnames or not expected.issubset(set(h.strip() for h in reader.fieldnames)):
        stats.errors += 1
        stats.error_samples.append(f"Missing required headers: {expected}")
        return _stats_to_dict(stats)

    for row in reader:
        try:
            merchant = (row.get("merchant") or "").strip()
            sku = (row.get("sku") or "").strip()
            country = (row.get("country") or "").strip().upper()

            # 3) Basic validation
            if not merchant or not sku or not country:
                stats.invalid += 1
                continue

            # 4) Insert-or-skip. Do NOT overwrite annotations.
            obj, created = RetailRow.objects.get_or_create(
                merchant=merchant,
                sku=sku,
                country=country,
                defaults={},
            )

            if created:
                stats.created += 1
            else:
                stats.skipped += 1

        except IntegrityError:
            stats.skipped += 1
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
