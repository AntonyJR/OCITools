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

stop_responses = []
for ocid in args.ocids :
  # Send the request to service, some parameters are not required, see API
  # doc for more info
  try :
    stop_responses.append((config["region"], ocid, integration_client.delete_integration_instance(integration_instance_id=ocid)))
  except oci.exceptions.ServiceError as se :
     print("Error {} {} {} {} {}".format(config["region"], ocid, se.status, se.code, se.message))

print("Region OCID Status")
for response in stop_responses :
  print("{} {} {}".format(response[0], response[1], response[2].status))
