r'''
# EC2 Image Builder Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

## README

[Amazon EC2 Image Builder](https://docs.aws.amazon.com/imagebuilder/latest/userguide/what-is-image-builder.html) is a
fully managed AWS service that helps you automate the creation, management, and deployment of customized, secure, and
up-to-date server images. You can use Image Builder to create Amazon Machine Images (AMIs) and container images for use
across AWS Regions.

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project. It allows you to define
Image Builder pipelines, images, recipes, components, workflows, and lifecycle policies.
A component defines the sequence of steps required to customize an instance during image creation (build component) or
test an instance launched from the created image (test component). Components are created from declarative YAML or JSON
documents that describe runtime configuration for building, validating, or testing instances. Components are included
when added to the image recipe or container recipe for an image build.

EC2 Image Builder supports AWS-managed components for common tasks, AWS Marketplace components, and custom components
that you create. Components run during specific workflow phases: build and validate phases during the build stage, and
test phase during the test stage.

### Infrastructure Configuration

Infrastructure configuration defines the compute resources and environment settings used during the image building
process. This includes instance types, IAM instance profile, VPC settings, subnets, security groups, SNS topics for
notifications, logging configuration, and troubleshooting settings like whether to terminate instances on failure or
keep them running for debugging. These settings are applied to builds when included in an image or an image pipeline.

```python
infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
    infrastructure_configuration_name="test-infrastructure-configuration",
    description="An Infrastructure Configuration",
    # Optional - instance types to use for build/test
    instance_types=[
        ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
        ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
    ],
    # Optional - create an instance profile with necessary permissions
    instance_profile=iam.InstanceProfile(self, "InstanceProfile",
        instance_profile_name="test-instance-profile",
        role=iam.Role(self, "InstanceProfileRole",
            assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
            ]
        )
    ),
    # Use VPC network configuration
    vpc=vpc,
    subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
    security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
    key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
    terminate_instance_on_failure=True,
    # Optional - IMDSv2 settings
    http_tokens=imagebuilder.HttpTokens.REQUIRED,
    http_put_response_hop_limit=1,
    # Optional - publish image completion messages to an SNS topic
    notification_topic=sns.Topic.from_topic_arn(self, "Topic",
        self.format_arn(service="sns", resource="image-builder-topic")),
    # Optional - log settings. Logging is enabled by default
    logging=imagebuilder.InfrastructureConfigurationLogging(
        s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
        s3_key_prefix="imagebuilder-logs"
    ),
    # Optional - host placement settings
    ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
    ec2_instance_host_id=dedicated_host.attr_host_id,
    ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
    resource_tags={
        "Environment": "production"
    }
)
```
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.enum(jsii_type="@aws-cdk/aws-imagebuilder-alpha.HttpTokens")
class HttpTokens(enum.Enum):
    '''(experimental) Indicates whether a signed token header is required for instance metadata retrieval requests.

    :see: https://docs.aws.amazon.com/imagebuilder/latest/APIReference/API_InstanceMetadataOptions.html#imagebuilder-Type-InstanceMetadataOptions-httpTokens
    :stability: experimental
    :exampleMetadata: infused

    Example::

        infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
            infrastructure_configuration_name="test-infrastructure-configuration",
            description="An Infrastructure Configuration",
            # Optional - instance types to use for build/test
            instance_types=[
                ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
                ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
            ],
            # Optional - create an instance profile with necessary permissions
            instance_profile=iam.InstanceProfile(self, "InstanceProfile",
                instance_profile_name="test-instance-profile",
                role=iam.Role(self, "InstanceProfileRole",
                    assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
                    managed_policies=[
                        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
                    ]
                )
            ),
            # Use VPC network configuration
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
            key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
            terminate_instance_on_failure=True,
            # Optional - IMDSv2 settings
            http_tokens=imagebuilder.HttpTokens.REQUIRED,
            http_put_response_hop_limit=1,
            # Optional - publish image completion messages to an SNS topic
            notification_topic=sns.Topic.from_topic_arn(self, "Topic",
                self.format_arn(service="sns", resource="image-builder-topic")),
            # Optional - log settings. Logging is enabled by default
            logging=imagebuilder.InfrastructureConfigurationLogging(
                s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
                s3_key_prefix="imagebuilder-logs"
            ),
            # Optional - host placement settings
            ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
            ec2_instance_host_id=dedicated_host.attr_host_id,
            ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
            resource_tags={
                "Environment": "production"
            }
        )
    '''

    OPTIONAL = "OPTIONAL"
    '''(experimental) Allows retrieval of instance metadata with or without a signed token header in the request.

    :stability: experimental
    '''
    REQUIRED = "REQUIRED"
    '''(experimental) Requires a signed token header in instance metadata retrieval requests.

    :stability: experimental
    '''


@jsii.interface(
    jsii_type="@aws-cdk/aws-imagebuilder-alpha.IInfrastructureConfiguration"
)
class IInfrastructureConfiguration(
    _aws_cdk_ceddda9d.IResource,
    typing_extensions.Protocol,
):
    '''(experimental) An EC2 Image Builder Infrastructure Configuration.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the infrastructure configuration.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationName")
    def infrastructure_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the infrastructure configuration.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant custom actions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.
        :param actions: - The list of actions.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.

        :stability: experimental
        '''
        ...


class _IInfrastructureConfigurationProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) An EC2 Image Builder Infrastructure Configuration.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-imagebuilder-alpha.IInfrastructureConfiguration"

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the infrastructure configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationName")
    def infrastructure_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the infrastructure configuration.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationName"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant custom actions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.
        :param actions: - The list of actions.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f4ed7436405bcfb3a075aa5c93725806206943d8dbaa96c5cef8dd4d46cae37)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2582830fbd4fc0772d12414b5d2346ecedd7b1bb8582db47fa079012ef22197)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IInfrastructureConfiguration).__jsii_proxy_class__ = lambda : _IInfrastructureConfigurationProxy


@jsii.implements(IInfrastructureConfiguration)
class InfrastructureConfiguration(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-imagebuilder-alpha.InfrastructureConfiguration",
):
    '''(experimental) Represents an EC2 Image Builder Infrastructure Configuration.

    :see: https://docs.aws.amazon.com/imagebuilder/latest/userguide/manage-infra-config.html
    :stability: experimental
    :exampleMetadata: infused

    Example::

        infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
            infrastructure_configuration_name="test-infrastructure-configuration",
            description="An Infrastructure Configuration",
            # Optional - instance types to use for build/test
            instance_types=[
                ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
                ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
            ],
            # Optional - create an instance profile with necessary permissions
            instance_profile=iam.InstanceProfile(self, "InstanceProfile",
                instance_profile_name="test-instance-profile",
                role=iam.Role(self, "InstanceProfileRole",
                    assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
                    managed_policies=[
                        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
                    ]
                )
            ),
            # Use VPC network configuration
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
            key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
            terminate_instance_on_failure=True,
            # Optional - IMDSv2 settings
            http_tokens=imagebuilder.HttpTokens.REQUIRED,
            http_put_response_hop_limit=1,
            # Optional - publish image completion messages to an SNS topic
            notification_topic=sns.Topic.from_topic_arn(self, "Topic",
                self.format_arn(service="sns", resource="image-builder-topic")),
            # Optional - log settings. Logging is enabled by default
            logging=imagebuilder.InfrastructureConfigurationLogging(
                s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
                s3_key_prefix="imagebuilder-logs"
            ),
            # Optional - host placement settings
            ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
            ec2_instance_host_id=dedicated_host.attr_host_id,
            ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
            resource_tags={
                "Environment": "production"
            }
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        ec2_instance_availability_zone: typing.Optional[builtins.str] = None,
        ec2_instance_host_id: typing.Optional[builtins.str] = None,
        ec2_instance_host_resource_group_arn: typing.Optional[builtins.str] = None,
        ec2_instance_tenancy: typing.Optional["Tenancy"] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[HttpTokens] = None,
        infrastructure_configuration_name: typing.Optional[builtins.str] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        logging: typing.Optional[typing.Union["InfrastructureConfigurationLogging", typing.Dict[builtins.str, typing.Any]]] = None,
        notification_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        terminate_instance_on_failure: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: (experimental) The description of the infrastructure configuration. Default: None
        :param ec2_instance_availability_zone: (experimental) The availability zone to place Image Builder build and test EC2 instances. Default: EC2 will select a random zone
        :param ec2_instance_host_id: (experimental) The ID of the Dedicated Host on which build and test instances run. This only applies if the instance tenancy is ``host``. This cannot be used with the ``ec2InstanceHostResourceGroupArn`` parameter. Default: None
        :param ec2_instance_host_resource_group_arn: (experimental) The ARN of the host resource group on which build and test instances run. This only applies if the instance tenancy is ``host``. This cannot be used with the ``ec2InstanceHostId`` parameter. Default: None
        :param ec2_instance_tenancy: (experimental) The tenancy of the instance. Dedicated tenancy runs instances on single-tenant hardware, while host tenancy runs instances on a dedicated host. Shared tenancy is used by default. Default: Tenancy.DEFAULT
        :param http_put_response_hop_limit: (experimental) The maximum number of hops that an instance metadata request can traverse to reach its destination. By default, this is set to 2. Default: 2
        :param http_tokens: (experimental) Indicates whether a signed token header is required for instance metadata retrieval requests. By default, this is set to ``required`` to require IMDSv2 on build and test EC2 instances. Default: HttpTokens.REQUIRED
        :param infrastructure_configuration_name: (experimental) The name of the infrastructure configuration. This name must be normalized by transforming all alphabetical characters to lowercase, and replacing all spaces and underscores with hyphens. Default: A name is generated
        :param instance_profile: (experimental) The instance profile to associate with the instance used to customize the AMI. By default, an instance profile and role will be created with minimal permissions needed to build the image, attached to the EC2 instance. If an S3 logging bucket and key prefix is provided, an IAM inline policy will be attached to the instance profile's role, allowing s3:PutObject permissions on the bucket. Default: An instance profile will be generated
        :param instance_types: (experimental) The instance types to launch build and test EC2 instances with. Default: Image Builder will choose from a default set of instance types compatible with the AMI
        :param key_pair: (experimental) The key pair used to connect to the build and test EC2 instances. The key pair can be used to log into the build or test instances for troubleshooting any failures. Default: None
        :param logging: (experimental) The log settings for detailed build logging. Default: None
        :param notification_topic: (experimental) The SNS topic on which notifications are sent when an image build completes. Default: No notifications are sent
        :param resource_tags: (experimental) The additional tags to assign to the Amazon EC2 instance that Image Builder launches during the build process. Default: None
        :param role: (experimental) An IAM role to associate with the instance profile used by Image Builder. The role must be assumable by the service principal ``ec2.amazonaws.com``: Note: You can provide an instanceProfile or a role, but not both. Default: A role will automatically be created, it can be accessed via the ``role`` property
        :param security_groups: (experimental) The security groups to associate with the instance used to customize the AMI. Default: The default security group for the VPC will be used
        :param subnet_selection: (experimental) Select which subnet to place the instance used to customize the AMI. The first subnet that is selected will be used. You must specify the VPC to customize the subnet selection. Default: The first subnet selected from the provided VPC will be used
        :param tags: (experimental) The tags to apply to the infrastructure configuration. Default: None
        :param terminate_instance_on_failure: (experimental) Whether to terminate the EC2 instance when the build or test workflow fails. Default: true
        :param vpc: (experimental) The VPC to place the instance used to customize the AMI. Default: The default VPC will be used

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8672dd2c6991d2ba23136620a37140cb449f0b7606cfe5538649d44bc009387)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = InfrastructureConfigurationProps(
            description=description,
            ec2_instance_availability_zone=ec2_instance_availability_zone,
            ec2_instance_host_id=ec2_instance_host_id,
            ec2_instance_host_resource_group_arn=ec2_instance_host_resource_group_arn,
            ec2_instance_tenancy=ec2_instance_tenancy,
            http_put_response_hop_limit=http_put_response_hop_limit,
            http_tokens=http_tokens,
            infrastructure_configuration_name=infrastructure_configuration_name,
            instance_profile=instance_profile,
            instance_types=instance_types,
            key_pair=key_pair,
            logging=logging,
            notification_topic=notification_topic,
            resource_tags=resource_tags,
            role=role,
            security_groups=security_groups,
            subnet_selection=subnet_selection,
            tags=tags,
            terminate_instance_on_failure=terminate_instance_on_failure,
            vpc=vpc,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromInfrastructureConfigurationArn")
    @builtins.classmethod
    def from_infrastructure_configuration_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        infrastructure_configuration_arn: builtins.str,
    ) -> IInfrastructureConfiguration:
        '''(experimental) Import an existing infrastructure configuration given its ARN.

        :param scope: -
        :param id: -
        :param infrastructure_configuration_arn: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35015fe2e49bc142df9482904b92351bbc9b41c560cac1ac06713b2b564cd982)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument infrastructure_configuration_arn", value=infrastructure_configuration_arn, expected_type=type_hints["infrastructure_configuration_arn"])
        return typing.cast(IInfrastructureConfiguration, jsii.sinvoke(cls, "fromInfrastructureConfigurationArn", [scope, id, infrastructure_configuration_arn]))

    @jsii.member(jsii_name="fromInfrastructureConfigurationName")
    @builtins.classmethod
    def from_infrastructure_configuration_name(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        infrastructure_configuration_name: builtins.str,
    ) -> IInfrastructureConfiguration:
        '''(experimental) Import an existing infrastructure configuration given its name.

        The provided name must be normalized by converting
        all alphabetical characters to lowercase, and replacing all spaces and underscores with hyphens.

        :param scope: -
        :param id: -
        :param infrastructure_configuration_name: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d30c941bd6f0f1b07145f10c999bbeef38a9fbbc483fdfb4e54de8301a42bd6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument infrastructure_configuration_name", value=infrastructure_configuration_name, expected_type=type_hints["infrastructure_configuration_name"])
        return typing.cast(IInfrastructureConfiguration, jsii.sinvoke(cls, "fromInfrastructureConfigurationName", [scope, id, infrastructure_configuration_name]))

    @jsii.member(jsii_name="isInfrastructureConfiguration")
    @builtins.classmethod
    def is_infrastructure_configuration(cls, x: typing.Any) -> builtins.bool:
        '''(experimental) Return whether the given object is an InfrastructureConfiguration.

        :param x: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__653ebae43bf6b6e095ea87727d122e7cab0c8786387877992a5a7e642a846e02)
            check_type(argname="argument x", value=x, expected_type=type_hints["x"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isInfrastructureConfiguration", [x]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant custom actions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.
        :param actions: - The list of actions.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d73bd89218669ef1c777360509401b7db5901968dd024b757f3c75f85ccd1228)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions to the given grantee for the infrastructure configuration.

        :param grantee: - The principal.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61c74f957e8c879932590c0d74b45224a68ab6d8eca577948a171e837ccc4cda)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationArn")
    def infrastructure_configuration_arn(self) -> builtins.str:
        '''(experimental) The ARN of the infrastructure configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationArn"))

    @builtins.property
    @jsii.member(jsii_name="infrastructureConfigurationName")
    def infrastructure_configuration_name(self) -> builtins.str:
        '''(experimental) The name of the infrastructure configuration.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "infrastructureConfigurationName"))

    @builtins.property
    @jsii.member(jsii_name="instanceProfile")
    def instance_profile(self) -> _aws_cdk_aws_iam_ceddda9d.IInstanceProfile:
        '''(experimental) The EC2 instance profile to use for the build.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IInstanceProfile, jsii.get(self, "instanceProfile"))

    @builtins.property
    @jsii.member(jsii_name="logBucket")
    def log_bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) The bucket used to upload image build logs.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], jsii.get(self, "logBucket"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The role associated with the EC2 instance profile used for the build.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "role"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-imagebuilder-alpha.InfrastructureConfigurationLogging",
    jsii_struct_bases=[],
    name_mapping={"s3_bucket": "s3Bucket", "s3_key_prefix": "s3KeyPrefix"},
)
class InfrastructureConfigurationLogging:
    def __init__(
        self,
        *,
        s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
        s3_key_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) The log settings for detailed build logging.

        :param s3_bucket: (experimental) The S3 logging bucket to use for detailed build logging.
        :param s3_key_prefix: (experimental) The S3 logging prefix to use for detailed build logging. Default: No prefix

        :stability: experimental
        :exampleMetadata: infused

        Example::

            infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
                infrastructure_configuration_name="test-infrastructure-configuration",
                description="An Infrastructure Configuration",
                # Optional - instance types to use for build/test
                instance_types=[
                    ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
                    ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
                ],
                # Optional - create an instance profile with necessary permissions
                instance_profile=iam.InstanceProfile(self, "InstanceProfile",
                    instance_profile_name="test-instance-profile",
                    role=iam.Role(self, "InstanceProfileRole",
                        assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                            iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
                        ]
                    )
                ),
                # Use VPC network configuration
                vpc=vpc,
                subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
                key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
                terminate_instance_on_failure=True,
                # Optional - IMDSv2 settings
                http_tokens=imagebuilder.HttpTokens.REQUIRED,
                http_put_response_hop_limit=1,
                # Optional - publish image completion messages to an SNS topic
                notification_topic=sns.Topic.from_topic_arn(self, "Topic",
                    self.format_arn(service="sns", resource="image-builder-topic")),
                # Optional - log settings. Logging is enabled by default
                logging=imagebuilder.InfrastructureConfigurationLogging(
                    s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
                    s3_key_prefix="imagebuilder-logs"
                ),
                # Optional - host placement settings
                ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
                ec2_instance_host_id=dedicated_host.attr_host_id,
                ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
                resource_tags={
                    "Environment": "production"
                }
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74cffe7aa25819eaef361f450e04e7112a9f46a9d0138a9696f9723b55a1d31d)
            check_type(argname="argument s3_bucket", value=s3_bucket, expected_type=type_hints["s3_bucket"])
            check_type(argname="argument s3_key_prefix", value=s3_key_prefix, expected_type=type_hints["s3_key_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_bucket": s3_bucket,
        }
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix

    @builtins.property
    def s3_bucket(self) -> _aws_cdk_aws_s3_ceddda9d.IBucket:
        '''(experimental) The S3 logging bucket to use for detailed build logging.

        :stability: experimental
        '''
        result = self._values.get("s3_bucket")
        assert result is not None, "Required property 's3_bucket' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.IBucket, result)

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) The S3 logging prefix to use for detailed build logging.

        :default: No prefix

        :stability: experimental
        '''
        result = self._values.get("s3_key_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfrastructureConfigurationLogging(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-imagebuilder-alpha.InfrastructureConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "ec2_instance_availability_zone": "ec2InstanceAvailabilityZone",
        "ec2_instance_host_id": "ec2InstanceHostId",
        "ec2_instance_host_resource_group_arn": "ec2InstanceHostResourceGroupArn",
        "ec2_instance_tenancy": "ec2InstanceTenancy",
        "http_put_response_hop_limit": "httpPutResponseHopLimit",
        "http_tokens": "httpTokens",
        "infrastructure_configuration_name": "infrastructureConfigurationName",
        "instance_profile": "instanceProfile",
        "instance_types": "instanceTypes",
        "key_pair": "keyPair",
        "logging": "logging",
        "notification_topic": "notificationTopic",
        "resource_tags": "resourceTags",
        "role": "role",
        "security_groups": "securityGroups",
        "subnet_selection": "subnetSelection",
        "tags": "tags",
        "terminate_instance_on_failure": "terminateInstanceOnFailure",
        "vpc": "vpc",
    },
)
class InfrastructureConfigurationProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        ec2_instance_availability_zone: typing.Optional[builtins.str] = None,
        ec2_instance_host_id: typing.Optional[builtins.str] = None,
        ec2_instance_host_resource_group_arn: typing.Optional[builtins.str] = None,
        ec2_instance_tenancy: typing.Optional["Tenancy"] = None,
        http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
        http_tokens: typing.Optional[HttpTokens] = None,
        infrastructure_configuration_name: typing.Optional[builtins.str] = None,
        instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
        instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
        key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
        logging: typing.Optional[typing.Union[InfrastructureConfigurationLogging, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        terminate_instance_on_failure: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> None:
        '''(experimental) Properties for creating an Infrastructure Configuration resource.

        :param description: (experimental) The description of the infrastructure configuration. Default: None
        :param ec2_instance_availability_zone: (experimental) The availability zone to place Image Builder build and test EC2 instances. Default: EC2 will select a random zone
        :param ec2_instance_host_id: (experimental) The ID of the Dedicated Host on which build and test instances run. This only applies if the instance tenancy is ``host``. This cannot be used with the ``ec2InstanceHostResourceGroupArn`` parameter. Default: None
        :param ec2_instance_host_resource_group_arn: (experimental) The ARN of the host resource group on which build and test instances run. This only applies if the instance tenancy is ``host``. This cannot be used with the ``ec2InstanceHostId`` parameter. Default: None
        :param ec2_instance_tenancy: (experimental) The tenancy of the instance. Dedicated tenancy runs instances on single-tenant hardware, while host tenancy runs instances on a dedicated host. Shared tenancy is used by default. Default: Tenancy.DEFAULT
        :param http_put_response_hop_limit: (experimental) The maximum number of hops that an instance metadata request can traverse to reach its destination. By default, this is set to 2. Default: 2
        :param http_tokens: (experimental) Indicates whether a signed token header is required for instance metadata retrieval requests. By default, this is set to ``required`` to require IMDSv2 on build and test EC2 instances. Default: HttpTokens.REQUIRED
        :param infrastructure_configuration_name: (experimental) The name of the infrastructure configuration. This name must be normalized by transforming all alphabetical characters to lowercase, and replacing all spaces and underscores with hyphens. Default: A name is generated
        :param instance_profile: (experimental) The instance profile to associate with the instance used to customize the AMI. By default, an instance profile and role will be created with minimal permissions needed to build the image, attached to the EC2 instance. If an S3 logging bucket and key prefix is provided, an IAM inline policy will be attached to the instance profile's role, allowing s3:PutObject permissions on the bucket. Default: An instance profile will be generated
        :param instance_types: (experimental) The instance types to launch build and test EC2 instances with. Default: Image Builder will choose from a default set of instance types compatible with the AMI
        :param key_pair: (experimental) The key pair used to connect to the build and test EC2 instances. The key pair can be used to log into the build or test instances for troubleshooting any failures. Default: None
        :param logging: (experimental) The log settings for detailed build logging. Default: None
        :param notification_topic: (experimental) The SNS topic on which notifications are sent when an image build completes. Default: No notifications are sent
        :param resource_tags: (experimental) The additional tags to assign to the Amazon EC2 instance that Image Builder launches during the build process. Default: None
        :param role: (experimental) An IAM role to associate with the instance profile used by Image Builder. The role must be assumable by the service principal ``ec2.amazonaws.com``: Note: You can provide an instanceProfile or a role, but not both. Default: A role will automatically be created, it can be accessed via the ``role`` property
        :param security_groups: (experimental) The security groups to associate with the instance used to customize the AMI. Default: The default security group for the VPC will be used
        :param subnet_selection: (experimental) Select which subnet to place the instance used to customize the AMI. The first subnet that is selected will be used. You must specify the VPC to customize the subnet selection. Default: The first subnet selected from the provided VPC will be used
        :param tags: (experimental) The tags to apply to the infrastructure configuration. Default: None
        :param terminate_instance_on_failure: (experimental) Whether to terminate the EC2 instance when the build or test workflow fails. Default: true
        :param vpc: (experimental) The VPC to place the instance used to customize the AMI. Default: The default VPC will be used

        :stability: experimental
        :exampleMetadata: infused

        Example::

            infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
                infrastructure_configuration_name="test-infrastructure-configuration",
                description="An Infrastructure Configuration",
                # Optional - instance types to use for build/test
                instance_types=[
                    ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
                    ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
                ],
                # Optional - create an instance profile with necessary permissions
                instance_profile=iam.InstanceProfile(self, "InstanceProfile",
                    instance_profile_name="test-instance-profile",
                    role=iam.Role(self, "InstanceProfileRole",
                        assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
                        managed_policies=[
                            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                            iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
                        ]
                    )
                ),
                # Use VPC network configuration
                vpc=vpc,
                subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
                security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
                key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
                terminate_instance_on_failure=True,
                # Optional - IMDSv2 settings
                http_tokens=imagebuilder.HttpTokens.REQUIRED,
                http_put_response_hop_limit=1,
                # Optional - publish image completion messages to an SNS topic
                notification_topic=sns.Topic.from_topic_arn(self, "Topic",
                    self.format_arn(service="sns", resource="image-builder-topic")),
                # Optional - log settings. Logging is enabled by default
                logging=imagebuilder.InfrastructureConfigurationLogging(
                    s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
                    s3_key_prefix="imagebuilder-logs"
                ),
                # Optional - host placement settings
                ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
                ec2_instance_host_id=dedicated_host.attr_host_id,
                ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
                resource_tags={
                    "Environment": "production"
                }
            )
        '''
        if isinstance(logging, dict):
            logging = InfrastructureConfigurationLogging(**logging)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07545a4f62a3521f9640beafa4b4d7cc1fbe20fc1df54541287ed96ffe7f8e4e)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument ec2_instance_availability_zone", value=ec2_instance_availability_zone, expected_type=type_hints["ec2_instance_availability_zone"])
            check_type(argname="argument ec2_instance_host_id", value=ec2_instance_host_id, expected_type=type_hints["ec2_instance_host_id"])
            check_type(argname="argument ec2_instance_host_resource_group_arn", value=ec2_instance_host_resource_group_arn, expected_type=type_hints["ec2_instance_host_resource_group_arn"])
            check_type(argname="argument ec2_instance_tenancy", value=ec2_instance_tenancy, expected_type=type_hints["ec2_instance_tenancy"])
            check_type(argname="argument http_put_response_hop_limit", value=http_put_response_hop_limit, expected_type=type_hints["http_put_response_hop_limit"])
            check_type(argname="argument http_tokens", value=http_tokens, expected_type=type_hints["http_tokens"])
            check_type(argname="argument infrastructure_configuration_name", value=infrastructure_configuration_name, expected_type=type_hints["infrastructure_configuration_name"])
            check_type(argname="argument instance_profile", value=instance_profile, expected_type=type_hints["instance_profile"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument key_pair", value=key_pair, expected_type=type_hints["key_pair"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument notification_topic", value=notification_topic, expected_type=type_hints["notification_topic"])
            check_type(argname="argument resource_tags", value=resource_tags, expected_type=type_hints["resource_tags"])
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument terminate_instance_on_failure", value=terminate_instance_on_failure, expected_type=type_hints["terminate_instance_on_failure"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if ec2_instance_availability_zone is not None:
            self._values["ec2_instance_availability_zone"] = ec2_instance_availability_zone
        if ec2_instance_host_id is not None:
            self._values["ec2_instance_host_id"] = ec2_instance_host_id
        if ec2_instance_host_resource_group_arn is not None:
            self._values["ec2_instance_host_resource_group_arn"] = ec2_instance_host_resource_group_arn
        if ec2_instance_tenancy is not None:
            self._values["ec2_instance_tenancy"] = ec2_instance_tenancy
        if http_put_response_hop_limit is not None:
            self._values["http_put_response_hop_limit"] = http_put_response_hop_limit
        if http_tokens is not None:
            self._values["http_tokens"] = http_tokens
        if infrastructure_configuration_name is not None:
            self._values["infrastructure_configuration_name"] = infrastructure_configuration_name
        if instance_profile is not None:
            self._values["instance_profile"] = instance_profile
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if key_pair is not None:
            self._values["key_pair"] = key_pair
        if logging is not None:
            self._values["logging"] = logging
        if notification_topic is not None:
            self._values["notification_topic"] = notification_topic
        if resource_tags is not None:
            self._values["resource_tags"] = resource_tags
        if role is not None:
            self._values["role"] = role
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection
        if tags is not None:
            self._values["tags"] = tags
        if terminate_instance_on_failure is not None:
            self._values["terminate_instance_on_failure"] = terminate_instance_on_failure
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the infrastructure configuration.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_availability_zone(self) -> typing.Optional[builtins.str]:
        '''(experimental) The availability zone to place Image Builder build and test EC2 instances.

        :default: EC2 will select a random zone

        :stability: experimental
        '''
        result = self._values.get("ec2_instance_availability_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_host_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ID of the Dedicated Host on which build and test instances run.

        This only applies if the instance tenancy is
        ``host``. This cannot be used with the ``ec2InstanceHostResourceGroupArn`` parameter.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("ec2_instance_host_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_host_resource_group_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The ARN of the host resource group on which build and test instances run.

        This only applies if the instance tenancy
        is ``host``. This cannot be used with the ``ec2InstanceHostId`` parameter.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("ec2_instance_host_resource_group_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ec2_instance_tenancy(self) -> typing.Optional["Tenancy"]:
        '''(experimental) The tenancy of the instance.

        Dedicated tenancy runs instances on single-tenant hardware, while host tenancy runs
        instances on a dedicated host. Shared tenancy is used by default.

        :default: Tenancy.DEFAULT

        :stability: experimental
        '''
        result = self._values.get("ec2_instance_tenancy")
        return typing.cast(typing.Optional["Tenancy"], result)

    @builtins.property
    def http_put_response_hop_limit(self) -> typing.Optional[jsii.Number]:
        '''(experimental) The maximum number of hops that an instance metadata request can traverse to reach its destination.

        By default,
        this is set to 2.

        :default: 2

        :stability: experimental
        '''
        result = self._values.get("http_put_response_hop_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_tokens(self) -> typing.Optional[HttpTokens]:
        '''(experimental) Indicates whether a signed token header is required for instance metadata retrieval requests.

        By default, this is
        set to ``required`` to require IMDSv2 on build and test EC2 instances.

        :default: HttpTokens.REQUIRED

        :stability: experimental
        '''
        result = self._values.get("http_tokens")
        return typing.cast(typing.Optional[HttpTokens], result)

    @builtins.property
    def infrastructure_configuration_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of the infrastructure configuration.

        This name must be normalized by transforming all alphabetical
        characters to lowercase, and replacing all spaces and underscores with hyphens.

        :default: A name is generated

        :stability: experimental
        '''
        result = self._values.get("infrastructure_configuration_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instance_profile(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile]:
        '''(experimental) The instance profile to associate with the instance used to customize the AMI.

        By default, an instance profile and role will be created with minimal permissions needed to build the image,
        attached to the EC2 instance.

        If an S3 logging bucket and key prefix is provided, an IAM inline policy will be attached to the instance profile's
        role, allowing s3:PutObject permissions on the bucket.

        :default: An instance profile will be generated

        :stability: experimental
        '''
        result = self._values.get("instance_profile")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile], result)

    @builtins.property
    def instance_types(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]]:
        '''(experimental) The instance types to launch build and test EC2 instances with.

        :default: Image Builder will choose from a default set of instance types compatible with the AMI

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.InstanceType]], result)

    @builtins.property
    def key_pair(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair]:
        '''(experimental) The key pair used to connect to the build and test EC2 instances.

        The key pair can be used to log into the build
        or test instances for troubleshooting any failures.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("key_pair")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair], result)

    @builtins.property
    def logging(self) -> typing.Optional[InfrastructureConfigurationLogging]:
        '''(experimental) The log settings for detailed build logging.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[InfrastructureConfigurationLogging], result)

    @builtins.property
    def notification_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''(experimental) The SNS topic on which notifications are sent when an image build completes.

        :default: No notifications are sent

        :stability: experimental
        '''
        result = self._values.get("notification_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def resource_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The additional tags to assign to the Amazon EC2 instance that Image Builder launches during the build process.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("resource_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) An IAM role to associate with the instance profile used by Image Builder.

        The role must be assumable by the service principal ``ec2.amazonaws.com``:
        Note: You can provide an instanceProfile or a role, but not both.

        :default: A role will automatically be created, it can be accessed via the ``role`` property

        :stability: experimental

        Example::

            role = iam.Role(self, "MyRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
            )
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The security groups to associate with the instance used to customize the AMI.

        :default: The default security group for the VPC will be used

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Select which subnet to place the instance used to customize the AMI.

        The first subnet that is selected will be used.
        You must specify the VPC to customize the subnet selection.

        :default: The first subnet selected from the provided VPC will be used

        :stability: experimental
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) The tags to apply to the infrastructure configuration.

        :default: None

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def terminate_instance_on_failure(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to terminate the EC2 instance when the build or test workflow fails.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("terminate_instance_on_failure")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''(experimental) The VPC to place the instance used to customize the AMI.

        :default: The default VPC will be used

        :stability: experimental
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InfrastructureConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-imagebuilder-alpha.Tenancy")
class Tenancy(enum.Enum):
    '''(experimental) The tenancy to use for an instance.

    :see: https://docs.aws.amazon.com/imagebuilder/latest/APIReference/API_Placement.html#imagebuilder-Type-Placement-tenancy
    :stability: experimental
    :exampleMetadata: infused

    Example::

        infrastructure_configuration = imagebuilder.InfrastructureConfiguration(self, "InfrastructureConfiguration",
            infrastructure_configuration_name="test-infrastructure-configuration",
            description="An Infrastructure Configuration",
            # Optional - instance types to use for build/test
            instance_types=[
                ec2.InstanceType.of(ec2.InstanceClass.STANDARD7_INTEL, ec2.InstanceSize.LARGE),
                ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.LARGE)
            ],
            # Optional - create an instance profile with necessary permissions
            instance_profile=iam.InstanceProfile(self, "InstanceProfile",
                instance_profile_name="test-instance-profile",
                role=iam.Role(self, "InstanceProfileRole",
                    assumed_by=iam.ServicePrincipal.from_static_service_principle_name("ec2.amazonaws.com"),
                    managed_policies=[
                        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                        iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
                    ]
                )
            ),
            # Use VPC network configuration
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup", vpc.vpc_default_security_group)],
            key_pair=ec2.KeyPair.from_key_pair_name(self, "KeyPair", "imagebuilder-instance-key-pair"),
            terminate_instance_on_failure=True,
            # Optional - IMDSv2 settings
            http_tokens=imagebuilder.HttpTokens.REQUIRED,
            http_put_response_hop_limit=1,
            # Optional - publish image completion messages to an SNS topic
            notification_topic=sns.Topic.from_topic_arn(self, "Topic",
                self.format_arn(service="sns", resource="image-builder-topic")),
            # Optional - log settings. Logging is enabled by default
            logging=imagebuilder.InfrastructureConfigurationLogging(
                s3_bucket=s3.Bucket.from_bucket_name(self, "LogBucket", f"imagebuilder-logging-{Aws.ACCOUNT_ID}"),
                s3_key_prefix="imagebuilder-logs"
            ),
            # Optional - host placement settings
            ec2_instance_availability_zone=Stack.of(self).availability_zones[0],
            ec2_instance_host_id=dedicated_host.attr_host_id,
            ec2_instance_tenancy=imagebuilder.Tenancy.HOST,
            resource_tags={
                "Environment": "production"
            }
        )
    '''

    DEFAULT = "DEFAULT"
    '''(experimental) Instances will be launched with default tenancy.

    :stability: experimental
    '''
    DEDICATED = "DEDICATED"
    '''(experimental) Instances will be launched with dedicated tenancy.

    :stability: experimental
    '''
    HOST = "HOST"
    '''(experimental) Instances will be launched on a dedicated host.

    :stability: experimental
    '''


__all__ = [
    "HttpTokens",
    "IInfrastructureConfiguration",
    "InfrastructureConfiguration",
    "InfrastructureConfigurationLogging",
    "InfrastructureConfigurationProps",
    "Tenancy",
]

publication.publish()

def _typecheckingstub__8f4ed7436405bcfb3a075aa5c93725806206943d8dbaa96c5cef8dd4d46cae37(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2582830fbd4fc0772d12414b5d2346ecedd7b1bb8582db47fa079012ef22197(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8672dd2c6991d2ba23136620a37140cb449f0b7606cfe5538649d44bc009387(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    ec2_instance_availability_zone: typing.Optional[builtins.str] = None,
    ec2_instance_host_id: typing.Optional[builtins.str] = None,
    ec2_instance_host_resource_group_arn: typing.Optional[builtins.str] = None,
    ec2_instance_tenancy: typing.Optional[Tenancy] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[HttpTokens] = None,
    infrastructure_configuration_name: typing.Optional[builtins.str] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    logging: typing.Optional[typing.Union[InfrastructureConfigurationLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    terminate_instance_on_failure: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35015fe2e49bc142df9482904b92351bbc9b41c560cac1ac06713b2b564cd982(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    infrastructure_configuration_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d30c941bd6f0f1b07145f10c999bbeef38a9fbbc483fdfb4e54de8301a42bd6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    infrastructure_configuration_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__653ebae43bf6b6e095ea87727d122e7cab0c8786387877992a5a7e642a846e02(
    x: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d73bd89218669ef1c777360509401b7db5901968dd024b757f3c75f85ccd1228(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61c74f957e8c879932590c0d74b45224a68ab6d8eca577948a171e837ccc4cda(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74cffe7aa25819eaef361f450e04e7112a9f46a9d0138a9696f9723b55a1d31d(
    *,
    s3_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    s3_key_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07545a4f62a3521f9640beafa4b4d7cc1fbe20fc1df54541287ed96ffe7f8e4e(
    *,
    description: typing.Optional[builtins.str] = None,
    ec2_instance_availability_zone: typing.Optional[builtins.str] = None,
    ec2_instance_host_id: typing.Optional[builtins.str] = None,
    ec2_instance_host_resource_group_arn: typing.Optional[builtins.str] = None,
    ec2_instance_tenancy: typing.Optional[Tenancy] = None,
    http_put_response_hop_limit: typing.Optional[jsii.Number] = None,
    http_tokens: typing.Optional[HttpTokens] = None,
    infrastructure_configuration_name: typing.Optional[builtins.str] = None,
    instance_profile: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IInstanceProfile] = None,
    instance_types: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.InstanceType]] = None,
    key_pair: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IKeyPair] = None,
    logging: typing.Optional[typing.Union[InfrastructureConfigurationLogging, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    resource_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    terminate_instance_on_failure: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IInfrastructureConfiguration]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
