from huggingface_hub import InferenceClient
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
#from langchain_chroma import Chroma

api_key='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'



client = InferenceClient(api_key=api_key)
hf_embeddings = HuggingFaceEndpointEmbeddings(
repo_id="sentence-transformers/all-MiniLM-L6-v2",  
huggingfacehub_api_token=api_key)
# loader = PyPDFLoader("/Users/ijazulhaq/Desktop/The-Kite-Runner.pdf", )
# book = loader.load()
# chunk_size = 2000
# chunk_overlap = 50  
# r_splitter =  RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap, separators='\xad')
# splits = r_splitter.split_documents(book)
# for x in range(len(splits)):
#     splits[x].page_content = splits[x].page_content.replace('\t\r \xa0', ' ')

persist_dir = 'static/chroma'
# vector_db = Chroma.from_documents(
# documents = splits,
# embedding = hf_embeddings,
# persist_directory=persist_dir
#          )


vector_db = Chroma(persist_directory=persist_dir, embedding_function=hf_embeddings) 
docs_returned = vector_db.similarity_search('who is assef', k=5, filter={'page':{'$lt': 55}})
print(docs_returned)
