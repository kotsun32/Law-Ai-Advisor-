#!/usr/bin/env python3
"""
Law AI Advisor - Streamlit Chatbot Interface
A conversational AI chatbot for legal advice powered by adaptive RAG
"""

import streamlit as st
import time
import os
from datetime import datetime
from updated_pipeline import process_query, build_workflow
import json

# Page configuration
st.set_page_config(
    page_title="Law AI Advisor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .user-avatar {
        background-color: #2196f3;
        color: white;
    }
    
    .assistant-avatar {
        background-color: #ff9800;
        color: white;
    }
    
    .complexity-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    
    .simple-badge {
        background-color: #4caf50;
        color: white;
    }
    
    .moderate-badge {
        background-color: #ff9800;
        color: white;
    }
    
    .complex-badge {
        background-color: #f44336;
        color: white;
    }
    
    .stats-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .legal-disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    
    if "complexity_stats" not in st.session_state:
        st.session_state.complexity_stats = {"Simple": 0, "Moderate": 0, "Complex": 0}
    
    if "pipeline_initialized" not in st.session_state:
        with st.spinner("🔧 Initializing AI Legal Advisor..."):
            try:
                st.session_state.pipeline = build_workflow()
                st.session_state.pipeline_initialized = True
                st.success("✅ AI Legal Advisor initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize pipeline: {e}")
                st.session_state.pipeline_initialized = False

def detect_complexity(question):
    """Simple complexity detection for UI purposes"""
    question_lower = question.lower()
    
    complex_indicators = ['explain', 'detailed', 'comprehensive', 'complex', 'in-depth', 'analysis', 'implications', 'legal consequences']
    moderate_indicators = ['how', 'why', 'steps', 'process', 'method', 'rights', 'should i', 'can i']
    simple_indicators = ['what', 'when', 'who', 'define', 'is', 'are', 'basic']
    
    complex_count = sum(1 for indicator in complex_indicators if indicator in question_lower)
    moderate_count = sum(1 for indicator in moderate_indicators if indicator in question_lower)
    simple_count = sum(1 for indicator in simple_indicators if indicator in question_lower)
    
    if complex_count > 0 or len(question.split()) > 15:
        return "Complex"
    elif moderate_count > 0 or len(question.split()) > 8:
        return "Moderate"
    else:
        return "Simple"

def display_message(role, content, metadata=None):
    """Display a chat message with proper styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <div class="message-avatar user-avatar">👤</div>
            <div style="flex: 1;">
                <strong>You:</strong><br>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        complexity = metadata.get("complexity", "Unknown") if metadata else "Unknown"
        docs_used = metadata.get("documents_used", 0) if metadata else 0
        processing_time = metadata.get("processing_time", 0) if metadata else 0
        
        complexity_class = f"{complexity.lower()}-badge" if complexity != "Unknown" else "simple-badge"
        
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <div class="message-avatar assistant-avatar">⚖️</div>
            <div style="flex: 1;">
                <strong>Legal AI Advisor:</strong>
                <span class="complexity-badge {complexity_class}">{complexity}</span>
                <br><br>
                {content}
                <br><br>
                <small style="color: #666;">
                    📄 {docs_used} documents used | ⏱️ {processing_time:.1f}s | 
                    🕒 {datetime.now().strftime('%H:%M')}
                </small>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Law AI Advisor</h1>
        <p>Your AI-powered legal assistant with adaptive complexity routing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Chat Statistics")
        
        if st.session_state.total_questions > 0:
            st.markdown(f"""
            <div class="stats-container">
                <h4>Session Stats</h4>
                <p><strong>Total Questions:</strong> {st.session_state.total_questions}</p>
                <p><strong>Simple:</strong> {st.session_state.complexity_stats['Simple']}</p>
                <p><strong>Moderate:</strong> {st.session_state.complexity_stats['Moderate']}</p>
                <p><strong>Complex:</strong> {st.session_state.complexity_stats['Complex']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.header("💡 Example Questions")
        
        examples = {
            "🟢 Simple": [
                "What is a lease?",
                "Define eviction",
                "What is a security deposit?"
            ],
            "🟡 Moderate": [
                "How do I file a complaint against my landlord?",
                "What are my rights as a tenant in NYC?",
                "How much notice does a landlord need to give?"
            ],
            "🔴 Complex": [
                "What are the legal implications of breaking a lease due to habitability issues?",
                "Can my landlord evict me for having a pet if it's not in my lease?",
                "What recourse do I have if my apartment was damaged in a fire?"
            ]
        }
        
        for category, questions in examples.items():
            with st.expander(category):
                for q in questions:
                    if st.button(q, key=f"example_{hash(q)}", help="Click to ask this question"):
                        st.session_state.example_question = q
                        st.rerun()
        
        if st.button("🗑️ Clear Chat History", help="Clear all chat messages"):
            st.session_state.messages = []
            st.session_state.conversation_started = False
            st.session_state.total_questions = 0
            st.session_state.complexity_stats = {"Simple": 0, "Moderate": 0, "Complex": 0}
            st.rerun()
        
        # Legal disclaimer
        st.markdown("""
        <div class="legal-disclaimer">
            <strong>⚠️ Legal Disclaimer:</strong><br>
            This AI provides general legal information and should not be considered as legal advice. 
            Always consult with qualified legal professionals for specific legal matters.
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat interface
    if not st.session_state.pipeline_initialized:
        st.error("❌ Pipeline not initialized. Please check your API keys and try again.")
        return
    
    # Welcome message
    if not st.session_state.conversation_started:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin-bottom: 2rem;">
            <h3>👋 Welcome to Law AI Advisor!</h3>
            <p>I'm here to help you with legal questions using advanced AI technology.</p>
            <p>I can handle questions of varying complexity:</p>
            <ul style="text-align: left; display: inline-block;">
                <li><strong>Simple:</strong> Basic definitions and general information</li>
                <li><strong>Moderate:</strong> Standard legal procedures and rights</li>
                <li><strong>Complex:</strong> Nuanced legal situations with detailed analysis</li>
            </ul>
            <p><em>Ask me anything about tenant rights, legal procedures, or general legal information!</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"], 
            message["content"], 
            message.get("metadata")
        )
    
    # Handle example question selection
    if hasattr(st.session_state, 'example_question'):
        question = st.session_state.example_question
        delattr(st.session_state, 'example_question')
        
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": question
        })
        
        # Process and add assistant response
        process_question(question)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask me a legal question..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Process question
        process_question(prompt)
        st.rerun()

def process_question(question):
    """Process user question and generate response"""
    if not st.session_state.pipeline_initialized:
        st.error("Pipeline not available")
        return
    
    # Update stats
    st.session_state.conversation_started = True
    st.session_state.total_questions += 1
    
    # Detect complexity for UI
    predicted_complexity = detect_complexity(question)
    st.session_state.complexity_stats[predicted_complexity] += 1
    
    try:
        # Show typing indicator
        with st.spinner("🤔 Analyzing your question..."):
            start_time = time.time()
            
            # Process the question
            result = process_query(question, debug=False)
            
            processing_time = time.time() - start_time
            
            # Add assistant response
            metadata = {
                "complexity": predicted_complexity,
                "documents_used": result.get("documents_used", 0),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "metadata": metadata
            })
            
    except Exception as e:
        st.error(f"❌ Error processing question: {e}")
        
        # Add error response
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I apologize, but I encountered an error processing your question. Please try rephrasing your question or check if the system is properly configured.",
            "metadata": {
                "complexity": "Error",
                "documents_used": 0,
                "processing_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        })

if __name__ == "__main__":
    main()