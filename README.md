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

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `keys.env` file with the following variables:
   ```
   # OpenAI Configuration
   LLM_API_KEY=your_openai_api_key
   LLM_BASE_URL=your_openai_api_base_url

   # WhatsApp Business API Configuration
   WHATSAPP_TOKEN=your_whatsapp_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   VERIFY_TOKEN=your_webhook_verify_token
   ```

4. Set up the SQLite database:
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

### Streamlit Web Interface
```bash
streamlit run streamlit_app.py
```

### WhatsApp Webhook Server
```bash
python whatsapp_webhook.py
```

Note: Make sure you have configured your WhatsApp Business API webhook URL in the Meta developer portal to point to your server's endpoint.

## Core Components

### 1. Chatbot Core (`chatbot_core.py`)
- Main logic for processing user messages
- Integration with LLM (Language Learning Model)
- Tool execution and response management

### 2. LLM Client (`llm_client.py`)
- Handles communication with OpenAI's GPT-4
- Manages API calls and responses

### 3. Conversation Manager (`conversation_manager.py`)
- Maintains chat history
- Tracks user information state
- Manages conversation context

### 4. Functions (`functions.py`)
Key functionalities include:
- Basic plan and premium lookup
- Recommended plans based on priority factors
- Insurer metrics comparison
- Plan details retrieval
- Visualization generation

### 5. Prompts (`prompts.py`)
- System and user prompt templates
- Function schemas for the LLM

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

This project is proprietary and confidential. All rights reserved. See the [LICENSE](LICENSE) file for details.

## Support

For support or queries, please open an issue in the repository.