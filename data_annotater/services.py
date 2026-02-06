from __future__ import annotations

import csv
import io

from .models import RetailRow

def ingest_csv(uploaded_file) -> dict[str, int]:
    created = skipped = invalid = errors = 0

    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except Exception:
        return {"created": 0, "skipped": 0, "invalid": 0, "errors": 1}

    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        try:
            merchant = (row.get("merchant") or "").strip()
            sku = (row.get("sku") or "").strip()
            country = (row.get("productcountry") or "").strip()

            if not merchant or not sku or not country:
                invalid += 1
                continue

            if RetailRow.objects.filter(
                merchant=merchant,
                sku=sku,
                country=country,
            ).exists():
                skipped += 1
                continue

            RetailRow.objects.create(
                merchant=merchant,
                sku=sku,
                country=country,
            )
            created += 1

        except Exception:
            errors += 1

    return {
        "created": created,
        "skipped": skipped,
        "invalid": invalid,
        "errors": errors,
    }
