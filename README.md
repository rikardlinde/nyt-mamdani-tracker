# NYT Mamdani Tracker

Automatisk övervakning av omnämnanden av "Mamdani" på New York Times förstasida (nytimes.com).

## Vad gör detta?

- Kontrollerar nytimes.com var 4:e timme
- Sparar alla omnämnanden med rubrik, länk och position på sidan
- Tar screenshot när Mamdani nämns
- Genererar en HTML-rapport

## Data

- `data/snapshots.json` — Alla datapunkter i JSON-format
- `data/screenshots/` — Screenshots (bara när omnämnanden hittas)
- `data/report.html` — Genererad HTML-rapport

---

## Setup-instruktioner (10 minuter)

### Steg 1: Skapa GitHub-repo

1. Gå till [github.com/new](https://github.com/new)
2. Fyll i:
   - **Repository name:** `nyt-mamdani-tracker`
   - **Description:** Övervakning av NYT:s bevakning av Mamdani
   - **Visibility:** Public (krävs för gratis Actions)
3. Klicka **Create repository**

### Steg 2: Ladda upp filerna

**Alternativ A: Via webben (enklast)**

1. På ditt nya repo, klicka **"uploading an existing file"**
2. Dra in alla filer från denna mapp (monitor.py, report.py, requirements.txt, README.md)
3. Klicka **Commit changes**

4. För `.github/workflows/monitor.yml`:
   - Klicka **Add file** → **Create new file**
   - Skriv filnamnet: `.github/workflows/monitor.yml`
   - Klistra in innehållet från filen
   - Klicka **Commit changes**

**Alternativ B: Via git (om du har git installerat)**

```bash
git clone https://github.com/DITT-ANVÄNDARNAMN/nyt-mamdani-tracker.git
cd nyt-mamdani-tracker
# Kopiera in alla filer hit
git add .
git commit -m "Initial setup"
git push
```

### Steg 3: Aktivera Actions

1. Gå till ditt repo på GitHub
2. Klicka på **Actions**-fliken
3. Om du ser en varning, klicka **"I understand my workflows, go ahead and enable them"**

### Steg 4: Testkör

1. Gå till **Actions** → **NYT Mamdani Monitor**
2. Klicka **Run workflow** → **Run workflow** (grön knapp)
3. Vänta ~2 minuter tills den blir grön
4. Kolla `data/snapshots.json` i repot för resultatet

---

## Hur använder jag datan för bloggen?

### Se rapporten

Efter första körningen finns `data/report.html` i repot. Du kan:

1. Ladda ner och öppna lokalt
2. Använda [GitHub Pages](https://pages.github.com/) för att publicera den som en webbsida

### Aktivera GitHub Pages (valfritt)

1. Gå till **Settings** → **Pages**
2. Under "Source", välj **Deploy from a branch**
3. Välj **main** branch och **/data** folder
4. Rapporten blir tillgänglig på: `https://DITT-ANVÄNDARNAMN.github.io/nyt-mamdani-tracker/report.html`

---

## Anpassa

### Ändra sökterm

I `monitor.py`, ändra:
```python
SEARCH_TERM = "mamdani"
```

### Ändra frekvens

I `.github/workflows/monitor.yml`, ändra cron:
```yaml
# Var 4:e timme (standard)
- cron: '0 */4 * * *'

# Varje timme
- cron: '0 * * * *'

# Var 6:e timme
- cron: '0 */6 * * *'
```

---

## Felsökning

### Workflowen misslyckas

Kolla loggen under Actions-fliken. Vanliga orsaker:
- Timeout vid sidladdning (NYT kan vara långsam)
- Playwright-installation misslyckades

### Inga omnämnanden hittas trots att de borde finnas

NYT:s HTML-struktur kan ha ändrats. Kontakta mig så uppdaterar vi parsern.

---

## Licens

MIT — använd fritt.
