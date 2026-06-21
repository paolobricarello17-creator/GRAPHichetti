from .detect_graph_type import detect_graph_type as dgt
import pandas as pd

#funzisone che inizializza l'oggetto grafico, l'ho tenuta in un file a parte per porte modificare i predefined settings 
def initialize_graph(variable1, variable2=None):
    graph = {
        "graph_type": dgt(variable1, variable2),
        "colore 1": "#FFD151",
        "colore 2": "white",
        "etichette assi": True,
        "valori": True , 
        "numero split": False,
        "bordi": 1 ,
        "assi": True,
        "highlight": True, 
        "KPI": True
    }
    return graph
