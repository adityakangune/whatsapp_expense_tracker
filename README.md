# 💰 WhatsApp Expense Tracker

> **Track your expenses effortlessly by simply texting or sending receipt photos to WhatsApp!** 📱✨

Never lose track of your spending again. This intelligent expense tracker automatically processes your WhatsApp messages and receipt photos, extracts expense details using AI, and maintains a live Google Sheets budget for you.

[![Watch the demo on YouTube](https://img.youtube.com/vi/q6Ly95irPn0/0.jpg)](https://youtu.be/q6Ly95irPn0)

## 🌟 Features

### 📝 **Smart Expense Logging**
- **Text Messages**: Simply text `paid 24.90 groceries` or `coffee $5.50`
- **Receipt Photos**: Snap and send photos of receipts - OCR automatically extracts details
- **Instant Processing**: Get immediate confirmation with parsed expense details

### 📊 **Automated Tracking**
- **Live Google Sheets**: All expenses automatically logged to your personal spreadsheet
- **AI-Powered Parsing**: Intelligent extraction of name, amount, category, and date
- **Smart Categorization**: Automatic expense categorization with learning capabilities

### 📈 **Insightful Summaries**
- **Daily Recaps**: End-of-day spending summaries 🌙
- **Weekly Reports**: Comprehensive weekly breakdowns 📅
- **Monthly Analysis**: Deep insights with spending patterns and suggestions 📋
- **Category Breakdown**: See exactly where your money goes

## 🚀 How It Works

1. **💬 Send a Message**
   - Text: `paid 24.90 groceries` or `uber ride $15.30`
   - Image: Take a photo of any receipt

2. **🤖 AI Processing**
   - OCR extracts text from receipt images
   - LLM parses and categorizes the expense
   - Data is structured and validated

3. **📝 Auto-Logging**
   - New row added to your Google Sheet instantly
   - WhatsApp confirmation with expense details
   - Running totals updated in real-time

4. **📊 Smart Summaries**
   - Scheduled daily, weekly, and monthly reports
   - Spending insights and budget recommendations
   - Category analysis and trends

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Flask + Gunicorn on Cloud Run | 🔧 Core application server |
| **Database** | Google Sheets API | 📊 Expense storage and tracking |
| **Messaging** | Twilio WhatsApp Sandbox | 💬 WhatsApp integration |
| **OCR** | OCR.Space API | 👁️ Receipt text extraction |
| **AI/LLM** | Groq (Llama 3.1) | 🧠 Expense parsing and summaries |
| **Scheduling** | Google Cloud Scheduler | ⏰ Automated summary delivery |

## 🔧 Environment Setup

Copy `.env.example` to `.env` or configure these Cloud Run environment variables:

### 📍 **Core Configuration**
```bash
TIMEZONE=America/Los_Angeles          # Your local timezone
SHEET_ID=your_google_sheet_id         # Target Google Sheets ID
GROQ_API_KEY=your_groq_api_key       # AI processing key
INTERNAL_CRON_TOKEN=random_hex_string # Security token for summaries
```

### 🔍 **OCR Settings**
```bash
OCR_BACKEND=ocrspace                  # OCR service (default: ocrspace)
OCRSPACE_API_KEY=your_ocr_key        # OCR.Space API key
```

### 📱 **WhatsApp Integration**
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886    # Twilio sandbox number
YOUR_WHATSAPP_NUMBER=whatsapp:+1234567890     # Your WhatsApp number
```

## 🏃‍♂️ Quick Start

### 💻 **Local Development**
```bash
# Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

### ☁️ **Cloud Deployment**
```bash
# Set your project variables
PROJECT_ID=your-gcp-project-id
SERVICE=expense-tracker
REGION=us-central1

# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE

gcloud run deploy $SERVICE \
  --image gcr.io/$PROJECT_ID/$SERVICE \
  --region $REGION \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1
```

## 🔗 Integration Setup

### 📱 **WhatsApp Webhook Configuration**
1. Go to **Twilio Console → WhatsApp Sandbox**
2. Set **"When a message comes in"** webhook URL:
   ```
   https://your-cloud-run-url.run.app/whatsapp
   ```

### 📊 **Google Sheets Permissions**
1. Create a Google Cloud service account
2. Download the service account JSON key
3. Share your Google Sheet with the service account email (Editor permissions)
4. Set the JSON key as an environment variable or upload to Cloud Run

### ⏰ **Automated Summaries (Cloud Scheduler)**
Create scheduled jobs for regular summaries:

```bash
# Daily summary (9 PM)
gcloud scheduler jobs create http daily-expense-summary \
  --schedule="0 21 * * *" \
  --uri="https://your-cloud-run-url.run.app/daily-summary-ai?token=YOUR_CRON_TOKEN" \
  --time-zone="America/Los_Angeles"

# Weekly summary (Sunday 8 PM)
gcloud scheduler jobs create http weekly-expense-summary \
  --schedule="0 20 * * 0" \
  --uri="https://your-cloud-run-url.run.app/weekly-summary-ai?token=YOUR_CRON_TOKEN"

# Monthly summary (1st of month, 8 PM)
gcloud scheduler jobs create http monthly-expense-summary \
  --schedule="0 20 1 * *" \
  --uri="https://your-cloud-run-url.run.app/monthly-summary-ai?token=YOUR_CRON_TOKEN"
```

## 💡 Usage Examples

### 📝 **Text Message Formats**
```
✅ "paid 24.90 groceries"
✅ "coffee $5.50 starbucks"
✅ "uber ride 15.30"
✅ "lunch with sarah $32.45 restaurant"
✅ "gas station $45 fuel"
```

### 📸 **Receipt Photos**
- Restaurant receipts
- Gas station receipts
- Grocery store receipts
- Coffee shop receipts
- Any printed receipt with clear text

## ⚠️ Important Notes

### 🔒 **Security Considerations**
- 🔑 Keep all API keys and tokens secure
- 🚫 Never commit secrets to version control
- 🛡️ Use Cloud Run's built-in secret management for production

### 📱 **Twilio Sandbox Limitations**
- ⏰ **24-hour window**: You must message the bot within 24 hours for outbound messages
- 🧪 **Sandbox mode**: For production, upgrade to a full Twilio WhatsApp Business account
- 📞 **Phone verification**: Your number must be verified in the Twilio console

### 📊 **Google Sheets Setup**
- 📝 Create a new Google Sheet or use existing
- 👥 Share with your service account (Editor permissions required)
- 🏷️ Recommended columns: Date, Description, Amount, Category, Notes

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

### 📋 **Development Roadmap**
- [ ] 📈 Budget alerts and limits
- [ ] 🏷️ Custom category management
- [ ] 📱 Multi-user support
- [ ] 💳 Bank account integration
- [ ] 📊 Advanced analytics dashboard
- [ ] 🌍 Multi-currency support

## 📄 License

This project is proprietary and all rights are reserved by the author.

## 🆘 Support

Having issues? Check out our troubleshooting guide or create an issue in the repository.

---

**💡 Pro Tip**: Set up your phone to auto-forward receipt emails to WhatsApp for even easier expense tracking!
