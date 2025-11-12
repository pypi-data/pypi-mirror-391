import requests


class API(object):

    URL = "https://api.onomondo.com/"
    SOFTSIM_ENDPOINT = "/sims/profiles"
    MAX_COUNT = 1000

    def __init__(self, key: str, url: str = URL):
        self.url = url
        self.key = key

    def softsim_fetch(self, quantity: int) -> dict:
        """
        Fetch softSIM profiles from API

        Args:
            quantity (int): Number of profiles to be fetched

        Raises:
            ValueError: If quantity is above max limit
            ValueError: If API has not been provided
            HTTPError: If request has failed

        Returns:
            dict: List of encrypted profiles ({"imsi", "profile"})
        """

        # Sanity checks
        if quantity > self.MAX_COUNT:
            raise ValueError(f"Quantity exceeds request max count")
        if self.key is None:
            raise ValueError("No API key provided")

        session = requests.Session()
        response = session.get(
            url=self.url.rstrip("/") + self.SOFTSIM_ENDPOINT,
            headers={"Authorization": self.key, "content-type": "application/json"},
            json={"count": quantity},
        )
        response.raise_for_status()

        return response.json()["profiles"]
