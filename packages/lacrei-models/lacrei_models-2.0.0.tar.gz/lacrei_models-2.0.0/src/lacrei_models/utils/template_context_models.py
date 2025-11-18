from pydantic import BaseModel as PydanticBaseModel


class BaseTemplateContext(PydanticBaseModel):
    has_base_email_context: bool
    _template_prefix: str = ""

    @classmethod
    def convert_from_pickled_context(cls, pickled_context: dict) -> dict:
        assert cls._template_prefix

        kwargs_after_conversion = (
            cls._convert_from_pickled_content_to_this_model_args(pickled_context) or {}
        )
        validated_instance = cls(**kwargs_after_conversion)
        json_dict = validated_instance.model_dump(mode="json")
        json_dict.pop("has_base_email_context", False)

        return json_dict

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        cls, pickled_context: dict
    ) -> dict:  # pragma: no cover
        raise NotImplementedError()


class WithBaseEmailContext(BaseTemplateContext):
    has_base_email_context: bool = True
