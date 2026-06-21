
import pandas as pd


# Importiamo le funzioni di controllo dal pacchetto GRAPHici
from .GRAPHici.detect_graph_type import detect_graph_type
from .GRAPHici.initialize_graph import initialize_graph

# Importiamo i moduli dei singoli grafici
from .GRAPHici.Bar_plot import Bar_plot
from .GRAPHici.Pie_chart import Grafico_torta
from .GRAPHici.Hist_chart import Istogramma
from .GRAPHici.Scatter_plot import Scatterplot
from .GRAPHici.Composed_barchart import Composed_barchart


def crea_grafico(variable1, variable2=None, graph=None):
    """
    Funzione principale (Regista):
    1. Rileva il tipo di grafico e inizializza la configurazione (se non passata).
    2. Smista i dati alla funzione di disegno corretta.
    """
    # Se l'utente non passa un dizionario di configurazione personalizzato,
    # lo creiamo sul momento (il quale imposterà anche il "graph_type")
    if graph is None:
        graph = initialize_graph(variable1, variable2)
    
    # Recuperiamo il tipo di grafico rilevato
    tipo_grafico = graph.get("graph_type")
    
    # Smistamento (Dispatching) al modulo corretto
    if tipo_grafico == "bar":
        return Bar_plot(variable1, graph)
        
    elif tipo_grafico == "pie":
        return Grafico_torta(variable1, graph)
        
    elif tipo_grafico == "histogram":
        return Istogramma(variable1, graph)
        
    elif tipo_grafico == "scatterplot":
        return Scatterplot(variable1, variable2, graph)
        
    elif tipo_grafico == "composed_barchart":
        return Composed_barchart(variable1, variable2, graph)
        
    else:
        raise ValueError(f"Tipo di grafico '{tipo_grafico}' non supportato o non riconosciuto.")