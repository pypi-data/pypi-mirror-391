"""ElevenLabs provider configuration."""

# HTTP Configuration
BASE_URL = "https://api.elevenlabs.io"
ENDPOINT = "/v1/text-to-speech/{voice_id}"
STREAM_ENDPOINT = "/v1/text-to-speech/{voice_id}/stream"
VOICES_ENDPOINT = "/v1/voices"

# Authentication
AUTH_HEADER_NAME = "xi-api-key"
AUTH_HEADER_PREFIX = ""  # No prefix, just the API key
