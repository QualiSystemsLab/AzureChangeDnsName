import cloudshell.helpers.scripts.cloudshell_scripts_helpers as script_help
import Azurehandler



class dns_altering_script():
    def __init__(self):
        self.session = script_help.get_api_session()
        self.name = script_help.get_resource_context_details().name
        self.id = script_help.get_reservation_context_details().id
        self.suffix = 'westeurope.cloudapp.azure.com'

    def get_cloud_provider(self):
        clp = Azurehandler.CloudProvider()
        resource_details = self.session.GetResourceDetails(self.name)
        cloud_provider_details = self.session.GetResourceDetails(resource_details.VmDetails.CloudProviderFullName)
        clp.azure_subscription_id = \
            [attr.Value for attr in cloud_provider_details.ResourceAttributes if attr.Name == 'Azure Subscription ID'][0]
        clp.azure_tenant = \
            [attr.Value for attr in cloud_provider_details.ResourceAttributes if attr.Name == 'Azure Tenant ID'][0]
        clp.azure_application_key = \
            self.session.DecryptPassword(
                [attr.Value for attr in cloud_provider_details.ResourceAttributes if attr.Name == 'Azure Application Key'][
                    0]).Value
        clp.azure_application_id = \
            [attr.Value for attr in cloud_provider_details.ResourceAttributes if attr.Name == 'Azure Application ID'][0]
        self.clp = clp

    def execute(self):
        az = Azurehandler.AzureClientsManager(self.clp)
        az.connect_to_azure(self.clp)
        dns_name = self.name[0:6]+ '-' + self.name[-8:]
        az.set_dns_label_on_public_ip(
            resource_group=self.id,
            vm_name=self.name,
            new_domain_name=dns_name,
            fqdn_suffix=self.suffix
        )

    def set_dns_attribute(self):
        az = Azurehandler.AzureClientsManager(self.clp)
        az.connect_to_azure(self.clp)
        dns_name = az.get_dns_label_on_public_ip(self.id, self.name)
        self.session.SetAttributeValue(
            resourceFullPath=self.name,
            attributeName='DNS web address',
            attributeValue=dns_name
        )