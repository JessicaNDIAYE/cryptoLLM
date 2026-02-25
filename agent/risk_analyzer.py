import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)



DB_PATH = os.path.join(os.path.dirname(__file__), "faiss_crypto_news")

if os.path.exists(DB_PATH):
    vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    print("Attention: Index FAISS introuvable. L'analyse de risque ne fonctionnera pas.")
    vectorstore = None

retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) if vectorstore else None