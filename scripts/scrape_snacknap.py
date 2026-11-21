"""Snack Nap 極巨戰清單 -> data/maxbattles.json（由 GitHub Actions 定時執行）"""
import json, re, sys, datetime, pathlib
import requests
from bs4 import BeautifulSoup

URL = "https://www.snacknap.com/max-battles"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "maxbattles.json"


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for tier_card in soup.select(".to-card"):
        tier = tier_card.get("data-tier", "")
        m = re.search(r"\d+", tier)
        if not m:
            continue
        tier_num = int(m.group())
        for pokemon in tier_card.select(".snk-tile"):
            title = pokemon.select_one(".pkmn-title")
            if not title:
                continue
            name = title.get_text(" ", strip=True)
            cp_el = pokemon.select_one(".pkmn-cp")
            cp = re.findall(r"\d+", cp_el.get_text(" ", strip=True)) if cp_el else []
            items.append({
                "tier": tier_num,
                "name": name,
                "cp_min": int(cp[0]) if len(cp) >= 1 else None,
                "cp_max": int(cp[1]) if len(cp) >= 2 else None,
            })
    return items


def main():
    html = requests.get(URL, timeout=30, headers={"User-Agent": "PokeLog personal tracker (GitHub Actions)"}).text
    items = parse(html)
    if not items:
        print("沒有解析到任何 Boss，保留舊檔")
        return 1
    OUT.parent.mkdir(exist_ok=True)
    if OUT.exists():
        try:
            if json.loads(OUT.read_text(encoding="utf-8")).get("items") == items:
                print("清單沒變，不更新")
                return 0
        except Exception:
            pass
    OUT.write_text(json.dumps({"source": URL, "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} 筆")
    return 0


if __name__ == "__main__":
    sys.exit(main())
