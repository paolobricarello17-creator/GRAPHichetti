import os
import sys
import pandas as pd
from scipy.stats import linregress
from svg import SVG, Line, Circle, Text, Rect

from initialize_graph import initialize_graph


def Scatterplot(variable1, variable2, graph=None):
    """
    Genera uno scatterplot bivariato con retta di regressione lineare 
    ed evidenziazione dinamica degli outlier in formato SVG.
    """
    # Se l'utente non passa il dizionario configurato, lo inizializziamo qui
    if graph is None:
        graph = initialize_graph(variable1)
        
    # 1. Preparazione Dati e Pulizia (Gestione NaN)
    df = pd.DataFrame({'x': variable1, 'y': variable2}).dropna()
    x_vals = df['x'].values
    y_vals = df['y'].values
    n_osservazioni = len(df)
    
    # Calcolo della Regressione Lineare
    slope, intercept, r_value, p_value, std_err = linregress(x_vals, y_vals)
    r_quadro = r_value ** 2
    
    # Calcolo dei residui per trovare gli outlier
    df['y_hat'] = slope * df['x'] + intercept
    df['residui'] = abs(df['y'] - df['y_hat'])
    
    # Identifichiamo dinamicamente i top outlier
    n_outliers = min(n_osservazioni, max(3, int(n_osservazioni * 0.05)))
    outliers_idx = df.nlargest(n_outliers, 'residui').index.tolist()

    # --- NUOVA LOGICA DI SCALING ---
    # 1. Calcolo dei limiti X con padding
    min_x_data, max_x_data = df['x'].min(), df['x'].max()
    pad_x = (max_x_data - min_x_data) * 0.05 if max_x_data > min_x_data else 1
    min_x = min_x_data - pad_x
    max_x = max_x_data + pad_x
    
    # 2. Estremi della retta di regressione sui bordi della X
    y_start = slope * min_x + intercept
    y_end = slope * max_x + intercept
    
    # 3. Calcolo limiti Y considerando SIA i dati reali SIA la retta
    min_y_data = min(df['y'].min(), y_start, y_end)
    max_y_data = max(df['y'].max(), y_start, y_end)
    
    # 4. Aggiunta del padding alla Y globale
    pad_y = (max_y_data - min_y_data) * 0.05 if max_y_data > min_y_data else 1
    min_y = min_y_data - pad_y
    max_y = max_y_data + pad_y
    # -------------------------------
    
    range_x = max_x - min_x
    range_y = max_y - min_y
    base = 380
    
    # Funzioni interne per mappare i valori reali sulle coordinate SVG
    def scale_x(val): return 10 + ((val - min_x) / range_x) * 580
    def scale_y(val): return base - ((val - min_y) / range_y) * 370 

    ## 2. Assi, Linee dello Zero e Retta di Regressione ##
    assi = []
    if graph['assi'] == True:
        assi.extend([
            Line(x1=10, y1=10, x2=10, y2=base, stroke="black", stroke_width=1.5, stroke_opacity=1),
            Line(x1=10, y1=base, x2=590, y2=base, stroke="black", stroke_width=2, stroke_opacity=1)
        ])
        
        # Linea per Y=0
        if min_y < 0 < max_y:
            y_zero = scale_y(0)
            assi.append(
                Line(x1=10, y1=y_zero, x2=590, y2=y_zero, 
                     stroke="gray", stroke_width=1, stroke_opacity=0.5, stroke_dasharray="4,4")
            )
            
        # Linea per X=0
        if min_x < 0 < max_x:
            x_zero = scale_x(0)
            assi.append(
                Line(x1=x_zero, y1=10, x2=x_zero, y2=base, 
                     stroke="gray", stroke_width=1, stroke_opacity=0.5, stroke_dasharray="4,4")
            )

    # Disegno della retta di regressione (usando 'colore 2')
    assi.append(
        Line(
            x1=scale_x(min_x), 
            y1=scale_y(y_start), 
            x2=scale_x(max_x), 
            y2=scale_y(y_end), 
            stroke="black", 
            stroke_width=2
        )
    )

    ## 3. Punti e Tratteggi degli Outlier ##
    barre = []
    for i in df.index:
        cx = scale_x(df.at[i, 'x'])
        cy = scale_y(df.at[i, 'y'])
        cy_hat = scale_y(df.at[i, 'y_hat'])
        
        is_outlier = (i in outliers_idx) and graph['highlight'] == True
        
        if is_outlier:
            barre.append(
                Line(
                    x1=cx, y1=cy, 
                    x2=cx, y2=cy_hat, 
                    stroke=graph['colore 1'], 
                    stroke_width=1.5, 
                    stroke_dasharray="4,4" 
                )
            )
            
        fill_color = graph['colore 1'] if is_outlier else "black"
        radius = 4 if is_outlier else 2.5 
        
        barre.append(
            Circle(
                cx=cx, cy=cy, r=radius, 
                fill=fill_color, 
                stroke="white" if not is_outlier else "black", 
                stroke_width=0.5
            )
        )

    ## 4. Etichette Assi (Estremi X) ##
    if graph['etichette assi'] == True:
        etichette_assi = [
            Text(x=scale_x(df['x'].min()), y=395, elements=[f"{df['x'].min():.1f}"], text_anchor="middle", font_size=10, font_family="Helvetica", fill="black"),
            Text(x=scale_x(df['x'].max()), y=395, elements=[f"{df['x'].max():.1f}"], text_anchor="middle", font_size=10, font_family="Helvetica", fill="black")
        ]
    else:
        etichette_assi = []

    ## 5. Valori Barre ##
    valori_barre = [] 

    ### 6. KPI ###
    if graph['KPI'] == True:
        KPI = []
        voci_kpi = [
            f"R²: {r_quadro:.3f}", 
            f"Intercetta: {intercept:.2f}", 
            f"Signif. (p-val): {p_value:.3e}"
        ]

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
                fill=graph['colore 1'],
                stroke="black",
                stroke_width=0.5
            )
        )
    else:
        KPI = []

    # Rendering finale dell'intero canvas SVG
    plot = SVG(
        width=600,
        height=400,
        elements=assi + barre + etichette_assi + valori_barre + KPI
    )
    return plot