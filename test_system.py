#!/usr/bin/env python3
"""
Test script for the updated Law AI Advisor system
"""

import os
from updated_pipeline import process_query

def test_system():
    """Test the system with sample queries"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set. Please create a .env file with your API key.")
        print("Example: echo 'OPENAI_API_KEY=your_key_here' > .env")
        return
    
    print("🧪 Testing Law AI Advisor System\n")
    
    # Test queries of different complexity
    test_queries = [
        ("Simple", "What is a lease?"),
        ("Moderate", "How do I file a complaint against my landlord?"),
        ("Complex", "What are the legal implications of breaking a lease due to habitability issues in NYC?")
    ]
    
    for complexity, query in test_queries:
        print(f"🔍 Testing {complexity} Query: {query}")
        print("-" * 60)
        
        try:
            result = process_query(query, debug=True)
            
            print(f"\n✅ Result:")
            print(f"📄 Documents used: {result['documents_used']}")
            print(f"💬 Answer: {result['answer'][:200]}...")
            print("=" * 80 + "\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("=" * 80 + "\n")

if __name__ == "__main__":
    test_system()