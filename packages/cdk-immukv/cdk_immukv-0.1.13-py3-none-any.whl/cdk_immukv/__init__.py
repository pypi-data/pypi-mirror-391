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

### Basic Setup

#### TypeScript

```python
import * as cdk from 'aws-cdk-lib';
import { ImmuKV } from 'cdk-immukv';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MyStack');

new ImmuKV(stack, 'ImmuKV', {
  bucketName: 'my-immukv-bucket',
  s3Prefix: 'myapp/',
});
```

#### Python

```python
import aws_cdk as cdk
from cdk_immukv import ImmuKV

app = cdk.App()
stack = cdk.Stack(app, "MyStack")

ImmuKV(stack, "ImmuKV",
    bucket_name="my-immukv-bucket",
    s3_prefix="myapp/",
)
```

### S3 Event Notifications

You can optionally configure S3 event notifications to trigger when log entries are created. This supports Lambda functions, SNS topics, and SQS queues.

All notification destinations can be configured using the `onLogEntryCreated` property. Destinations can be in the same stack or different stacks - the Construct pattern handles this cleanly.

#### TypeScript - Lambda Trigger

```python
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { ImmuKV } from 'cdk-immukv';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MyStack');

// Create a Lambda function
const processorFn = new lambda.Function(stack, 'LogProcessor', {
  runtime: lambda.Runtime.PYTHON_3_11,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda'),
});

// Configure ImmuKV to trigger the Lambda on log entry creation
new ImmuKV(stack, 'ImmuKV', {
  bucketName: 'my-immukv-bucket',
  onLogEntryCreated: new s3n.LambdaDestination(processorFn),
});
```

#### TypeScript - SNS Topic

```python
import * as cdk from 'aws-cdk-lib';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { ImmuKV } from 'cdk-immukv';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MyStack');

// Create SNS topic
const topic = new sns.Topic(stack, 'LogEntryTopic');

// Configure ImmuKV to publish to SNS on log entry creation
new ImmuKV(stack, 'ImmuKV', {
  bucketName: 'my-immukv-bucket',
  onLogEntryCreated: new s3n.SnsDestination(topic),
});
```

#### TypeScript - SQS Queue

```python
import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import { ImmuKV } from 'cdk-immukv';

const app = new cdk.App();
const stack = new cdk.Stack(app, 'MyStack');

// Create SQS queue
const queue = new sqs.Queue(stack, 'LogEntryQueue');

// Configure ImmuKV to send to SQS on log entry creation
new ImmuKV(stack, 'ImmuKV', {
  bucketName: 'my-immukv-bucket',
  onLogEntryCreated: new s3n.SqsDestination(queue),
});
```

#### Python - Lambda Trigger

```python
import aws_cdk as cdk
from aws_cdk import aws_lambda as lambda_
from aws_cdk.aws_s3_notifications import LambdaDestination
from cdk_immukv import ImmuKV

app = cdk.App()
stack = cdk.Stack(app, "MyStack")

# Create Lambda function
processor_fn = lambda_.Function(stack, "LogProcessor",
    runtime=lambda_.Runtime.PYTHON_3_11,
    handler="index.handler",
    code=lambda_.Code.from_asset("lambda"),
)

# Configure ImmuKV with Lambda trigger
ImmuKV(stack, "ImmuKV",
    bucket_name="my-immukv-bucket",
    on_log_entry_created=LambdaDestination(processor_fn),
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


class ImmuKV(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-immukv.ImmuKV",
):
    '''(experimental) AWS CDK Construct for ImmuKV infrastructure.

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
        key_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        key_versions_to_retain: typing.Optional[jsii.Number] = None,
        log_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_versions_to_retain: typing.Optional[jsii.Number] = None,
        on_log_entry_created: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        use_kms_encryption: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param bucket_name: (experimental) Name of the S3 bucket for ImmuKV storage. Default: - Auto-generated bucket name
        :param key_version_retention: (experimental) Duration to retain old key object versions. If specified, old key versions will be deleted after this duration. Must be expressible in whole days (e.g., Duration.days(180)). Can be used independently or combined with keyVersionsToRetain. Default: undefined - No time-based deletion (keep forever)
        :param key_versions_to_retain: (experimental) Number of old key versions to retain per key. If specified, only this many old versions will be kept per key. Can be used independently or combined with keyVersionRetentionDays. Default: undefined - No count-based deletion (keep all versions)
        :param log_version_retention: (experimental) Duration to retain old log versions. If specified, old log versions will be deleted after this duration. Must be expressible in whole days (e.g., Duration.days(365)). Can be used independently or combined with logVersionsToRetain. Default: undefined - No time-based deletion (keep forever)
        :param log_versions_to_retain: (experimental) Number of old log versions to retain. If specified, only this many old log versions will be kept. Can be used independently or combined with logVersionRetentionDays. Default: undefined - No count-based deletion (keep all versions)
        :param on_log_entry_created: (experimental) Optional notification destination to trigger when log entries are created. Supports Lambda functions, SNS topics, and SQS queues. Example with Lambda:: import * as s3n from 'aws-cdk-lib/aws-s3-notifications'; new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.LambdaDestination(myFunction) }); Example with SNS:: new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.SnsDestination(myTopic) }); Example with SQS:: new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.SqsDestination(myQueue) }); Default: - No event notification configured
        :param s3_prefix: (experimental) S3 prefix for all ImmuKV objects. Controls where ImmuKV stores its data within the S3 bucket: - Empty string or undefined: Files stored at bucket root (e.g., ``_log.json``, ``keys/mykey.json``) - Without trailing slash (e.g., ``myapp``): Flat prefix (e.g., ``myapp_log.json``, ``myappkeys/mykey.json``) - With trailing slash (e.g., ``myapp/``): Directory-style prefix (e.g., ``myapp/_log.json``, ``myapp/keys/mykey.json``) Note: S3 event notifications use prefix matching, so the filter will match any object starting with ``${s3Prefix}_log.json`` (e.g., ``_log.json``, ``_log.json.backup``, etc.). This is intentional behavior. Default: - No prefix (root of bucket)
        :param use_kms_encryption: (experimental) Enable KMS encryption instead of S3-managed encryption. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf89bf43b11632d41df9085531c36079dbf8b6c7b0e05db6941b2fedec39190f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ImmuKVProps(
            bucket_name=bucket_name,
            key_version_retention=key_version_retention,
            key_versions_to_retain=key_versions_to_retain,
            log_version_retention=log_version_retention,
            log_versions_to_retain=log_versions_to_retain,
            on_log_entry_created=on_log_entry_created,
            s3_prefix=s3_prefix,
            use_kms_encryption=use_kms_encryption,
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
    jsii_type="cdk-immukv.ImmuKVProps",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "key_version_retention": "keyVersionRetention",
        "key_versions_to_retain": "keyVersionsToRetain",
        "log_version_retention": "logVersionRetention",
        "log_versions_to_retain": "logVersionsToRetain",
        "on_log_entry_created": "onLogEntryCreated",
        "s3_prefix": "s3Prefix",
        "use_kms_encryption": "useKmsEncryption",
    },
)
class ImmuKVProps:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        key_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        key_versions_to_retain: typing.Optional[jsii.Number] = None,
        log_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        log_versions_to_retain: typing.Optional[jsii.Number] = None,
        on_log_entry_created: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination] = None,
        s3_prefix: typing.Optional[builtins.str] = None,
        use_kms_encryption: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param bucket_name: (experimental) Name of the S3 bucket for ImmuKV storage. Default: - Auto-generated bucket name
        :param key_version_retention: (experimental) Duration to retain old key object versions. If specified, old key versions will be deleted after this duration. Must be expressible in whole days (e.g., Duration.days(180)). Can be used independently or combined with keyVersionsToRetain. Default: undefined - No time-based deletion (keep forever)
        :param key_versions_to_retain: (experimental) Number of old key versions to retain per key. If specified, only this many old versions will be kept per key. Can be used independently or combined with keyVersionRetentionDays. Default: undefined - No count-based deletion (keep all versions)
        :param log_version_retention: (experimental) Duration to retain old log versions. If specified, old log versions will be deleted after this duration. Must be expressible in whole days (e.g., Duration.days(365)). Can be used independently or combined with logVersionsToRetain. Default: undefined - No time-based deletion (keep forever)
        :param log_versions_to_retain: (experimental) Number of old log versions to retain. If specified, only this many old log versions will be kept. Can be used independently or combined with logVersionRetentionDays. Default: undefined - No count-based deletion (keep all versions)
        :param on_log_entry_created: (experimental) Optional notification destination to trigger when log entries are created. Supports Lambda functions, SNS topics, and SQS queues. Example with Lambda:: import * as s3n from 'aws-cdk-lib/aws-s3-notifications'; new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.LambdaDestination(myFunction) }); Example with SNS:: new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.SnsDestination(myTopic) }); Example with SQS:: new ImmuKV(this, 'ImmuKV', { onLogEntryCreated: new s3n.SqsDestination(myQueue) }); Default: - No event notification configured
        :param s3_prefix: (experimental) S3 prefix for all ImmuKV objects. Controls where ImmuKV stores its data within the S3 bucket: - Empty string or undefined: Files stored at bucket root (e.g., ``_log.json``, ``keys/mykey.json``) - Without trailing slash (e.g., ``myapp``): Flat prefix (e.g., ``myapp_log.json``, ``myappkeys/mykey.json``) - With trailing slash (e.g., ``myapp/``): Directory-style prefix (e.g., ``myapp/_log.json``, ``myapp/keys/mykey.json``) Note: S3 event notifications use prefix matching, so the filter will match any object starting with ``${s3Prefix}_log.json`` (e.g., ``_log.json``, ``_log.json.backup``, etc.). This is intentional behavior. Default: - No prefix (root of bucket)
        :param use_kms_encryption: (experimental) Enable KMS encryption instead of S3-managed encryption. Default: false

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f38ba88d5eb7c35a08092e7656a1247dfe38e78f3d61072f111badd15889223)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument key_version_retention", value=key_version_retention, expected_type=type_hints["key_version_retention"])
            check_type(argname="argument key_versions_to_retain", value=key_versions_to_retain, expected_type=type_hints["key_versions_to_retain"])
            check_type(argname="argument log_version_retention", value=log_version_retention, expected_type=type_hints["log_version_retention"])
            check_type(argname="argument log_versions_to_retain", value=log_versions_to_retain, expected_type=type_hints["log_versions_to_retain"])
            check_type(argname="argument on_log_entry_created", value=on_log_entry_created, expected_type=type_hints["on_log_entry_created"])
            check_type(argname="argument s3_prefix", value=s3_prefix, expected_type=type_hints["s3_prefix"])
            check_type(argname="argument use_kms_encryption", value=use_kms_encryption, expected_type=type_hints["use_kms_encryption"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if key_version_retention is not None:
            self._values["key_version_retention"] = key_version_retention
        if key_versions_to_retain is not None:
            self._values["key_versions_to_retain"] = key_versions_to_retain
        if log_version_retention is not None:
            self._values["log_version_retention"] = log_version_retention
        if log_versions_to_retain is not None:
            self._values["log_versions_to_retain"] = log_versions_to_retain
        if on_log_entry_created is not None:
            self._values["on_log_entry_created"] = on_log_entry_created
        if s3_prefix is not None:
            self._values["s3_prefix"] = s3_prefix
        if use_kms_encryption is not None:
            self._values["use_kms_encryption"] = use_kms_encryption

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Name of the S3 bucket for ImmuKV storage.

        :default: - Auto-generated bucket name

        :stability: experimental
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_version_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Duration to retain old key object versions.

        If specified, old key versions will be deleted after this duration.
        Must be expressible in whole days (e.g., Duration.days(180)).
        Can be used independently or combined with keyVersionsToRetain.

        :default: undefined - No time-based deletion (keep forever)

        :stability: experimental
        '''
        result = self._values.get("key_version_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def key_versions_to_retain(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of old key versions to retain per key.

        If specified, only this many old versions will be kept per key.
        Can be used independently or combined with keyVersionRetentionDays.

        :default: undefined - No count-based deletion (keep all versions)

        :stability: experimental
        '''
        result = self._values.get("key_versions_to_retain")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_version_retention(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Duration to retain old log versions.

        If specified, old log versions will be deleted after this duration.
        Must be expressible in whole days (e.g., Duration.days(365)).
        Can be used independently or combined with logVersionsToRetain.

        :default: undefined - No time-based deletion (keep forever)

        :stability: experimental
        '''
        result = self._values.get("log_version_retention")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def log_versions_to_retain(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Number of old log versions to retain.

        If specified, only this many old log versions will be kept.
        Can be used independently or combined with logVersionRetentionDays.

        :default: undefined - No count-based deletion (keep all versions)

        :stability: experimental
        '''
        result = self._values.get("log_versions_to_retain")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def on_log_entry_created(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination]:
        '''(experimental) Optional notification destination to trigger when log entries are created. Supports Lambda functions, SNS topics, and SQS queues.

        Example with Lambda::

           import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

           new ImmuKV(this, 'ImmuKV', {
             onLogEntryCreated: new s3n.LambdaDestination(myFunction)
           });

        Example with SNS::

           new ImmuKV(this, 'ImmuKV', {
             onLogEntryCreated: new s3n.SnsDestination(myTopic)
           });

        Example with SQS::

           new ImmuKV(this, 'ImmuKV', {
             onLogEntryCreated: new s3n.SqsDestination(myQueue)
           });

        :default: - No event notification configured

        :stability: experimental
        '''
        result = self._values.get("on_log_entry_created")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination], result)

    @builtins.property
    def s3_prefix(self) -> typing.Optional[builtins.str]:
        '''(experimental) S3 prefix for all ImmuKV objects.

        Controls where ImmuKV stores its data within the S3 bucket:

        - Empty string or undefined: Files stored at bucket root (e.g., ``_log.json``, ``keys/mykey.json``)
        - Without trailing slash (e.g., ``myapp``): Flat prefix (e.g., ``myapp_log.json``, ``myappkeys/mykey.json``)
        - With trailing slash (e.g., ``myapp/``): Directory-style prefix (e.g., ``myapp/_log.json``, ``myapp/keys/mykey.json``)

        Note: S3 event notifications use prefix matching, so the filter will match any object
        starting with ``${s3Prefix}_log.json`` (e.g., ``_log.json``, ``_log.json.backup``, etc.).
        This is intentional behavior.

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
        return "ImmuKVProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ImmuKV",
    "ImmuKVProps",
]

publication.publish()

def _typecheckingstub__cf89bf43b11632d41df9085531c36079dbf8b6c7b0e05db6941b2fedec39190f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    key_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    key_versions_to_retain: typing.Optional[jsii.Number] = None,
    log_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_versions_to_retain: typing.Optional[jsii.Number] = None,
    on_log_entry_created: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    use_kms_encryption: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f38ba88d5eb7c35a08092e7656a1247dfe38e78f3d61072f111badd15889223(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    key_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    key_versions_to_retain: typing.Optional[jsii.Number] = None,
    log_version_retention: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    log_versions_to_retain: typing.Optional[jsii.Number] = None,
    on_log_entry_created: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucketNotificationDestination] = None,
    s3_prefix: typing.Optional[builtins.str] = None,
    use_kms_encryption: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass
