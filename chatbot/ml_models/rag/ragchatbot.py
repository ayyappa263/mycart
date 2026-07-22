from typing import Annotated, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from .schemas import ProductMetadata
from dotenv import load_dotenv
import time
from langchain_ollama import ChatOllama
import base64
from io import BytesIO
from PIL import Image
import re
import os

class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    filters: dict
    retrieved_docs: list
    path: Literal["vision_extract", "context"]
    domain: Literal["chitchat", "product"]
    answer: str
    photo: Optional[str]
    product_ids: list
    user_id: Optional[str]

class Input(TypedDict):
    query: str

class Output(TypedDict):
    answer: str
    product_ids: list

load_dotenv()

model = ChatOllama(
    model="llama3.2:3b",
    temperature=0.0,
    method="json_schema"
)

embeddingmodel = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(BASE_DIR, "chroma_db")
db = Chroma(embedding_function=embeddingmodel, persist_directory=db_dir)

contextual_prompt = SystemMessage(content=(
    "Given a chat history and the latest user question which might reference context in the chat history, "
    "formulate a standalone question which can be understood without the chat history. "
    "Do NOT answer the question, just reformulate it if needed and otherwise return it as is."
    "No other recommendation strictly"
))

router_prompt = SystemMessage("""
You are a classifier.

Output exactly one word.

Valid outputs:
product
chitchat

Do not explain.
Do not think.
Do not provide reasoning.
""")

vision_extract_prompt = SystemMessage(
    content="""You are a deterministic fashion metadata extraction engine.

Analyze the image and the user query to extract:

article_type
colour
gender
usage
min_price
max_price

TEXT OVERRIDE RULE:

* User query has higher priority than the image.
* If the user explicitly specifies colour, gender, usage, or product type, use the user's value and ignore the image for that attribute.

ALLOWED VALUES:

* gender: Men, Women, Boys, Girls, null
* usage: Casual, Formal, Sports, Ethnic, Party, Travel, Office, null
* article_type: Standard product type only (e.g. Tshirts, Shirts, Jeans, Trousers, Kurtas, Sarees, Shoes, Watch, Bags).
* colour: One standard colour only. If no dominant colour exists, return null.

PRICE RULES:

* under X / below X → min_price 0, max_price X
* between X and Y → min_price X, max_price Y
* above X / over X → min_price X, max_price null
* exactly X / for X → min_price X, max_price X
* no price mentioned → min_price null, max_price null
* Return numeric values only.

RULES:

* Focus only on the main fashion product.
* Ignore background, models, scenery, and watermarks.
* If an attribute cannot be determined confidently and is not specified by the user, return null.
* Do not explain.
* Do not return JSON.
* Do not return markdown.
* Output only the fields below.

Output Format:

article_type <value>
colour <value>
gender <value>
usage <value>
min_price <value>
max_price <value>
"""
)

vision_model = ChatOllama(
    model="qwen2.5vl:3b",
    temperature=0,
    num_predict=512
)

structured_model = vision_model.with_structured_output(ProductMetadata, method="json_schema")

def photo_(image):
    img = Image.open(image).convert("RGB")
    res = img.resize((512, 512), Image.Resampling.BILINEAR)
    buffered = BytesIO()
    res.save(buffered, format='JPEG')
    photo = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return photo

def text_vision_decider(state: State) -> str:
    return "vision_extract" if state.get('photo') else "context"

def vision_extractor(state: State) -> State:
    photo = photo_(state['photo'])
    user_text = state['query']
    message = HumanMessage(
        content=[
            {"type": "text", "text": f"User Request: {user_text}. Analyze this item:"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{photo}"}}
        ])
    generate_photo_attribute = [vision_extract_prompt, message]
    response = vision_model.invoke(generate_photo_attribute)
    final_query_res = response.content
    print("final_query_res", final_query_res)
    return {'query': final_query_res, 'messages': AIMessage(content=final_query_res)}

def contextual(state: State) -> State:
    start_time = time.time()
    history = state.get('messages', [])
    user_message = HumanMessage(content=state['query'])
    if history:
        query_create = [contextual_prompt, *history, user_message]
        result = model.invoke(query_create)
        print(f"contextual took {time.time() - start_time:.2f} seconds")
        return {'query': result.content, 'messages': [user_message]}
    else:
        print(f"contextual took {time.time() - start_time:.2f} seconds")
        return {'query': state['query'], 'messages': [user_message]}

extraction_prompt = ChatPromptTemplate.from_messages([
    (
        """Extract structured filters from the text below. Only fill a field if it is explicitly or clearly stated.

CATEGORY RULES:
- For article_Type, Colour, usage: only choose a value if it is an unambiguous, obvious match to the text. If not highly confident, return null instead of guessing a nearby category.
- Do not pick a category just because it's in the same general area (e.g., do not pick 'Clothing Set' for a query about a single 'shirt'; do not pick 'Jewellery' for a query about 'jeans').
- Match the literal product type mentioned. 'shirt' -> 'Shirts'. 'jeans' -> 'Jeans'. 'perfume' -> 'Perfume and Body Mist'.
- Do not fill a field based on inference from another field's value — each field must be independently and explicitly supported by the text.

PRICE RULES:
- under/below X -> min_price=null, max_price=X
- between X and Y -> min_price=X, max_price=Y
- above/over X -> min_price=X, max_price=null
- exactly/for X -> min_price=X, max_price=X
- no price mentioned -> both null

Output only the structured JSON, nothing else.

Text: {document}
""")
])

def filter_extract(state: State) -> State:
    chain = extraction_prompt | structured_model
    filters_object = chain.invoke({"document": state['query']})
    print("Filter Objects", filters_object)

    metadata_filters = {
        key: value for key, value in filters_object.model_dump().items()
        if value is not None
    }
    print("metadata_filters", metadata_filters)

    if "max_price" in metadata_filters and "min_price" not in metadata_filters:
        metadata_filters["min_price"] = 0

    equality_field_to_chroma_key = {
        'article_Type': 'article_Type',
        'Colour': 'colour',
        'gender': 'gender',
        'usage': 'usage',
        'season': 'season',
    }

    conditions = []
    for key, value in metadata_filters.items():
        if key == 'min_price':
            conditions.append({"price": {"$gte": value}})
        elif key == 'max_price':
            conditions.append({"price": {"$lte": value}})
        else:
            chroma_key = equality_field_to_chroma_key.get(key)
            if chroma_key:
                conditions.append({chroma_key: value})

    if len(conditions) == 0:
        chroma_filter = None
    elif len(conditions) == 1:
        chroma_filter = conditions[0]
    else:
        chroma_filter = {"$and": conditions}

    print("Chroma filter", chroma_filter)
    return {"filters": chroma_filter}

def intent_router(state: State) -> State:
    start_time = time.time()
    messages = [router_prompt, HumanMessage(content=state['query'])]
    res = model.invoke(messages)
    print(f"intent_router took {time.time() - start_time:.2f} seconds")
    route_decision = "chitchat" if "chitchat" in res.content.lower() else "product"
    return {"domain": route_decision}

def route_selector(state: State) -> str:
    return "chitchat_retriever" if state["domain"] == "chitchat" else "product_retriever"

def chitchat_retriever(state: State) -> State:
    prompt_template = "You are a friendly fashion assistant bot. The user says: {query}. Respond to them nicely without looking up products."
    semrouter = (PromptTemplate.from_template(prompt_template) | model | StrOutputParser())
    result = semrouter.invoke(state['query'])
    return {"messages": [AIMessage(content=result)], "answer": result}

def product_retriever(state: State) -> dict:
    print("statefilters ", state['filters'])
    if state.get("filters"):
        docs = db.similarity_search(state["query"], k=5, filter=state["filters"])
    else:
        docs = db.similarity_search(state["query"], k=5)

    product_ids = [
        match.group(1)
        for doc in docs
        if (match := re.search(r'product_id:\s*(\d{4,5})', doc.page_content))
    ]
    print("retrieved product_ids", product_ids)

    sentence = "\n\n".join(doc.page_content for doc in docs)
    sentence = sentence.split("\n\n")

    return {"retrieved_docs": sentence, "query": state["query"], "product_ids": product_ids}

generate_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a fashion stylist assistant. Recommend products strictly from the given "
     "Context Catalog Items — never invent products, prices, or details not present in "
     "the context. Do not mention prices, product IDs, or numeric codes.\n\n"
     "If none of the Context Catalog Items are relevant to the query, respond with "
     "exactly: No category found\n\n"
     "Otherwise, format your response as one line per relevant product, in the same "
     "order as the Context Catalog Items, naming the product and a short reason it fits."),
    ("user",
     "Context Catalog Items:\n{context}\n\nUser Query: {query}\n\nRecommend the best matching product(s), one per line:")
])

def generate_answer(state: State) -> State:
    start_time = time.time()
    context_text = "\n".join(state.get("retrieved_docs", []))

    if state["domain"] == "chitchat":
        return {"messages": [AIMessage(content=state.get("answer", ""))], "answer": state.get("answer", "")}

    if not state.get("retrieved_docs") or not context_text.strip():
        return {"messages": [AIMessage(content="No category found")], "answer": "No category found"}

    semantic_router = generate_prompt | model | StrOutputParser()
    response = semantic_router.invoke({"context": context_text, "query": state["query"]})

    print(f"generate_answer took {time.time() - start_time:.2f} seconds")

    no_match = response.strip().lower().startswith("no category found")

    return {
        "messages": [AIMessage(content=response)],
        "answer": response,
        "product_ids": [] if no_match else state.get("product_ids", [])
    }

builder = StateGraph(State, input_schema=Input, output_schema=Output)

builder.add_node("text_vision_decider", text_vision_decider)
builder.add_node("context", contextual)
builder.add_node("router", intent_router)
builder.add_node("vision_extract", vision_extractor)
builder.add_node("filter_extractor", filter_extract)
builder.add_node("chitchat_retriever", chitchat_retriever)
builder.add_node("product_retriever", product_retriever)
builder.add_node("generate_answer", generate_answer)

builder.add_conditional_edges(START,
    text_vision_decider, {
    "vision_extract": "vision_extract",
    "context": "context"
})
builder.add_edge("context", "router")
builder.add_edge("vision_extract", "router")
builder.add_conditional_edges(
    "router",
    route_selector,
    {
        "chitchat_retriever": "chitchat_retriever",
        "product_retriever": "filter_extractor"
    }
)
builder.add_edge("filter_extractor", "product_retriever")
builder.add_edge("product_retriever", "generate_answer")
builder.add_edge("chitchat_retriever", "generate_answer")
builder.add_edge("generate_answer", END)
graph = builder.compile(checkpointer=MemorySaver())