# Fényképalbum Webalkalmazás

Ez a projekt egy felhőalapú (PaaS) fényképalbum webalkalmazás. Az alkalmazás ezen végleges verziója szétválasztott architektúrát használ (Azure App Service + Neon.tech PostgreSQL), és fel van készítve a nagy terhelés alatti automatikus felskálázódásra.

## Élő alkalmazás (PaaS környezet)
A működő alkalmazás az alábbi linken érhető el:
[https://photo-apc9dee7gjg9hwa5.germanywestcentral-01.azurewebsites.net](https://photo-apc9dee7gjg9hwa5.germanywestcentral-01.azurewebsites.net)

## Megvalósított Funkciók

Az alábbi funkciók kerültek implementálásra:

* **Felhasználókezelés:** Regisztráció, bejelentkezés és kijelentkezés (cookie-alapú session kezeléssel).
* **Fényképek kezelése (jogosultsághoz kötve):**
  * Képek feltöltése és törlése. *(Csak bejelentkezett felhasználók számára elérhető, és mindenki csak a saját képét törölheti).*
* **Metaadatok:**
  * Minden feltöltött kép rendelkezik névvel (maximum 40 karakter) és feltöltési dátummal (Év-Hónap-Nap Óra:Perc formátumban).
* **Listázás és Rendezés:**
  * A feltöltött képek listázása.
  * A lista rendezhető **dátum** (legújabb elöl) és **név** szerint.
* **Kép megtekintése:**
  * A listában a "Megnyitás" gombra/linkre kattintva egy részletező oldal nyílik meg, ahol megjelenik maga a fizikai képfájl, a fotó neve, dátuma, és a tulajdonos számára a törlés funkció.

## Alkalmazott Technológiák

* **Backend:** Python 3.12, FastAPI
* **Adatbázis & ORM:** PostgreSQL, SQLModel (SQLAlchemy), `psycopg2-binary`
* **Biztonság:** Jelszó hashelés (`pwdlib`, `bcrypt`)
* **Frontend:** HTML, Jinja2 sablonok
* **Kiszolgáló szerver:** Gunicorn, Uvicorn (worker)
* **Felhőkörnyezet (Web):** Microsoft Azure App Service (Linux PaaS)
* **Felhőkörnyezet (Adatbázis):** Neon.tech (Serverless PostgreSQL PaaS)
* **Terheléspróba & DevOps:** Locust (Azure Cloud Shell-ből futtatva), Azure Autoscale, Azure Bicep (IaC), GitHub Actions (CI/CD)

## Adatbázis és Fájltárolás (Szétválasztott Architektúra)

Az alkalmazás architektúrája szétválasztásra került:

1. **Adatbázis (Relációs adatok):** Az alkalmazás már nem lokális SQLite fájlt használ, hanem egy különálló **PostgreSQL** szerverhez csatlakozik a Neon.tech felhőjében. A kapcsolati adatokat a kód az Azure App Service környezeti változóiból (`DATABASE_URL`) olvassa ki, így a hitelesítő adatok nem szerepelnek a forráskódban.
2. **Képtárolás (Fizikai fájlok):** Mivel az Azure App Service ideiglenes fájlrendszert használ, a feltöltött képek (`media` mappa) mentése automatikusan a soha nem törlődő `/home/data/media` perzisztens könyvtárba történik, elkerülve az adatvesztést a szerver újraindulása esetén.

---

## Automatikus Skálázódás és Terheléspróba

### 1. Az automatikus skálázódás (Autoscale) konfigurációja
A fényképalbum alkalmazást kiszolgáló Azure App Service környezetet egy magasabb (Production) csomagra skáláztuk fel a teszt idejére, hogy elérhetővé váljon az automatikus méretezés funkció. 

**Példánykorlátok (Instance limits):**
* Minimum példányszám: 1
* Maximum példányszám: 3
* Alapértelmezett: 1

**Méretezési szabályok (Scale rules):**
1. **Felskálázás (Scale out):** Ha a CPU terheltség átlaga meghaladja az 5%-ot legalább 1 percig, az alkalmazás automatikusan elindít +1 példányt. *(Megjegyzés: A küszöbértéket szándékosan alacsony, mivel a FastAPI alkalmazás rendkívül erőforrás-hatékony).*
2. **Visszaskálázás (Scale in):** Ha a CPU terheltség átlaga 30% alá esik legalább 5 percig, az alkalmazás leállít 1 példányt, ezzel optimalizálva a költségeket.

### 2. A terheléspróba konfigurációja és eszközei
A terheléspróbát nem lokális gépről, hanem **felhős környezetből (Azure Cloud Shell felügyelt Linux konténerből)** lett végrehajtva a hálózati sávszélesség-korlátok elkerülése végett. A teszteléshez a nyílt forráskódú **Locust** keretrendszert használtuk headless módban.

* **Terhelési paraméterek:** 500 egyidejű felhasználó (Concurrency), 50 új felhasználó/másodperc indítási sebességgel (Spawn rate).
* **Tesztesetek:** A szkript lefedi a fő funkciókat (regisztráció, belépés, lista folyamatos lekérése, rendezések, új memóriagenerált képek feltöltése és megnyitása).

**A terheléspróba szkriptje:** `locustfile.py`

### 3. Eredmények és Felskálázódás
A terheléspróba indítása után a szerver rövid idő alatt több mint 14 000 kérést dolgozott fel hibamentesen. A hirtelen megnövekedett forgalom hatására az Azure infrastruktúra érzékelte a CPU küszöbérték átlépését.

Az Azure Portal *Run history* metrikái alapján egyértelműen igazolható, hogy az automatikus skálázó motor működésbe lépett, és az alkalmazást kiszolgáló aktív példányok (Instances) számát **1-ről 2-re növelte**, sikeresen elosztva a terhelést. 

### 4. Tanulságok
* **Kód optimalizáltsága:** A FastAPI és a szétválasztott felhős adatbázis (Neon.tech PostgreSQL) annyira jól bírta a terhelést, hogy a szerver CPU-ja önmagában nehezen érte el a magas határértékeket, így a teszteléshez a skálázási szabályokat "érzékenyebbre" kellett hangolni.
* **Metrika késleltetés:** Az automatikus skálázás nem azonnali; a felhőszolgáltatónak időre van szüksége a megbízható CPU átlag kiszámításához, így kivédve a pillanatnyi forgalmi tüskék miatti felesleges felskálázásokat.
* **Felhős tesztelés:** Egy reális terheléspróbát kizárólag felhőből érdemes indítani, elkerülve a lokális hálózatok szűk keresztmetszeteit.

---

## Infrastructure-as-Code (IaC) Telepítés

A projekt teljes infrastruktúrájának és kódjának telepítése (CI/CD) automatizálva van a **GitHub Actions** és az **Azure Bicep** segítségével.

### Használt eszközök
* **IaC Nyelv:** Azure Bicep (a Microsoft natív infrastruktúra-leíró nyelve).
* **CI/CD Pipeline:** GitHub Actions.
* **Titkosítás:** GitHub Secrets (az Azure belépési kulcsok és az adatbázis URL biztonságos tárolására).

### Konfigurált komponensek (`infra/main.bicep`)
A Bicep fájl a következő felhős erőforrások deklaratív létrehozásáért és konfigurálásáért felel:
1. **Azure App Service Plan (`Microsoft.Web/serverfarms`):** A fizikai szerverkörnyezet biztosítása. Jelen esetben egy költséghatékony, Linux alapú, `F1` (Free) tier csomag.
2. **Azure Web App (`Microsoft.Web/sites`):** Maga az alkalmazásszerver, az alábbi beállításokkal:
   * **Környezet:** Python 3.12 futtatókörnyezet (`linuxFxVersion`).
   * **Biztonság:** Kötelező HTTPS kapcsolat (`httpsOnly: true`).
   * **Környezeti változók (App Settings):** A Bicep kód automatikusan és biztonságosan injektálja a `DATABASE_URL` változót az App Service-be a GitHub Secrets-ből, így az alkalmazás a külső (Neon.tech) adatbázishoz csatlakozik adatvesztés nélkül (Continuous Deployment).
   * **Build rendszer:** Az `SCM_DO_BUILD_DURING_DEPLOYMENT` bekapcsolása az Azure natív Oryx build motorjának használatához (pip csomagok automatikus telepítése a szerveren).

### A telepítési folyamat (Workflow)
Amikor új kód kerül a `main` ágra, a `.github/workflows/main_photo.yml` automatikusan lefut:
1. Hitelesíti magát az Azure-ban egy Service Principal segítségével.
2. Lefuttatja az IaC (`main.bicep`) telepítést az `azure/arm-deploy@v1` akcióval (létrehozza/frissíti az infrastruktúrát).
3. Telepíti a friss Python (`FastAPI`) forráskódot a felkonfigurált Web App-ra az `azure/webapps-deploy@v2` akcióval.
