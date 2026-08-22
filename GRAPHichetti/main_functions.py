import pandas as pd
import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IPython.display import display, SVG

# Importiamo le funzioni di controllo dal pacchetto GRAPHici
from .detect_graph_type import detect_graph_type
from .initialize_graph import initialize_graph

# Importiamo i moduli dei singoli grafici
from .Bar_plot import Grafico_barre
from .Pie_chart import Grafico_torta
from .Hist_chart import Istogramma
from .Scatter_plot import Scatterplot
from .Composed_barchart import Grafico_barre_composto

# ==========================================
# GESTIONE MODELLO NLP
# ==========================================

# Nomi brevi selezionabili per il parametro 'model' di modifica_grafico,
# mappati sui rispettivi repo Hugging Face. Se 'model' non e' tra questi
# preset, viene usato cosi' com'e' come id di repo HF (permette di puntare
# a un modello non ancora elencato qui).
_MODELLI_PRESET = {
    "it5": "Paolobricarello17/graphichetti-it5",
    "bert": "Paolobricarello17/graphichetti-BERT",
}

_MODELLO_DEFAULT = "it5"

# Cache dei modelli gia' caricati (repo id risolto -> (tokenizer, modello)),
# cosi' si possono usare piu' modelli nella stessa sessione senza che uno
# scavalchi la cache dell'altro.
_modelli_caricati = {}


def _risolvi_modello(model):
    chiave = str(model).strip().lower()
    return _MODELLI_PRESET.get(chiave, model)


def _carica_modello(model=_MODELLO_DEFAULT):
    repo_id = _risolvi_modello(model)
    if repo_id not in _modelli_caricati:
        print(f"[GRAPHichetti] Caricamento modello NLP da Hugging Face ({repo_id})...")
        tokenizer = AutoTokenizer.from_pretrained(repo_id)
        modello = AutoModelForSeq2SeqLM.from_pretrained(repo_id)

        # Sposta su GPU se disponibile per velocizzare l'esecuzione
        if torch.cuda.is_available():
            modello.to("cuda")

        _modelli_caricati[repo_id] = (tokenizer, modello)

    return _modelli_caricati[repo_id]


# Chiavi impostabili in 'graph' (vedi initialize_graph.py). Il modello NLP
# a volte genera varianti minori (underscore/spazi/maiuscole) rispetto a
# queste: _normalizza_chiave le riconduce alla forma canonica.
_CHIAVI_CANONICHE = [
    "colore1", "colore2", "etichette_assi", "valori",
    "numero_split", "bordi", "assi", "highlight", "kpi", "graph_type",
]


def _normalizza_chiave(k):
    """Ritorna None se k non corrisponde a nessuna chiave canonica, invece
    di lasciarla passare invariata: una chiave inventata non deve finire
    dentro 'graph' (nessun renderer la leggerebbe comunque, ma sporcherebbe
    lo stato per sempre)."""
    k_pulita = k.strip().lower().replace(" ", "").replace("_", "")
    for canonica in _CHIAVI_CANONICHE:
        if canonica.replace("_", "") == k_pulita:
            return canonica
    return None


# Tipi di grafico validi (vedi detect_graph_type.py). Il modello NLP a volte
# genera sinonimi/abbreviazioni (es. 'scatter' invece di 'scatterplot'):
# _normalizza_tipo_grafico li riconduce al tipo canonico.
_SINONIMI_TIPO_GRAFICO = {
    "bar": "bar", "barre": "bar", "barchart": "bar",
    "pie": "pie", "torta": "pie", "piechart": "pie",
    "histogram": "histogram", "istogramma": "histogram", "hist": "histogram",
    "scatterplot": "scatterplot", "scatter": "scatterplot", "dispersione": "scatterplot",
    "composedbarchart": "composed_barchart", "barrecomposte": "composed_barchart",
    "composed": "composed_barchart", "barrestratificate": "composed_barchart",
    "stackedbar": "composed_barchart", "stackedbarchart": "composed_barchart",
}


def _normalizza_tipo_grafico(valore):
    v_pulito = str(valore).strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    return _SINONIMI_TIPO_GRAFICO.get(v_pulito, valore)


# Nomi colore italiani (quelli che il modello NLP tende a generare) mappati
# sull'equivalente hex, per colore1/colore2. Se il valore e' gia' un hex
# valido o un nome colore CSS/SVG (es. 'red') resta invariato: SVG lo
# interpreta correttamente da solo.
_COLORI_NOME_HEX = {
    "rosso": "#FF0000", "verde": "#008000", "blu": "#0000FF",
    "giallo": "#FFD151", "arancione": "#FFA500", "viola": "#800080",
    "rosa": "#FFC0CB", "nero": "#000000", "bianco": "#FFFFFF",
    "grigio": "#808080", "marrone": "#8B4513", "azzurro": "#00BFFF",
    "ciano": "#00FFFF", "magenta": "#FF00FF", "oro": "#FFD700",
    "argento": "#C0C0C0", "turchese": "#40E0D0", "indaco": "#4B0082",
    "beige": "#F5F5DC",
}

_HEX_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_ALPHA_PATTERN = re.compile(r"^[a-zA-Z]+$")


def _normalizza_colore(valore):
    """Ritorna None se valore non e' riconoscibile come colore, invece di
    lasciarlo passare invariato: a differenza di un tipo di grafico
    invalido (che fallisce a _disegna e fa scattare il rollback gia'
    presente in modifica_grafico), un colore invalido verrebbe scritto
    silenziosamente in 'graph' e comparirebbe rotto nell'SVG senza che
    nulla se ne accorga."""
    v = str(valore).strip()
    if _HEX_PATTERN.match(v):
        return v
    mappato = _COLORI_NOME_HEX.get(v.lower())
    if mappato is not None:
        return mappato
    if _ALPHA_PATTERN.match(v):
        # Non e' uno dei nomi italiani noti, ma e' comunque una singola
        # parola alfabetica: potrebbe essere un nome colore CSS/SVG valido
        # (es. 'red', 'salmon') che SVG interpreta da solo - lo lasciamo
        # passare come da intento originale del commento sopra.
        return v
    return None


def _normalizza_numero_split(valore):
    """numero_split deve essere False (fasce automatiche) o un intero
    positivo (numero di fasce). Il modello a volte genera True: non e' un
    numero di fasce valido (Hist_chart.py farebbe int(True) = 1 fascia
    sola), quindi in quel caso la modifica viene scartata invece di
    rompere silenziosamente l'istogramma."""
    if isinstance(valore, bool):
        # bool e' sottotipo di int in Python (int(True) == 1): va intercettato
        # esplicitamente, altrimenti 'True' passerebbe come se fosse 1 fascia.
        return False if valore is False else None
    try:
        n = int(valore)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def _parse_output_modello(pred_str):
    """
    Parser Universale Anti-Crash:
    Gestisce sia output JSON che output in formato chiave:valore (IT5).
    """
    parametri = {}
    
    # 1. Tentativo JSON
    match = re.search(r'\{.*\}', pred_str, re.DOTALL)
    if match:
        try:
            parametri = json.loads(match.group(0))
        except Exception:
            parametri = {}
            
    # 2. Tentativo Chiave:Valore (se JSON fallisce)
    if not parametri:
        for item in pred_str.split(","):
            if ":" in item:
                parts = item.split(":", 1)
                parametri[parts[0].strip()] = parts[1].strip()

    # 3. Normalizzazione Chiavi + Tipi (Stringhe -> Booleani / Numeri + Correzione Refusi)
    parametri_puliti = {}
    for k, v in parametri.items():
        chiave = _normalizza_chiave(k)
        if chiave is None:
            print(f"[GRAPHichetti Warning] Chiave sconosciuta ('{k}'), modifica ignorata.")
            continue
        v_str = str(v).lower().strip()

        if v_str in ["true", "rue"]:
            valore = True
        elif v_str in ["false", "alse", "lse"]:
            valore = False
        elif v_str in ["none", "null", ""]:
            continue
        elif chiave in ("colore1", "colore2"):
            valore = _normalizza_colore(v)
            if valore is None:
                print(f"[GRAPHichetti Warning] Valore colore non valido ('{v}') per '{chiave}', modifica ignorata.")
                continue
        else:
            valore = v

        if chiave == "numero_split":
            valore = _normalizza_numero_split(valore)
            if valore is None:
                print(f"[GRAPHichetti Warning] Valore 'numero_split' non valido ('{v}'), modifica ignorata.")
                continue

        parametri_puliti[chiave] = valore

    return parametri_puliti


# ==========================================
# FUNZIONI PRINCIPALI
# ==========================================

def _disegna(graph):
    """Dispatcher interno: legge dati e tipo dal dizionario 'graph' e produce l'SVG del grafico."""
    v1 = graph.get("_data_v1")
    v2 = graph.get("_data_v2")

    if v1 is None:
        raise ValueError("Dati originali non trovati nel dizionario 'graph'.")

    tipo_grafico = graph.get("graph_type")

    if tipo_grafico == "bar":
        return Grafico_barre(v1, graph)
    elif tipo_grafico == "pie":
        return Grafico_torta(v1, graph)
    elif tipo_grafico == "histogram":
        return Istogramma(v1, graph)
    elif tipo_grafico == "scatterplot":
        return Scatterplot(v1, v2, graph)
    elif tipo_grafico == "composed_barchart":
        return Grafico_barre_composto(v1, v2, graph)
    else:
        raise ValueError(f"Tipo di grafico '{tipo_grafico}' non supportato.")


def _mostra_grafico(plot_svg):
    """Mostra l'SVG del grafico inline in un notebook Jupyter."""
    display(SVG(str(plot_svg)))


def crea_grafico(variable1, variable2=None):
    """Funzione Regista: Inizializza lo stato, disegna e mostra il grafico. Ritorna il dizionario 'graph'."""
    graph = initialize_graph(variable1, variable2)
    plot_svg = _disegna(graph)
    _mostra_grafico(plot_svg)
    return graph


def visualizza_grafico(graph):
    """Ridisegna e mostra il grafico a partire dal dizionario 'graph', senza modificarlo."""
    plot_svg = _disegna(graph)
    _mostra_grafico(plot_svg)


def modifica_grafico(prompt, graph, model=_MODELLO_DEFAULT):
    """Accetta un prompt vocale/testuale, aggiorna il dizionario 'graph' e ridisegna."""
    tokenizer, nlp_model = _carica_modello(model)
    device = next(nlp_model.parameters()).device

    # Inferenza
    input_txt = "estrai parametri json: " + str(prompt)
    inputs = tokenizer(input_txt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = nlp_model.generate(**inputs, max_length=128)
    pred_str = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Estrazione parametri con il parser universale
    nuovi_parametri = _parse_output_modello(pred_str)

    if "graph_type" in nuovi_parametri:
        nuovi_parametri["graph_type"] = _normalizza_tipo_grafico(nuovi_parametri["graph_type"])

    if nuovi_parametri:
        graph_precedente = dict(graph)
        graph.update(nuovi_parametri)
        try:
            plot_svg = _disegna(graph)
        except Exception as e:
            # La modifica non e' disegnabile (es. tipo di grafico non valido
            # per questi dati): annulliamo per non lasciare 'graph' in uno
            # stato rotto, e ridisegniamo lo stato precedente.
            graph.clear()
            graph.update(graph_precedente)
            print(f"[GRAPHichetti Warning] Modifica annullata, il grafico resta quello precedente: {e}")
            plot_svg = _disegna(graph)
        else:
            print(f"[GRAPHichetti] Modifiche applicate con successo: {nuovi_parametri}")
    else:
        print("[GRAPHichetti Warning] Nessuna modifica rilevata nella frase.")
        plot_svg = _disegna(graph)

    _mostra_grafico(plot_svg)
    return graph