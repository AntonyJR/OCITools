import oci

config = oci.config.from_file()
identity_client = oci.identity.IdentityClient(config)
regions = identity_client.list_region_subscriptions(config["tenancy"]).data
compartments = identity_client.list_compartments(compartment_id=config["tenancy"], limit=1000, compartment_id_in_subtree=True, lifecycle_state="ACTIVE").data
compartments.append(identity_client.get_compartment(compartment_id=config["tenancy"]).data)

out_format = "{:14} {:20} {:105} {:40} {:15} {:34} {}"
print(out_format.format("Region", "Resource_Type", "OCID", "Display_Name", "Lifecycle_State", "Compartment", "Creator"))
for region in regions :
  config["region"] = region.region_name

  search_client = oci.resource_search.ResourceSearchClient(config)

  search_details = oci.resource_search.models.StructuredSearchDetails(query='query all resources where lifecycleState != "Deleted" sorted by identifier  asc')
  resources = oci.pagination.list_call_get_all_results(search_client.search_resources, search_details=search_details, limit=1000).data
  for resource in resources :
    try :
      compartment_name = next((compartment.name for compartment in compartments if compartment.id == resource.compartment_id), "**Not_Known**")
      creator = resource.defined_tags["Oracle-Tags"]["CreatedBy"] \
                if hasattr(resource, "defined_tags") and "Oracle-Tags" in resource.defined_tags and "CreatedBy" in resource.defined_tags["Oracle-Tags"] \
                else "**Not_Known**"
      lifecycle_state = resource.lifecycle_state if resource.lifecycle_state is not None else "N/A"
      if resource.resource_type not in ["User", "Group", "Policy", "Compartment", "TagNamespace", "TagDefault", "WaasCertificate", "WaasPolicy", "IdentityProvider"] :
        print(out_format.format(config["region"], resource.resource_type, resource.identifier, '"'+resource.display_name+'"', lifecycle_state, compartment_name, creator))
    except Exception as e :
      print(resource)
      print(e)
