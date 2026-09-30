"""
Projekt Jev Python - Nauka użycia AI do klasyfikacji odpowiedzi użytkownika
Źródło: https://realpython.com/how-to-get-started-with-jev-in-python/

Ten projekt demonstruje trzy podejścia do obsługi odpowiedzi użytkownika:

1. plain_python.py
   - Prosty skrypt bez AI
   - Wymaga odpowiedzi w formacie Y/N
   - Pokazuje problem: każdy wariant naturalnej odpowiedzi wymaga osobnego if'a

2. jev_noul.py
   - Używa Noul (Yes-or-No-Understanding-Level) z AI Jev
   - Rozumie naturalne odpowiedzi: "yeah", "yes", "nope", itd.
   - Zwraca wartość od 0 do 1 (pewność odpowiedzi)

3. jev_desk.py
   - Najbardziej zaawansowany
   - Zadaje trzy rodzaje pytań naraz:
     * Choice (wybór z opcji)
     * Score (ocena na skali)
     * Noul (pytanie tak/nie)
   - Jedna liczba żądań, trzy odpowiedzi

KONFIGURACJA:
1. Edytuj plik .env i wstaw swój klucz OpenRouter API
2. Zainstaluj zależności: uv pip install -r pyproject.toml

URUCHOMIENIE:
- plain_python.py  : uv run plain_python.py
- jev_noul.py      : uv run --env-file .env jev_noul.py
- jev_desk.py      : uv run --env-file .env jev_desk.py
"""


def print_instructions():
    print(__doc__)


if __name__ == '__main__':
    print_instructions()
