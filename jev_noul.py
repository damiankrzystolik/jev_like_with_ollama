# Krok 2: Zadawanie pytań tak/nie za pomocą Noul
# Noul (Yes-or-No-Understanding-Level) zastępuje sztywną kontrolę Y/N inteligentnym
# rozpoznawaniem intencji użytkownika, niezależnie od tego, jak sformułuje odpowiedź.

import os
from typesafe_sdk import Noul, TypeSafeClient

# Inicjalizacja klienta Jev poprzez OpenRouter API
# - api_key pochodzi ze zmiennej środowiskowej OPENROUTER_API_KEY (z pliku .env)
# - base_url wskazuje na OpenRouter (zamiast bezpośrednio do TypeSafe AI)
client = TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
)


def respond(lost_something):
    """Zwróć odpowiedź na podstawie wyniku analizy Jev."""
    if lost_something:
        print("You can find the lost and found counter on the right.")
    else:
        print("What can I help you with?")


def ask():
    """
    Pyta użytkownika naturalnym językiem i używa Jev do zrozumienia odpowiedzi.

    Noul zwraca wartość float od 0 do 1:
    - 1 = zdecydowanie "tak"
    - 0 = zdecydowanie "nie"
    - 0.5 = niepewna odpowiedź

    Ustawiamy własne progi cutoff:
    - > 0.8 = interpretujemy jako "tak"
    - < 0.2 = interpretujemy jako "nie"
    - między 0.2 a 0.8 = prosimy o powtórzenie
    """
    while True:
        # Niewymagana już odpowiedź w formacie Y/N - Jev zrozumie każdą formę
        answer = input("Did you lose something? ")

        # client.system_one() wysyła żądanie do Jev z:
        # - state: tekst do analizy (odpowiedź użytkownika)
        # - questions: słownik pytań, które chcemy, aby Jev odpowiedział
        r = client.system_one(
            state=answer,
            questions={
                # Noul wymaga "instructions" - instrukcji, jak interpretować stan
                "lost_something": Noul(
                    instructions="Is the answer from the user affirmative?"
                ),
            },
        )

        # Wyodrębniamy Noul score dla naszego pytania
        lost_something = r.answers["lost_something"].noul

        # Stosujemy progi cutoff - możemy je dostosować do potrzeb
        if lost_something > 0.8:
            return True
        if lost_something < 0.2:
            return False

        # Jeśli Jev nie jest pewny, prosimy o powtórzenie
        print("Sorry, I didn't get that.")


def main():
    lost_something = ask()
    respond(lost_something)


if __name__ == "__main__":
    main()
