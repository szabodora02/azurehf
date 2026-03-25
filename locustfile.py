import random
import string
import io
from locust import HttpUser, task, between

class PhotoAlbumUser(HttpUser):
    # Két művelet között a virtuális felhasználó 1-3 másodpercet vár
    wait_time = between(1, 3)

    def on_start(self):
        """Ez fut le először, amikor egy virtuális felhasználó 'megérkezik' az oldalra."""
        # Random email és jelszó generálása, hogy minden virtuális user egyedi legyen
        random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
        self.email = f"locust_{random_str}@example.com"
        self.password = "TestPassword123!"

        # 1. Regisztráció
        self.client.post("/auth/register", data={
            "email": self.email,
            "password": self.password
        })

        # 2. Bejelentkezés (A Locust automatikusan kezeli a visszakapott cookie-kat!)
        self.client.post("/auth/login", data={
            "email": self.email,
            "password": self.password
        })

    @task(3)
    def view_homepage(self):
        """A főoldal (kép lista) letöltése. Ez a leggyakoribb művelet (súly: 3)"""
        self.client.get("/")

    @task(1)
    def sort_images(self):
        """Képek rendezése dátum és név szerint (súly: 1)"""
        self.client.get("/?sort=date")
        self.client.get("/?sort=name")

    @task(2)
    def upload_image(self):
        """Kép feltöltése (súly: 2)"""
        # Létrehozunk egy apró "kamu" képet a memóriában
        dummy_image_content = b"Ez egy kamu kep tartalom a terhelesprobahoz."
        dummy_image = io.BytesIO(dummy_image_content)
        
        # Fájl és űrlap adatok küldése (Feltételezve, hogy a végpont '/upload' és vár egy 'file' meg egy 'name' mezőt)
        # Ha a te kódodban a kép neve mondjuk 'title', akkor a "name" kulcsot írd át arra!
        response = self.client.post("/upload", files={
            "file": ("test_image.jpg", dummy_image, "image/jpeg")
        }, data={
            "name": f"Locust Test Photo {random.randint(1, 1000)}"
        })

        # Ha a feltöltés sikeres volt, próbáljunk meg megnyitni egy képet (pl. az 1-es, 2-es vagy 3-as ID-jűt)
        if response.status_code in [200, 302, 303]:
            photo_id = random.randint(1, 3)
            self.client.get(f"/photos/{photo_id}", name="/photos/[id]")
