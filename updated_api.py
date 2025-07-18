#!/usr/bin/env python3
"""
Updated Flask API for Law AI Advisor
"""

import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import traceback
from updated_pipeline import process_query, build_workflow

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Build the workflow once at startup
try:
    pipeline_app = build_workflow()
    print("✅ Pipeline initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
    pipeline_app = None

@app.route("/", methods=["GET"])
def home():
    """Simple web interface for testing"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Law AI Advisor</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            textarea { width: 100%; height: 100px; margin: 10px 0; padding: 10px; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #005a87; }
            .result { margin-top: 20px; padding: 20px; background: white; border-radius: 5px; border-left: 4px solid #007cba; }
            .error { border-left-color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ Law AI Advisor</h1>
            <p>Ask legal questions and get AI-powered answers with adaptive complexity routing.</p>
            
            <form id="queryForm">
                <textarea id="question" placeholder="Enter your legal question here..."></textarea><br>
                <button type="submit">Get Legal Advice</button>
            </form>
            
            <div id="result"></div>
        </div>

        <script>
            document.getElementById('queryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const question = document.getElementById('question').value;
                const resultDiv = document.getElementById('result');
                
                if (!question.trim()) {
                    resultDiv.innerHTML = '<div class="result error">Please enter a question.</div>';
                    return;
                }
                
                resultDiv.innerHTML = '<div class="result">🤔 Processing your question...</div>';
                
                try {
                    const response = await fetch('/api/ask', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `
                            <div class="result">
                                <h3>💬 Answer:</h3>
                                <p>${data.answer}</p>
                                <p><small>📄 Documents used: ${data.documents_used} | ⏱️ Processing time: ${data.processing_time}s</small></p>
                            </div>
                        `;
                    } else {
                        resultDiv.innerHTML = `<div class="result error">❌ Error: ${data.error}</div>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<div class="result error">❌ Network error: ${error.message}</div>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/api/ask", methods=["POST"])
def ask_question():
    """
    Main API endpoint for processing legal questions
    
    Accepts JSON: {"question": "your legal question"}
    Returns JSON: {"answer": "...", "documents_used": 3, "status": "success"}
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        question = data.get("question", "").strip()
        
        if not question:
            return jsonify({"error": "Missing or empty 'question' field"}), 400
        
        # Check if pipeline is available
        if pipeline_app is None:
            return jsonify({"error": "Pipeline not initialized"}), 500
        
        # Process the question
        import time
        start_time = time.time()
        
        result = process_query(question)
        
        processing_time = round(time.time() - start_time, 2)
        
        # Return response
        response = {
            "question": question,
            "answer": result["answer"],
            "documents_used": result["documents_used"],
            "status": result["status"],
            "processing_time": processing_time
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Error in ask_question: {e}")
        print(traceback.format_exc())
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "status": "error"
        }), 500

@app.route("/api/status", methods=["GET"])
def status():
    """Health check endpoint"""
    try:
        # Check if required environment variables are set
        openai_key = os.getenv("OPENAI_API_KEY")
        
        status_info = {
            "status": "healthy" if pipeline_app is not None else "unhealthy",
            "pipeline_initialized": pipeline_app is not None,
            "openai_configured": bool(openai_key),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
            "version": "2.0"
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/api/examples", methods=["GET"])
def examples():
    """Get example questions for different complexity levels"""
    example_questions = {
        "simple": [
            "What is a lease?",
            "What does eviction mean?",
            "What is a security deposit?"
        ],
        "moderate": [
            "How do I file a complaint against my landlord?",
            "What are my rights as a tenant in New York?",
            "How much notice does a landlord need to give before entering my apartment?"
        ],
        "complex": [
            "What are the legal implications of breaking a lease due to habitability issues in NYC?",
            "Can my landlord evict me for having a pet if it's not mentioned in my lease?",
            "What legal recourse do I have if my apartment was damaged in a fire and my landlord won't let me break my lease?"
        ]
    }
    
    return jsonify(example_questions), 200

if __name__ == "__main__":
    print("🚀 Starting Law AI Advisor API...")
    print("📊 Status endpoint: http://localhost:5000/api/status")
    print("🌐 Web interface: http://localhost:5000/")
    print("📋 Examples: http://localhost:5000/api/examples")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )