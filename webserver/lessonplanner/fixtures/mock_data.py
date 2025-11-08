"""
Mock data fixtures for lessonplanner application.

This module contains sample data used until the database implementation is complete.
All data is in Polish to match the application's target language.
"""

# Mock curriculum reference data
# Format: {code: full_text}
MOCK_CURRICULUM_REFS = {
    "1.1": "zgłasza potrzeby fizjologiczne, samodzielnie wykonuje podstawowe czynności higieniczne;",
    "2.5": "rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;",
    "3.8": "obdarza uwagą inne dzieci i osoby dorosłe;",
    "4.15": "przelicza elementy zbiorów w czasie zabawy, prac porządkowych, ćwiczeń i wykonywania innych czynności, posługuje się liczebnikami głównymi i porządkowymi, rozpoznaje cyfry oznaczające liczby od 0 do 10, eksperymentuje z tworzeniem kolejnych liczb, wykonuje dodawanie i odejmowanie w sytuacji użytkowej, liczy obiekty, odróżnia liczenie błędne od poprawnego;",
    "4.18": "eksperymentuje w zakresie orientacji przestrzennej: wysoko – nisko, blisko – daleko, z przodu – z tyłu, nad – pod, prawo – lewo, góra – dół;"
}

# Mock educational module data
# Format: list of dicts with id, name, is_ai_suggested, created_at
MOCK_EDUCATIONAL_MODULES = [
    {
        'id': 1,
        'name': 'JĘZYK',
        'is_ai_suggested': False,
        'created_at': '2025-10-28T10:00:00Z'
    },
    {
        'id': 2,
        'name': 'MATEMATYKA',
        'is_ai_suggested': False,
        'created_at': '2025-10-28T10:00:00Z'
    },
    {
        'id': 3,
        'name': 'MOTORYKA DUŻA',
        'is_ai_suggested': False,
        'created_at': '2025-10-28T10:00:00Z'
    },
    {
        'id': 4,
        'name': 'FORMY PLASTYCZNE',
        'is_ai_suggested': False,
        'created_at': '2025-10-28T10:00:00Z'
    },
    {
        'id': 5,
        'name': 'EDUKACJA MUZYCZNA',
        'is_ai_suggested': True,
        'created_at': '2025-10-28T10:00:00Z'
    }
]
