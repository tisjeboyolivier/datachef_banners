import random
from locust import HttpUser, task, constant


class MyUser(HttpUser):
    wait_time = constant(1)

    @task
    def query_api(self):
        response = self.client.post("/get-banners", json={"cam_id":random.randint(1,50), "tq":random.randint(1,4)})
        print("Response text:", response.text)