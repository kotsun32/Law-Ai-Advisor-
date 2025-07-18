#!/usr/bin/env python3
"""
Updated Law AI Advisor Pipeline
Adaptive RAG system for legal queries with complexity-based routing
"""

import os
from typing import List, Optional, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain.schema import Document

# LangGraph imports
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize LLM and embeddings
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings()

# Load or create FAISS index
def load_or_create_vector_store():
    """Load existing FAISS index or create from scratch if needed"""
    try:
        faiss_index = FAISS.load_local(
            "faiss_index", 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        print("✅ Loaded existing FAISS index")
        return faiss_index
    except Exception as e:
        print(f"⚠️ Could not load FAISS index: {e}")
        print("Creating new vector store from web sources...")
        return create_vector_store()

def create_vector_store():
    """Create vector store from legal web sources"""
    urls = [
        "https://ag.ny.gov/publications/residential-tenants-rights-guide", 
        "https://www.curbed.com/article/new-york-city-landlord-tenant-law-rights.html",
        "https://www.legalservicesnyc.org/what-we-do/practice-areas-and-projects/housing",
        "https://hcr.ny.gov/fire-damaged-vacate-order-apartments",
        "https://www.consumerfinance.gov/ask-cfpb/what-should-i-do-if-my-house-is-destroyed-in-a-natural-disaster-en-1521/"
    ]
    
    # Load documents
    docs = []
    for url in urls:
        try:
            loader = WebBaseLoader(url)
            docs.extend(loader.load())
            print(f"✅ Loaded: {url}")
        except Exception as e:
            print(f"❌ Failed to load {url}: {e}")
    
    if not docs:
        raise ValueError("No documents could be loaded")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, 
        chunk_overlap=50
    )
    doc_splits = text_splitter.split_documents(docs)
    
    # Create FAISS index
    faiss_index = FAISS.from_documents(doc_splits, embeddings)
    faiss_index.save_local("faiss_index")
    print(f"✅ Created FAISS index with {len(doc_splits)} document chunks")
    
    return faiss_index

# Initialize vector store and retriever
vector_store = load_or_create_vector_store()
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# Pydantic models for structured outputs
class RouteQuery(BaseModel):
    """Route a user query to the most relevant processing tier."""
    datasource: Literal["Complex", "Moderate", "Simple"] = Field(
        description="Route query based on complexity: Complex for nuanced legal questions requiring detailed analysis, Moderate for standard legal queries, Simple for basic questions or off-topic queries."
    )

class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )

class GradeHallucinations(BaseModel):
    """Binary score for hallucination detection in generated answers."""
    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

class GradeAnswer(BaseModel):
    """Binary score to assess if answer addresses the question."""
    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )

# Create structured LLM instances
router_llm = llm.with_structured_output(RouteQuery)
doc_grader_llm = llm.with_structured_output(GradeDocuments)
hallucination_grader_llm = llm.with_structured_output(GradeHallucinations)
answer_grader_llm = llm.with_structured_output(GradeAnswer)

# Prompts
router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at routing legal questions based on complexity.

Routes:
- Complex: Multi-faceted legal issues requiring detailed analysis, interpretation of multiple laws, or nuanced situations
- Moderate: Standard legal questions with some complexity, requiring legal knowledge but straightforward
- Simple: Basic legal definitions, off-topic questions, or easily answered queries

Complexity indicators:
- Complex: 'explain in detail', 'legal implications', 'comprehensive analysis', 'court precedents'
- Moderate: 'how to', 'what are my rights', 'process for', 'steps to take'
- Simple: 'what is', 'define', 'basic information', non-legal topics

Examples:
- Complex: "What are the legal implications of breaking a lease due to habitability issues in NYC?"
- Moderate: "How do I file a complaint against my landlord for not fixing heating?"
- Simple: "What is a lease?" or "Tell me about basketball"
"""),
    ("human", "{question}")
])

doc_grader_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a grader assessing relevance of retrieved documents to a legal question.
Grade as 'yes' if the document contains information related to the question.
Grade as 'no' if the document is completely unrelated."""),
    ("human", "Question: {question}\n\nDocument: {document}")
])

hallucination_grader_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a grader assessing whether an LLM generation is grounded in the provided facts.
Give 'yes' if the answer is supported by the documents.
Give 'no' if the answer contains unsupported claims."""),
    ("human", "Facts: {documents}\n\nGeneration: {generation}")
])

answer_grader_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a grader assessing whether an answer addresses the user's question.
Give 'yes' if the answer directly addresses the question.
Give 'no' if the answer is off-topic or doesn't address the question."""),
    ("human", "Question: {question}\n\nAnswer: {generation}")
])

# Create chains
question_router = router_prompt | router_llm
retrieval_grader = doc_grader_prompt | doc_grader_llm
hallucination_grader = hallucination_grader_prompt | hallucination_grader_llm
answer_grader = answer_grader_prompt | answer_grader_llm

# RAG chain
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful legal advisor assistant. Use the provided context to answer questions about legal matters.

Guidelines:
- Base your answers on the provided legal documents
- If information is not in the context, say so clearly
- Provide practical, actionable advice when appropriate
- Include relevant legal disclaimers when giving advice
- Be clear and concise while being thorough

Context: {context}"""),
    ("human", "{question}")
])

rag_chain = rag_prompt | llm | StrOutputParser()

# Simple LLM chain (no RAG)
simple_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer questions clearly and concisely."),
    ("human", "{question}")
])

simple_chain = simple_prompt | llm | StrOutputParser()

# Question rewriter
rewriter_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a question rewriter that converts questions into better versions optimized for legal document retrieval.
Focus on legal terminology and key concepts that would appear in legal documents."""),
    ("human", "Original question: {question}\n\nRewrite this question for better legal document retrieval:")
])

question_rewriter = rewriter_prompt | llm | StrOutputParser()

# Web search (optional)
web_search_tool = None
if TAVILY_API_KEY:
    web_search_tool = TavilySearchResults(k=3)

# Graph State
class GraphState(TypedDict):
    question: str
    generation: str
    documents: Optional[List[Document]]

# Node functions
def route_question(state):
    """Route question based on complexity"""
    print("🔄 ROUTING QUESTION")
    question = state["question"]
    route = question_router.invoke({"question": question})
    print(f"📍 Route: {route.datasource}")
    return {"question": question, "route": route.datasource}

def retrieve_documents(state):
    """Retrieve relevant documents"""
    print("📚 RETRIEVING DOCUMENTS")
    question = state["question"]
    documents = retriever.invoke(question)
    print(f"📄 Retrieved {len(documents)} documents")
    return {"documents": documents, "question": question}

def grade_documents(state):
    """Filter relevant documents"""
    print("🔍 GRADING DOCUMENTS")
    question = state["question"]
    documents = state["documents"]
    
    filtered_docs = []
    for doc in documents:
        grade = retrieval_grader.invoke({
            "question": question, 
            "document": doc.page_content
        })
        if grade.binary_score == "yes":
            print("✅ Document relevant")
            filtered_docs.append(doc)
        else:
            print("❌ Document not relevant")
    
    return {"documents": filtered_docs, "question": question}

def generate_rag_response(state):
    """Generate RAG response"""
    print("🤖 GENERATING RAG RESPONSE")
    question = state["question"]
    documents = state["documents"]
    
    context = "\n\n".join([doc.page_content for doc in documents])
    generation = rag_chain.invoke({"context": context, "question": question})
    
    return {"documents": documents, "question": question, "generation": generation}

def generate_simple_response(state):
    """Generate simple LLM response"""
    print("🤖 GENERATING SIMPLE RESPONSE")
    question = state["question"]
    generation = simple_chain.invoke({"question": question})
    return {"question": question, "generation": generation}

def transform_query(state):
    """Rewrite query for better retrieval"""
    print("🔄 TRANSFORMING QUERY")
    question = state["question"]
    documents = state.get("documents", [])
    
    better_question = question_rewriter.invoke({"question": question})
    print(f"🔄 Rewritten: {better_question}")
    
    return {"documents": documents, "question": better_question}

def web_search(state):
    """Perform web search"""
    print("🌐 WEB SEARCH")
    question = state["question"]
    
    if web_search_tool:
        search_results = web_search_tool.invoke({"query": question})
        web_content = "\n".join([result["content"] for result in search_results])
        web_doc = Document(page_content=web_content)
        return {"documents": [web_doc], "question": question}
    else:
        print("⚠️ Web search not available (no Tavily API key)")
        return {"documents": [], "question": question}

# Edge functions
def decide_route(state):
    """Decide which processing route to take"""
    route = state.get("route", "Simple")
    print(f"🎯 Taking {route} route")
    return route.lower()

def decide_to_generate(state):
    """Decide whether to generate or transform query"""
    documents = state["documents"]
    
    if not documents:
        print("🔄 No relevant documents found, transforming query")
        return "transform_query"
    else:
        print("✅ Relevant documents found, generating response")
        return "generate"

def grade_generation(state):
    """Grade the generation for hallucinations and relevance"""
    print("🔍 GRADING GENERATION")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    
    # Check hallucinations
    hallucination_score = hallucination_grader.invoke({
        "documents": documents,
        "generation": generation
    })
    
    if hallucination_score.binary_score == "yes":
        print("✅ Generation grounded in documents")
        # Check if it answers the question
        answer_score = answer_grader.invoke({
            "question": question,
            "generation": generation
        })
        
        if answer_score.binary_score == "yes":
            print("✅ Generation addresses question")
            return "useful"
        else:
            print("❌ Generation doesn't address question")
            return "not_useful"
    else:
        print("❌ Generation contains hallucinations")
        return "not_supported"

# Build the workflow
def build_workflow():
    """Build and compile the adaptive RAG workflow"""
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("route_question", route_question)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("generate_rag", generate_rag_response)
    workflow.add_node("generate_simple", generate_simple_response)
    workflow.add_node("transform_query", transform_query)
    workflow.add_node("web_search", web_search)
    
    # Set entry point
    workflow.set_conditional_entry_point(
        decide_route,
        {
            "complex": "retrieve",
            "moderate": "retrieve", 
            "simple": "generate_simple"
        }
    )
    
    # Add edges
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate_rag"
        }
    )
    workflow.add_edge("transform_query", "web_search")
    workflow.add_edge("web_search", "generate_rag")
    
    # Complex route includes quality checking
    workflow.add_conditional_edges(
        "generate_rag",
        grade_generation,
        {
            "not_supported": "generate_rag",  # Retry
            "useful": END,
            "not_useful": "transform_query"
        }
    )
    
    # Simple route goes directly to end
    workflow.add_edge("generate_simple", END)
    
    return workflow.compile()

# Main execution function
def process_query(question: str, debug: bool = False):
    """
    Process a legal query through the adaptive RAG system
    
    Args:
        question: The legal question to process
        debug: Whether to show debug output
        
    Returns:
        dict: Response containing the answer and metadata
    """
    app = build_workflow()
    
    inputs = {"question": question}
    
    if debug:
        print(f"\n🚀 Processing query: {question}\n")
        for output in app.stream(inputs):
            for key, value in output.items():
                print(f"📍 Node: {key}")
                if "generation" in value:
                    print(f"💬 Generation: {value['generation'][:100]}...")
            print("---")
    
    # Get final result
    final_state = None
    for output in app.stream(inputs):
        final_state = list(output.values())[0]
    
    return {
        "question": question,
        "answer": final_state.get("generation", "No answer generated"),
        "documents_used": len(final_state.get("documents", [])),
        "status": "success"
    }

# Example usage and testing
if __name__ == "__main__":
    # Test queries
    test_queries = [
        "What is a lease?",  # Simple
        "How do I file a complaint against my landlord?",  # Moderate  
        "What are the legal implications of breaking a lease due to habitability issues in NYC?"  # Complex
    ]
    
    print("🧪 Testing Law AI Advisor Pipeline\n")
    
    for query in test_queries:
        try:
            result = process_query(query, debug=True)
            print(f"\n✅ Query: {result['question']}")
            print(f"📄 Documents used: {result['documents_used']}")
            print(f"💬 Answer: {result['answer']}\n")
            print("="*80)
        except Exception as e:
            print(f"❌ Error processing '{query}': {e}")