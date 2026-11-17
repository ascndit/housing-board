import json
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Резервный HTML, имитирующий разметку каталога недвижимости (на случай 403/капчи от сайта)
FALLBACK_HTML = """
<div class="catalog">
  <article class="offer-card" data-id="101">
    <h2 class="offer-title">2-комн. квартира, 54 м²</h2>
    <div class="offer-price">42 000 ₽/мес.</div>
    <div class="offer-district">Центральный</div>
    <div class="offer-specs" data-rooms="2" data-area="54"></div>
    <p class="offer-desc">Светлая квартира после свежего ремонта. Есть вся необходимая мебель, посудомоечная машина и кондиционер. Рядом метро и парк.</p>
    <div class="offer-photos">
      <img src="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800" />
      <img src="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800" />
    </div>
  </article>

  <article class="offer-card" data-id="102">
    <h2 class="offer-title">Студия в новом ЖК, 28 м²</h2>
    <div class="offer-price">27 500 ₽/мес.</div>
    <div class="offer-district">Октябрьский</div>
    <div class="offer-specs" data-rooms="0" data-area="28"></div>
    <p class="offer-desc">Уютная студия с панорамным балконом. Закрытый двор без машин, развитая инфраструктура.</p>
    <div class="offer-photos">
      <img src="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800" />
    </div>
  </article>

  <article class="offer-card" data-id="103">
    <h2 class="offer-title">3-комн. квартира у парка, 78 м²</h2>
    <div class="offer-price">65 000 ₽/мес.</div>
    <div class="offer-district">Советский</div>
    <div class="offer-specs" data-rooms="3" data-area="78"></div>
    <p class="offer-desc">Просторная квартира для семьи. Два санузла, гардеробная, подземный паркинг включен в стоимость.</p>
    <div class="offer-photos">
      <img src="https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800" />
      <img src="https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800" />
    </div>
  </article>

  <!-- Объявление с пропущенными полями (проверка устойчивости интерфейса) -->
  <article class="offer-card" data-id="104">
    <h2 class="offer-title">1-комн. квартира, без посредников</h2>
    <div class="offer-price">31 000 ₽/мес.</div>
    <div class="offer-specs" data-rooms="1"></div>
    <div class="offer-photos"></div>
  </article>

  <article class="offer-card" data-id="105">
    <h2 class="offer-title">2-комн. квартира в тихом центре, 60 м²</h2>
    <div class="offer-price">48 000 ₽/мес.</div>
    <div class="offer-district">Центральный</div>
    <div class="offer-specs" data-rooms="2" data-area="60"></div>
    <p class="offer-desc">Кирпичный дом, высокие потолки, тихие соседи. Сдается на длительный срок.</p>
    <div class="offer-photos">
      <img src="https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=800" />
    </div>
  </article>
</div>
"""


def clean_number(text: str | None) -> int | None:
    """Извлекает целое число из строки (например, '42 000 ₽/мес.' -> 42000)."""
    if not text:
        return None
    digits = re.sub(r"\D", "", text)
    return int(digits) if digits else None


def fetch_html(url: str) -> str:
    """Загружает HTML страницы или возвращает резервный шаблон при блокировке."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()
        # Если сайт вернул страницу с капчей вместо карточек, используем резервный HTML
        if "offer-card" not in response.text:
            print("Сайт вернул защиту от ботов, используется локальный HTML-шаблон.")
            return FALLBACK_HTML
        return response.text
    except requests.RequestException as exc:
        print(f"Не удалось загрузить URL ({exc}). Используется резервный HTML.")
        return FALLBACK_HTML


def parse_listings(html: str) -> list[dict]:
    """Разбирает HTML-дерево и извлекает структурированные данные об объявлениях."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.offer-card")
    results = []

    for index, card in enumerate(cards, start=1):
        title_el = card.select_one(".offer-title")
        price_el = card.select_one(".offer-price")
        district_el = card.select_one(".offer-district")
        specs_el = card.select_one(".offer-specs")
        desc_el = card.select_one(".offer-desc")
        photo_els = card.select(".offer-photos img")

        raw_rooms = specs_el.get("data-rooms") if specs_el else None
        raw_area = specs_el.get("data-area") if specs_el else None

        listing = {
            "id": int(card.get("data-id", index)),
            "title": title_el.get_text(strip=True) if title_el else None,
            "price": clean_number(price_el.get_text()) if price_el else None,
            "district": district_el.get_text(strip=True) if district_el else None,
            "rooms": int(raw_rooms) if raw_rooms is not None and raw_rooms.isdigit() else None,
            "area": float(raw_area) if raw_area else None,
            "description": desc_el.get_text(strip=True) if desc_el else None,
            "photos": [img.get("src") for img in photo_els if img.get("src")],
        }
        results.append(listing)

    return results


def main() -> None:
    target_url = "https://www.cian.ru/snyat-kvartiru/"
    html = fetch_html(target_url)
    listings = parse_listings(html)

    output_path = Path(__file__).resolve().parent.parent / "src" / "data" / "listings.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(listings, file, ensure_ascii=False, indent=2)

    print(f"Сохранено объявлений: {len(listings)} -> {output_path}")


if __name__ == "__main__":
    main()