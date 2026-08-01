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
_tokenizer = None
_model = None

def _carica_modello(model="Paolobricarello17/graphichetti-it5"):
    global _tokenizer, _model
    if _model is None:
        print("[GRAPHichetti] Caricamento modello NLP da Hugging Face...")
        _tokenizer = AutoTokenizer.from_pretrained(model)
        _model = AutoModelForSeq2SeqLM.from_pretrained(model)
        
        # Sposta su GPU se disponibile per velocizzare l'esecuzione
        if torch.cuda.is_available():
            _model.to("cuda")
            
    return _tokenizer, _model


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

    # 3. Normalizzazione Tipi (Stringhe -> Booleani / Numeri + Correzione Refusi)
    parametri_puliti = {}
    for k, v in parametri.items():
        v_str = str(v).lower().strip()
        
        if v_str in ["true", "rue"]:
            parametri_puliti[k] = True
        elif v_str in ["false", "alse", "lse"]:
            parametri_puliti[k] = False
        elif v_str in ["none", "null", ""]:
            continue
        else:
            parametri_puliti[k] = v

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


def modifica_grafico(prompt, graph, model="Paolobricarello17/graphichetti-it5"):
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

    if nuovi_parametri:
        graph.update(nuovi_parametri)
        print(f"[GRAPHichetti] Modifiche applicate con successo: {nuovi_parametri}")
    else:
        print("[GRAPHichetti Warning] Nessuna modifica rilevata nella frase.")

    # Ridisegno e visualizzazione
    plot_svg = _disegna(graph)
    _mostra_grafico(plot_svg)
    return graph