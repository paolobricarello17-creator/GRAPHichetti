import math
import pandas as pd
from svg import SVG, Circle, Path, Text, Rect


from initialize_graph import initialize_graph


def _get_modes(variable1):
    if isinstance(variable1, pd.DataFrame):
        series = variable1.iloc[:, 0]
    else:
        series = pd.Series(variable1)
    return series.dropna().mode().tolist()


def Grafico_torta(variable1, graph=None):
    """
    Genera un grafico a torta / ciambella in formato SVG mantendo la logica originale.
    """
    # Se l'utente non passa il dizionario configurato, lo inizializziamo qui
    if graph is None:
        graph = initialize_graph(variable1)

    # 1. Preparazione dati
    variable1_df = pd.DataFrame(variable1)
    freq = variable1_df.value_counts(sort=False)   # Categoria e conteggio
    category_name = list(zip(*freq.index))[0] 
    valori = freq.values.tolist()              # Frequenze
    n_categorie = len(freq) 
    n_osservazioni = sum(valori)
    moda = _get_modes(variable1)
    valore_massimo = max(valori) if max(valori) > 0 else 1

    # Parametri del cerchio (Torta centrata a sinistra per lasciare spazio ai KPI)
    cx, cy = 200, 200  # Centro del grafico
    raggio = 130       # Raggio della torta

    ## 2. Spicchi della Torta (Sostituiscono le barre) ##
    barre = [] # Chiamata 'barre' per mantenere la tua struttura di output finale
    
    # Calcolo delle percentuali e degli angoli
    angolo_corrente = -math.pi / 2 # Partiamo dall'alto (ore 12)

    for i in range(0, n_categorie):
        # Scelta del colore (Evidenzia lo spicchio della moda)
        if category_name[i] in moda and graph['highlight'] == True:
            fill = graph['colore 1'] 
        else: 
            fill = graph['colore 2'] 

        # Se c'è una sola categoria, fa un cerchio pieno direttamente
        if n_categorie == 1:
            barre.append(
                Circle(cx=cx, cy=cy, r=raggio, fill=fill, stroke="black", stroke_width=1.5)
            )
            continue

        # Calcolo ampiezza spicchio in radianti
        percentuale = valori[i] / n_osservazioni
        ampiezza_angolo = percentuale * 2 * math.pi

        # Coordinate punto iniziale e finale dello spicchio
        x1 = cx + raggio * math.cos(angolo_corrente)
        y1 = cy + raggio * math.sin(angolo_corrente)
        
        angolo_successivo = angolo_corrente + ampiezza_angolo
        x2 = cx + raggio * math.cos(angolo_successivo)
        y2 = cy + raggio * math.sin(angolo_successivo)

        # Flag per archi SVG maggiori di 180 gradi
        large_arc_flag = 1 if ampiezza_angolo > math.pi else 0

        # Costruzione del Path SVG dello spicchio
        path_d = f"M {cx} {cy} L {x1} {y1} A {raggio} {raggio} 0 {large_arc_flag} 1 {x2} {y2} Z"
        
        barre.append(
            Path(d=path_d, fill=fill, stroke="black", stroke_width=1.5)
        )

        # Aggiorna l'angolo per il prossimo spicchio
        angolo_corrente = angolo_successivo

    ## 3. Cerchio al centro (Donut hole) ##
    if graph['assi'] == True:
        assi = [
            Circle(cx=cx, cy=cy, r=55, fill="white", stroke="black", stroke_width=1.5)
        ]
    else:
        assi = []

    ## 4. Etichette delle Categorie (Legenda vicino agli spicchi) ##
    if graph['etichette assi'] == True:
        etichette_assi = []
        angolo_corrente = -math.pi / 2
        
        for i in range(0, n_categorie):
            percentuale = valori[i] / n_osservazioni
            ampiezza_angolo = percentuale * 2 * math.pi
            
            # Angolo centrale dello spicchio per posizionare il testo fuori
            angolo_testo = angolo_corrente + (ampiezza_angolo / 2)
            x_testo = cx + (raggio * 1.25) * math.cos(angolo_testo)
            y_testo = cy + (raggio * 1.25) * math.sin(angolo_testo)

            # Allineamento dinamico del testo in base a dove si trova
            if math.cos(angolo_testo) > 0.1:
                anchor = "start"
            elif math.cos(angolo_testo) < -0.1:
                anchor = "end"
            else:
                anchor = "middle"

            etichette_assi.append(
                Text(
                    x=x_testo,
                    y=y_testo + 4, 
                    elements=[str(category_name[i])],
                    text_anchor=anchor,
                    font_size=11,
                    font_family="Helvetica",
                    fill="black"
                )
            )
            angolo_corrente += ampiezza_angolo
    else: 
        etichette_assi = []

    ## 5. Valori dentro gli spicchi (Percentuali) ##
    if graph['valori'] == True:
        valori_barre = []
        angolo_corrente = -math.pi / 2
        
        for i in range(0, n_categorie):
            percentuale = valori[i] / n_osservazioni
            ampiezza_angolo = percentuale * 2 * math.pi
            
            # Angolo centrale dello spicchio, raggio intermedio per stare dentro
            angolo_valore = angolo_corrente + (ampiezza_angolo / 2)
            x_valore = cx + (raggio * 0.65) * math.cos(angolo_valore)
            y_valore = cy + (raggio * 0.65) * math.sin(angolo_valore)

            # Mostra la percentuale (es. "25%")
            testo_percentuale = f"{round(percentuale * 100, 1)}%"

            valori_barre.append(
                Text(
                    x=x_valore,
                    y=y_valore + 4,
                    elements=[testo_percentuale],
                    text_anchor="middle",
                    font_size=11,
                    font_family="Helvetica",
                    fill="black"
                )
            )
            angolo_corrente += ampiezza_angolo
    else: 
        valori_barre = []

    ### 6. KPI ###
    if graph['KPI'] == True:
        KPI = []
        voci_kpi = [
            f"N.osservazioni: {n_osservazioni}", 
            f"Moda: {moda[0]}", 
            f"N.osservazioni moda: {max(valori)}"
        ]

        if n_categorie > 1:
            for i in range(len(voci_kpi)):
                KPI.append( 
                    Text(
                        x=420,
                        y=200 + (10 * i),
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
                    y=200,
                    height=10,
                    width=10,
                    fill=graph['colore 1'],
                    stroke="black",
                    stroke_width=0.5
                )
            )
    else: 
        KPI = []
        
    # Output finale ordinato come impostato da te
    plot = SVG(
        width=600,
        height=400,
        elements=barre + assi + etichette_assi + valori_barre + KPI
    )
    return plot