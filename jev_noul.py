# Krok 2: Zadawanie pytań tak/nie za pomocą Noul
# Noul (Yes-or-No-Understanding-Level) zastępuje sztywną kontrolę Y/N inteligentnym
# rozpoznawaniem intencji użytkownika, niezależnie od tego, jak sformułuje odpowiedź.
#
# Ta wersja używa LOKALNEGO Ollama zamiast OpenRouter API.
# Wymaga: Ollama v0.35.0+ z zainstalowanym modelem (np. ollama pull tev1:0.8b)

import requests
import json

# Konfiguracja lokalnego Ollama
# - host: localhost (twój komputer)
# - port: 11434 (domyślny port Ollamy)
# - endpoint: /v1/systemone (nowy endpoint Jev w Ollama)
OLLAMA_URL = "http://localhost:11434/v1/systemone"

# Nazwa modelu do użycia - upewnij się, że jest pobrany
# Dostępne: "nimble" (9B), "tev1" (4B), "tev1:0.8b" (0.8B)
MODEL_NAME = "tev1:0.8b"


def respond(lost_something):
    """Zwróć odpowiedź na podstawie wyniku analizy Ollama."""
    if lost_something:
        print("You can find the lost and found counter on the right.")
    else:
        print("What can I help you with?")


def ask():
    """
    Pyta użytkownika naturalnym językiem i używa Ollama do zrozumienia odpowiedzi.

    Noul zwraca wartość float od 0 do 1:
    - 1.0 = zdecydowanie "tak"
    - 0.0 = zdecydowanie "nie"
    - 0.5 = niepewna odpowiedź

    Ustawiamy własne progi cutoff:
    - > 0.8 = interpretujemy jako "tak"
    - < 0.2 = interpretujemy jako "nie"
    - między 0.2 a 0.8 = prosimy o powtórzenie
    """
    while True:
        # Niewymagana już odpowiedź w formacie Y/N - Ollama zrozumie każdą formę
        answer = input("Did you lose something? ")

        try:
            # === PRZYGOTOWANIE ŻĄDANIA ===
            # Struktura JSON wysyłana do Ollama /v1/systemone endpoint
            request_payload = {
                # Model do użycia - musi być pobrany lokalnie
                "model": MODEL_NAME,

                # State - treść do analizy (odpowiedź użytkownika)
                # Może być string lub dict, tutaj: proste sformułowanie
                "state": answer,

                # Questions - słownik pytań, które zadajemy modelowi
                # Każde pytanie wysyłane jest osobno, ale w jednym żądaniu
                "questions": {
                    # Nazwa pytania ("lost_something") - będzie kluczem w odpowiedzi
                    "lost_something": {
                        # Typ pytania: "noul" = pytanie tak/nie
                        # Inne opcje: "choice" (wybór), "score" (ocena na skali)
                        "type": "noul",

                        # Instructions - co model ma zrobić z state'em?
                        # Model będzie analizować 'answer' pod kątem tej instrukcji
                        "instructions": "Is the answer from the user affirmative?",

                        # Criteria - opcjonalne dla noul, ale możemy podać
                        # aby wyjaśnić co to "false" i "true"
                        "criteria": {
                            "false": "User is denying or saying no",
                            "true": "User is affirming or saying yes"
                        }
                    }
                }
            }

            # === WYSŁANIE ŻĄDANIA ===
            # POST request do lokalnego Ollama
            response = requests.post(
                OLLAMA_URL,
                json=request_payload,
                timeout=30  # timeout 30 sekund
            )

            # Sprawdzenie czy request się powiódł
            if response.status_code != 200:
                print(f"❌ Błąd Ollama: {response.status_code}")
                print(f"   {response.text}")
                continue

            # === PRZETWARZANIE ODPOWIEDZI ===
            # Parsowanie JSON odpowiedzi od Ollama
            result = response.json()

            # Wyodrębnianie Noul score dla naszego pytania "lost_something"
            # Struktura: result["answers"]["lost_something"]["noul"]
            lost_something_score = result["answers"]["lost_something"]["noul"]

            # Drukowanie statystyk (opcjonalne)
            print(f"   [Confidence: {lost_something_score:.2%}]")

            # === INTERPRETACJA WYNIKU ===
            # Stosujemy progi cutoff - możemy je dostosować do potrzeb
            # Wyższe thresholdy = bardziej pewne odpowiedzi
            if lost_something_score > 0.8:
                # Model jest pewny że odpowiedź to "tak"
                return True

            if lost_something_score < 0.2:
                # Model jest pewny że odpowiedź to "nie"
                return False

            # Jeśli model nie jest pewny (0.2-0.8), prosimy o powtórzenie
            print("Sorry, I didn't get that.")

        except requests.exceptions.ConnectionError:
            # Ollama nie odpowiada - może nie jest uruchomiony
            print("❌ Nie mogę połączyć się z Ollamą.")
            print("   Uruchom: ollama serve")
            return None
        except requests.exceptions.Timeout:
            print("❌ Timeout - Ollama odpowiada zbyt długo")
            continue
        except KeyError as e:
            # Błąd w parsowaniu odpowiedzi
            print(f"❌ Błąd parsowania odpowiedzi: {e}")
            print(f"   Odpowiedź: {result}")
            continue
        except Exception as e:
            # Inny błąd
            print(f"❌ Nieoczekiwany błąd: {e}")
            continue


def main():
    print(f"🤖 Używam modelu: {MODEL_NAME}")
    print(f"🌐 Endpoint: {OLLAMA_URL}\n")

    lost_something = ask()

    if lost_something is not None:
        respond(lost_something)


if __name__ == "__main__":
    main()
