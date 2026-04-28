import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def setup_rag(data_dir="./data", persist_directory="./chroma_db"):
    # Lokal Embedding modeli kullanıyoruz (HuggingFace sentence-transformers)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # DB zaten varsa olanı yükle
    if os.path.exists(persist_directory):
        print("Mevcut Vektör Veritabanı yükleniyor...")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return vectorstore

    print("Veri yükleniyor ve Vektör DB oluşturuluyor...")
    loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    docs = loader.load()
    
    # Veriyi küçük parçalara (chunk) bölüyoruz
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)
    
    # Verileri Chroma'ya kaydediyoruz
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_directory)
    print("Vektör DB başarıyla oluşturuldu!")
    return vectorstore

if __name__ == "__main__":
    setup_rag()
