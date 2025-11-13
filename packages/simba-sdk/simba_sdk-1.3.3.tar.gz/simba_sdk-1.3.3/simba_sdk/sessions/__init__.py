import inspect
import logging
import traceback
from dataclasses import fields, is_dataclass
from functools import wraps
from typing import Callable, Type, cast

from pydantic import BaseModel, ValidationError

from simba_sdk.sessions.base import Base

logger = logging.getLogger(__name__)


def parse(model_type: Type):
    def decorator(fn: Callable):
        param_names = list(inspect.signature(fn).parameters.keys())

        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            args, kwargs = _handle_parse_args(fn, args, kwargs, model_type, param_names)
            return await fn(*args, **kwargs)

        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            args, kwargs = _handle_parse_args(fn, args, kwargs, model_type, param_names)
            return fn(*args, **kwargs)

        return async_wrapper if inspect.iscoroutinefunction(fn) else sync_wrapper

    return decorator


def _handle_parse_args(
    fn: Callable,
    args: tuple,
    kwargs: dict,
    model_type: Type,
    param_names: list,
):
    """
    Convert incoming args/kwargs into a model instance for the target function.

    Supports:
    - Passing a Pydantic model or dataclass instance directly (positional or named).
    - Building the model/dataclass from kwargs when an instance is not provided.
    - Forwarding extra kwargs that do not belong to the model.
    - Safe 'field_' remapping for Pydantic models only.

    Raises:
        ValueError: If conversion fails due to type or validation errors.
    """
    try:
        # Find the parameter name into which we will inject the parsed model
        target_param = _find_target_param_name(param_names)
        target_idx = param_names.index(target_param)

        if target_param in kwargs and isinstance(kwargs[target_param], model_type):
            # A full Pydantic or dataclass model instance has been supplied in kwargs
            return args, kwargs

        if len(args) > target_idx and isinstance(args[target_idx], model_type):
            # A full Pydantic or dataclass model instance has been supplied in args
            # Remove any duplicate entry in kwargs for the target param (keeps all != target_param)
            cleaned_kwargs = {k: v for k, v in kwargs.items() if k != target_param}
            return args, cleaned_kwargs

        if issubclass(model_type, BaseModel):
            # No model instance supplied. Build Pydantic model from kwargs:
            model_field_names = set(model_type.model_fields.keys())

            # Remap for Pydantic models only (e.g., context -> field_context)
            # mapped: A copy of kwargs with any applicable remaps applied (e.g., adds 'field_context' from 'context')
            # consumed: contains Keys from kwargs that were remapped to model field names (e.g., 'context' → 'field_context')
            mapped, consumed = remap_fallback_field_prefixes_for_model(
                model_type, kwargs
            )

            # Grab the model keys from kwargs, only grab keys that are in model_field_names
            model_input = {k: v for k, v in mapped.items() if k in model_field_names}

            # Validate and instantiate the Pydantic model using the found set of model key/values
            model_instance = model_type.model_validate(model_input)

            # Collect passthrough kwargs: those not in the model and not remapped
            passthrough = {
                k: v
                for k, v in kwargs.items()
                if k not in model_field_names
                and k not in consumed
                and k != target_param
            }

        # Build dataclass from kwargs
        elif is_dataclass(model_type):
            # No remapping for dataclasses, see above for description of `consumed`
            consumed = set()

            # No dataclass model instance supplied. Build dataclass model from kwargs:
            model_field_names = {f.name for f in fields(model_type)}
            # Filter kwargs to only those matching dataclass field names
            model_input = {k: v for k, v in kwargs.items() if k in model_field_names}

            # Instantiate the dataclass
            if issubclass(model_type, Base):
                model_instance = cast(Type[Base], model_type).from_dict(model_input)
            else:
                model_instance = model_type(**model_input)

            # Collect passthrough kwargs: those not in the dataclass
            passthrough = {
                k: v
                for k, v in kwargs.items()
                if k not in model_field_names and k != target_param
            }

        else:
            raise TypeError(f"Unsupported model type: {model_type}")

        # Log extra fields and missing optional fields
        # extra_keys is difference between the passed kwargs and keys used (model fields, remapped keys, and the model parameter name)
        extra_keys = set(kwargs.keys()) - (
            model_field_names | consumed | {target_param}
        )
        # missing_keys: Optional/defaulted model keys not provided in kwargs
        missing_keys = model_field_names - set(model_input.keys())
        if extra_keys:
            logger.info(
                f"[parse] Ignored extra fields for {model_type.__name__}: {sorted(extra_keys)}"
            )
        if missing_keys:
            logger.debug(
                f"[parse] Missing optional fields for {model_type.__name__}: {sorted(missing_keys)}"
            )

        # --- Inject model into args or kwargs ---
        if len(args) > target_idx:
            # Replace positional arg at target index
            new_args = list(args)
            new_args[target_idx] = model_instance
            return tuple(new_args), passthrough
        else:
            # Inject as keyword arg
            return args, {target_param: model_instance, **passthrough}

    except (TypeError, ValidationError) as ex:
        # Wrap errors with context for easier debugging
        stack = traceback.format_exc()
        raise ValueError(
            f"[parse] Failed to convert kwargs into {model_type.__name__}\n"
            f"kwargs: {kwargs}\n"
            f"Error: {ex}\n"
            f"Traceback:\n{stack}"
        )


def _find_target_param_name(param_names) -> str:
    """Return the first parameter name that isn't 'self' or 'cls'."""
    for name in param_names:
        if name not in ("self", "cls"):
            return name
    raise RuntimeError("No suitable parameter found to inject parsed model into.")


def remap_fallback_field_prefixes_for_model(
    model_type: Type, data: dict
) -> tuple[dict, set]:
    """
    Used to map the server's proper filed names, e.g. in CreateVCHttp `context` to the SDK `field_context`.
    The SDK mangles the proper field name because it is build from the OpenApi data which contains
    the alias `@context` which is not an allowed python/pydantic field name.

    The mapping is only performed iff:
      - the Pydantic model has a prefixed version of the field, e.g., `field_context`
      - the SDK model does NOT have a real `context` field.
      - caller passed `context` but not `field_context` in kwargs.

    Returns (new_data_dict, consumed_source_keys)
    """
    out = dict(data)
    consumed: set = set()

    # Collect declared field names for the model (pydantic OR dataclass)
    if issubclass(model_type, BaseModel):
        all_fields = set(model_type.model_fields.keys())
    elif is_dataclass(model_type):
        all_fields = {f.name for f in fields(model_type)}
    else:
        raise TypeError(f"Unsupported model type: {model_type}")

    # Apply the field_ fallback mapping
    for field_name in all_fields:
        if not field_name.startswith("field_"):
            continue

        # e.g. field_context -> context
        input_key = field_name[len("field_") :]  # suffix after "field_"

        if (
            input_key in data  # caller passed `context`
            and field_name not in data  # but not `field_context`
            and input_key not in all_fields  # and model does NOT have a real `context`
        ):
            out[field_name] = data[input_key]
            consumed.add(input_key)
            logger.debug(
                f"[parse] Remapped '{input_key}' -> '{field_name}' (field_ fallback)"
            )

    return out, consumed
