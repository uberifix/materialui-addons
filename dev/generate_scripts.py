import collections
import json
import pathlib

### Material UI for Penumbra - Development Script Generator
# A script to ease material ui addon creation, automatically generate a nvtt batch script for use with Nvidia Texture Tools
# to dynamically convert hud elements from png to dds and generate penumbra options based on a simple folder layout
###

# Path library and root folder
Path = pathlib.Path
root = Path(__file__).parent
# Working directory, containing png ui elements
elements_dir = root.joinpath("elements")
# Output directory, export of all png elements to dds
output_dir = root.joinpath("output")

# Get all png files in elements directory
elements = elements_dir.glob("**/*.png")

# Dict objects for penumbra json
penumbra_input = collections.defaultdict(set)
penumbra_check = collections.defaultdict(set)

# Iterate through elements and create nvtt batch script
nvtt_batch = open(root.joinpath("conv_elements_to_dds.nvtt"), "w")
for e in elements:
    # Get elements parent directory
    e_dir = e.relative_to(elements_dir).parent
    # Add relative paths for penumbra json
    penumbra_input[e.parent.name].add(e_dir.as_posix())
    penumbra_check[e.parent.name].add(e.parent.parent.parent.name)
    # Create output directories if they dont exist (nvtt script wont run if directories dont exist)
    Path.mkdir(output_dir.joinpath("elements", e_dir), parents = True, exist_ok=True)

    # Get element input path and create a relative output path
    nvtt_in = e.resolve()
    nvtt_out = output_dir.joinpath(e.relative_to(root)).with_suffix(".dds").resolve()
    # Write element to nvtt batch script in bgra8 format
    nvtt_batch.write(f"{nvtt_in} --format bgra8 --output {nvtt_out}\n")
nvtt_batch.close()

# Add default json lines if no options are found
def add_defaults(set, check):
    if "parameter_gauge" not in check: set.add("ui/uld/parameter_gauge")
    if "parameter_gauge2" not in check: set.add("ui/uld/parameter_gauge2")
    if "jobhudsimple_stacka" not in check: set.add("ui/uld/jobhudsimple_stacka")
    if "jobhudsimple_stackb" not in check: set.add("ui/uld/jobhudsimple_stackb")
    if "jobhudmnk0" not in check: set.add("ui/uld/jobhudmnk0")
    if "jobhudsam1" not in check: set.add("ui/uld/jobhudsam1")
    if "jobhudsmn1" not in check: set.add("ui/uld/jobhudsmn1")
        
for key in penumbra_input:
    add_defaults(penumbra_input[key], penumbra_check[key])

# Function to return set as a sorted list for json formatting
def set_as_list(obj):
    if isinstance(obj, set):
        return sorted(obj)
    return obj

# Add generated json object to default penumbra json layout (as a list of options)
penumbra_output = {"penumbra" : [{"name": "Gauges","options": penumbra_input}]}
penumbra_json = json.dumps(penumbra_output, sort_keys=True, indent=4, default=set_as_list)

json = open(root.joinpath("penumbra.json"), "w")
json.write(penumbra_json)
json.close