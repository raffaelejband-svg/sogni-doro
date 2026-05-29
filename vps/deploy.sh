#!/usr/bin/env bash
# =============================================================================
#  deploy.sh — Installazione completa di "Sogni d'Oro" su VPS Hostinger
#  Ubuntu 22.04 LTS — eseguire come root: bash deploy.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# LOG
# ---------------------------------------------------------------------------
LOG_FILE="/var/log/sognidoro_deploy.log"
# Se /var/log non è ancora scrivibile (pre-root check) usiamo /tmp
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/sognidoro_deploy.log"

exec > >(tee -a "$LOG_FILE") 2>&1

# ---------------------------------------------------------------------------
# COLORI ANSI
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

ok()   { echo -e "${GREEN}[OK]${RESET}    $*"; }
err()  { echo -e "${RED}[ERRORE]${RESET} $*" >&2; }
warn() { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
info() { echo -e "${CYAN}[INFO]${RESET}  $*"; }
step() { echo -e "\n${BOLD}${CYAN}════════════════════════════════════════${RESET}"; \
         echo -e "${BOLD}${CYAN}  $*${RESET}"; \
         echo -e "${BOLD}${CYAN}════════════════════════════════════════${RESET}"; }

# ---------------------------------------------------------------------------
# TRAP — pulizia in caso di errore
# ---------------------------------------------------------------------------
trap 'err "Deploy interrotto alla riga $LINENO. Controlla il log: $LOG_FILE"' ERR

# =============================================================================
# FASE 1 — Configurazione iniziale
# =============================================================================
step "FASE 1 — Configurazione iniziale"

# --- Header colorato ---
echo -e ""
echo -e "${BOLD}${CYAN}  ╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}  ║        ✦  SOGNI D'ORO  ✦            ║${RESET}"
echo -e "${BOLD}${CYAN}  ║   Deploy automatico su VPS Hostinger ║${RESET}"
echo -e "${BOLD}${CYAN}  ╚══════════════════════════════════════╝${RESET}"
echo -e ""

# --- Carica .env se esiste ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

# Valori di default
GITHUB_REPO="${GITHUB_REPO:-https://github.com/tuousername/sogni-doro.git}"
APP_DIR="${APP_DIR:-/var/www/sogni-doro}"
APP_USER="${APP_USER:-sognidoro}"
DOMAIN_NAME="${DOMAIN_NAME:-sogni-doro.example.com}"
EMAIL="${EMAIL:-admin@example.com}"
APP_PORT="${APP_PORT:-8000}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if [[ -f "$ENV_FILE" ]]; then
    info "Carico variabili da $ENV_FILE"
    # shellcheck disable=SC1090
    set -o allexport
    source "$ENV_FILE"
    set +o allexport
    ok "Variabili caricate da .env"
else
    warn "File .env non trovato — uso valori di default"
fi

info "Repository  : $GITHUB_REPO"
info "Directory   : $APP_DIR"
info "Utente app  : $APP_USER"
info "Dominio     : $DOMAIN_NAME"
info "Email       : $EMAIL"
info "Porta app   : $APP_PORT"

# --- Verifica root ---
if [[ "$EUID" -ne 0 ]]; then
    err "Questo script deve essere eseguito come root (sudo bash deploy.sh)"
    exit 1
fi
ok "Eseguito come root"

# --- Verifica Ubuntu 22.04 ---
if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    if [[ "${ID:-}" != "ubuntu" ]] || [[ "${VERSION_ID:-}" != "22.04" ]]; then
        warn "Sistema rilevato: ${PRETTY_NAME:-sconosciuto}"
        warn "Lo script è ottimizzato per Ubuntu 22.04 LTS. Continuo comunque..."
    else
        ok "Ubuntu 22.04 LTS rilevato"
    fi
else
    warn "Impossibile verificare la versione OS — continuo..."
fi

# =============================================================================
# FASE 2 — Installazione dipendenze
# =============================================================================
step "FASE 2 — Installazione dipendenze di sistema"

info "apt update && apt upgrade..."
apt-get update -y
apt-get upgrade -y

PACKAGES=(
    python3.11
    python3.11-venv
    python3-pip
    nginx
    git
    certbot
    python3-certbot-nginx
    ufw
    curl
    software-properties-common
)

info "Installo pacchetti: ${PACKAGES[*]}"
apt-get install -y "${PACKAGES[@]}"
ok "Tutti i pacchetti installati"

# =============================================================================
# FASE 3 — Creazione utente dedicato
# =============================================================================
step "FASE 3 — Creazione utente dedicato '$APP_USER'"

if id "$APP_USER" &>/dev/null; then
    warn "Utente '$APP_USER' già esistente — salto la creazione"
else
    useradd --system --no-create-home --shell /usr/sbin/nologin "$APP_USER"
    ok "Utente '$APP_USER' creato"
fi

# Crea directory app con permessi corretti
mkdir -p "$APP_DIR"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
chmod -R 755 "$APP_DIR"
ok "Directory $APP_DIR creata con permessi corretti"

# =============================================================================
# FASE 4 — Clone repository e setup Python
# =============================================================================
step "FASE 4 — Clone repository e setup ambiente Python"

# Clona repo
if [[ -d "$APP_DIR/.git" ]]; then
    warn "Repository già clonato in $APP_DIR — eseguo git pull"
    git -C "$APP_DIR" pull
else
    info "Clono $GITHUB_REPO in $APP_DIR ..."
    # Il clone va in una dir temporanea poi spostiamo i file
    TMP_CLONE=$(mktemp -d)
    git clone "$GITHUB_REPO" "$TMP_CLONE"
    cp -a "$TMP_CLONE/." "$APP_DIR/"
    rm -rf "$TMP_CLONE"
    ok "Repository clonato"
fi

chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# Setup venv
VENV_DIR="$APP_DIR/venv"
info "Creo virtual environment con $PYTHON_BIN..."
"$PYTHON_BIN" -m venv "$VENV_DIR"
ok "Virtual environment creato in $VENV_DIR"

# Installa dipendenze Python
REQUIREMENTS="$APP_DIR/requirements.txt"
if [[ -f "$REQUIREMENTS" ]]; then
    info "Installo dipendenze Python da requirements.txt..."
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS"
    ok "Dipendenze Python installate"
else
    warn "requirements.txt non trovato in $APP_DIR — salto pip install"
fi

chown -R "$APP_USER":"$APP_USER" "$VENV_DIR"

# =============================================================================
# FASE 5 — Configurazione systemd
# =============================================================================
step "FASE 5 — Configurazione servizio systemd"

SERVICE_FILE="/etc/systemd/system/sogni-doro.service"
LOCAL_SERVICE="${SCRIPT_DIR}/sogni-doro.service"

if [[ -f "$LOCAL_SERVICE" ]]; then
    info "Copio $LOCAL_SERVICE in $SERVICE_FILE"
    cp "$LOCAL_SERVICE" "$SERVICE_FILE"
else
    warn "File sogni-doro.service non trovato nella dir script — genero uno di default"
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Sogni d'Oro — App Flask/Gunicorn
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind 127.0.0.1:${APP_PORT} app:app
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=sogni-doro

[Install]
WantedBy=multi-user.target
EOF
    ok "File .service generato automaticamente"
fi

systemctl daemon-reload
systemctl enable sogni-doro
systemctl start sogni-doro

# Verifica servizio attivo
sleep 2
if systemctl is-active --quiet sogni-doro; then
    ok "Servizio sogni-doro attivo e in esecuzione"
else
    err "Il servizio sogni-doro NON è partito. Controlla: journalctl -u sogni-doro -n 50"
    exit 1
fi

# =============================================================================
# FASE 6 — Configurazione nginx
# =============================================================================
step "FASE 6 — Configurazione nginx"

NGINX_AVAILABLE="/etc/nginx/sites-available/sognidoro"
NGINX_ENABLED="/etc/nginx/sites-enabled/sognidoro"
LOCAL_NGINX="${SCRIPT_DIR}/nginx_no_ssl.conf"

if [[ -f "$LOCAL_NGINX" ]]; then
    info "Copio $LOCAL_NGINX in $NGINX_AVAILABLE"
    cp "$LOCAL_NGINX" "$NGINX_AVAILABLE"
else
    warn "nginx_no_ssl.conf non trovato — genero configurazione di default"
    cat > "$NGINX_AVAILABLE" << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    access_log  /var/log/nginx/sognidoro_access.log;
    error_log   /var/log/nginx/sognidoro_error.log;

    location / {
        proxy_pass         http://127.0.0.1:${APP_PORT};
        proxy_set_header   Host              \$host;
        proxy_set_header   X-Real-IP         \$remote_addr;
        proxy_set_header   X-Forwarded-For   \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_read_timeout 90;
    }

    location /static {
        alias ${APP_DIR}/static;
        expires 7d;
    }
}
EOF
    ok "Configurazione nginx generata automaticamente"
fi

# Crea symlink
if [[ ! -L "$NGINX_ENABLED" ]]; then
    ln -s "$NGINX_AVAILABLE" "$NGINX_ENABLED"
    ok "Symlink sites-enabled creato"
else
    warn "Symlink già presente — aggiornato"
    ln -sf "$NGINX_AVAILABLE" "$NGINX_ENABLED"
fi

# Rimuovi default site
if [[ -f "/etc/nginx/sites-enabled/default" ]]; then
    rm /etc/nginx/sites-enabled/default
    warn "Default site nginx rimosso"
fi

# Test configurazione nginx
info "Test configurazione nginx..."
nginx -t
ok "Configurazione nginx valida"

systemctl restart nginx
ok "nginx riavviato"

# =============================================================================
# FASE 7 — Firewall (UFW)
# =============================================================================
step "FASE 7 — Configurazione firewall UFW"

ufw allow OpenSSH
ok "Regola OpenSSH aggiunta"

ufw allow 'Nginx Full'
ok "Regola 'Nginx Full' aggiunta"

ufw --force enable
ok "UFW abilitato"

ufw status verbose

# =============================================================================
# FASE 8 — SSL con Let's Encrypt (opzionale)
# =============================================================================
step "FASE 8 — SSL con Let's Encrypt (opzionale)"

# Legge risposta da variabile env oppure chiede all'utente
SETUP_SSL="${SETUP_SSL:-}"

if [[ -z "$SETUP_SSL" ]]; then
    echo ""
    read -r -p "$(echo -e "${YELLOW}Vuoi configurare SSL con Let's Encrypt adesso? [s/N]: ${RESET}")" SETUP_SSL
fi

case "${SETUP_SSL,,}" in
    s|si|y|yes|1)
        info "Configuro Let's Encrypt per $DOMAIN_NAME (email: $EMAIL)..."

        if certbot --nginx \
            -d "$DOMAIN_NAME" \
            --non-interactive \
            --agree-tos \
            -m "$EMAIL"; then
            ok "Certificato SSL installato per $DOMAIN_NAME"

            # Rinnovo automatico via cron
            CRON_LINE="0 3 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'"
            (crontab -l 2>/dev/null | grep -qF "certbot renew") || \
                (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
            ok "Rinnovo automatico SSL configurato (cron alle 03:00)"
        else
            warn "Certbot non riuscito. Probabilmente il dominio non punta ancora a questo IP."
            warn "Esegui manualmente: certbot --nginx -d $DOMAIN_NAME -m $EMAIL"
        fi
        ;;
    *)
        warn "SSL saltato. Esegui manualmente quando il DNS è configurato:"
        warn "  certbot --nginx -d $DOMAIN_NAME -m $EMAIL"
        ;;
esac

# =============================================================================
# FASE 9 — Riepilogo finale
# =============================================================================
step "FASE 9 — Riepilogo finale"

# Rileva IP pubblico
SERVER_IP=$(curl -s --max-time 5 https://api.ipify.org 2>/dev/null || \
            curl -s --max-time 5 http://ifconfig.me 2>/dev/null || \
            hostname -I | awk '{print $1}')

PROTOCOL="http"
if certbot certificates 2>/dev/null | grep -q "$DOMAIN_NAME"; then
    PROTOCOL="https"
fi

echo ""
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo -e "${BOLD}${GREEN}  ✔  Deploy completato con successo!${RESET}"
echo -e "${BOLD}${GREEN}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${BOLD}IP del server   :${RESET} $SERVER_IP"
echo -e "  ${BOLD}URL applicazione:${RESET} ${PROTOCOL}://${DOMAIN_NAME}"
echo -e "  ${BOLD}Log deploy      :${RESET} $LOG_FILE"
echo ""
echo -e "${BOLD}${CYAN}  Comandi utili:${RESET}"
echo -e "  ${YELLOW}# Stato servizio${RESET}"
echo -e "  systemctl status sogni-doro"
echo ""
echo -e "  ${YELLOW}# Log in tempo reale${RESET}"
echo -e "  journalctl -u sogni-doro -f"
echo ""
echo -e "  ${YELLOW}# Aggiornare l'app dal repo${RESET}"
echo -e "  git -C ${APP_DIR} pull && systemctl restart sogni-doro"
echo ""
echo -e "  ${YELLOW}# Riavviare nginx${RESET}"
echo -e "  systemctl restart nginx"
echo ""
echo -e "  ${YELLOW}# Rinnovo manuale SSL${RESET}"
echo -e "  certbot renew --dry-run"
echo ""
echo -e "${BOLD}${GREEN}  Sogni d'Oro è online!${RESET}"
echo ""

ok "Log salvato in: $LOG_FILE"
