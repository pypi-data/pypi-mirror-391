import logging

from .client import Client
from .model import ServiceModel

logger = logging.getLogger(__name__)

class MLOps(ServiceModel):
    service_name = "mlops"

    def __init__(self, client: Client | None = None, output: str | None = 'json'):
        super().__init__(client, output)

    def list_models(self):
        response, error = self._client.request(
            f"{self._url}/api/model/list",
        )
        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def list_experiments(self):
        response, error = self._client.request(
            f"{self._url}/api/experiment/list",
        )
        if error:
            self.stderr(response)
        else:
            self.stdout(response)

    def train(self, payload: dict):
        response, error = self._client.request(
            f"{self._url}/api/train",
            method="post",
            data=payload
        )
        if error:
            # self.stderr(response) # temporary to provide the mock response
            # mocking response of train
            mock_response = {
                "job_id": "job_9n4zx",
                "status": "Queued",
                "created_at": "2025-10-13T10:15:20Z",
                "message": "Training job submitted successfully"
            }
            self.stdout(mock_response)
        else:
            self.stdout(response)

    def status(self, experiment_id: str, experiment_type: str):
        self.stdout("Running status subcommand under MLOPS")
        response, error = self._client.request(
            f"{self._url}/api/{experiment_type}/status/{experiment_id}",
        )
        if error:
            # self.stderr(response) # temporary to provide the mock response
            # mocking response of train
            mock_response = {
                "job_id": "job_9n4zx",
                "type": "train",
                "status": "Running",
                "created_at": "2025-10-13T10:15:20Z",
                "started_at": "2025-10-13T10:16:02Z"
            }
            self.stdout(mock_response)
        else:
            self.stdout(response)

    def result(self, experiment_id: str, experiment_type: str):
        response, error = self._client.request(
            f"{self._url}/api/{experiment_type}/result/{experiment_id}",
        )
        if error:
            # self.stderr(response) # temporary to provide the mock response
            # mocking response of train
            mock_response = {
                "job_id": "job_9n4z8x",
                "status": "Completed",
                "finished_at": "2025-10-13T10:25:00Z",
                "result": {
                    "metrics": {
                        "metric_name": "top1_acc",
                        "value": 0.762,
                        "at_epoch": 1,
                    }
                }
            }
            self.stdout(mock_response)
        else:
            self.stdout(response)

    def deploy(self, payload: dict):
        if payload["deployment_backend"] == "cmn_app":
            input_video_path = payload["input_video"]
            # stream the video directly to backend
        elif payload["deployment_backend"] == "app_register":
            app_location_path = payload["app_location"]
            # push the files in app_location dir to backend to be pushed to s3 bucket
        response, error = self._client.request(
            f"{self._url}/api/deploy",
            method="post",
            data=payload
        )
        if error:
            # self.stderr(response) # temporary to provide the mock response
            # mocking response of train
            mock_response = {
                "job_id": "job_9n4zx",
                "status": "Queued",
                "created_at": "2025-10-13T10:15:20Z",
                "message": "Deploy job submitted successfully"
            }
            self.stdout(mock_response)
        else:
            self.stdout(response)
