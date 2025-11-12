"""High-level client for interacting with the Simulacrum forecasting API."""

from typing import Any, Dict, Sequence

import numpy as np

from simulacrum.api import send_request
from simulacrum.config import BASE_URL
from simulacrum.exceptions import ApiError, AuthError
from simulacrum.models import ForecastRequest, ForecastResponse, ValidateAPIKeyResponse


class Simulacrum:
    """Client wrapper around Simulacrum's REST API.

    Example:
        >>> from simulacrum import Simulacrum
        >>> client = Simulacrum(api_key="sp_example_key")
        >>> forecast = client.forecast(series=[1.0, 1.1, 1.2], horizon=2, model="default")
        >>> forecast.shape
        (2,)
    """

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        """Create a client that can issue authenticated requests to Simulacrum.

        Args:
            api_key (str): Simulacrum API key that authorizes requests.
            base_url (str): Base URL for the API; defaults to the production endpoint.
        """
        if not isinstance(api_key, str) or not api_key.strip():
            raise TypeError("api_key must be a non-empty string.")
        if not isinstance(base_url, str) or not base_url.strip():
            raise TypeError("base_url must be a non-empty string.")

        self.api_key: str = api_key
        self.base_url: str = base_url
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def forecast(
        self, series: Sequence[float] | np.ndarray, horizon: int | None = None, model: str = "default"
    ) -> np.ndarray:
        """Request a forecast for the provided time series data.

        Parameters:
            series (Sequence[float] | numpy.ndarray): Historical time series data (1D or 2D) to use as forecast input.
            horizon (int, optional): Number of future periods to predict. Required for all models except ``"onsiteiq"``.
            model (str, optional): Model identifier to use for forecasting (default is ``"default"``).

        Returns:
            numpy.ndarray: Forecasted values as a NumPy array, ordered chronologically.

        Raises:
            TypeError: If ``series`` is not convertible to a 1D or 2D array of floats.
            ValueError: If ``series`` does not have valid dimensionality or ``horizon`` is not appropriate for the model.
            ApiError: If the API returns an error response.
            AuthError: If API key authentication fails.
        """

        series_to_send = np.asarray(series, dtype=float)
        payload: ForecastRequest = ForecastRequest(
            series=series_to_send, horizon=horizon, model=model
        )
        request_body: Dict[str, Any] = payload.model_dump()
        # Exclude optional fields that are None (e.g., horizon for onsiteiq)
        request_body = payload.model_dump(exclude_none=True)
        response_data: Dict[str, Any] = send_request(
            method="POST",
            url=f"{self.base_url}/{model}/v1/forecast",
            headers=self.headers,
            json=request_body,
        )
        validated_response: ForecastResponse = ForecastResponse.model_validate(
            response_data
        )
        return validated_response.get_forecast()

    def validate(self, model: str = "tempo") -> ValidateAPIKeyResponse:
        """Validate the configured API key and return its metadata.

        Returns:
            ValidateAPIKeyResponse: Structured validation details including key status and expiration date.

        Raises:
            AuthError: The API key is invalid or unauthorized.
            ApiError: An unexpected API error occurred.

        Example:
            >>> client = Simulacrum(api_key="sp_example_key")
            >>> validation = client.validate()
            >>> validation.valid
            True
        """
        response_data: Dict[str, Any] = send_request(
            method="GET",
            url=f"{self.base_url}/{model}/v1/validate",
            headers=self.headers,
            json=None,
        )

        return ValidateAPIKeyResponse.model_validate(response_data)
