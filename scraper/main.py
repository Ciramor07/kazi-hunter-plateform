import os, hashlib
import time
from dotenv import load_dotenv
from loguru import logger
from utils.db import get_session, Offer
from platforms.indeed import scrape_indeed
from platforms.wttj import scrape_wttj
from platforms.linkedin import scrape_linkedin
from scorer import score_all_offers

load_dotenv()

EXCLUDE_KEYWORDS = [k.lower() for k in os.getenv("EXCLUDE_KEYWORDS", "").split(",") if k]
MAX_DAYS_OLD     = int(os.getenv("MAX_DAYS_OLD", "7"))

def is_valid_offer(offer: dict) -> bool:
    title = offer.get("title", "").lower()
    desc  = offer.get("description", "").lower()
    text  = f"{title} {desc}"

    for kw in EXCLUDE_KEYWORDS:
        if kw in text:
            logger.debug(f"❌ Exclu ('{kw}') : {offer['title']}")
            return False
    return True

def deduplicate_and_save(offers: list):
    session   = get_session()
    new_count = 0
    excluded  = 0

    for offer in offers:
        if not is_valid_offer(offer):
            excluded += 1
            continue

        unique_str  = f"{offer['title']}{offer['company']}{offer['platform']}"
        offer["id"] = hashlib.md5(unique_str.encode()).hexdigest()

        exists = session.query(Offer).filter_by(id=offer["id"]).first()
        if not exists:
            session.add(Offer(**offer))
            new_count += 1

    session.commit()
    session.close()
    logger.success(f"✅ {new_count} nouvelles offres sauvegardées")
    logger.info(f"🚫 {excluded} offres exclues par les filtres")

def main():
    keywords = os.getenv("KEYWORDS", "DevOps,Cloud,Docker").split(",")
    location = os.getenv("LOCATION", "France")

    logger.info("🚀 Démarrage Kazi Hunter")
    logger.info(f"🔍 Mots-clés : {keywords}")
    logger.info(f"📍 Localisation : {location}")
    logger.info(f"🚫 Exclusions : {EXCLUDE_KEYWORDS}")

    all_offers = []

    logger.info("📌 Scraping Indeed...")
    all_offers += scrape_indeed(keywords, location)

    logger.info("🌴 Scraping WTTJ...")
    all_offers += scrape_wttj(keywords, location)

    logger.info("🔗 Scraping LinkedIn...")
    all_offers += scrape_linkedin(keywords, location)

    logger.info(f"📦 Total brut : {len(all_offers)} offres")
    deduplicate_and_save(all_offers)

    logger.info("🤖 Lancement du scoring IA dans 10s...")
    time.sleep(10)
    import time; time.sleep(30); score_all_offers()

if __name__ == "__main__":
    main()
