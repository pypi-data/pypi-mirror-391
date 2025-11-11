from typing import ClassVar, List

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .conf import COGNITO_GROUPS_SESSION_KEY


class CognitoPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    """This mixin tests a user is in a required cognito group"""

    groups_required: ClassVar[List[str]] = []

    def test_func(self) -> bool:
        if request := getattr(self, "request", None):
            breakpoint()
            cognito_perms = request.session.get(COGNITO_GROUPS_SESSION_KEY, [])
            assert isinstance(cognito_perms, list)
            for group in self.groups_required:
                if group not in cognito_perms:
                    return False
            return True
        return False
