# Krok 1: Prosty skrypt bez AI
# Ten plik pokazuje, jak trudne jest obsługiwanie wszystkich wariantów odpowiedzi użytkownika
# bez korzystania z AI. Tutaj wymuszamy odpowiedź w formacie Y lub N.

def respond(lost_something):
    """Zwróć odpowiedź na podstawie decyzji użytkownika."""
    if lost_something:
        print("You can find the lost and found counter on the right.")
    else:
        print("What can I help you with?")


def ask():
    """
    Pyta użytkownika, czy coś zgubił.
    Wymaga dokładnie "Y" lub "N" (wielkie litery).
    Jest to problem, bo każdy wariant naturalnej odpowiedzi (yes, yeah, nope, etc.)
    wymagałby dodatkowego warunku if.
    """
    while True:
        answer = input("Did you lose something? (Y/N) ")
        if answer == "Y":
            return True
        if answer == "N":
            return False
        print("Please answer with Y or N.")


def main():
    lost_something = ask()
    respond(lost_something)


if __name__ == "__main__":
    main()
