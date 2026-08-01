import pandas as pd
from svg import SVG, Rect, Line, Text


from .initialize_graph import initialize_graph


def _get_modes(variable1):
    """Funzione di supporto interna per calcolare la moda"""
    variable1 = pd.DataFrame(variable1)
    freq = variable1.value_counts()
    max_f = freq.max()
    mode_index = freq[freq == max_f].index.tolist()
    modes = list(zip(*mode_index))[0] 
    return modes


def Grafico_barre(variable1, graph=None):
    """
    Genera un grafico a barre in formato SVG.
    Input:
        - variable1: i dati da analizzare (es. lista o colonna pandas)
        - graph: (Opzionale) il dizionario con le impostazioni del grafico. 
                 Se omesso, viene inizializzato automaticamente.
    """
    # Se l'utente non passa il dizionario 'graph', lo generiamo automaticamente dai dati
    if graph is None:
        graph = initialize_graph(variable1)
        
    # Leggi la variabile e prendi i dati 
    variable1 = pd.DataFrame(variable1)
    freq = variable1.value_counts(sort=False)   # freq è una tabella con categoria e conteggio 
    category_name = list(zip(*freq.index))[0] 
    valori = freq.values.tolist()                # valori è una lista [freq1, freq2 ecc]
    n_categorie = len(freq) 
    n_osservazioni = sum(valori)
    moda = _get_modes(variable1)
    valore_massimo = max(valori) if max(valori) > 0 else 1
    altezza_max_grafico = 320

    # ==========================================
    # 1. ASSI
    # ==========================================
    if graph.get('assi') == True:
        assi = [
            Line(x1=10, y1=10, x2=10, y2=380, stroke="black", stroke_width=1.5, stroke_opacity=1),
            Line(x1=10, y1=380, x2=590, y2=380, stroke="black", stroke_width=2, stroke_opacity=1)
        ]
    else: 
        assi = []

    # ==========================================
    # 2. ETICHETTE ASSI
    # ==========================================
    if graph.get('etichette_assi') == True:
        etichette_assi = []
        for i in range(0, n_categorie):
            x_centro = 10 + (i + 1) * (580 / (n_categorie + 1))
            etichette_assi.append(
                Text(
                    x=x_centro,
                    y=395,
                    elements=[str(category_name[i])],
                    text_anchor="middle",
                    font_size=12,
                    font_family="Helvetica",
                    fill="black"
                )
            )               
    else: 
        etichette_assi = []

    # ==========================================
    # 3. VALORI BARRE
    # ==========================================
    if graph.get('valori') == True:
        valori_barre = []
        for i in range(0, n_categorie):
            x = 10 + (i + 1) * (580 / (n_categorie + 1))               
            y = 380 - ((valori[i] / valore_massimo) * altezza_max_grafico) - 5 
            valori_barre.append(
                Text(
                    x=x,
                    y=y,
                    elements=[str(valori[i])],
                    text_anchor="middle",
                    font_size=12,
                    font_family="Helvetica",
                    fill="black"
                )
            )               
    else: 
        valori_barre = []

    # ==========================================
    # 4. BARRE
    # ==========================================
    barre = []
    base = 380
    larghezza = 300 / n_categorie
    spessore_bordo = 2 * graph.get('bordi', 1)
    for i in range(0, n_categorie):
        if category_name[i] in moda and graph.get('highlight') == True:
            fill = graph.get('colore1')
        else:
            fill = graph.get('colore2')

        altezza = (valori[i] / valore_massimo) * altezza_max_grafico
        barre.append(
            Rect(
                x=10 + (i + 1) * (580 / (n_categorie + 1)) - (larghezza / 2),
                y=base - altezza,
                height=altezza,
                width=larghezza,
                fill=fill,
                stroke="black",
                stroke_width=spessore_bordo
            )
        )

    # ==========================================
    # 5. KPI
    # ==========================================
    if graph.get('kpi') == True and n_categorie > 1:
        KPI = []
        voci_kpi = [
            f"N.osservazioni: {n_osservazioni}", 
            f"Moda: {moda[0]}", 
            f"N.osservazioni moda: {max(valori)}"
        ]

        for i in range(len(voci_kpi)):
            KPI.append( 
                Text(
                    x=420,
                    y=20 + (15 * i), # Ho aumentato leggermente il passo da 10 a 15 per non sovrapporre il testo
                    elements=[str(voci_kpi[i])],
                    text_anchor="start", # "left" non è standard SVG, meglio "start"
                    font_size=12,
                    font_family="Arial",
                    fill="black"
                )
            )

        # Il quadratino del colore KPI lo mettiamo una volta sola fuori dal loop del testo
        KPI.append(
            Rect(
                x=400,
                y=12,
                height=10,
                width=10,
                fill=graph.get('colore1'),
                stroke="black",
                stroke_width=0.5
            )
        )
    else: 
        KPI = []
        
    # ==========================================
    # 6. COSTRUZIONE PLOT FINALE
    # ==========================================
    plot = SVG(
        width=600,
        height=400,
        elements=assi + barre + etichette_assi + valori_barre + KPI
    )
    
    return plot