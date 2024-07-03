# Law-Ai-Advisor-
WIP

Linkedin article for our project: 
https://www.linkedin.com/pulse/adaptive-rag-access-justice-sateesh-nori-vqwte/?trackingId=I9lc7EFLRaKslISryNhaKQ%3D%3D

This project leverages an Adaptive Retrieval-Augmented Generation (RAG) system to handle law-related queries with varying levels of complexity. The system dynamically routes queries to appropriate processing mechanisms, ensuring reliable and accurate responses.
Query Routing by Complexity

    Easy Queries:
        Easy questions are processed directly through the Language Model (LLM), currently utilizing the OpenAI ChatGPT 3.5 Turbo API for testing.

    Medium Complexity Queries:
        Medium complexity questions use the RAG's vector store and the LLM. Note that the current RAG implementation is based on a small dummy dataset for initial testing.

    Highly Complex Queries:
        For highly complex questions, the system employs a self-reflection flow. This mechanism iterates through the query multiple times to ground the answers and check for hallucinations, enhancing the reliability of the responses.

This approach ensures that each query is handled with the appropriate level of processing, optimizing both speed and accuracy.



![image for flowchart](Screenshot%202024-06-25%20at%208.20.40%20PM.png)

