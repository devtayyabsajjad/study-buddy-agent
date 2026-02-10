# 📚 Study Buddy Bot

An intelligent AI-powered study assistant that helps you learn from your documents. Upload PDFs or text files and ask questions - get accurate answers based only on your uploaded content.

## ✨ Features

- 🤖 **AI-Powered Q&A**: Uses Groq's Llama model for intelligent responses
- 📄 **Multi-Format Support**: Upload PDF and TXT files
- 💾 **Memory Efficient**: Optimized PDF processing with streaming to handle large files
- 🎨 **Modern UI**: Beautiful dark theme with glassmorphism effects
- 📊 **Source Citations**: See which document chunks were used for each answer
- ⚡ **Fast Processing**: Efficient chunking and retrieval system
- 🔒 **Privacy First**: All processing happens locally,documents stay on  machine

## 🚀 Quick Start
- 🔒 **Privacy First**: All processing happens locally,documents stay on  machine


### Prerequisites

- Python 3.8 or higher
- Groq API key (get one free at [groq.com](https://groq.com))

### Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run frontend/app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 📖 Usage

1. **Upload Documents**: Click "Browse files" or drag & drop PDF/TXT files
2. **Wait for Processing**: Progress bars show upload and processing status
3. **Ask Questions**: Type your question in the chat input
4. **View Answers**: Get AI-generated answers with source citations
5. **Check Sources**: Expand the sources section to see which document chunks were used

## ⚙️ Configuration

Edit `.env` to customize settings:

```bash
# Groq API Configuration
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Document Processing
CHUNK_SIZE=1200              # Size of text chunks
CHUNK_OVERLAP=200            # Overlap between chunks
MAX_CONTEXT_CHARS=14000      # Max context sent to AI

# File Upload Limits
MAX_FILE_SIZE_MB=50          # Maximum file size in MB
MAX_PDF_PAGES=500            # Maximum pages per PDF

# Retrieval Settings
TOP_K=5                      # Number of chunks to retrieve per query
```

## 🏗️ Project Structure

```
study-buddy-bot/
├── backend/
│   ├── config.py              # Configuration settings
│   ├── loaders/               # Document loaders (PDF, TXT)
│   ├── services/              # AI chat and retrieval services
│   ├── storage/               # In-memory document storage
│   └── utils/                 # Utilities (chunking, validation)
├── frontend/
│   ├── app.py                 # Main Streamlit application
│   └── ui/                    # UI components and styling
├── .env                       # Environment variables (create this)
├── .env.example               # Example environment file
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Troubleshooting

### Memory Issues with Large PDFs

The app now includes memory-efficient PDF processing, but for very large files:
- Reduce `MAX_PDF_PAGES` in `.env`
- Reduce `MAX_FILE_SIZE_MB` in `.env`
- Upload files one at a time

### API Errors

- Verify your `GROQ_API_KEY` is correct in `.env`
- Check your Groq API quota at [console.groq.com](https://console.groq.com)

### Import Errors

Make sure you're running from the project root:
```bash
streamlit run frontend/app.py
```

## 🎨 UI Features

- **Dark Theme**: Easy on the eyes for long study sessions
- **Glassmorphism**: Modern frosted glass effects
- **Smooth Animations**: Polished transitions and interactions
- **Progress Indicators**: Real-time feedback during file uploads
- **Responsive Layout**: Works on different screen sizes

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 🙏 Acknowledgments

- Powered by [Groq](https://groq.com) for fast AI inference
- Built with [Streamlit](https://streamlit.io) for the UI
- Uses [pypdf](https://github.com/py-pdf/pypdf) for PDF processing
