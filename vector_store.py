from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# 1) Load data
urls = [
    "https://ag.ny.gov/publications/residential-tenants-rights-guide", 
    "https://www.curbed.com/article/new-york-city-landlord-tenant-law-rights.html",
    "https://www.legalservicesnyc.org/what-we-do/practice-areas-and-projects/housing",
    "https://hcr.ny.gov/fire-damaged-vacate-order-apartments",
    "https://www.consumerfinance.gov/ask-cfpb/what-should-i-do-if-my-house-is-destroyed-in-a-natural-disaster-en-1521/"
]

docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# 2) Split
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, 
    chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

# 3) Create the embedding function
embeddings = OpenAIEmbeddings()

faiss_index = FAISS.from_documents(doc_splits, embeddings)

# Save the FAISS index locally
faiss_index.save_local("faiss_index")

