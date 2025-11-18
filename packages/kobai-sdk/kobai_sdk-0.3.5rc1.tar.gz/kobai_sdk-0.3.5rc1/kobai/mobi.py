import requests
import urllib.parse
import json
import base64
from random import randrange
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .mobi_config import MobiSettings

def special_request(api_url, mobi_config, **kwargs):
    if mobi_config.use_cookies: 
        response = requests.get(api_url, cookies={'mobi_web_token':mobi_config.cookies}, **kwargs)
    else: 
        response = requests.get(api_url, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password), **kwargs)
    return(response) 
    
def special_post(api_url, mobi_config, **kwargs):
    if mobi_config.use_cookies: 
        response = requests.post(api_url, cookies={'mobi_web_token':mobi_config.cookies}, **kwargs)
    else: 
        response = requests.post(api_url, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password), **kwargs)
    return(response) 

def special_put(api_url, mobi_config, **kwargs):
    if mobi_config.use_cookies: 
        response = requests.put(api_url, cookies={'mobi_web_token':mobi_config.cookies}, **kwargs)
    else: 
        response = requests.put(api_url, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password), **kwargs)
    return(response) 
    
def special_delete(api_url, mobi_config, **kwargs):
    if mobi_config.use_cookies: 
        response = requests.delete(api_url, cookies={'mobi_web_token':mobi_config.cookies}, **kwargs)
    else: 
        response = requests.delete(api_url, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password), **kwargs)
    return(response) 

##############################
# Mobi Pull
##############################

def get_tenant(top_level_ontology_name, mobi_config: MobiSettings):
    #Find Ontology Record

    ont_record_id = _get_ont_record_by_name(top_level_ontology_name, mobi_config)
    print("Mobi Ontology Record ID:", ont_record_id)
    #Get Deprecated Nodes
    
    api_url = mobi_config.mobi_api_url + "/ontologies/" + urllib.parse.quote_plus(ont_record_id) + "/property-ranges"
    #response = requests.get(api_url, verify=False, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    prop_ranges = response.json()["propertyToRanges"]


    api_url = mobi_config.mobi_api_url + "/ontologies/" + urllib.parse.quote_plus(ont_record_id) + "/ontology-stuff"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    ########################
    # Deprecated Classes
    ########################

    deprecated = []

    try:
        resp_data = response.json()["iriList"]["deprecatedIris"]
    except requests.exceptions.JSONDecodeError:
        resp_data = []

    for iri in resp_data:
        deprecated.append(iri)

    try:
        resp_data = response.json()["importedIRIs"]
    except requests.exceptions.JSONDecodeError:
        resp_data = []

    for o in resp_data:
        for iri in o["deprecatedIris"]:
            deprecated.append(iri)

    ########################
    # Properties
    ########################

    data_properties = []
    object_properties = []

    for p in response.json()["iriList"]["dataProperties"]:
        data_properties.append(p)

    for p in response.json()["iriList"]["objectProperties"]:
        object_properties.append(p)

    for o in response.json()["importedIRIs"]:
        for p in o["dataProperties"]:
            data_properties.append(p)

    for o in response.json()["importedIRIs"]:
        for p in o["objectProperties"]:
            object_properties.append(p)

    all_properties = data_properties + object_properties

    ########################
    # Classes and Domains
    ########################

    domains = {}
    concepts = {}
    prop_domains = {}

    for ont in _get_classes_by_ont(ont_record_id, mobi_config):
        for c in ont["classes"]:
            if c not in deprecated:
                d = _domain_from_uri(c, mobi_config)
                c_lu = _fix_uri(c, "concept", mobi_config)
            
                if d not in domains:
                    domains[d] = {"name": d, "concepts": [], "color": ""}

                #Add Leaf Ontology Concepts
                loc = _parent_uri_from_uri(c)
                loc_lu = _fix_uri(loc, "concept", mobi_config)
                if loc_lu not in concepts:
                    name = _name_from_uri(loc, mobi_config)
                    concepts[loc_lu] = {"label": name, "domainName": d, "name": name, "uri": loc_lu, "properties": [], "relations": [], "inheritedConcepts": []}

                #Add Class Concepts
                name = _name_from_uri(c, mobi_config)
                concepts[c_lu] = {"label": name, "domainName": d, "name": name, "uri": c_lu, "properties": [], "relations": [], "inheritedConcepts": [loc_lu]}

    try:
        resp_data = response.json()["classToAssociatedProperties"]
    except requests.exceptions.JSONDecodeError:
        resp_data = {}

    class_to_props = resp_data

    props_with_domain = []
    for c in class_to_props:
        for p in class_to_props[c]:
            props_with_domain.append(p)

    #for p in resp_data:
    for p in all_properties:
        if p not in props_with_domain:
            leaf_ont_concept = _parent_uri_from_uri(p)
            if leaf_ont_concept not in class_to_props:
                class_to_props[leaf_ont_concept] = []
            class_to_props[leaf_ont_concept].append(p)
    
    for c in class_to_props:
        if c not in deprecated:
            for p in class_to_props[c]:
                #loc_lu = _fix_uri(c, "concept", mobi_config)

                if p in prop_ranges:
                    range = prop_ranges[p][0]
                    if range not in ["http://www.w3.org/2001/XMLSchema#string", "http://www.w3.org/2001/XMLSchema#number", "http://www.w3.org/2001/XMLSchema#boolean", "http://www.w3.org/2001/XMLSchema#dateTime"]:
                        range = "http://www.w3.org/2001/XMLSchema#string"
                else:
                    range = "http://www.w3.org/2001/XMLSchema#string"
                
                #range_lu = _fix_uri(prop_ranges[p][0], "concept", mobi_config)

                #if p in prop_domains:
                    #for dc in prop_domains[p]:
                #cp =  dc + "/" + _label_from_uri(p)
                cp =  c + "/" + _label_from_uri(p)
                #dc_lu = _fix_uri(dc, "concept", mobi_config)
                dc_lu = _fix_uri(c, "concept", mobi_config)

                #deal with case where literal and relation have same name
                relation_labels = []
                for p in object_properties:
                    if p in prop_ranges:
                        relation_labels.append(_label_from_uri(p))

                if p in data_properties:
                    prop = {"label": _label_from_uri(p), "uri": _fix_uri(cp, "prop", mobi_config), "conceptUri": dc_lu, "propTypeUri": range, "dataClassTags": []}
                    if dc_lu in concepts:
                        if prop not in concepts[dc_lu]["properties"]:
                            if prop["label"] not in relation_labels:
                                concepts[dc_lu]["properties"].append(prop)
                if p in object_properties:
                    if p in prop_ranges:
                        range_lu = _fix_uri(prop_ranges[p][0], "concept", mobi_config)
                        prop = {"label": _label_from_uri(p), "uri": _fix_uri(cp, "prop", mobi_config), "conceptUri": dc_lu, "relationTypeUri": range_lu, "dataClassTags": []}
                        if dc_lu in concepts:
                            if range_lu in concepts:
                                if prop not in concepts[dc_lu]["relations"]:
                                    concepts[dc_lu]["relations"].append(prop)
                    else:
                        print("PROPERTY RANGE MISSING", p)

    try:
        resp_data = response.json()["classHierarchy"]["childMap"]
    except requests.exceptions.JSONDecodeError:
        resp_data = {}                           

    for c in resp_data:
        c_lu = _fix_uri(c, "concept", mobi_config)
        for pc in resp_data[c]:
            pc_lu = _fix_uri(pc, "concept", mobi_config)
            if c not in deprecated:
                if c_lu in concepts:
                    concepts[c_lu]["inheritedConcepts"].append(pc_lu)
                else:
                    print("RELATION TARGET MISSING", c_lu)

    empty_leaf_concepts = []
    for c in concepts:
        if c.split("#")[1][0] == "_":
            if len(concepts[c]["properties"]) == 0 and len(concepts[c]["relations"]) == 0:
                empty_leaf_concepts.append(c)
                for cc in concepts:
                    if c in concepts[cc]["inheritedConcepts"]:
                        concepts[cc]["inheritedConcepts"].remove(c)
            else:
                print("KEEPING LEAF ONTOLOGY", c)
    for c in empty_leaf_concepts:
        print("REMOVING LEAF ONTOLOGY", c)
        del concepts[c]

    tenant = {"solutionId": 0, "model": {"name": "AssetModel", "uri": "http://kobai/" + mobi_config.default_tenant_id + "/AssetModel"}, "tenantId": mobi_config.default_tenant_id, "domains": []}
    tenant_encoded = {"solutionId": 0, "model": {"name": "AssetModel", "uri": "http://kobai/" + mobi_config.default_tenant_id + "/AssetModel"}, "tenantId": mobi_config.default_tenant_id, "domains": []}
    _add_empty_tenant_metadata(tenant)
    _add_empty_tenant_metadata(tenant_encoded)

    di = 0
    for dk, d in domains.items():
        d['id'] = di
        d['color'] = "#" + str(randrange(222222, 888888))
        d_encoded = {}
        d_encoded['id'] = di
        d_encoded['color'] = "#" + str(randrange(222222, 888888))
        d_encoded['name'] = dk

        for _, c in concepts.items():
            if dk == c['domainName']:
                cprime = {"uri": c['uri'], "label": c['label'], "relations": c['relations'], "properties": c['properties'], "inheritedConcepts": c['inheritedConcepts']}
                d['concepts'].append(cprime)
        encodedConcepts = base64.b64encode(json.dumps(d['concepts']).encode('ascii')).decode('ascii')
        d_encoded['concepts'] = encodedConcepts
        tenant['domains'].append(d)
        tenant_encoded['domains'].append(d_encoded)
        di += 1

    return tenant, tenant_encoded

def _get_classes_by_ont(ont_record_id, mobi_config):
    api_url = mobi_config.mobi_api_url + "/ontologies/" + urllib.parse.quote_plus(ont_record_id) + "/imported-classes"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    data = []
    try:
        resp_data = response.json()
    except requests.exceptions.JSONDecodeError:
        resp_data = []

    #for ont in response.json():
    for ont in resp_data:
        record = {}
        record["id"] = _trim_trailing_slash(ont["id"])
        record["classes"] = []
        for c in ont["classes"]:
            record["classes"].append(c)
        data.append(record)

    api_url = mobi_config.mobi_api_url + "/ontologies/" + urllib.parse.quote_plus(ont_record_id) + "/classes"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    try:
        resp_data = response.json()
    except requests.exceptions.JSONDecodeError:
        resp_data = []

    record = {}
    if len(resp_data) == 0:
        return data
    record["id"] = _parent_uri_from_uri(_trim_trailing_slash(response.json()[0]["@id"]))
    record["classes"] = []

    for c in resp_data:
        record["classes"].append(c["@id"])
    data.append(record)

    return data

def _get_ont_record_by_name(name, mobi_config):
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    ont_record_id = ""
    for r in response.json():
        if r["http://purl.org/dc/terms/title"][0]["@value"] == name:
            ont_record_id = r["@id"]
    return ont_record_id

def _get_ont_record_by_url(url, mobi_config):
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    ont_record_id = ""
    for r in response.json():
        for u in r["http://mobi.com/ontologies/ontology-editor#ontologyIRI"]:
            if url == _trim_trailing_slash(u["@id"]):
                ont_record_id = r["@id"]
    return ont_record_id

def _add_empty_tenant_metadata(tenant):
    tenant["dataAccessTags"] = []
    tenant["conceptAccessTags"] = []
    tenant["dataSources"] = []
    tenant["dataSets"] = []
    tenant["collections"] = []
    tenant["visualizations"] = []
    tenant["queries"] = []
    tenant["mappingDefs"] = []
    tenant["dataSourceFileKeys"] = []
    tenant["apiQueryProfiles"] = []
    tenant["collectionVizs"] = []
    tenant["collectionVizOrders"] = []
    tenant["queryDataTags"] = []
    tenant["queryCalcs"] = []
    tenant["dataSourceSettings"] = []
    tenant["publishedAPIs"] = []
    tenant["scenarios"] = []

##############################
# Mobi Replace
##############################

def replace_tenant_to_mobi(kobai_tenant, top_level_ontology, mobi_config: MobiSettings):
    json_ld = _create_jsonld(kobai_tenant, top_level_ontology)
    _post_model(json_ld, top_level_ontology, mobi_config)

def replace_tenant_to_file(kobai_tenant, top_level_ontology):
    return _create_jsonld(kobai_tenant, top_level_ontology)

def _create_jsonld(kobai_tenant, top_level_ontology):
    output_json = []
    uri = kobai_tenant["model"]["uri"]
    uri = uri.replace("AssetModel", top_level_ontology)

    group = {
        "@id": uri,
        "@type": ["http://www.w3.org/2002/07/owl#Ontology"],
        "http://purl.org/dc/terms/description": [{"@value": "This model was exported from Kobai."}],
        "http://purl.org/dc/terms/title": [{"@value": top_level_ontology}]
    }
    output_json.append(group)


    for dom in kobai_tenant["domains"]:
        for con in dom["concepts"]:

            group = {
                "@id": con["uri"].replace("AssetModel", top_level_ontology),
                "@type": ["http://www.w3.org/2002/07/owl#Class"],
                "http://purl.org/dc/terms/title": [{"@value": con["label"]}]
            }
            if len(con["inheritedConcepts"]) > 0:
                group["http://www.w3.org/2000/01/rdf-schema#subClassOf"] = []
                for parent in con["inheritedConcepts"]:
                    group["http://www.w3.org/2000/01/rdf-schema#subClassOf"].append(
                        {"@id": parent.replace("AssetModel", top_level_ontology)}
                    )
            output_json.append(group)

            for prop in con["properties"]:
                group = {
                    "@id": prop["uri"].replace("AssetModel", top_level_ontology),
                    "@type": ["http://www.w3.org/2002/07/owl#DatatypeProperty"],
                    "http://purl.org/dc/terms/title": [{"@value": prop["label"]}],
                    "http://www.w3.org/2000/01/rdf-schema#domain": [{"@id": con["uri"].replace("AssetModel", top_level_ontology)}],
                    "http://www.w3.org/2000/01/rdf-schema#range": [{"@id": prop["propTypeUri"]}]
                }
                output_json.append(group)

            for rel in con["relations"]:
                group = {
                    "@id": rel["uri"].replace("AssetModel", top_level_ontology),
                    "@type": ["http://www.w3.org/2002/07/owl#ObjectProperty"],
                    "http://purl.org/dc/terms/title": [{"@value": rel["label"]}],
                    "http://www.w3.org/2000/01/rdf-schema#domain": [{"@id": con["uri"].replace("AssetModel", top_level_ontology)}],
                    "http://www.w3.org/2000/01/rdf-schema#range": [{"@id": rel["relationTypeUri"].replace("AssetModel", top_level_ontology)}]
                }
                output_json.append(group)
    return output_json

def _post_model(tenant_json, top_level_ontology, mobi_config):

    mp = MultipartEncoder(fields={
            "title": top_level_ontology, 
            "description": "This model was exported from Kobai.",
            "json": json.dumps(tenant_json)
            })
    h = {"Content-type": mp.content_type}

    api_url = mobi_config.mobi_api_url + "/ontologies"
    #response = requests.post(
    response = special_post(
        api_url,
        mobi_config,
        headers = h,
        data = mp,
        verify=False, 
        timeout=5000
        #auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password)
        )
    print("Upload Status", response.status_code)
    if response.status_code != 201:
        print(response.text)

##############################
# Mobi Update
##############################

def update_tenant(kobai_tenant, top_level_ontology_name, mobi_config: MobiSettings):
    record_id = _get_ont_record_by_name(top_level_ontology_name, mobi_config)

    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(record_id) + "/branches"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

    classes = _get_classes_by_ont(record_id, mobi_config)
    ontology_by_class = {}
    for o in classes:
        for c in o["classes"]:
            ontology_by_class[c] = o["id"]

    _, mobi_tenant = get_tenant(top_level_ontology_name, mobi_config)

    change_json = _compare_tenants(kobai_tenant, mobi_tenant, classes, mobi_config)

    #################################
    # Apply changes with Mobi API calls
    #################################

    for o in change_json:
        if not change_json[o]["changed"]:
            continue

        ont_record_id = _get_ont_record_by_url(o, mobi_config)
        if ont_record_id == "":
            continue
        
        branch_id = _get_or_create_branch_by_record(ont_record_id, "kobai_dev", mobi_config)
        master_branch_id = _get_or_create_branch_by_record(ont_record_id, "MASTER", mobi_config)
        
        for change in change_json[o]["class"]:
            _stage_changes([change["mobi"]], ont_record_id, mobi_config)
            _commit_changes("Kobai added class " + change["mobi"]["http://purl.org/dc/terms/title"][0]["@value"], ont_record_id, branch_id, mobi_config)
        for change in change_json[o]["property"]:
            _stage_changes([change["mobi"]], ont_record_id, mobi_config)
            _commit_changes("Kobai added property " + change["mobi"]["http://purl.org/dc/terms/title"][0]["@value"], ont_record_id, branch_id, mobi_config)

        api_url = mobi_config.mobi_api_url + "/merge-requests"
        pd = {"title": "Kobai Change from kobai-dev to master", "recordId": ont_record_id, "sourceBranchId": branch_id, "targetBranchId": master_branch_id, "assignees": ["admin"], "removeSource": "true"}
        response = requests.post(api_url, verify=mobi_config.verify_ssl, timeout=5000, params=pd, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
        #print(response.status_code)

def _compare_tenants(kobai_tenant, mobi_tenant, classes, mobi_config):
    existing_concepts = []
    existing_relations = {}
    existing_properties = {}

    for dom in mobi_tenant["domains"]:
        conText = base64.b64decode(dom['concepts']).decode('UTF-8')
        cons = json.loads(conText)
        for con in cons:
            existing_concepts.append(con["uri"])
            existing_properties[con["uri"]] = []
            for prop in con["properties"]:
                existing_properties[con["uri"]].append(prop["uri"])
            existing_relations[con["uri"]] = []
            for rel in con["relations"]:
                existing_relations[con["uri"]].append(rel["uri"])

    new_concepts = []
    new_relations = {}
    new_properties = {}

    tenantId = kobai_tenant["tenantId"]
    for dom in kobai_tenant["domains"]:
        conText = base64.b64decode(dom['concepts']).decode('UTF-8')
        cons = json.loads(conText)
        for con in cons:
            con_d = con["uri"].replace(tenantId, mobi_config.default_tenant_id)
            if con_d not in existing_concepts:
                print("New Class Detected")
                new_concepts.append(con)
            for prop in con["properties"]:
                prop_d = prop["uri"].replace(tenantId, mobi_config.default_tenant_id)
                if con_d in existing_properties:
                    if prop_d not in existing_properties[con_d]:
                        print("New Prop Detected")
                        if con_d not in new_properties:
                            new_properties[con_d] = []
                        new_properties[con_d].append(prop)
                        print(prop)
                else:
                    print("New Property due to New Concept")
            for rel in con["relations"]:
                rel_d = rel["uri"].replace(tenantId, mobi_config.default_tenant_id)
                if con_d in existing_relations:
                    if rel_d not in existing_relations[con_d]:
                        print("New Rel Detected")
                        if con_d not in new_relations:
                            new_relations[con_d] = []
                            new_relations[con_d].append(rel)
                else:
                    print("New Relation due to New Concept")
    
    change_json = {}
    for o in classes:
        ont_exist = o["id"]
        change_json[ont_exist] = {}
        change_json[ont_exist]["exists"] = True
        change_json[ont_exist]["changed"] = False
        change_json[ont_exist]["class"] = []
        change_json[ont_exist]["property"] = []
        change_json[ont_exist]["relation"] = []

    #################################
    # Identify and capture changes associated to Mobi ontology
    #################################
    for c in new_concepts:
        c_d = c["uri"].replace(tenantId, mobi_config.default_tenant_id)
        ont_sig = c_d.replace("http://kobai/" + mobi_config.default_tenant_id + "/AssetModel/", "").replace("#", "/").replace("_", "/")
        ont_sig = "/".join(ont_sig.split("/")[:-1])
        ont = ""
        for o in classes:
            ont_exist = o["id"]
            if ont_sig == _get_ont_sig_from_ont(ont_exist, len(ont_sig.split("/"))):
                change_json[ont_exist]["class"].append({"type": "new", "kobai": c, "mobi": {}})

    for c in new_properties:
        for p in new_properties[c]:
            ont_sig = _get_ont_sig_from_concept(tenantId, c, mobi_config)
            for o in classes:
                ont_exist = o["id"]
                if ont_sig == _get_ont_sig_from_ont(ont_exist, len(ont_sig.split("/"))):
                    change_json[ont_exist]["property"].append({"type": "new", "kobai": p, "mobi": {}})

    for c in new_relations:
        for r in new_properties[c]:
            ont_sig = _get_ont_sig_from_concept(tenantId, c, mobi_config)
            for o in classes:
                ont_exist = o["id"]
                if ont_sig == _get_ont_sig_from_ont(ont_exist, len(ont_sig.split("/"))):
                    change_json[ont_exist]["relation"].append({"type": "new", "kobai": r, "mobi": {}})      

    #################################
    # Generate Mobi json for every change
    #################################   
    for ont in change_json:
        changed = False
        for i, change in enumerate(change_json[ont]["class"]):
            c = change["kobai"]
            c_json = {}
            c_json["@id"] = ont + "/" + c["label"].split("_")[-1]
            c_json["@type"] = [ "http://www.w3.org/2002/07/owl#Class" ]
            c_json["http://www.w3.org/2000/01/rdf-schema#label"] = [{"@value": c["label"].split("_")[-1]}]
            c_json["http://purl.org/dc/terms/title"] = [{"@value": c["label"].split("_")[-1]}]
            c_json["http://www.w3.org/2000/01/rdf-schema#subClassOf"] = []
            #c_json["http://www.w3.org/2002/07/owl#deprecated"] = [{"@value": "true", "@type": "http://www.w3.org/2001/XMLSchema#boolean"}]
            for pc in c["inheritedConcepts"]:
                c_json["http://www.w3.org/2000/01/rdf-schema#subClassOf"].append(pc)
            change_json[ont]["class"][i]["mobi"] = c_json
            changed = True

        for i, change in enumerate(change_json[ont]["property"]):
            p = change["kobai"]
            p_json = {}
            p_json["@id"] = ont + "/" + p["label"]
            p_json["@type"] = [ "http://www.w3.org/2002/07/owl#Class" ]
            p_json["http://www.w3.org/2000/01/rdf-schema#label"] = [{"@value": p["label"]}]
            p_json["http://purl.org/dc/terms/title"] = [{"@value": p["label"]}]
            p_json["http://www.w3.org/2000/01/rdf-schema#domain"] = [{"@id": ont + "/" + _get_concept_name_from_prop_uri(p["uri"])}]
            p_json["http://www.w3.org/2000/01/rdf-schema#range"] = [{"@id": p["propTypeUri"]}]
            change_json[ont]["property"][i]["mobi"] = p_json
            changed = True

        if changed is True:
            change_json[ont]["changed"] = True

    return change_json

def _stage_changes(changes, ont_record_id, mobi_config):
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(ont_record_id) + "/in-progress-commit"
    #response = requests.delete(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_delete(api_url, mobi_config, verify=False, timeout=5000)

    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(ont_record_id) + "/in-progress-commit"
    m = MultipartEncoder(fields={"additions": json.dumps(changes), "deletions": "[]"})
    h = {"Content-type": m.content_type}
    #response = requests.put(api_url, verify=False, timeout=5000, data=m, headers=h, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_put(api_url, mobi_config, verify=False, timeout=5000, data=m, headers=h)

    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(ont_record_id) + "/in-progress-commit"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)

def _commit_changes(message, ont_record_id, branch_id, mobi_config):
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(ont_record_id) + "/branches/" + urllib.parse.quote_plus(branch_id) + "/commits"
    pd = {"message": message}
    #response = requests.post(api_url, verify=False, timeout=5000, params=pd, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_post(api_url, mobi_config, verify=False, timeout=5000, params=pd)

##############################
# Mobi Branch
##############################

#def jprint(data):
#    json_str = json.dumps(data, indent=4)

def _get_branches_by_record(id, mobi_config):
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(id) + "/branches"
    #response = requests.get(api_url, verify=False, timeout=5000, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    response = special_request(api_url, mobi_config, verify=False, timeout=5000)
    return response.json()

def _get_or_create_branch_by_record(id, name, mobi_config):
    branches = _get_branches_by_record(id, mobi_config)
    for b in branches:
        if b["http://purl.org/dc/terms/title"][0]["@value"] == name:
            return b["@id"]

    commit = ""
    for b in branches:
        if b["http://purl.org/dc/terms/title"][0]["@value"] == "MASTER":
            commit = b["http://mobi.com/ontologies/catalog#head"][0]["@id"]
        
    api_url = mobi_config.mobi_api_url + "/catalogs/" + urllib.parse.quote_plus(mobi_config.catalog_name) + "/records/" + urllib.parse.quote_plus(id) + "/branches"
    pd = {"type": "http://mobi.com/ontologies/catalog#Branch", "title": name, "commitId": commit}
    #requests.post(api_url, verify=False, timeout=5000, params=pd, auth=requests.auth.HTTPBasicAuth(mobi_config.mobi_username, mobi_config.mobi_password))
    special_post(api_url, mobi_config, verify=False, timeout=5000, params=pd)
    
    branches = _get_branches_by_record(id, mobi_config)
    for b in branches:
        if b["http://purl.org/dc/terms/title"][0]["@value"] == name:
            return b["@id"]
    return ""

##############################
# Mobi Parse
##############################
def _get_domain_range(url, mobi_config):
    for d, r in mobi_config.domain_extraction.items():
        if d in url:
            return r
    return {"min": 0, "max": 0}

def _parent_uri_from_uri(uri):
    #return "/".join(uri.split("/")[:-1])
    return "/".join(_uri_split(uri)[:-1])

def _trim_trailing_slash(uri):
    if uri[-1] == "/":
        return uri[:-1]
    else:
        return uri

def _uri_split(uri):
    uri = uri.replace("#", "/")
    return uri.split("/")


################################
# Transform from Kobai to Mobi
################################

def _get_ont_sig_from_concept(tenantId, uri, mobi_config):
    uri = uri.replace(tenantId, mobi_config.default_tenant_id)
    ont_sig = uri.replace("http://kobai/" + mobi_config.default_tenant_id + "/AssetModel/", "").replace("#", "/").replace("_", "/")
    ont_sig = "/".join(ont_sig.split("/")[:-1])
    return ont_sig

def _get_ont_sig_from_ont(uri, length):
    return "/".join(uri.split("/")[-length:])

def _get_concept_name_from_prop_uri(uri):
    return uri.split("#")[0].split("/")[-1]
    #return uri.split("#")[0].split("_")[-1]

################################
# Transform from Mobi to Kobai
################################

def _domain_from_uri(uri, mobi_config):
    #domain = "_".join(uri.split("/")[_get_domain_range(uri, mobi_config)['min']:_get_domain_range(uri, mobi_config)['max']+1])
    domain = "_".join(_uri_split(uri)[_get_domain_range(uri, mobi_config)['min']:_get_domain_range(uri, mobi_config)['max']+1])
    return domain

def _name_from_uri(uri, mobi_config):
    #name = "_".join(uri.split("/")[_get_domain_range(uri, mobi_config)['max']+1:])
    name = "_".join(_uri_split(uri)[_get_domain_range(uri, mobi_config)['max']+1:])
    if name == "":
        #name = "_" + "_".join(uri.split("/")[_get_domain_range(uri, mobi_config)['max']:])
        name = "_" + "_".join(_uri_split(uri)[_get_domain_range(uri, mobi_config)['max']:])
    return name

def _label_from_uri(uri):
    #return uri.split("/")[-1]
    return _uri_split(uri)[-1]

def _fix_uri(uri, type, mobi_config):
    domain = _domain_from_uri(uri, mobi_config)
    name = _name_from_uri(uri, mobi_config)

    top = "/".join(uri.split("/")[0:_get_domain_range(uri, mobi_config)['min']])
    
    if type == "concept":
        uri = domain + "#" + name
    elif type == "prop":
        uri = domain + "/" + "_".join(name.split("_")[0:-1]) + "#" + name.split("_")[-1]

    for d in mobi_config.domain_extraction:
        
        if d in top:
            uri = "http://kobai/" + mobi_config.default_tenant_id + "/AssetModel/" + uri
    
    return uri


