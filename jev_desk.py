# Krok 3: Zadawanie trzech różnych typów pytań naraz
# Ten skrypt demonstruje moc Jev/Ollama - można jednocześnie prosić o:
# 1. Choice (wybór z opcji) - dokąd skierować wizytującego?
# 2. Score (ocena na skali) - jak pilna jest sprawa?
# 3. Noul (pytanie tak/nie) - czy ktoś potrzebuje pomocy?
#
# Ta wersja używa LOKALNEGO Ollama zamiast OpenRouter API.
# Wymaga: Ollama v0.35.0+ z zainstalowanym modelem (np. ollama pull tev1:0.8b)

import requests
import json
from pprint import pprint

# Konfiguracja lokalnego Ollama
OLLAMA_URL = "http://localhost:11434/v1/systemone"
MODEL_NAME = "tev1:0.8b"


def format_results(response_data):
    """
    Formatuje i wyodrębnia wyniki z odpowiedzi Ollama.

    Args:
        response_data: dict z JSON odpowiedzi od Ollama

    Returns:
        dict z wyodrębnionym wynikami
    """
    answers = response_data["answers"]

    # === WYODRĘBNIANIE WYNIKÓW ===
    # Każdy typ pytania zwraca inne pola:

    # Choice - zawiera "choice" (najprawdopodobniejsza opcja)
    # i "probabilities" (szanse dla każdej opcji)
    desk_result = answers["desk"]
    desk_choice = desk_result["choice"]
    desk_confidence = desk_result["confidence"]
    desk_probs = desk_result["probabilities"]

    # Score - zawiera "score" (średnia ważona na skali)
    # i "legend" (mapowanie indeksów na opisy)
    urgency_result = answers["urgency"]
    urgency_score = urgency_result["score"]
    urgency_confidence = urgency_result["confidence"]

    # Noul - zawiera "noul" (prawdopodobieństwo "true")
    # wartość 0-1 gdzie 1 = zdecydowane "tak", 0 = zdecydowane "nie"
    assistance_result = answers["needs_assistance"]
    assistance_prob = assistance_result["noul"]

    return {
        "desk": {
            "choice": desk_choice,
            "confidence": desk_confidence,
            "probabilities": desk_probs,
        },
        "urgency": {
            "score": urgency_score,
            "confidence": urgency_confidence,
            "max_score": len(urgency_result["legend"]) - 1,
        },
        "needs_assistance": {
            "probability": assistance_prob,
            "answer": "Yes" if assistance_prob > 0.5 else "No",
        },
    }


def main():
    """
    Główna funkcja - pobiera sformułowanie od wizytującego i wysyła do Ollama.
    """
    print(f"🤖 Używam modelu: {MODEL_NAME}")
    print(f"🌐 Endpoint: {OLLAMA_URL}\n")

    # Pobierz naturalne sformułowanie od użytkownika
    visitor_says = input("What does the visitor say? ")

    try:
        # === PRZYGOTOWANIE ŻĄDANIA ===
        request_payload = {
            # Model do użycia
            "model": MODEL_NAME,

            # State - treść do analizy
            # Tutaj: słownik z kluczem "visitor_says"
            # Model może się do niego odwołać w instrukcjach
            "state": {"visitor_says": visitor_says},

            # Questions - TRZY PYTANIA NARAZ
            # Wszystkie są wysyłane w jednym żądaniu, co jest bardziej efektywne
            # niż wysyłanie kilku żądań osobno
            "questions": {
                # === PYTANIE 1: CHOICE - WYBÓR Z OPCJI ===
                "desk": {
                    "type": "choice",

                    # Instrukcja dla modelu
                    "instructions": "Where should the info desk send the visitor?",

                    # Criteria - słownik opcji z opisami
                    # Klucze: identyfikatory opcji
                    # Wartości: opisy opcji (pomocne dla modelu)
                    "criteria": {
                        "ticket_counter": "Buying, changing, or refunding tickets.",
                        "lost_and_found": "Looking for something they lost.",
                        "immediate_help": "An emergency, an injury, or a missing person.",
                    }
                },

                # === PYTANIE 2: SCORE - OCENA NA SKALI ===
                "urgency": {
                    "type": "score",

                    "instructions": "How urgent is the request of the visitor?",

                    # Criteria - LISTA od najniższej do najwyższej oceny
                    # Indeks = wartość (0, 1, 2, 3)
                    # Model zwróci średnią ważoną tych indeksów
                    "criteria": [
                        "Not urgent at all.",                              # 0
                        "Should be handled today.",                        # 1
                        "Should be handled within the next few minutes.",  # 2
                        "Needs to be handled right now.",                  # 3
                    ]
                },

                # === PYTANIE 3: NOUL - TAK/NIE ===
                "needs_assistance": {
                    "type": "noul",

                    "instructions": (
                        "Does the visitor need a staff member to help them get around "
                        "the station, for example because of a wheelchair, heavy "
                        "luggage, or small children?"
                    ),

                    # Criteria - opcjonalne dla noul
                    # Wyjaśnia co oznacza false i true
                    "criteria": {
                        "false": "Visitor does not need physical assistance",
                        "true": "Visitor needs staff to help them"
                    }
                },
            }
        }

        # === WYSŁANIE ŻĄDANIA ===
        print("📤 Wysyłam żądanie do Ollama...\n")

        response = requests.post(
            OLLAMA_URL,
            json=request_payload,
            timeout=30
        )

        # Sprawdzenie czy request się powiódł
        if response.status_code != 200:
            print(f"❌ Błąd Ollama ({response.status_code})")
            print(response.text)
            return

        # === PRZETWARZANIE ODPOWIEDZI ===
        result = response.json()

        print("✅ Otrzymana odpowiedź\n")

        # === WYŚWIETLENIE SUROWEJ ODPOWIEDZI ===
        print("=== Raw Ollama Response ===")
        pprint(result["answers"])

        # === WYŚWIETLENIE SFORMATOWANYCH WYNIKÓW ===
        parsed = format_results(result)

        print("\n=== Parsed Results ===")

        # Rezultaty pytania Choice
        print(f"\n🏪 Desk (Choice):")
        print(f"   Decision: {parsed['desk']['choice']}")
        print(f"   Confidence: {parsed['desk']['confidence']:.1%}")
        print(f"   All options:")
        for option, prob in parsed['desk']['probabilities'].items():
            print(f"     - {option}: {prob:.1%}")

        # Rezultaty pytania Score
        print(f"\n⏰ Urgency (Score):")
        max_score = parsed['urgency']['max_score']
        current_score = parsed['urgency']['score']
        print(f"   Score: {current_score:.2f}/{max_score}")
        print(f"   Confidence: {parsed['urgency']['confidence']:.1%}")

        # Rezultaty pytania Noul
        print(f"\n🆘 Needs Assistance (Noul):")
        print(f"   Answer: {parsed['needs_assistance']['answer']}")
        print(f"   Probability: {parsed['needs_assistance']['probability']:.1%}")

        # === STATYSTYKI ===
        print(f"\n📊 Token Usage:")
        print(f"   Input: {result['usage']['input_tokens']}")
        print(f"   Output: {result['usage']['output_tokens']}")

    except requests.exceptions.ConnectionError:
        print("❌ Nie mogę połączyć się z Ollamą.")
        print("   Uruchom: ollama serve")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Ollama odpowiada zbyt długo")
    except Exception as e:
        print(f"❌ Błąd: {e}")


if __name__ == "__main__":
    main()
