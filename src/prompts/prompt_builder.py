class PromptBuilder:
    def __init__(self, prompt_template):
        self.prompt_template = prompt_template

    def build_prompt(self, template_args: dict) -> str:
        # Fill the template with provided arguments
        prompt = self.prompt_template.format(**template_args)
        return prompt