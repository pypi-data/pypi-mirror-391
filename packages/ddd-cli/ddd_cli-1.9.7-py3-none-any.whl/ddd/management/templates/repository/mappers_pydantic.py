# utils/mappers.py
import json
import decimal
from datetime import datetime, date, time
from uuid import UUID
from decimal import Decimal
from enum import Enum
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from django.db import models
from django.db.models import JSONField, ManyToManyField, ForeignKey

from ..domain.exceptions import [[ entity_name.capitalize() ]]ValueError
from ..domain.schemas import FileData

T = TypeVar("T", bound=BaseModel)

def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False

def make_json_safe(value):
    if isinstance(value, dict):
        return {k: make_json_safe(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [make_json_safe(v) for v in value]
    elif isinstance(value, (datetime, date, time)):
        return value.isoformat()
    elif isinstance(value, UUID):
        return str(value)
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, set):
        return list(value)
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return value        

class Mapper:

    @staticmethod
    def model_to_entity(model_instance: models.Model, entity_class: Type[T]) -> T:
        """Convierte modelo Django → entidad Pydantic con validación y submodelos"""
        
        if not model_instance:
            raise PromotionValueError("Model_instance_cannot_be_None_Cannot_convert_None_to_entity")

        data = {}

        for field_name, field_info in entity_class.model_fields.items():
            model_field_name = field_info.alias or field_name

            if not hasattr(model_instance, model_field_name):
                # Usar default si está definido
                if field_info.default_factory:
                    data[field_name] = field_info.default_factory()
                elif field_info.default is not None:
                    data[field_name] = field_info.default
                continue

            value = getattr(model_instance, model_field_name)
            field_object = None
            try:
                field_object = model_instance._meta.get_field(model_field_name)
            except Exception:
                pass

            # ManyToMany
            if isinstance(value, models.Manager):
                value = list(value.values_list('pk', flat=True)) if value else []

            # ForeignKey / OneToOne
            elif hasattr(value, 'pk') and value is not None:
                value = value.pk

            # Archivos e Imágenes
            elif field_object and isinstance(field_object, (models.FileField, models.ImageField)):
                try:
                    if value and value.name and hasattr(value, 'url'):
                        file_info = {"file_name": value.name, "url": value.url}
                        if field_info.annotation == FileData:
                            value = FileData(**file_info)
                        else:
                            value = file_info
                    else:
                        value = None
                except (ValueError, AttributeError):
                    value = None

            # Decimal → float
            elif isinstance(value, decimal.Decimal):
                value = float(value)

            # Submodelos Pydantic
            elif isinstance(field_info.annotation, type) and issubclass(field_info.annotation, BaseModel):
                if isinstance(value, dict):
                    value = field_info.annotation.model_validate(value)

            data[field_name] = value

        return entity_class.model_validate(data)    

    @staticmethod
    def update_model_from_entity(instance, entity, excluded_fields=None):
        """
        Actualiza una instancia de modelo Django desde una entidad de dominio.
        
        - Ignora campos no persistibles.
        - Ignora valores None.
        - Maneja correctamente JSONField, ForeignKey y ManyToMany.
        """
        excluded_fields = excluded_fields or []

        for key, value in entity.to_dict().items():
            if (
                key is not None
                and key not in excluded_fields
                and hasattr(instance, key)
                and value is not None
            ):
                model_field = instance._meta.get_field(key)

                # JSONField
                if isinstance(model_field, JSONField):
                    if isinstance(value, dict) and is_json_serializable(make_json_safe(value)):
                        setattr(instance, key, make_json_safe(value))

                # ForeignKey (ej: company_id → company)
                elif isinstance(model_field, ForeignKey) and key.endswith("_id"):
                    setattr(instance, key, value)

                # ManyToMany (ej: branches, categories)
                elif isinstance(model_field, ManyToManyField):
                    # Se actualiza con .set() después de guardar la instancia
                    pass  # se maneja fuera de esta función
                
                # id y uuid se ignoran
                elif key in ['id', 'uuid']:
                    pass  # No se actualizan estos campos

                # Campo normal
                else:
                    setattr(instance, key, value)            

    @staticmethod
    def entity_to_dict(entity_instance: BaseModel) -> dict:
        """Convierte una entidad Pydantic a diccionario"""
        return entity_instance.model_dump()

    @staticmethod
    def model_to_dict(model_instance: models.Model) -> dict:
        """Convierte modelo Django → dict (sin pasar por entidad)"""
        # Tu implementación actual aquí (no cambia)
        data = {}
        for field in model_instance._meta.get_fields():
            try:
                value = getattr(model_instance, field.name)
                if isinstance(field, models.ManyToManyField):
                    data[field.name] = list(value.values_list('pk', flat=True))
                elif isinstance(field, models.ForeignKey) and value:
                    data[field.name] = value.pk
                else:
                    data[field.name] = value
            except (AttributeError, ValueError):
                continue
        return data


        
