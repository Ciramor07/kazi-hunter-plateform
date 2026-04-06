import os, time, random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from loguru import logger
from fake_useragent import UserAgent

def scrape_wttj(keywords: list, location: str) -> list:
    ua = UserAgent()
    query = "%20".join(keywords[:3])
    url = f"https://www.welcometothejungle.com/fr/jobs?query={query}&aroundQuery={location}&date=7"
    offers = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=os.getenv("HEADLESS", "true") == "true",
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent=ua.random,
            viewport={"width": 1280, "height": 800},
            locale="fr-FR"
        )
        page = context.new_page()

        try:
            logger.info(f"🌴 WTTJ : {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 5))

            try:
                page.click("button[data-testid*='cookie'], button[id*='accept']", timeout=3000)
                time.sleep(1)
            except:
                pass

            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(random.uniform(2, 3))
            page.wait_for_selector("[data-testid='job-list-item'], li[data-id]", timeout=15000)

            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select("[data-testid='job-list-item']")[:20]
            logger.info(f"🌴 {len(cards)} offres trouvées sur WTTJ")

            for card in cards:
                try:
                    title    = card.select_one("h4, h3, [class*='title']")
                    company  = card.select_one("[class*='company'], [class*='organization']")
                    loc      = card.select_one("[class*='location'], [class*='place']")
                    contract = card.select_one("[class*='contract'], [class*='type']")
                    link     = card.select_one("a[href*='/jobs/']")

                    offer = {
                        "title"      : title.get_text(strip=True) if title else "N/A",
                        "company"    : company.get_text(strip=True) if company else "N/A",
                        "location"   : loc.get_text(strip=True) if loc else location,
                        "salary"     : "N/C",
                        "contract"   : contract.get_text(strip=True) if contract else "N/C",
                        "description": "",
                        "url"        : "https://www.welcometothejungle.com" + link["href"] if link else "",
                        "platform"   : "wttj",
                    }
                    offers.append(offer)

                except Exception as e:
                    logger.warning(f"Erreur parsing WTTJ : {e}")
                    continue

        except Exception as e:
            logger.error(f"Erreur WTTJ : {e}")
        finally:
            browser.close()

    logger.success(f"✅ WTTJ : {len(offers)} offres")
    return offers
