# 🌙 Sogni e Numeri

> Racconti un sogno → riconosce simboli → consulta 7 fonti esoteriche → propone numeri per Lotto, MillionDAY e SuperEnalotto.
>
> **Live:** [sognienumeri.space](https://sognienumeri.space) · Community/SEO: vedi [MARKETING_SEO.md](MARKETING_SEO.md)

---

## Le 7 Fonti Integrate

| Fonte | Tipo | Voci |
|-------|------|------|
| Smorfia napoletana | Pratica | 5.470 |
| Capacelli 1881 | Storica | 9.733 |
| Sefer Yetzira | Kabala ebraica | Sefirot + 22 Lettere |
| Semprini | Filosofia del linguaggio | 5 gradi ermeneutici |
| René Guénon | Esoterismo | Framework 3 livelli |
| Sepharial (1920) | Numerologia planetaria | Cifre 0-9 + numeri 1-84 |
| Ronchetti (1922) | Iconologia italiana | ~900 voci simboliche |

---

## Avvio locale

```bash
git clone https://github.com/TUO_USERNAME/sogni-doro
cd sogni-doro
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy su Streamlit Community Cloud

1. Fai il fork di questo repo su GitHub
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Collega il repo → seleziona `app.py`
4. Deploy 🚀

---

## Struttura

```
app.py                  → interfaccia web (Streamlit)
dream_chatbot.py        → motore simboli + combinazioni
cabala_layer.py         → livello esoterico (7 fonti)
synonyms.yml            → sinonimi simboli (~90 voci)
data/
  smorfia_symbol_index_v0.csv    → 5.470 voci Smorfia
  capacelli_symbol_index_v0.csv  → 9.733 voci Capacelli
.streamlit/config.toml  → tema scuro/oro
requirements.txt
```

---

## Supporta il progetto

Se lo usi e ti piace → [☕ offrimi un caffè su Ko-fi](https://ko-fi.com/smorfiasogni)
