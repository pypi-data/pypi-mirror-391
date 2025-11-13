import requests
import urllib.parse


class Widgets:
    def __init__(self, session, logger, base_url, workspace_instance):
        self.session = session
        self.logger = logger
        self.base_url = base_url
        self.workspace_instance = workspace_instance

    def get_widget(self, widget_id: str):
        """
        Retrieve widget details by widget ID.

        :param widget_id: ID of the widget to retrieve.
        :return: Dictionary containing widget details.
        :raises ValueError: If widget_id is missing or API returns an error.
        :raises requests.exceptions.HTTPError: For HTTP-level errors.
        """
        if not widget_id:
            raise ValueError("widget_id is required to get the widget details")

        url = f"{self.base_url}/rest/v17/analytics/widget/{widget_id}/get"

        try:
            response = self.session.get(url)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Widget response: {resp}")

            if not resp or resp.get("error", True):
                message = resp.get("message", "Failed to retrieve widget details.")
                self.logger.error(f"Widget retrieval failed: {message}")
                raise ValueError(message)

            data = resp.get("data", {}).get("elements", [])
            if not data:
                raise ValueError(f"No widget data found for ID {widget_id}")

            self.logger.info(f"Widget details retrieved successfully for ID {widget_id}")
            return data[0]

        except requests.exceptions.RequestException as http_err:
            # Safely parse response JSON if possible
            try:
                error_response = response.json()
                status_code = error_response.get("statusCode", response.status_code)
                error_message = error_response.get("message", str(http_err))
            except Exception:
                status_code = response.status_code
                error_message = str(http_err)

            formatted_error = f"{status_code} Error: {error_message}"
            self.logger.error(f"HTTP error occurred while fetching widget: {formatted_error}")
            raise requests.exceptions.HTTPError(formatted_error)

        except Exception as e:
            self.logger.exception(f"Unexpected error occurred while fetching widget: {e}")
            raise

    def post_widget(self, payload: dict, dashboard_id: str):
        """
        Add a widget to a dashboard
        :param payload: Dictionary containing widget details to be added.
        :param dashboard_id: Dashboard ID where widget needs to be added.
        :return: API response JSON
        """

        if not dashboard_id:
            raise ValueError("dashboard_id is required to add widget")

        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary containing widget details")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/{dashboard_id}/widgets/add"
            self.logger.info(f"POST URL: {url}")
            self.logger.info(f"POST Payload: {payload}")

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Widget added successfully to dashboard {dashboard_id}")
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

    def put_widget(self, widget_id: str, payload: dict):
        """
        Update an existing dashboard widget

        :param widget_id: ID of the widget to update
        :param payload: Dictionary containing updated widget details
        :return: API response JSON
        """

        if not widget_id:
            raise ValueError("widget_id is required to update the widget")

        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary containing widget details")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/widget/edit/{widget_id}"
            self.logger.info(f"PUT URL: {url}")
            self.logger.info(f"PUT Payload: {payload}")

            response = self.session.put(url, json=payload)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Widget {widget_id} updated successfully")
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
        
    def delete_widget(self, widget_id: str):
        """
        Delete a dashboard widget (Analytics API)

        :param widget_id: ID of the widget to delete
        :return: API response JSON
        """

        if not widget_id:
            raise ValueError("widget_id is required to delete the widget")

        try:
            url = f"{self.base_url}/rest/v17/analytics/reports/widget/delete/{widget_id}"
            self.logger.info(f"DELETE URL: {url}")

            response = self.session.delete(url)
            response.raise_for_status()

            resp = response.json()
            self.logger.info(f"Response: {resp}")

            if resp.get("error") is False:
                self.logger.info(f"Widget {widget_id} deleted successfully")
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
