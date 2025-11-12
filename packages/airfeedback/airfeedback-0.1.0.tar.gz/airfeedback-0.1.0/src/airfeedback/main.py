"""
AirFeedback - Simple feedback collection for Air/FastAPI apps.

Usage:
    async def save_feedback(user_id: int, text: str, route: str | None):
        # Your save logic here (DB, file, API call, etc.)
        feedback = Feedback(user_id=user_id, text=text, route=route)
        session.add(feedback)
        await session.commit()

    feedback = AirFeedback(on_save=save_feedback)
    app.mount_routes(feedback.routes)

    # In your UI (unstyled by default):
    feedback.button()
    feedback.modal()

    # With DaisyUI:
    feedback.button(class_="btn btn-ghost btn-sm")
    feedback.modal(
        modal_class="",
        form_class="",
        textarea_class="textarea textarea-bordered w-full mb-4 min-h-32",
        submit_class="btn btn-primary",
        cancel_class="btn ml-2"
    )

    # With custom CSS:
    feedback.button(class_="my-feedback-btn")
    feedback.modal(textarea_class="my-textarea", submit_class="my-submit-btn")
"""

from collections.abc import Callable
from typing import Any

import air


class AirFeedback:
    """Flexible feedback collection system."""

    def __init__(
        self,
        on_save: Callable[[int, str, str | None], Any],
        route_path: str = "/feedback",
        button_text: str = "💬 Feedback",
        success_message: str = "✓ Thanks for your feedback!",
        error_message: str = "Feedback cannot be empty",
    ):
        """
        Initialize AirFeedback.

        Args:
            on_save: Async callback(user_id, text, route) to save feedback
            route_path: URL path for feedback submission (default: /feedback)
            button_text: Text for feedback button (default: 💬 Feedback)
            success_message: Message shown on successful submission
            error_message: Message shown on validation error
        """
        self.on_save = on_save
        self.route_path = route_path
        self.button_text = button_text
        self.success_message = success_message
        self.error_message = error_message
        self._cleanup_js = "feedback_modal.close(); this.reset(); document.querySelector('#feedback-result').innerHTML = '';"

    @property
    def routes(self) -> list[tuple[str, Callable]]:
        """Returns list of (path, handler) tuples to register."""
        return [(self.route_path, self._submit_handler)]

    async def _submit_handler(self, request: air.Request, user: Any):
        """Handle feedback submission."""
        form = await request.form()
        text = form.get("text", "").strip()
        route = form.get("route", "")

        if not text:
            return air.Div(
                self.error_message,
                class_="text-error text-sm",
            )

        # Get user ID - flexible to handle different user objects
        user_id = user.id if hasattr(user, "id") else user

        await self.on_save(user_id, text, route if route else None)

        return air.Div(
            air.P(self.success_message, class_="text-success font-semibold"),
            id="feedback-result",
        )

    def button(self, class_: str = "", **kwargs) -> air.Button:
        """
        Returns a feedback button component.

        Args:
            class_: CSS classes to apply
            **kwargs: Additional attributes for the button
        """
        return air.Button(
            self.button_text,
            onclick="document.getElementById('feedback-route').value = window.location.pathname; feedback_modal.showModal();",
            class_=class_,
            **kwargs,
        )

    def modal(
        self,
        modal_class: str = "",
        form_class: str = "",
        textarea_class: str = "",
        submit_class: str = "",
        cancel_class: str = "",
        title: str = "Share Your Feedback",
        title_class: str = "",
        placeholder: str = "What's on your mind? Bugs, feature requests, or just say hi!",
    ) -> air.Dialog:
        """
        Returns a feedback modal component (unstyled by default).

        Args:
            modal_class: CSS classes for modal container
            form_class: CSS classes for form
            textarea_class: CSS classes for textarea
            submit_class: CSS classes for submit button
            cancel_class: CSS classes for cancel button
            title: Modal title text
            title_class: CSS classes for title
            placeholder: Textarea placeholder text
        """
        return air.Dialog(
            air.Div(
                air.Form(
                    air.H3(title, class_=title_class) if title else None,
                    air.Textarea(
                        placeholder=placeholder,
                        name="text",
                        class_=textarea_class,
                        required=True,
                    ),
                    air.Input(type="hidden", name="route", id="feedback-route"),
                    air.Div(id="feedback-result", class_="mb-4"),
                    air.Div(
                        air.Button(
                            "Submit",
                            type="submit",
                            class_=submit_class,
                        ),
                        air.Button(
                            "Cancel",
                            type="button",
                            onclick=self._cleanup_js,
                            class_=cancel_class,
                        ),
                        class_="flex justify-end",
                    ),
                    method="dialog",
                    hx_post=self.route_path,
                    hx_target="#feedback-result",
                    hx_swap="innerHTML",
                    class_=form_class,
                    **{
                        "hx-on::after-swap": f"setTimeout(() => {{ {self._cleanup_js} }}, 800)"
                    },
                ),
                class_=modal_class,
            ),
            id="feedback_modal",
            class_="modal",
        )
