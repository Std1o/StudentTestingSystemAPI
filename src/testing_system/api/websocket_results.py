from fastapi import APIRouter, WebSocket, Depends, HTTPException
from starlette import status
from starlette.websockets import WebSocketDisconnect

from testing_system.models.test_results_request import TestResultsRequest
from testing_system.services.auth import get_current_user
from testing_system.test_service.test_results_getter import TestResultsService
test_router = APIRouter()


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
        while True:
            # Получаем параметры запроса от клиента
            params_data = await websocket.receive_json()
            params = TestResultsRequest(**params_data)
            # Получаем результаты
            print(type(params))
            print("before get_results")
            results = service.get_results(
                user.id, course_id, test_id, params.only_max_result, params.search_prefix,
                params.upper_bound, params.lower_bound, params.score_equals,
                params.date_from, params.date_to, params.ordering
            )
            # Отправляем данные клиенту
            data = results.dict()
            new_data = data.copy()
            new_data["results"] = [
                {**item, "passing_time": str(item["passing_time"])} for item in data.get("results", [])
            ]
            await websocket.send_json(new_data)
    except WebSocketDisconnect:
        print(f"WebSocket connection closed for test_id={test_id}.")
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        print(f"Error in WebSocket connection: {e}")