"""
ViaPlayTestTemplate - Python based template class for creating the coding test config.

Required config_data variables:

- environment (str): Name of the environment this config is targetted for.
"""

from troposphere import Template, Tags, Parameter, Ref, Output
from troposphere import ec2

class ViaPlayTestTemplate(object):
    """
    Self contained Python template class that builds our configuration.

    The __init__function handles all of the calls to build the configuration calling specific functions
    as necessary.

    Specific functions exist that use Troposphere to add specific elements to the configuration template
    taking input parameters and returning the reference where possible. This can be used in further
    function calls.
    """


    def __init__(self, config_data):
        """Initialse class variables and invokes config construction actions"""
        
        # config data we passed in, pull some expected values out.
        self.config_data = config_data
        self.env = config_data['environment']

        # TODO: Add some function to check if all data required by this config exists (hard fail)
        #       or add a fallback to default values (soft fail?)
        
        # Troposphere template that will contain our config
        self.template = Template()
        
        # Config specific data (could be passed as part of the config_data)
        self.deps = []
        self.mdata = {
            'DependsOn': self.deps,
            'Environment':self.env,
            'StackName': '%s-%s' % (self.env, 'VPC')
        }

        # Action steps to build the template.
        self.add_description('Service VPC')
        self.add_metadata(self.mdata)

        self.vpc_ref = self.add_vpc('VPC', self.env, 'ServiceVPC')
        self.igw_ref = self.add_internetgateway('InternetGateway', self.env, 'InternetGateway')
        self.gwa_ref = self.add_vpcgatewayattachement(self.igw_ref, self.vpc_ref, self.env, 'VpcGatewayAttachment')
        
        self.add_output('VPCID', self.vpc_ref)
        self.add_output('InternetGateway', self.igw_ref)

        self.netacl_ref = self.add_networkacl('VpcNetworkAcl', self.vpc_ref, self.env, 'NetworkAcl')
        self.aclin = self.add_inbound_acl("VpcNetworkAclInboundRule", self.netacl_ref)
        self.aclout = self.add_outbound_acl("VpcNetworkAclOutboundRule", self.netacl_ref)

    
# ---------------------------------------------------------    
    def add_description(self, desc: str):
        """ Add a description to the config """

        self.template.add_description(desc)


    def add_metadata(self, data: dict):
        """Add metadata to the config passed as a dictionary"""

        self.template.add_metadata(data)


    def add_vpc(self, vpc_name: str, env: str, tag_name: str) -> Ref:
        """Adds a VPC resource"""

        # Can also do it this way...
        # vpc = ec2.VPC('VPC')
        # vpc.CidrBlock = '10.0.0.0/16'
        # etc.
        
        vpc = ec2.VPC(
            vpc_name,
            CidrBlock = '10.0.0.0/16',
            EnableDnsHostnames = 'true',
            EnableDnsSupport = 'true',
            InstanceTenancy = 'default',
            Tags = Tags(
                Environment = env,
                Name = '%s-%s' % (env, tag_name)
            )
        )
        self.template.add_resource(vpc)

        return Ref(vpc)


    def add_internetgateway(self, igw_name: str, env: str, tag_name: str) -> Ref:
        """Adds a Internet Gateway resource"""
        
        igw = ec2.InternetGateway(
            igw_name,
            Tags = Tags(
                Environment = env,
                Name = '%s-%s' % (env, tag_name)
            )
        )
        self.template.add_resource(igw)

        return Ref(igw)


    def add_vpcgatewayattachement(self, igw: Ref, vpc: Ref, env: str, name: str) -> Ref:
        """Adds a VPC gateway attachment resource"""

        vpcgwa = ec2.VPCGatewayAttachment(
            name,
            VpcId = vpc,
            InternetGatewayId = igw,
        )
        self.template.add_resource(vpcgwa)

        return Ref(vpcgwa)


    def add_output(self, out_name: str, ref: Ref) -> Ref:
        """Adds a simple output"""

        out = Output(
            out_name,
            Value = ref
        )
        self.template.add_output(out)

        return Ref(out)


    def add_networkacl(self, nacl_name: str, vpc: Ref, env: str, tag_name: str) -> Ref:
        """Adds a Network ACL resource"""

        nacl = ec2.NetworkAcl(
            nacl_name,
            VpcId = vpc,
            Tags = Tags(
                Environment = env,
                Name = '%s-%s' % (env, tag_name)
            )
        )
        self.template.add_resource(nacl)

        return Ref(nacl)


    def add_inbound_acl(self, name: str, acl_id: Ref) -> Ref:
        """Adds an inbound network ACL rule resource"""

        nacl_ent = ec2.NetworkAclEntry(
            name,
            CidrBlock = '0.0.0.0/0',
            Egress = 'false',
            NetworkAclId = acl_id,
            PortRange = ec2.PortRange(
                From = '443',
                To = '443'
            ),
            Protocol = '6',
            RuleAction = 'allow',
            RuleNumber = 100
        )
        self.template.add_resource(nacl_ent)

        return Ref(nacl_ent)


    def add_outbound_acl(self, name: str, acl_id: Ref):
        """Adds an outbound network ACL rule resource"""

        nacl_ent = ec2.NetworkAclEntry(
            name,
            CidrBlock = '0.0.0.0/0',
            Egress = 'true',
            NetworkAclId = acl_id,
            Protocol = '6',
            RuleAction = 'allow',
            RuleNumber = 200
        )
        self.template.add_resource(nacl_ent)

        return Ref(nacl_ent)

# ---------------------------------------------------------
def execute_template(config_data):
    """Standard template function which executes our template code and returns the template as JSON"""    
    
    t = ViaPlayTestTemplate(config_data)
    return t.template.to_json()