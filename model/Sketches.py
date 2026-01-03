stroke_1 = [
    (128, 32),
    (96, 38),
    (68, 58),
    (48, 90),
    (40, 128),
    (48, 168),
    (68, 200),
    (96, 220),
    (128, 232),
    (160, 220),
    (188, 200),
    (208, 168),
    (216, 128),
    (208, 90),
    (188, 58),
    (160, 38),
    (128, 32),
]
stroke_2 = [
    (108, 40),
    (118, 52),
    (128, 56),
    (138, 52),
    (148, 40),
]
stroke_3 = [
    (128, 32),
    (130, 18),
    (134, 6),
]
stroke_4 = [
    (134, 18),
    (162, 6),
    (192, 18),
    (170, 36),
    (144, 30),
]
apple_sketch = [
    stroke_1,
    stroke_2,
    stroke_3,
    stroke_4,
]


plane_sketch = [
    [
        (30, 140),   # Punta (Nariz)
        (45, 125),   # Techo cabina
        (80, 115),   # Parte superior delantera
        (220, 115),  # Parte superior trasera
        (280, 135),  # Hacia la cola
        (280, 145),  # Base de la cola
        (220, 160),  # Parte inferior trasera
        (80, 160),   # Parte inferior delantera
        (45, 155),   # Curva inferior nariz
        (30, 140),   # Cierre
    ],
    # ALA PRINCIPAL (Con ángulo de flecha)
    [
        (110, 155),  # Unión delantera
        (140, 195),  # Punta exterior delantera
        (170, 195),  # Punta exterior trasera
        (160, 155),  # Unión trasera
    ],
    # ESTABILIZADOR HORIZONTAL (Cola)
    [
        (250, 140), 
        (285, 130), 
        (295, 130), 
        (275, 145),
    ],
    # ESTABILIZADOR VERTICAL (Timón de dirección)
    [
        (240, 120),  # Base delantera
        (275, 80),   # Punta superior
        (290, 80),   # Punta superior trasera
        (275, 120),  # Base trasera
    ],
    # VENTANAS DE LA CABINA (Parabrisas)
    [
        (45, 130), (60, 125), (75, 125), (70, 135)
    ],
    # VENTANAS DE PASAJEROS (Puntos individuales)
    [(90, 135)], [(110, 135)], [(130, 135)], [(150, 135)], [(170, 135)], [(190, 135)]
]


triangle_sketch = [
    [
        (128, 30),
        (40, 210),
        (216, 210),
        (128, 30),
    ]
]


rectangle_sketch = [
    [
        (40, 40),
        (216, 40),
        (216, 216),
        (40, 216),
        (40, 40),
    ]
]

circle_sketch = [
    [
        (128, 24),
        (176, 32),
        (216, 64),
        (232, 128),
        (216, 192),
        (176, 224),
        (128, 232),
        (80, 224),
        (40, 192),
        (24, 128),
        (40, 64),
        (80, 32),
        (128, 24),
    ]
]


fish_sketch = [
     [
        (20, 128),
        (40, 100),
        (80, 80),
        (140, 80),
        (200, 100),
        (220, 128),
        (200, 156),
        (140, 176),
        (80, 176),
        (40, 156),
        (20, 128),
    ],
    # cola (en V)
    [
        (220, 128),
        (255, 96),
        (245, 128),
        (255, 160),
        (220, 128),
    ],
    # ojo
    [
        (60, 120),
        (62, 120),
    ],
    # aleta dorsal
    [
        (120, 80),
        (135, 55),
        (150, 80),
    ],
]

sketches = {
    "airplane": plane_sketch,
    "triangle": triangle_sketch,
    "square": rectangle_sketch,
    "circle": circle_sketch,
    "fish": fish_sketch,
    "apple": apple_sketch
}
