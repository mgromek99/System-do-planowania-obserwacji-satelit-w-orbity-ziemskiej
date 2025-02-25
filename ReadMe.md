
---

# System do planowania obserwacji satelitów orbity ziemskiej

Projekt umożliwia planowanie obserwacji satelitów krążących wokół Ziemi poprzez optymalne dopasowanie dostępnych przedziałów czasowych obserwatoriów. Aplikacja przetwarza dane wejściowe (m.in. dane TLE oraz informacje o lokalizacjach obserwacyjnych) i generuje plan obserwacji, eliminując nakładanie się przedziałów oraz umożliwiając priorytetyzację obiektów.

## Spis treści

- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Instrukcja uruchomienia](#instrukcja-uruchomienia)
- [Opis interfejsu użytkownika](#opis-interfejsu-użytkownika)
- [Struktura projektu](#struktura-projektu)
- [Wkład i rozwój projektu](#wkład-i-rozwój-projektu)
- [Kontakt](#kontakt)

## Wymagania

- **Python 3.11** lub nowszy
- Zainstalowane biblioteki:
  - **tkinter** – tworzenie interfejsu graficznego
  - **skyfield** – obliczenia astronomiczne, przewidywanie pozycji satelitów
  - **pytz** – obsługa stref czasowych
  - **matplotlib** – wizualizacja danych (np. wykres Gantta)

## Instalacja

1. **Klonowanie repozytorium:**

   ```bash
   git clone https://github.com/mgromek99/System-do-planowania-obserwacji-satelit-w-orbity-ziemskiej.git
   ```

2. **Przejście do katalogu projektu:**

   ```bash
   cd System-do-planowania-obserwacji-satelit-w-orbity-ziemskiej
   ```

3. **Instalacja zależności:**

   Upewnij się, że masz zainstalowane następujące pakiety:
   - tkinter
   - skyfield
   - pytz
   - matplotlib

## Instrukcja uruchomienia


1. Upewnij się, że wszystkie wymagane zależności są zainstalowane.
2. Uruchom główny plik aplikacji:

   ```bash
   python main.py
   ```
3. Aplikacja uruchomi graficzny interfejs użytkownika. W przypadku modyfikacji kodu lub dodawania nowych funkcji, zaleca się pracę na osobnych gałęziach i stosowanie systemu kontroli wersji Git.

4. Po uruchomieniu aplikacji zobaczysz główny interfejs zawierający kilka sekcji:
   - **Application Feedback:** Okno wyświetlające komunikaty o błędach, informacjach o sukcesach operacji (np. eksport danych, błędy formatu daty itp.).
   - **TLE/Observatory JSON Viewer:** Interfejs do ładowania i podglądu plików JSON zawierających:
     - Dane TLE satelitów (TLE_LINE1, TLE_LINE2, itp.)
     - Dane punktów obserwacyjnych (lokalizacja, przedziały czasowe, kąt obserwacji, priorytety)
   - **Plan Viewer:** Miejsce generowania planu obserwacji. Po kliknięciu przycisku `[Re]Generate Plan` aplikacja:
     - Łączy dane satelitów i obserwatoriów,
     - Usuwa nakładające się przedziały czasowe,
     - Generuje listę przelotów satelitów oraz przedziałów czasowych (np. między zachodem a wschodem żeglarskim).
   - Opcje eksportu umożliwiają zapis wygenerowanego planu do pliku tekstowego lub graficznego (wykres Gantta).

5. Aby rozpocząć pracę, załaduj odpowiednie pliki JSON, ustaw priorytety oraz daty, a następnie wygeneruj plan obserwacji.

## Opis interfejsu użytkownika

- **Application Feedback:** Miejsce, gdzie aplikacja wyświetla komunikaty typu:
  - "Start time must be earlier than end time."
  - "Invalid date format."
  - "Content exported successfully." lub "Failed to export content. Error: ..."
- **TLE/Observatory JSON Viewer:** Umożliwia:
  - Otwieranie plików JSON z danymi TLE i punktami obserwacyjnymi.
  - Podgląd szczegółowych danych poszczególnych obiektów po kliknięciu przycisku „Toggle”.
  - Ustawianie priorytetów (liczby całkowite, gdzie wyższa wartość oznacza wyższy priorytet).
- **Plan Viewer:**
  - Generowanie planu na podstawie załadowanych danych.
  - Wyświetlanie listy przelotów satelitów oraz przedziałów czasowych (np. przedziały zmierzchu żeglarskiego).
  - Opcje eksportu – zapis do pliku tekstowego lub generowanie wykresu Gantta.

### Dane TLE

Pliki JSON z danymi TLE zawierają m.in.:
- **TLE_LINE1**: Pierwsza linia elementów orbitalnych (numer katalogowy NORAD, data epoki, pochodna średniego ruchu, BSTAR, itd.).
- **TLE_LINE2**: Druga linia z danymi dotyczącymi inklinacji, rektascensji, ekscentryczności, argumentu perygeum, anomalii średniej oraz numeru obiegu.

### Dane punktów obserwacyjnych

Plik JSON zawiera następujące pola:
- **PRIORITY** – Liczba całkowita (priorytet obserwatora).
- **COMMENT** – Komentarz opisujący lokalizację (np. nazwa miasta).
- **START_TIME** – Data i czas rozpoczęcia dostępności obserwacji.
- **END_TIME** – Data i czas zakończenia dostępności obserwacji.
- **ANGLE** – Kąt określający od którego momentu można obserwować satelity.
- **LATITUDE** – Szerokość geograficzna.
- **LONGITUDE** – Długość geograficzna.
- **TIMEZONE_OFFSET** – Przesunięcie strefowe względem UTC (zwykle 0).

### Kluczowe moduły

- **satellite_visibility.py:** Oblicza widoczność satelity dla danego obserwatora, wykorzystując dane TLE, daty oraz pozycję geograficzną.
- **generate_plan.py:** Główna funkcja generująca plan obserwacji na podstawie danych satelitarnych i obserwatoriów.
- **process_overlaps.py:** Moduł usuwający nakładające się przedziały czasowe, zapewniający spójność danych.
- **PlanViewer.py, JsonFileViewer.py, UniquePriorityPicker.py:** Moduły obsługujące interfejs graficzny oraz dodatkowe funkcjonalności (np. przypisywanie unikalnych priorytetów).

## Struktura projektu

```
├── main.py                   # Główny plik uruchamiający aplikację
├── generate_plan.py          # Generowanie planu obserwacji
├── process_overlaps.py       # Przetwarzanie nakładających się przedziałów czasowych
├── satellite_visibility.py   # Obliczanie widoczności satelitów
├── PlanViewer.py             # Interfejs graficzny do przeglądania planu obserwacji
├── JsonFileViewer.py         # Podgląd i obsługa plików JSON
├── UniquePriorityPicker.py   # Przypisywanie unikalnych priorytetów
├── README.md                 # Niniejsza dokumentacja
├── Sprawozdanie.pdf          # Szczegółowa dokumentacja
```

## Wkład i rozwój projektu

- **Autor:** Maciej Gromek
- Projekt jest rozwijany przy użyciu systemu kontroli wersji Git i platformy GitHub.
- Wszelkie propozycje poprawek, zgłoszenia błędów oraz nowe funkcjonalności są mile widziane. Prosimy o otwieranie issue lub przesyłanie pull requestów.

## Kontakt

W razie pytań lub sugestii prosimy o kontakt za pomocą:
- GitHub Issues na repozytorium projektu
- Bezpośredni kontakt e-mail: [macigro159@student.polsl.pl]

---