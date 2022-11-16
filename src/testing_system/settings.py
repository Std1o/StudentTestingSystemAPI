from pydantic import BaseSettings

class Settings(BaseSettings):
    server_host: str = '0.0.0.0'
    server_port: int = 80
    db_host = '127.0.0.1'
    db_port = 3306
    db_name = 'testing_system'
    db_user = 'root'
    db_password = 'mysql_pass'

    jwt_sercret: str = 'I8HheOD_Ue-xmEH1yo8OgxvRLUPbh7ujm2zsoHyjaM4'
    jwt_algorithm: str = 'HS256'
    jwt_expiration: int = 3600

settings = Settings()