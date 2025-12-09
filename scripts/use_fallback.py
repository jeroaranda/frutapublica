"""Small example showing how to use the CSV fallback store."""
from database.fallback_store import FallbackStore


def main():
    store = FallbackStore()
    print(f"Total observations: {len(store.all())}")

    # show a sample
    print("--- Sample ---")
    for r in store.sample(5):
        print(r.get("id"), "-", r.get("flora_name"), "-", r.get("username"))

    # show a filter example
    print("\n--- Filter by 'Naranja' ---")
    matches = store.filter_by_flora("Naranja")
    print(f"Found {len(matches)} observations matching 'Naranja'")


if __name__ == "__main__":
    main()
