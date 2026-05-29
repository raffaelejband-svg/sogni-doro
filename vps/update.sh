#!/bin/bash
# =============================================================================
# update.sh — Aggiornamento rapido di Sogni d'Oro dal repository GitHub
#
# USO:
#   sudo bash update.sh
#   (oppure da cron o webhook CI/CD)
#
# PREREQUISITI:
#   - Il file .env deve esistere in APP_DIR e contenere APP_DIR correttamente
#   - L'utente che esegue lo script deve avere accesso a systemctl
#   - Git deve essere configurato per leggere il repository (SSH key o token)
# =============================================================================

set -euo pipefail  # Interrompi su errore, variabili non definite, errori in pipe

# --------------------------------------------------------------------------
# Carica variabili d'ambiente
# --------------------------------------------------------------------------

# Percorso di default: sovrascrivibile con APP_DIR=/path/to/app bash update.sh
APP_DIR="${APP_DIR:-/var/www/sogni-doro}"

# Carica il file .env se esiste
if [ -f "$APP_DIR/.env" ]; then
    # shellcheck disable=SC1091
    source "$APP_DIR/.env"
fi

# --------------------------------------------------------------------------
# Colori per output leggibile
# --------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_info() { echo -e "${YELLOW}[..] $1${NC}"; }
log_err()  { echo -e "${RED}[ERR]${NC} $1" >&2; }

# --------------------------------------------------------------------------
# Funzione di cleanup in caso di errore
# --------------------------------------------------------------------------
on_error() {
    log_err "Aggiornamento fallito alla riga $1. Il servizio NON e' stato riavviato."
    log_err "Controlla i log con: journalctl -u sogni-doro -n 50"
    exit 1
}
trap 'on_error $LINENO' ERR

# --------------------------------------------------------------------------
# 1. Spostati nella directory dell'app
# --------------------------------------------------------------------------
log_info "Directory app: $APP_DIR"
cd "$APP_DIR" || { log_err "Directory $APP_DIR non trovata"; exit 1; }

# --------------------------------------------------------------------------
# 2. Pull dal repository GitHub
# --------------------------------------------------------------------------
log_info "Recupero aggiornamenti da GitHub (branch main)..."
git pull origin main
log_ok "Codice aggiornato"

# --------------------------------------------------------------------------
# 3. Installa/aggiorna dipendenze Python
# --------------------------------------------------------------------------
log_info "Aggiornamento dipendenze Python..."

# Usa il virtualenv se presente, altrimenti pip di sistema
if [ -f "$APP_DIR/venv/bin/pip" ]; then
    "$APP_DIR/venv/bin/pip" install -r requirements.txt --quiet
else
    pip install -r requirements.txt --quiet
fi
log_ok "Dipendenze aggiornate"

# --------------------------------------------------------------------------
# 4. Riavvia il servizio systemd
# --------------------------------------------------------------------------
log_info "Riavvio del servizio sogni-doro..."
systemctl restart sogni-doro

# Attendi qualche secondo e verifica che il servizio sia attivo
sleep 3
if systemctl is-active --quiet sogni-doro; then
    log_ok "Servizio riavviato correttamente"
else
    log_err "Il servizio non risulta attivo dopo il riavvio"
    log_err "Log recenti:"
    journalctl -u sogni-doro -n 20 --no-pager
    exit 1
fi

# --------------------------------------------------------------------------
# 5. Report finale
# --------------------------------------------------------------------------
echo ""
echo -e "${GREEN}✓ Sogni d'Oro aggiornato e riavviato${NC}"
echo "  Versione: $(git log -1 --format='%h — %s (%ci)')"
echo "  Stato:    $(systemctl is-active sogni-doro)"
echo "  Log:      journalctl -u sogni-doro -f"
