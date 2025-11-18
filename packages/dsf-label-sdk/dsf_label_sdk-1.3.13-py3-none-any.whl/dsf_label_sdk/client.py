import os
import requests
import time
import logging
import json
import numpy as np
import uuid 
import io
from typing import Dict, List, Any, Optional, Union
from . import __version__
from .exceptions import ValidationError, APIError, JobTimeoutError
from .models import Config, EvaluationResult, Job
from google.cloud import storage

logger = logging.getLogger(__name__)

TIER_LIMITS = {
    'community': {'batch': 100},
    'professional': {'batch': 1000},
    'enterprise': {'batch': 10000}
}

class DSFLabelClient:
    # Usamos el dominio estable
    BASE_URL = 'https://dsf-label-api-i42k2m0qw-api-dsfuptech.vercel.app/api' 
    
    def __init__(self, license_key: Optional[str] = None, tier: str = 'community', timeout: int = 60):
        if tier not in TIER_LIMITS:
            raise ValidationError(f"Invalid tier: {tier}")
        
        self.license_key = license_key
        self.tier = tier
        self.timeout = timeout
        self.base_url = self.BASE_URL
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'DSF-Label-SDK/{__version__}'
        })
    
    # --- HELPER DE SANITIZACIÓN (FIX CRÍTICO 1) ---
    def _sanitize_value(self, v: Any) -> Any:
        """
        Convierte valores de NumPy a tipos nativos de Python y maneja recursión.
        Esto previene fallos de serialización JSON.
        """
        if isinstance(v, (np.generic,)):
            return v.item()
        if isinstance(v, (np.ndarray,)):
            return v.tolist()
        
        # Recursión para colecciones (listas y diccionarios)
        if isinstance(v, dict):
            return self._sanitize_record(v)
        if isinstance(v, list):
            return [self._sanitize_value(item) for item in v]

        return v

    def _sanitize_record(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica sanitización a los valores de un diccionario."""
        return {str(k): self._sanitize_value(v) for k, v in rec.items()}
    # ------------------------------------------

    def _prepare_payload(self, data_points: List[Dict[str, Any]], config: Dict, calibration: Dict) -> Dict[str, Any]:
        """Prepara el JSON body para la API, incluyendo la sanitización de vectores."""
        
        # FIX CRÍTICO 2 (parte 1): Sanitizar Config y Calibration ANTES de usarlos
        config = self._sanitize_record(config)
        calibration = self._sanitize_record(calibration)

        # 1. Sanitizar data_points: Limpia los datos de entrada para evitar TypeErrors de JSON
        sanitized_data_points = [self._sanitize_record(dp) for dp in data_points]

        fields = list(config.keys())
        sample = sanitized_data_points[0] if sanitized_data_points else {}
        
        # Lógica de extracción (se mantiene)
        has_embedding_keys = any(f"embedding_{f}" in sample for f in fields)
        is_vector = any(isinstance(sample.get(f), (list, np.ndarray)) for f in fields if f in sample)
        
        if has_embedding_keys:
            embeddings_batch = [{f: dp[f"embedding_{f}"] for f in fields} for dp in sanitized_data_points]
            prototypes_batch = [{f: dp[f"prototype_{f}"] for f in fields} for dp in sanitized_data_points]
            logger.info("Format: embedding_X/prototype_X")
        elif is_vector:
            embeddings_batch = [{f: dp[f] for f in fields if f in dp} for dp in sanitized_data_points]
            prototypes_batch = [{f: config[f].get('prototype', []) for f in fields} for _ in sanitized_data_points]
            logger.info("Format: vectors")
        else:
            raise ValidationError("Unknown format. Expected embeddings with 'embedding_X' keys or vector fields")
        
        # 2. Devolvemos el payload completo con la configuración adicional
        return {
            "embeddings_batch": embeddings_batch,
            "prototypes_batch": prototypes_batch,
            "config": config,
            "calibration": calibration, 
            "license_key": self.license_key,
            "tier": self.tier
        }

    def batch_evaluate(
        self, 
        data_points: List[Dict[str, Any]], 
        config: Optional[Union[Dict, Config]] = None,
        calibration: Optional[Dict[str, Dict]] = None, 
        mode: str = 'sync'
    ) -> Union[List[EvaluationResult], Job]:
        
        if isinstance(config, Config):
            config = config.to_dict()
        if calibration is None:
            calibration = {}

        batch_limit = TIER_LIMITS[self.tier]['batch']
        if len(data_points) > batch_limit and mode == 'sync':
            raise ValidationError(
                f"Batch ({len(data_points)}) exceeds {self.tier} limit for sync mode ({batch_limit}). "
                "Use mode='async'."
            )

        t0 = time.time()
        # full_payload ya tiene config/calibration sanitizados (ver _prepare_payload)
        full_payload = self._prepare_payload(data_points, config, calibration)

        try:
            # 🚀 MODO ASÍNCRONO (heavy payload -> enqueue)
            if mode == 'async' and self.tier in ['professional', 'enterprise']:
                
                endpoint = f"{self.base_url}/enqueue"
                sanitized_payload = self._sanitize_record(full_payload) # FIX CRÍTICO 2 (parte 2)
                
                resp = self.session.post(
                    endpoint, 
                    json=sanitized_payload, 
                    timeout=60 
                )
                
                resp.raise_for_status()

                job_data = resp.json()
                logger.info(
                    f"Async job {job_data.get('job_id')} enqueued in {time.time() - t0:.2f}s"
                )
                return Job(
                    job_id=job_data["job_id"],
                    sdk=self,
                    status=job_data.get("status", "queued"),
                )

            # ⚙️ MODO SÍNCRONO (lotes pequeños -> eval directa)
            else:
                api_payload = full_payload
                endpoint = f"{self.base_url}/evaluate" 
                sanitized_payload = self._sanitize_record(api_payload) # FIX CRÍTICO 2 (parte 2)
                
                resp = self.session.post(endpoint, json=sanitized_payload, timeout=self.timeout) 
                resp.raise_for_status()
                
                response_data = resp.json() # Capturar toda la respuesta

                scores = response_data.get("scores", [])
                metrics = response_data.get("metrics") 

                logger.info(f"Sync evaluation completed in {time.time() - t0:.2f}s")
                
                # FIX CRÍTICO 3: Incluir métricas en la Evaluación
                results = [
                    EvaluationResult(score=float(s), tier=self.tier, metrics=metrics) 
                    for s in scores
                ]
                
                # FIX: Adjuntar métricas de batch al primer resultado (compatibilidad)
                if metrics and results:
                    results[0].batch_metrics = metrics 

                return results

        except requests.exceptions.HTTPError as e:
            try:
                data = e.response.json()
            except Exception:
                data = {"error": e.response.text}
            raise APIError(f"API Error {e.response.status_code}: {data.get('error')}")

        except Exception as e:
            raise APIError(f"Evaluation failed: {e}")

    def get_job_status(self, job_id: str) -> Dict:
        """Consulta el estado de un job asíncrono"""
        try:
            endpoint = f"{self.base_url}/status/{job_id}"
            resp = self.session.get(endpoint, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            try: data = e.response.json()
            except: data = {'error': e.response.text}
            raise APIError(f"API Error {e.response.status_code}: {data.get('error')}")
        except Exception as e:
            raise APIError(f"Status check failed: {e}")

    def create_config(self) -> Config:
        return Config()
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
