import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
import tempfile
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Ashok 2.0 - Problem Solving Assistant",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    .sub-header {
        text-align: center;
        color: #A23B72;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #2E86AB;
    }
    .user-message {
        background-color: #E8F4FD;
        border-left-color: #2E86AB;
    }
    .assistant-message {
        background-color: #F0F8FF;
        border-left-color: #A23B72;
    }
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
    .book-reference {
        background-color: #f0f8ff;
        padding: 10px;
        border-left: 4px solid #2E86AB;
        margin: 10px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

class AshokChatbot:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.book_content = ""
        self.book_chunks = []  # Store chunks with metadata
        
    def configure_gemini(self, api_key):
        """Configure Gemini API with the provided key"""
        try:
            genai.configure(api_key=api_key)
            # Test the API key
            model = genai.GenerativeModel('gemini-2.0-flash')
            test_response = model.generate_content("Test")
            return True, "API key configured successfully!"
        except Exception as e:
            return False, f"Error configuring API: {str(e)}"
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file with better structure preservation"""
        try:
            # Create a temporary file to save the uploaded PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_file.read())
                tmp_file_path = tmp_file.name
            
            # Extract text from PDF with page information
            reader = PdfReader(tmp_file_path)
            text = ""
            page_texts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    page_texts.append({
                        'page': page_num,
                        'text': page_text,
                        'word_count': len(page_text.split())
                    })
                    text += f"\n--- Page {page_num} ---\n{page_text}\n"
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return text, page_texts
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return None, []
    
    def process_book_content(self, text, page_texts):
        """Process the book content and create vector embeddings with better chunking"""
        try:
            # Initialize embeddings (using free HuggingFace embeddings)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Create text splitter with better parameters for problem-solving content
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,  # Smaller chunks for better precision
                chunk_overlap=150,  # More overlap for context
                length_function=len,
                separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]  # Better separators
            )
            
            # Create documents with better metadata
            documents = []
            for page_info in page_texts:
                page_text = page_info['text']
                
                # Try to identify chapter/section titles
                lines = page_text.split('\n')
                chapter_title = self._extract_chapter_title(lines)
                
                # Create document with rich metadata
                doc = Document(
                    page_content=page_text,
                    metadata={
                        "source": "problem_solving_book",
                        "page": page_info['page'],
                        "chapter": chapter_title,
                        "word_count": page_info['word_count']
                    }
                )
                documents.append(doc)
            
            # Split documents into chunks
            chunks = text_splitter.split_documents(documents)
            
            # Enhance chunks with additional metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata['chunk_id'] = i
                chunk.metadata['chunk_length'] = len(chunk.page_content)
            
            # Store chunks for reference
            self.book_chunks = chunks
            
            # Create vector store
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
            self.book_content = text
            
            return True, f"Successfully processed {len(chunks)} chunks from {len(page_texts)} pages!"
        except Exception as e:
            return False, f"Error processing book content: {str(e)}"
    
    def _extract_chapter_title(self, lines):
        """Extract chapter or section title from page content"""
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line:
                # Look for chapter patterns
                if re.match(r'(chapter|section|part|unit)\s+\d+', line.lower()):
                    return line
                # Look for title-like patterns (short lines in uppercase or title case)
                if len(line) < 60 and (line.isupper() or line.istitle()):
                    return line
        return "Unknown Section"
    
    def is_silly_or_irrelevant_question(self, question):
        """Enhanced detection of silly, irrelevant, or abusive questions"""
        # Convert to lowercase for checking
        question_lower = question.lower().strip()
        
        # Very short questions or empty
        if len(question_lower) < 3:
            return True
        
        # Greeting patterns (more comprehensive)
        greeting_patterns = [
            r'\b(hello|hi|hey|salam|assalam|namaste|adab|sat sri akal)\b',
            r'\b(good morning|good evening|good afternoon|good night)\b',
            r'\b(how are you|kaise ho|kya hal|sup|wassup|how r u)\b',
            r'\b(what.*your name|tumhara naam|aap ka naam|name kya hai)\b',
            r'\b(who are you|tum kaun|aap kaun|kaun ho)\b',
            r'\b(nice to meet|pleasure to meet|glad to meet)\b'
        ]
        
        # Expanded silly/irrelevant keywords
        silly_keywords = [
            # Fun/entertainment
            'stupid', 'dumb', 'idiot', 'fool', 'nonsense', 'bullshit', 'crap',
            'joke', 'funny', 'lol', 'haha', 'hehe', 'lmao', 'rofl', 'lmfao',
            # Personal preferences
            'what color', 'favorite food', 'favorite movie', 'favorite song',
            'favorite book', 'favorite actor', 'favorite place', 'best food',
            # Entertainment
            'weather', 'movie', 'song', 'game', 'sport', 'celebrity', 'actor',
            'actress', 'singer', 'cricket', 'football', 'drama', 'tv show',
            # Relationships/personal
            'gossip', 'love', 'relationship', 'dating', 'marriage', 'girlfriend',
            'boyfriend', 'crush', 'romance', 'flirt', 'beautiful', 'handsome',
            'cute', 'sexy', 'hot', 'attract',
            # Personal info
            'age', 'old', 'young', 'birthday', 'party', 'dance', 'music',
            'height', 'weight', 'appearance', 'look like',
            # Social media
            'facebook', 'instagram', 'twitter', 'tiktok', 'youtube', 'snapchat',
            'whatsapp', 'telegram', 'social media',
            # Politics/controversial
            'politics', 'election', 'government', 'minister', 'president',
            'prime minister', 'political party', 'vote', 'democracy',
            # Random topics
            'conspiracy', 'alien', 'ufo', 'ghost', 'magic', 'supernatural',
            'religion', 'god', 'allah', 'prayer', 'temple', 'mosque', 'church'
        ]
        
        # Abusive/inappropriate keywords (expanded)
        abusive_keywords = [
            # English abusive
            'fuck', 'shit', 'damn', 'hell', 'bitch', 'bastard', 'asshole',
            'stupid', 'idiot', 'moron', 'retard', 'crazy', 'mad', 'loser',
            'suck', 'sucks', 'cunt', 'dick', 'penis', 'vagina', 'sex',
            # Urdu/Hindi abusive
            'chutiya', 'madarchod', 'behenchod', 'gandu', 'randi', 'saala',
            'kamina', 'harami', 'kutta', 'kutti', 'gadha', 'ullu', 'pagal',
            'bhenchod', 'madarchodd', 'randii', 'gaandu', 'lodu', 'lawde',
            'bhosdike', 'gaand', 'lauda', 'lund', 'choot', 'bhosda'
        ]
        
        # Problem-solving related keywords (expanded and categorized)
        problem_solving_keywords = [
            # Core problem solving
            'problem', 'solve', 'solution', 'issue', 'challenge', 'difficulty',
            'dilemma', 'obstacle', 'hurdle', 'barrier', 'bottleneck',
            # Methods and approaches
            'strategy', 'approach', 'method', 'technique', 'framework',
            'methodology', 'process', 'procedure', 'system', 'model',
            # Analysis and thinking
            'analysis', 'analyze', 'evaluate', 'assess', 'examine',
            'investigate', 'research', 'study', 'review', 'consider',
            # Decision making
            'decision', 'choose', 'select', 'option', 'alternative',
            'choice', 'decide', 'determine', 'conclude', 'judgment',
            # Planning and execution
            'plan', 'planning', 'goal', 'objective', 'target', 'aim',
            'step', 'steps', 'phase', 'stage', 'milestone', 'timeline',
            # Skills and improvement
            'skill', 'ability', 'competence', 'improve', 'enhance',
            'develop', 'learn', 'master', 'practice', 'train',
            # Effectiveness and optimization
            'effective', 'efficient', 'optimize', 'maximize', 'minimize',
            'improve', 'enhance', 'better', 'best', 'optimal',
            # Resolution and handling
            'resolve', 'overcome', 'handle', 'manage', 'deal with',
            'tackle', 'address', 'fix', 'repair', 'correct',
            # Creative and critical thinking
            'creative', 'innovation', 'brainstorm', 'idea', 'concept',
            'thinking', 'critical thinking', 'logical', 'rational',
            # Specific domains
            'conflict', 'negotiation', 'communication', 'leadership',
            'team', 'collaboration', 'productivity', 'workflow',
            'project', 'task', 'deadline', 'priority', 'organize'
        ]
        
        # Test patterns and keywords
        
        # 1. Check for greeting patterns
        for pattern in greeting_patterns:
            if re.search(pattern, question_lower):
                return True
        
        # 2. Check for abusive keywords (immediate flag)
        if any(keyword in question_lower for keyword in abusive_keywords):
            return True
        
        # 3. Check for problem-solving keywords (strong indicator of relevance)
        problem_solving_score = sum(1 for keyword in problem_solving_keywords 
                                  if keyword in question_lower)
        if problem_solving_score >= 2:  # Multiple problem-solving keywords
            return False
        
        # 4. Check for silly keywords
        silly_score = sum(1 for keyword in silly_keywords 
                         if keyword in question_lower)
        if silly_score >= 1:  # Even one silly keyword is suspicious
            return True
        
        # 5. Check for proper question structure
        question_words = [
            'what', 'how', 'why', 'when', 'where', 'which', 'who',
            'can', 'should', 'would', 'could', 'will', 'do', 'does',
            'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'explain', 'describe', 'tell', 'show', 'help', 'suggest'
        ]
        
        has_question_word = any(word in question_lower.split() for word in question_words)
        
        # 6. Advanced heuristics
        word_count = len(question_lower.split())
        
        # Very short questions without context
        if word_count < 4 and not has_question_word:
            return True
        
        # Questions with reasonable length and structure
        if word_count >= 5 and has_question_word:
            # Check if it's a genuine question
            if problem_solving_score >= 1 or '?' in question:
                return False
        
        # Random statements or very short queries
        if word_count < 6 and '?' not in question and not has_question_word:
            return True
        
        # If unclear, err on the side of being helpful
        return False
    
    def search_book_content(self, query, k=5):
        """Enhanced search for relevant content in the book"""
        if not self.vectorstore:
            return []
        
        try:
            # Perform similarity search with more results
            docs = self.vectorstore.similarity_search(query, k=k)
            
            # Format results with metadata
            results = []
            for doc in docs:
                result = {
                    'content': doc.page_content,
                    'page': doc.metadata.get('page', 'Unknown'),
                    'chapter': doc.metadata.get('chapter', 'Unknown Section'),
                    'score': 0  # Placeholder for similarity score
                }
                results.append(result)
            
            return results
        except Exception as e:
            st.error(f"Error searching book content: {str(e)}")
            return []
    
    def generate_response(self, question, api_key):
        """Generate response using Gemini API with enhanced book integration"""
        try:
            # Check if question is silly or irrelevant
            if self.is_silly_or_irrelevant_question(question):
                # More varied "Abay Sallay" responses
                silly_responses = [
                    "Abay Sallay! Don't waste my time with such bakwas. Ask me something related to problem solving yaar!",
                    "Abay Sallay! Ye kya timepass hai? I'm here to help with problem solving, not for chit-chat. Be serious!",
                    "Abay Sallay! Stop this nonsense and ask me something meaningful about problem solving techniques, samjha?",
                    "Abay Sallay! Mera time waste mat karo with such silly questions. Focus on real problems that need solving!",
                    "Abay Sallay! This is not the place for mazak. Ask me about problem-solving strategies and approaches!",
                    "Abay Sallay! Kya ye sawal hai? I'm a problem-solving expert, not your entertainment buddy. Ask something useful!",
                    "Abay Sallay! Tumhara dimagh kahan hai? Ask questions about problem solving, conflict resolution, ya decision making!",
                    "Abay Sallay! Ye koi game nahi hai. I'm here to share problem-solving wisdom, not for bakwas. Be focused!",
                    "Abay Sallay! Bilkul time waste kar rahe ho. Ask me about analytical thinking, planning, ya strategic approaches!",
                    "Abay Sallay! Pagal ho gaye ho kya? This is a problem-solving platform. Ask something related to challenges and solutions!"
                ]
                
                import random
                return random.choice(silly_responses)
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Search for relevant content in the book
            relevant_results = self.search_book_content(question, k=3)
            
            # Format book context with references
            book_context = ""
            book_references = []
            
            if relevant_results:
                book_context = "=== RELEVANT CONTENT FROM THE BOOK ===\n\n"
                for i, result in enumerate(relevant_results, 1):
                    chapter_info = f"Chapter/Section: {result['chapter']}"
                    page_info = f"Page: {result['page']}"
                    
                    book_context += f"**Reference {i}** ({chapter_info}, {page_info}):\n"
                    book_context += f"{result['content']}\n\n"
                    
                    book_references.append({
                        'chapter': result['chapter'],
                        'page': result['page'],
                        'content_preview': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                    })
            
            # Create enhanced prompt
            prompt = f"""
            You are Ashok, a problem-solving expert with a distinctive Pakistani/Indian style. Your characteristics:
            
            1. **Language Style**: Mix English with Urdu words naturally - use words like "yaar", "acha", "bilkul", "samjha", "bas", "abhi", "phir", "waise", "matlab", "dekho", "suno"
            
            2. **Personality**: 
               - Enthusiastic and encouraging about good questions
               - Practical and no-nonsense approach
               - Supportive but direct
               - Uses local expressions and cultural references
            
            3. **Response Pattern**:
               - Start with appreciation: "Excellent question yaar!" or "Bahut acha sawal!" or "Bilkul sahi poocha!"
               - Provide detailed, actionable advice
               - Use examples and analogies
               - ALWAYS reference the book content when available
               - End with encouragement or next steps
            
            4. **Book Integration Rules**:
               - ALWAYS use the book content provided below when it's relevant
               - Reference specific chapters/sections and pages
               - Quote or paraphrase from the book
               - Acknowledge the book as the source: "According to the book..." or "As mentioned in Chapter X..."
               - Don't just use book content - explain and expand on it
            
            5. **Urdu-English Integration**: 
               - Use them naturally in context
               - Examples: "Dekho yaar, the book says...", "Bilkul theek approach hai ye", "Samjha na?"
            
            {book_context}
            
            User Question: {question}
            
            Instructions:
            - If book content is provided above, YOU MUST reference it in your response
            - Mention specific chapters, pages, or sections when citing the book
            - Expand on the book's content with your own insights
            - Provide practical, actionable advice
            - Use your characteristic English-Urdu mixed style
            - Be comprehensive but conversational
            """
            
            response = model.generate_content(prompt)
            
            # Add book references to the response if available
            final_response = response.text
            
            if book_references:
                final_response += "\n\n" + "="*50 + "\n"
                final_response += "📚 **References from the Book:**\n"
                for ref in book_references:
                    final_response += f"• {ref['chapter']} (Page {ref['page']})\n"
            
            return final_response
            
        except Exception as e:
            return f"Sorry yaar, I encountered an error: {str(e)}. Please try again!"

def main():
    # Initialize the chatbot and session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = AshokChatbot()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize PDF processing state
    if 'book_processed' not in st.session_state:
        st.session_state.book_processed = False
    
    # Initialize processed file key
    if 'processed_file_key' not in st.session_state:
        st.session_state.processed_file_key = None
    
    # Main title
    st.markdown('<h1 class="main-header">🧠 Ashok 2.0</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Problem Solving Assistant</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Enter your Gemini API Key:",
            type="password",
            help="Get your free API key from https://makersuite.google.com/app/apikey"
        )
        
        # PDF upload
        st.header("📚 Upload Problem Solving Book")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload your boss's problem-solving book"
        )
        
        if uploaded_file is not None:
            # Create a unique key for the uploaded file
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            
            # Check if this file has already been processed
            if 'processed_file_key' not in st.session_state or st.session_state.processed_file_key != file_key:
                with st.spinner("Processing PDF... (This will only happen once)"):
                    result = st.session_state.chatbot.extract_text_from_pdf(uploaded_file)
                    if result[0]:  # Check if extraction was successful
                        text, page_texts = result
                        success, message = st.session_state.chatbot.process_book_content(text, page_texts)
                        if success:
                            st.success(message)
                            # Store the file key to prevent reprocessing
                            st.session_state.processed_file_key = file_key
                            st.session_state.book_processed = True
                            
                            # Show book statistics
                            st.info(f"📊 Book Stats: {len(page_texts)} pages processed")
                        else:
                            st.error(message)
            else:
                # File already processed, show confirmation
                st.success("✅ PDF already processed and ready to use!")
                st.session_state.book_processed = True
                
                # Show book info
                if hasattr(st.session_state.chatbot, 'book_chunks') and st.session_state.chatbot.book_chunks:
                    st.info(f"📖 {len(st.session_state.chatbot.book_chunks)} content chunks available")
        
        # Instructions
        st.header("📝 Instructions")
        st.markdown("""
        1. Enter your Gemini API key
        2. Upload the problem-solving PDF book
        3. Ask questions about problem solving
        4. Get responses with book references!
        
        **Enhanced Features:**
        - ✅ Better book content integration
        - ✅ Chapter/page references
        - ✅ Smarter silly question detection
        - ✅ Improved response quality
        
        **Note:** Silly questions will get "Abay Sallay" responses! 😄
        """)
        
        # Show processing status
        if st.session_state.book_processed:
            st.success("📖 Book is loaded and ready!")
        else:
            st.info("📖 Please upload a PDF book to get started.")
    
    # Main chat interface
    if api_key:
        # Configure API
        success, message = st.session_state.chatbot.configure_gemini(api_key)
        if not success:
            st.error(message)
            return
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask Ashok about problem solving..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chatbot.generate_response(prompt, api_key)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Reset PDF button (in case user wants to upload a new PDF)
        if st.button("🔄 Reset PDF"):
            st.session_state.book_processed = False
            st.session_state.processed_file_key = None
            st.session_state.chatbot = AshokChatbot()  # Reset chatbot
            st.rerun()
    
    else:
        st.info("👆 Please enter your Gemini API key in the sidebar to start chatting!")
        st.markdown("""
        ### How to get a free Gemini API key:
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy the key and paste it in the sidebar
        """)

if __name__ == "__main__":
    main()