# Term Insurance Assistant

A sophisticated chatbot-powered assistant designed to help users navigate and understand term insurance plans. The system provides personalized recommendations, detailed plan comparisons, and interactive visualizations to make insurance decisions easier.

## Features

- **Interactive Chat Interface**: Built with Streamlit for a seamless user experience
- **WhatsApp Integration**: Available through WhatsApp for easy accessibility
- **Intelligent Plan Recommendations**: Uses multiple factors to suggest the best insurance plans
- **Visual Comparisons**: Generates clear visualizations of plan comparisons
- **Comprehensive Insurance Data**: Includes information about:
  - Multiple insurance providers
  - Plan details and premiums
  - Claim settlement ratios
  - Amount settlement ratios
  - Complaint volumes

## Tech Stack

- **Python 3.10**
- **OpenAI GPT-4o**: For natural language processing and intelligent responses
- **Streamlit**: Web interface
- **Flask**: WhatsApp webhook server
- **SQLite**: Database for insurance plans and metrics
- **Pandas & Matplotlib**: Data processing and visualization

## Project Structure

```
term-insurance-assistant/
├── src/
│   ├── chat/               # Chat-related functionality
│   │   ├── chatbot_core.py
│   │   └── conversation_manager.py
│   ├── llm/                # LLM-related functionality
│   │   └── llm_client.py
│   ├── prompts/            # Prompt-related files
│   │   ├── prompts.py
│   │   └── prompt_builder.py
│   └── tools/             # Tool functions
│       └── functions.py
├── data/                  # Data files and database
│   ├── insurance.db      # SQLite database
│   ├── schema.sql        # Database schema
│   └── generate_mock_data.py  # Script to generate test data
├── streamlit_app.py       # Web interface
├── whatsapp_webhook.py    # WhatsApp webhook server
├── keys.env              # Environment variables (not in version control)
├── setup.py             # Package setup file
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/term-insurance-assistant.git
cd term-insurance-assistant
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Create a `keys.env` file with your API keys:
```env
# OpenAI Configuration
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_base_url

# WhatsApp Business API Configuration
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_API_VERSION=v17.0
```

5. Set up the SQLite database:
```bash
# Create the database file
sqlite3 data/insurance.db

# Initialize database schema
sqlite3 data/insurance.db < data/schema.sql

# Generate and insert mock data
python data/generate_mock_data.py
```

The database will be populated with:
- Mock insurance providers and their metrics
- Various term insurance plans
- Premium rates for different age groups and terms
- Sample claim settlement ratios and complaint volumes

## Running the Application

### Web Interface
```bash
streamlit run streamlit_app.py
```

### WhatsApp Webhook
```bash
flask run
```

Note: Make sure you have configured your WhatsApp Business API webhook URL in the Meta developer portal to point to your server's endpoint.

## Core Components

### 1. Chat Module (`src/chat/`)
- Main logic for processing user messages
- Integration with LLM
- Tool execution and response management
- Conversation state management

### 2. LLM Module (`src/llm/`)
- Handles communication with OpenAI's GPT-4
- Manages API calls and responses

### 3. Prompts Module (`src/prompts/`)
- System and user prompt templates
- Function schemas for the LLM
- Prompt building utilities

### 4. Tools Module (`src/tools/`)
Key functionalities include:
- Basic plan and premium lookup
- Recommended plans based on priority factors
- Insurer metrics comparison
- Plan details retrieval
- Visualization generation

## Database Schema

The SQLite database includes tables for:
- Insurers (with performance metrics)
- Term plans (with coverage details)
- Premiums (age and term-specific rates)

## Features in Detail

1. **Basic Plan & Premium Lookup**
   - Search plans based on age, term, coverage amount, and income
   - Visual comparison of available plans

2. **Priority-based Recommendations**
   - Customized plan suggestions based on user priorities:
     - Lowest premium
     - Highest claim settlement ratio
     - Best amount settlement ratio
     - Lowest complaints volume

3. **Insurer Analysis**
   - Detailed metrics for each insurance provider
   - Performance comparisons
   - Historical data analysis

4. **Plan Visualization**
   - Clear, tabular comparisons
   - Highlighted key differences
   - Easy-to-understand metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the terms of the license included with this repository.

## Support

For support or queries, please open an issue in the repository.