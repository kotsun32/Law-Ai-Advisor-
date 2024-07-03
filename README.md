# Law-Ai-Advisor-
WIP

Linkedin article for our project: 
https://www.linkedin.com/pulse/adaptive-rag-access-justice-sateesh-nori-vqwte/?trackingId=I9lc7EFLRaKslISryNhaKQ%3D%3D

Utilizing a Adaptive Rag system to allow checks on reliability and allow for dynamic routing for different levels of complexy queries. 

First using query routing directing different queries to different starting points. In this case by level of complexity for a law related question.

If the question is easy it will directly go through the LLM currently using Open Ai chatgpt 3.5 turbo api for testing.

If it is medium complexity it will use the vectorstore of the RAG and the LLM. Currently the Rag is a very small dummy data set.

If it is highly complex it will use a self reflextion flow to check it self several times with the goal of grounding the answers and checking for hallucinations.



![image for flowchart](Screenshot%202024-06-25%20at%208.20.40%20PM.png)

