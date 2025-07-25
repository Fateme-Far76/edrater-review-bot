# 🏫 School Review Automation Bot

This project automates the process of submitting school reviews on [edrater.com](https://edrater.com), using AI-generated comments and Selenium.

---

## 🚀 Features

- ✅ Logs in to edrater.com using Selenium
- ✅ Supports AI-generated comments using a local open-source LLM (Mistral via Ollama)
- ✅ Falls back to predefined comments if AI fails
- ✅ Submits reviews (ratings + comment) for schools
- ✅ Tracks reviewed schools to avoid duplication
- ✅ Processes 133,000+ schools efficiently
- ✅ Supports 3 mode of full batch, random sample, or custom range for schools to be reviewed
- ✅ Modular code with clear separation of logic

---

## 📂 Project Structure

.
├── main.py # CLI entry point – handles CSV loading and user interaction
├── review_bot.py # Core automation logic (login, comment generation, review submission)
├── Fallback_Comments.csv # List of fallback comments (used if AI fails)
├── reviewed_schools.json # Logs of already-reviewed school URLs
├── .gitignore # Excludes pycache, .DS_Store, etc.
├── README.md # This documentation file


---

## 🧠 Requirements

- Python 3.9+
- Google Chrome + ChromeDriver installed
- The local LLM endpoint (Mistral running via Ollama)
- Install dependencies:

```bash
pip install selenium pandas requests
```

## 🛠️ Usage
1. Run the bot

```bash
python main.py
```

2. Choose one of the modes:
all – Review all schools in the listing

random – Review a random number of schools

range – Choose specific index range (e.g., from 100 to 200)

3. The script will:
Fetch the CSV from a URL

Ask for your desired range

Open Chrome and prompt for login

Submit reviews with AI-generated comments

Log successful submissions in reviewed_schools.json

## 🤖 AI Integration
The review_bot.py script uses a local model API:

### 🔧 Installation & Usage

1. **Install Ollama**
```bash
brew install ollama
```
2. **Download and Run Mistral**
```bash
ollama run mistral
```
3. **Run Ollama in Server Mode with Optimizations**
```bash
OLLAMA_FLASH_ATTENTION="1" OLLAMA_KV_CACHE_TYPE="q8_0" ollama serve
```

4. **The bot will POST prompts to this local API:**
```bash
http://localhost:11434/api/generate
```
If the AI response fails or is not available, the script will gracefully fallback to predefined comments from Fallback_Comments.csv.

## 📌 Tips
Make sure Fallback_Comments.csv is present in the same directory

## ✨ Author
Fatemeh Rakhshanifar