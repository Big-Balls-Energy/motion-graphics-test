"""Línea de tiempo maestra: 60 s exactos a 30 fps (frames 0..1799)."""
FPS = 30
TOTAL_FRAMES = 1800

# Rango de frames maestros que renderiza cada plano (inclusive), con "colas" para las transiciones.
SHOTS = {
    "s1a": (0, 135),     # 0.0–4.5 s   pierna: piel -> escáner -> red venosa -> várice
    "s1b": (122, 248),   # 4.07–8.27   dentro de la vena: válvula incompetente y reflujo
    "s2": (234, 488),    # 7.8–16.27   corte de tejido: ecografía + microaguja
    "s3a": (474, 623),   # 15.8–20.77  microespuma desplaza la sangre
    "s3b": (609, 758),   # 20.3–25.27  endotelio: reacción local
    "s3c": (744, 908),   # 24.8–30.27  cierre progresivo y fibrosis
    "s4": (894, 1208),   # 29.8–40.27  red venosa: la circulación continúa
    "s5": (1194, 1508),  # 39.8–50.27  beneficios
    "s6": (1494, 1799),  # 49.8–60.0   cierre institucional
}

# Cortes (frame maestro donde el plano siguiente ya domina) y duración de la transición en frames.
CUTS = [("s1a", "s1b", 129, 12), ("s1b", "s2", 241, 12), ("s2", "s3a", 481, 12), ("s3a", "s3b", 616, 12),
        ("s3b", "s3c", 751, 12), ("s3c", "s4", 901, 12), ("s4", "s5", 1201, 12), ("s5", "s6", 1501, 12)]

# Narración: (segmento, inicio en segundos)
NARRATION = [("n1", 0.35), ("n2", 8.15), ("n3a", 17.0), ("n3b", 22.3), ("n4a", 30.25), ("n4b", 36.15),
             ("n5", 40.35), ("n6a", 50.45), ("n6b", 56.4)]


def local_t(shot, frame):
    return (frame - SHOTS[shot][0]) / FPS
