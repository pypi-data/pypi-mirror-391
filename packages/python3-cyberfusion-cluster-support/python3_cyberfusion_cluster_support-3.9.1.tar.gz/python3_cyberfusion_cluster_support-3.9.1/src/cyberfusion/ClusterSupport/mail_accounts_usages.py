"""Helper classes for scripts for cluster support packages."""

from datetime import datetime

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)

ENDPOINT_PUBLIC_MAIL_ACCOUNTS_USAGES = "/api/v1/mail-accounts/usages"
ENDPOINT_INTERNAL_MAIL_ACCOUNTS_USAGES = "/internal/api/v1/mail-accounts/usages"


class MailAccountUsage(APIObjectInterface):
    """Represents object."""

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.json_body = obj

        self.usage = obj["usage"]
        self.mail_account_id = obj["mail_account_id"]
        self.timestamp = obj["timestamp"]

        self.datetime_object = datetime.strptime(self.timestamp, "%Y-%m-%dT%H:%M:%S")

        self.mail_account = self.support.get_mail_accounts(id_=self.mail_account_id)[0]

    def create(self, *, usage: float, mail_account_id: int) -> None:
        """Create object."""
        url = ENDPOINT_INTERNAL_MAIL_ACCOUNTS_USAGES
        data = {
            "usage": usage,
            "mail_account_id": mail_account_id,
        }

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)
