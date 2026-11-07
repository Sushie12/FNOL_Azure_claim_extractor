"""
Explore Azure Document Intelligence KEY-VALUE PAIR extraction on pages 1-2.

    pip install azure-ai-documentintelligence python-dotenv
    python kv_explore.py pdf10.pdf

* One Azure call = 2 pages of your free (F0) quota.
* The pairs are cached in .kv_cache/, so re-running on the same file costs 0 pages.
* Everything is also saved to kv_output.json so you can inspect it.
"""
import os
import io
import sys
import json
import hashlib

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()
CACHE_DIR = ".kv_cache"


def analyze_pairs(path):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "rb") as f:
        data = f.read()
    cache = os.path.join(CACHE_DIR, hashlib.sha1(data).hexdigest() + ".json")
    if os.path.exists(cache):
        print(f"[cache] {cache} (0 pages used)\n")
        with open(cache) as f:
            return json.load(f)

    client = DocumentIntelligenceClient(
        os.getenv("azure_endpoint"), AzureKeyCredential(os.getenv("azure_key"))
    )
    poller = client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=io.BytesIO(data),
        features=["keyValuePairs"],   # <- the only add-on used
        pages="1-2",                  # free tier analyses at most 2 pages anyway
    )
    result = poller.result()

    pairs = []
    for kv in (result.key_value_pairs or []):
        page = None
        if kv.key and kv.key.bounding_regions:
            page = kv.key.bounding_regions[0].page_number
        pairs.append({
            "page": page,
            "key": kv.key.content.strip() if kv.key else None,
            "value": kv.value.content.strip() if kv.value and kv.value.content else None,
            "confidence": round(kv.confidence, 2) if kv.confidence is not None else None,
        })

    marks = {}
    for p in (result.pages or []):
        marks[p.page_number] = [str(getattr(m.state, "value", m.state))
                                for m in (p.selection_marks or [])]

    out = {"pairs": pairs, "selection_marks": marks}
    with open(cache, "w") as f:
        json.dump(out, f)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python kv_explore.py <file.pdf>")
    out = analyze_pairs(sys.argv[1])
    pairs = out["pairs"]

    print(f"{len(pairs)} key-value pairs found\n")
    print(f"{'pg':<3} {'conf':<5} {'KEY':<45} VALUE")
    print("-" * 100)
    for p in pairs:
        print(f"{p['page']!s:<3} {p['confidence']!s:<5} {(p['key'] or '')[:44]:<45} {p['value']}")

    empty = [p for p in pairs if not p["value"]]
    print(f"\n{len(empty)} pairs have NO value (label found, nothing paired to it)")
    for pg, st in out["selection_marks"].items():
        print(f"page {pg}: {len(st)} checkboxes detected, {st.count('selected')} ticked")

    with open("kv_output.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("\nsaved -> kv_output.json")