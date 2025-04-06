class ConversationManager:
    def __init__(self):
        # We store conversation text and user info in memory
        self.messages = []
        self.buffer_size = 5  # Store last 5 messages
        self.user_info_state = {
            "name": None,
            "age": None, 
            "gender": None,
            "family_situation": None,
            "annual_income": None,
            "liabilities": None,
            "financial_goals": None,
            "existing_savings_investments": None,
            "decided_coverage_amount": None,
            "decided_term": None,
            "framework_step": 1,
            "additional_notes": None
        }
    
    def add_user_message(self, message: str):
        self.messages.append(("Customer", message))
        if len(self.messages) > self.buffer_size:
            self.messages.pop(0)
        
    def add_assistant_message(self, message: str):
        self.messages.append(("TIA", message))
        if len(self.messages) > self.buffer_size:
            self.messages.pop(0)

    @property
    def chat_history(self) -> str:
        return "\n".join([f"{role}: {msg}" for role, msg in self.messages])

    def update_user_info_state(self, new_info: dict):
        # Merge new_info into existing user_info_state
        self.user_info_state.update(new_info)