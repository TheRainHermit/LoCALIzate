# backend/app/ml/ux_writing.py

def generate_caleño_narrative(lugar, user_style, tone='enthusiastic') -> str:
    """
    Genera narrativa personalizada con acento caleño
    
    Ejemplos de tono caleño:
    - "¡Oís!" (inicio)
    - "Chimba" (genial)
    - "Arrechísimo" (increíble)
    - "Paila" (problema)
    """
    
    narratives = {
        ('Iglesia La Ermita', 'cultural'): """
            ¡Oís, bienvenido a La Ermita! Esta iglesia es de lo más chimba que vas a ver en Cali.
            Fue construida en 1747 en estilo gótico, inspirada en la Catedral de Colonia en Alemania.
            
            Mira bien los detalles: las vidrieras, los arcos apuntados. La historia que contiene 
            estas paredes es arrechísima. Aquí se han rezado las plegarias de generaciones de caleños.
            
            Pro tip: Sube al campanario al atardecer. La vista de la ciudad desde arriba 
            es de lo mejor que vas a experimentar.
        """,
        
        ('El Gato del Río', 'cultura'): """
            ¡Oís, este es el gato más famoso de Cali! Toda una institución.
            
            La escultura es de Hernando Tejada y está rodeada por las "gatas de la ribera", 
            unas 12 esculturas más pequeñas. Los caleños lo veneramos como si fuera un santo.
            
            Cuenta la leyenda que si tocas al gato y le pides un deseo con fe, 
            puede que se te cumpla. Así que no dudes en hacerlo.
        """,
    }
    
    # Si existe narrativa personalizada, usarla
    key = (lugar['nombre'], user_style)
    if key in narratives:
        return narratives[key]
    
    # Si no, generar genéricamente
    base_intro = "¡Oís, bienvenido a {nombre}!"
    
    if tone == 'enthusiastic':
        template = base_intro + "\n{descripcion}\n\nEsta es una chimba de lugar que no te puedes perder."
    elif tone == 'relaxed':
        template = base_intro + "\n{descripcion}\n\nTómate tu tiempo, no hay prisa."
    elif tone == 'health':
        template = base_intro + "\n{descripcion}\n\nAquí encontrarás paz y tranquilidad."
    
    return template.format(
        nombre=lugar['nombre'],
        descripcion=lugar['descripcion']
    )