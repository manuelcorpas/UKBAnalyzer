from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document

class UKBSchemaRAG:
    def __init__(self):
        self.llm = OllamaLLM(model="llama2")
        self.embeddings = OllamaEmbeddings(model="llama2")
        
    def load_schema(self):
        publication_schema = """
Description: Publications
Publications related to the study, the use of its data and results generated therefrom. Properties included are:
1. publication id (UKB internal)
2. title 
3. keywords
4. author(s)
5. journal
6. year of publication
7. publication date
8. abstract
9. PubMed ID
10. DOI
11. URL
12. Total citations
13. Recent citations (last 2 years)
14. When citation counts last updated
"""
        return [publication_schema]

    def create_retriever(self, texts):
        documents = [Document(page_content=text, metadata={"source": "schema"}) for text in texts]
        vectorstore = Chroma.from_documents(documents=documents, embedding=self.embeddings)
        return vectorstore.as_retriever()

    def setup_qa_chain(self, retriever):
        return RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=retriever)

def main():
    rag = UKBSchemaRAG()
    texts = rag.load_schema()
    retriever = rag.create_retriever(texts)
    qa_chain = rag.setup_qa_chain(retriever)
    
    while True:
        question = input("\nEnter your question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        answer = qa_chain.run(question)
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()
