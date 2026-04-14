#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${BLUE}[KAZI]${NC} $1"; }
ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERR]${NC} $1"; exit 1; }

echo -e "${BLUE}"
echo "  ██╗  ██╗ █████╗ ███████╗██╗"
echo "  ██║ ██╔╝██╔══██╗╚══███╔╝██║"
echo "  █████╔╝ ███████║  ███╔╝ ██║"
echo "  ██╔═██╗ ██╔══██║ ███╔╝  ██║"
echo "  ██║  ██╗██║  ██║███████╗██║"
echo "  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝"
echo -e "${NC}"
echo "  🎯 Kazi Hunter — Installation automatique"
echo "─────────────────────────────────────────────"

# ── 1. Système ────────────────────────────────
log "Mise à jour du système..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    curl wget git \
    python3 python3-pip python3-venv \
    python-is-python3 \
    sqlite3 \
    ca-certificates gnupg lsb-release
ok "Paquets système installés"

# ── 2. Docker ─────────────────────────────────
log "Installation de Docker..."
if command -v docker &> /dev/null; then
    ok "Docker déjà installé"
else
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    newgrp docker
    ok "Docker installé"
fi
ok "Docker Compose OK"

# ── 3. Ollama + Mistral ───────────────────────
log "Installation d'Ollama..."
if command -v ollama &> /dev/null; then
    ok "Ollama déjà installé"
else
    curl -fsSL https://ollama.com/install.sh | sh
    ok "Ollama installé"
fi

sudo systemctl enable ollama
sudo systemctl start ollama
sleep 3

log "Téléchargement de Mistral 7B (~4GB)..."
ollama pull mistral
ok "Mistral 7B prêt"

# ── 4. Dossiers ───────────────────────────────
log "Création des dossiers..."
mkdir -p ~/kazi-data
ok "Dossiers créés"

# ── 5. Configuration ──────────────────────────
KAZI_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "$KAZI_DIR/.env" ]; then
    cp "$KAZI_DIR/.env.example" "$KAZI_DIR/.env"
    sed -i "s|/home/TON_USER|/home/$USER|g" "$KAZI_DIR/.env"
    warn "Configure tes mots-clés : nano $KAZI_DIR/.env"
else
    ok ".env déjà configuré"
fi

# ── 6. Build Docker ───────────────────────────
log "Build des images Docker..."
cd "$KAZI_DIR"
docker build -t kazi-scraper ./scraper
docker compose build dashboard
ok "Images Docker buildées"

# ── 7. Lance le dashboard ─────────────────────
log "Démarrage du dashboard..."
docker compose up -d dashboard
ok "Dashboard démarré"

# ── 8. Premier scraping ───────────────────────
log "Premier scraping (~5-10 min)..."
docker run --rm \
    --network host \
    -e OLLAMA_HOST=http://localhost:11434 \
    -e DB_PATH=/kazi-data/kazi.db \
    -v ~/kazi-data:/kazi-data \
    kazi-scraper python main.py
ok "Premier scraping terminé !"

# ── Résumé ────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Kazi Hunter installé avec succès !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  📊 Dashboard  : http://localhost:8501"
echo "  🗄️  Base DB    : ~/kazi-data/kazi.db"
echo "  ⚙️  Config     : $KAZI_DIR/.env"
echo ""
echo "  👉 Personnalise tes mots-clés :"
echo "     nano $KAZI_DIR/.env"
echo ""
