"""Factories for API object."""

import factory
import factory.fuzzy

from cyberfusion.ClusterSupport.clusters import (
    Cluster,
)
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class ClusterFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = Cluster

        exclude = (
            "customer",
            "cluster",
            "site",
            "site_to_customer",
            "service_account_phpmyadmin",
            "service_account_security_txt_policy_server",
            "service_account_mail_gateway",
            "service_account_load_balancer",
            "service_account_mail_proxy",
            "service_account_server_phpmyadmin",
            "service_account_server_security_txt_policy_server",
            "service_account_server_mail_gateway",
            "service_account_server_load_balancer",
            "service_account_server_mail_proxy",
        )

    customer = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.customers.CustomerFactory"
    )
    customer_id = factory.SelfAttribute("customer.id")
    description = factory.Faker("word")
    site = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.sites.SiteFactory",
    )
    site_id = factory.SelfAttribute("site.id")
    site_to_customer = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.sites_to_customers.SiteToCustomerFactory",
        customer=factory.SelfAttribute("..customer"),
        site=factory.SelfAttribute("..site"),
    )
    service_account_phpmyadmin = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountPhpMyAdminFactory",
        site=factory.SelfAttribute("..site"),
    )
    service_account_security_txt_policy_server = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountSecurityTXTPolicyServerFactory",
        site=factory.SelfAttribute("..site"),
    )
    service_account_mail_gateway = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountMailGatewayFactory",
        site=factory.SelfAttribute("..site"),
    )
    service_account_load_balancer = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountLoadBalancerFactory",
        site=factory.SelfAttribute("..site"),
    )
    service_account_mail_proxy = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_accounts.ServiceAccountMailProxyFactory",
        site=factory.SelfAttribute("..site"),
    )
    service_account_server_phpmyadmin = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_account_servers.ServiceAccountServerPhpMyAdminFactory",
        service_account=factory.SelfAttribute("..service_account_phpmyadmin"),
    )
    service_account_server_security_txt_policy_server = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_account_servers.ServiceAccountServerSecurityTXTPolicyServerFactory",
        service_account=factory.SelfAttribute(
            "..service_account_security_txt_policy_server"
        ),
    )
    service_account_server_mail_gateway = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_account_servers.ServiceAccountServerMailGatewayFactory",
        service_account=factory.SelfAttribute("..service_account_mail_gateway"),
    )
    service_account_server_load_balancer = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_account_servers.ServiceAccountServerLoadBalancerFactory",
        service_account=factory.SelfAttribute("..service_account_load_balancer"),
    )
    service_account_server_mail_proxy = factory.SubFactory(
        "cyberfusion.ClusterSupport.tests_factories.service_account_servers.ServiceAccountServerMailProxyFactory",
        service_account=factory.SelfAttribute("..service_account_mail_proxy"),
    )


class ClusterWebFactory(ClusterFactory):
    """Factory for specific object."""

    pass


class ClusterRedirectFactory(ClusterFactory):
    """Factory for specific object."""

    pass


class ClusterDatabaseFactory(ClusterFactory):
    """Factory for specific object."""

    pass


class ClusterMailFactory(ClusterFactory):
    """Factory for specific object."""

    pass


class ClusterBorgClientFactory(ClusterFactory):
    """Factory for specific object."""

    pass


class ClusterBorgServerFactory(ClusterFactory):
    """Factory for specific object."""

    pass
