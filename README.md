# 1	Business Approach

1.1	Introduction

Due to the high number of changes applied by different users, we need to create copies of the original dashboard to implement the changes.
As easy as it is to create a copy of the dashboard, the issue arises when we want to unify them again.
Why create copies of the dashboards in the first place?
•	It's easier for testers to check if the implementation works on the original dashboard
•	It ensures the other developers do not overwrite each other’s changes accidentally
•	It creates multiple backups of the dashboard in case of deleting it by accident

1.2	Logical Approach

The current approach is designed to work on 2 test dashboards that were created from the same original dashboard.

<img width="885" height="428" alt="image" src="https://github.com/user-attachments/assets/a7334850-462b-49b7-b202-581143782c59" />

The logic is as follows:
1.	Create a copy of the original (OG) dashboard as a new one (NEW)
2.	Iterate NEW by the V1 and update all assets that are different
3.	If assets in V1 are not present in NEW add them to the output
4.	Iterate OG by the V2 to identify everything that is different/nonexistent in OG dashboard
5.	Add all that differs between OG and V2 to the NEW dashboard
6.	The OG is not being updated or overwritten in any way

# 2	Code

2.1	Prerequisites

For the developer to be able to merge the test dashboards they need the following:
•	Visual Studio Code
•	Python 3.12 or higher
•	Microsoft Visual C++ 14.0 or higher
•	Node.js
•	Salesforce CLI
For Python you need the basing understanding of the dictionaries, tuples, and flows.
The entire functionality needs the following files:
•	files.py
•	merge.py
•	settings.py
Let's walk through them step by step.

2.2	First script - settings.py

This is the script that handles the initial settings, decorators for the main script, and most importantly the dashboards we want to merge with.

2.3	Second script - files.py

This script is the source of all attributes used in the main code. However, it is not to be changed once you ensure the source URLs are correct.

2.4	Main script - merge.py

This is where magic happens. The step-by-step explanation of the code is in the separate documentation at the bottom of the documentation. 

# 3 Code Explanation

xml.etree.ElementTree	- This library allows python to read, analyze, and transform xml files 	We use "as ET" to shorten the name for de clarity
copy	- As name states	
json	- This library allows python to read, analyze, and transform JSON files 	
difflib	- Checks for differences	
colorama	- Adds color scheme to differences	
files	- Import objects from files.py	
settings	- Import objects from settings.py	

3.2	JSON Merge

To understand the code, we need to understand how the JSON file is built. Salesforce Dashboards always have the same structure:

{
    "gridlayouts": [
        {
            "name": "Default",
            "pages": [
                {
                    "label": "labelName",
                    "name": "uniqueLabelID",
                    "widgets": [
                    {
                            "name": "filter_BrandRange",
                            "widgetStyle": {}
                        },
            ]
            }
    ]
    }
],
    "steps": {
        "query_names": {
        }
    }
}


Let's start with the helper functions:

merge_widgets	- It merges widgets by unique names and appends if missing	(json)
merge_by_label	- It merges the widgets inside matching pages by checking unique names and labels		(uses merge_by_widgets helper)
merge_gridlayout	- Checks JSON grid layout by unique name and label to avoid duplicates		(uses merge_by_label helper)
merge_generic_list	- Check the JSON files. If any item is not in the other, it adds it to the output.	(json)
show_query_diff	- It handles the coloring of the differences between V1 and V2	(difflib, colorama)
handle_difference	- It is an interactive function that checks if the queries in V1 and V2 differ. If there's a mismatch, we can choose the preferred version.	(files)	

Then we have the main function, that is the helpers above. Additionally, it uses isinstance() function, which returns true is the object is of the specified type.

merge_dicts	- Uses all the helpers above to merge the JSON files. It allows the user to define which version of the mismatching queries to use.		
run_jsonmerge	- Runs the function and saves the output in the file defined in the settings.py	json

3.3	XML Merge

remove_namespaces	- Removes spaces in the names of the XML tags		
elements_equal	- Compares tags, attributes, text, and children in XML		
find_matching_element -	Finds element that fits the tree-based on tags and attributes		
merge_if_different	- Appends elements from V1 or V1 if they are different than original	copy	
deduplicate_elements_by_tag_and_field	- Removes duplicates of tags in fields		
ensure_wave_visualization_name	- Ensures the name of wave Visualisation taken from settings.py 		
ensure_meta_name	- Sets masterLabel and application defined in settings.py		
sort_children_alphabetically	- Sorts XML children tag alphabetically		
ensure_all_fields_from_steps_exist	- Ensures all steps in the output JSON have the XML fields based on "query_name"		
get_fields_by_type	- Returns element for tag in dimensions/measures.		
get_element_by_step	- Returns element by step name that starts after "."		
find_in_sources	- Finds field in measures and dimensions to append missing element.		

3.4	Main Function

Now we put everything together and run all the functions in proper order:
1.	run_jsonmerge
2.	remove_namespaces
3.	merge_if_different
4.	ensure_wave_visualisation_name
5.	ensure_meta_name
6.	deduplicate_elements_by_tag_and_field
7.	ensure all_fields)from_steps_exist
8.	sort_children_alphabetically
9.	save


