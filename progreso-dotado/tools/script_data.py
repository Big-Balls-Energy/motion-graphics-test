"""Narration script as data.

Markup inside each unit's text:
  *word        keyword (highlighted orange in the captions)
  #word        figure token: shown big and alone with a count-up
  word=a_b_c   display "word", spoken "a b c" (numbers, acronyms)
  |            preferred caption block break (blocks are optimized automatically)
  + (leading)  unit continues the previous unit's caption block
A caption block holding a #figure renders the figure huge, with the words
before/after it as small lines above/below.
Each unit is synthesized separately; `pause` is the silence after it.
"""

UNITS = [
    # ---------------------------------------------------------------- HOOK
    ('hook', "¿Por qué esta *cafetería | te regala *dos *sellos… | antes de que compres *nada?", 0.38),
    # ---------------------------------------------------------------- GIRO
    ('giro', "No es *generosidad.", 0.22),
    ('giro', "Es *psicología. | Se llama:", 0.16),
    ('giro', "el *efecto de *progreso *dotado.", 0.45),
    # ---------------------------------------------------------- EXPERIMENTO
    ('experimento', "En un *estudio, | un *autolavado repartió | dos *tarjetas.", 0.22),
    ('experimento', "Una pedía *8=ocho *lavados.", 0.20),
    ('experimento', "La otra pedía *10=diez… | pero ya traía *2=dos *sellados.", 0.45),
    # ------------------------------------------------------------ RESULTADO
    ('resultado', "Las dos pedían *exactamente…", 0.22),
    ('resultado', "*8=ocho *compras.", 0.40),
    ('resultado', "Con la tarjeta *en *blanco, | solo el…", 0.30),
    ('resultado', "+ #19%=diecinueve_por_ciento la terminó.", 0.24),
    ('resultado', "Con la tarjeta *empezada: | el…", 0.30),
    ('resultado', "+ #34%=treinta_y_cuatro_por_ciento.", 0.30),
    ('resultado', "#Casi #el #doble.", 0.50),
    # ----------------------------------------------------------- POR QUÉ
    ('porque', "Cuando sientes que ya *avanzaste, | tu *cerebro no quiere | dejar algo a *medias.", 0.32),
    ('porque', "Ya no ves *8=ocho *pasos | por hacer: ves una *meta…", 0.22),
    ('porque', "+ #20%=veinte_por_ciento *cumplida.", 0.45),
    # ------------------------------------------------------------- DÓNDE
    ('donde', "Está en *perfiles | que empiezan al *20%=veinte_por_ciento, | en *apps=aps que te regalan | *puntos de *bienvenida, | y en *cursos que marcan | la primera lección | como *lista.", 0.45),
    # -------------------------------------------------------- APLICACIÓN
    ('aplicacion', "¿Tienes un *negocio?", 0.18),
    ('aplicacion', "No regales *descuentos.", 0.42),
    ('aplicacion', "Regala *progreso.", 0.45),
    # ---------------------------------------------------------------- CTA
    ('cta', "*Sígueme para más trucos | de *psicología que usan | las marcas *contigo.", 0.0),
]
