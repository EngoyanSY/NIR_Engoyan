from locust import HttpUser, TaskSet, task, between
import random as rnd


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)
    host = "http://127.0.0.1:8000"
    fixed_count = 20
    spawn_rate = 2

    @task(1)
    def check_vuz_prog_page(self):
        vuz_id = rnd.randint(1, 100)
        with self.client.get(f"/vuz/2025/prog/{vuz_id}/", name=f"vuz/2025/prog/{vuz_id}/", catch_response=True) as response:
            if response.status_code == 200:
                if len(response.content) > 150000:
                    response.failure(f"Too large response: {len(response.content) / 1024} > 150 Кбайт")
                else:
                    response.success()
            else:
                response.failure("Response status code is not 200")