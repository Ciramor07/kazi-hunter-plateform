import os, time, random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from loguru import logger
from fake_useragent import UserAgent

def scrape_linkedin(keywords: list, location: str) -> list:
    ua = UserAgent()
    query = "%20".join(keywords[:3])
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&sortBy=DD&f_TPR=r604800"
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
            logger.info(f"🔗 LinkedIn : {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 6))

            try:
                page.click("button[action-type='ACCEPT']", timeout=3000)
                time.sleep(1)
            except:
                pass

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(random.uniform(1, 2))

            page.wait_for_selector(".job-search-card, .base-card", timeout=15000)
            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select(".job-search-card, .base-card")[:20]
            logger.info(f"🔗 {len(cards)} offres trouvées sur LinkedIn")

            for card in cards:
                try:
                    title   = card.select_one("h3.base-search-card__title")
                    company = card.select_one("h4.base-search-card__subtitle")
                    loc     = card.select_one("span.job-search-card__location")
                    link    = card.select_one("a.base-card__full-link")

                    offer = {
                        "title"      : title.get_text(strip=True) if title else "N/A",
                        "company"    : company.get_text(strip=True) if company else "N/A",
                        "location"   : loc.get_text(strip=True) if loc else location,
                        "salary"     : "N/C",
                        "contract"   : "N/C",
                        "description": "",
                        "url"        : link["href"] if link else "",
                        "platform"   : "linkedin",
                    }
                    offers.append(offer)
                    time.sleep(random.uniform(1, 2))

                except Exception as e:
                    logger.warning(f"Erreur parsing LinkedIn : {e}")
                    continue

        except Exception as e:
            logger.error(f"Erreur LinkedIn : {e}")
        finally:
            browser.close()

    logger.success(f"✅ LinkedIn : {len(offers)} offres")
    return offers
