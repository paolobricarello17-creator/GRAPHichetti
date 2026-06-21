import math
import pandas as pd
from svg import SVG, Line, Text, Rect


from .initialize_graph import initialize_graph


def Istogramma(variable1, graph=None):
    """
    Genera un istogramma per variabili quantitative in formato SVG mantenendo la logica originale.
    """
    # Se l'utente non passa il dizionario configurato, lo inizializziamo qui dove variable1 esiste
    if graph is None:
        graph = initialize_graph(variable1)

    # 1. Preparazione dati (Quantitative)
    variable1_df = pd.DataFrame(sorted(variable1))
    n_osservazioni = len(variable1_df)
    
    # Calcolo numero di split (bins)
    if graph["numero split"] is False or graph["numero split"] == False:
        n_bins = int(math.ceil(math.log2(n_osservazioni) + 1))  # Regola di Sturges
    else:
        n_bins = int(graph['numero split'])

    # Creazione intervalli e conteggio frequenze
    bins_series = pd.cut(variable1_df.iloc[:, 0], bins=n_bins)
    freq = bins_series.value_counts(sort=False)
    
    # Formattazione intervalli per le etichette assi (es. "10.5-20.1")
    category_name = [f"{round(interval.left, 1)}-{round(interval.right, 1)}" for interval in freq.index]
    valori = freq.values.tolist()
    valore_massimo = max(valori) if max(valori) > 0 else 1
    n_categorie = len(valori)
    max_f = max(valori)
    
    # Calcolo della moda basato sulle frequenze degli intervalli
    moda_indices = [i for i, v in enumerate(valori) if v == max_f]
    nomi_moda = [category_name[i] for i in moda_indices]

    altezza_max_grafico = 320
    base = 380
    
    # Larghezza dinamica per far sì che le barre siano adiacenti
    larghezza_totale = 580
    larghezza_barra = larghezza_totale / n_categorie

    ## 2. Assi ##
    if graph['assi'] == True:
        assi = [
            Line(x1=10, y1=10, x2=10, y2=base, stroke="black", stroke_width=1.5, stroke_opacity=1),
            Line(x1=10, y1=base, x2=590, y2=base, stroke="black", stroke_width=2, stroke_opacity=1)
        ]
    else:
        assi = []

    ## 3. Etichette Assi (Intervalli) ##
    if graph['etichette assi'] == True:
        etichette_assi = []
        for i in range(n_categorie):
            x_centro = 10 + (i * larghezza_barra) + (larghezza_barra / 2)
            etichette_assi.append(
                Text(
                    x=x_centro, 
                    y=395, 
                    elements=[category_name[i]], 
                    text_anchor="middle", 
                    font_size=12,
                    font_family="Helvetica",
                    fill="black"
                )
            )
    else:
        etichette_assi = []

    ## 4. Valori sopra le barre ##
    if graph['valori'] == True:
        valori_barre = []
        for i in range(n_categorie):
            x_centro = 10 + (i * larghezza_barra) + (larghezza_barra / 2)
            altezza = (valori[i] / valore_massimo) * altezza_max_grafico
            y_pos = base - altezza - 5
            valori_barre.append(
                Text(
                    x=x_centro, 
                    y=y_pos, 
                    elements=[str(valori[i])], 
                    text_anchor="middle", 
                    font_size=12,
                    font_family="Helvetica",
                    fill="black"
                )
            )
    else:
        valori_barre = []

    ## 5. Barre (Istogramma: adiacenti) ##
    barre = []
    for i in range(n_categorie):
        if category_name[i] in nomi_moda and graph['highlight'] == True:
            fill = graph['colore 1']
        else:
            fill = graph['colore 2']
            
        altezza = (valori[i] / valore_massimo) * altezza_max_grafico
        
        barre.append(
            Rect(
                x=10 + (i * larghezza_barra),
                y=base - altezza,
                height=altezza,
                width=larghezza_barra,
                fill=fill,
                stroke="black",
                stroke_width=2
            )
        )

    ## 6. KPI ##
    if graph['KPI'] == True:
        KPI = []
        voci_kpi = [
            f"N.osservazioni: {n_osservazioni}", 
            f"Classe Modale: {nomi_moda[0]}", 
            f"Freq. Max: {max_f}"
        ]
        
        if n_categorie > 1:
            # 1. Scrittura del testo con spaziatura ridotta (identica a barchart)
            for i in range(len(voci_kpi)):
                KPI.append( 
                    Text(
                        x=420,
                        y=20 + (10 * i),   # Spaziatura passo 10px coordinata con barchart
                        elements=[str(voci_kpi[i])],
                        text_anchor="start",
                        font_size=12,
                        font_family="Arial",
                        fill="black"
                    )
                )
            
            # 2. Unico quadratino di legenda per il colore di highlight
            KPI.append(
                Rect(
                    x=400,
                    y=20,
                    height=10,
                    width=10,
                    fill=graph['colore 1'],
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