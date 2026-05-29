# 🌙 Sogni d'Oro — Guida Deploy su VPS Hostinger (Ubuntu 22.04)

Questa guida ti accompagna passo dopo passo nel deploy dell'app su un VPS Hostinger.
Bastano conoscenze base del terminale: se sai aprire un terminale e copiare comandi, sei pronto.

---

## 0. Prima di iniziare

### Cosa ti serve

- ✅ Accesso al pannello Hostinger (hPanel) → [hpanel.hostinger.com](https://hpanel.hostinger.com)
- ✅ L'**IP del tuo VPS** (es. `185.123.45.67`)
- ✅ La **password root** del VPS
- ✅ (Opzionale ma consigliato) Un **dominio** puntato al VPS

### Come trovare le credenziali in hPanel

1. Vai su [hpanel.hostinger.com](https://hpanel.hostinger.com) e accedi
2. Nel menu laterale clicca su **VPS** → seleziona il tuo server
3. Nella scheda **Panoramica** trovi:
   - **Indirizzo IP** → copialo, ti serve subito
   - **Nome utente**: `root`
4. La password l'hai ricevuta per email al momento dell'acquisto, oppure la puoi reimpostare dalla scheda **Gestione** → **Reimposta password root**

> 💡 Se hai perso la password, reimpostala dall'hPanel prima di procedere: nessun problema, ci vogliono 30 secondi.

### Come aprire il terminale su Mac

- Premi `Cmd + Spazio`, digita **Terminale**, premi Invio
- Oppure: **Finder → Applicazioni → Utility → Terminale**

---

## 1. Primo accesso SSH

### Connettiti al server

Dal tuo terminale Mac, digita:

```bash
ssh root@IP_DEL_TUO_VPS
```

Sostituisci `IP_DEL_TUO_VPS` con l'IP che hai copiato dall'hPanel.
Esempio: `ssh root@185.123.45.67`

La prima volta ti chiede di confermare l'identità del server:

```
The authenticity of host '185.123.45.67' can't be established.
Are you sure you want to continue connecting (yes/no)? yes
```

Digita `yes` e premi Invio.

⚠️ **Inserisci la password root** (non appare mentre digiti, è normale).

### Cosa fare al primo accesso

Una volta dentro, esegui questi comandi nell'ordine:

```bash
# Aggiorna la lista dei pacchetti e installa gli aggiornamenti
apt update && apt upgrade -y
```

> ⏳ Ci vogliono 1-3 minuti. Aspetta che finisca prima di continuare.

```bash
# (Facoltativo ma consigliato) Cambia la password root
passwd
```

Ti chiede la nuova password due volte. Scegli qualcosa di robusto e salvala.

---

## 2. Deploy automatico (metodo consigliato)

Il modo più semplice per installare l'app è usare lo script `deploy.sh` già incluso nel repository. Lo script fa tutto da solo: installa Python, le dipendenze, configura il servizio e avvia l'app.

### Cosa fa lo script `deploy.sh`

1. Installa Python 3, pip e le dipendenze di sistema
2. Clona il repository GitHub sul server in `/var/www/sogni-doro`
3. Crea un ambiente virtuale Python e installa tutti i pacchetti
4. Configura **Nginx** come reverse proxy (porta 80 → app Streamlit)
5. Crea un servizio **systemd** che mantiene l'app sempre attiva (anche dopo riavvii)
6. (Se hai un dominio) Può attivare SSL con Let's Encrypt

### ⏱️ Tempo stimato: ~5 minuti

### Comandi da eseguire sul VPS

```bash
# Scarica lo script di deploy
wget https://raw.githubusercontent.com/TUO-USERNAME/sogni-doro/main/vps/deploy.sh

# Rendilo eseguibile
chmod +x deploy.sh

# Esegui il deploy
bash deploy.sh
```

> ⚠️ **Sostituisci** `TUO-USERNAME` con il tuo username GitHub e `sogni-doro` con il nome esatto del repository.

Lo script potrebbe chiederti:
- Il **dominio** (premi Invio per saltare e usare solo l'IP)
- La tua **email** (usata da Let's Encrypt per le notifiche SSL)

Quando vedi il messaggio `✅ Deploy completato!`, l'app è online.

---

## 3. Verifica che funzioni

### Controlla che il servizio sia attivo

```bash
systemctl status sogni-doro
```

Dovresti vedere una riga verde con scritto **active (running)**. Se vedi `failed` o `inactive`, vai alla sezione Troubleshooting.

### Apri l'app nel browser

**Prima del dominio (solo IP):**

```
http://IP_DEL_TUO_VPS:8501
```

Esempio: `http://185.123.45.67:8501`

**Con Nginx configurato (porta 80):**

```
http://IP_DEL_TUO_VPS
```

**Con dominio:**

```
http://sognidoro.it
```

> 💡 Se la pagina non si apre, il firewall potrebbe bloccare la porta. Vedi la sezione Troubleshooting.

### Come leggere i log se c'è un errore

```bash
# Log dell'app in tempo reale (Ctrl+C per uscire)
journalctl -u sogni-doro -f

# Ultime 50 righe di log
journalctl -u sogni-doro -n 50

# Log di Nginx
tail -n 50 /var/log/nginx/error.log
```

---

## 4. Configurazione del dominio (opzionale ma consigliato)

Avere un dominio custom (es. `sognidoro.it`) rende l'app più professionale e ti permette di attivare il certificato SSL gratuito (https://).

### Punta il dominio al VPS in hPanel

1. Vai su hPanel → **Domini** → seleziona il tuo dominio
2. Clicca su **Gestione DNS** (o **Zone DNS**)
3. Trova il record **A** e modifica il valore:
   - **Nome**: `@` (rappresenta il dominio principale)
   - **Punta a**: `IP_DEL_TUO_VPS`
   - **TTL**: `3600` (o lascia il default)
4. Aggiungi anche un record A per `www`:
   - **Nome**: `www`
   - **Punta a**: `IP_DEL_TUO_VPS`
5. Salva le modifiche

> ⚠️ La propagazione DNS può richiedere fino a **24-48 ore**, ma di solito in pochi minuti inizia già a funzionare. Puoi verificare lo stato su [dnschecker.org](https://dnschecker.org).

### Attiva SSL gratuito con Let's Encrypt

Una volta che il dominio punta al VPS, esegui sul server:

```bash
# Installa Certbot (se non già installato dallo script)
apt install certbot python3-certbot-nginx -y

# Richiedi il certificato SSL
certbot --nginx -d sognidoro.it -d www.sognidoro.it
```

Certbot ti chiede:
- La tua **email** (per le notifiche di scadenza)
- Di accettare i termini di servizio → `A`
- Se vuoi condividere l'email con EFF → `N` (facoltativo)
- Se vuoi reindirizzare HTTP → HTTPS → scegli `2` (consigliato)

> ✅ Il certificato è gratuito e si rinnova automaticamente ogni 90 giorni.

Dopo questo passaggio, l'app è raggiungibile su:

```
https://sognidoro.it
```

---

## 5. Aggiornare l'app

Ogni volta che modifichi il codice in locale e lo pubblichi su GitHub, puoi aggiornare il server con un solo comando.

### Aggiornamento manuale

Connettiti al VPS via SSH e lancia:

```bash
bash /var/www/sogni-doro/vps/update.sh
```

Lo script fa:
1. `git pull` per scaricare le ultime modifiche
2. Aggiorna le dipendenze Python se `requirements.txt` è cambiato
3. Riavvia il servizio `sogni-doro`

### Aggiornamento automatico con cron (ogni notte)

Se vuoi che il server si aggiorni da solo ogni notte senza doverlo fare manualmente:

```bash
# Apri il crontab
crontab -e
```

Aggiungi questa riga in fondo al file (aggiorna ogni notte alle 3:00):

```
0 3 * * * bash /var/www/sogni-doro/vps/update.sh >> /var/log/sogni-doro-update.log 2>&1
```

Salva con `Ctrl+O`, poi `Ctrl+X` per uscire.

> 💡 Il log degli aggiornamenti automatici finisce in `/var/log/sogni-doro-update.log`.

---

## 6. Comandi utili

Tienili a portata di mano per la gestione quotidiana del server.

```bash
# Stato del servizio
systemctl status sogni-doro

# Riavviare l'app
systemctl restart sogni-doro

# Fermare l'app
systemctl stop sogni-doro

# Avviare l'app
systemctl start sogni-doro

# Vedere i log in tempo reale
journalctl -u sogni-doro -f

# Ultime 100 righe di log
journalctl -u sogni-doro -n 100

# Aggiornare da GitHub
bash /var/www/sogni-doro/vps/update.sh

# Verificare che Nginx funzioni
systemctl status nginx

# Riavviare Nginx
systemctl restart nginx

# Controllare le porte aperte
ss -tlnp

# Spazio su disco disponibile
df -h

# RAM utilizzata
free -h
```

---

## 7. Troubleshooting

### 🔴 App non raggiungibile (timeout o connessione rifiutata)

Checklist da seguire nell'ordine:

**1. Il servizio è attivo?**
```bash
systemctl status sogni-doro
```
Se non è `active (running)` → `systemctl start sogni-doro`

**2. Nginx è attivo?**
```bash
systemctl status nginx
```
Se non è attivo → `systemctl start nginx`

**3. Il firewall blocca la porta?**
```bash
# Abilita le porte necessarie
ufw allow 80
ufw allow 443
ufw allow 8501
ufw status
```

**4. Hostinger firewall:** Vai su hPanel → VPS → **Firewall** e verifica che le porte 80, 443 e 8501 siano aperte.

---

### 🔴 Errore 502 Bad Gateway

Significa che Nginx è attivo ma l'app Streamlit non risponde.

```bash
# Guarda perché l'app non parte
journalctl -u sogni-doro -n 50

# Riavvia il servizio
systemctl restart sogni-doro

# Aspetta 10 secondi e controlla di nuovo
systemctl status sogni-doro
```

Cause comuni:
- Dipendenza Python mancante → `pip install -r requirements.txt`
- Errore nel codice Python → leggi i log per il traceback

---

### 🔴 Pagina bianca o errore all'apertura dell'app

Problema di import Python o file mancante.

```bash
# Leggi i log dettagliati
journalctl -u sogni-doro -n 100
```

Cerca righe con `Error`, `ImportError`, `ModuleNotFoundError` o `FileNotFoundError`.

```bash
# Se mancano dipendenze
cd /var/www/sogni-doro
source venv/bin/activate
pip install -r requirements.txt
systemctl restart sogni-doro
```

---

### 🔴 SSL non funziona (ERR_SSL_PROTOCOL_ERROR o lucchetto mancante)

> ⚠️ Il DNS deve propagarsi prima di poter attivare SSL. Se hai appena modificato i record DNS, **aspetta fino a 24 ore**.

Verifica che il dominio punti già al VPS:

```bash
# Dal tuo Mac (non dal server)
nslookup sognidoro.it
```

Deve restituire l'IP del tuo VPS. Se restituisce un altro IP, il DNS non è ancora propagato.

Quando il DNS è ok, riprova:

```bash
certbot --nginx -d sognidoro.it -d www.sognidoro.it
```

Per rinnovare un certificato scaduto:

```bash
certbot renew
```

---

### 🔴 Errore "Permission denied" durante il deploy

```bash
# Assicurati di essere root
whoami

# Se sei un altro utente, diventa root
sudo -i
```

---

## 8. Confronto: Streamlit Cloud vs VPS Hostinger

| Caratteristica | Streamlit Cloud (gratuito) | VPS Hostinger (~4-6€/mese) |
|---|---|---|
| 💰 Costo | Gratuito | ~4-6€/mese |
| ⚡ Velocità avvio app | Lenta (si "addormenta") | Sempre attiva, istantanea |
| 🌐 Dominio custom | A pagamento (piano Pro) | Incluso (basta il tuo dominio) |
| 🔒 SSL (https) | Incluso | Gratuito con Let's Encrypt |
| 📊 Uptime | Variabile (limiti piano free) | 99.9% garantito |
| 🔐 Privacy dati | Dati su cloud Streamlit | Dati solo sul tuo server |
| 📁 File persistenti | Limitati | Disco completo disponibile |
| ⚙️ Controllo server | Nessuno | Controllo totale |
| 🔧 Manutenzione | Zero | Minima (aggiornamenti OS) |
| 📈 Scalabilità | Limitata al piano | Upgradabile in pochi clic |
| 👥 Utenti simultanei | Pochi (piano free) | Dipende dal piano VPS |
| 🚀 Deploy | Git push automatico | Script update.sh manuale/cron |

> 💡 **Consiglio:** Per un progetto personale o piccola community, il VPS da 4€/mese è la scelta giusta: più veloce, più privato, più flessibile. Streamlit Cloud va bene solo per demo rapide.

---

## 📞 Risorse utili

- **hPanel Hostinger**: [hpanel.hostinger.com](https://hpanel.hostinger.com)
- **Verifica DNS**: [dnschecker.org](https://dnschecker.org)
- **Documentazione Streamlit**: [docs.streamlit.io](https://docs.streamlit.io)
- **Let's Encrypt**: [letsencrypt.org](https://letsencrypt.org)
- **Log del server**: `journalctl -u sogni-doro -f`

---

*Guida per Sogni d'Oro — Aggiornata a maggio 2026*
