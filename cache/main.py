from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import json
import os
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cache Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    status: str
    data: Optional[T] = None
    message: Optional[str] = None

class CacheItem(BaseModel):
    key: str
    value: Any
    ttl: int = 3600  # 1 hora por padrão

# Configuração do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )
    # Testar conexão
    redis_client.ping()
    logger.info(f"Conectado ao Redis em {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"Erro ao conectar com Redis: {e}")
    redis_client = None

@app.get("/saude")
def saude():
    redis_status = "conectado" if redis_client and redis_client.ping() else "desconectado"
    return ResponseModel(
        status="success",
        data={
            "status": "saudavel",
            "servico": "cache-service",
            "redis": redis_status,
            "host": REDIS_HOST,
            "port": REDIS_PORT
        }
    )

@app.post("/cache/set")
def set_cache(item: CacheItem):
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        # Serializar o valor para JSON
        value_json = json.dumps(item.value)
        redis_client.setex(item.key, item.ttl, value_json)
        
        logger.info(f"Cache definido: {item.key} (TTL: {item.ttl}s)")
        
        return ResponseModel(
            status="success",
            message=f"Cache definido com sucesso para a chave: {item.key}"
        )
    except Exception as e:
        logger.error(f"Erro ao definir cache: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/cache/get/{key}")
def get_cache(key: str):
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        value = redis_client.get(key)
        if value is None:
            return ResponseModel(
                status="error",
                message=f"Chave não encontrada: {key}"
            )
        
        # Deserializar o valor JSON
        try:
            value_data = json.loads(value)
        except json.JSONDecodeError:
            value_data = value
        
        logger.info(f"Cache recuperado: {key}")
        
        return ResponseModel(
            status="success",
            data={
                "key": key,
                "value": value_data
            }
        )
    except Exception as e:
        logger.error(f"Erro ao recuperar cache: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.delete("/cache/delete/{key}")
def delete_cache(key: str):
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        result = redis_client.delete(key)
        if result == 0:
            return ResponseModel(
                status="error",
                message=f"Chave não encontrada: {key}"
            )
        
        logger.info(f"Cache deletado: {key}")
        
        return ResponseModel(
            status="success",
            message=f"Cache deletado com sucesso: {key}"
        )
    except Exception as e:
        logger.error(f"Erro ao deletar cache: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/cache/keys")
def list_keys(pattern: str = "*"):
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        keys = redis_client.keys(pattern)
        
        return ResponseModel(
            status="success",
            data={
                "pattern": pattern,
                "keys": keys,
                "count": len(keys)
            }
        )
    except Exception as e:
        logger.error(f"Erro ao listar chaves: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.post("/cache/flush")
def flush_cache():
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        redis_client.flushdb()
        
        logger.info("Cache limpo completamente")
        
        return ResponseModel(
            status="success",
            message="Cache limpo com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        )

@app.get("/cache/stats")
def cache_stats():
    try:
        if not redis_client:
            return ResponseModel(
                status="error",
                message="Redis não está disponível"
            )
        
        info = redis_client.info()
        
        return ResponseModel(
            status="success",
            data={
                "total_keys": info.get("db0", {}).get("keys", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        )
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return ResponseModel(
            status="error",
            message=str(e)
        ) 