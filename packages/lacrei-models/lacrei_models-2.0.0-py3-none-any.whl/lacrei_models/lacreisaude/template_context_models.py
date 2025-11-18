from pydantic import HttpUrl

from lacrei_models.utils.template_context_models import WithBaseEmailContext


class BoardVerificationNumberRejectedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/board_verification_number_rejected"

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        return {}


class PostRegistrationApprovedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/post_registration_approved"
    button_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        button_url = pickled_context.get("button_url", "")

        return {"button_url": button_url}


class PostRegistrationRejectedContext(WithBaseEmailContext):
    _template_prefix: str = "verification/post_registration_rejected"
    button_url: HttpUrl

    @classmethod
    def _convert_from_pickled_content_to_this_model_args(
        self, pickled_context: dict
    ) -> dict:
        button_url = pickled_context.get("button_url", "")

        return {"button_url": button_url}
