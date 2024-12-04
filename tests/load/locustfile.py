from locust import HttpUser, task, between
import json
import random
from typing import Dict, Any

class NutritionApiUser(HttpUser):
    wait_time = between(1, 3)  # Temps d'attente entre les requêtes
    
    def on_start(self):
        """Exécuté quand un utilisateur démarre"""
        # Login
        response = self.client.post("/auth/login", json={
            "email": f"user{random.randint(1, 1000)}@example.com",
            "password": "testpassword123"
        })
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
    
    def generate_meal_data(self) -> Dict[str, Any]:
        """Génère des données de repas aléatoires"""
        meal_types = ["breakfast", "lunch", "dinner", "snack"]
        return {
            "name": f"Test Meal {random.randint(1, 100)}",
            "type": random.choice(meal_types),
            "calories": random.randint(200, 1000),
            "protein": random.randint(10, 50),
            "carbs": random.randint(20, 100),
            "fat": random.randint(5, 30),
            "date": "2024-01-01T12:00:00Z"
        }
    
    @task(3)
    def view_meals(self):
        """Consultation des repas (haute fréquence)"""
        self.client.get(
            "/api/meals",
            headers=self.headers,
            name="/api/meals - GET"
        )
    
    @task(2)
    def add_meal(self):
        """Ajout de repas (fréquence moyenne)"""
        meal_data = self.generate_meal_data()
        self.client.post(
            "/api/meals",
            json=meal_data,
            headers=self.headers,
            name="/api/meals - POST"
        )
    
    @task(2)
    def view_analysis(self):
        """Consultation des analyses (fréquence moyenne)"""
        self.client.get(
            "/api/analysis/nutrients",
            headers=self.headers,
            name="/api/analysis/nutrients - GET"
        )
    
    @task(1)
    def update_profile(self):
        """Mise à jour du profil (basse fréquence)"""
        profile_data = {
            "weight": random.uniform(60, 90),
            "height": random.uniform(160, 190),
            "activity_level": random.choice(["low", "medium", "high"])
        }
        self.client.put(
            "/api/profile",
            json=profile_data,
            headers=self.headers,
            name="/api/profile - PUT"
        )

class AdminUser(HttpUser):
    wait_time = between(5, 10)
    weight = 1  # Moins d'admins que d'utilisateurs normaux
    
    def on_start(self):
        """Login admin"""
        response = self.client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "adminpass123"
        })
        if response.status_code == 200:
            self.token = response.json()["token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
    
    @task
    def view_metrics(self):
        """Consultation des métriques système"""
        self.client.get(
            "/api/admin/metrics",
            headers=self.headers,
            name="/api/admin/metrics - GET"
        )
    
    @task
    def view_users(self):
        """Liste des utilisateurs"""
        self.client.get(
            "/api/admin/users",
            headers=self.headers,
            name="/api/admin/users - GET"
        )
