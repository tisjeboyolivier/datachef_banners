import random
from locust import HttpUser, task, constant


class MyUser(HttpUser):
    wait_time = constant(1)

    @task
    def query_api(self):
        self.client.post("/get-banners", json={"cam_id":7, "tq":random.randint(1,4)})
