#funzisone che inizializza l'oggetto grafico, l'ho tenuta in un file a parte per porte modificare i predefined settings 
from .detect_graph_type import detect_graph_type as dgt
import pandas as pd

# Funzione che inizializza l'oggetto grafico e salva i dati in memoria
def initialize_graph(variable1, variable2=None):
    graph = {
        "graph_type": dgt(variable1, variable2), # Rilevamento automatico!
        
        # --- NUOVE CHIAVI NASCOSTE ---
        "_data_v1": variable1,  # Memorizza i dati (es. asse x o valori interi)
        "_data_v2": variable2,  # Memorizza i dati (es. asse y o etichette)
        # -----------------------------

        # --- IMPOSTAZIONI PREDEFINITE (con underscore per matchare l'AI) ---
        "colore 1": "#FFD151",
        "colore 2": "white",
        "etichette assi": True,
        "valori": True, 
        "numero split": False,
        "bordi": 1,
        "assi": True,
        "highlight": True, 
        "KPI": True
    }
    return graph
