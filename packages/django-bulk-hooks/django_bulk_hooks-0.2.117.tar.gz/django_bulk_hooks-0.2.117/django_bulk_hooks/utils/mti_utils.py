"""Utilities for Multi-Table Inheritance (MTI) detection and field expansion."""

import logging
from typing import List, Type

from django.db import models

logger = logging.getLogger(__name__)


def get_mti_child_models(parent_model: Type[models.Model]) -> List[Type[models.Model]]:
    """
    Get all direct child models that inherit from a parent model via MTI.
    
    Django automatically creates a OneToOneField with parent_link=True from child
    to parent in MTI relationships. We can detect these via related_objects.
    
    Args:
        parent_model: The parent model class
        
    Returns:
        List of child model classes that inherit from parent_model via MTI
        
    Example:
        >>> class Business(Company):
        ...     pass
        >>> get_mti_child_models(Company)
        [<class 'Business'>]
    """
    child_models = []
    
    for related_object in parent_model._meta.related_objects:
        # MTI creates a OneToOneField from child to parent with parent_link=True
        if (related_object.one_to_one and 
            getattr(related_object.field, 'parent_link', False)):
            child_model = related_object.related_model
            child_models.append(child_model)
            
    return child_models


def expand_mti_related_fields(fields: tuple, model_cls: Type[models.Model]) -> list:
    """
    Expand related fields to include MTI child models automatically.
    
    When a field points to a parent model in an MTI hierarchy, this function
    automatically adds the child model lookup paths so that select_related
    can load the complete object graph without N+1 queries.
    
    For each direct field (not chained with __):
    1. Check if it's a relation field
    2. Get the related model
    3. Check if the related model has MTI child models
    4. Add child model lookups (e.g., "business__cimbbusiness")
    
    Chained fields (e.g., "business__name") are not expanded because MTI child
    fields are accessible through the parent once the child is loaded.
    
    Args:
        fields: Tuple of field names to expand
        model_cls: The model class being queried
        
    Returns:
        List of expanded field names with MTI child lookups added
        
    Example:
        Input: ("business", "revenue_stream")
        If business points to Business (parent) and CIMBBusiness (child) exists:
        Output: ["business", "business__cimbbusiness", "revenue_stream"]
    
    Notes:
        - If a parent has multiple MTI children, ALL children will be added as
          LEFT JOINs. Django handles this gracefully (returns NULL for non-matching
          children), but it does add extra joins.
        - This is a safe trade-off to ensure the framework "just works" without
          requiring users to know about MTI internals.
    """
    from django_bulk_hooks.operations.field_utils import _get_field_or_none
    
    expanded_fields = []
    
    for field in fields:
        expanded_fields.append(field)
        
        # Only process direct fields (not chained like "business__name")
        if "__" in field:
            continue
            
        # Get the field object
        relation_field = _get_field_or_none(model_cls, field)
        if relation_field is None or not relation_field.is_relation:
            continue
            
        # Get the related model
        related_model = getattr(relation_field.remote_field, "model", None)
        if related_model is None:
            continue
            
        # Check if the related model has MTI child models
        child_models = get_mti_child_models(related_model)
        if child_models:
            # Add the child model lookup paths
            for child_model in child_models:
                child_accessor = child_model._meta.model_name
                expanded_field = f"{field}__{child_accessor}"
                expanded_fields.append(expanded_field)
                logger.info(
                    "MTI EXPANSION: %s.%s -> added %s (child: %s.%s)",
                    model_cls.__name__,
                    field,
                    expanded_field,
                    related_model.__name__,
                    child_model.__name__
                )
        else:
            logger.debug(
                "MTI EXPANSION: %s.%s -> no MTI children found for %s",
                model_cls.__name__,
                field,
                related_model.__name__
            )
    
    return expanded_fields

