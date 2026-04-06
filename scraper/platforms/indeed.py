import os, time, random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from loguru import logger
from fake_useragent import UserAgent

def scrape_indeed(keywords: list, location: str) -> list:
    ua = UserAgent()
    query = "+".join(keywords[:3])
    url = f"https://fr.indeed.com/jobs?q={query}&l={location}&sort=date&fromage=7"
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
            logger.info(f"🔍 Indeed : {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(random.uniform(2, 4))

            try:
                page.click("button[id*='cookie'], button[id*='consent']", timeout=3000)
            except:
                pass

            page.wait_for_selector(".job_seen_beacon, .jobsearch-ResultsList", timeout=15000)
            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select(".job_seen_beacon")[:20]
            logger.info(f"📌 {len(cards)} offres trouvées sur Indeed")

            for card in cards:
                try:
                    title   = card.select_one("h2.jobTitle span")
                    company = card.select_one("[data-testid='company-name']")
                    loc     = card.select_one("[data-testid='text-location']")
                    salary  = card.select_one("[class*='salary']")
                    link    = card.select_one("h2.jobTitle a")

                    offer = {
                        "title"      : title.get_text(strip=True) if title else "N/A",
                        "company"    : company.get_text(strip=True) if company else "N/A",
                        "location"   : loc.get_text(strip=True) if loc else location,
                        "salary"     : salary.get_text(strip=True) if salary else "N/C",
                        "contract"   : "N/C",
                        "description": "",
                        "url"        : "https://fr.indeed.com" + link["href"] if link else "",
                        "platform"   : "indeed",
                    }
                    offers.append(offer)
                    time.sleep(random.uniform(0.5, 1.5))

                except Exception as e:
                    logger.warning(f"Erreur parsing Indeed : {e}")
                    continue

        except Exception as e:
            logger.error(f"Erreur Indeed : {e}")
        finally:
            browser.close()

    logger.success(f"✅ Indeed : {len(offers)} offres")
    return offers
