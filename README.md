# 🧠 Ashok 2.0 - Problem Solving Assistant

An intelligent chatbot that helps you solve problems using uploaded PDF books and Google's Gemini AI. Ashok responds in a unique English-Urdu mixed style and provides contextual answers with specific book references.

## ✨ Features

- 📚 **PDF Book Integration**: Upload problem-solving books and get contextual answers
- 🔍 **Smart Vector Search**: Uses FAISS for efficient content retrieval
- 📖 **Chapter/Page References**: Provides specific citations from your uploaded books
- 🧠 **Gemini AI Powered**: Leverages Google's advanced language model
- 🚫 **Smart Filtering**: Detects and handles silly/irrelevant questions with humor
- 🌍 **Bilingual Responses**: Natural English-Urdu mixed communication style
- 💬 **Chat History**: Maintains conversation context throughout the session
- 🎯 **Problem-Solving Focus**: Specialized for analytical and strategic thinking


colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860


## 🚀 Live Demo

[https://ashokai.streamlit.app/]


## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hassan0111/ashok-chatbot.git
   cd ashok-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and go to `http://localhost:8501`

## 🔧 Configuration

### 1. Get Gemini API Key
- Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Create a new API key
- Copy the key for use in the application

### 2. Prepare Your PDF Book
- Ensure your PDF is text-based (not scanned images)
- Problem-solving, management, or self-help books work best
- File size should be reasonable (< 50MB for better performance)

## 📖 Usage

### Basic Usage
1. **Enter API Key**: Paste your Gemini API key in the sidebar
2. **Upload PDF**: Choose your problem-solving book
3. **Wait for Processing**: The app will create searchable chunks
4. **Start Chatting**: Ask questions about problem-solving techniques

### Example Questions
- "How can I improve my decision-making process?"
- "What are the steps for effective conflict resolution?"
- "How do I prioritize tasks when everything seems urgent?"
- "What techniques can help me think more creatively?"

### What NOT to Ask (You'll get "Abay Sallay" responses!)
- Personal questions about Ashok
- Weather, movies, or entertainment
- Greetings without context
- Silly or irrelevant topics

## 🏗️ Technical Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   PDF Parser    │    │  Vector Store   │
│   Frontend      │◄──►│   (PyPDF2)     │◄──►│   (FAISS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Question       │    │   Gemini AI     │    │  HuggingFace    │
│  Processor      │◄──►│   (2.0 Flash)  │    │  Embeddings     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Technologies
- **Frontend**: Streamlit for interactive web interface
- **AI Model**: Google Gemini 2.0 Flash for response generation
- **Vector Database**: FAISS for similarity search
- **Embeddings**: HuggingFace sentence-transformers
- **PDF Processing**: PyPDF2 for text extraction
- **Text Processing**: LangChain for document chunking

## 📁 Project Structure

```
ashok-chatbot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── .streamlit/           # Streamlit config (optional)
    └── config.toml
```

## 🔍 How It Works

1. **PDF Processing**: 
   - Extracts text from uploaded PDF
   - Splits into manageable chunks (800 characters)
   - Creates embeddings using HuggingFace models
   - Stores in FAISS vector database

2. **Question Analysis**:
   - Filters out silly/irrelevant questions
   - Identifies problem-solving related queries
   - Searches vector database for relevant content

3. **Response Generation**:
   - Retrieves top matching book content
   - Sends context + question to Gemini AI
   - Generates response with book references
   - Formats in English-Urdu mixed style

## 🎭 Ashok's Personality

Ashok is designed with a unique personality:
- **Supportive**: Encourages good questions and problem-solving
- **Direct**: No-nonsense approach to silly questions
- **Cultural**: Uses Pakistani/Indian expressions naturally
- **Expert**: Focused on problem-solving methodologies
- **Humorous**: "Abay Sallay" responses for inappropriate questions

## 🚨 Limitations

- **PDF Quality**: Works best with text-based PDFs, not scanned images
- **Language**: Optimized for English content with Urdu expressions
- **API Dependency**: Requires active Gemini API key
- **Processing Time**: Large PDFs may take time to process initially
- **Context Length**: Very long conversations may lose early context

## 🐛 Troubleshooting

### Common Issues

**1. API Key Not Working**
- Verify key is correct and active
- Check if you have API quota remaining
- Ensure key has Gemini API access

**2. PDF Processing Fails**
- Try a different PDF file
- Ensure PDF contains text (not just images)
- Check if file size is reasonable

**3. No Book References in Responses**
- Ensure PDF was processed successfully
- Check if your question relates to book content
- Try more specific problem-solving questions

**4. App Running Slowly**
- Large PDFs take time to process initially
- Consider using smaller, focused books
- Check your internet connection

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug mode
streamlit run app.py --server.runOnSave true
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI**: For the Gemini API
- **Streamlit**: For the amazing web app framework
- **HuggingFace**: For the embedding models
- **LangChain**: For document processing utilities
- **FAISS**: For efficient vector search

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [Issues](https://github.com/YOUR_USERNAME/ashok-chatbot/issues) page
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Support for multiple PDF books simultaneously
- [ ] Advanced search filters by chapter/topic
- [ ] Export chat history functionality
- [ ] Multi-language support
- [ ] Voice input/output capabilities
- [ ] Integration with more AI models
- [ ] Custom personality settings

## 📊 Version History

- **v2.0.0** (Current): Enhanced book integration with chapter references
- **v1.0.0**: Basic chatbot with PDF support

---

Made with ❤️ by [Hassan jalil] | Powered by Gemini AI & Streamlit