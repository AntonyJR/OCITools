import oci

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
regions = identity_client.list_region_subscriptions(config["tenancy"]).data
compartments = identity_client.list_compartments(compartment_id=config["tenancy"], limit=1000, compartment_id_in_subtree=True, lifecycle_state="ACTIVE").data

out_format = "{:14} {:105} {:20} {:15} {:20}"
print(out_format.format("Region","OCID","Display_Name","Lifecycle_State","Compartment"))
for region in regions :
  config["region"] = region.region_name

  integration_client = oci.integration.IntegrationInstanceClient(config)
  search_client = oci.resource_search.ResourceSearchClient(config)

  search_details = oci.resource_search.models.StructuredSearchDetails(query='query IntegrationInstance resources where lifecycleState != "Deleted"')
  instances = search_client.search_resources(search_details=search_details, limit=1000).data.items
  for integration in instances :
    compartment_name = next((compartment.name for compartment in compartments if compartment.id == integration.compartment_id), None)
    print(out_format.format(config["region"], integration.identifier, '"'+integration.display_name+'"', integration.lifecycle_state,
          compartment_name if compartment_name is not None else "NO_COMPARTMENT"))
