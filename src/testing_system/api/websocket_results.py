import asyncio
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from starlette import status
from starlette.websockets import WebSocketDisconnect

from testing_system.models.test_results_request import TestResultsRequest
from testing_system.services.auth import get_current_user
from testing_system.test_service.test_results_getter import TestResultsService

test_router = APIRouter()


async def send_results(websocket, service, user_id, course_id, test_id, params, update_type="request"):
    """Общая функция для отправки результатов"""
    results = service.get_results(
        user_id, course_id, test_id, params.only_max_result, params.search_prefix,
        params.upper_bound, params.lower_bound, params.score_equals,
        params.date_from, params.date_to, params.ordering
    )

    data = results.dict()
    new_data = data.copy()
    new_data["results"] = [
        {**item, "passing_time": str(item["passing_time"])} for item in data.get("results", [])
    ]
    new_data["update_type"] = update_type

    await websocket.send_json(new_data)
    print(f"Sent {update_type} update")


@test_router.websocket("/tests/ws/results/{test_id}")
async def get_results_via_websocket(websocket: WebSocket,
                                    test_id: int,
                                    course_id: int,
                                    service: TestResultsService = Depends()):
    await websocket.accept()
    user = None
    try:
        token = websocket.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

        token = token.split(" ")[1]  # Убираем "Bearer"
        user = get_current_user(token)

        # Переменная для хранения текущих параметров
        current_params = None

        async def send_periodic_updates():
            """Отправляет данные каждые 5 секунд"""
            while True:
                await asyncio.sleep(5)
                if current_params:
                    try:
                        await send_results(
                            websocket, service, user.id, course_id, test_id,
                            current_params, "periodic"
                        )
                    except Exception as e:
                        print(f"Error in periodic update: {e}")

        # Запускаем фоновую задачу для периодических обновлений
        update_task = asyncio.create_task(send_periodic_updates())

        while True:
            # Получаем параметры запроса от клиента
            params_data = await websocket.receive_json()
            params = TestResultsRequest(**params_data)
            current_params = params  # Сохраняем параметры для периодических обновлений

            await send_results(
                websocket, service, user.id, course_id, test_id,
                params, "request"
            )
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for test_id={test_id}.")
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        print(f"Error in WebSocket connection: {e}")