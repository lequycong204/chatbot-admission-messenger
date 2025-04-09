import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import numpy as np
import google.generativeai as genai #from google import genai
from google.genai import types
from dotenv import load_dotenv
from lightrag.utils import EmbeddingFunc
from lightrag import LightRAG, QueryParam
from sentence_transformers import SentenceTransformer
from lightrag.kg.shared_storage import initialize_pipeline_status

import asyncio
import nest_asyncio

# Apply nest_asyncio to solve event loop issues
nest_asyncio.apply()

load_dotenv()
gemini_api_key = "AIzaSyDFrt-C2FM7Ob4D8ARkXl2vP3s-8maocGs"

genai.configure(api_key=gemini_api_key)

WORKING_DIR = './dickens' #"./local_database"

if os.path.exists(WORKING_DIR):
    import shutil

    shutil.rmtree(WORKING_DIR)
os.mkdir(WORKING_DIR)

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    llm = genai.GenerativeModel("gemini-2.0-flash")

    # 2. Combine prompts: system prompt, history, and user prompt
    if history_messages is None:
        history_messages = []

    system_prompt = """Bạn là trợ lí AI có kiến thức đầy đủ về vấn đề tuyển sinh trường Đại học Khoa học Tự nhiên
        Dựa vào các thông tin và tài liệu dưới đây. (nếu không có thông tin nào liên quan đến câu hỏi của tôi, hãy trả lời "Dựa vào kiến thức của tôi, ..." \n
        """
    
    combined_prompt = ""
    if system_prompt:
        combined_prompt += f"{system_prompt}\n"

    for msg in history_messages:
        # Each msg is expected to be a dict: {"role": "...", "content": "..."}
        combined_prompt += f"{msg['role']}: {msg['content']}\n"

    # Finally, add the new user prompt
    combined_prompt += f"user: Trả lời đầy đủ, chính xác cùng ngôn ngữ với câu hỏi sau: {prompt} \n Output:"

    # 3. Call the Gemini model
    response = llm.generate_content(contents=[combined_prompt])

    # 4. Return the response text
    return response.text


async def embedding_func(texts: list[str]) -> np.ndarray:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

def insert_data(rag, file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    rag.insert(text)

def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())
    
    file_path = "data/de-an-tuyen-sinh-2024.txt"
    insert_data(rag, file_path)

    # response = rag.query(
    #     query="Thí sinh đăng kí xét tuyển sắp xếp nguyện vọng theo thứ tự nào?",
    #     param=QueryParam(mode="hybrid", top_k=5, response_type="single line"),
    # )

    # print(response)


if __name__ == "__main__":
    main()
