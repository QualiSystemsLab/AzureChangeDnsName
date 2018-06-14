# AzureChangeDnsName
this adds a script to resources created by Azure, and running the script adds a DNS name for that VM

it expects an attribute "FQDN Suffix" to be added to the app resource.
it will create a DNS name in the following template:

vm resource name.FQDN Suffix attribute value
