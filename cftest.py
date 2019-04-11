import argparse, os, pprint
import jinja2
import json
import importlib.machinery, importlib.util
from troposphere import Template, Output


def use_jinja_template(template_file: str, config_data: dict) -> str:
    """
    Loads a Jinja2 JSON template and replaces tags with those from the config_data dictionry.

    Returns the transformed template.
    """
    path, file = os.path.split(template_file)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path),
        undefined=jinja2.StrictUndefined
    )

    template = env.get_template(file)
    template_json = template.render(**config_data)

    return template_json


def use_python_template(template_file: str, config_data: dict) -> str:
    """
    Loads our Python template as a module and calls the 'execute_template' function.

    Returns the generated template as a JSON formatted string.
    """
    
    if not os.path.isfile(template_file):
        raise FileNotFoundError('Template file not found')

    # Load our template as a module
    loader = importlib.machinery.SourceFileLoader('PyTemplate', template_file)
    spec = importlib.util.spec_from_loader(loader.name, loader)
    template = importlib.util.module_from_spec(spec)
    loader.exec_module(template)
    
    try:
        template_json = template.execute_template(config_data)
    
    except AttributeError as e:
        if 'execute_template' in str(e):
            raise ImportError('Template is missing the execute_template(config_data) function.')
        else:
            raise e
    
    return template_json


def compare_files(outfile: str, compare_file: str):
    """
    Simple file compare function to see if the generate and compare configs match
    
    This can probably be expanded to produce a diff off the tow using difflib.
    """
    
    try:
        with open(outfile) as out, open(compare_file) as comp:
            
            a = json.load(out)
            b = json.load(comp)

            if a == b:
                print(f'PASS: No differences found')
            else:
                print(f'FAIL: Generated config does not match compare file!')
    
    except Exeption as e:       
        raise e


def load_params(param_file: str) -> dict:
    """Load our JSON parameters into a local storage variable for templates."""

    try:
        with open(param_file, 'r') as fh:
            params = json.load(fh)
    
    except IOError:
         raise Exception( "Could read from parameters file" )

    return params


def main():
    
    # parse command line arguments
    parser = argparse.ArgumentParser(description = 'Constructs a CloudFormation configuration from Python or Jinja templates')
    parser.add_argument('template', action = 'store', help = 'Input template file in Python or Jinja2 format')
    parser.add_argument('outfile', help = 'Output JSON config file')
    parser.add_argument('paramfile', action = 'store', help = 'Name of the JSON file containing customisation parameters')
    parser.add_argument('--c', action = 'store', dest = 'compare_file', help = 'Name of the file to compare the output with for validation', default = None)
    args = parser.parse_args()
    
    # load up some local vars
    template_file = args.template
    out_file = args.outfile
    param_file = args.paramfile
    compare_file = args.compare_file
    conf_json = None
    
    print(f'AWS CloudFront Templating Example - Neil "Jed" Jedrzjewski')
    print(f'----------------------------------------------------\n')
    print(f'Template File: {template_file}')
    print(f'Param File: {param_file}')

    config_data = load_params(param_file)

    if not os.path.isfile(template_file):
        raise FileNotFoundError('Template file not found')

    print(f'Writing Config: {out_file}')

    # check file extension and figure out how we're going to handle the template
    file_extension = os.path.splitext(template_file)[1]

    if file_extension == ".j2":
        print(f'Template Format: Jinja2')
        conf_json = use_jinja_template(template_file, config_data)

    elif file_extension == ".py":
        print(f'Template Format: Python')
        conf_json = use_python_template(template_file, config_data)

    else:
        raise Exception( 'Unrecognised file extension. Only .py and .j2 are supported.' )

    # write the completed template
    try:
        print(f'\nWriting Configuration...')

        with open(out_file, 'w') as fh:
            fh.write(conf_json)
        
        print(f'Done...\n')
    
    except IOError:
         raise Exception( "Could not write to output file" )
        
    # validate our output against a given JSON config.
    if compare_file is not None:
        print(f'Performing Diff against file: {compare_file}')
        compare_files(out_file, compare_file)


# ---------------------------------------------------------
if __name__ == "__main__":
    main()