# Testplan – Toolshop (Practice Software Testing)

Version: 1.0  
Stand: 2025-12-26  
Gültig für: dieses Repository (Docker-Compose Stack + Robot Framework UI Tests + pytest API Tests)

---

## Inhaltsverzeichnis

1. Ziel und Zweck  
2. System under Test  
3. Testziele  
4. Scope  
5. Teststrategie  
6. Testarten und Abdeckung  
7. Testdaten und Datenmanagement  
8. Testumgebungen  
9. Tooling und Infrastruktur  
10. Testdurchführung  
11. Entry-/Exit-Kriterien  
12. Defect- und Incident-Management  
13. Reporting und Metriken  
14. Risiken und Gegenmaßnahmen  
15. Wartung, Clean Code und Doku-Standards  
16. Appendix: Test-Inventar (UI + API)

---

## 1. Ziel und Zweck

Dieser Testplan beschreibt, **wie** wir die Toolshop-Anwendung automatisiert testen, **welche** Qualitätsziele abgedeckt werden und **unter welchen Bedingungen** ein Build als „lieferbar“ gilt.

Der Plan ist so geschrieben, dass ein neuer Entwickler/Tester in kurzer Zeit:
- die Testarchitektur versteht,
- Tests lokal/CI reproduzieren kann,
- weiß, wo Artefakte liegen,
- und welche Regeln für Erweiterungen gelten.

---

## 2. System under Test

### 2.1 Komponenten (Docker Compose)

- **angular-ui** (Frontend) – HTTP Port (default 4200, in CI random)
- **web** (nginx) – Reverse Proxy und API Routing – HTTP Port (default 8091, in CI random)
- **laravel-api** (Backend) – Laravel/PHP-FPM
- **mariadb** – Persistente Datenbank

### 2.2 Schnittstellen

- UI: `BASE_URL` (z. B. `http://localhost:4200`)
- API Doku: `API_DOC_URL` (z. B. `http://localhost:8091/api/documentation`)
- API Endpunkte (typisch): `/products`, `/brands`, `/categories`, `/users/login`, etc.

---

## 3. Testziele

### 3.1 Funktionale Ziele
- **Grundfunktionalität**: UI lädt, Navigation vorhanden, Produkte sichtbar.
- **Kern-Use-Cases**:
  - Login (positiv/negativ)
  - Product Listing / Product Details
  - Filter (Brand/Category)
  - Search (Treffer & keine Treffer)
  - Cart (Add-to-cart, Persistenz, Inhalte)

### 3.2 Qualitätsziele (Testautomatisierung)
- **Determinismus**: vor jedem Lauf wird die DB per `migrate:fresh --seed` in einen definierten Zustand gebracht.
- **Stabilität**: keine “sleep”-basierte Flakiness; stattdessen robuste Waits und State-Checks.
- **Nachvollziehbarkeit**: Artefakte (Robot Reports + Screenshots, Pytest JUnit) werden immer erzeugt und in CI hochgeladen.
- **Gating**: Smoke-Testset als Quality Gate, Regression nur wenn Smoke grün.

---

## 4. Scope

### 4.1 In Scope
- UI Tests (Robot Framework + Browser Library):
  - Smoke: schneller „is it alive“-Gate
  - Regression: breitere Abdeckung der Kernflows
- API Tests (pytest + requests):
  - Smoke: zentrale Endpunkte erreichbar, Basisschema ok
  - Regression: Verhalten (Filter/Sort/Auth) soweit in Spec beschrieben und implementiert
- Docker-Compose Start, Wait-Strategie, Seed-Verifikation

### 4.2 Out of Scope (aktuell)
- Performance-/Lasttests (kann später ergänzt werden)
- Security Scans (ZAP, SAST, Dependency scanning – optional)
- Mobile/Responsive UI Tests
- Browser-Matrix (aktuell nur Chromium/Playwright)

> Out-of-scope heißt: wird nicht “grün/rot” bewertet, kann aber als optionaler Job ergänzt werden.

---

## 5. Teststrategie

### 5.1 Grundprinzipien
- **Shift-left**: Smoke läuft bei jedem PR als Gate.
- **Testpyramide** (praktisch):
  - API Tests: günstiger, schneller, breiter (wo sinnvoll)
  - UI Tests: teurer, dafür End-to-End Kernflüsse
- **Selectors**: bevorzugt `data-test` Attribute.
- **Warte-Logik**: “wait for UI state” statt sleeps.

### 5.2 Tagging / Suiten
- Robot: Tags `smoke` und `regression` (Ausführung über `--include`)
- Pytest: Marker `smoke` und `regression` (Ausführung über `-m`)

### 5.3 Deterministische Daten
- Seed vor jedem Run.
- Seed-Verifikation: `Product::count() > 0` (Blocker, wenn nicht erfüllt).

---

## 6. Testarten und Abdeckung

### 6.1 UI Smoke (Gate)
Ziel: in < wenige Minuten feststellen, ob der Stack *grundsätzlich* funktioniert.

Beispiele:
- Homepage erreichbar (Navbar + Search sichtbar)
- Login möglich
- Products-Seite zeigt mindestens ein Produkt
- Navigation (Privacy/Contact) erreichbar

### 6.2 UI Regression
Ziel: Kernflows in realistischer Sequenz abdecken.

Beispiele:
- Search:
  - Treffer liefern Ergebnisse
  - „No results“-State korrekt (z. B. “Searched for: …” + „No products found“-Text / leere Liste)
- Filters:
  - Category Filter reduziert Liste
  - Brand Filter wirkt und lässt sich zurücksetzen
- Cart:
  - Add-to-cart
  - Cart enthält Produktname
  - Persistenz über Reload

### 6.3 API Smoke
Ziel: API ist erreichbar, Grundendpunkte funktionieren, OpenAPI-Doc lesbar.

Beispiele:
- `GET /products` liefert JSON mit Items
- `GET /brands`, `GET /categories` liefern plausible Daten
- OpenAPI Dokumentation erreichbar

### 6.4 API Regression
Ziel: Verhalten prüfen, ohne Annahmen zu erfinden.
- Filter/Sort nur testen, wenn in OpenAPI beschrieben.
- Auth-Endpunkte nur testen, wenn vorhanden und nutzbar.

Wichtig: Wenn ein Test “optional” ist (Feature in Spec fehlt), wird **geskippt** (kein roter Build).

---

## 7. Testdaten und Datenmanagement

### 7.1 Quelle der Testdaten
- Daten werden durch Seeder im Backend generiert.
- Testdaten sind **nicht** individuell gepflegt, sondern entstehen deterministisch aus Seedern.

### 7.2 Stabilität in UI Tests
- Wo möglich: erste Karte / erstes Element (Index 1) – robust gegen IDs.
- Keine harten Produkt-IDs in UI Tests.
- Für „No results“: Suche mit bewusst unmöglichem String, z. B. `zzzz__no_such_product__zzzz`.

### 7.3 Datenreset
- vor jedem Testlauf: `migrate:fresh --seed`
- optional: `make clean` (löscht Volumes) wenn DB/Ports/State hängen

---

## 8. Testumgebungen

### 8.1 Lokal
- Ports standardmäßig:
  - UI: 4200
  - Web/API: 8091
  - DB: 3306
- Artefakte: `artifacts/` (oder lokal `artifacts_local/`, je nach Konfiguration)

### 8.2 CI (GitHub Actions)
- Ports werden in CI auf **random host ports** gemappt, um Konflikte zu vermeiden.
- CI exportiert `BASE_URL` und `API_DOC_URL` dynamisch in `$GITHUB_ENV`.
- Headless Standard: `HEADLESS=true`.

---

## 9. Tooling und Infrastruktur

### 9.1 UI
- Robot Framework
- Robot Framework Browser (Playwright)
- `rfbrowser init` installiert Browser binaries

### 9.2 API
- pytest + requests
- JUnit XML output für CI (z. B. `artifacts/api/**/junit.xml`)

### 9.3 Docker / Compose
- Single stack via `docker compose`
- CI nutzt zusätzlich ein Override-Compose, um Host-Port-Binds zu vermeiden

---

## 10. Testdurchführung

### 10.1 Lokal (Makefile)
Empfohlene Flows:

```bash
make up
make seed
make smoke
make regression
make test-all
```

Wichtige ENV Overrides:
- `BASE_URL`, `HEADLESS`
- `API_DOC_URL`
- `COMPOSE_FILE`
- Ports: `UI_PORT`, `API_PORT` (wenn docker-compose das unterstützt)

### 10.2 CI
- Job **smoke**:
  - stack up → wait API → wait DB → seed → verify → UI tests smoke → upload artifacts
- Job **regression**:
  - nur wenn smoke erfolgreich → gleiches Setup → regression tests → upload artifacts

---

## 11. Entry-/Exit-Kriterien

### 11.1 Entry-Kriterien (bevor Tests starten)
- Docker stack läuft (`docker compose ps`)
- API Doku erreichbar (`API_DOC_URL`)
- DB ist healthy/reachable
- Seed erfolgreich + Produktcount > 0
- UI erreichbar (`BASE_URL`)

### 11.2 Exit-Kriterien (wann gilt ein Lauf als “grün”)
- **Smoke**:
  - alle Smoke Tests PASS
- **Regression**:
  - alle Regression Tests PASS
- Skips sind akzeptabel, wenn Feature nicht vorhanden/ nicht beschrieben ist.
- XFail/XPass wird im Reporting sichtbar bewertet (Konfiguration abhängig von pytest).

---

## 12. Defect- und Incident-Management

### 12.1 Defect-Workflow
1. Fehler im CI sichtbar (rot) inkl. Artefakte
2. Reproduzieren lokal (gleiche Steps, gleiche BASE_URL)
3. Ticket anlegen (kurze Beschreibung + Steps + Artefakte + Erwartung/ Ist)
4. Fix + Test anpassen (nur wenn Test falsch ist)

### 12.2 Artefakte, die bei Bugs Pflicht sind
- Robot: `log.html`, `report.html`, relevante Screenshots
- API: `junit.xml`, ggf. Response snippets im Testlog

---

## 13. Reporting und Metriken

### 13.1 Robot
- PASS/FAIL pro Suite/Test
- Timing pro Keyword (Robot log)
- Screenshots im Failure-Fall

### 13.2 Pytest
- JUnit XML (CI-Auswertung)
- Marker-basierte Selektion (smoke/regression)

### 13.3 Qualitätsmetriken (praktisch)
- Flake Rate (wie oft re-run nötig)
- Laufzeit Smoke/Regression
- Fail-Gründe: Infrastruktur vs. echter Bug vs. Testfehler

---

## 14. Risiken und Gegenmaßnahmen

| Risiko | Auswirkung | Gegenmaßnahme |
|---|---|---|
| Port-Konflikte (3306/8091/4200) | `Bind failed` | CI: random ports; lokal: Ports über ENV ändern oder alte Stacks stoppen |
| Seed nicht deterministisch / leer | Tests failen “random” | Seed-Verifikation + Reset via `migrate:fresh --seed` |
| UI flaky durch Timing | sporadische Fails | robuste Waits (UI ready gate, “Wait Until Keyword Succeeds”) |
| Selector-Drift | Tests brechen nach UI Änderungen | `data-test` Konvention, keine CSS-über-komplexen Selektoren |
| API/Spec drift | API regression unzuverlässig | Tests an OpenAPI koppeln, sonst skippen |

---

## 15. Wartung, Clean Code und Doku-Standards

### 15.1 Testcode-Standards
- **Keine sleeps** ohne Begründung; stattdessen State-based waits.
- Keywords in Robot: sprechende Namen, single responsibility.
- Wiederverwendung: gemeinsame Keywords in `ui-tests/resources/keywords/common.robot`.

### 15.2 Dokumentations-Standards
- README: Quickstart + Troubleshooting + Artefakte
- docs/CI.md: CI Ablauf + Debugging
- docs/TESTING.md: Tagging/Struktur/Erweiterung
- Änderungen an Tests/Infra → Doku mitziehen (PR-Checkliste)

---

## 16. Appendix: Test-Inventar (Beispiele)

### 16.1 UI Smoke (Beispiel-Suiten)
- Homepage reachable
- Navigation visible
- Login possible
- Product page reachable
- Search field available
- Extra: categories dropdown, privacy, contact

### 16.2 UI Regression (Beispiel-Suiten)
- Cart: add-to-cart, cart contains, persists after reload
- Filters: category filter, brand filter, clear brand filter
- Products: open details, add-to-cart visible, back to products, image src not empty
- Search: search returns matching, clear search restores, no-results state visible
- Sorting: sort by price

### 16.3 API Smoke/Regression (Beispiele)
- OpenAPI erreichbar/valid
- Products list returns data
- Optional: filter/sort (nur wenn Spec es beschreibt)
- Optional: auth/me/cart/favorites/invoices (nur wenn Endpoint vorhanden)

---

## Änderungslog

- 1.0 (2025-12-26): Initialer Testplan basierend auf aktuellem Docker/Robot/pytest Setup.

## 17. Testfall-Katalog (Automatisierung)

Diese Sektion beschreibt **konkret**, was jeder automatisierte Test prüft. Sie dient als gemeinsame Referenz für QA/Dev/CI und wird bei neuen Tests aktualisiert.

### 17.1 API Smoke (pytest, Marker: `smoke`)
| ID | Bereich | Tag | Datei/Test | Zweck | Haupt-Checks |
|---|---|---|---|---|---|
| API-SM-01 | API | smoke | api-tests/tests/smoke/test_api_smoke.py::test_swagger_ui_is_reachable | API-Doku erreichbar | GET API Docs liefert 200 + HTML Titel |
| API-SM-02 | API | smoke | ...::test_openapi_spec_is_loadable | OpenAPI Spec ladbar | Spec ist JSON-Dict und enthält paths |
| API-SM-03 | API | smoke | ...::test_products_list_returns_200 | Produktliste erreichbar | GET /products liefert 200 + JSON Content-Type |
| API-SM-04 | API | smoke | ...::test_products_list_is_not_empty | Produktliste nicht leer | Mind. 1 Produkt vorhanden (nach Seed) |
| API-SM-05 | API | smoke | ...::test_product_details_for_first_item | Produktdetails abrufbar | GET /products/{id} liefert 200 + id + name/title |
| API-SM-06 | API | smoke | ...::test_categories_list_returns_200 | Kategorien erreichbar | GET /categories liefert 200 |
| API-SM-07 | API | smoke | ...::test_brands_list_returns_200 | Brands erreichbar | GET /brands liefert 200 |
| API-SM-08 | API | smoke | ...::test_filter_products_by_category_param_if_supported | Category-Filter funktioniert (falls vorhanden) | GET /products?category=... liefert 200 oder skip wenn nicht spezifiziert |
| API-SM-09 | API | smoke | ...::test_filter_products_by_brand_param_if_supported | Brand-Filter funktioniert (falls vorhanden) | GET /products?brand=... liefert 200 oder skip |
| API-SM-10 | API | smoke | ...::test_pagination_param_if_supported | Pagination funktioniert (falls vorhanden) | GET /products?page=2 liefert 200 oder skip |

### 17.2 UI Smoke (Robot, Tag: `smoke`)
| ID | Bereich | Tag | Datei/Test | Zweck | Haupt-Checks |
|---|---|---|---|---|---|
| UI-SM-01 | UI | smoke | ui-tests/smoke/home.robot | Homepage erreichbar | Navbar + Search sichtbar |
| UI-SM-02 | UI | smoke | ui-tests/smoke/navigation.robot | Navigation sichtbar | Navbar vorhanden |
| UI-SM-03 | UI | smoke | ui-tests/smoke/login.robot | Login möglich | Login mit Demo-User klappt, URL nicht /login |
| UI-SM-04 | UI | smoke | ui-tests/smoke/product.robot | Products geladen | Mind. 1 Product-Card sichtbar |
| UI-SM-05 | UI | smoke | ui-tests/smoke/search.robot | Search Feld verfügbar | Search input sichtbar |
| UI-SM-06 | UI | smoke | ui-tests/smoke/extra/categories_dropdown.robot | Categories Dropdown öffnet | Dropdown klickbar, Entries sichtbar |
| UI-SM-07 | UI | smoke | ui-tests/smoke/extra/contact_route.robot | Contact Seite erreichbar | Navigation /contact, Heading/Form sichtbar |
| UI-SM-08 | UI | smoke | ui-tests/smoke/extra/filters_panel_has_brands.robot | Brand Filter vorhanden | Mind. 1 brand checkbox sichtbar |
| UI-SM-09 | UI | smoke | ui-tests/smoke/extra/filters_panel_has_categories.robot | Category Filter vorhanden | Mind. 1 category checkbox sichtbar |
| UI-SM-10 | UI | smoke | ui-tests/smoke/extra/login_page_fields.robot | Login Felder vorhanden | Email+Password Felder sichtbar |
| UI-SM-11 | UI | smoke | ui-tests/smoke/extra/privacy_route.robot | Privacy Seite erreichbar | /privacy heading sichtbar |
| UI-SM-12 | UI | smoke | ui-tests/smoke/extra/product_details_add_to_cart_visible.robot | Details: Add to cart sichtbar | Erstes Produkt öffnen, Button sichtbar |
| UI-SM-13 | UI | smoke | ui-tests/smoke/extra/products_have_images.robot | Product Thumbnails sichtbar | Erste Card hat img sichtbar |
| UI-SM-14 | UI | smoke | ui-tests/smoke/extra/products_have_prices.robot | Product Price sichtbar | Erste Card zeigt Preis (z.B. €) |
| UI-SM-15 | UI | smoke | ui-tests/smoke/extra/products_route_is_reachable.robot | /products erreichbar | Direkt /products öffnet, Cards sichtbar |

### 17.3 API Regression (pytest, Marker: `regression`)
| ID | Bereich | Tag | Datei/Test | Zweck | Haupt-Checks |
|---|---|---|---|---|---|
| API-REG-01 | API | regression | api-tests/tests/regression/test_api_regression.py::test_openapi_has_info | OpenAPI Metadaten vorhanden | Spec enthält info/title/version |
| API-REG-02 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_schema_min_fields | Produktliste hat Mindestfelder | Jedes Produkt enthält id + name/title + price o.ä. |
| API-REG-03 | API | regression | api-tests/tests/regression/test_api_regression.py::test_categories_have_names | Kategorien haben Namen | Jede Kategorie enthält name/title |
| API-REG-04 | API | regression | api-tests/tests/regression/test_api_regression.py::test_brands_have_names | Brands haben Namen | Jede Brand enthält name/title |
| API-REG-05 | API | regression | api-tests/tests/regression/test_api_regression.py::test_product_details_endpoint_returns_same_id | Details liefern die gleiche ID | GET /products/{id} enthält gleiche id wie angefragt |
| API-REG-06 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_pagination_changes_items_if_supported | Pagination verändert Ergebnis (falls unterstützt) | Seite 1 != Seite 2 (oder skip) |
| API-REG-07 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_search_returns_subset_if_supported | Search reduziert Ergebnis (falls unterstützt) | Query liefert Teilmenge oder skip |
| API-REG-08 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_sort_price_asc_if_supported | Sortierung nach Preis (falls unterstützt) | Sort-Param liefert 200/4xx, aber kein 5xx |
| API-REG-09 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_filter_by_category_if_supported | Kategorie-Filter (falls unterstützt) | Filter liefert 200, kein 5xx, ggf. skip |
| API-REG-10 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_filter_by_brand_if_supported | Brand-Filter (falls unterstützt) | Filter liefert 200, kein 5xx, ggf. skip |
| API-REG-11 | API | regression | api-tests/tests/regression/test_api_regression.py::test_login_returns_token | Login gibt Token zurück | POST /users/login liefert token (JWT o.ä.) |
| API-REG-12 | API | regression | api-tests/tests/regression/test_api_regression.py::test_me_endpoint_requires_auth_if_present | Auth-Guard /me | Ohne Auth 401/403 oder skip wenn Endpoint fehlt |
| API-REG-13 | API | regression | api-tests/tests/regression/test_api_regression.py::test_invoices_list_requires_auth_if_present | Auth-Guard invoices | Ohne Auth 401/403 oder skip |
| API-REG-14 | API | regression | api-tests/tests/regression/test_api_regression.py::test_favorites_list_requires_auth_if_present | Auth-Guard favorites | Ohne Auth 401/403 oder skip |
| API-REG-15 | API | regression | api-tests/tests/regression/test_api_regression.py::test_cart_get_requires_auth_if_present | Cart-GET Verhalten | Ohne Auth 401/403/404 je nach API; mit Auth 200/404 |
| API-REG-16 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_endpoint_does_not_error_on_large_page_if_supported | Large page Param robust | Große page/pageSize verursacht kein 5xx (oder skip) |
| API-REG-17 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_endpoint_rejects_invalid_sort_value_if_supported | Invalid sort robust | Ungültiger sort verursacht kein 5xx (200/4xx ok) |
| API-REG-18 | API | regression | api-tests/tests/regression/test_api_regression.py::test_categories_endpoint_is_idempotent | Kategorien idempotent | 2x GET liefert konsistente Struktur |
| API-REG-19 | API | regression | api-tests/tests/regression/test_api_regression.py::test_brands_endpoint_is_idempotent | Brands idempotent | 2x GET konsistente Struktur |
| API-REG-20 | API | regression | api-tests/tests/regression/test_api_regression.py::test_products_endpoint_response_time_reasonable | Response time grob ok | /products antwortet < definierter Schwelle (z.B. 2s) |

### 17.4 UI Regression (Robot, Tag: `regression`)
| ID | Bereich | Tag | Datei/Test | Zweck | Haupt-Checks |
|---|---|---|---|---|---|
| UI-REG-01 | UI | regression | ui-tests/regression/cart/add_to_cart.robot | Add to Cart | Produkt öffnen und in Cart legen; Cart count/Badge aktualisiert |
| UI-REG-02 | UI | regression | ui-tests/regression/cart/cart_contains_added_product.robot | Cart enthält Produktname | Cart Seite zeigt Name des hinzugefügten Produkts |
| UI-REG-03 | UI | regression | ui-tests/regression/cart/cart_persists_after_reload.robot | Cart persistiert nach Reload | Reload behält Cart Inhalt (local storage/session) |
| UI-REG-04 | UI | regression | ui-tests/regression/filters/filter_by_category.robot | Filter by Category | Kategorie anhaken -> Ergebnisse ändern/Tag aktiv |
| UI-REG-05 | UI | regression | ui-tests/regression/filters/filter_by_brand.robot | Filter by Brand | Brand anhaken -> Ergebnisse ändern/Tag aktiv |
| UI-REG-06 | UI | regression | ui-tests/regression/filters/clear_brand_filter.robot | Clear Brand Filter | Filter setzen und wieder entfernen -> Ergebnisse wieder da |
| UI-REG-07 | UI | regression | ui-tests/regression/login/negative_login.robot | Negative Login | Falsche Credentials -> Fehlermeldung, bleibt auf /login |
| UI-REG-08 | UI | regression | ui-tests/regression/navigation/categories_dropdown_entries.robot | Categories Dropdown Entries | Dropdown enthält >=1 Eintrag |
| UI-REG-09 | UI | regression | ui-tests/regression/navigation/contact_page_form_present.robot | Contact Form vorhanden | Contact Seite hat Formularfelder + Submit |
| UI-REG-10 | UI | regression | ui-tests/regression/navigation/privacy_page_heading.robot | Privacy Heading | Privacy Seite zeigt Heading/Content |
| UI-REG-11 | UI | regression | ui-tests/regression/products/direct_products_access.robot | Direct /products | Direktzugriff lädt Cards |
| UI-REG-12 | UI | regression | ui-tests/regression/products/open_first_product_details.robot | Open Product Details | Erstes Produkt öffnen -> Details-Seite sichtbar |
| UI-REG-13 | UI | regression | ui-tests/regression/products/details_has_add_to_cart.robot | Details Add to Cart | Details-Seite hat Add-to-cart Button |
| UI-REG-14 | UI | regression | ui-tests/regression/products/back_to_products_after_details.robot | Back to Products | Von Details zurück -> Productliste sichtbar |
| UI-REG-15 | UI | regression | ui-tests/regression/products/open_two_products_titles_differ.robot | Two Products Titles differ | Zwei Produkte öffnen -> Titel sind verschieden |
| UI-REG-16 | UI | regression | ui-tests/regression/products/product_image_src_not_empty.robot | Image src not empty | Produktbild src ist nicht leer |
| UI-REG-17 | UI | regression | ui-tests/regression/search/search_results.robot | Search returns results | Suche nach existierendem Begriff -> Cards vorhanden |
| UI-REG-18 | UI | regression | ui-tests/regression/search/clear_search_restores_products.robot | Clear search restores | Search leeren -> Cards wieder sichtbar |
| UI-REG-19 | UI | regression | ui-tests/regression/search/no_results_empty_or_message.robot | No results state | Suche nach Unsinn -> entweder 'no products found' ODER 0 Cards |
| UI-REG-20 | UI | regression | ui-tests/regression/sorting/sort_by_price.robot | Sort by price | Sort Dropdown -> Preis sortiert (oder mind. kein Error) |

### 17.5 Pflege-Regeln (damit es nicht veraltet)
- **Jeder neue Test** muss in diesen Katalog aufgenommen werden (1 Zeile).
- In `pytest`: kurze Docstring pro Test (`"""Purpose…"""`) + sprechender Name.
- In Robot: pro Testcase eine `Documentation`-Zeile (oder auf Suite-Ebene).
- Wenn ein Test **bewusst** wacklig ist (flaky), markiere ihn (z.B. `xfail`/Skip) und dokumentiere den Grund + Ticket.
