from locust import HttpUser, task, between
import json

class LibraryAPIUser(HttpUser):

    wait_time = between(1, 3)
    
    def on_start(self):

        print(f"Користувач {self.environment.runner.user_count} почав тестування")
    
    @task(10)
    def get_books_load_test(self):

        with self.client.get("/api/v1/books/load-test", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    if "books" in json_response and "count" in json_response:
                        response.success()
                    else:
                        response.failure("Response doesn't contain expected fields")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"Got status code {response.status_code}")
    
    @task(3)
    def get_books_public(self):

        with self.client.get("/api/v1/books/public", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:

                response.success()
                print("Rate limit hit on public endpoint (expected)")
            else:
                response.failure(f"Unexpected status code {response.status_code}")
    
    @task(1)
    def health_check(self):

        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with status {response.status_code}")

class AdminUser(HttpUser):

    wait_time = between(2, 5)
    
    def on_start(self):

        self.login()
    
    def login(self):

        login_data = {
            "username": "testuser",
            "password": "123456"
        }
        
        with self.client.post("/auth/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    self.token = json_response.get("access_token")
                    if self.token:
                        response.success()
                        print("Admin user logged in successfully")
                    else:
                        response.failure("No access token in response")
                        self.token = None
                except json.JSONDecodeError:
                    response.failure("Login response is not valid JSON")
                    self.token = None
            else:
                response.failure(f"Login failed with status {response.status_code}")
                self.token = None
    
    @task(5)
    def get_books_authenticated(self):

        if not hasattr(self, 'token') or not self.token:
            self.login()
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with self.client.get("/api/v1/books", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:

                self.login()
                response.failure("Token expired, re-logging in")
            elif response.status_code == 429:

                response.success()
                print("Rate limit hit on authenticated endpoint")
            else:
                response.failure(f"Unexpected status code {response.status_code}")
    
    @task(1)
    def create_book(self):

        if not hasattr(self, 'token') or not self.token:
            self.login()
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        book_data = {
            "title": "Load Test Book",
            "author": "Locust Tester",
            "year_published": 2025,
            "genre": "testing"
        }
        
        with self.client.post("/api/v1/books", json=book_data, headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 401:
                self.login()
                response.failure("Token expired during book creation")
            elif response.status_code == 429:
                response.success()
                print("Rate limit hit on book creation")
            else:
                response.failure(f"Book creation failed with status {response.status_code}")