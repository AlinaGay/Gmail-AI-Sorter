# Gmail AI Sorter

An intelligent email categorization tool that uses Google's Gemini AI to automatically analyze and suggest folder categories for your Gmail inbox.

## Features

- **Automated Email Analysis**: Fetches recent emails from your Gmail account
- **AI-Powered Categorization**: Uses Gemini AI to analyze email content and suggest logical folder categories
- **Smart Caching**: Caches email data to minimize API calls
- **Rate Limit Handling**: Automatic retry mechanism for API quota limits

## Architecture
```
gmail-ai-sorter/
├── main.py                     # Application entry point
├── config/
│   └── credentials.json        # Google OAuth credentials
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Base agent class
│   │   └── email_analyzer.py   # Email analysis agent
│   └── services/
│       ├── gmail_service.py    # Gmail API integration
│       └── email_data_service.py # Email data processing
│       └── gemini_service.py    # Gemini integration
├── .env                        # Environment variables
├── token.pickle                # OAuth token (auto-generated)
└── requirements.txt            # Dependencies
```

## Prerequisites

- Python 3.12+
- Google Cloud Project with Gmail API enabled
- Gemini API key

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/gmail-ai-sorter.git
cd gmail-ai-sorter
```

### 2. Set up virtual environment

Using uv (recommended):
```bash
uv venv
uv sync
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `config/credentials.json`

### 4. Get Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key
3. Create `.env` file in project root:
```env
GEMINI_API_KEY=your_api_key_here
```

## Usage

### Run the application
```bash
uv run python main.py
```

Or with activated virtual environment:
```bash
python main.py
```

### First run

On first run, a browser window will open for Gmail authorization. After authorizing, a `token.pickle` file will be created for future sessions.

### Example output
```
Connecting to Gmail ...
Connecting with Gemini
Analyzing with Gemini
[EmailAnalyzer] Analyzing 10 emails:

id: 19b8ea8e43d94151
thread_id: 19b8ea8e43d94151
subject: Thank you for applying for the Senior Python Engineer position
from_addr: "Company" <noreply@company.com>
snippet: Hi, Thank you for applying...
labels: ['CATEGORY_UPDATES', 'INBOX']
date: Mon, 5 Jan 2026 09:56:31 -0500

[EmailAnalyzer] Found 4 categories:

Category 1:
name: Job Applications
description: Emails related to job applications and responses
email_ids: ['19b8ea8e43d94151', '19b8df646ee8b648']
count: 2

--------------------------------------------------

Category 2:
name: LinkedIn
description: Notifications and updates from LinkedIn
email_ids: ['19b8c2c14de2fe57', '19b8a16a2053ea21']
count: 2

--------------------------------------------------

Category 3:
name: Newsletters
description: Daily digests from Medium, Quora, etc.
email_ids: ['19b8db3b821ff49f', '19b8c8ff3e0d22c3']
count: 2
```

## Configuration

### Environment variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

### Adjustable parameters

In `main.py`:
```python
results = analyzer.execute(num_emails=10)  # Number of emails to analyze
```

In `email_analyzer.py`:
```python
def execute(self, num_emails: int = 100, max_retries: int = 3)
```

## API Rate Limits

### Gmail API
- 250 quota units per user per second

### Gemini API (Free tier)
- 15 requests per minute
- 1,500 requests per day
- 1,000,000 tokens per minute

The application handles rate limits automatically with retry logic.

## Troubleshooting

### "invalid_grant: Bad Request"
Delete `token.pickle` and re-run the application to re-authenticate.
```bash
rm token.pickle
uv run python main.py
```

### "429 ResourceExhausted"
API quota exceeded. Options:
1. Wait for quota reset (1 minute for RPM, midnight PST for daily)
2. Use a different model: `gemini-pro` instead of `gemini-2.0-flash`
3. Create a new API key in a different project

### "models/gemini-x is not found"
Check available models:
```python
import google.generativeai as genai
genai.configure(api_key="YOUR_KEY")
for m in genai.list_models():
    print(m.name)
```

## Dependencies

- `google-api-python-client` - Gmail API client
- `google-auth-oauthlib` - OAuth authentication
- `google-generativeai` - Gemini AI SDK
- `python-dotenv` - Environment variable management

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
