"""Simple CSV-based fallback data store for frutapublica.

This provides a minimal API similar to what code using the database might
expect: listing observations, getting by id, and searching by flora name.
It loads `data/flora_data.csv` by default and caches rows in memory.
"""
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import json


class FallbackStore:
    def __init__(self, csv_path: Optional[Path] = None, cache: bool = True):
        if csv_path is None:
            csv_path = Path(__file__).parent.parent / "data" / "flora_data.csv"

        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Fallback CSV not found: {self.csv_path}")

        # Read CSV using pandas to get convenient parsing for datetime columns
        # Keep default_na=False to avoid turning empty strings into NaN when possible
        self.df = pd.read_csv(self.csv_path, parse_dates=["datetime"], keep_default_na=False)

        # Normalize column names to simple keys we expect in the codebase
        # The source CSV has: datetime,address,lat,lon,description,id,flora_name,username
        # We'll ensure those keys exist (lower-cased) and produce a list of dicts
        self.df.columns = [str(c).strip() for c in self.df.columns]

        rows = []
        for r in self.df.to_dict(orient="records"):
            # Convert id to int when possible
            try:
                r_id = int(r.get("id") if r.get("id") != "" else None)
            except Exception:
                r_id = None
            # Parse lat/lon to floats
            def to_float(v):
                try:
                    if v == "":
                        return None
                    return float(v)
                except Exception:
                    return None

            row = {
                "id": r_id,
                "datetime": r.get("datetime"),
                "address": r.get("address") or None,
                "lat": to_float(r.get("lat")),
                "lon": to_float(r.get("lon")),
                "description": r.get("description") or None,
                "flora_name": (r.get("flora_name") or r.get("flora inferida") or None),
                "username": r.get("username") or r.get("usuario") or None,
                # keep original raw row if callers want additional fields
                "_raw": r,
            }
            rows.append(row)

        self._rows: List[Dict] = rows
        self._cache_enabled = bool(cache)

    def all(self) -> List[Dict]:
        """Return all observations as a list of dicts."""
        return list(self._rows)

    def get(self, obs_id: int) -> Optional[Dict]:
        """Return a single observation by its numeric id, or None if not found."""
        if obs_id is None:
            return None
        for r in self._rows:
            if r.get("id") == obs_id:
                return r
        return None

    def filter_by_flora(self, name: str) -> List[Dict]:
        """Case-insensitive substring match on `flora_name`."""
        if not name:
            return []
        needle = name.strip().lower()
        return [r for r in self._rows if r.get("flora_name") and needle in r.get("flora_name").lower()]

    def sample(self, n: int = 5) -> List[Dict]:
        """Return `n` sample rows (first n)."""
        return self._rows[:n]

    def to_json(self, out_path: Optional[Path] = None) -> Path:
        """Dump all observations to a JSON file. Returns path to written file."""
        if out_path is None:
            out_path = Path.cwd() / "flora_fallback.json"
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(self._rows, fh, default=str, ensure_ascii=False, indent=2)
        return out_path


def _quick_demo():
    store = FallbackStore()
    print(f"Loaded {len(store.all())} observations from {store.csv_path}")
    print("Example sample:")
    for r in store.sample(3):
        print(r.get("id"), r.get("flora_name"), r.get("username"))


if __name__ == "__main__":
    _quick_demo()
