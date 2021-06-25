import oci
import argparse
import os

parser = argparse.ArgumentParser();
parser.add_argument("--region", action="store", help="Region containing ocids")
parser.add_argument("ocids", nargs="+", help="Integration Instance OCIDs")
args = parser.parse_args();

# Create a default config using DEFAULT profile in default location
# Refer to
# https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm#SDK_and_CLI_Configuration_File
# for more info
# Change region if provided as an argument
config = oci.config.from_file()
if args.region is not None :
  config["region"] = args.region
elif "region" not in config :
  config["region"] = os.environ["OCI_REGION"]


# Initialize service client with default config file
integration_client = oci.integration.IntegrationInstanceClient(config)
identity_client = oci.identity.IdentityClient(config)

print("Region OCID Display_Name Lifecycle_State State_Message Compartment")
for ocid in args.ocids :
  # Send the request to service, some parameters are not required, see API
  # doc for more info
  try :
    ii = integration_client.get_integration_instance(integration_instance_id=ocid).data
    print("{} {} {} {} {} [{}]".format(config["region"], ocid, ii.display_name, ii.lifecycle_state, ii.state_message, identity_client.get_compartment(ii.compartment_id).data.name))
  except oci.exceptions.ServiceError as se :
     print("Error {} {} {} {} {}".format(config["region"], ocid, se.status, se.code, se.message))
