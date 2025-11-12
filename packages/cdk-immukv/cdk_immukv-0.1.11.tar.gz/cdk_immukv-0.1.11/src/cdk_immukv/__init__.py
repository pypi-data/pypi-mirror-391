r'''
# cdk-immukv

AWS CDK constructs for deploying ImmuKV infrastructure.

## Installation

### TypeScript/JavaScript

```bash
npm install cdk-immukv
```

### Python

```bash
pip install cdk-immukv
```

## Usage

### TypeScript

```python
import * as cdk from 'aws-cdk-lib';
import { ImmuKVStack } from 'cdk-immukv';

const app = new cdk.App();
new ImmuKVStack(app, 'MyImmuKVStack', {
  bucketName: 'my-immukv-bucket',
  s3Prefix: 'myapp/',
});
```

### Python

```python
import aws_cdk as cdk
from cdk_immukv import ImmuKVStack

app = cdk.App()
ImmuKVStack(app, "MyImmuKVStack",
    bucket_name="my-immukv-bucket",
    s3_prefix="myapp/",
)
```

## API

See the [API documentation](https://github.com/Portfoligno/immukv/tree/main/cdk) for detailed information.

## License

MIT
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
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


class ImmuKVStack(
    _aws_cdk_ceddda9d.Stack,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-immukv.ImmuKVStack",
):
    '''(experimental) AWS CDK Stack for ImmuKV infrastructure.

    Creates an S3 bucket with versioning enabled and IAM policies for
    read/write and read-only access.

    :stability: experimental
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        key_version_retention_days: typing.Optional[jsii.Number] = None,
        key_versions_to_retain: typing.Optional[jsii.Number] = None,
        log_version_retention_days: typing.Optional[jsii.Number] = None,
        log_versions_to_retain: typing.Optional[jsii.Number] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        use_kms_encryption: typing.Optional[builtins.bool] = None,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: (experimental) Name of the S3 bucket for ImmuKV storage. Default: - Auto-generated bucket name
        :param key_version_retention_days: (experimental) Number of days to retain old key object versions. Default: 365
        :param key_versions_to_retain: (experimental) Number of old key versions to retain per key. Default: 100
        :param log_version_retention_days: (experimental) Number of days to retain old log versions. Default: 365
        :param log_versions_to_retain: (experimental) Number of old log versions to retain. Default: 1000
        :param s3_prefix: (experimental) S3 prefix for all ImmuKV objects. Default: - No prefix (root of bucket)
        :param use_kms_encryption: (experimental) Enable KMS encryption instead of S3-managed encryption. Default: false
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notification arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param property_injectors: A list of IPropertyInjector attached to this Stack. Default: - no PropertyInjectors
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Tags that will be applied to the Stack. These tags are applied to the CloudFormation Stack itself. They will not appear in the CloudFormation template. However, at deployment time, CloudFormation will apply these tags to all resources in the stack that support tagging. You will not be able to exempt resources from tagging (using the ``excludeResourceTypes`` property of ``Tags.of(...).add()``) for tags applied in this way. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff501672c790221a5a3d3b7792489059affb4e766151422255b75be4eb3a6aaf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ImmuKVStackProps(
            bucket_name=bucket_name,
            key_version_retention_days=key_version_retention_days,
            key_versions_to_retain=key_versions_to_retain,
            log_version_retention_days=log_version_retention_days,
            log_versions_to_retain=log_versions_to_retain,
            s3_prefix=s3_prefix,
            use_kms_encryption=use_kms_encryption,
            analytics_reporting=analytics_reporting,
            cross_region_references=cross_region_references,
            description=description,
            env=env,
            notification_arns=notification_arns,
            permissions_boundary=permissions_boundary,
            property_injectors=property_injectors,
            stack_name=stack_name,
            suppress_template_indentation=suppress_template_indentation,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''(experimental) The S3 bucket used for ImmuKV storage.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyPolicy")
    def read_only_policy(self) -> _aws_cdk_aws_iam_ceddda9d.ManagedPolicy:
        '''(experimental) IAM managed policy for read-only access.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.ManagedPolicy, jsii.get(self, "readOnlyPolicy"))

    @builtins.property
    @jsii.member(jsii_name="readWritePolicy")
    def read_write_policy(self) -> _aws_cdk_aws_iam_ceddda9d.ManagedPolicy:
        '''(experimental) IAM managed policy for read/write access.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.ManagedPolicy, jsii.get(self, "readWritePolicy"))


@jsii.data_type(
    jsii_type="cdk-immukv.ImmuKVStackProps",
    jsii_struct_bases=[_aws_cdk_ceddda9d.StackProps],
    name_mapping={
        "analytics_reporting": "analyticsReporting",
        "cross_region_references": "crossRegionReferences",
        "description": "description",
        "env": "env",
        "notification_arns": "notificationArns",
        "permissions_boundary": "permissionsBoundary",
        "property_injectors": "propertyInjectors",
        "stack_name": "stackName",
        "suppress_template_indentation": "suppressTemplateIndentation",
        "synthesizer": "synthesizer",
        "tags": "tags",
        "termination_protection": "terminationProtection",
        "bucket_name": "bucketName",
        "key_version_retention_days": "keyVersionRetentionDays",
        "key_versions_to_retain": "keyVersionsToRetain",
        "log_version_retention_days": "logVersionRetentionDays",
        "log_versions_to_retain": "logVersionsToRetain",
        "s3_prefix": "s3Prefix",
        "use_kms_encryption": "useKmsEncryption",
    },
)
class ImmuKVStackProps(_aws_cdk_ceddda9d.StackProps):
    def __init__(
        self,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        cross_region_references: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
        notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
        property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
        stack_name: typing.Optional[builtins.str] = None,
        suppress_template_indentation: typing.Optional[builtins.bool] = None,
        synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        key_version_retention_days: typing.Optional[jsii.Number] = None,
        key_versions_to_retain: typing.Optional[jsii.Number] = None,
        log_version_retention_days: typing.Optional[jsii.Number] = None,
        log_versions_to_retain: typing.Optional[jsii.Number] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        use_kms_encryption: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param analytics_reporting: Include runtime versioning information in this Stack. Default: ``analyticsReporting`` setting of containing ``App``, or value of 'aws:cdk:version-reporting' context key
        :param cross_region_references: Enable this flag to allow native cross region stack references. Enabling this will create a CloudFormation custom resource in both the producing stack and consuming stack in order to perform the export/import This feature is currently experimental Default: false
        :param description: A description of the stack. Default: - No description.
        :param env: The AWS environment (account/region) where this stack will be deployed. Set the ``region``/``account`` fields of ``env`` to either a concrete value to select the indicated environment (recommended for production stacks), or to the values of environment variables ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment depend on the AWS credentials/configuration that the CDK CLI is executed under (recommended for development stacks). If the ``Stack`` is instantiated inside a ``Stage``, any undefined ``region``/``account`` fields from ``env`` will default to the same field on the encompassing ``Stage``, if configured there. If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the Stack will be considered "*environment-agnostic*"". Environment-agnostic stacks can be deployed to any environment but may not be able to take advantage of all features of the CDK. For example, they will not be able to use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not automatically translate Service Principals to the right format based on the environment's AWS partition, and other such enhancements. Default: - The environment of the containing ``Stage`` if available, otherwise create the stack will be environment-agnostic.
        :param notification_arns: SNS Topic ARNs that will receive stack events. Default: - no notification arns.
        :param permissions_boundary: Options for applying a permissions boundary to all IAM Roles and Users created within this Stage. Default: - no permissions boundary is applied
        :param property_injectors: A list of IPropertyInjector attached to this Stack. Default: - no PropertyInjectors
        :param stack_name: Name to deploy the stack with. Default: - Derived from construct path.
        :param suppress_template_indentation: Enable this flag to suppress indentation in generated CloudFormation templates. If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation`` context key will be used. If that is not specified, then the default value ``false`` will be used. Default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        :param synthesizer: Synthesis method to use while deploying this stack. The Stack Synthesizer controls aspects of synthesis and deployment, like how assets are referenced and what IAM roles to use. For more information, see the README of the main CDK package. If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used. If that is not specified, ``DefaultStackSynthesizer`` is used if ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no other synthesizer is specified. Default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        :param tags: Tags that will be applied to the Stack. These tags are applied to the CloudFormation Stack itself. They will not appear in the CloudFormation template. However, at deployment time, CloudFormation will apply these tags to all resources in the stack that support tagging. You will not be able to exempt resources from tagging (using the ``excludeResourceTypes`` property of ``Tags.of(...).add()``) for tags applied in this way. Default: {}
        :param termination_protection: Whether to enable termination protection for this stack. Default: false
        :param bucket_name: (experimental) Name of the S3 bucket for ImmuKV storage. Default: - Auto-generated bucket name
        :param key_version_retention_days: (experimental) Number of days to retain old key object versions. Default: 365
        :param key_versions_to_retain: (experimental) Number of old key versions to retain per key. Default: 100
        :param log_version_retention_days: (experimental) Number of days to retain old log versions. Default: 365
        :param log_versions_to_retain: (experimental) Number of old log versions to retain. Default: 1000
        :param s3_prefix: (experimental) S3 prefix for all ImmuKV objects. Default: - No prefix (root of bucket)
        :param use_kms_encryption: (experimental) Enable KMS encryption instead of S3-managed encryption. Default: false

        :stability: experimental
        '''
        if isinstance(env, dict):
            env = _aws_cdk_ceddda9d.Environment(**env)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6876d8005d85845308f24f5375b249734faed84590190bd0f19dada533150362)
            check_type(argname="argument analytics_reporting", value=analytics_reporting, expected_type=type_hints["analytics_reporting"])
            check_type(argname="argument cross_region_references", value=cross_region_references, expected_type=type_hints["cross_region_references"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument env", value=env, expected_type=type_hints["env"])
            check_type(argname="argument notification_arns", value=notification_arns, expected_type=type_hints["notification_arns"])
            check_type(argname="argument permissions_boundary", value=permissions_boundary, expected_type=type_hints["permissions_boundary"])
            check_type(argname="argument property_injectors", value=property_injectors, expected_type=type_hints["property_injectors"])
            check_type(argname="argument stack_name", value=stack_name, expected_type=type_hints["stack_name"])
            check_type(argname="argument suppress_template_indentation", value=suppress_template_indentation, expected_type=type_hints["suppress_template_indentation"])
            check_type(argname="argument synthesizer", value=synthesizer, expected_type=type_hints["synthesizer"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection", value=termination_protection, expected_type=type_hints["termination_protection"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument key_version_retention_days", value=key_version_retention_days, expected_type=type_hints["key_version_retention_days"])
            check_type(argname="argument key_versions_to_retain", value=key_versions_to_retain, expected_type=type_hints["key_versions_to_retain"])
            check_type(argname="argument log_version_retention_days", value=log_version_retention_days, expected_type=type_hints["log_version_retention_days"])
            check_type(argname="argument log_versions_to_retain", value=log_versions_to_retain, expected_type=type_hints["log_versions_to_retain"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument use_kms_encryption", value=use_kms_encryption, expected_type=type_hints["use_kms_encryption"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if analytics_reporting is not None:
            self._values["analytics_reporting"] = analytics_reporting
        if cross_region_references is not None:
            self._values["cross_region_references"] = cross_region_references
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if notification_arns is not None:
            self._values["notification_arns"] = notification_arns
        if permissions_boundary is not None:
            self._values["permissions_boundary"] = permissions_boundary
        if property_injectors is not None:
            self._values["property_injectors"] = property_injectors
        if stack_name is not None:
            self._values["stack_name"] = stack_name
        if suppress_template_indentation is not None:
            self._values["suppress_template_indentation"] = suppress_template_indentation
        if synthesizer is not None:
            self._values["synthesizer"] = synthesizer
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection is not None:
            self._values["termination_protection"] = termination_protection
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if key_version_retention_days is not None:
            self._values["key_version_retention_days"] = key_version_retention_days
        if key_versions_to_retain is not None:
            self._values["key_versions_to_retain"] = key_versions_to_retain
        if log_version_retention_days is not None:
            self._values["log_version_retention_days"] = log_version_retention_days
        if log_versions_to_retain is not None:
            self._values["log_versions_to_retain"] = log_versions_to_retain
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if use_kms_encryption is not None:
            self._values["use_kms_encryption"] = use_kms_encryption

    @builtins.property
    def analytics_reporting(self) -> typing.Optional[builtins.bool]:
        '''Include runtime versioning information in this Stack.

        :default:

        ``analyticsReporting`` setting of containing ``App``, or value of
        'aws:cdk:version-reporting' context key
        '''
        result = self._values.get("analytics_reporting")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cross_region_references(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to allow native cross region stack references.

        Enabling this will create a CloudFormation custom resource
        in both the producing stack and consuming stack in order to perform the export/import

        This feature is currently experimental

        :default: false
        '''
        result = self._values.get("cross_region_references")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the stack.

        :default: - No description.
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[_aws_cdk_ceddda9d.Environment]:
        '''The AWS environment (account/region) where this stack will be deployed.

        Set the ``region``/``account`` fields of ``env`` to either a concrete value to
        select the indicated environment (recommended for production stacks), or to
        the values of environment variables
        ``CDK_DEFAULT_REGION``/``CDK_DEFAULT_ACCOUNT`` to let the target environment
        depend on the AWS credentials/configuration that the CDK CLI is executed
        under (recommended for development stacks).

        If the ``Stack`` is instantiated inside a ``Stage``, any undefined
        ``region``/``account`` fields from ``env`` will default to the same field on the
        encompassing ``Stage``, if configured there.

        If either ``region`` or ``account`` are not set nor inherited from ``Stage``, the
        Stack will be considered "*environment-agnostic*"". Environment-agnostic
        stacks can be deployed to any environment but may not be able to take
        advantage of all features of the CDK. For example, they will not be able to
        use environmental context lookups such as ``ec2.Vpc.fromLookup`` and will not
        automatically translate Service Principals to the right format based on the
        environment's AWS partition, and other such enhancements.

        :default:

        - The environment of the containing ``Stage`` if available,
        otherwise create the stack will be environment-agnostic.

        Example::

            // Use a concrete account and region to deploy this stack to:
            // `.account` and `.region` will simply return these values.
            new Stack(app, 'Stack1', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              },
            });
            
            // Use the CLI's current credentials to determine the target environment:
            // `.account` and `.region` will reflect the account+region the CLI
            // is configured to use (based on the user CLI credentials)
            new Stack(app, 'Stack2', {
              env: {
                account: process.env.CDK_DEFAULT_ACCOUNT,
                region: process.env.CDK_DEFAULT_REGION
              },
            });
            
            // Define multiple stacks stage associated with an environment
            const myStage = new Stage(app, 'MyStage', {
              env: {
                account: '123456789012',
                region: 'us-east-1'
              }
            });
            
            // both of these stacks will use the stage's account/region:
            // `.account` and `.region` will resolve to the concrete values as above
            new MyStack(myStage, 'Stack1');
            new YourStack(myStage, 'Stack2');
            
            // Define an environment-agnostic stack:
            // `.account` and `.region` will resolve to `{ "Ref": "AWS::AccountId" }` and `{ "Ref": "AWS::Region" }` respectively.
            // which will only resolve to actual values by CloudFormation during deployment.
            new MyStack(app, 'Stack1');
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Environment], result)

    @builtins.property
    def notification_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''SNS Topic ARNs that will receive stack events.

        :default: - no notification arns.
        '''
        result = self._values.get("notification_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def permissions_boundary(
        self,
    ) -> typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary]:
        '''Options for applying a permissions boundary to all IAM Roles and Users created within this Stage.

        :default: - no permissions boundary is applied
        '''
        result = self._values.get("permissions_boundary")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary], result)

    @builtins.property
    def property_injectors(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.IPropertyInjector]]:
        '''A list of IPropertyInjector attached to this Stack.

        :default: - no PropertyInjectors
        '''
        result = self._values.get("property_injectors")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.IPropertyInjector]], result)

    @builtins.property
    def stack_name(self) -> typing.Optional[builtins.str]:
        '''Name to deploy the stack with.

        :default: - Derived from construct path.
        '''
        result = self._values.get("stack_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def suppress_template_indentation(self) -> typing.Optional[builtins.bool]:
        '''Enable this flag to suppress indentation in generated CloudFormation templates.

        If not specified, the value of the ``@aws-cdk/core:suppressTemplateIndentation``
        context key will be used. If that is not specified, then the
        default value ``false`` will be used.

        :default: - the value of ``@aws-cdk/core:suppressTemplateIndentation``, or ``false`` if that is not set.
        '''
        result = self._values.get("suppress_template_indentation")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def synthesizer(self) -> typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer]:
        '''Synthesis method to use while deploying this stack.

        The Stack Synthesizer controls aspects of synthesis and deployment,
        like how assets are referenced and what IAM roles to use. For more
        information, see the README of the main CDK package.

        If not specified, the ``defaultStackSynthesizer`` from ``App`` will be used.
        If that is not specified, ``DefaultStackSynthesizer`` is used if
        ``@aws-cdk/core:newStyleStackSynthesis`` is set to ``true`` or the CDK major
        version is v2. In CDK v1 ``LegacyStackSynthesizer`` is the default if no
        other synthesizer is specified.

        :default: - The synthesizer specified on ``App``, or ``DefaultStackSynthesizer`` otherwise.
        '''
        result = self._values.get("synthesizer")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Tags that will be applied to the Stack.

        These tags are applied to the CloudFormation Stack itself. They will not
        appear in the CloudFormation template.

        However, at deployment time, CloudFormation will apply these tags to all
        resources in the stack that support tagging. You will not be able to exempt
        resources from tagging (using the ``excludeResourceTypes`` property of
        ``Tags.of(...).add()``) for tags applied in this way.

        :default: {}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def termination_protection(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable termination protection for this stack.

        :default: false
        '''
        result = self._values.get("termination_protection")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the S3 bucket for ImmuKV storage.

        :default: - Auto-generated bucket name

        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_version_retention_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of days to retain old key object versions.

        :default: 365

        :stability: experimental
        '''
        result = self._values.get("key_version_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def key_versions_to_retain(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of old key versions to retain per key.

        :default: 100

        :stability: experimental
        '''
        result = self._values.get("key_versions_to_retain")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_version_retention_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of days to retain old log versions.

        :default: 365

        :stability: experimental
        '''
        result = self._values.get("log_version_retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_versions_to_retain(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of old log versions to retain.

        :default: 1000

        :stability: experimental
        '''
        result = self._values.get("log_versions_to_retain")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 prefix for all ImmuKV objects.

        :default: - No prefix (root of bucket)

        :stability: experimental
        '''
        result = self._values.get("s3_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_kms_encryption(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Enable KMS encryption instead of S3-managed encryption.

        :default: false

        :stability: experimental
        '''
        result = self._values.get("use_kms_encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImmuKVStackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ImmuKVStack",
    "ImmuKVStackProps",
]

publication.publish()

def _typecheckingstub__ff501672c790221a5a3d3b7792489059affb4e766151422255b75be4eb3a6aaf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    key_version_retention_days: typing.Optional[jsii.Number] = None,
    key_versions_to_retain: typing.Optional[jsii.Number] = None,
    log_version_retention_days: typing.Optional[jsii.Number] = None,
    log_versions_to_retain: typing.Optional[jsii.Number] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    use_kms_encryption: typing.Optional[builtins.bool] = None,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6876d8005d85845308f24f5375b249734faed84590190bd0f19dada533150362(
    *,
    analytics_reporting: typing.Optional[builtins.bool] = None,
    cross_region_references: typing.Optional[builtins.bool] = None,
    description: typing.Optional[builtins.str] = None,
    env: typing.Optional[typing.Union[_aws_cdk_ceddda9d.Environment, typing.Dict[builtins.str, typing.Any]]] = None,
    notification_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_boundary: typing.Optional[_aws_cdk_ceddda9d.PermissionsBoundary] = None,
    property_injectors: typing.Optional[typing.Sequence[_aws_cdk_ceddda9d.IPropertyInjector]] = None,
    stack_name: typing.Optional[builtins.str] = None,
    suppress_template_indentation: typing.Optional[builtins.bool] = None,
    synthesizer: typing.Optional[_aws_cdk_ceddda9d.IStackSynthesizer] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    termination_protection: typing.Optional[builtins.bool] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    key_version_retention_days: typing.Optional[jsii.Number] = None,
    key_versions_to_retain: typing.Optional[jsii.Number] = None,
    log_version_retention_days: typing.Optional[jsii.Number] = None,
    log_versions_to_retain: typing.Optional[jsii.Number] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    use_kms_encryption: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
