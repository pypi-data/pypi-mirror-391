"""Helper classes for scripts for cluster support packages."""

from enum import Enum
from typing import Any, Optional

from cyberfusion.ClusterSupport._interfaces import (
    APIObjectInterface,
    sort_lists,
)
from cyberfusion.ClusterSupport.enums import IPAddressFamily
from cyberfusion.ClusterSupport.nodes import NodeGroup
from cyberfusion.ClusterSupport.task_collections import TaskCollection

ENDPOINT_PUBLIC_CLUSTERS = "/api/v1/clusters"
ENDPOINT_INTERNAL_CLUSTERS = "/internal/api/v1/clusters"


class MeilisearchEnvironment(str, Enum):
    """Meilisearch environments."""

    PRODUCTION: str = "production"
    DEVELOPMENT: str = "development"


class HTTPRetryCondition(str, Enum):
    """HTTP retry conditions."""

    CONNECTION_FAILURE: str = "Connection failure"
    EMPTY_RESPONSE: str = "Empty response"
    JUNK_RESPONSE: str = "Junk response"
    RESPONSE_TIMEOUT: str = "Response timeout"
    ZERO_RTT_REJECTED: str = "0-RTT rejected"
    HTTP_STATUS_401: str = "HTTP status 401"
    HTTP_STATUS_403: str = "HTTP status 403"
    HTTP_STATUS_404: str = "HTTP status 404"
    HTTP_STATUS_408: str = "HTTP status 408"
    HTTP_STATUS_425: str = "HTTP status 425"
    HTTP_STATUS_500: str = "HTTP status 500"
    HTTP_STATUS_501: str = "HTTP status 501"
    HTTP_STATUS_502: str = "HTTP status 502"
    HTTP_STATUS_503: str = "HTTP status 503"
    HTTP_STATUS_504: str = "HTTP status 504"


class LoadBalancingMethod(str, Enum):
    """Load balancing methods."""

    ROUND_ROBIN: str = "Round Robin"
    SOURCE_IP_ADDRESS: str = "Source IP Address"


class UNIXUserHomeDirectory(str, Enum):
    """UNIX user home directories."""

    VAR_WWW_VHOSTS: str = "/var/www/vhosts"
    VAR_WWW: str = "/var/www"
    HOME: str = "/home"
    MNT_MAIL: str = "/mnt/mail"
    MNT_BACKUPS: str = "/mnt/backups"


class PHPExtension(str, Enum):
    """PHP extensions."""

    REDIS: str = "redis"
    IMAGICK: str = "imagick"
    SQLITE3: str = "sqlite3"
    XMLRPC: str = "xmlrpc"
    INTL: str = "intl"
    BCMATH: str = "bcmath"
    XDEBUG: str = "xdebug"
    PGSQL: str = "pgsql"
    SSH2: str = "ssh2"
    LDAP: str = "ldap"
    MCRYPT: str = "mcrypt"
    APCU: str = "apcu"
    SQLSRV: str = "sqlsrv"
    GMP: str = "gmp"
    VIPS: str = "vips"
    EXCIMER: str = "excimer"
    TIDEWAYS: str = "tideways"
    MAILPARSE: str = "mailparse"
    UV: str = "uv"
    AMQP: str = "amqp"


class ClusterGroup(str, Enum):
    """Cluster groups."""

    WEB: str = "Web"
    MAIL: str = "Mail"
    DB: str = "Database"
    BORG_CLIENT: str = "Borg Client"
    BORG_SERVER: str = "Borg Server"
    REDIRECT: str = "Redirect"


class Cluster(APIObjectInterface):
    """Represents object."""

    _TABLE_HEADERS = [
        "ID",
        "Name",
        "Description",
        "Site",
    ]
    _TABLE_HEADERS_DETAILED: list = []

    _TABLE_FIELDS = [
        "id",
        "name",
        "description",
        "_site_name",
    ]
    _TABLE_FIELDS_DETAILED: list = []

    @sort_lists  # type: ignore[misc]
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        self.json_body = obj

        self.id = obj["id"]
        self.name = obj["name"]
        self.customer_id = obj["customer_id"]
        self.description = obj["description"]
        self.region_id = obj["region_id"]
        self.created_at = obj["created_at"]
        self.updated_at = obj["updated_at"]

        self.site = self.support.get_sites(id_=self.region_id)[0]
        self._site_name = self.site.name

        self._label = f"{self.description} ({self.name})"

    @property
    def redis_master_node_hostname(self) -> Optional[str]:
        """Get hostname of Redis master node."""
        for node in self.support.get_nodes(cluster_id=self.id):
            if not node.groups_properties[NodeGroup.REDIS]:
                continue

            if not node.groups_properties[NodeGroup.REDIS]["is_master"]:
                continue

            return node.hostname

        return None

    @property
    def mariadb_master_node_hostname(self) -> Optional[str]:
        """Get hostname of MariaDB master node."""
        for node in self.support.get_nodes(cluster_id=self.id):
            if not node.groups_properties[NodeGroup.MARIADB]:
                continue

            if not node.groups_properties[NodeGroup.MARIADB]["is_master"]:
                continue

            return node.hostname

        return None

    @property
    def rabbitmq_master_node_hostname(self) -> Optional[str]:
        """Get hostname of RabbitMQ master node."""
        for node in self.support.get_nodes(cluster_id=self.id):
            if not node.groups_properties[NodeGroup.RABBITMQ]:
                continue

            if not node.groups_properties[NodeGroup.RABBITMQ]["is_master"]:
                continue

            return node.hostname

        return None

    def create(
        self,
        *,
        customer_id: int,
        description: str,
        site_id: int,
    ) -> TaskCollection:
        """Create object."""
        url = ENDPOINT_PUBLIC_CLUSTERS
        data = {
            "customer_id": customer_id,
            "description": description,
            "site_id": site_id,
        }

        # Create object and create and set attributes on TaskCollection
        # class

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        obj = TaskCollection(self.support)
        obj._set_attributes_from_model(response)

        # Get object and set attributes on local class

        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{obj.object_id}"

        self.support.request.GET(url)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

        self.support.clusters.append(self)

        return obj

    def update(self) -> None:
        """Update object."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}"
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "site_id": self.site_id,
        }

        self.support.request.PATCH(url, data)
        response = self.support.request.execute()

        self._set_attributes_from_model(response)

    def delete(self) -> None:
        """Delete object."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}"

        self.support.request.DELETE(url)
        self.support.request.execute()

        self.support.clusters.remove(self)

    def get_borg_public_ssh_key(self) -> str:
        """Get Borg public SSH key."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}/borg-ssh-key"

        self.support.request.GET(url)
        response = self.support.request.execute()

        return response["public_key"]

    def get_common_properties(self) -> dict[str, Any]:
        """Get common properties."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/common-properties"

        self.support.request.GET(url)

        return self.support.request.execute()

    def get_ip_addresses(self) -> dict[str, Any]:
        """Get IP addresses."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}/ip-addresses"

        self.support.request.GET(url)

        return self.support.request.execute()

    def create_ip_address(
        self,
        *,
        service_account_name: str,
        dns_name: str,
        address_family: IPAddressFamily,
    ) -> TaskCollection:
        """Create IP address."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}/ip-addresses"
        data = {
            "service_account_name": service_account_name,
            "dns_name": dns_name,
            "address_family": address_family,
        }

        self.support.request.POST(url, data)
        response = self.support.request.execute()

        obj = TaskCollection(self.support)
        obj._set_attributes_from_model(response)

        return obj

    def delete_ip_address(self, ip_address: str) -> TaskCollection:
        """Delete IP address."""
        url = f"{ENDPOINT_PUBLIC_CLUSTERS}/{self.id}/ip-addresses/{ip_address}"

        self.support.request.DELETE(url)
        response = self.support.request.execute()

        obj = TaskCollection(self.support)
        obj._set_attributes_from_model(response)

        return obj
