#!/bin/python3
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from cmd import Cmd
import warnings

warnings.filterwarnings('ignore')

class SecurityAssistant(Cmd):
    intro = """Welcome to Security Assistant! \r\nInstructions: Enter your questions.  When done, enter \"exit\" or \"quit\" to end the session.
    """
    prompt ='question> '
    chain = ""

    def emptyline(self):
        pass

    def preloop(self):
        vector_db = Chroma(persist_directory="db", embedding_function=OllamaEmbeddings(model="nomic-embed-text"), collection_name="local-rag",)
        local_model = "llama3:instruct"
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        llm_study = ChatOllama(model=local_model)
        study_template = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate 2 different versions of the given user question to retrieve relevant documents from a vector database. By generating multiple perspectives on the user question, your goal is to help the user overcome some of the limitations of the distance-based similarity search. Provide these alternative questions separated by newlines.
            Original question: {question}"""
        )
        retriever = MultiQueryRetriever.from_llm(
            vector_db.as_retriever(), 
            llm_study,
            prompt=study_template
        )

        llm_responder = ChatOllama(model=local_model, callbacks=callback_manager) 
        responder_template="""You are a security analyst answering questions from auditors. Answer in 1-3 sentences with only facts and never reference the documentation. Provide informative and descriptive answers. If you can't find the answer in the doucmentation, start your response with "NEEDS REVIEW: " and then what you think is the best answer. Use the following context:
        {context}
        Question: {question}"""

        self.chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | ChatPromptTemplate.from_template(responder_template)
            | llm_responder
            | StrOutputParser()
        )

        
    def default(self, args):
        
        if args in ["exit", "quit"]:
            return True
        
        print("response> thinking...")
        self.chain.invoke(args)
        print("")



assistant = SecurityAssistant()  
assistant.cmdloop()
