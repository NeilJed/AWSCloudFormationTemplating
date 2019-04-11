import argparse, jinja2, os
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


def main():
    
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('template', action='store', help='Input template file in Python or Jinja2 format')
    parser.add_argument("outfile", help="Output JSON config file")
    parser.add_argument("environment", action='store', help="Name of the custom environment name used in the config")
    args = parser.parse_args()
    
    # load up some local vars
    template_file = args.template
    outfile = args.outfile
    conf_json = None

    print(f'AWS CloudFront Templating Example - Neil "Jed" Jedrzjewski')
    print(f'----------------------------------------------------')
    print(f'Template File: {template_file}')
    print(f'Writing Config: {outfile}')
    print(f'Environment: {args.environment}')

    # set-up our custom config parameters. Would probaly pull this from a JSON file but as this example
    # only has one parameter we're just going to set the dictionary quickly.
    config_data  = {'environment':args.environment}

    if not os.path.isfile(template_file):
        raise FileNotFoundError('Template file not found')

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
        print(f'Writing Configuration...')

        with open('output.json', 'w') as fh:
            fh.write(conf_json)
        
        print(f'Done...')
    
    except IOError:
         raise Exception( "Could not write to output file" )
        
# ---------------------------------------------------------
if __name__ == "__main__":
    main()