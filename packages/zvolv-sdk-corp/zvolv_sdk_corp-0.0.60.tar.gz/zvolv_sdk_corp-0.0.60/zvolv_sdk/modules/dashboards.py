import json
import requests
import urllib.parse


class Dashboards:
    def __init__(self, session, logger, base_url, workspace_instance):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = workspace_instance

    def get_all_dashboards(self, workflow_type_id: str, dashboard_type:str="DASHBOARD"):
        """
        Get all dashboards with the specified workflow type and type.

        :param workflow_type_id: WorkflowTypeID filter (default=2)
        :param dashboard_type: Type filter (default="DASHBOARD")
        :return: List of dashboards (API response JSON)
        """

        try:
            filter_payload = {
                "WorkflowTypeID": workflow_type_id,
                "Type": dashboard_type
            }

            url = f"{self.base_url}/rest/v17/analytics/reports/get"
            self.logger.info(f"GET URL: {url}")
            self.logger.info(f"Filter: {filter_payload}")

            response = self.session.get(
                url,
                params={"filter": json.dumps(filter_payload)}
            )
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Dashboards retrieved successfully")
                return resp["data"]["elements"]
            else:
                raise ValueError(resp.get("message", "Unknown API error"))

        except requests.exceptions.RequestException as http_err:
            try:
                error_response = response.json()
            except:
                error_response = {}

            status_code = error_response.get("statusCode", response.status_code)
            error_message = error_response.get("message", str(http_err))

            full_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP request failed: {full_error}")
            raise requests.exceptions.HTTPError(full_error)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e

    def get_dashboard(self, dashboard_id, workflow_type_id=2):
        """
        Get dashboard details using the new analytics API.

        :param dashboard_id: Dashboard ID (ex: 73)
        :param workflow_type_id: WorkflowTypeID for filtering (default is 2)
        :return: Dashboard data/elements
        """
        if not dashboard_id:
            raise ValueError("dashboard_id is required to get the dashboard data")

        try:
            filter_payload = {
                "WorkflowTypeID": workflow_type_id,
                "Type": "DASHBOARD"
            }

            url = f"{self.base_url}/rest/v17/analytics/reports/get/{dashboard_id}"
            self.logger.info(f"GET URL: {url}")

            response = self.session.get(
                url,
                params={"filter": json.dumps(filter_payload)}  # attaches filter as URL param
            )
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Dashboard Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Dashboard data retrieved successfully for ID {dashboard_id}")
                return resp['data']['elements'][0]
            raise ValueError(resp.get("message", "Unknown API error"))

        except requests.exceptions.RequestException as http_err:
            try:
                error_response = response.json()
            except:
                error_response = {}

            status_code = error_response.get("statusCode", response.status_code)
            error_message = error_response.get("message", str(http_err))

            full_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP request failed: {full_error}")
            raise requests.exceptions.HTTPError(full_error)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e

    def post_dashboard(self, payload: dict):
        """
        Create a new dashboard

        :param payload: Dictionary containing new dashboard details
        :return: API response JSON
        """

        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary containing dashboard details")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/add"
            self.logger.info(f"POST URL: {url}")
            self.logger.info(f"POST Payload: {payload}")

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Dashboard created successfully")
                return resp
            else:
                raise ValueError(resp.get("message", "Unknown API error"))

        except requests.exceptions.RequestException as http_err:
            try:
                error_response = response.json()
            except:
                error_response = {}

            status_code = error_response.get("statusCode", response.status_code)
            error_message = error_response.get("message", str(http_err))

            full_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP request failed: {full_error}")
            raise requests.exceptions.HTTPError(full_error)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e

    def put_dashboard(self, dashboard_id: int, payload: dict):
        """
        Update a dashboard

        :param dashboard_id: ID of the dashboard to update
        :param payload: Dictionary containing updated dashboard details
        :return: API response JSON
        """

        if not dashboard_id:
            raise ValueError("dashboard_id is required to update the dashboard")

        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary containing dashboard details")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/edit/{dashboard_id}"
            self.logger.info(f"PUT URL: {url}")
            self.logger.info(f"PUT Payload: {payload}")

            response = self.session.put(url, json=payload)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Dashboard {dashboard_id} updated successfully")
                return resp
            else:
                raise ValueError(resp.get("message", "Unknown API error"))

        except requests.exceptions.RequestException as http_err:
            try:
                error_response = response.json()
            except:
                error_response = {}

            status_code = error_response.get("statusCode", response.status_code)
            error_message = error_response.get("message", str(http_err))

            full_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP request failed: {full_error}")
            raise requests.exceptions.HTTPError(full_error)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e

    def delete_dashboard(self, dashboard_id: int):
        """
        Delete a dashboard

        :param dashboard_id: ID of the dashboard to delete
        :return: API response JSON
        """

        if not dashboard_id:
            raise ValueError("dashboard_id is required to delete the dashboard")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/delete/{dashboard_id}"
            self.logger.info(f"DELETE URL: {url}")

            response = self.session.delete(url)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Dashboard {dashboard_id} deleted successfully")
                return resp
            else:
                raise ValueError(resp.get("message", "Unknown API error"))

        except requests.exceptions.RequestException as http_err:
            try:
                error_response = response.json()
            except:
                error_response = {}

            status_code = error_response.get("statusCode", response.status_code)
            error_message = error_response.get("message", str(http_err))

            full_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP request failed: {full_error}")
            raise requests.exceptions.HTTPError(full_error)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise e
