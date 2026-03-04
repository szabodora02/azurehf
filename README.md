# azurehf
# Fényképalbum Webalkalmazás (4. Feladat)

Ez a projekt egy felhőalapú (PaaS) fényképalbum webalkalmazás, amely a 4. beadandó feladat követelményei alapján készült. Az alkalmazás jelenlegi verziója fájlalapú (SQLite) adatbázist használ, amely az Azure környezetben egy perzisztens tárolón fut.

##Élő alkalmazás (PaaS környezet)
A működő alkalmazás az alábbi linken érhető el:
**[https://photo-apc9dee7gjg9hwa5.germanywestcentral-01.azurewebsites.net]**

##Megvalósított Funkciók (1. Fázis)

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

Alkalmazott Technológiák

* **Backend:** Python 3.12, FastAPI
* **Adatbázis & ORM:** SQLite, SQLModel (SQLAlchemy)
* **Biztonság:** Jelszó hashelés (`pwdlib`, `bcrypt`)
* **Frontend:** HTML, Jinja2 sablonok (Templates)
* **Kiszolgáló szerver:** Gunicorn, Uvicorn (worker)
* **Felhőkörnyezet (PaaS):** Microsoft Azure App Service (Linux)

##Adatbázis és Fájltárolás (Azure Architektúra)
Mivel az Azure App Service ideiglenes fájlrendszert használ az alkalmazás futtatásához, az alkalmazás kódja fel van készítve arra, hogy felismerje a felhős környezetet. Azure-on futva a kód az adatbázist (`app.db`) és a feltöltött képeket (`media` mappa) automatikusan a soha nem törlődő `/home/data` perzisztens könyvtárba menti, így elkerülve az adatvesztést a szerver újraindulása esetén.
