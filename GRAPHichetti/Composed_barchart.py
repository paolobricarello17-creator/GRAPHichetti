
import pandas as pd
from svg import SVG, Rect, Line, Text

from .initialize_graph import initialize_graph


def Grafico_barre_composto(variable1, variable2, graph=None):

    # Se l'utente non passa il dizionario configurato, lo inizializziamo qui dove variable1 esiste
    if graph is None:
        graph = initialize_graph(variable1)

    # 1. Preparazione dati (Bivariata: Tabella di contingenza/Frequenze incrociate)
    df = pd.DataFrame({'v1': variable1, 'v2': variable2}).dropna()
    n_osservazioni = len(df)
    
    # Creazione della matrice delle frequenze (Righe = Barre, Colonne = Strati)
    ct = pd.crosstab(df['v1'], df['v2'])
    categories = ct.index.tolist()      # Nomi delle barre (Variabile 1)
    strata = ct.columns.tolist()        # Segmenti interni (Variabile 2)
    n_categorie = len(categories)
    
    # Calcolo dei totali per ogni barra per la scalatura dell'asse Y
    totali_barre = ct.sum(axis=1).tolist()
    valore_massimo = max(totali_barre) if max(totali_barre) > 0 else 1

    # Calcolo KPI richiesti
    barra_piu_alta = ct.sum(axis=1).idxmax()
    
    # Trova la combinazione più frequente assoluta
    matrice_stacked = ct.stack()
    comb_piu_frequente = matrice_stacked.idxmax() # Ritorna una tupla (val1, val2)
    max_elementi_comb = matrice_stacked.max()
    stringa_combinazione = f"{comb_piu_frequente[0]}/{comb_piu_frequente[1]}"

    # Parametri geometrici (Stile barchart con leggero spazio tra le barre)
    altezza_max_grafico = 320
    base = 380
    larghezza_totale = 580
    larghezza_slot = larghezza_totale / n_categorie
    larghezza_barra = larghezza_slot * 0.8  # 80% dello spazio per la barra, 20% spazio vuoto

    ## 2. Assi ##
    if graph['assi'] == True:
        assi = [
            Line(x1=10, y1=10, x2=10, y2=base, stroke="black", stroke_width=1.5, stroke_opacity=1),
            Line(x1=10, y1=base, x2=590, y2=base, stroke="black", stroke_width=2, stroke_opacity=1)
        ]
    else:
        assi = []

    ## 3. Etichette Assi (Categorie della Variabile 1) ##
    if graph['etichette_assi'] == True:
        etichette_assi = []
        for i in range(n_categorie):
            x_centro = 10 + (i * larghezza_slot) + (larghezza_slot / 2)
            etichette_assi.append(
                Text(
                    x=x_centro, 
                    y=395, 
                    elements=[str(categories[i])], 
                    text_anchor="middle", 
                    font_size=12, 
                    font_family="Helvetica",
                    fill="black"
                )
            )
    else:
        etichette_assi = []

    ## 4. Valori sopra le barre (Solo il TOTALE di ogni barra) ##
    if graph['valori'] == True:
        valori_barre = []
        for i in range(n_categorie):
            x_centro = 10 + (i * larghezza_slot) + (larghezza_slot / 2)
            
            # Altezza totale della barra combinata
            altezza_totale_calc = (totali_barre[i] / valore_massimo) * altezza_max_grafico
            y_pos = base - altezza_totale_calc - 5
            
            valori_barre.append(
                Text(
                    x=x_centro, 
                    y=y_pos, 
                    elements=[str(totali_barre[i])], 
                    text_anchor="middle", 
                    font_size=12, 
                    font_family="Helvetica",
                    fill="black"
                )
            )
    else:
        valori_barre = []

    ## 5. Barre Stratificate (Fascia massima evidenziata per singola barra) ##
    barre = []
    for i in range(n_categorie):
        x_pos = 10 + (i * larghezza_slot) + (larghezza_slot * 0.1) 
        valori_strati_barra = ct.iloc[i].tolist()
        max_strato_locale = max(valori_strati_barra) if max(valori_strati_barra) > 0 else -1
        y_corrente = base
        highlight_fatto = False 
        
        for j in range(len(strata)):
            valore_strato = valori_strati_barra[j]
            if valore_strato == 0:
                continue 
                
            altezza_strato = (valore_strato / valore_massimo) * altezza_max_grafico
            y_pos_strato = y_corrente - altezza_strato
            
            if valore_strato == max_strato_locale and not highlight_fatto and graph['highlight'] == True:
                fill = graph['colore1']
                highlight_fatto = True 
            else:
                fill = graph['colore2']
            
            barre.append(
                Rect(
                    x=x_pos,
                    y=y_pos_strato,
                    height=altezza_strato,
                    width=larghezza_barra,
                    fill=fill,
                    stroke="black",
                    stroke_width=1.5
                )
            )
            y_corrente = y_pos_strato

    ## 6. KPI ##
    if graph['kpi'] == True:
        KPI = []
        voci_kpi = [
            f"Barra più alta: {barra_piu_alta}", 
            f"Comb. Top: {stringa_combinazione}", 
            f"Elementi Comb: {max_elementi_comb}"
        ]
        
        if n_categorie > 1:
            for i in range(len(voci_kpi)):
                KPI.append( 
                    Text(
                        x=420,
                        y=20 + (10 * i),
                        elements=[str(voci_kpi[i])],
                        text_anchor="start",
                        font_size=12,
                        font_family="Arial",
                        fill="black"
                    )
                )
            
            KPI.append(
                Rect(
                    x=400,
                    y=20,
                    height=10,
                    width=10,
                    fill=graph['colore1'],
                    stroke="black",
                    stroke_width=0.5
                )
            )
    else:
        KPI = []

    # Output finale
    plot = SVG(
        width=600,
        height=400,
        elements=assi + barre + etichette_assi + valori_barre + KPI
    )
    return plot