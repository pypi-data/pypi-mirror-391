import requests

class ComeBackPy:
    def __init__(self, base_url="https://comebackai.onrender.com/api/generate"):
        """
        Initialize the ComeBackPy client.
        base_url: URL of the backend API (default is your hosted Node backend)
        """
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        """
        Sends a prompt to the ComeBackPy backend and returns AI-generated text.
        """
        try:
            response = requests.post(
                self.base_url,
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("output", "No response received.")
        except Exception as e:
            return f"Error: {e}"
