from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os
from datetime import datetime, timedelta
from typing import TypeVar, Generic, Optional, Any, Dict, List
from pydantic import BaseModel
import logging
import time
import threading
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Monitoring Service")

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

class ServiceHealth(BaseModel):
    name: str
    url: str
    status: str
    response_time: float
    last_check: datetime
    uptime: Optional[float] = None

class Metric(BaseModel):
    service: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime

# Configuração dos serviços
SERVICES = {
    "api_gateway": "http://localhost:8000",
    "load_balancer": "http://localhost:8001",
    "server1": "http://localhost:8002",
    "server2": "http://localhost:8003",
    "cache": "http://localhost:8004"
}

# Armazenamento de métricas (em produção, usar banco de dados)
metrics_db = []
health_status = {}
request_counts = defaultdict(int)
error_counts = defaultdict(int)

def check_service_health(service_name: str, url: str) -> ServiceHealth:
    """Verifica a saúde de um serviço"""
    start_time = time.time()
    try:
        response = requests.get(f"{url}/saude", timeout=5)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            status = "healthy"
            data = response.json()
            uptime = data.get("data", {}).get("uptime", None)
        else:
            status = "unhealthy"
            uptime = None
            
    except Exception as e:
        response_time = time.time() - start_time
        status = "unreachable"
        uptime = None
        logger.error(f"Erro ao verificar {service_name}: {e}")
    
    return ServiceHealth(
        name=service_name,
        url=url,
        status=status,
        response_time=response_time,
        last_check=datetime.now(),
        uptime=uptime
    )

def monitor_services():
    """Função para monitorar serviços em background"""
    while True:
        for service_name, url in SERVICES.items():
            health = check_service_health(service_name, url)
            health_status[service_name] = health
            logger.info(f"Health check {service_name}: {health.status} ({health.response_time:.3f}s)")
        
        time.sleep(30)  # Verificar a cada 30 segundos

# Iniciar monitoramento em background
monitor_thread = threading.Thread(target=monitor_services, daemon=True)
monitor_thread.start()

@app.get("/saude")
def saude():
    return ResponseModel(
        status="success",
        data={
            "status": "saudavel",
            "servico": "monitoring-service",
            "servicos_monitorados": len(SERVICES)
        }
    )

@app.get("/health")
def get_health_status():
    """Retorna o status de saúde de todos os serviços"""
    return ResponseModel(
        status="success",
        data={
            "services": health_status,
            "timestamp": datetime.now(),
            "total_services": len(SERVICES)
        }
    )

@app.get("/health/{service_name}")
def get_service_health(service_name: str):
    """Retorna o status de saúde de um serviço específico"""
    if service_name not in SERVICES:
        return ResponseModel(
            status="error",
            message=f"Serviço não encontrado: {service_name}"
        )
    
    if service_name in health_status:
        return ResponseModel(
            status="success",
            data=health_status[service_name]
        )
    else:
        return ResponseModel(
            status="error",
            message=f"Status não disponível para: {service_name}"
        )

@app.post("/metrics")
def add_metric(metric: Metric):
    """Adiciona uma nova métrica"""
    metrics_db.append(metric)
    
    # Contar requisições
    request_counts[f"{metric.service}:{metric.endpoint}"] += 1
    
    # Contar erros
    if metric.status_code >= 400:
        error_counts[f"{metric.service}:{metric.endpoint}"] += 1
    
    # Manter apenas as últimas 1000 métricas
    if len(metrics_db) > 1000:
        metrics_db.pop(0)
    
    return ResponseModel(
        status="success",
        message="Métrica adicionada com sucesso"
    )

@app.get("/metrics")
def get_metrics(
    service: Optional[str] = None,
    endpoint: Optional[str] = None,
    limit: int = 100
):
    """Retorna métricas filtradas"""
    filtered_metrics = metrics_db
    
    if service:
        filtered_metrics = [m for m in filtered_metrics if m.service == service]
    
    if endpoint:
        filtered_metrics = [m for m in filtered_metrics if m.endpoint == endpoint]
    
    # Retornar as métricas mais recentes
    recent_metrics = filtered_metrics[-limit:]
    
    return ResponseModel(
        status="success",
        data={
            "metrics": recent_metrics,
            "total": len(filtered_metrics),
            "returned": len(recent_metrics)
        }
    )

@app.get("/metrics/summary")
def get_metrics_summary():
    """Retorna um resumo das métricas"""
    if not metrics_db:
        return ResponseModel(
            status="success",
            data={
                "total_requests": 0,
                "total_errors": 0,
                "avg_response_time": 0,
                "service_breakdown": {}
            }
        )
    
    total_requests = len(metrics_db)
    total_errors = len([m for m in metrics_db if m.status_code >= 400])
    avg_response_time = sum(m.response_time for m in metrics_db) / total_requests
    
    # Breakdown por serviço
    service_breakdown = {}
    for service in SERVICES.keys():
        service_metrics = [m for m in metrics_db if m.service == service]
        if service_metrics:
            service_breakdown[service] = {
                "total_requests": len(service_metrics),
                "errors": len([m for m in service_metrics if m.status_code >= 400]),
                "avg_response_time": sum(m.response_time for m in service_metrics) / len(service_metrics)
            }
    
    return ResponseModel(
        status="success",
        data={
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": (total_errors / total_requests) * 100 if total_requests > 0 else 0,
            "avg_response_time": avg_response_time,
            "service_breakdown": service_breakdown,
            "period": {
                "start": metrics_db[0].timestamp if metrics_db else None,
                "end": metrics_db[-1].timestamp if metrics_db else None
            }
        }
    )

@app.get("/alerts")
def get_alerts():
    """Retorna alertas baseados nas métricas"""
    alerts = []
    
    # Verificar serviços não saudáveis
    for service_name, health in health_status.items():
        if health.status != "healthy":
            alerts.append({
                "type": "service_unhealthy",
                "service": service_name,
                "message": f"Serviço {service_name} está {health.status}",
                "severity": "high",
                "timestamp": datetime.now()
            })
    
    # Verificar alta taxa de erro
    if metrics_db:
        recent_metrics = [m for m in metrics_db if m.timestamp > datetime.now() - timedelta(minutes=5)]
        if recent_metrics:
            error_rate = len([m for m in recent_metrics if m.status_code >= 400]) / len(recent_metrics)
            if error_rate > 0.1:  # Mais de 10% de erro
                alerts.append({
                    "type": "high_error_rate",
                    "message": f"Taxa de erro alta: {error_rate:.2%}",
                    "severity": "medium",
                    "timestamp": datetime.now()
                })
    
    # Verificar tempo de resposta alto
    if metrics_db:
        recent_metrics = [m for m in metrics_db if m.timestamp > datetime.now() - timedelta(minutes=5)]
        if recent_metrics:
            avg_response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
            if avg_response_time > 2.0:  # Mais de 2 segundos
                alerts.append({
                    "type": "high_response_time",
                    "message": f"Tempo de resposta alto: {avg_response_time:.2f}s",
                    "severity": "medium",
                    "timestamp": datetime.now()
                })
    
    return ResponseModel(
        status="success",
        data={
            "alerts": alerts,
            "total_alerts": len(alerts)
        }
    )

@app.get("/dashboard")
def get_dashboard():
    """Retorna dados para dashboard"""
    return ResponseModel(
        status="success",
        data={
            "health": health_status,
            "summary": get_metrics_summary().data,
            "alerts": get_alerts().data,
            "timestamp": datetime.now()
        }
    ) 