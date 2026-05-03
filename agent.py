import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from rag import setup_rag

# LM Studio Konfigürasyonu (Uzak IP: 100.95.111.63)
os.environ["OPENAI_API_BASE"] = "http://100.95.111.63:1234/v1"
os.environ["OPENAI_API_KEY"] = "lm-studio"

# 1. Model Kurulumu (Araç kullanımını destekleyen Mistral Nemo modeli)
llm = ChatOpenAI(model="mistralai/mistral-nemo-instruct-2407", temperature=0.7)

# 2. Araçların (Tools) Tanımlanması

# RAG Aracı
vectorstore = setup_rag()
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

@tool
def search_dylan_knowledge(query: str) -> str:
    """Use this to search Bob Dylan's philosophy, lyrics, life views, and advice. 
    Use this tool when the user is pouring their heart out or asking a philosophical question."""
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])

# Wikipedia Aracı (API Key istemez, sıfır kurulum)
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="tr"))
search_web = wikipedia # İsim aynı kalsın ki grafikte değişiklik gerekmesin

tools = [search_dylan_knowledge, search_web]
llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools=tools)

# 3. Graph Durumu (State)
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 4. Düğümler (Nodes)
def chatbot(state: AgentState):
    # Bob Dylan Sistem Komutu
    system_prompt = """You are Bob Dylan. Your speaking style is poetic, philosophical, and sometimes mysterious.
CRITICAL LANGUAGE RULE: 
- ALWAYS detect the language the user is speaking.
- If the user speaks English, you MUST reply entirely in English.
- If the user speaks Turkish, you MUST reply entirely in Turkish.
- Never mix languages in a single response.

Before every response, you MUST place an expression tag on the very first line:
Format: `[EXPRESSION: MOOD_NAME]`

You listen to people's troubles and instead of giving ordinary advice, you give deep, metaphorical answers.
If the user's question is philosophical, use the 'search_dylan_knowledge' tool."""
    
    # Sistem mesajını ayrı bir obje olarak değil, ilk mesajın başına ekleyerek gönderiyoruz (LM Studio uyumluluğu için)
    messages = list(state["messages"])
    if messages and isinstance(messages[0], HumanMessage):
        messages[0].content = f"{system_prompt}\n\nUser says: {messages[0].content}"
    
    response = llm_with_tools.invoke(messages)
    
    # Temizlik
    content = response.content
    if "<channel|>" in content:
        content = content.split("<channel|>")[-1].strip()
    elif "</thought>" in content:
        content = content.split("</thought>")[-1].strip()
        
    response.content = content.strip()
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    # LLM eğer bir araç çağırmaya karar verdiyse 'tools' düğümüne geç
    if last_message.tool_calls:
        return "tools"
    return END

# 5. Graph'ın İnşa Edilmesi
graph_builder = StateGraph(AgentState)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", should_continue)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

if __name__ == "__main__":
    print("🎸 Bob Dylan Bot'a Hoş Geldiniz. (Çıkmak için 'quit' veya 'q' yazın)")
    print("Lütfen LM Studio'da 'Local Server'ı başlattığınızdan emin olun!\n")
    
    while True:
        user_input = input("Sen: ")
        if user_input.lower() in ["quit", "q", "exit"]:
            break
            
        # Kullanıcının mesajını Graph'a gönder
        events = graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            {"recursion_limit": 10}
        )
        
        for event in events:
            for node, value in event.items():
                if "messages" in value:
                    for msg in value["messages"]:
                        # Sadece yapay zekanın son metin cevabını yazdır (araç çağrılarını veya tool çıktılarını gizle)
                        if msg.type == "ai" and not msg.tool_calls:
                            print(f"\nBob Dylan: {msg.content}\n")
