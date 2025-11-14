import asyncio

from fastapi import APIRouter
from gigachat import GigaChat

router = APIRouter(prefix='/ai')

@router.get('/get_ai_question', response_model=str)
async def get_ai_question(request: str):
    giga = GigaChat(
        credentials="api_key",
        verify_ssl_certs=False
    )

    response = await asyncio.to_thread(giga.chat, f"Сгенерируй вопрос для короткого ответа:{request}")
    return response.choices[0].message.content