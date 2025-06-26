# ZotecoRD - Zotero to Discord Integration Bot

ZotecoRD is a Discord bot that bridges Zotero research management with Discord communication and Google Sheets data organization. It allows researchers to seamlessly extract highlighted annotations from Zotero PDFs and distribute them to categorized Discord channels, while also pushing comprehensive metadata to Google Sheets for collaborative research tracking.

## 🔥 Features

- **Smart Annotation Extraction**: Automatically extracts color-coded highlights from Zotero PDF annotations
- **Discord Integration**: Distributes annotations to specific Discord channels based on highlight colors
- **Google Sheets Export**: Pushes complete research metadata to Google Sheets for collaborative tracking
- **Color-Coded Organization**: Maps highlight colors to research categories (methods, contributions, results, claims, limitations)
- **Real-time Processing**: Instant processing of Zotero attachment keys via Discord commands

## 🎯 Color Mapping System

ZotecoRD uses a sophisticated color-coding system to categorize research highlights:

| Color | Category | Purpose |
|-------|----------|---------|
| 🟡 Yellow | Methods | Research methodology and approaches |
| 🟢 Green | Contributions | Key contributions and novel findings |
| 🔵 Blue | Results | Research results and outcomes |
| 🟣 Purple | Claims | Claims and assertions made by authors |
| 🔴 Red | Limitations | Study limitations and constraints |

## 📋 Prerequisites

- **Zotero Desktop**: Installed with PDF annotations
- **Discord Account**: With bot creation permissions
- **Google Cloud Account**: For Google Sheets API access (optional)
- **Python 3.8+**: For running the bot

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sakhadib/zotecord.git
cd zotecord
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `discord.py` - Discord bot framework
- `gspread` - Google Sheets API client
- `google-auth` - Google authentication
- `sqlite3` - Built-in Python library for Zotero database access

### 3. Set Up Configuration

1. Copy the example configuration:
   ```bash
   cp config.example.py config.py
   ```

2. Fill in your configuration details in `config.py`:

```python
# Discord Configuration
DISCORD_TOKEN = "your_discord_bot_token"
DISCORD_USER_ID = "your_discord_user_id" 
USER_EMAIL = "your_email@example.com"

# Channel IDs for different purposes
DETAILS_CHANNEL_ID = "channel_id_for_details"
PDF_CHANNEL_ID = "channel_id_for_pdfs"

# Color-to-Channel Mapping
COLOR_CHANNEL_MAP = {
    "yellow": "methods_channel_id",
    "green":  "contributions_channel_id", 
    "blue":   "results_channel_id",
    "purple": "claims_channel_id",
    "red":    "limitations_channel_id"
}

# Google Sheets Configuration (Optional)
SERVICE_ACCOUNT_FILE = 'path/to/service-account.json'
SPREADSHEET_ID = "your_google_sheet_id"
SHEET_NAME = "your_sheet_tab_name"
```

## 🚀 Setup Guide

### Discord Bot Setup

1. **Create Discord Application**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and name it "ZotecoRD"
   - Navigate to "Bot" section and click "Add Bot"

2. **Get Bot Token**:
   - Copy the bot token and add it to `config.py`
   - Enable "Message Content Intent" in bot settings

3. **Invite Bot to Server**:
   - Go to "OAuth2" > "URL Generator"
   - Select "bot" scope and necessary permissions
   - Use generated URL to invite bot to your server

4. **Create Discord Channels**:
   - Create channels for each color category
   - Copy channel IDs and add them to `config.py`

### Google Sheets Setup (Optional)

1. **Enable Google Sheets API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Enable Google Sheets API and Google Drive API

2. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Create new service account
   - Download JSON credentials file

3. **Share Spreadsheet**:
   - Create a Google Sheet
   - Share it with your service account email
   - Copy spreadsheet ID from URL

### Zotero Database Path

Update the Zotero database path in `zotero_reader.py`:

```python
# Windows (default)
ZOTERO_DB_PATH = r"C:\Users\{username}\Zotero\zotero.sqlite"

# macOS
# ZOTERO_DB_PATH = "/Users/{username}/Zotero/zotero.sqlite"

# Linux
# ZOTERO_DB_PATH = "/home/{username}/Zotero/zotero.sqlite"
```

## 🎮 Usage

### Starting the Bot

```bash
python bot.py
```

You should see:
```
✅ Logged in as ZotecoRD#1234 (ID: 123456789)
Bot is ready to receive \pull and \push commands.
```

### Discord Commands

#### `\pull <item_key>`
Extracts annotations from a Zotero PDF and distributes them to Discord channels.

**Example**:
```
\pull RFCM2DHI
```

**What it does**:
1. Queries Zotero database for the attachment
2. Extracts all color-coded annotations
3. Groups annotations by color
4. Sends each color group to its designated Discord channel
5. Includes paper title and URL when available

#### `\push <item_key>`
Exports complete research metadata to Google Sheets.

**Example**:
```
\push RFCM2DHI
```

**What it does**:
1. Extracts comprehensive metadata (title, authors, year, venue, DOI)
2. Organizes all annotations by color category
3. Formats data for spreadsheet entry
4. Appends new row to Google Sheets

### Finding Zotero Item Keys

1. **In Zotero Desktop**:
   - Right-click on PDF attachment
   - Select "Copy Zotero URI"
   - Extract the 8-character key from the URI

2. **From Zotero URI**:
   ```
   zotero://select/library/items/RFCM2DHI
                                 ^^^^^^^^ (this is your item key)
   ```

## 📊 Google Sheets Output Format

The bot creates rows with the following columns:

| Column | Content |
|--------|---------|
| Email | User email from config |
| Title | Paper title |
| Relevance | (Manual entry) |
| Authors | Comma-separated author list |
| Year | Publication year |
| Venue | Journal/conference name |
| DOI | Digital Object Identifier |
| Tag | (Manual entry) |
| Claims | Purple highlights (formatted as numbered list) |
| Limitations | Red highlights (formatted as numbered list) |
| Contributions | Green highlights (formatted as numbered list) |
| Methodology | Yellow highlights (formatted as numbered list) |
| Results | Blue highlights (formatted as numbered list) |
| Links | (Manual entry) |
| Notes | (Manual entry) |

## 🔧 Troubleshooting

### Common Issues

1. **"Zotero DB not found"**:
   - Verify Zotero installation path
   - Update `ZOTERO_DB_PATH` in `zotero_reader.py`
   - Ensure Zotero is closed when running the bot

2. **"No annotations found"**:
   - Verify the item key is correct
   - Ensure PDF has highlighted text (not just notes)
   - Check that highlights use the supported colors

3. **Discord channel errors**:
   - Verify all channel IDs in `config.py`
   - Ensure bot has permission to send messages
   - Check that channels exist and bot can access them

4. **Google Sheets permission errors**:
   - Verify service account has access to the spreadsheet
   - Check that the spreadsheet ID is correct
   - Ensure Google Sheets API is enabled

### Debug Mode

For troubleshooting, you can use the debug scripts:
```bash
python debug.py <item_key>  # Debug specific item
python expose.py           # Explore database structure
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Integrates with [Zotero](https://www.zotero.org/) research management
- Uses [gspread](https://github.com/burnash/gspread) for Google Sheets integration

## 📧 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information about your problem

---

**Happy researching! 🔬📚**
