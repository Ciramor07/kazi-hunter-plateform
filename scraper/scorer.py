import os, requests, json, time
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

PROFILE = """
Candidat : Ricky
Poste recherché : DevOps Engineer Junior
Expérience : débutant à 2 ans
Compétences : Docker, Kubernetes, Terraform, CI/CD, GitHub Actions, Linux, Python, Bash, AWS, Azure
Contrat : CDI
Localisation : France (remote ou hybride accepté)
Salaire cible : 35 000€ - 55 000€
"""

PROMPT_TEMPLATE = """
Tu es un assistant de recherche d'emploi. Évalue cette offre d'emploi pour le candidat suivant :

PROFIL DU CANDIDAT :
{profile}

OFFRE D'EMPLOI :
Titre : {title}
Entreprise : {company}
Localisation : {location}
Contrat : {contract}
Salaire : {salary}

Réponds UNIQUEMENT en JSON avec ce format exact :
{{
  "score": <nombre entre 0 et 10>,
  "raison": "<explication courte en français>"
}}

Critères de scoring :
- 8-10 : Parfait pour un junior, compétences alignées, bon salaire
- 5-7  : Intéressant mais quelques écarts
- 3-4  : Possible mais difficile
- 0-2  : Inadapté (trop senior, mauvais salaire, hors sujet)
"""

def is_offer_expired(url: str) -> bool:
    if not url:
        return False
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        expired_signals = [
            "cette offre a expiré",
            "offre expirée",
            "job expired",
            "no longer accepting",
            "plus disponible",
            "offre pourvue"
        ]
        content = response.text.lower()
        return any(signal in content for signal in expired_signals)
    except:
        return False

def score_offer(offer: dict) -> tuple[float, str]:
    prompt = PROMPT_TEMPLATE.format(
        profile  = PROFILE,
        title    = offer.get("title", "N/A"),
        company  = offer.get("company", "N/A"),
        location = offer.get("location", "N/A"),
        contract = offer.get("contract", "N/A"),
        salary   = offer.get("salary", "N/C"),
    )

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model"  : OLLAMA_MODEL,
                "prompt" : prompt,
                "stream" : False,
            },
            timeout=300
        )
        response.raise_for_status()
        raw = response.json().get("response", "")

        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("Pas de JSON dans la réponse")

        data   = json.loads(raw[start:end])
        score  = float(data.get("score", 0))
        raison = data.get("raison", "")

        return score, raison

    except Exception as e:
        logger.warning(f"Erreur scoring : {e}")
        return 0.0, "Erreur scoring"


def score_all_offers():
    from utils.db import get_session, Offer

    session = get_session()
    offers  = session.query(Offer).filter(Offer.score == 0.0).all()

    logger.info(f"🤖 Scoring de {len(offers)} offres avec Mistral...")

    for offer in offers:
        logger.info(f"📊 Scoring : {offer.title} @ {offer.company}")

        if is_offer_expired(offer.url):
            logger.warning(f"⚠️ Offre expirée : {offer.title}")
            offer.status = "expired"
            session.commit()
            continue

        score, raison = score_offer({
            "title"   : offer.title,
            "company" : offer.company,
            "location": offer.location,
            "contract": offer.contract,
            "salary"  : offer.salary,
        })

        offer.score = score
        offer.notes = raison
        session.commit()
        logger.info(f"   → Score : {score}/10 — {raison}")

    session.close()
    logger.success(f"✅ Scoring terminé !")


if __name__ == "__main__":
    score_all_offers()
