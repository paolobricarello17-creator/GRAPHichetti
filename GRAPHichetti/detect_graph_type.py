
import pandas as pd

def detect_graph_type(variable1, variable2=None):
    """
    Rileva automaticamente il tipo di grafico ideale in base alla natura dei dati.
    """
    # Convertiamo in Series per analizzare i tipi di dati di Pandas
    s1 = pd.Series(variable1)
    
    # CASO 1: Due variabili (Analisi bivariata)
    if variable2 is not None:
        s2 = pd.Series(variable2)
        # Se sono entrambe numeriche -> Scatterplot
        if pd.api.types.is_numeric_dtype(s1) and pd.api.types.is_numeric_dtype(s2):
            return "scatterplot"
        else:
            return "composed_barchart"
            
    # CASO 2: Una sola variabile (Analisi univariata)
    else:
        # Se è numerica/quantitativa -> Istogramma
        if pd.api.types.is_numeric_dtype(s1):
            return "histogram"
        # Se è qualitativa/categorica (stringhe, booleani, object)
        else:
            # Se ha pochissime categorie (es. <= 3) possiamo usare la torta, altrimenti barre
            if s1.nunique() <= 3:
                return "pie"
            else:
                return "bar"