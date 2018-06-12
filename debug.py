import cloudshell.helpers.scripts.cloudshell_dev_helpers as dev_help
import execute

vm_name = 'azurevm-560e7e5c'
# suffix = 'westeurope.cloudapp.azure.com'
resource_group = 'c51fa7da-37ba-49d2-81e1-059cbbf7d4ac'

username = 'admin'
password = 'admin'
server = 'localhost'
domain = 'Global'

dev_help.attach_to_cloudshell_as(
    user=username,
    password=password,
    domain=domain,
    server_address=server,
    resource_name=vm_name,
    reservation_id=resource_group

)
dns_script = execute.dns_altering_script()
dns_script.get_cloud_provider()
dns_script.execute()
dns_script.set_dns_attribute()
pass

