
# ### Tracing (optional)
# secret keys 
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
LangCHAIN_Tracing_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LangCHAIN_Enpoint = os.getenv("LANGCHAIN_ENDPOINT")
LangCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

### Build Index


# Load embeddings first
embeddings = OpenAIEmbeddings()

# Load FAISS index
faiss_index = FAISS.load_local(
    "faiss_index", 
    embeddings, 
    allow_dangerous_deserialization=True
)

retriever = faiss_index.as_retriever()
#retriever = vectorstore.as_retriever()


### Router

from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["Complex", "Moderate", "Simple"] = Field(
        ...,
        #description="Given a user question choose to route it to web search or a vectorstore.",
        description="Given a user question choose to route it to Complex if the query is highly complex, Moderate if the query is moderately complex, and use Simple if it is simple or irrelavant to anything else in the vectorestore.", 
    )

# LLM with function call
#llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm_router = llm.with_structured_output(RouteQuery)

# Prompt
system = """You are an expert at routing a user question. There are three tiers Complex, Moderate, and Simple.
The Complex are prompts with alot of nuance and are diffictult to solve. Moderate are easier but with some complexity. Simple can easily be solved or is irrelvant to anything in the vectore store.
complex_indicators = ['explain', 'detailed', 'comprehensive', 'complex', 'in-depth', 'analysis'],
moderate_indicators = ['how', 'why', 'steps', 'process', 'method', 'moderate', 'overview', 'general'],
simple_indicators = ['what', 'when', 'who', 'define', 'simple', 'basic', 'example']

Example of a simple, irrelevant prompt: 
- Prompt: "What is a MacBook?"
- Answer: "A MacBook is a line of laptop computers developed and manufactured by Apple Inc."

"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

question_router = route_prompt | structured_llm_router
'''print(
    question_router.invoke(
        {"question": "Explain to me about Trump's legal issues?"}
    )
)
print(question_router.invoke({"question": "What did the supreme court recently say?"}))
print(question_router.invoke({"question": "steps in the proccess in prompting?"}))
print(question_router.invoke({"question": "Lebron James?"}))
'''

### Retrieval Grader


# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# LLM with function call
#llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeDocuments)

# Prompt
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader
question = "agent memory"
docs = retriever.get_relevant_documents(question)
doc_txt = docs[1].page_content
print(retrieval_grader.invoke({"question": question, "document": doc_txt}))


### Generate

from langchain import hub
from langchain_core.output_parsers import StrOutputParser

# Prompt
prompt = hub.pull("rlm/rag-prompt")

# LLM
#llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)


# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Chain
rag_chain = prompt | llm | StrOutputParser()

# Run
generation = rag_chain.invoke({"context": docs, "question": question})
print(generation)

# Define a simple prompt template
prompt_template = ChatPromptTemplate.from_messages(
    ["Question: {question} \nAnswer: "]
)

# Create the language model chain
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_chain = prompt_template | llm | StrOutputParser()

# Define the question
question = "Hi, how are you?"

# Run the model chain
generation = llm_chain.invoke({"question": question})
print(generation)



### Hallucination Grader


# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""

    binary_score: str = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


# LLM with function call
#llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# Prompt
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader
hallucination_grader.invoke({"documents": docs, "generation": generation})


### Answer Grader


# Data model
class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: str = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# LLM with function call
#llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

answer_grader = answer_prompt | structured_llm_grader
answer_grader.invoke({"question": question, "generation": generation})



### Question Re-writer

# LLM
#llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
#llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Prompt
system = """You a question re-writer that converts an input question to a better version that is optimized \n 
     for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
re_write_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Here is the initial question: \n\n {question} \n Formulate an improved question.",
        ),
    ]
)

question_rewriter = re_write_prompt | llm | StrOutputParser()
question_rewriter.invoke({"question": question})



### Search

from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=3)

# %%
from typing import List, Optional 

from typing import Dict, Any
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: Optional list of documents
    """

    question: str
    generation: str
    documents: Optional[List[str]]

from langchain.schema import Document


def retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}

def self_reflection_retrieve(state):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---RETRIEVE---")
    question = state["question"]

    # Retrieval
    documents = retriever.invoke(question)
    return {"documents": documents, "question": question}


def generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

def mod_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]

    # RAG generation
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}

# testing no rag gen 
def rag_less_generate(state):
    """
    Generate answer

    Args:
        state (dict): The current graph state
        llm (callable): The language model function to generate responses

    Returns:
        state (dict): New key added to state, generation, that contains LLM generation
    """
    print("---GENERATE---")
    question = state["question"]

    # LLM generation
    generation = llm_chain.invoke({"question": question})
    return {"question": question, "generation": generation}


def grade_documents(state):
    """
    Determines whether the retrieved documents are relevant to the question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with only filtered relevant documents
    """

    print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    # Score each doc
    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade == "yes":
            print("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
        else:
            print("---GRADE: DOCUMENT NOT RELEVANT---")
            continue
    return {"documents": filtered_docs, "question": question}


def transform_query(state):
    """
    Transform the query to produce a better question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates question key with a re-phrased question
    """

    print("---TRANSFORM QUERY---")
    question = state["question"]
    documents = state["documents"]

    # Re-write question
    better_question = question_rewriter.invoke({"question": question})
    return {"documents": documents, "question": better_question}


def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question}


### Edges ###


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "Moderate":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "Moderate"
    elif source.datasource == "Complex":
        print("---ROUTE QUESTION TO RAG---")
        return "Complex"
    elif source.datasource == "Simple":
        print("---ROUTE QUESTION TO LLM---")
        return "Simple"


def decide_to_generate(state):
    """
    Determines whether to generate an answer, or re-generate a question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Binary decision for next node to call
    """

    print("---ASSESS GRADED DOCUMENTS---")
    state["question"]
    filtered_documents = state["documents"]

    if not filtered_documents:
        # All documents have been filtered check_relevance
        # We will re-generate a new query
        print(
            "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
        )
        return "transform_query"
    else:
        # We have relevant documents, so generate answer
        print("---DECISION: GENERATE---")
        return "generate"


def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


from langgraph.graph import END, StateGraph

"""
workflow = StateGraph(GraphState)

# Define the nodes
#workflow.add_node("web_search", web_search)  # web search
workflow.add_node("retrieve", retrieve)  # retrieve
workflow.add_node("self_reflection_retrieve", self_reflection_retrieve)  # self reflection retrieve
workflow.add_node("grade_documents", grade_documents)  # grade documents
workflow.add_node("generate", generate)  # generate
workflow.add_node("mod_generate", mod_generate)  # moderate generate
workflow.add_node("rag-less generate", rag_less_generate) 
workflow.add_node("transform_query", transform_query)  # transform_query

# Build graph
workflow.set_conditional_entry_point(
    route_question,
    {
        #"web_search": "web_search",
        #"vectorstore": "retrieve",
        #"llm": "rag-less generate",
        "Complex": "self_reflection_retrieve",
        "Moderate": "retrieve",
        "Simple": "rag-less generate",

    },
)
#workflow.add_edge("web_search", "generate")
#workflow.add_edge("Moderate", "retrieve")
workflow.add_edge("retrieve", "mod_generate")

workflow.add_edge("self_reflection_retrieve", "grade_documents")
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "transform_query": "transform_query",
        "generate": "generate",
    },
)
workflow.add_edge("transform_query", "self_reflection_retrieve")
workflow.add_conditional_edges(
    "generate",
    grade_generation_v_documents_and_question,
    {
        "not supported": "generate",
        "useful": END,
        "not useful": "transform_query",
    },
)

# Compile
app = workflow.compile()

from pprint import pprint

# Run
inputs = {
    "question": "What is Basketball?"
}
for output in app.stream(inputs):
    for key, value in output.items():
        # Node
        pprint(f"Node '{key}':")
        # Optional: print full state at each node
        # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
    pprint("\n---\n")

# Final generation
pprint(value["generation"])

"""
#!/usr/bin/env python3

from pprint import pprint
# Import or define all the components you need:
# - StateGraph, GraphState
# - route_question, retrieve, self_reflection_retrieve, grade_documents, ...
# - generate, mod_generate, rag_less_generate, transform_query
# - decide_to_generate, grade_generation_v_documents_and_question, END

def build_workflow():
    """
    Build and compile the workflow, then return the compiled app.
    """
    # Instantiate the StateGraph with your custom GraphState
    workflow = StateGraph(GraphState)
    
    # Define nodes
    # workflow.add_node("web_search", web_search)  # optional example
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("self_reflection_retrieve", self_reflection_retrieve)
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("generate", generate)
    workflow.add_node("mod_generate", mod_generate)
    workflow.add_node("rag-less generate", rag_less_generate)
    workflow.add_node("transform_query", transform_query)

    # Build the graph with conditional entry points
    workflow.set_conditional_entry_point(
        route_question,
        {
            # "web_search": "web_search",
            # "vectorstore": "retrieve",
            # "llm": "rag-less generate",
            "Complex": "self_reflection_retrieve",
            "Moderate": "retrieve",
            "Simple": "rag-less generate",
        },
    )

    # (Optional) Add edges
    # workflow.add_edge("web_search", "generate")
    # workflow.add_edge("Moderate", "retrieve")
    workflow.add_edge("retrieve", "mod_generate")

    workflow.add_edge("self_reflection_retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        },
    )
    workflow.add_edge("transform_query", "self_reflection_retrieve")
    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": END,
            "not useful": "transform_query",
        },
    )

    # Compile the workflow to get an executable app
    app = workflow.compile()
    return app


def main(question: str):
    """
    Main entry point:
      1) Build the workflow/app
      2) Provide an input (question)
      3) Stream or run the workflow
      4) Print results

    Args:
        question (str): The question to feed into the workflow.
    """
    # Build the workflow
    app = build_workflow()

    # Define your inputs
    inputs = {
        "question": question
    }

    # Run the workflow in a streaming fashion (or use .run() if that’s your pattern)
    for output in app.stream(inputs):
        for key, value in output.items():
            pprint(f"Node '{key}':")
            # Here you can inspect or log the state at each node if needed
            # pprint(value, indent=2, width=80, depth=None)
        pprint("\n---\n")

    # 'value' now holds the final state from the last iteration
    # Print the final generation
    pprint(value["generation"])


if __name__ == "__main__":
    # Pass in the desired question as a string
    main("What is Basketball?")














