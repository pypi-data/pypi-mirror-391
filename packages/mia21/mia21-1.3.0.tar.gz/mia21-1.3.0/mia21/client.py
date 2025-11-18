"""Main Mia21 client implementation."""

import requests
import json
import uuid
import base64
from enum import Enum
from typing import Optional, List, Generator, Dict, Any
from .models import ChatMessage, Space, InitializeResponse, ChatResponse, Tool, ToolCall, StreamEvent
from .exceptions import Mia21Error, ChatNotInitializedError, APIError


class ResponseMode(str, Enum):
    """Response mode for chat requests"""
    TEXT = "text"
    STREAM_TEXT = "stream_text"
    STREAM_VOICE = "stream_voice"
    STREAM_VOICE_ONLY = "stream_voice_only"


class VoiceConfig:
    """Configuration for voice output"""
    
    def __init__(
        self,
        enabled: bool = True,
        voice_id: str = "P7x743VjyZEOihNNygQ9",
        elevenlabs_api_key: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75
    ):
        """
        Initialize voice configuration.
        
        Args:
            enabled: Enable voice output
            voice_id: ElevenLabs voice ID
            elevenlabs_api_key: Customer's ElevenLabs API key (BYOK)
            stability: Voice stability (0.0-1.0)
            similarity_boost: Voice similarity boost (0.0-1.0)
        """
        self.enabled = enabled
        self.voice_id = voice_id
        self.elevenlabs_api_key = elevenlabs_api_key
        self.stability = stability
        self.similarity_boost = similarity_boost
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API requests"""
        return {
            "enabled": self.enabled,
            "voice_id": self.voice_id,
            "elevenlabs_api_key": self.elevenlabs_api_key,
            "stability": self.stability,
            "similarity_boost": self.similarity_boost
        }


class Mia21Client:
    """
    Mia21 Chat API Client
    
    Example:
        >>> from mia21 import Mia21Client
        >>> client = Mia21Client(api_key="your-api-key")
        >>> client.initialize()
        >>> response = client.chat("Hello!")
        >>> print(response.message)
    """
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.mia21.com",
        user_id: Optional[str] = None,
        timeout: int = 90,
        customer_llm_key: Optional[str] = None
    ):
        """
        Initialize Mia21 client.
        
        Args:
            api_key: Your Mia21 API key (optional if using BYOK)
            base_url: API base URL (default: production)
            user_id: Unique user identifier (auto-generated if not provided)
            timeout: Request timeout in seconds (default: 90)
            customer_llm_key: Your LLM API key for BYOK (OpenAI or Gemini)
        """
        self.api_key = api_key
        self.customer_llm_key = customer_llm_key
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.user_id = user_id or str(uuid.uuid4())
        self.timeout = timeout
        self.current_space = None
        self._session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key
        self._session.headers.update(headers)
    
    def list_spaces(self) -> List[Space]:
        """
        List all available spaces.
        
        Returns:
            List of Space objects
            
        Example:
            >>> spaces = client.list_spaces()
            >>> for space in spaces:
            ...     print(f"{space.id}: {space.name}")
        """
        try:
            response = self._session.get(
                f"{self.api_url}/spaces",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            # API returns list directly
            spaces_list = data if isinstance(data, list) else data.get("spaces", [])
            return [Space(**s) for s in spaces_list]
        except requests.RequestException as e:
            raise APIError(f"Failed to list spaces: {e}")
    
    def initialize(
        self,
        space_id: str = "dr_panda",
        bot_id: Optional[str] = None,
        llm_identifier: Optional[str] = None,
        llm_type: Optional[str] = None,
        user_name: Optional[str] = None,
        language: Optional[str] = None,
        generate_first_message: bool = True,
        incognito_mode: bool = False,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None
    ) -> InitializeResponse:
        """
        Initialize a chat session with a bot.
        
        Args:
            space_id: Space to use (default: "dr_panda")
            bot_id: Bot ID within the space (uses default bot if not specified)
            llm_identifier: LLM model identifier in format "provider/model" (e.g., "openai/gpt-4o", "gemini/gemini-2.5-flash")
            llm_type: [DEPRECATED] Use llm_identifier instead. Legacy format: "openai" or "gemini"
            user_name: User's display name
            language: Force language (e.g., "es", "de")
            generate_first_message: Generate AI greeting
            incognito_mode: Privacy mode (no data saved)
            customer_llm_key: Your LLM API key for BYOK (overrides instance key)
            space_config: Complete space configuration (for external/custom spaces)
            
        Returns:
            InitializeResponse with first message
            
        Example:
            >>> # Initialize with specific bot
            >>> response = client.initialize(
            ...     space_id="customer-support",
            ...     bot_id="sarah",
            ...     llm_type="openai",
            ...     customer_llm_key="your-openai-key"
            ... )
            >>> print(response.message)
            
            >>> # Initialize with default bot (bot_id omitted)
            >>> response = client.initialize(
            ...     space_id="customer-support",
            ...     llm_type="openai"
            ... )
        """
        try:
            payload = {
                "user_id": self.user_id,
                "space_id": space_id,
                "user_name": user_name,
                "language": language,
                "generate_first_message": generate_first_message,
                "incognito_mode": incognito_mode
            }
            
            # Add LLM identifier (new format) or llm_type (legacy)
            if llm_identifier:
                payload["llm_identifier"] = llm_identifier
            elif llm_type:
                payload["llm_type"] = llm_type
            
            # Add bot_id if provided
            if bot_id:
                payload["bot_id"] = bot_id
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided (for external spaces)
            if space_config:
                payload["space_config"] = space_config
            
            response = self._session.post(
                f"{self.api_url}/initialize_chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.current_space = space_id
            return InitializeResponse(**data)
        except requests.RequestException as e:
            raise APIError(f"Failed to initialize chat: {e}")
    
    def chat(
        self,
        message: str,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None,
        llm_identifier: Optional[str] = None,
        llm_type: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ChatResponse:
        """
        Send a message and get a response.
        
        Args:
            message: User message
            space_id: Which space to chat with (uses current if not specified)
            bot_id: Which bot to chat with (uses default if not specified)
            temperature: Override temperature (0.0-2.0)
            max_tokens: Override max tokens
            customer_llm_key: Your LLM API key for BYOK (overrides instance key)
            space_config: Complete space configuration (for external spaces)
            llm_identifier: LLM model identifier in format "provider/model"
            llm_type: [DEPRECATED] Use llm_identifier instead
            
        Returns:
            ChatResponse with AI message and tool_calls (if any)
            
        Example:
            >>> response = client.chat("I'm feeling anxious today", bot_id="sarah")
            >>> print(response.message)
            >>> if response.tool_calls:
            ...     print(f"Functions triggered: {[tc['name'] for tc in response.tool_calls]}")
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        try:
            payload = {
                "user_id": self.user_id,
                "space_id": space_id or self.current_space,
                "messages": [{"role": "user", "content": message}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            # Add LLM identifier (new format) or llm_type (legacy)
            if llm_identifier:
                payload["llm_identifier"] = llm_identifier
            elif llm_type:
                payload["llm_type"] = llm_type
            
            # Add bot_id if provided
            if bot_id:
                payload["bot_id"] = bot_id
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided
            if space_config:
                payload["space_config"] = space_config
            
            # Add tools if provided
            if tools:
                payload["tools"] = tools
            
            response = self._session.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return ChatResponse(**data)
        except requests.RequestException as e:
            raise APIError(f"Failed to send message: {e}")
    
    def stream_chat(
        self,
        message: str = None,
        messages: Optional[List[Dict[str, str]]] = None,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        customer_llm_key: Optional[str] = None,
        space_config: Optional[Dict[str, Any]] = None,
        llm_identifier: Optional[str] = None,
        llm_type: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the response in real-time.
        
        Args:
            message: User message
            space_id: Which space to chat with
            temperature: Override temperature
            max_tokens: Override max tokens
            customer_llm_key: Your LLM API key for BYOK
            space_config: Complete space configuration (for external spaces)
            llm_identifier: LLM model identifier in format "provider/model"
            llm_type: [DEPRECATED] Use llm_identifier instead
            
        Yields:
            Text chunks as they arrive
            
        Example:
            >>> for chunk in client.stream_chat("Tell me a story"):
            ...     print(chunk, end='', flush=True)
            
            >>> # With custom space
            >>> for chunk in client.stream_chat(
            ...     "Hello!",
            ...     space_config={
            ...         "space_id": "my_bot",
            ...         "prompt": "You are helpful",
            ...         "llm_identifier": "gemini-2.5-flash",
            ...         "temperature": 0.7,
            ...         "max_tokens": 1000
            ...     },
            ...     llm_type="gemini",
            ...     customer_llm_key="your-gemini-key"
            ... ):
            ...     print(chunk, end='', flush=True)
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        try:
            # Support both message and messages parameters
            if messages is None:
                if message is None:
                    raise ValueError("Either 'message' or 'messages' must be provided")
                messages = [{"role": "user", "content": message}]
            
            payload = {
                "user_id": self.user_id,
                "space_id": space_id or self.current_space,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # Add bot_id if provided
            if bot_id:
                payload["bot_id"] = bot_id
            
            # Add LLM identifier (new format) or llm_type (legacy)
            if llm_identifier:
                payload["llm_identifier"] = llm_identifier
            elif llm_type:
                payload["llm_type"] = llm_type
            
            # Add customer LLM key if provided
            llm_key = customer_llm_key or self.customer_llm_key
            if llm_key:
                payload["customer_llm_key"] = llm_key
            
            # Add space config if provided
            if space_config:
                payload["space_config"] = space_config
            
            # Add tools if provided
            if tools:
                payload["tools"] = tools
            
            response = self._session.post(
                f"{self.api_url}/chat/stream",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        content = line_text[6:]  # Remove "data: " prefix
                        
                        # Check if it's "[DONE]" marker
                        if content == "[DONE]":
                            break
                        
                        # Try to parse as JSON first (new format)
                        try:
                            data = json.loads(content)
                            
                            # Handle errors (skip function_call conversion errors)
                            if 'error' in data and data['error']:
                                error_msg = data['error']
                                if 'function_call' not in error_msg and 'convert' not in error_msg.lower():
                                    raise APIError(f"Streaming error: {error_msg}")
                            
                            # Handle function calls (logged but not yielded)
                            if data.get('type') == 'function_call':
                                # Function calls execute silently in background
                                continue
                            
                            # Handle text content
                            if 'content' in data:
                                yield data['content']
                            
                            # Handle completion
                            if data.get('done'):
                                # Log any tool calls that were triggered
                                if data.get('tool_calls'):
                                    import logging
                                    logging.info(f"Functions triggered: {[tc['name'] for tc in data['tool_calls']]}")
                                break
                        except json.JSONDecodeError:
                            # Plain text format (legacy/simple mode)
                            if content:
                                yield {"type": "text", "content": content}
        except requests.RequestException as e:
            raise APIError(f"Failed to stream message: {e}")
    
    def chat_stream_v2(
        self,
        messages: List[Dict[str, str]],
        response_mode: ResponseMode = ResponseMode.STREAM_TEXT,
        voice_config: Optional[VoiceConfig] = None,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        llm_type: str = "openai",
        customer_llm_key: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Send chat with enhanced response modes including voice (v2 endpoint).
        
        Args:
            messages: Message history [{"role": "user", "content": "..."}]
            response_mode: Response mode (TEXT, STREAM_TEXT, STREAM_VOICE, STREAM_VOICE_ONLY)
            voice_config: Voice configuration for voice modes (required if using voice)
            space_id: Optional space ID
            bot_id: Optional bot ID
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            llm_type: LLM type ("openai" or "gemini")
            customer_llm_key: Your LLM API key for BYOK
            tools: List of tool definitions in OpenAI format (optional)
            tool_choice: Control tool usage: "auto", "none", or {"type": "function", "function": {"name": "..."}}
            
        Yields:
            Dict with:
                - type: "text" | "audio" | "tool_call" | "text_complete" | "done" | "error"
                - data: Content (string for text, dict for audio/tool_call)
                
        Examples:
            >>> # Simple text streaming
            >>> for event in client.chat_stream_v2(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ...     response_mode=ResponseMode.STREAM_TEXT
            ... ):
            ...     if event["type"] == "text":
            ...         print(event["data"], end="", flush=True)
            
            >>> # Voice streaming
            >>> from mia21 import ResponseMode, VoiceConfig
            >>> 
            >>> for event in client.chat_stream_v2(
            ...     messages=[{"role": "user", "content": "Tell me a joke"}],
            ...     response_mode=ResponseMode.STREAM_VOICE,
            ...     voice_config=VoiceConfig(
            ...         enabled=True,
            ...         elevenlabs_api_key="sk_..."
            ...     )
            ... ):
            ...     if event["type"] == "text":
            ...         print(event["data"], end="", flush=True)
            ...     elif event["type"] == "audio":
            ...         # Decode and play audio
            ...         audio_b64 = event["data"]["audio"]
            ...         audio_bytes = base64.b64decode(audio_b64)
            ...         # Save or play audio_bytes
        """
        payload = {
            "user_id": self.user_id,
            "messages": messages,
            "llm_type": llm_type,
            "response_mode": response_mode.value
        }
        
        # Optional parameters
        if space_id:
            payload["space_id"] = space_id
        if bot_id:
            payload["bot_id"] = bot_id
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if customer_llm_key or self.customer_llm_key:
            payload["customer_llm_key"] = customer_llm_key or self.customer_llm_key
        if voice_config:
            payload["voice_config"] = voice_config.to_dict()
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
        
        # For non-streaming mode (TEXT), use regular POST
        if response_mode == ResponseMode.TEXT:
            response = self._session.post(
                f"{self.api_url}/chat/stream",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}", response.text)
            
            result = response.json()
            yield {"type": "done", "data": result}
            return
        
        # For streaming modes, use SSE
        try:
            response = self._session.post(
                f"{self.api_url}/chat/stream",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise APIError(f"API request failed: {response.status_code}", response.text)
            
            # Process SSE stream
            current_event = None
            text_buffer = []  # Buffer for multi-line text chunks
            
            for line in response.iter_lines(decode_unicode=True):
                # Empty line - signals end of multi-line message
                if not line:
                    # If we have buffered text lines, join them with newlines and yield
                    if text_buffer:
                        text = '\n'.join(text_buffer)
                        yield {"type": "text", "data": text}
                        text_buffer = []
                    continue
                
                # Event type
                if line.startswith("event: "):
                    current_event = line[7:].strip()
                    
                    # Handle simple events
                    if current_event == "text_complete":
                        # Flush buffered text before text_complete
                        if text_buffer:
                            text = '\n'.join(text_buffer)
                            yield {"type": "text", "data": text}
                            text_buffer = []
                        yield {"type": "text_complete", "data": None}
                        current_event = None
                    elif current_event == "done":
                        # Flush buffered text before done
                        if text_buffer:
                            text = '\n'.join(text_buffer)
                            yield {"type": "text", "data": text}
                            text_buffer = []
                        yield {"type": "done", "data": None}
                        break
                    elif current_event == "error":
                        yield {"type": "error", "data": "Stream error"}
                        current_event = None
                    continue
                
                # Data line
                if line.startswith("data: "):
                    data_content = line[6:]
                    
                    # Handle [DONE] marker
                    if data_content == "[DONE]":
                        # Flush any buffered text
                        if text_buffer:
                            text = '\n'.join(text_buffer)
                            yield {"type": "text", "data": text}
                            text_buffer = []
                        continue
                    
                    # Try to parse as JSON (only if it looks like JSON)
                    if data_content.startswith("{") or data_content.startswith("["):
                        try:
                            data_json = json.loads(data_content)
                            
                            # Flush any buffered text before yielding structured data
                            if text_buffer:
                                text = '\n'.join(text_buffer)
                                yield {"type": "text", "data": text}
                                text_buffer = []
                            
                            # Tool call event
                            if current_event == "tool_call" or data_json.get("type") == "tool_call":
                                yield {"type": "tool_call", "data": data_json}
                                current_event = None
                            # Audio chunk
                            elif "audio" in data_json:
                                yield {"type": "audio", "data": data_json}
                            # Error
                            elif "error" in data_json:
                                yield {"type": "error", "data": data_json["error"]}
                            else:
                                # Unknown JSON structure - treat as text
                                text_buffer.append(data_content)
                        except json.JSONDecodeError:
                            # JSON parse failed - treat as text
                            text_buffer.append(data_content)
                    else:
                        # Plain text chunk - buffer it
                        text_buffer.append(data_content)
            
            # Flush any remaining buffered text
            if text_buffer:
                text = '\n'.join(text_buffer)
                yield {"type": "text", "data": text}
        
        except Exception as e:
            raise Mia21Error(f"Streaming failed: {str(e)}")
    
    def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file (mp3, wav, m4a, etc.)
            language: Optional language code (e.g., 'en', 'es'). Auto-detect if None
            prompt: Optional context to guide transcription
            response_format: Response format (json, verbose_json, text, srt, vtt)
            temperature: Sampling temperature (0.0 - 1.0)
            openai_api_key: Your OpenAI API key (BYOK)
            
        Returns:
            Dict with transcription results
            
        Example:
            >>> result = client.transcribe_audio("recording.mp3", language="en")
            >>> print(result["text"])
            "Hello, this is a test"
        """
        try:
            url = f"{self.api_url}/stt/transcribe"
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'response_format': response_format,
                    'temperature': temperature
                }
                
                if language:
                    data['language'] = language
                if prompt:
                    data['prompt'] = prompt
                if openai_api_key:
                    data['openai_api_key'] = openai_api_key
                
                response = self._session.post(url, files=files, data=data, timeout=60)
                
                if response.status_code != 200:
                    raise APIError(f"Transcription failed: {response.status_code}", response.text)
                
                return response.json()
        
        except Exception as e:
            raise Mia21Error(f"Failed to transcribe audio: {str(e)}")
    
    def translate_audio(
        self,
        audio_file_path: str,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate audio in any language to English using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file
            prompt: Optional context to guide translation
            response_format: Response format (json, verbose_json, text, srt, vtt)
            temperature: Sampling temperature (0.0 - 1.0)
            openai_api_key: Your OpenAI API key (BYOK)
            
        Returns:
            Dict with translation results (always in English)
            
        Example:
            >>> result = client.translate_audio("spanish_audio.mp3")
            >>> print(result["text"])
            "Hello, how are you?"
        """
        try:
            url = f"{self.api_url}/stt/translate"
            
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {
                    'response_format': response_format,
                    'temperature': temperature
                }
                
                if prompt:
                    data['prompt'] = prompt
                if openai_api_key:
                    data['openai_api_key'] = openai_api_key
                
                response = self._session.post(url, files=files, data=data, timeout=60)
                
                if response.status_code != 200:
                    raise APIError(f"Translation failed: {response.status_code}", response.text)
                
                return response.json()
        
        except Exception as e:
            raise Mia21Error(f"Failed to translate audio: {str(e)}")

    def close(self, space_id: Optional[str] = None):
        """
        Close chat session and save conversation.
        
        Args:
            space_id: Which space to close (current if not specified)
            
        Example:
            >>> client.close()
        """
        try:
            response = self._session.post(
                f"{self.api_url}/close_chat",
                json={
                    "user_id": self.user_id,
                    "space_id": space_id or self.current_space
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise APIError(f"Failed to close chat: {e}")
    
    def close_chat(self, space_id: Optional[str] = None):
        """
        Alias for close(). Close chat session and save conversation.
        
        Args:
            space_id: Which space to close (current if not specified)
            
        Example:
            >>> client.close_chat()
        """
        return self.close(space_id)
    
    def chat_stream(
        self,
        message: str,
        space_id: Optional[str] = None,
        bot_id: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Send a message and get streaming response.
        
        Args:
            message: User message
            space_id: Which space to chat with (uses current if not specified)
            bot_id: Which bot to chat with (uses default if not specified)
            temperature: Override temperature (0.0-2.0)
            max_tokens: Override max tokens
            tools: List of tool definitions
            
        Yields:
            Dict with streaming events (type: "text", "audio", "tool_call", etc.)
            
        Example:
            >>> for chunk in client.chat_stream("Tell me a story"):
            ...     if chunk.get("type") == "text":
            ...         print(chunk.get("content"), end="", flush=True)
        """
        if not self.current_space and not space_id:
            raise ChatNotInitializedError("Chat not initialized. Call initialize() first.")
        
        # Use existing stream_chat method
        return self.stream_chat(
            messages=[{"role": "user", "content": message}],
            space_id=space_id,
            bot_id=bot_id,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools
        )
    
    # Bot Management Methods (Phase 2: Independent Bots)
    
    def create_bot(
        self,
        bot_id: str,
        name: str,
        prompt: str,
        llm_identifier: str = "openai/gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 512,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new bot (Phase 2: Independent bots with LLM config).
        
        Args:
            bot_id: Unique bot identifier
            name: Bot display name
            prompt: Bot's personality/tone prompt
            llm_identifier: LLM model (e.g., "openai/gpt-4o", "gemini/gemini-2.5-flash")
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens (1-16384)
            language: Language code (e.g., "en", "es")
            voice_id: ElevenLabs voice ID
            is_default: Whether this is a default bot
            
        Returns:
            Created bot data
            
        Example:
            >>> bot = client.create_bot(
            ...     bot_id="friendly-bot",
            ...     name="Friendly Assistant",
            ...     prompt="I'm warm and friendly!",
            ...     llm_identifier="openai/gpt-4o-mini",
            ...     temperature=0.8,
            ...     max_tokens=512,
            ...     voice_id="P7x743VjyZEOihNNygQ9",
            ...     is_default=True
            ... )
        """
        try:
            payload = {
                "bot_id": bot_id,
                "name": name,
                "prompt": prompt,
                "llm_identifier": llm_identifier,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "language": language,
                "voice_id": voice_id,
                "is_default": is_default
            }
            
            response = self._session.post(
                f"{self.api_url}/bots",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to create bot: {e}")
    
    def list_bots(self) -> List[Dict[str, Any]]:
        """
        List all bots for the customer (Phase 2: Independent bots).
        
        Returns:
            List of bot objects
            
        Example:
            >>> bots = client.list_bots()
            >>> for bot in bots:
            ...     print(f"{bot['name']} ({bot['bot_id']})")
        """
        try:
            response = self._session.get(
                f"{self.api_url}/bots",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("bots", [])
        except requests.RequestException as e:
            raise APIError(f"Failed to list bots: {e}")
    
    def get_bot(self, bot_id: str) -> Dict[str, Any]:
        """
        Get a specific bot by ID (Phase 2: Independent bots).
        
        Args:
            bot_id: Bot ID
            
        Returns:
            Bot object
            
        Example:
            >>> bot = client.get_bot("sarah")
            >>> print(f"Voice: {bot['voice_id']}")
        """
        try:
            response = self._session.get(
                f"{self.api_url}/bots/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to get bot: {e}")
    
    def update_bot(
        self,
        bot_id: str,
        name: Optional[str] = None,
        prompt: Optional[str] = None,
        llm_identifier: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        is_default: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a bot (Phase 2: Independent bots with LLM config).
        
        Args:
            bot_id: Bot ID to update
            name: New name (optional)
            prompt: New bot prompt (optional)
            llm_identifier: New LLM identifier (optional)
            temperature: New temperature (optional)
            max_tokens: New max tokens (optional)
            language: New language (optional)
            voice_id: New voice ID (optional)
            is_default: Set as default bot (optional)
            
        Returns:
            Updated bot object
            
        Example:
            >>> updated = client.update_bot(
            ...     bot_id="sarah",
            ...     temperature=0.9,
            ...     voice_id="nova"
            ... )
        """
        try:
            payload = {}
            if name is not None:
                payload["name"] = name
            if prompt is not None:
                payload["prompt"] = prompt
            if llm_identifier is not None:
                payload["llm_identifier"] = llm_identifier
            if temperature is not None:
                payload["temperature"] = temperature
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            if language is not None:
                payload["language"] = language
            if voice_id is not None:
                payload["voice_id"] = voice_id
            if is_default is not None:
                payload["is_default"] = is_default
            
            response = self._session.put(
                f"{self.api_url}/bots/{bot_id}",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to update bot: {e}")
    
    def delete_bot(self, bot_id: str) -> bool:
        """
        Delete a bot.
        
        Args:
            bot_id: Bot ID to delete
            
        Returns:
            True if successful
            
        Example:
            >>> success = client.delete_bot("old-bot")
            >>> print(f"Deleted: {success}")
        """
        try:
            response = self._session.delete(
                f"{self.api_url}/bots/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            raise APIError(f"Failed to delete bot: {e}")
    
    def add_bot_to_space(self, space_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Add a bot to a space (Phase 2: Bot-space relationships).
        
        Args:
            space_id: Space ID
            bot_id: Bot ID to add
            
        Returns:
            Success response with updated bots list
            
        Example:
            >>> result = client.add_bot_to_space("default_space", "friendly-bot")
            >>> print(f"Bots in space: {result['bots']}")
        """
        try:
            response = self._session.post(
                f"{self.api_url}/spaces/{space_id}/add-bot/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to add bot to space: {e}")
    
    def remove_bot_from_space(self, space_id: str, bot_id: str) -> Dict[str, Any]:
        """
        Remove a bot from a space (Phase 2: Bot-space relationships).
        
        Args:
            space_id: Space ID
            bot_id: Bot ID to remove
            
        Returns:
            Success response with updated bots list
            
        Example:
            >>> result = client.remove_bot_from_space("default_space", "old-bot")
            >>> print(f"Remaining bots: {result['bots']}")
        """
        try:
            response = self._session.delete(
                f"{self.api_url}/spaces/{space_id}/remove-bot/{bot_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIError(f"Failed to remove bot from space: {e}")
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close on context exit."""
        if self.current_space:
            try:
                self.close()
            except:
                pass

