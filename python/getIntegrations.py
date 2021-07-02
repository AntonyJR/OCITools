import re
import oci

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
regions = identity_client.list_region_subscriptions(config["tenancy"]).data
compartments = identity_client.list_compartments(compartment_id=config["tenancy"], limit=1000, compartment_id_in_subtree=True, lifecycle_state="ACTIVE").data
compartments.append(identity_client.get_compartment(compartment_id=config["tenancy"]).data)

out_format =            "{:14} {:40} {:8} {:34} {:34} {:20} {:105}"
print(out_format.format("Region", "Display_Name", "State", "Compartment", "Creator", "Created", "OCID"))
for region in regions :
  config["region"] = region.region_name

  integration_client = oci.integration.IntegrationInstanceClient(config)
  search_client = oci.resource_search.ResourceSearchClient(config)

  search_details = oci.resource_search.models.StructuredSearchDetails(query='query IntegrationInstance resources where lifecycleState != "Deleted"')
  instances = search_client.search_resources(search_details=search_details, limit=1000).data.items
  for integration in instances :
    compartment_name = next((compartment.name for compartment in compartments if compartment.id == integration.compartment_id), "**Not_Known**")
    creator = integration.defined_tags["Oracle-Tags"]["CreatedBy"] \
              if hasattr(integration, "defined_tags") and "Oracle-Tags" in integration.defined_tags and "CreatedBy" in integration.defined_tags["Oracle-Tags"] \
              else "**Not_Known**"
    creator = re.sub(r'^.*?/', '*fed*/', creator)
    print(out_format.format(config["region"], '"'+integration.display_name+'"', integration.lifecycle_state, compartment_name, creator, integration.time_created.strftime('%Y-%m-%dT%H:%M-%Z'), integration.identifier))
