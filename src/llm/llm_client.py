import io
from openai import AzureOpenAI

class LLMClient:
    """
    A client for interacting with a custom OpenAI-compatible API endpoint.
    Uses openai.OpenAI(...) with base_url for a specialized LLM service 
    (like RabbitHole at https://api.rabbithole.cred.club/v1).

    Now accepts 'messages' (list of {role, content}) and optional 'functions' 
    for function calling.
    """
    def __init__(self, azure_endpoint: str, azure_openai_key: str, model_name: str):
        # Create a specialized client referencing RabbitHole's endpoint
        self.client = AzureOpenAI(
            api_version='2023-09-01-preview',
            azure_endpoint=azure_endpoint,
            api_key=azure_openai_key,
            timeout=60
        )
        self.model_name = model_name

    def call_llm(self, messages, tools) -> str:
        """
        Sends the given list of messages to the custom LLM endpoint and returns
        the LLM's response text. 
        If 'functions' is provided (list of function schemas) and function_call 
        is set to "auto", the LLM can decide to call them.

        :param messages: List of dicts like [{"role": "system", "content": ...}, ...]
        :param functions: Optional list of function schemas for function calling
        :param function_call: "none"|"auto"|"function_name"

        :return: The text content of the LLM's top response.
        """
        # Build the arguments
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["parallel_tool_calls"] = False

        response = self.client.chat.completions.create(**kwargs)

        # Typically, you'd also handle the case where the LLM returns a function_call 
        # instead of direct content. For now, we assume it returns normal text.
        return response.choices[0].message, response.usage
     
    def call_stt(self, audio_data, media_id) -> str:
        """
        Sends the given audio data to the custom STT endpoint and returns
        the STT's response text.
        """
        # Pass the binary data directly to the STT client
        audio_bytes = io.BytesIO(audio_data)
        audio_bytes.name = f"{media_id}.ogg"  # Give a filename with extension for MIME type detection        
        
        transcription = self.client.audio.transcriptions.create(
            model=self.model_name, 
            file=audio_bytes,
            language="en"
        )

        return transcription.text
    
    
    
    
    
# tools = [{
#     "type": "function",
#     "function": {
#         "name": "get_weather",
#         "description": "Get current temperature for provided coordinates in celsius.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "latitude": {"type": "number"},
#                 "longitude": {"type": "number"}
#             },
#             "required": ["latitude", "longitude"],
#             "additionalProperties": False
#         },
#         "strict": True
#     }
# }]    

# llm_client = LLMClient(
#     api_key="sk-aRKhqyNY-DEYtlkoEo9SQw",
#     base_url="https://api.rabbithole.cred.club/v1"
# )
# print(llm_client.call_llm(messages=[{"role": "user", "content": "whats weather lat 10 long 10"}], tools=tools))