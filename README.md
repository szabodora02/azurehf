# azurehf
# Fényképalbum Webalkalmazás (5. Feladat - Végleges változat)

Ez a projekt egy felhőalapú (PaaS) fényképalbum webalkalmazás, amely az 5. beadandó feladat követelményei alapján készült. Az alkalmazás ezen végleges verziója szétválasztott architektúrát használ: a webkiszolgáló az Azure környezetben fut, míg az adatok egy különálló, felhős PostgreSQL adatbázis-szerveren (Neon.tech) kapnak helyet.

## Élő alkalmazás (PaaS környezet)
A működő alkalmazás az alábbi linken érhető el:
[https://photo-apc9dee7gjg9hwa5.germanywestcentral-01.azurewebsites.net](https://photo-apc9dee7gjg9hwa5.germanywestcentral-01.azurewebsites.net)

## Megvalósított Funkciók

A feladatkiírásnak megfelelően az alábbi funkciók kerültek implementálásra:

* **Felhasználókezelés:** * Regisztráció, bejelentkezés és kijelentkezés (cookie-alapú session kezeléssel).
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
* **Frontend:** HTML, Jinja2 sablonok (Templates)
* **Kiszolgáló szerver:** Gunicorn, Uvicorn (worker)
* **Felhőkörnyezet (Web):** Microsoft Azure App Service (Linux PaaS)
* **Felhőkörnyezet (Adatbázis):** Neon.tech (Serverless PostgreSQL PaaS)

## Adatbázis és Fájltárolás (Szétválasztott Architektúra)

Az 5. feladat követelményeinek megfelelően az alkalmazás architektúrája szétválasztásra került:

1. **Adatbázis (Relációs adatok):** Az alkalmazás már nem lokális SQLite fájlt használ, hanem egy különálló **PostgreSQL** szerverhez csatlakozik a Neon.tech felhőjében. A kapcsolati adatokat a kód az Azure App Service környezeti változóiból (`DATABASE_URL`) olvassa ki, így a hitelesítő adatok nem szerepelnek a forráskódban.
2. **Képtárolás (Fizikai fájlok):** Mivel az Azure App Service ideiglenes fájlrendszert használ, a feltöltött képek (`media` mappa) mentése automatikusan a soha nem törlődő `/home/data/media` perzisztens könyvtárba történik, elkerülve az adatvesztést a szerver újraindulása esetén.
