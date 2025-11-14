import uvicorn
from .settings import settings


def main():
    uvicorn.run('src.testing_system.app:app',
                host=settings.server_host,
                port=settings.server_port,
                ssl_keyfile='www.testingsystem.ru.key',
                ssl_certfile='www.testingsystem.ru.crt',
                reload=True)


if __name__ == "__main__":
    main()
