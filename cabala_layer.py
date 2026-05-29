"""Livello esoterico integrato.

Fonti integrate:
- Sefer Yetzira (traduzione diretta)
- Danilo Semprini — studio filosofico-linguistico del Sefer Yetzirah
- René Guénon — Esoterismo ed Exoterismo
- Sepharial (Walter Gorn Old, 1920) — The Kabala Of Numbers
- Giuseppe Ronchetti (1922) — Dizionario Illustrato dei Simboli

Il modulo fornisce tre livelli di lettura:
  exoterico  → corrispondenze pratiche Smorfia/Capacelli (già nel chatbot)
  esoterico  → Sefer Yetzira: Sefirot, Lettere, Elementi, Zodiaco, Gematria
             + Sepharial: pianeti per cifre 0-9, significati numeri 1-84
             + Ronchetti: iconologia simbolica
  metafisico → Guénon: simbolo come velo che rivela e cela; Keter inesprimibile
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Le dieci Sefirot
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Sefirah:
    numero: int
    nome_ebraico: str
    nome_italiano: str
    principio: str
    piano: str
    opposto: str
    colore: str          # colore tradizionale
    patriarca: str       # personificazione biblica (Semprini)
    senso_guenon: str    # lettura metafisica (Guénon)


SEFIROT: dict[int, Sefirah] = {
    1:  Sefirah(1,  "Keter",   "Corona",
                "trascendenza pura, origine prima, l'inesprimibile",
                "trascendente", "assenza totale",
                "bianco abbagliante", "Ain Sof (Infinito)",
                "il luogo dove la parola si ferma; il mistero nel senso etimologico"),
    2:  Sefirah(2,  "Chokhma", "Sapienza",
                "intuizione, lampo di rivelazione, pensiero primordiale",
                "cognitivo", "ignoranza",
                "grigio perlaceo", "Abramo (amore)",
                "l'esoterico per eccellenza: ciò che ognuno deve concepire da sé"),
    3:  Sefirah(3,  "Bina",    "Intelligenza",
                "comprensione, ragione, contenitore del pensiero",
                "cognitivo", "ottusità",
                "nero profondo", "Isacco (forza)",
                "il pensiero razionale che dà forma all'intuizione di Chokhma"),
    4:  Sefirah(4,  "Chesed",  "Amore / Misericordia",
                "generosità, grazia, apertura verso l'altro",
                "emotivo", "severità cieca",
                "bianco / argento", "Abramo",
                "il polo positivo della dualità fondamentale dell'esistenza"),
    5:  Sefirah(5,  "Ghevura", "Forza / Severità",
                "giudizio, resistenza, confine necessario",
                "emotivo", "debolezza",
                "rosso / oro", "Isacco",
                "il polo negativo: senza confine, la grazia diventa caos"),
    6:  Sefirah(6,  "Tiferet", "Bellezza / Armonia",
                "equilibrio, cuore, punto di unificazione tra alto e basso",
                "emotivo", "disarmonia",
                "giallo / oro solare", "Giacobbe",
                "il cuore del creato; in Cabalà LEV (32) = cuore = 32 sentieri"),
    7:  Sefirah(7,  "Netzach", "Eternità / Vittoria",
                "emozione pura, natura, impulso creativo, desiderio",
                "emotivo", "resa",
                "verde smeraldo", "Mosè",
                "l'impulso primordiale; nel sogno: il desiderio che muove"),
    8:  Sefirah(8,  "Hod",     "Splendore / Gloria",
                "comunicazione, linguaggio, mente analitica, forma",
                "emotivo", "silenzio vuoto",
                "arancio / rame", "Aronne",
                "la lettera come veicolo: exoterico nella sua forma, esoterico nel senso"),
    9:  Sefirah(9,  "Yesod",   "Fondamento",
                "connessione tra alto e basso, canale vitale, ciclo lunare",
                "emotivo", "disconnessione",
                "violetto / indaco", "Giuseppe",
                "il canale attraverso cui scende la luce; la luna come specchio del sole"),
    10: Sefirah(10, "Malkut",  "Regno / Presenza divina",
                "materializzazione, realtà concreta, terra, corpo fisico",
                "pratico", "esilio dalla radice",
                "bruno / oro antico", "David e Shlomoh",
                "l'exoterico per Guénon: ciò che è visibile, la 'lettera' della dottrina"),
}


# ---------------------------------------------------------------------------
# Le tre Lettere Madri (Sefer Yetzira cap. III + analisi Semprini)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LetteraMadre:
    lettera: str
    traslitt: str
    valore: int
    elemento: str
    mondo: str
    anno: str
    anima: str
    parte_corpo: str
    semprini_sintesi: str   # dall'analisi di Semprini


LETTERE_MADRI: dict[str, LetteraMadre] = {
    "shin": LetteraMadre(
        "ש", "Shin", 300, "Fuoco",
        "Cielo", "Estate / Caldo", "Maschile EMESH · Femminile ASHAM", "Testa",
        "Tre punte = tre parti del cervello (intuitivo/logico/sentimento). "
        "Il fuoco come motore di volontà e conoscenza. Keter del microcosmo. "
        "Il sibilo della combustione. Le tre lingue di fuoco. "
        "Abulafia: stato conscio della mente e dell'IO nello stato di veglia. "
        "Suono caotico come il bianco (tutte le lunghezze d'onda). Shin→Mem alternati col respiro inducono la transizione meditativa."
    ),
    "alef": LetteraMadre(
        "א", "Alef", 1, "Aria",
        "Corpo / Tronco", "Stagione temperata / Umido", "Corpo (mediatore)", "Tronco / Cuore",
        "Mediatore tra Shin (alto) e Mem (basso). Due Yod + una Vav: "
        "Acque Superiori (alto) + canale (Vav, 6) + Acque Inferiori (basso). "
        "Valore 26 = YHVH. Valore 111 = Uno sui tre piani (Mondo/Anno/Anima). "
        "Il soffio prima della parola. L'aria come ossigeno del sangue. "
        "Abulafia: 'Pronunciate Alef in un solo respiro — esprime il mistero dell'unità (Yichud)' (Or ha-sekhel). "
        "Ponte tra conscio (Shin) e inconscio (Mem): il respiro controllato è il primo passo verso l'estasi."
    ),
    "mem": LetteraMadre(
        "מ", "Mem", 40, "Acqua",
        "Terra", "Inverno / Freddo", "Femminile MASHA · Ventre", "Ventre / Genitali",
        "Mem aperta (מ) = fontana in superficie = maschile + femminile. "
        "Mem chiusa (ם) = profondità della terra = il non-manifestato. "
        "40 = purificazione (diluvio, Sinai, deserto). "
        "13ª lettera = AHAVAH (Amore) + AGUDAH (Unione). "
        "Mem×2 = 80 = YESOD (Fondamento). La forza generativa. "
        "Abulafia: sede dell'inconscio e delle emozioni profonde (istinti basilari). "
        "Suono armonico puro come il diapason — usato per indurre tranquillità nella meditazione. "
        "Opposto caotico della Shin; si equilibrano tramite l'Alef (respiro/aria)."
    ),
}

ELEMENTO_A_LETTERA: dict[str, str] = {
    "fuoco": "shin",
    "aria": "alef",
    "acqua": "mem",
}


# ---------------------------------------------------------------------------
# Le sette Lettere Doppie e i Pianeti
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LetteraDoppia:
    lettera: str
    traslitt: str
    valore: int
    pianeta: str
    giorno: str
    dono: str
    opposto: str
    porta_anima: str
    semprini_nota: str


LETTERE_DOPPIE: dict[str, LetteraDoppia] = {
    "bet":  LetteraDoppia("ב", "Bet",   2,   "Luna",     "Lunedì",    "Saggezza",  "Stoltezza",   "occhio destro",
                          "La Bet è la prima lettera della Torà (Bereshit). Valore 2 = polarità fondamentale. "
                          "Abulafia: ultima tappa dei Sette Centri di Consapevolezza, appena sotto Keter. "
                          "Archetipo di ogni recipiente — la 'casa' dell'anima completata dal percorso iniziatico (Tau→Bet)."),
    "gimel":LetteraDoppia("ג", "Gimel", 3,   "Marte",    "Martedì",   "Ricchezza", "Povertà",     "orecchio destro",
                          "Gimel = donare. La ricchezza che scorre tra chi ha e chi riceve."),
    "dalet":LetteraDoppia("ד", "Dalet", 4,   "Sole",     "Mercoledì", "Fertilità", "Deserto",     "narice destra",
                          "Dalet = porta. Il sole come porta tra il mondo visibile e invisibile."),
    "kaf":  LetteraDoppia("כ", "Kaf",   20,  "Venere",   "Giovedì",   "Vita",      "Morte",       "occhio sinistro",
                          "Kaf = palmo della mano. Venere come forza vitale e amore creativo."),
    "pe":   LetteraDoppia("פ", "Pe",    80,  "Mercurio", "Venerdì",   "Dominio",   "Schiavitù",   "orecchio sinistro",
                          "Pe = bocca. Mercurio come linguaggio e comunicazione. Hod nel corpo."),
    "resh": LetteraDoppia("ר", "Resh",  200, "Saturno",  "Sabato",    "Pace",      "Guerra",      "narice sinistra",
                          "Resh = testa/capo. Saturno come il Tempo che porta saggezza o peso."),
    "tav":  LetteraDoppia("ת", "Tav",   400, "Giove",    "Domenica",  "Bellezza",  "Bruttezza",   "bocca",
                          "Tav = segno/sigillo. Prima tappa del percorso iniziatico dei Sette Centri: il 'Sigillo in basso'. "
                          "L'ultima lettera dell'alfabeto è il primo passo del viaggio verso la Bet (la Casa). "
                          "Giove come compimento del ciclo cosmico."),
}

PIANETA_A_LETTERA: dict[str, str] = {l.pianeta.lower(): k for k, l in LETTERE_DOPPIE.items()}
# Somma valori = 709 = "Ein mazal le Israel" (Semprini)
SOMMA_DOPPIE = 2 + 3 + 4 + 20 + 80 + 200 + 400  # = 709


# ---------------------------------------------------------------------------
# Le dodici Lettere Semplici e lo Zodiaco
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LetteraSemplice:
    lettera: str
    traslitt: str
    valore: int
    segno_zodiacale: str
    mese_ebraico: str
    mese_italiano: str
    organo: str
    senso: str


LETTERE_SEMPLICI: dict[str, LetteraSemplice] = {
    "he":    LetteraSemplice("ה", "He",    5,   "Ariete",     "Nissan",   "Marzo-Aprile",    "gamba destra",    "conversazione"),
    "vav":   LetteraSemplice("ו", "Vav",   6,   "Toro",       "Iyyar",    "Aprile-Maggio",   "rene destro",     "riflessione"),
    "zayin": LetteraSemplice("ז", "Zayin", 7,   "Gemelli",    "Sivan",    "Maggio-Giugno",   "gamba sinistra",  "cammino"),
    "chet":  LetteraSemplice("ח", "Chet",  8,   "Cancro",     "Tamuz",    "Giugno-Luglio",   "mano destra",     "vista"),
    "tet":   LetteraSemplice("ט", "Tet",   9,   "Leone",      "Av",       "Luglio-Agosto",   "rene sinistro",   "udito"),
    "yod":   LetteraSemplice("י", "Yod",   10,  "Vergine",    "Elul",     "Agosto-Settembre","mano sinistra",   "azione"),
    "lamed": LetteraSemplice("ל", "Lamed", 30,  "Bilancia",   "Tishri",   "Settembre-Ottobre","cistifellea",    "accoppiamento"),
    "nun":   LetteraSemplice("נ", "Nun",   50,  "Scorpione",  "Cheshvan", "Ottobre-Novembre","intestino",       "odorato"),
    "samekh":LetteraSemplice("ס", "Samekh",60,  "Sagittario", "Kislev",   "Novembre-Dicembre","stomaco",        "dormire"),
    "ayin":  LetteraSemplice("ע", "Ayin",  70,  "Capricorno", "Tevet",    "Dicembre-Gennaio","fegato",          "rabbia"),
    "tsadi": LetteraSemplice("צ", "Tsadi", 90,  "Acquario",   "Shevat",   "Gennaio-Febbraio","trachea",         "nutrimento"),
    "kof":   LetteraSemplice("ק", "Kof",   100, "Pesci",      "Adar",     "Febbraio-Marzo",  "milza",           "riso"),
}

ZODIACO_A_LETTERA: dict[str, str] = {l.segno_zodiacale.lower(): k for k, l in LETTERE_SEMPLICI.items()}


# ---------------------------------------------------------------------------
# Numeri sacri (Semprini + Sefer Yetzira + tradizione ebraica)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NumeroSacro:
    valore: int
    nome: str
    significato: str
    fonte: str


NUMERI_SACRI: dict[int, NumeroSacro] = {
    1:   NumeroSacro(1,  "Alef / Uno",
                    "L'unità divina. Il punto dell'origine. '1 + 0 + 0 = 1 + 1' (Sefer Yetzira sec. 1).",
                    "Sefer Yetzira"),
    2:   NumeroSacro(2,  "Bet / Polarità",
                    "Prima lettera della Torà (Bereshit). La polarità fondamentale: bene/male, maschio/femmina. "
                    "2^5 = 32 sentieri.",
                    "Semprini"),
    3:   NumeroSacro(3,  "Tre Madri",
                    "Alef, Mem, Shin: Aria, Acqua, Fuoco. Tre Sefarim: Sefor (numero), Sippur (parola), Safer (scrittura). "
                    "Triade fondamentale del creato.",
                    "Sefer Yetzira"),
    7:   NumeroSacro(7,  "Settenario",
                    "Le 7 Lettere Doppie: 7 pianeti, 7 giorni, 7 porte dell'anima (occhi/orecchie/narici/bocca). "
                    "Proviene dal 'Cranio Divino' (Gulgalta). Somma = 709 = 'Ein mazal le Israel'.",
                    "Semprini"),
    9:   NumeroSacro(9,  "Yesod / Fondamento",
                    "La 9ª Sefirah. Connessione tra alto e basso. Il canale vitale. La luna come specchio del sole. "
                    "Nel corpo: gli organi sessuali, sede della forza generativa.",
                    "Semprini"),
    10:  NumeroSacro(10, "Dieci Sefirot",
                    "Dieci e non nove, dieci e non undici. Le dita delle mani. Il patto dell'unità. "
                    "Malkut: la materializzazione, la 'lettera' della dottrina per Guénon.",
                    "Sefer Yetzira"),
    12:  NumeroSacro(12, "Dodici Semplici",
                    "12 segni zodiacali, 12 mesi, 12 organi. Nasce dall'Estremità Infinitamente Lunga (Arikh Anpin). "
                    "Il piano dell'azione materiale e dei 12 sensi.",
                    "Semprini"),
    13:  NumeroSacro(13, "Ahavah / Echad",
                    "AHAVAH = Amore (1+5+2+5=13). ECHAD = Uno (1+8+4=13). "
                    "13ª lettera = Mem. L'amore come fondamento dell'unità.",
                    "Semprini"),
    22:  NumeroSacro(22, "Ventidue Lettere",
                    "Le lettere fondamentali con cui Dio ha creato il mondo. "
                    "La radice Tzeruf (permutazione) appare 22 volte nella Torà.",
                    "Sefer Yetzira"),
    26:  NumeroSacro(26, "YHVH / Tetragramma",
                    "Il Nome Divino più importante: Yod(10)+He(5)+Vav(6)+He(5)=26. "
                    "Stesso valore della lettera Alef scomposta in Yod+Yod+Vav (10+10+6=26). "
                    "Il sentiero 26 nel Genesi: 'Faremo l'uomo a nostra immagine'.",
                    "Semprini"),
    32:  NumeroSacro(32, "I 32 Sentieri della Sapienza",
                    "10 Sefirot + 22 Lettere. LEV = Cuore (Lamed 30 + Bet 2 = 32). "
                    "Elohim appare 32 volte nel Genesi. 2^5 = 32 (polarità × 5 dimensioni). "
                    "Il cuore del creato; i sentieri iniziatici dell'Albero della Vita.",
                    "Semprini"),
    40:  NumeroSacro(40, "Mem / Purificazione",
                    "Il valore della lettera Mem. 40 giorni del Diluvio. 40 giorni di Mosè sul Sinai. "
                    "40 anni nel deserto. 40 Sea d'acqua nel Mikve. Il tempo necessario per purificarsi. "
                    "CHEVEL (dolori del parto) = 40.",
                    "Semprini"),
    50:  NumeroSacro(50, "Cinquanta Porte dell'Intelligenza",
                    "Bina come 'Porte dell'Intelligenza': 50 forme di conoscenza razionale. "
                    "Il secondo percorso cabalistico (dopo i 32 Sentieri). L'anno del Giubileo.",
                    "Semprini"),
    72:  NumeroSacro(72, "I 72 Nomi di Dio",
                    "Dalla permutazione di tre versetti dell'Esodo (14:19-21), ognuno di 72 lettere. "
                    "La matrice combinatoria della creazione.",
                    "Cabala"),
    90:  NumeroSacro(90, "Tsadi / Acquario",
                    "Lettera semplice, valore 90. Segno Acquario, mese Shevat (Gen-Feb). "
                    "Senso: nutrimento. Organo: trachea. Il respiro come nutrimento.",
                    "Sefer Yetzira"),
    70:  NumeroSacro(70, "Ayin / Nulla",
                    "La lettera Ayin vale 70 = 'nulla', nullificazione. Nella scala meditativa cabalistica: "
                    "YESH AMITI (Vera Esistenza — Keter) / AYIN (Nulla — Chokhmà) / YESH YEHASSI (Esistenza Relativa — ultime 8 Sefirot). "
                    "In Shemà (שמע), l'Ayin è la terza lettera: testimonia lo stato di annullamento dell'ego che la meditazione porta.",
                    "Semprini/Abulafia"),
    120: NumeroSacro(120, "Ripetizioni del Nome — Hekhalot / Merkavà",
                    "Negli Hekhalot ('I Palazzi'), il Nome divino si ripete 120 volte senza interruzione: "
                    "prima tappa mantrica dell'Opera del Carro (Ma'assè Merkavah). "
                    "Non un fine in sé, ma apertura dello stato alterato per il viaggio di palazzo in palazzo (sette stadi di coscienza).",
                    "Semprini/Abulafia"),
}


# ---------------------------------------------------------------------------
# Sepharial — The Kabala Of Numbers (1920)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SepharialNumero:
    cifra: int
    pianeta: str
    significato_maggiore: str   # Major Key — significato profondo
    significato_minore: str     # Minor Key — significato conciso
    sogno_keywords: list[str]   # parole chiave per mapping onirico


SEPHARIAL_CIFRE: dict[int, SepharialNumero] = {
    0: SepharialNumero(0, "Infinito",
        "Infinito, paradosso universale, cosmo. L'uovo dell'universo, il cerchio primordiale. "
        "Anche negazione, limitazione, circumnavigazione, voyaging.",
        "Zero: universalità, cosmopolitismo, paradosso (né grande né piccolo).",
        ["vuoto", "cosmo", "oceano", "infinito", "cerchio"]),
    1: SepharialNumero(1, "Sole",
        "Manifestazione, asserzione, principio positivo-attivo. Il Logos. "
        "Ego, autoaffidamento, dignità, signoria. Il Sole come Unità.",
        "Individualità, possibile egoismo, autoaffidamento, distinzione.",
        ["sole", "luce", "re", "padre", "oro", "gloria", "signore"]),
    2: SepharialNumero(2, "Luna",
        "Antitesi. Dualismo del manifesto: Dio e Natura, Spirito e Materia. "
        "Riflessione, alternanza, creazione per combinazione. Luna come specchio.",
        "Relazione, attrazione psichica, emozione, simpatia o antipatia, dubbio.",
        ["luna", "notte", "specchio", "madre", "argento", "sogno", "dubbio"]),
    3: SepharialNumero(3, "Marte",
        "Trinità. La famiglia (padre-madre-figlio). Le tre dimensioni. "
        "Volontà, procedimento, penetrazione. Il fuoco della volontà.",
        "Espansione, aumento, capacità intellettuale, ricchezze, successo.",
        ["fuoco", "guerra", "sangue", "fratello", "forza", "volontà"]),
    4: SepharialNumero(4, "Mercurio",
        "Realtà e concrezione. L'universo materiale. Il cubo, il quadrato. "
        "Leggi fisiche, logica, ragione. La croce come materia dispiegata.",
        "Realizzazione, proprietà, possesso, credito, materialità.",
        ["terra", "casa", "lavoro", "libro", "lettera", "legge", "logica"]),
    5: SepharialNumero(5, "Giove",
        "Espansione, comprensione, giudizio. Aumento, fecondità, propagazione. "
        "Giustizia, ricompensa, raccolto. Il seme-frutto, la moltiplicazione.",
        "Ragione, logica, etica, viaggi, commercio, utilità.",
        ["abbondanza", "viaggio", "frutto", "grano", "giustizia", "ricchezza"]),
    6: SepharialNumero(6, "Venere",
        "Co-operazione, matrimonio, connessione. Alchimia. Concordia, armonia, pace. "
        "Psichismo, telepatia, psicometria. Il bello, la bontà, la verità.",
        "Co-operazione, matrimonio, reciprocità, simpatia, arte, musica, danza.",
        ["amore", "matrimonio", "fiore", "bellezza", "musica", "pace", "verde"]),
    7: SepharialNumero(7, "Saturno",
        "Completamento. Tempo e spazio. Le 7 età, i 7 giorni, i 7 sigilli. "
        "Saggezza, perfezione, equilibrio, riposo. Adam Kadmon — l'Uomo Perfetto.",
        "Equilibrio, contratti, accordi, trattati, armonia o discordia.",
        ["vecchio", "tempo", "ciclo", "sabato", "saggezza", "limite", "fine"]),
    8: SepharialNumero(8, "Urano",
        "Dissoluzione. Evoluzione ciclica, reazione, rivoluzione, anarchismo. "
        "Ispirazione, genio, invenzione. Lesione, separazione, divorzio.",
        "Ricostruzione, morte, negazione, decadenza, perdita, estinzione.",
        ["rottura", "rivoluzione", "lampo", "invenzione", "separazione", "fine"]),
    9: SepharialNumero(9, "Nettuno",
        "Rigenerazione. Nuova nascita. Spiritualità, estensione sensoriale, premonizione. "
        "Chiaroveggenza, sogni, telaestesia. Nebulosa, pulsazione, ritmo, rivelazione.",
        "Penetrazione, conflitto, energia, impresa, separazione, collera, acutezza.",
        ["acqua", "sogno", "visione", "spirito", "mistero", "rigenerazione", "profondo"]),
}

# Significati dei numeri 1-84 (Sepharial, Cap. XI)
SEPHARIAL_SIGNIFICATI: dict[int, str] = {
    1:  "Posizione, elevazione, cose al di sopra, un maestro o progenitore, una vetta",
    2:  "Distanza, cose remote, un viaggio o una terra straniera",
    3:  "Evento personale, un'infermità, febbre, calore o rabbia",
    4:  "Affare domestico, cerchia familiare, amore e piacere, cuore, qualcosa di molto desiderato",
    5:  "Matrimonio, accordo, comprensione, cose in unione o armonia",
    6:  "Notizie, cose riferite, un fratello, mezzi di comunicazione, viaggi",
    7:  "Una casa, cose sotterranee, terra o acqua in distesa, oceano, cambiamento o trasloco",
    8:  "Cose antiche o prodotti stranieri, un paese straniero, l'Oriente",
    9:  "Una morte o perdita, contratti difettosi, mezzi di restituzione",
    10: "Un'alleanza sfortunata, accordo problematico o disputa",
    11: "Il valore di una proprietà, una miniera, questioni di beni immobili",
    12: "Ambiente piacevole, festività, riunione conviviale, vestiti pregiati, comfort personale",
    13: "Denaro, questioni speculative, guadagno",
    14: "Un viaggio breve, crociera, messaggi attraverso l'acqua, una parente femminile",
    15: "Un lutto o morte, abiti funebri, una perdita o sfortuna",
    16: "Un'alleanza fortunata e felice, una moglie, buon accordo o comprensione",
    17: "Un servitore, o più vicino a sé stessi: un disagio, malattia o infermità",
    18: "Un viaggio piacevole, cosa d'oro, amore, domesticità o gioia, un fratello, un messaggio desiderato",
    19: "Una restrizione, reclusione, prigionia, segregazione; un figlio",
    20: "Un viaggio o lettera; qualcosa portato; comunicazione con un altro; una strada",
    21: "Guadagno, denaro, vantaggio finanziario, cose in possesso, cosa bianca e argentea",
    22: "Un matrimonio sfortunato o un partner malato, contratto difficile, un nemico o rivale",
    23: "Buona vita, vestiti ricchi, cibo abbondante, servi fedeli, buona salute, comfort",
    24: "Posizione incerta, disputa familiare, figli, impresa sfortunata, amori illeciti",
    25: "Grande guadagno, grande ricchezza, oro, il sole, qualcosa di brillante o sfolgorante",
    26: "Possesso pacifico, buona proprietà, la casa, terra piana, fondamenta",
    27: "Un luogo chiuso o stanza, viaggio breve in barca, un fratello o persona in relazione, lettera o messaggero",
    28: "Di sé stessi nell'immaginazione; lino bianco; una ciotola o vaso d'argento; luna nuova",
    29: "Cattiva salute, disturbo del sangue, scarso sostentamento, un periodo di povertà e difficoltà",
    30: "Bambini felici, esperienza piacevole, unione, una dote o lascito fortunato",
    31: "Qualcosa di sotterraneo, un serpente in casa, uno scorpione o rettile, un paese straniero",
    32: "Un re o ragiò, veste dorata, il sole, propria individualità e carattere",
    33: "Un messaggio piacevole, buona posizione, un fratello, qualche distinzione",
    34: "Beneficio finanziario, acquisto di cibo o altri beni necessari, cereali, qualche beneficio corporeo",
    35: "Una donna, una nascita, un complotto o piano, qualcosa di segreto; una reclusione",
    36: "Una perdita per speculazione, un figlio malato, una famiglia infelice, miseria e guai",
    37: "Un contratto sfortunato, un matrimonio infelice, una casa o proprietà, una stalla",
    38: "Una morte per malaria o febbre enterica; un viaggio, un messaggio; una sorella; un laghetto vicino",
    39: "Un luogo chiuso o tempio; camera dorata, la reclusione o esilio di un re",
    40: "Denaro, cose di valore, gioielli o abiti, il prezzo del grano",
    41: "Sé stessi o la propria figura, i propri abiti, investitura, cibo, posizione, credito",
    42: "Un amico, una donna di qualità, una mecenate o il suo favore, una riunione di persone",
    43: "Proprietà ancestrale, un vecchio, un vecchio edificio, il valore dei minerali, un cimitero",
    44: "Un fratello, una lettera d'oltremare o da grande distanza, un libro di teologia, buona salute, lusso",
    45: "Un matrimonio, guadagno o perdita, cosa di scarso valore, un'ineguaglianza, una frode",
    46: "Un amico, uomo di posizione e onore; qualcosa d'oro, di valore, un gioiello, un anello d'oro",
    47: "Giustizia, equità, valore, misura, peso, proporzione, pace, soddisfazione, riposo, una morte",
    48: "Una stanza per vestirsi, un luogo privato, una serva nascosta, salute di una donna, notizie da lontano",
    49: "Un cambiamento di posizione, la propria madre, cosa di distinzione, una donna al potere, una regina",
    50: "Un viaggio doloroso, una sorella in difficoltà, un messaggio dolente, una chiamata all'ufficio",
    51: "Guadagno e ricchezza, una scommessa, denaro da lontano, una professione",
    52: "Malattia o morte personale, cose perdute, nascoste o occulte, un servo maschio, un rettile",
    53: "Alto ufficio, il re, un uomo al potere, perdita d'oro, un leone morto",
    54: "Una malattia pericolosa, una donna in difficoltà, una moglie, una ragazza, un accordo, quattro mura",
    55: "Una morte, una carta perduta, un messaggio smarrito, una giovane ragazza, una riunione, un amico",
    56: "Un paese straniero oltre i mari, un viaggio per mare, una riunione religiosa, una pubblicazione, una nave",
    57: "Ricchezza acquisita, un tesoro o riserva, una pensione o eredità, un parente maschio",
    58: "Acquisizione, influenza personale, un giudice o guru, istruzione; proprietà personale, tenuta",
    59: "Una camera della morte, un ospedale o camera di malattia, un figlio maschio; il fuoco domestico",
    60: "Una cerimonia religiosa; un re straniero; un rishi; samadhi; il sole del cielo; il tempo",
    61: "Cibo, commercio, abiti pregiati; un amico maschio; un mercato; un servo",
    62: "Uno scritto o accordo; un impegno o contratto; un processo legale; una posizione; un padre",
    63: "Una donna morta, proprietà perduta, un lenzuolo funebre, luna calante, la dote della moglie",
    64: "Sé stessi riguardo alla posizione; proprietà acquisita; un'eredità; un vecchio; una durata; un baratto",
    65: "Un viaggio breve e ritorno; andare e venire; un viaggio a piedi; una stanza chiusa; una sorella",
    66: "Un luogo di cremazione o rogo; un luogo roccioso; minerali; un medico; un amico morto; casa che brucia",
    67: "Un raja morto; la perdita d'oro; la dote della moglie; una cintura; un figlio malato",
    68: "Una figlia; la cerchia domestica; una posizione di fiducia; sicurezza",
    69: "Abbigliamento, un servo, una nave, merci, generi alimentari, commercio, una cosa di scienza",
    70: "Una moglie, un accordo, una riunione pubblica, luna piena",
    71: "Una brocca d'acqua; una vecchia associazione; un amico; sé stessi in compagnia; un luogo privato",
    72: "Ricchezza, un amico principesco, un bramino, una riunione religiosa, sandali e cose a coppie",
    73: "Un fratello; una posizione; la morte di un sovrano; un viaggio rapido; un messaggio arrabbiato",
    74: "Un sole brillante; un grande splendore; la vista; una moglie orgogliosa; un potente nemico; una caccia",
    75: "Un luogo piacevole; una tenuta ricca; moksha; un tesoro sepolto; bestiame",
    76: "Un figlio; un luogo di apprendimento; una scuola; una sposa; un brahmachari",
    77: "Un turbante bianco o dhoti; una serva; medicine; acqua; bere",
    78: "Un vecchio amico; un'istituzione; una vecchia alleanza; un ospedale; un uomo in prigione",
    79: "Sé stessi; aumento e prosperità, posizione, potere e ricchezza; le estremità, i piedi",
    80: "Guadagno; un rischio di perdita; una perdita per fuoco; un paese straniero; una morte lontana",
    81: "Un parente ricco; abiti pregiati; ornamenti d'oro; salute personale; frutta matura",
    82: "Una morte pacifica; una ricca dote; un messaggio piacevole; un viaggio per profitto; una sorella",
    83: "Commercio; un trattato o accordo; un contratto d'affitto di proprietà; una sposa o fidanzamento",
    84: "Una figlia; un luogo di bagno o festività; una persona amata",
}


# ---------------------------------------------------------------------------
# Ronchetti — Dizionario Illustrato dei Simboli (1922)
# Voci oniriche chiave
# ---------------------------------------------------------------------------

RONCHETTI_SIMBOLI: dict[str, str] = {
    "acqua": "Fecondità primordiale, purificazione, vita. Culto antico dell'acqua come elemento divino. "
             "Animali: pesce (venerazione assira). Diversi: azzurro (colore dell'acqua marina), urna (emblema delle sorgenti).",
    "fuoco": "Il più nobile degli elementi, immagine viva del sole. Divinità familiare (Romani). "
             "Il fuoco eterno affidato alle Vestali. Il tempio del fuoco aveva forma rotonda = l'universo.",
    "mare":  "Il ventre. 'Gli spiegatori dei sogni prendono il mare per il ventre.' (Ronchetti) "
             "Tridente = Nettuno = terza regione. Vedi: purificazione, molestie, impeto dei nemici.",
    "luna":  "Astro che rappresenta l'infanzia. Diana in cielo. Argento (sua luce pallida). "
             "Gatto = simbolo lunare egiziano. Cipolla (mostra le fasi lunari). Mezzaluna = attributo.",
    "sole":  "Vita, coscienza, fonte di tutto. Consacrato a: cavallo (Persiani), gallo (risveglio), aquila (sovranità). "
             "L'oro è il metallo del sole.",
    "morte": "Figlia della Notte e del Tempo. Falce, orologio a polvere, ali di pipistrello. "
             "Carro tirato da quattro cavalli neri. Civetta (malaugurio), cipresso, gallo (risveglio dopo la morte).",
    "serpente": "Prudenza, saggezza, salute. Il custode regale (Egitto). "
                "Bastone con serpente = medicina (Esculapio). Anche: inganno, tentazione.",
    "aquila":   "Uccello di Giove, forza e potere sovrano. Insegna di Persia, Roma, Egitto. "
                "Dai Salmi: 'Si rinnoverà la tua gioventù a guisa d'aquila' → rinnovamento.",
    "leone":    "Forza e coraggio. Turchese = pietra del coraggio. Emblema della regalità.",
    "cavallo":  "Consacrato a Marte. L'incontro di un cavallo era presagio di guerra. "
                "I Lacedemoni adoravano il Sole sotto forma di cavallo. Velocità, potere bellico.",
    "cane":     "Fedeltà verso il padrone (Edera — si attacca tenacemente). "
                "In senso biblico: vile, abbietto, spregevole. Guardiano dei sepolcri.",
    "stella":   "Un tempo credute abitate da angeli vigilanti che investigassero i fatti degli uomini. "
                "Platone: le stelle come esploratori. Guida, speranza, destino.",
    "corona":   "Potere regale, dignità, trionfo, vittoria. Segno di signoria.",
    "croce":    "Intersezione del verticale (spirituale) e dell'orizzontale (materiale). Redenzione.",
    "oro":      "Sole, perfezione, regalità. Età dell'oro: pace e prosperità. "
                "Libertà (gli schiavi liberati ricevevano oro e si vestivano di bianco).",
    "amore":    "Eros/Cupido. Arco e frecce (d'oro → gioia; di piombo → dolore). "
                "Ali (incostanza). Benda sugli occhi (accecamento). Fiaccola (ardente passione).",
    "abbondanza": "Cornucopia, formiche (portano provviste → predizione di ricchezza), frumento, gru. "
                  "La giovane coronata di fiori con manto verde.",
    "luce":     "Lucerna accesa = vita. 'L'olio che mantiene la fiamma simboleggia l'umore vitale.' (Ronchetti) "
                "Plutarco: lucerna = corpo, fiamma = anima.",
    "re":       "Elefante (guida il branco = guida il popolo). Dominio, signoria, potere sovrano.",
    "angelo":   "Messaggero di Dio. Ceti angelici = custodi dei cieli e degli uomini.",
    "formica":  "Abbondanza e ricchezza (predizione). Ma anche morte: 'abitano in buche sotterranee dove si pongono i cadaveri'.",
    "civetta":  "Malaugurio, morte. Vaga di notte = la notte rappresenta la morte.",
    "gallo":    "Risveglio alla vita eterna dopo la morte. Sacrificato alla Morte ma simbolo di resurrezione.",
    "cipresso": "Morte, cimitero. Attributo della morte. Segno di malaugurio per gli indovini.",
    "colomba":  "Purezza, pace, Spirito Santo. Messaggera divina.",
    "torre":    "Orgoglio, ambizione, ma anche fortezza e protezione.",
    "chiave":   "Accesso, autorità, apertura del sacro. Porta della conoscenza.",
}


# ---------------------------------------------------------------------------
# Cinque gradi ermeneutici (Semprini da Sefer Mayan Ha Chokhmà)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GradoErmeneutico:
    nome_ebraico: str
    traduzione: str
    sefirah: str
    descrizione: str
    applicazione: str


CINQUE_GRADI: list[GradoErmeneutico] = [
    GradoErmeneutico("Tiqun", "Proprio / Essenza",
                     "Keter (inesprimibile)",
                     "Il significato ultimo, raffinato da ogni impurità. Irraggiungibile. "
                     "È il luogo dove si radica la langue stessa, il suo 'orizzonte di senso'.",
                     "Non si descrive: si sente nel silenzio dopo la lettura"),
    GradoErmeneutico("Tzeruf", "Permutazione",
                     "Chokhma (intuizione)",
                     "Le lettere del simbolo permutate rivelano un significato parallelo. "
                     "Purificare, raffinare, bruciare (Tzoref = orafo; Tzarfit = crogiolo).",
                     "Inverti le lettere del simbolo: cosa rivela l'ombra?"),
    GradoErmeneutico("Ma'amar", "Acrostico / Espansione",
                     "Bina (intelligenza razionale)",
                     "Ogni lettera del simbolo è l'iniziale di un'altra parola. "
                     "La parola si decomprime in una frase.",
                     "A-C-Q-U-A: ogni lettera apre un universo semantico"),
    GradoErmeneutico("Mikhlol", "Contesto / Insieme",
                     "Tiferet (armonia sintetica)",
                     "Studio del simbolo nel contesto del sogno: come si relaziona agli altri simboli? "
                     "Tiferet armonizza Chesed (amore) e Ghevura (forza).",
                     "Il sogno come sistema: ogni simbolo modifica gli altri"),
    GradoErmeneutico("Cheshbon", "Calcolo / Gematria",
                     "Malkut (terra, realtà concreta)",
                     "Il valore numerico della parola. La tecnica più popolare ma la meno profonda. "
                     "'Numeri piccoli per cervelli piccoli' (Zohar).",
                     "Il numero estratto dalla Smorfia è qui: il grado più basso, ma il più pratico"),
]


# ---------------------------------------------------------------------------
# Mappature simbolo → elemento
# ---------------------------------------------------------------------------

SIMBOLO_A_ELEMENTO: dict[str, str] = {
    "fuoco": "fuoco", "fiamma": "fuoco", "incendio": "fuoco", "sole": "fuoco",
    "luce": "fuoco", "caldo": "fuoco", "bruciare": "fuoco", "ardere": "fuoco",
    "calore": "fuoco", "candela": "fuoco", "brace": "fuoco", "vampa": "fuoco",
    "testa": "fuoco", "mente": "fuoco", "intuizione": "fuoco",
    "acqua": "acqua", "mare": "acqua", "fiume": "acqua", "pioggia": "acqua",
    "lago": "acqua", "oceano": "acqua", "nuotare": "acqua", "bagnarsi": "acqua",
    "sorgente": "acqua", "lacrime": "acqua", "piangere": "acqua", "ghiaccio": "acqua",
    "neve": "acqua", "nebbia": "acqua", "ventre": "acqua", "grembo": "acqua",
    "vento": "aria", "aria": "aria", "brezza": "aria", "tempesta": "aria",
    "soffio": "aria", "respiro": "aria", "voce": "aria", "parola": "aria",
    "spirito": "aria", "volare": "aria", "nuvola": "aria", "cielo": "aria",
    "uragano": "aria", "bufera": "aria", "tronco": "aria", "corpo": "aria",
}

SIMBOLO_A_PIANETA: dict[str, str] = {
    "luna": "Luna", "notte": "Luna", "argento": "Luna", "specchio": "Luna",
    "marte": "Marte", "guerra": "Marte", "sangue": "Marte", "coltello": "Marte",
    "sole": "Sole", "giorno": "Sole", "oro": "Sole", "luce": "Sole",
    "venere": "Venere", "amore": "Venere", "verde": "Venere", "rose": "Venere",
    "mercurio": "Mercurio", "libro": "Mercurio", "lettera": "Mercurio", "voce": "Mercurio",
    "saturno": "Saturno", "tempo": "Saturno", "vecchio": "Saturno", "pietra": "Saturno",
    "giove": "Giove", "re": "Giove", "abbondanza": "Giove", "tempio": "Giove",
}

SIMBOLO_A_SEGNO: dict[str, str] = {
    "leone": "Leone", "sole": "Leone", "oro": "Leone",
    "acqua": "Cancro", "luna": "Cancro", "notte": "Cancro",
    "mare": "Pesci", "pesce": "Pesci", "profondo": "Pesci",
    "terra": "Toro", "toro": "Toro", "montagna": "Capricorno",
    "vento": "Gemelli", "uccello": "Gemelli", "parola": "Gemelli",
    "bilancia": "Bilancia", "giustizia": "Bilancia",
    "scorpione": "Scorpione", "serpente": "Scorpione",
    "ariete": "Ariete", "coltello": "Ariete", "fuoco": "Ariete",
    "arciere": "Sagittario", "freccia": "Sagittario", "viaggio": "Sagittario",
    "acquario": "Acquario", "stelle": "Acquario",
    "vergine": "Vergine", "grano": "Vergine", "campo": "Vergine",
}


# ---------------------------------------------------------------------------
# Funzioni di base
# ---------------------------------------------------------------------------

def _normalizza(testo: str) -> str:
    decomposed = unicodedata.normalize("NFD", testo.lower())
    ascii_text = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", ascii_text).strip()


def gematria_italiano(testo: str) -> int:
    """Gematria Mispar Echrakhi adattata all'italiano (A=1, B=2, ..., Z=26).

    Dalla tradizione: 'il valore numerico è il sistema più umile ma il più pratico'
    (Semprini, dal grado Cheshbon = Malkut).
    """
    norm = _normalizza(testo)
    valore = 0
    for ch in norm:
        if "a" <= ch <= "z":
            valore += ord(ch) - ord("a") + 1
    return valore


def radice_digitale(n: int) -> int:
    """Mispar Qatan: riduce alla radice digitale (1-9).

    Nota di Semprini: 'Numeri Piccoli è per cervelli piccoli' (Zohar).
    Utile come primo accesso, ma non è il livello più profondo.
    """
    if n <= 0:
        return 1
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def sefirah_per_numero(n: int) -> Sefirah:
    """Sefirah associata a un numero tramite radice digitale."""
    if n == 10 or n % 10 == 0:
        return SEFIROT[10]
    chiave = radice_digitale(n % 90 or 90) if n > 10 else n
    return SEFIROT.get(chiave or 9, SEFIROT[9])


def numeri_sacri_trovati(numeri: list[int]) -> list[NumeroSacro]:
    """Individua i numeri sacri tra quelli proposti dalla Smorfia."""
    trovati = []
    for n in numeri:
        if n in NUMERI_SACRI:
            trovati.append(NUMERI_SACRI[n])
        # Cerca anche per radice digitale
        radice = radice_digitale(n)
        if radice in NUMERI_SACRI and NUMERI_SACRI[radice] not in trovati:
            trovati.append(NUMERI_SACRI[radice])
    # Deduplica
    seen = set()
    result = []
    for ns in trovati:
        if ns.valore not in seen:
            seen.add(ns.valore)
            result.append(ns)
    return result[:4]


# ---------------------------------------------------------------------------
# Note meditative di Abulafia (Chokhmath ha-tzeruf / Or ha-sekhel)
# ---------------------------------------------------------------------------

_ABULAFIA_NOTE: dict[int, str] = {
    1:   ("Alef — il mistero dell'unità (Yichud). 'Pronunciate Alef in un solo respiro: esprime "
          "il mistero dell'unità. Non interrompete il respiro' (Or ha-sekhel)."),
    2:   ("Bet — la prima dualità. Ogni lettera si canta in coppia; tra ogni coppia due respiri "
          "silenziosi, non di più. La polarità è il fondamento del creato."),
    3:   ("Tre livelli dell'estasi: mikhtav (scrittura) → mivtà (pronuncia/canto) → machshav (pensiero puro). "
          "Ogni livello abbandona la fisicità del precedente; al terzo la lettera diventa puro moto interiore."),
    4:   ("Quattro azioni del cammino estatico: dilug (balzare — restare in una tecnica), "
          "saltare (passare da sistema a sistema), spaccare (entrare coscienti nell'estasi), "
          "incidere (imprimere il momento estatico nell'anima)."),
    5:   ("Cinque vocali del Tetragramma. Cholem → est, testa in avanti. Chirik → guarda in basso. "
          "Shuruk → capo in avanti (neutro). Tzerè → sinistra a destra. Kametz → destra a sinistra. "
          "Ogni movimento attira la potenza superna verso di sé."),
    7:   ("I Sette Palazzi (Hekhalot) = sette stadi del viaggio mistico. "
          "Percorso iniziatico dalla Tau (Sigillo in basso) alla Bet (la Casa — anima completata appena sotto Keter). "
          "'Andavano e venivano come un baleno' (Ezechiele 1:14) — MATI VELO MATI."),
    10:  ("Dieci Sefirot senza determinazione. 'Frena il tuo cuore sì che non pensi, la tua bocca sì che non parli; "
          "e se il tuo cuore corre via, che ritorni là donde era partito' (Sefer Yetzira V). "
          "Il patto con il limite umano: Tocca e non Tocca."),
    22:  ("Chokhmath ha-tzeruf — Scienza della combinazione delle 22 lettere. Le combinazioni non devono "
          "significare nulla per noi: ciò che è assoluto e indeterminato libera l'anima dalle forme naturali. "
          "'La musica del puro pensiero' — la serie di Abulafia corrisponde a una scala diatonica."),
    25:  ("Venticinque paia di lettere nelle tecniche vocali. Tra Yod e He: 25 respiri, non di più. "
          "Dopo ogni serie: 5 respiri liberi. Il respiro conta i passi del ritorno all'unità."),
    26:  ("YHVH — il Tetragramma, base delle tecniche estatiche di Abulafia. "
          "Combinato con Alef e le 5 vocali (Or ha-sekhel). "
          "'Quando Abramo invocò il Nome di Dio era in grado di raggiungere gli stati mistici più alti' (Genesi 12:8)."),
    32:  ("I 32 Sentieri: 'Di qui in poi procedi a calcolare quel che la bocca non può pronunciare, "
          "l'occhio non può vedere né l'orecchio ascoltare' (Sefer Yetzira). "
          "Passaggio dal calcolo combinatorio all'abbandono di ogni fisicità delle lettere."),
    40:  ("Quaranta — il tempo della purificazione. La meditazione profonda richiede lo stesso "
          "tempo di Mosè sul Sinai: l'inconscio (Mem) si apre solo dopo lungo silenzio."),
    50:  ("Cinquanta Porte dell'Intelligenza (Bina). Chokhmà = AYIN (Nulla); Bina = 50 porte "
          "che danno forma al lampo intuitivo. Le due Sefirot superiori accessibili all'uomo."),
    70:  ("Ayin (ע) — il Nulla (valore 70). La soglia della nullificazione: "
          "YESH AMITI (Vera Esistenza — Keter) / AYIN (Nulla — Chokhmà) / YESH YEHASSI (Esistenza Relativa). "
          "In Shemà, l'Ayin è lo stato di annullamento dell'ego verso cui tende la meditazione."),
    72:  ("Nome di 72 Lettere — dai tre versetti di Esodo 14:19-21 (unici al mondo per simmetria). "
          "Prima triade 'VHV' si pronuncia 'VaHeVa'. "
          "Abulafia usa questo Nome nel Chayay Olam Abach per le più alte tecniche del Ma'assè Merkavah."),
    120: ("Negli Hekhalot il Nome si ripete 120 volte senza interruzione: apertura dello stato alterato "
          "per il viaggio di palazzo in palazzo. Il mantra non è un fine ma una soglia — "
          "l'Opera del Carro (Ma'assè Merkavah) inizia dove il mantra finisce."),
}


def abulafia_note(numero_chiave: int) -> str:
    """Nota meditativa di Abulafia per il numero (Chokhmath ha-tzeruf)."""
    nota = _ABULAFIA_NOTE.get(numero_chiave)
    if nota:
        return nota
    radice = radice_digitale(numero_chiave)
    nota = _ABULAFIA_NOTE.get(radice)
    if nota:
        return f"[Radice {radice} di {numero_chiave}] {nota}"
    sf = SEFIROT.get(radice, SEFIROT[1])
    return (
        f"Per {numero_chiave}, Abulafia prescrive di combinare le lettere del valore numerico: "
        f"'procedi a calcolare quel che la bocca non può pronunciare'. "
        f"Radice: {radice} → {sf.nome_ebraico} ({sf.nome_italiano})."
    )


# ---------------------------------------------------------------------------
# Triade dell'Anima (Shin / Alef / Mem) — dal cap. III Sefer Yetzira + Semprini
# ---------------------------------------------------------------------------

def _conta_triade(parole: list[str]) -> dict[str, int]:
    """Conta quante parole appartengono a ciascun elemento della Triade."""
    conteggio = {"fuoco": 0, "aria": 0, "acqua": 0}
    for p in parole:
        el = SIMBOLO_A_ELEMENTO.get(_normalizza(p))
        if el:
            conteggio[el] += 1
    return conteggio


def triade_anima_testo(shin: int, alef: int, mem: int) -> str:
    """Rappresentazione testuale della Triade dell'Anima."""
    totale = shin + alef + mem or 1

    def barra(n: int) -> str:
        piena = min(10, round(n / totale * 10))
        return "█" * piena + "░" * (10 - piena)

    dom = max((shin, "FUOCO / Shin / Testa"), (alef, "ARIA / Alef / Tronco"),
              (mem, "ACQUA / Mem / Ventre"))[1]

    righe = [
        f"  SHIN ש (Fuoco/Testa):   {barra(shin)} {shin}",
        f"  ALEF א (Aria/Tronco):   {barra(alef)} {alef}",
        f"  MEM  מ (Acqua/Ventre):  {barra(mem)} {mem}",
        f"  → Dominante: {dom}",
    ]
    return "\n".join(righe)


# ---------------------------------------------------------------------------
# Albero della Vita (testo) — i nodi attivati dal sogno
# ---------------------------------------------------------------------------

def albero_vita_testo(sefirot_attivate: set[int]) -> str:
    """Rappresentazione schematica dell'Albero della Vita con nodi attivati."""

    def nodo(n: int) -> str:
        s = SEFIROT[n]
        mark = "◉" if n in sefirot_attivate else "○"
        return f"{mark} {n:02d} {s.nome_ebraico} ({s.nome_italiano[:12]})"

    righe = [
        "         " + nodo(1),
        "    " + nodo(2) + "       " + nodo(3),
        "         " + nodo(4),
        "    " + nodo(5) + "       " + nodo(6),
        "         " + nodo(7),
        "    " + nodo(8) + "       " + nodo(9),
        "         " + nodo(10),
    ]
    return "\n".join(righe)


# ---------------------------------------------------------------------------
# Lettura Guénon: i tre livelli esoterico/exoterico/metafisico
# ---------------------------------------------------------------------------

def guenon_lettura(
    testo_sogno: str,
    simboli: list[str],
    elemento_dom: Optional[str],
    sefirah_chiave: Sefirah,
) -> dict[str, str]:
    """Produce la lettura secondo il framework di Guénon (3 livelli).

    Dal testo: exoterico = ciò che è più esteriore e alla portata di tutti;
    esoterico = lo sviluppo più profondo della stessa dottrina;
    metafisico = ciò che è realmente inesprimibile (Keter).
    """
    nomi_simboli = ", ".join(simboli[:5]) if simboli else "simboli non identificati"
    elem_testo = elemento_dom.upper() if elemento_dom else "indefinito"
    lm_testo = ""
    if elemento_dom and elemento_dom in ELEMENTO_A_LETTERA:
        lm = LETTERE_MADRI[ELEMENTO_A_LETTERA[elemento_dom]]
        lm_testo = f" (Lettera Madre {lm.traslitt}, valore {lm.valore})"

    return {
        "exoterico": (
            f"I simboli '{nomi_simboli}' vengono letti secondo la Smorfia napoletana e "
            f"Capacelli 1881: corrispondenze dirette, pratiche, accessibili a tutti. "
            f"Questo è il livello della 'lettera' — utile e verificabile."
        ),
        "esoterico": (
            f"Lo stesso sogno parla in modo più profondo: elemento dominante {elem_testo}{lm_testo}, "
            f"Sefirah chiave {sefirah_chiave.nome_ebraico} ({sefirah_chiave.nome_italiano}). "
            f"'{sefirah_chiave.principio}'. "
            f"Questo livello 'sviluppa e completa, dando un senso più profondo a ciò che "
            f"l'exoterismo espone in forma troppo semplificata' (Guénon)."
        ),
        "metafisico": (
            f"Oltre la Smorfia e oltre il Sefer Yetzira c'è Keter: '{SEFIROT[1].senso_guenon}'. "
            f"Il simbolo è un velo che rivela e contemporaneamente cela. "
            f"Come per l'ideogramma cinese che significa insieme 'sole', 'luce' e 'verità', "
            f"questo sogno ha un significato sensibile (i numeri), uno razionale (le corrispondenze) "
            f"e uno metafisico (l'inesprimibile che ognuno deve concepire da sé)."
        ),
    }


# ---------------------------------------------------------------------------
# I cinque gradi applicati al simbolo principale
# ---------------------------------------------------------------------------

def cinque_gradi_testo(simbolo_principale: str, tema_sogno: str) -> list[str]:
    """Applica i cinque gradi ermeneutici al simbolo principale del sogno."""
    if not simbolo_principale:
        return []

    s = _normalizza(simbolo_principale)
    # Tzeruf (permutazione): inverti la parola
    permutazione = s[::-1]

    # Gematria del simbolo
    gem = gematria_italiano(simbolo_principale)
    radice = radice_digitale(gem)
    sefirah = SEFIROT.get(radice, SEFIROT[1])

    righe = []
    for i, grado in enumerate(CINQUE_GRADI, start=1):
        if grado.nome_ebraico == "Tiqun":
            applicazione = "[silenzio] — il significato ultimo sfugge alla parola"
        elif grado.nome_ebraico == "Tzeruf":
            applicazione = f"'{simbolo_principale}' permutato = '{permutazione}' — l'ombra del simbolo"
        elif grado.nome_ebraico == "Ma'amar":
            acrostico = " · ".join(f"{c.upper()}-" for c in s if c.isalpha())
            applicazione = f"Acrostico: {acrostico[:60]}"
        elif grado.nome_ebraico == "Mikhlol":
            applicazione = f"Nel contesto '{tema_sogno[:40]}…': il simbolo trasforma il tema"
        else:  # Cheshbon
            applicazione = (
                f"Gematria '{simbolo_principale}' = {gem} → radice {radice} → "
                f"{sefirah.nome_ebraico} ({sefirah.nome_italiano})"
            )
        righe.append(
            f"  {i}. {grado.nome_ebraico} ({grado.traduzione} / {grado.sefirah})\n"
            f"     {applicazione}"
        )
    return righe


# ---------------------------------------------------------------------------
# Dataclass di output principale
# ---------------------------------------------------------------------------

@dataclass
class LetturaEstetica:
    """Lettura esoterica integrata: Sefer Yetzira + Semprini + Guénon + Sepharial + Ronchetti."""
    # Sefirah
    numero_chiave: int
    radice_digitale: int
    sefirah: Sefirah

    # Gematria
    gematria_sogno: int
    gematria_radice: int

    # Triade
    elem_shin: int
    elem_alef: int
    elem_mem: int
    elemento_dominante: Optional[str]
    lettera_madre: Optional[LetteraMadre]

    # Pianeta e Segno
    pianeta: Optional[str]
    segno: Optional[str]

    # Numeri sacri
    numeri_sacri: list[NumeroSacro]

    # Albero della Vita — sefirot attivate
    sefirot_attivate: set[int]

    # Guénon
    guenon: dict[str, str]

    # Cinque gradi
    cinque_gradi: list[str]

    # Simboli con elemento
    simboli_con_elemento: list[tuple[str, str]]

    # Sentiero principale (tra i 32)
    sentiero: int

    # Sepharial — The Kabala Of Numbers (1920)
    sepharial_cifra: Optional[SepharialNumero]       # cifra-unità del numero chiave
    sepharial_significato: Optional[str]              # significato Cap. XI (1-84)

    # Ronchetti — simboli dal dizionario
    ronchetti_note: list[tuple[str, str]]             # [(simbolo, nota Ronchetti), ...]


# ---------------------------------------------------------------------------
# Funzione di lettura principale
# ---------------------------------------------------------------------------

def leggi_sogno(
    testo_sogno: str,
    simboli_trovati: list[str],
    numeri_principali: list[int],
) -> LetturaEstetica:
    """Produce la lettura esoterica completa del sogno."""

    # Sefirah dal numero più forte
    numero_chiave = numeri_principali[0] if numeri_principali else 1
    radice = radice_digitale(numero_chiave)
    sefirah = SEFIROT.get(radice, SEFIROT[1])

    # Gematria
    gem = gematria_italiano(testo_sogno)
    gem_radice = radice_digitale(gem)

    # Triade
    tutte_parole = _normalizza(testo_sogno).split() + [_normalizza(s) for s in simboli_trovati]
    conteggio = _conta_triade(tutte_parole)
    shin = conteggio["fuoco"]
    alef = conteggio["aria"]
    mem = conteggio["acqua"]

    elemento_dom: Optional[str] = None
    if shin or alef or mem:
        elemento_dom = max(("fuoco", shin), ("aria", alef), ("acqua", mem), key=lambda x: x[1])[0]
        if max(shin, alef, mem) == 0:
            elemento_dom = None

    lettera_madre: Optional[LetteraMadre] = None
    if elemento_dom:
        chiave_lm = ELEMENTO_A_LETTERA.get(elemento_dom)
        if chiave_lm:
            lettera_madre = LETTERE_MADRI[chiave_lm]

    # Pianeta e segno dai simboli
    pianeta: Optional[str] = None
    segno: Optional[str] = None
    for parola in tutte_parole:
        if parola in SIMBOLO_A_PIANETA and not pianeta:
            pianeta = SIMBOLO_A_PIANETA[parola]
        if parola in SIMBOLO_A_SEGNO and not segno:
            segno = SIMBOLO_A_SEGNO[parola]

    # Numeri sacri
    ns = numeri_sacri_trovati(numeri_principali)

    # Sefirot attivate: quelle corrispondenti ai top numeri
    sefirot_attivate = {radice_digitale(n) for n in numeri_principali[:6]}
    sefirot_attivate.discard(0)

    # Guénon
    simboli_unici = list({s for s in simboli_trovati})[:6]
    guenon = guenon_lettura(testo_sogno, simboli_unici, elemento_dom, sefirah)

    # Cinque gradi: usa il primo simbolo come punto di lavoro
    simbolo_principale = simboli_trovati[0] if simboli_trovati else ""
    tema_sogno = testo_sogno[:50]
    cinque = cinque_gradi_testo(simbolo_principale, tema_sogno)

    # Simboli con elemento
    simboli_con_elem = []
    for s in simboli_trovati:
        el = SIMBOLO_A_ELEMENTO.get(_normalizza(s))
        if el:
            simboli_con_elem.append((s, el))

    # Sentiero (1-32): usa il numero chiave mod 32
    sentiero = numero_chiave % 32 or 32

    # Sepharial: cifra-unità e significato Cap. XI
    cifra_unita = radice_digitale(numero_chiave) if numero_chiave > 0 else 0
    sepharial_cifra = SEPHARIAL_CIFRE.get(cifra_unita)
    # Significato diretto 1-84 o tramite modulo 84
    if 1 <= numero_chiave <= 84:
        sepharial_sig = SEPHARIAL_SIGNIFICATI.get(numero_chiave)
    else:
        sig_key = numero_chiave % 84 or 84
        sepharial_sig = SEPHARIAL_SIGNIFICATI.get(sig_key)

    # Ronchetti: cerca le note per i simboli trovati
    ronchetti_note = []
    for s in simboli_trovati[:6]:
        chiave_r = _normalizza(s)
        nota_r = RONCHETTI_SIMBOLI.get(chiave_r)
        if nota_r:
            ronchetti_note.append((s, nota_r))

    return LetturaEstetica(
        numero_chiave=numero_chiave,
        radice_digitale=radice,
        sefirah=sefirah,
        gematria_sogno=gem,
        gematria_radice=gem_radice,
        elem_shin=shin,
        elem_alef=alef,
        elem_mem=mem,
        elemento_dominante=elemento_dom,
        lettera_madre=lettera_madre,
        pianeta=pianeta,
        segno=segno,
        numeri_sacri=ns,
        sefirot_attivate=sefirot_attivate,
        guenon=guenon,
        cinque_gradi=cinque,
        simboli_con_elemento=simboli_con_elem,
        sentiero=sentiero,
        sepharial_cifra=sepharial_cifra,
        sepharial_significato=sepharial_sig,
        ronchetti_note=ronchetti_note,
    )


# ---------------------------------------------------------------------------
# Formattazione dell'output
# ---------------------------------------------------------------------------

def formatta_lettura(lettura: LetturaEstetica) -> str:
    """Formatta la lettura esoterica completa come testo leggibile."""

    righe: list[str] = ["", "═" * 60]
    righe.append("  LETTURA ESOTERICA INTEGRATA")
    righe.append("  Sefer Yetzira · Semprini · Guénon · Sepharial · Ronchetti")
    righe.append("═" * 60)

    # ---- Guénon: tre livelli ----
    righe.append("")
    righe.append("── I TRE LIVELLI (Guénon) ──────────────────────────────")
    g = lettura.guenon
    righe.append("")
    righe.append("EXOTERICO  (lettera, portata di tutti):")
    righe.append("  " + g["exoterico"])
    righe.append("")
    righe.append("ESOTERICO  (senso più profondo, simbolico):")
    righe.append("  " + g["esoterico"])
    righe.append("")
    righe.append("METAFISICO (inesprimibile — Keter):")
    righe.append("  " + g["metafisico"])

    # ---- Sefirah ----
    sf = lettura.sefirah
    righe.append("")
    righe.append("── SEFIRAH ─────────────────────────────────────────────")
    righe.append(
        f"  Numero chiave {lettura.numero_chiave} → radice {lettura.radice_digitale} "
        f"→ {sf.nome_ebraico} ({sf.nome_italiano})"
    )
    righe.append(f"  Principio : {sf.principio}")
    righe.append(f"  Piano     : {sf.piano}  |  Opposto: {sf.opposto}")
    righe.append(f"  Patriarca : {sf.patriarca}")
    righe.append(f"  Guénon    : {sf.senso_guenon}")
    righe.append(
        f"  Gematria sogno = {lettura.gematria_sogno} "
        f"→ radice {lettura.gematria_radice} → {SEFIROT.get(lettura.gematria_radice, SEFIROT[1]).nome_ebraico}"
    )

    # ---- Triade dell'Anima ----
    righe.append("")
    righe.append("── TRIADE DELL'ANIMA (Sefer Yetzira cap. III) ──────────")
    righe.append(triade_anima_testo(lettura.elem_shin, lettura.elem_alef, lettura.elem_mem))
    if lettura.lettera_madre:
        lm = lettura.lettera_madre
        righe.append(f"  Lettera Madre dominante: {lm.lettera} {lm.traslitt} (valore {lm.valore})")
        righe.append(f"  Semprini: {lm.semprini_sintesi[:120]}…")

    # ---- Pianeta e Segno ----
    if lettura.pianeta or lettura.segno:
        righe.append("")
        righe.append("── PIANETA · SEGNO ─────────────────────────────────────")
        if lettura.pianeta:
            ld = next((l for l in LETTERE_DOPPIE.values() if l.pianeta == lettura.pianeta), None)
            if ld:
                righe.append(
                    f"  Pianeta: {lettura.pianeta} → {ld.lettera} {ld.traslitt} "
                    f"(valore {ld.valore}, {ld.giorno})"
                )
                righe.append(f"  Dono: {ld.dono}  |  Opposto: {ld.opposto}  |  {ld.porta_anima}")
                righe.append(f"  {ld.semprini_nota}")
        if lettura.segno:
            chiave_z = ZODIACO_A_LETTERA.get(lettura.segno.lower())
            if chiave_z:
                ls = LETTERE_SEMPLICI[chiave_z]
                righe.append(
                    f"  Segno: {lettura.segno} → {ls.lettera} {ls.traslitt} "
                    f"(valore {ls.valore}, {ls.mese_italiano})"
                )
                righe.append(f"  Organo: {ls.organo}  |  Senso: {ls.senso}")

    # ---- Numeri sacri ----
    if lettura.numeri_sacri:
        righe.append("")
        righe.append("── NUMERI SACRI ────────────────────────────────────────")
        for ns in lettura.numeri_sacri:
            righe.append(f"  {ns.valore} → {ns.nome}")
            righe.append(f"     {ns.significato[:120]}…" if len(ns.significato) > 120
                         else f"     {ns.significato}")
            righe.append(f"     Fonte: {ns.fonte}")

    # ---- Albero della Vita ----
    if lettura.sefirot_attivate:
        righe.append("")
        righe.append("── ALBERO DELLA VITA (nodi attivati ◉) ─────────────────")
        righe.append(albero_vita_testo(lettura.sefirot_attivate))

    # ---- Sentiero ----
    righe.append("")
    righe.append(
        f"── SENTIERO {lettura.sentiero:02d} / 32 ──────────────────────────────────────"
    )
    righe.append(
        f"  I 32 Sentieri della Sapienza = 10 Sefirot + 22 Lettere. "
        f"LEV = Cuore (L30 + V2 = 32). "
        f"32 = 2^5 (polarità × 5 dimensioni). "
        f"Elohim appare 32 volte nel Genesi."
    )

    # ---- Sepharial — The Kabala Of Numbers ----
    righe.append("")
    righe.append("── SEPHARIAL (1920) ─────────────────────────────────────")
    sc = lettura.sepharial_cifra
    if sc:
        righe.append(f"  Cifra {sc.cifra} → Pianeta: {sc.pianeta}")
        righe.append(f"  Chiave Maggiore: {sc.significato_maggiore[:120]}")
        righe.append(f"  Chiave Minore  : {sc.significato_minore}")
    if lettura.sepharial_significato:
        righe.append(f"  N. {lettura.numero_chiave} (Cap. XI): {lettura.sepharial_significato}")

    # ---- Ronchetti — simbolismo iconologico ----
    if lettura.ronchetti_note:
        righe.append("")
        righe.append("── RONCHETTI (1922) — Simbolismo ────────────────────────")
        for simbolo, nota in lettura.ronchetti_note:
            righe.append(f"  {simbolo.upper()}: {nota[:150]}")

    # ---- Cinque gradi ermeneutici ----
    if lettura.cinque_gradi:
        righe.append("")
        righe.append("── 5 GRADI ERMENEUTICI (Sefer Mayan Ha Chokhmà / Semprini) ─")
        for riga in lettura.cinque_gradi:
            righe.append(riga)

    righe.append("")
    righe.append("═" * 60)
    righe.append("")

    return "\n".join(righe)
