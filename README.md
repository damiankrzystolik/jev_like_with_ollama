# Projekt Jev Python — Lokalne decyzje z Ollama

Nauka użycia **Ollama v0.35.0+** z endpointem `/v1/systemone` do szybkich, typizowanych decyzji. Implementacja **TypeSafe Jev API** — bardziej efektywna niż LLM do pytań z zamkniętym zbiorem odpowiedzi.

## 📋 Problem, który rozwiązuje Jev

Tradycyjne LLM są **wolne i drogie** do pytań, które mają ograniczoną liczbę odpowiedzi:
- Czy to spam czy nie?
- Którą kategorię wybrać z 5 opcji?
- Jak pilna jest ta sprawa? (skala 0-5)
- Czy użytkownik to rzeczywiście powiedział?

**Jev rozwiązuje to:**
- ⚡ Średnio **91ms** na decyzję (Nimble 9B na M5 Max)
- 💰 Tańsze — brak kosztów API, lokalnie
- 🎯 Dokładniejsze — wytrenowane do decyzji, nie do generacji tekstu
- 📦 Trzy typy pytań: **Choice**, **Score**, **Noul**

## 🎓 Trzy podejścia w tym projekcie

### 1️⃣ `plain_python.py` — Bez AI

```bash
python plain_python.py
```

**Problem:** Wymaga odpowiedzi w formacie `Y/N`. Każdy wariant naturalnej odpowiedzi ("yeah", "nope", "absolutely") wymaga osobnego `if`.

```python
if answer == "Y":
    return True
if answer == "N":
    return False
print("Please answer with Y or N.")
```

✗ Nie skaluje się  
✗ Frustrujące dla użytkownika

---

### 2️⃣ `jev_noul.py` — Pytania tak/nie (Noul)

```bash
python jev_noul.py
```

**Rozwiązanie:** Ollama rozumie naturalne odpowiedzi i zwraca pewność (0.0-1.0).

```
Did you lose something? yeah, I lost my keys
[Confidence: 95.23%]
You can find the lost and found counter on the right.
```

**Co robi:**
- Wysyła tekstową odpowiedź użytkownika do `/v1/systemone`
- Model zwraca prawdopodobieństwo "tak" (0.0-1.0)
- Stosujemy threshold (np. >0.8 = tak, <0.2 = nie)
- Niepewne odpowiedzi (0.2-0.8) — pytamy ponownie

**JSON wysyłany do Ollama:**
```json
{
  "model": "tev1:0.8b",
  "state": "yeah, I lost my keys",
  "questions": {
    "lost_something": {
      "type": "noul",
      "instructions": "Is the answer from the user affirmative?",
      "criteria": {
        "false": "User is denying",
        "true": "User is affirming"
      }
    }
  }
}
```

---

### 3️⃣ `jev_desk.py` — Trzy pytania naraz (Choice + Score + Noul)

```bash
python jev_desk.py
```

**Scenariusz:** Obsługa informacji na lotnisku — trzeba:
1. **Wybrać dział** (choice) — ticket counter / lost & found / emergency
2. **Ocenić pilność** (score) — skala 0-3
3. **Sprawdzić czy potrzeba pomocy** (noul) — tak/nie

**Przykład:**
```
What does the visitor say? I've been waiting 2 hours for my flight and I can't find the gate
📤 Wysyłam żądanie do Ollama...
✅ Otrzymana odpowiedź

=== Parsed Results ===

🏪 Desk (Choice):
   Decision: immediate_help
   Confidence: 89.4%
   All options:
     - ticket_counter: 5.2%
     - lost_and_found: 1.3%
     - immediate_help: 93.5%

⏰ Urgency (Score):
   Score: 2.75/3
   Confidence: 72.1%

🆘 Needs Assistance (Noul):
   Answer: Yes
   Probability: 61.3%

📊 Token Usage:
   Input: 841
   Output: 4
```

**JSON wysyłany (wszystko naraz):**
```json
{
  "model": "tev1:0.8b",
  "state": {"visitor_says": "..."},
  "questions": {
    "desk": {
      "type": "choice",
      "instructions": "Where should the info desk send the visitor?",
      "criteria": {
        "ticket_counter": "Buying, changing, or refunding tickets.",
        "lost_and_found": "Looking for something they lost.",
        "immediate_help": "An emergency, an injury, or a missing person."
      }
    },
    "urgency": {
      "type": "score",
      "instructions": "How urgent is the request?",
      "criteria": [
        "Not urgent at all.",
        "Should be handled today.",
        "Should be handled within the next few minutes.",
        "Needs to be handled right now."
      ]
    },
    "needs_assistance": {
      "type": "noul",
      "instructions": "Does the visitor need staff help?"
    }
  }
}
```

---

## 🛠️ Setup

### Wymagania

- **Ollama v0.35.0+** — [pobierz](https://ollama.com)
- **Python 3.8+**
- **requests** — instalacja poniżej

### Instalacja

```bash
# 1. Zainstaluj requests
pip install requests

# 2. Uruchom Ollama w tle
ollama serve

# 3. W innym terminalu pobierz model (jednorazowo)
ollama pull tev1:0.8b
# lub inne modele:
# ollama pull nimble        # 9B - większy, dokładniejszy
# ollama pull tev1           # 4B - średni
# ollama pull tev1:0.8b      # 0.8B - najmniejszy, najszybszy
```

### Uruchomienie

```bash
# Prosty skrypt bez AI
python plain_python.py

# Pytania tak/nie z Ollama
python jev_noul.py

# Trzy pytania naraz z Ollama
python jev_desk.py
```

---

## 📚 Dostępne modele

| Model | Rozmiar | Szybkość | Dokładność | Najlepsze do |
|-------|---------|----------|-----------|-------------|
| nimble | 9B | Średnia | ⭐⭐⭐⭐⭐ (76%) | Produkcja, wysokie wymagania |
| tev1 | 4B | Szybka | ⭐⭐⭐⭐ (73%) | Balans szybkości i dokładności |
| tev1:0.8b | 0.8B | ⚡ Bardzo szybka | ⭐⭐⭐ (63%) | Real-time, low latency |

Zmień model w kodzie:
```python
MODEL_NAME = "tev1:0.8b"  # zmień tutaj
```

---

## 🔑 Kluczowe koncepty

### Trzy typy pytań

#### 🔘 Choice — Wybór z opcji
Odpowiedź: jeden klucz (np. "bug", "billing", "account")
```python
"questions": {
  "label": {
    "type": "choice",
    "instructions": "Which category fits this ticket?",
    "criteria": {
      "billing": "Payments and refunds",
      "bug": "Software errors",
      "account": "Login issues"
    }
  }
}
```

Response zawiera:
- `choice` — wybrana opcja
- `probabilities` — szanse dla każdej opcji
- `confidence` — jak pewny model (0-1)

#### 📊 Score — Ocena na skali
Odpowiedź: liczba zmiennoprzecinkowa (średnia ważona indeksów)
```python
"questions": {
  "urgency": {
    "type": "score",
    "instructions": "How urgent?",
    "criteria": [
      "Routine: no hurry",         # indeks 0
      "Soon: within hours",        # indeks 1
      "Immediate: right now"       # indeks 2
    ]
  }
}
```

Response zawiera:
- `score` — średnia ważona (0.0-2.0)
- `legend` — mapowanie indeksów na opisy
- `probabilities` — szanse dla każdego poziomu

#### ✅ Noul — Pytanie tak/nie
Odpowiedź: liczba 0-1 (prawdopodobieństwo "true")
```python
"questions": {
  "needs_help": {
    "type": "noul",
    "instructions": "Does user need assistance?",
    "criteria": {  # opcjonalne
      "false": "User can self-serve",
      "true": "User needs human help"
    }
  }
}
```

Response zawiera:
- `noul` — prawdopodobieństwo "tak" (0.0-1.0)

---

## 🎯 Use-case'y (z `about_jev.txt`)

Jev doskonale nadaje się do:

| Zastosowanie | Typ pytania | Przykład |
|---|---|---|
| **Moderacja treści** | Choice | Spam / Hateful / OK |
| **Ticket triage** | Choice + Score | Kategoria + Pilność |
| **Content moderation** | Noul | Narusza regulamin? |
| **Weryfikacja cytowań** | Choice | Źródło potwierdza / Przeczy / Częściowo |
| **Kontrola QA** | Score | Jakość kodu: Low / Medium / High |
| **Fraud detection** | Score | Ryzyko: Routine / Średnie / Wysokie |
| **Detekcja PII** | Choice | Brak PII / Osobowe / Finansowe / Sekrety |
| **Routing do człowieka** | Choice | Automat / Review / Expert |

---

## 💡 Porady praktyczne

### 1. Instrukcje muszą być jasne
```python
# ✗ Źle
"instructions": "What is it?"

# ✅ Dobrze
"instructions": "Is this ticket about a payment issue or a technical bug?"
```

### 2. Criteria muszą być rozłączne
```python
# ✗ Źle — nakładają się
"criteria": {
  "priority_high": "Important tasks",
  "priority_urgent": "Very important tasks"
}

# ✅ Dobrze — jasne granice
"criteria": {
  "routine": "Can wait a week",
  "urgent": "Within 24 hours",
  "critical": "Right now"
}
```

### 3. Dostrojenie thresholdów dla Noul
```python
# Domyślnie: > 0.5 = tak
if noul_score > 0.8:  # bardziej pewnie
    return True

# Lub: < 0.2 = nie, 0.2-0.8 = niepewnie
if noul_score > 0.8:
    return True
elif noul_score < 0.2:
    return False
else:
    print("Not sure, try again")
```

### 4. Łączenie z LLM
Jev nie zawsze wymaga pełnego LLM:
```
Użytkownik
    ↓
Jev: Kategoria? Pilność? Człowiek?
    ↓
  ├─ Niski risk → Automatycznie
  ├─ Średni → Poproś AI o odpowiedź
  └─ Wysoki → Przekaż człowiekowi
```

---

## 🚨 Troubleshooting

### "Connection refused"
```
❌ Nie mogę połączyć się z Ollamą.
   Uruchom: ollama serve
```

Rozwiązanie: W innym terminalu uruchom `ollama serve`

### "Model not found"
```
❌ Błąd: Local model not found
```

Rozwiązanie: `ollama pull tev1:0.8b`

### Wysyłanie wymagań
Jeśli chcesz wysyłać requirements do wersji kontroli:

```bash
pip freeze > requirements.txt
```

Lub ręcznie:
```
requests>=2.28.0
```

---

## 📖 Struktura pliku

```
.
├── main.py              # Dokumentacja projektu
├── plain_python.py      # Bez AI (Y/N)
├── jev_noul.py         # Ollama + Noul (tak/nie)
├── jev_desk.py         # Ollama + 3 pytania
├── README.md           # Ten plik
└── about_jev.txt       # Use-case'y Jev (16+)
```

---

## 📚 Więcej zasobów

- [Ollama Docs](https://ollama.com) — oficjalna dokumentacja
- [System One API](https://docs.ollama.com/api/systemone) — OpenAPI spec
- [Decision Guide](https://docs.ollama.com/capabilities/decision) — więcej przykładów
- `about_jev.txt` — 16+ rzeczywistych use-case'ów w tym projekcie

---

## ⚖️ Licencja

Projekt edukacyjny, MIT Licensed.

---

**Happy deciding! 🚀**
