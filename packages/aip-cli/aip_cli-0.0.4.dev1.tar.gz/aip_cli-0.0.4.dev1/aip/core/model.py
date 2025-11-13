import json
import os
import sys
from abc import ABCMeta

from aip.utils.console import console, err_console

from rich.pretty import Pretty


class ServiceModel(metaclass=ABCMeta):
    service_name = None

    def __init__(self, client, output):
        self._client = client
        self._url = os.getenv("AIP_URL", "https://aiwb.ai-portal.dev1.altium.com/")
        # self._env = self._derive_env_from_url(self._url)
        self.output = output

    def get_organization_name(self):
        user_schema = self._client.get_user_schema()
        if not user_schema:
            self.stderr("Unable to retrieve user's organization name")

        return user_schema

    def get_current_user_sub(self):
        user_sub = self._client.get_user_sub()
        if not user_sub:
            self.stderr("Unable to retrieve user's organization name")

        return user_sub


    @staticmethod
    def _derive_env_from_url(url):
        """
        Derive the environment from the URL.
        """
        url_lower = url.lower()
        if "ai-d." in url_lower or "localhost" in url_lower:
            return "dev"
        if "ai-t." in url_lower:
            return "test"
        if "ai-s." in url_lower:
            return "stag"
        if "ai." in url_lower:
            return "prod"
        raise ValueError("Environment not specified in URL")

    @staticmethod
    def _console(data, output="text", stderr=False, pretty=True):
        _console = console
        if stderr:
            _console = err_console
            pretty = False
            if isinstance(data, dict) and output != "json":
                data = data.get("message")
        if output == "json":
            try:
                data = json.dumps(data)
            except (TypeError, ValueError):
                _console = _console.print
                data = Pretty(data, indent_guides=False, expand_all=True)
            else:
                _console = _console.print_json
        elif output == "text":
            _console = _console.out
            pretty = False
        else:
            _console = _console.print
            if pretty:
                data = Pretty(data, indent_guides=False, expand_all=True)
        _console(data)

    def stdout(self, data):
        self._console(data, self.output)
        sys.exit(0)

    def stderr(self, data):
        self._console(data, self.output, stderr=True)
        sys.exit(1)

    def process(self, path, method="GET", **kwargs):
        res, err = self._client.request(f"{self._url}/{path}", method, **kwargs)
        if err:
            self.stderr(res)
        self.stdout(res)

    @classmethod
    def is_service(cls, service_name):
        if not cls.service_name:
            raise TypeError(
                "Subclass of ServiceModel needs to have the `service_name` class attribute."
            )
        return service_name == cls.service_name
