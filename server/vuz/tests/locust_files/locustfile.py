from locust import HttpUser, task, between

class WebsiteUser(HttpUser):

    wait_time = between(1, 5)

    @task(5)
    def index_page(self):
        self.client.get("/", name="index")
    
    @task(3)
    def vuz_info_page(self):
        self.client.get("/vuz/217", name="vuz")
    
    @task(3)
    def vuz_program_page(self):
        self.client.get("/vuz/2025/prog/217/", name="program_page")
    
    @task(3)
    def vuz_profit_page(self):
        self.client.get("/vuz/2025/217/profit/", name="profit_page")

    @task(3)
    def analitic_page(self):
        self.client.get("/vuz/2025/analitic/district/?field_id=11.04.04", name="analitic_page")
    @task(3)
    def analitic_price(self):
        self.client.get("/vuz/analitic/price/?field_id=07.04.04&district_id=1&region_id=&year_from=2023&year_to=2025", name="analitic_price")
    
    @task(3)
    def profit_sorting(self):
        self.client.get("/vuz/2025/3/profit/?sort=fieldid&order=asc HTTP/1.1", name="profit_sorting")