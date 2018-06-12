from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.storage import StorageManagementClient
from msrestazure.azure_active_directory import ServicePrincipalCredentials
from azure.mgmt.network.models import public_ip_address_dns_settings

from cloudshell.cp.azure.common.singletons import SingletonByArgsMeta
from cloudshell.cp.azure.common.singletons import AbstractComparableInstance


class AzureClientsManager(AbstractComparableInstance):
    __metaclass__ = SingletonByArgsMeta

    def check_params_equality(self, cloud_provider, *args, **kwargs):
        """Check if instance have the same attributes for initializing Azure session as provided in cloud_provider

        :param cloud_provider: AzureCloudProviderResourceModel instance
        :return: (bool) True/False whether attributes are same or not
        """
        subscription_id = self._get_subscription(cloud_provider)
        application_id = self._get_azure_application_id(cloud_provider)
        application_key = self._get_azure_application_key(cloud_provider)
        tenant = self._get_azure_tenant(cloud_provider)

        return all([
            subscription_id == self._subscription_id,
            application_id == self._application_id,
            application_key == self._application_key,
            tenant == self._tenant])

    def __init__(self, cloud_provider):
        """
        :param cloud_provider: AzureCloudProviderResourceModel instance
        :return
        """
        self._subscription_id = self._get_subscription(cloud_provider)
        self._application_id = self._get_azure_application_id(cloud_provider)
        self._application_key = self._get_azure_application_key(cloud_provider)
        self._tenant = self._get_azure_tenant(cloud_provider)
        self._service_credentials = self._get_service_credentials()
        self._compute_client = None
        self._network_client = None
        self._storage_client = None
        self._resource_client = None
        self._subscription_client = None

    def _get_service_credentials(self):
        return ServicePrincipalCredentials(client_id=self._application_id, secret=self._application_key, tenant=self._tenant)

    def _get_subscription(self, cloud_provider_model):
        return cloud_provider_model.azure_subscription_id

    def _get_azure_application_id(self, cloud_provider_model):
        return cloud_provider_model.azure_application_id

    def _get_azure_application_key(self, cloud_provider_model):
        return cloud_provider_model.azure_application_key

    def _get_azure_tenant(self, cloud_provider_model):
        return cloud_provider_model.azure_tenant

    @property
    def compute_client(self):
        if self._compute_client is None:
            with SingletonByArgsMeta.lock:
                if self._compute_client is None:
                    self._compute_client = ComputeManagementClient(self._service_credentials, self._subscription_id)

        return self._compute_client

    @property
    def network_client(self):
        if self._network_client is None:
            with SingletonByArgsMeta.lock:
                if self._network_client is None:
                    self._network_client = NetworkManagementClient(self._service_credentials, self._subscription_id)

        return self._network_client

    @property
    def storage_client(self):
        if self._storage_client is None:
            with SingletonByArgsMeta.lock:
                if self._storage_client is None:
                    self._storage_client = StorageManagementClient(self._service_credentials, self._subscription_id)

        return self._storage_client

    @property
    def resource_client(self):
        if self._resource_client is None:
            with SingletonByArgsMeta.lock:
                if self._resource_client is None:
                    self._resource_client = ResourceManagementClient(self._service_credentials, self._subscription_id)

        return self._resource_client

    @property
    def subscription_client(self):
        if self._subscription_client is None:
            with SingletonByArgsMeta.lock:
                if self._subscription_client is None:
                    self._subscription_client = SubscriptionClient(self._service_credentials)

        return self._subscription_client

    def connect_to_azure(self, clp):
        self.clp = clp
        self.clients = AzureClientsManager(cloud_provider=self.clp)

    def get_vm_object_by_name(self, resource_group, vm_name):
        vm = self.clients.compute_client.virtual_machines.get\
            (resource_group_name=resource_group, vm_name=vm_name)
        return vm

    def set_dns_label_on_public_ip(self, resource_group, vm_name, new_domain_name='', fqdn_suffix=''):
        my_public_ip = self.clients.network_client.public_ip_addresses.get(
            resource_group_name=resource_group,
            public_ip_address_name=vm_name
        )
        my_dns = public_ip_address_dns_settings.PublicIPAddressDnsSettings()
        my_public_ip.domain_name_label = new_domain_name
        my_dns.domain_name_label = new_domain_name
        my_dns.fqdn = '{0}.{1}'.format(new_domain_name, fqdn_suffix)
        my_public_ip.fqdn = '{0}.{1}'.format(new_domain_name, fqdn_suffix)
        my_public_ip.dns_settings = my_dns
        self.clients.network_client.public_ip_addresses.create_or_update(
            resource_group_name=resource_group,
            public_ip_address_name=vm_name,
            parameters=my_public_ip
        )

    def get_dns_label_on_public_ip(self, resource_group, vm_name):
        my_public_ip = self.clients.network_client.public_ip_addresses.get(
            resource_group_name=resource_group,
            public_ip_address_name=vm_name
        )
        dns_settings = my_public_ip.dns_settings
        if not dns_settings:
            dns_web_address = ''
        else:
            dns_web_address = '{0}'.format(dns_settings.fqdn)
        return dns_web_address

class CloudProvider(object):
    def __init__(self):
        self.azure_subscription_id = ''
        self.azure_tenant = ''
        self.azure_application_key = ''
        self.azure_application_id = ''



# clp = CloudProvider()
# clients = AzureClientsManager(cloud_provider=clp)
# nic_name = vm.network_profile.network_interfaces[0].id.split('/')[-1]
# nic = clients.network_client.network_interfaces.get(resource_group_name=resource_group, network_interface_name=nic_name)
# print vm.name
# my actual code:
