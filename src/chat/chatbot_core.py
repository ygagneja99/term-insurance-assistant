import json
import re
from src.chat.conversation_manager import ConversationManager
from src.llm.llm_client import LLMClient
from src.prompts.prompt_builder import PromptBuilder
from src.prompts.prompts import INSURANCE_AGENT_SYSTEM, INSURANCE_AGENT_USER, FUNCTION_SCHEMAS
from src.tools.functions import execute_function

def jsonify(text: str):
    cleaned_text = re.sub(r"```json|```", "", text, flags=re.IGNORECASE).strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from input: {e}")

class ChatbotCore:
    def __init__(self, azure_endpoint, azure_openai_key, azure_model_name):
        self.conversation_manager = ConversationManager()
        self.llm_client = LLMClient(
            azure_endpoint=azure_endpoint,
            azure_openai_key=azure_openai_key,
            model_name=azure_model_name
        )
        self.insurance_agent_system = PromptBuilder(prompt_template=INSURANCE_AGENT_SYSTEM)
        self.insurance_agent_user = PromptBuilder(prompt_template=INSURANCE_AGENT_USER)
    
    def process_message(self, user_input):
        """
        Process a user message and return the chatbot's response(s)
        
        Args:
            user_input (str): The user's message
            
        Returns:
            dict: {
                "responses": list of response strings, 
                "user_info_state": updated user info state,
                "debug_info": optional debug information
            }
        """
        # Update conversation history
        self.conversation_manager.add_user_message(user_input)
        
        # Build the messages for the LLM
        system_message = self.insurance_agent_system.build_prompt({})
        user_message = self.insurance_agent_user.build_prompt({
            "chat_history": self.conversation_manager.chat_history,
            "user_info_state_json": json.dumps(self.conversation_manager.user_info_state)
        })
        
        # Create the messages for the LLM
        messages_for_llm = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        # Call the LLM
        llm_response, usage = self.llm_client.call_llm(messages=messages_for_llm, tools=FUNCTION_SCHEMAS)
        self.conversation_manager.total_input_tokens += usage.prompt_tokens
        self.conversation_manager.total_output_tokens += usage.completion_tokens
        # Process the response
        assistant_text_content = ""
        debug_info = {
            "tool_calls": [],
            "tool_results": []
        }
        
        image_path = None
        
        # Handle tool calls if present
        if llm_response.tool_calls:
            messages_for_llm.append(llm_response)
            
            for tool_call in llm_response.tool_calls:
                if tool_call.type == 'function':
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Log the function call for debugging
                    debug_info["tool_calls"].append({
                        "function": function_name,
                        "arguments": function_args
                    })
                    
                    # Execute the function
                    result, image_path = execute_function(function_name, function_args)
                    debug_info["tool_results"].append(result)
                    
                    # Add the result to the messages
                    messages_for_llm.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            
            # Process results with the LLM
            follow_up_response, follow_up_usage = self.llm_client.call_llm(messages=messages_for_llm, tools=[])
            self.conversation_manager.total_input_tokens += follow_up_usage.prompt_tokens
            self.conversation_manager.total_output_tokens += follow_up_usage.completion_tokens
            assistant_text_content = follow_up_response.content if follow_up_response.content else ""
        else:
            # Regular text response
            assistant_text_content = llm_response.content if llm_response.content else ""
        
        # Process the final response
        try:
            # Check if the response is our expected JSON format
            if assistant_text_content and '{' in assistant_text_content and '"next_responses"' in assistant_text_content:
                llm_json = jsonify(assistant_text_content)
                assistant_responses = llm_json.get("next_responses", "")
                updated_state = llm_json.get("updated_user_info_state", {})
                
                # Update conversation state
                self.conversation_manager.update_user_info_state(updated_state)
                
                # Add the assistant messages to history
                for response in assistant_responses:
                    self.conversation_manager.add_assistant_message(response)
                
                return {
                    "responses": assistant_responses,
                    "user_info_state": self.conversation_manager.user_info_state,
                    "debug_info": debug_info,
                    "image_path": image_path
                }
            else:
                # If the response is not in our expected JSON format, use it directly
                self.conversation_manager.add_assistant_message(assistant_text_content)
                return {
                    "responses": [assistant_text_content],
                    "user_info_state": self.conversation_manager.user_info_state,
                    "debug_info": debug_info,
                    "image_path": image_path
                }
        except Exception as e:
            error_message = f"Error processing response: {str(e)}"
            return {
                "responses": [error_message],
                "user_info_state": self.conversation_manager.user_info_state,
                "debug_info": {
                    "error": error_message,
                    "raw_response": assistant_text_content
                },
                "image_path": image_path
            } 