"""
Projekt Jev Python - Nauka użycia Ollama do klasyfikacji decyzji
Oparty na: Ollama v0.35.0+ z /v1/systemone endpoint
            (implementacja TypeSafe Jev API)

Ten projekt demonstruje trzy podejścia do obsługi odpowiedzi użytkownika:

1. plain_python.py
   - Prosty skrypt bez AI
   - Wymaga odpowiedzi w formacie Y/N
   - Pokazuje problem: każdy wariant naturalnej odpowiedzi wymaga osobnego if'a

2. jev_noul.py (ZAKTUALIZOWANY - LOKALNY OLLAMA)
   - Używa Noul (Yes-or-No-Understanding-Level) z Ollama
   - Rozumie naturalne odpowiedzi: "yeah", "yes", "nope", itd.
   - Zwraca wartość od 0 do 1 (pewność odpowiedzi)
   - Model: tev1:0.8b (ale może być nimble lub tev1:4b)

3. jev_desk.py (ZAKTUALIZOWANY - LOKALNY OLLAMA)
   - Najbardziej zaawansowany
   - Zadaje trzy rodzaje pytań naraz:
     * Choice (wybór z opcji)
     * Score (ocena na skali)
     * Noul (pytanie tak/nie)
   - Jedna liczba żądań, trzy odpowiedzi
   - Model: tev1:0.8b

WYMAGANIA:
1. Ollama v0.35.0+ uruchomiona lokalnie
2. Pobrany model (np. "ollama pull tev1:0.8b")
3. Python z requests: pip install requests

URUCHOMIENIE:
- plain_python.py  : python plain_python.py
- jev_noul.py      : python jev_noul.py
- jev_desk.py      : python jev_desk.py

PRZED URUCHOMIENIEM:
Upewnij się że Ollama serwer jest uruchomiony:
  ollama serve

W innym terminalu pobierz model (jeśli jeszcze go nie masz):
  ollama pull tev1:0.8b
  # lub
  ollama pull nimble

ZMIANA MODELU:
Edytuj zmienną MODEL_NAME w jev_noul.py lub jev_desk.py:
  MODEL_NAME = "nimble"      # duży (9B)
  MODEL_NAME = "tev1"        # średni (4B)
  MODEL_NAME = "tev1:0.8b"   # mały (0.8B)
"""


def print_instructions():
    print(__doc__)


if __name__ == '__main__':
    print_instructions()
