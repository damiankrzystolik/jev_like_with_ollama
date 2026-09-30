# Krok 3: Zadawanie trzech różnych typów pytań naraz
# Ten skrypt demonstruje moc Jev - można jednocześnie prosić o:
# 1. Noul (pytanie tak/nie) - czy ktoś potrzebuje pomocy?
# 2. Choice (wybór z opcji) - dokąd skierować wizytującego?
# 3. Score (ocena na skali) - jak pilna jest sprawa?

import os
from pprint import pprint
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

# Inicjalizacja klienta Jev
client = TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
)

# QUESTIONS - zdefiniuj wszystkie pytania, które chcesz zadać
# Wszystkie są wysyłane w jednym żądaniu, co jest bardziej efektywne niż
# wysyłanie kilku żądań osobno.
QUESTIONS = {
    # Choice - Jev wybiera jedną z podanych opcji
    # Wymaga "instructions" (co zrobić?) i "criteria" (słownik opcji)
    "desk": Choice(
        instructions="Where should the info desk send the visitor?",
        criteria={
            "ticket_counter": "Buying, changing, or refunding tickets.",
            "lost_and_found": "Looking for something they lost.",
            "immediate_help": "An emergency, an injury, or a missing person.",
        },
    ),

    # Score - Jev ocenia czymś na uporządkowanej skali
    # Wymaga "instructions" i "criteria" (lista od najniższej do najwyższej)
    # Wynik zwracany jako float - średnia ważona pozycji na skali
    "urgency": Score(
        instructions="How urgent is the request of the visitor?",
        criteria=[
            "Not urgent at all.",                                    # 0
            "Should be handled today.",                             # 1
            "Should be handled within the next few minutes.",       # 2
            "Needs to be handled right now.",                       # 3
        ],
    ),

    # Noul - pytanie tak/nie
    # Zmienna pomocnicza - czy wizytujący potrzebuje asysty?
    "needs_assistance": Noul(
        instructions=(
            "Does the visitor need a staff member to help them get around "
            "the station, for example because of a wheelchair, heavy "
            "luggage, or small children?"
        ),
    ),
}


def main():
    """
    Główna funkcja - pobiera polecenie od wizytującego i wysyła do Jev.
    """
    # Pobierz naturalne sformułowanie od użytkownika
    visitor_says = input("What does the visitor say? ")

    # client.system_one() - wyślij stan i wszystkie pytania naraz
    # state: słownik z "visitor_says" - możemy się do niego odwołać w instrukcjach
    # questions: wszystkie pytania z QUESTIONS
    r = client.system_one(
        state={"visitor_says": visitor_says},
        questions=QUESTIONS,
    )

    # Wydrukuj wyniki w czytelnym formacie
    # r.model_dump() konwertuje odpowiedź do słownika Python
    print("\n=== Jev Response ===")
    pprint(r.model_dump()["answers"])

    # Możesz też dostęp do poszczególnych wartości:
    print("\n=== Parsed Results ===")
    desk_choice = r.answers["desk"].choice
    urgency_score = r.answers["urgency"].score
    needs_help = r.answers["needs_assistance"].noul

    print(f"Send to: {desk_choice}")
    print(f"Urgency level: {urgency_score:.2f}/3")
    print(f"Needs assistance: {'Yes' if needs_help > 0.5 else 'No'}")


if __name__ == "__main__":
    main()
