import xml.etree.ElementTree as ET
import copy
import files
import json
import difflib
from colorama import init, Fore, Style
from settings import start_merge, break_line, success, wait_for_it


################################################################################################################################
                                                # === JSON HELPERS === #
################################################################################################################################

def merge_widgets(widgets1, widgets2):
    seen_names = {w.get("name", json.dumps(w, sort_keys=True)): w for w in widgets1}
    for w in widgets2:
        key = w.get("name", json.dumps(w, sort_keys=True))
        if key not in seen_names:
            widgets1.append(w)
            seen_names[key] = w
    #print(f"➕ Merged widgets {widgets1} and {widgets2}")
    return widgets1

def merge_by_label(list1, list2):
    seen_labels = {item.get("label"): item for item in list1 if "label" in item}
    for item in list2:
        label = item.get("label")
        if label and label in seen_labels:
            # Merge widgets inside matching pages
            existing_widgets = seen_labels[label].get("widgets", [])
            new_widgets = item.get("widgets", [])
            seen_labels[label]["widgets"] = merge_widgets(existing_widgets, new_widgets)
        elif label:
            list1.append(item)
            seen_labels[label] = item
    #print(f"➕ Merged labels {new_widgets}")
    return list1

def merge_gridlayouts(layouts1, layouts2):
    seen_names = {l.get("name"): l for l in layouts1 if "name" in l}
    for layout in layouts2:
        name = layout.get("name")
        if name and name in seen_names:
            # Merge pages in matching layouts
            existing_pages = seen_names[name].get("pages", [])
            new_pages = layout.get("pages", [])
            seen_names[name]["pages"] = merge_by_label(existing_pages, new_pages)
        elif name:
            layouts1.append(layout)
            seen_names[name] = layout
    return layouts1


def merge_generic_list(list1, list2):
    seen = {json.dumps(item, sort_keys=True): item for item in list1}
    for item in list2:
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            list1.append(item)
            seen[key] = item
        #print(f"➕ Added idems to the list {list1}")
    return list1

init(autoreset=True)


def show_query_diff(v1_query, v2_query):
    diff = difflib.unified_diff(
        v1_query.splitlines(),
        v2_query.splitlines(),
        fromfile="V1",
        tofile="V2",
        lineterm="",
        n=0  # lines of context
    )
    for line in diff:
        if line.startswith("-") and not line.startswith("---"):
            print(Fore.RED + line)
        elif line.startswith("+") and not line.startswith("+++"):
            print(Fore.GREEN + line)
        elif line.startswith("@@"):
            print(Fore.CYAN + line)
        else:
            print(Style.RESET_ALL + line)

def handle_difference(key, v1_val, v2_val, context="", target_dict=None):
    if v1_val != v2_val:
        if key == "query" and isinstance(v1_val, str) and isinstance(v2_val, str):
            print(f"\n🔍 Mismatch in query – [{context}]:")
            show_query_diff(v1_val, v2_val)
            print("-" * 60 + "\n")
            print(f"Pick a version to save in {files.name}?\n")
            print("1. V1")
            print("2. V2")
            print("3. Original")

            choice = input("\nChoose and press enter. \n").strip()

            if target_dict is not None and context:
                if choice == "1":
                    target_dict[context][key] = v1_val
                    print("✅ Saved version V1.")
                    break_line()
                elif choice == "2":
                    target_dict[context][key] = v2_val
                    print("✅ Saved version V2.")
                    break_line()
                else:
                    print("⏭ Ignored change.")
                    break_line()



            
################################################################################################################################
                                                # === JSON MERGE === #
################################################################################################################################


def merge_dicts(dict1, dict2):
    for key, value2 in dict2.items():
        if key in dict1:
            value1 = dict1[key]

            if isinstance(value1, dict) and isinstance(value2, dict):
                if key == "steps":
                    for step_key, step_val in value2.items():
                        if step_key not in dict1[key]:
                            dict1[key][step_key] = step_val
                        else:
                            v1_step = dict1[key][step_key]
                            v2_step = step_val
                            all_keys = set(v1_step.keys()).union(v2_step.keys())
                            for k in all_keys:
                                v1_val = v1_step.get(k, "<none>")
                                v2_val = v2_step.get(k, "<none>")
                                handle_difference(k, v1_val, v2_val, context=step_key, target_dict=value1)

                            merge_dicts(v1_step, v2_step)
                else:
                    merge_dicts(value1, value2)

            elif isinstance(value1, list) and isinstance(value2, list):
                if key == "gridLayouts":
                    dict1[key] = merge_gridlayouts(value1, value2)
                elif key == "pages":
                    dict1[key] = merge_by_label(value1, value2)
                elif key == "widgets":
                    dict1[key] = merge_widgets(value1, value2)
                else:
                    dict1[key] = merge_generic_list(value1, value2)

            
        else:
            dict1[key] = value2

def run_jsonmerge():
    # Loading JSON files
    with open(files.json1, "r", encoding="utf-8") as f:
        data1 = json.load(f)

    with open(files.json2, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    # Merging JSON files
    merge_dicts(data1, data2)

    # Saving the output file
    with open(files.output_json, "w", encoding="utf-8") as f:
        json.dump(data1, f, indent=4, ensure_ascii=False)

    print(f"✅ Merged file was saved as: {files.name} JSON")
    wait_for_it()
    break_line()
    

################################################################################################################################
                                                # === XML HELPERS === #
################################################################################################################################


def remove_namespaces(elem):
# Removes spaces in the tag names in the XML file
    for el in elem.iter():
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]

def elements_equal(e1, e2):
# Compares tags, attributes, text, and children (not reccurently)
    if e1 is None or e2 is None:
        return False
    if e1.tag != e2.tag or e1.attrib != e2.attrib:
        return False
    if (e1.text or '').strip() != (e2.text or '').strip():
        return False
    if len(e1) != len(e2):
        return False
    return all(
        c1.tag == c2.tag and (c1.text or '').strip() == (c2.text or '').strip()
        for c1, c2 in zip(e1, e2)
    )

def find_matching_element(root, target):
# Finds element that fits the tree based on tags and attributes
    for elem in root:
        if elem.tag == target.tag and elem.attrib == target.attrib:
            return elem
    return None

def merge_if_different(base_root, updates_root, compare_root=None):
# Adds/updates elements from updates_root to base_root if they differ from compare_root
    for elem in updates_root:
        existing = find_matching_element(base_root, elem)
        compare_to = find_matching_element(compare_root, elem) if compare_root is not None else None

        if existing is None:
            base_root.append(copy.deepcopy(elem))
        elif not elements_equal(existing, elem):
            if compare_to is None or not elements_equal(compare_to, elem):
                base_root.remove(existing)
                base_root.append(copy.deepcopy(elem))
                

def deduplicate_elements_by_tag_and_field(root, tag):
    seen_fields = set()
    for elem in list(root.findall(tag)):
        field_elem = elem.find('field')
        if field_elem is not None and field_elem.text in seen_fields:
            root.remove(elem)
        else:
            if field_elem is None:
                seen_fields.append(field_elem.text)

def ensure_wave_visualization_name(original_root, new_root):
# Set the <waveVisualization> == Original
    original_wave = original_root.find("waveVisualization") 
    if original_wave is None:
        original_wave = ET.SubElement(original_root, "waveVisualization")
    original_wave.text = files.waveName  # If no tag - we add it
        
    new_wave = new_root.find("waveVisualization")
    if new_wave is None:
        new_wave = (ET.SubElement(new_root, "waveVisualization"))
    new_wave.text = original_wave.text
    
    if new_wave is not None: 
        new_wave = files.waveName
    new_wave = original_wave.text

def ensure_meta_name(original_meta, new_meta):
# Set the <masterLabel> == Original
    original_label = original_meta.find("masterLabel") 
    if original_label is None:
        original_label = ET.SubElement(original_meta, "masterLabel")
    original_label.text = files.waveName  # If no tag - we add it
        
    new_wave = new_meta.find("masterLabel")
    if new_wave is None:
        new_wave = (ET.SubElement(new_meta, "masterLabel"))
    new_wave.text = original_label.text
    
    if new_wave is not None: 
        new_wave = files.waveName
    new_wave = original_label.text

    original_app = original_meta.find("application") 
    if original_app is None:
        original_app = ET.SubElement(original_meta, "application")
    original_app.text = files.app  # If no tag - we add it
        
    new_wave = new_meta.find("application")
    if new_wave is None:
        new_wave = (ET.SubElement(new_meta, "application"))
    new_wave.text = original_app.text
    
    if new_wave is not None: 
        new_wave = files.waveName
    new_wave = original_app.text

def sort_children_alphabetically(parent):
# Sorts children alphabetically by tag
    parent[:] = sorted(parent, key=lambda e: e.tag) 

def ensure_all_fields_from_steps_exist(json_data, xml_output_root, xml1_root, xml2_root, xml_original_root):
    step_names = set(json_data.get("steps", {}).keys())

    def get_fields_by_type(root, tag_type):
    # Returns dict {step_name: element} for tag (dimensions/measures)
        result = {}
        for elem in root.findall(tag_type):
            field_elem = elem.find("field")
            if field_elem is not None and field_elem.text:
                step_prefix = field_elem.text.split(".")[0]
                result[step_prefix] = elem
        return result
    
    def get_element_by_step(root, tag_type, step_name):
        for elem in root.findall(tag_type):
            field_elem = elem.find("field")
            if field_elem is not None and field_elem.text.startswith(step_name + "."):
                return elem
                
        return None

    # 1. Get existing fields from output_xml
    existing_dimensions = get_fields_by_type(xml_output_root, "dimensions")
    existing_measures = get_fields_by_type(xml_output_root, "measures")

    # 2. Get Original fields for comparison
    original_dimensions = get_fields_by_type(xml_original_root, "dimensions")
    original_measures = get_fields_by_type(xml_original_root, "measures")

    # 3. Get source fields from V1 and V2
    def find_in_sources(step, tag_type):
        for src in [xml1_root, xml2_root]:
            for elem in src.findall(tag_type):
                field_elem = elem.find("field")
                if field_elem is not None and field_elem.text.startswith(step + "."):
                    return copy.deepcopy(elem)
        return None

    for step in step_names:
        has_dim = step in existing_dimensions
        has_mea = step in existing_measures

        orig_dim = original_dimensions.get(step)
        orig_mea = original_measures.get(step)

        # Missing dimentions → add if exists only in sources and differs from original
        if not has_dim:
            dim_elem = find_in_sources(step, "dimensions")
            if dim_elem is not None and not elements_equal(dim_elem, orig_dim):
                xml_output_root.append(dim_elem)
                print(f"➕ Added missing <dimensions> for <field>{step}</field>")

        # Missing measures → add if exists only in sources and differs from original
        if not has_mea:
            mea_elem = find_in_sources(step, "measures")
            if mea_elem is not None and not elements_equal(mea_elem, orig_mea):
                xml_output_root.append(mea_elem)
                print(f"➕ Added missing <measures> for <field>{step}</field>")

        # If we have dimensions but no measures — check V1
        if has_dim and not has_mea:
            candidate = get_element_by_step(xml1_root, "measures", step)
            if candidate is not None:
                xml_output_root.append(candidate)
                print(f"➕ Added missing <measures> for <field>{step}</field>")
                break_line()

        if has_mea and not has_dim:
            candidate = get_element_by_step(xml1_root, "dimensions", step)
            if candidate is not None:
                xml_output_root.append(candidate)
                print(f"➕ Added missing <dimensions> for <field>{step}</field>")
                break_line()


#########################################################################################################################################
                                            # === MAIN FUNCTION === #
#########################################################################################################################################


def main():
    start_merge()

    # Running JSON Merge
    run_jsonmerge() 

    start_merge() 

    # Starting XML Merge Process

    # === 1. Upload and clean === #
    
    # Upload dashboard meta file
    tree_meta = ET.parse(files.meta)
    root_meta = tree_meta.getroot()
    remove_namespaces(root_meta)

    # Upload original dashboard file
    tree_orig = ET.parse(files.original_xml)
    root_orig = tree_orig.getroot()
    remove_namespaces(root_orig)

    # Upload Dev 1 dashboard file
    tree_v1 = ET.parse(files.xml1)
    root_v1 = tree_v1.getroot()
    remove_namespaces(root_v1)

    # Upload Dev 2 dashboard file
    tree_v2 = ET.parse(files.xml2)
    root_v2 = tree_v2.getroot()
    remove_namespaces(root_v2)


    # === 2. Create New dashbord and the copy of the Original meta file === #
    root_new = copy.deepcopy(root_orig)
    root_meta_new = copy.deepcopy(root_meta)

    # === 3. Add/update assets from V1 if is different than New  === #
    merge_if_different(root_new, root_v1, compare_root=root_new)

    # === 4. Add/update assets from V2 if is different than Original === #
    merge_if_different(root_new, root_v2, compare_root=root_orig)

    # === 5. Ensure <waveVizualization> is exactly the same as in Original dashboard === #
    ensure_wave_visualization_name(root_orig, root_new)

    # === 6. Ensure <masterLabel> in meta is exactly the same as in Original dashboard === #
    ensure_meta_name(root_meta, root_meta_new)

    # === 7. Save the result === #
    new_tree = ET.ElementTree(root_new)
    new_meta = ET.ElementTree(root_meta_new)
    
    # === 8. Unduplicate dimensions, measures, etc. === #
    for tag in ['dimensions', 'measures', 'field', 'formatValue']:
        deduplicate_elements_by_tag_and_field(root_new, tag)

    # === 9. JSON merge finished above, ensure XML has fields for all steps === #
    with open(files.output_json, "r", encoding="utf-8") as jf:
        merged_json = json.load(jf)

    ensure_all_fields_from_steps_exist(merged_json, root_new, root_v1, root_v2, root_orig)

    # === 10. Set sorting of children so dimensions go first, then measures, and visualization last === #
    sort_children_alphabetically(root_new)

    # === 11. Save output files === #
    new_tree.write(files.output_xml, encoding="utf-8", xml_declaration=True)
    new_meta.write(files.meta_new, encoding="utf-8", xml_declaration=True)
    
    
    
    print(f"✅ Merged file was saved as: {files.name} XML")
    wait_for_it()
    break_line()

    success()

# === RUN MAIN FUNCTION === #

if __name__ == "__main__":
    main()