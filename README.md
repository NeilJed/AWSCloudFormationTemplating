# AWS CloudFormation Templating Exercise

# About

Small Python Exercise in using Troposphere plus Python to automate [AWS CloudFormation](https://aws.amazon.com/cloudformation) template creation.

The concept is to support "configuration as code" in that templates can be defined as code or files and thus version controlled. The Python script serves as a framework for loading in the template and the customisation data to populate it with and outputing a JSON CloudFront configuration file.

# Exercise features

- Uses JSON Jinja2 (.j2) or Python (.py) templates that use Troposphere.
- Currently uses a single custom parameter (Environment name) for each template but can easily support more.
- Outputs CloudFormation config as JSON.

# Requirements

- Written with Python 3.7
- Requires [Troposphere](https://github.com/cloudtools/troposphere) and [Jinja2](http://jinja.pocoo.org/)

# Usage

```
usage: cftest.py [-h] [--c COMPARE_FILE] template outfile paramfile

Constructs a CloudFormation configuration from Python or Jinja templates

positional arguments:
  template          Input template file in Python or Jinja2 format
  outfile           Output JSON config file
  paramfile         Name of the JSON file containing customisation parameters

optional arguments:
  -h, --help        show this help message and exit
  --c COMPARE_FILE  Name of the file to compare the output with for validation
```

## Example

```
$ cftest.py templates/stack.py output.json params.json --compare json/template_production.json
```

This will use the Python `templates/stack.py` template, write the configuration to `output.json` and load the parameters from the template from `params.json`. It will then do a simple compare of the generated template against `json/template_production.json` to see if they match.


# Templates

## Customisation Data

For templates, data to be used for customisation is held in a simple dictionary as a JSON file. For example:
```
{
  "description": "Service VPC",
  "stackname": "Experimental-VPC",
  "environment": "Experimental"
}
```

## Jinja2

Templates using Jinja2 are just tagged CloudFormation JSON files. The custom_data structure is passed to the renderer to populate the template.

## Python

Templates using Python basically use code to create the template. In the included example we're using Troposphere to build the configuration.

Python templates requre a function called `execute_template(custom_data)` which is called once the template is loaded. This function should then create an instance of your template class and return its output as JSON.

In the example, our template has a single class which performs all the creation steps in the `__init__` function and creates CloudFormation elements using specific functions.



