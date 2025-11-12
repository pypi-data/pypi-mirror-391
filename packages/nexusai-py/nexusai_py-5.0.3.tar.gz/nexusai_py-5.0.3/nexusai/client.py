import requests
import json
from typing import Optional, Union, List, Dict, Any, Iterator
from .exceptions import (
    NexusAPIError,
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    ServerError,
    NotFoundError
)


class NexusAI:
    """
    Main client for interacting with the Nexus AI API.
    
    This client provides access to:
    - Image Generation (14 AI models)
    - Text Generation (20+ AI models with streaming support)
    - Akinator Game API
    
    Args:
        api_key (str): Your Nexus API key from https://nexus.drexus.xyz
        base_url (str, optional): Base URL for the API. Defaults to official endpoint.
    
    Example:
        >>> client = NexusAI(api_key="your-api-key")
        >>> result = client.generate_image(prompt="A sunset over mountains")
        >>> print(result['imageUrl'])
    """
    
    BASE_URL = "https://nexus.drexus.xyz"
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Nexus AI client.
        
        Args:
            api_key: Your API key from the Nexus dashboard
            base_url: Optional custom base URL
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions"""
        try:
            data = response.json()
        except ValueError:
            data = {"error": response.text}
        
        if response.status_code == 200 or response.status_code == 204:
            return data
        elif response.status_code == 400:
            raise BadRequestError(
                data.get("error", "Bad Request"),
                status_code=400,
                response=data
            )
        elif response.status_code == 401:
            raise AuthenticationError(
                "Invalid or missing API key",
                status_code=401,
                response=data
            )
        elif response.status_code == 404:
            raise NotFoundError(
                data.get("error", "Resource not found"),
                status_code=404,
                response=data
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded - 500 requests per day",
                status_code=429,
                response=data
            )
        elif response.status_code >= 500:
            raise ServerError(
                data.get("error", "Internal server error"),
                status_code=response.status_code,
                response=data
            )
        else:
            raise NexusAPIError(
                f"Unexpected error: {response.status_code}",
                status_code=response.status_code,
                response=data
            )
    
    def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 512,
        height: int = 512
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt using AI.
        
        Args:
            prompt: Text description of the image to generate
            model: AI model to use (default: "flux")
                Available models: flux, flux-realism, flux-anime, flux-3d,
                flux-pro, any-dark, turbo, stable-diffusion, and more
            width: Image width in pixels (default: 512, max: 2048)
            height: Image height in pixels (default: 512, max: 2048)
        
        Returns:
            Dictionary containing:
                - success: Boolean indicating success
                - imageUrl: Relative URL path to the generated image
                - model: Model used
                - prompt: Original prompt
                - size: Image dimensions
                - expiresIn: Expiration time
                - user: User information
        
        Example:
            >>> result = client.generate_image(
            ...     prompt="A futuristic city at sunset",
            ...     model="flux",
            ...     width=1024,
            ...     height=768
            ... )
            >>> full_url = f"https://nexus.drexus.xyz{result['imageUrl']}"
            >>> print(full_url)
        """
        payload = {
            "prompt": prompt,
            "model": model,
            "width": width,
            "height": height
        }
        
        response = self.session.post(
            f"{self.base_url}/v1/generate-image",
            json=payload
        )
        
        return self._handle_response(response)
    
    def get_full_image_url(self, image_url: str) -> str:
        """
        Convert relative image URL to full URL.
        
        Args:
            image_url: Relative URL from API response (e.g., "/data/generated-images/...")
        
        Returns:
            Full URL to the image
        
        Example:
            >>> result = client.generate_image(prompt="A cat")
            >>> full_url = client.get_full_image_url(result['imageUrl'])
        """
        if image_url.startswith("http"):
            return image_url
        return f"{self.base_url}{image_url}"
    
    def generate_text(
        self,
        model: str,
        prompt: str,
        userid: Optional[str] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 1.0,
        max_output_tokens: int = 8192,
        images: Optional[Union[str, List[str], Dict[str, str]]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Iterator[str]]:
        """
        Generate text using various AI models.
        
        Args:
            model: AI model to use (e.g., "gemini-2.5-flash", "gpt-4", "qwen-2.5-72b-instruct")
            prompt: The text prompt to generate from
            userid: Optional user ID for conversation history
            system_instruction: System instruction to control model behavior
            temperature: Sampling temperature (0-2, default: 1.0)
            max_output_tokens: Maximum tokens to generate (default: 8192)
            images: Image URL(s) or base64 data (Gemini only)
            stream: Enable real-time streaming responses
        
        Returns:
            If stream=False: Dictionary with completion and metadata
            If stream=True: Iterator yielding text chunks
        
        Available Models:
            - Google Gemini: gemini-2.5-flash, gemini-2.5-pro, gemini-2.0-flash
            - OpenAI: gpt-4
            - Meta: llama-3.3-70b-instruct
            - Alibaba: qwen2.5-coder-32b
            - DeepSeek: deepseek-r1, deepseek-v3.1
            - And many more!
        
        Example:
            >>> result = client.generate_text(
            ...     model="gemini-2.5-flash",
            ...     prompt="Explain quantum computing",
            ...     temperature=0.7
            ... )
            >>> print(result['completion'])
        
        Streaming Example:
            >>> for chunk in client.generate_text(
            ...     model="gemini-2.5-flash",
            ...     prompt="Write a story",
            ...     stream=True
            ... ):
            ...     print(chunk, end='', flush=True)
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
            "stream": stream
        }
        
        if userid:
            payload["userid"] = userid
        if system_instruction:
            payload["systemInstruction"] = system_instruction
        if images:
            payload["images"] = images
        
        if stream:
            return self._stream_text(payload)
        else:
            response = self.session.post(
                f"{self.base_url}/v1/text/generate",
                json=payload
            )
            return self._handle_response(response)
    
    def _stream_text(self, payload: Dict[str, Any]) -> Iterator[str]:
        """Handle streaming text generation"""
        response = self.session.post(
            f"{self.base_url}/v1/text/generate",
            json=payload,
            stream=True
        )
        
        if response.status_code != 200:
            self._handle_response(response)
        
        for line in response.iter_lines(decode_unicode=True):
            if line and line.startswith("data: "):
                data_str = line[6:]
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    if "chunk" in data:
                        yield data["chunk"]
                except json.JSONDecodeError:
                    continue
    
    def clear_conversation_history(self, userid: str) -> None:
        """
        Clear conversation history for a specific user.
        
        Args:
            userid: User ID whose history should be cleared
        
        Example:
            >>> client.clear_conversation_history("user123")
        """
        response = self.session.delete(
            f"{self.base_url}/v1/text/history/{userid}"
        )
        self._handle_response(response)
    
    def start_akinator_game(
        self,
        region: str = "en",
        child_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Start a new Akinator game session.
        
        Args:
            region: Language region (en, es, fr, de, it, pt, ru, jp, zh)
            child_mode: Enable child-friendly mode
        
        Returns:
            Dictionary containing:
                - gameId: Unique game identifier
                - question: First question
                - answers: Available answer options
                - progress: Current progress (0-100)
                - status: Game status
        
        Example:
            >>> game = client.start_akinator_game(region="en")
            >>> print(game['question'])
            >>> print(game['gameId'])
        """
        params = {
            "region": region,
            "childMode": str(child_mode).lower()
        }
        
        response = self.session.get(
            f"{self.base_url}/v1/games/akinator/start",
            params=params
        )
        
        return self._handle_response(response)
    
    def answer_akinator(
        self,
        game_id: str,
        answer: str
    ) -> Dict[str, Any]:
        """
        Answer the current Akinator question.
        
        Args:
            game_id: Game ID from start_akinator_game()
            answer: Your answer - one of:
                "yes", "no", "dont-know", "probably", "probably-not"
        
        Returns:
            Dictionary containing either:
                - Next question (if game continues)
                - Character guess (if game is solved)
        
        Example:
            >>> result = client.answer_akinator(game_id, "yes")
            >>> if 'solved' in result:
            ...     print(f"Found: {result['name']}")
            ... else:
            ...     print(result['question'])
        """
        valid_answers = ["yes", "no", "dont-know", "probably", "probably-not"]
        if answer not in valid_answers:
            raise ValueError(f"Answer must be one of: {', '.join(valid_answers)}")
        
        params = {"answer": answer}
        
        response = self.session.get(
            f"{self.base_url}/v1/games/akinator/answer/{game_id}",
            params=params
        )
        
        return self._handle_response(response)
    
    def akinator_go_back(self, game_id: str) -> Dict[str, Any]:
        """
        Go back to the previous question in Akinator.
        
        Args:
            game_id: Game ID
        
        Returns:
            Previous question data
        
        Example:
            >>> result = client.akinator_go_back(game_id)
            >>> print(result['question'])
        """
        response = self.session.get(
            f"{self.base_url}/v1/games/akinator/back/{game_id}"
        )
        
        return self._handle_response(response)
    
    def get_akinator_progress(self, game_id: str) -> Dict[str, Any]:
        """
        Check the current progress of an Akinator game.
        
        Args:
            game_id: Game ID
        
        Returns:
            Dictionary with progress (0-100) and status
        
        Example:
            >>> progress = client.get_akinator_progress(game_id)
            >>> print(f"Progress: {progress['progress']}%")
        """
        response = self.session.get(
            f"{self.base_url}/v1/games/akinator/progress/{game_id}"
        )
        
        return self._handle_response(response)
    
    def delete_akinator_game(self, game_id: str) -> None:
        """
        Delete an active Akinator game session.
        
        Args:
            game_id: Game ID to delete
        
        Example:
            >>> client.delete_akinator_game(game_id)
        """
        response = self.session.delete(
            f"{self.base_url}/v1/games/akinator/game/{game_id}"
        )
        
        if response.status_code != 204:
            self._handle_response(response)
