"""
Mock data for AI client service - Polish curriculum data
"""

# 12 standard educational modules from Polish curriculum
# Used by AI service for random module selection
MODULE_NAMES = [
    "JĘZYK",
    "MATEMATYKA",
    "MOTORYKA MAŁA",
    "MOTORYKA DUŻA",
    "FORMY PLASTYCZNE",
    "MUZYKA",
    "POZNAWCZE",
    "WSPÓŁPRACA",
    "EMOCJE",
    "SPOŁECZNE",
    "SENSORYKA",
    "ZDROWIE",
]

# Educational modules with metadata for API responses
EDUCATIONAL_MODULES = [
    {'id': 1, 'name': 'JĘZYK', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 2, 'name': 'MATEMATYKA', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 3, 'name': 'MOTORYKA MAŁA', 'is_ai_suggested': True, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 4, 'name': 'MOTORYKA DUŻA', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 5, 'name': 'FORMY PLASTYCZNE', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 6, 'name': 'MUZYKA', 'is_ai_suggested': True, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 7, 'name': 'POZNAWCZE', 'is_ai_suggested': True, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 8, 'name': 'WSPÓŁPRACA', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 9, 'name': 'EMOCJE', 'is_ai_suggested': True, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 10, 'name': 'SPOŁECZNE', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 11, 'name': 'SENSORYKA', 'is_ai_suggested': True, 'created_at': '2025-10-28T10:00:00Z'},
    {'id': 12, 'name': 'ZDROWIE', 'is_ai_suggested': False, 'created_at': '2025-10-28T10:00:00Z'},
]

# Sample curriculum references with Polish text for tooltips
CURRICULUM_REFERENCES = {
    "1.1": "Dziecko rozwija koordynację wzrokowo-ruchową podczas zabaw plastycznych.",
    "1.2": "Dziecko rozumie podstawowe pojęcia matematyczne, takie jak więcej, mniej, tyle samo.",
    "1.3": "Dziecko potrafi klasyfikować przedmioty według jednej cechy.",
    "2.1": "Dziecko słucha uważnie i rozumie proste polecenia.",
    "2.2": "Dziecko eksperymentuje z różnymi materiałami plastycznymi.",
    "2.3": "Dziecko wyraża swoje myśli i uczucia w sposób zrozumiały dla innych.",
    "2.5": "rozstaje się z rodzicami bez lęku, ma świadomość, że rozstanie takie bywa dłuższe lub krótsze;",
    "2.7": "Dziecko potrafi wykonać proste ruchy taneczne do muzyki.",
    "3.1": "Dziecko zapoznaje się z literaturą dziecięcą, słucha uważnie wiersza.",
    "3.8": "obdarza uwagą inne dzieci i osoby dorosłe;",
    "4.15": "Dziecko porównuje liczebność grup przedmiotów w zakresie 5.",
    "4.18": "Dziecko rozpoznaje poznane wcześniej cyfry i litery.",
    "5.2": "Dziecko wykazuje zainteresowanie poznawaniem otaczającego świata.",
    "6.1": "Dziecko wyraża emocje w sposób akceptowalny społecznie.",
    "7.3": "Dziecko współpracuje z innymi dziećmi podczas wspólnych zabaw.",
    "8.1": "Dziecko dba o higienę osobistą i zdrowie.",
    "9.1": "Dziecko uczestniczy w zabawach ruchowych, rozwija motorykę dużą.",
}

# Pool of sample objectives in Polish (used for random selection)
SAMPLE_OBJECTIVES = [
    "Dziecko potrafi przeliczać w zakresie 5",
    "Dziecko rozpoznaje poznane wcześniej cyfry",
    "Dziecko zapoznaje się z literaturą dziecięcą, słucha uważnie wiersza",
    "Dziecko potrafi współpracować z innymi podczas tworzenia wspólnej pracy",
    "Rozwijanie koordynacji wzrokowo-ruchowej",
    "Dziecko eksperymentuje z różnymi technikami plastycznymi",
    "Dziecko rozwija sprawność manualną podczas pracy z drobnymi przedmiotami",
    "Dziecko wyraża swoje emocje i uczucia poprzez sztukę",
    "Dziecko klasyfikuje przedmioty według koloru i wielkości",
    "Dziecko aktywnie uczestniczy w zabawach ruchowych",
    "Dziecko śpiewa piosenki i rytmicznie się porusza",
    "Dziecko rozpoznaje podstawowe kształty geometryczne",
    "Dziecko rozwija umiejętności społeczne podczas wspólnych zabaw",
    "Dziecko potrafi nazywać emocje swoje i innych",
    "Dziecko poznaje zjawiska przyrodnicze poprzez obserwację",
    "Dziecko rozwija zmysły przez zabawy sensoryczne",
    "Dziecko dba o bezpieczeństwo własne i innych",
    "Dziecko wykazuje inicjatywę w działaniach twórczych",
    "Dziecko rozumie pojęcia przestrzenne: na, pod, obok, za",
    "Dziecko słucha ze zrozumieniem prostych instrukcji",
]
