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

from ..._jsii import *

import constructs as _constructs_77d1e7e8
from .. import IEnvironmentAware as _IEnvironmentAware_f39049ee


@jsii.interface(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.IOrganizationCentralizationRuleRef"
)
class IOrganizationCentralizationRuleRef(
    _constructs_77d1e7e8.IConstruct,
    _IEnvironmentAware_f39049ee,
    typing_extensions.Protocol,
):
    '''(experimental) Indicates that this resource can be referenced as a OrganizationCentralizationRule.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="organizationCentralizationRuleRef")
    def organization_centralization_rule_ref(
        self,
    ) -> "OrganizationCentralizationRuleReference":
        '''(experimental) A reference to a OrganizationCentralizationRule resource.

        :stability: experimental
        '''
        ...


class _IOrganizationCentralizationRuleRefProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_IEnvironmentAware_f39049ee), # type: ignore[misc]
):
    '''(experimental) Indicates that this resource can be referenced as a OrganizationCentralizationRule.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.interfaces.aws_observabilityadmin.IOrganizationCentralizationRuleRef"

    @builtins.property
    @jsii.member(jsii_name="organizationCentralizationRuleRef")
    def organization_centralization_rule_ref(
        self,
    ) -> "OrganizationCentralizationRuleReference":
        '''(experimental) A reference to a OrganizationCentralizationRule resource.

        :stability: experimental
        '''
        return typing.cast("OrganizationCentralizationRuleReference", jsii.get(self, "organizationCentralizationRuleRef"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganizationCentralizationRuleRef).__jsii_proxy_class__ = lambda : _IOrganizationCentralizationRuleRefProxy


@jsii.interface(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.IOrganizationTelemetryRuleRef"
)
class IOrganizationTelemetryRuleRef(
    _constructs_77d1e7e8.IConstruct,
    _IEnvironmentAware_f39049ee,
    typing_extensions.Protocol,
):
    '''(experimental) Indicates that this resource can be referenced as a OrganizationTelemetryRule.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="organizationTelemetryRuleRef")
    def organization_telemetry_rule_ref(self) -> "OrganizationTelemetryRuleReference":
        '''(experimental) A reference to a OrganizationTelemetryRule resource.

        :stability: experimental
        '''
        ...


class _IOrganizationTelemetryRuleRefProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_IEnvironmentAware_f39049ee), # type: ignore[misc]
):
    '''(experimental) Indicates that this resource can be referenced as a OrganizationTelemetryRule.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.interfaces.aws_observabilityadmin.IOrganizationTelemetryRuleRef"

    @builtins.property
    @jsii.member(jsii_name="organizationTelemetryRuleRef")
    def organization_telemetry_rule_ref(self) -> "OrganizationTelemetryRuleReference":
        '''(experimental) A reference to a OrganizationTelemetryRule resource.

        :stability: experimental
        '''
        return typing.cast("OrganizationTelemetryRuleReference", jsii.get(self, "organizationTelemetryRuleRef"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IOrganizationTelemetryRuleRef).__jsii_proxy_class__ = lambda : _IOrganizationTelemetryRuleRefProxy


@jsii.interface(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.ITelemetryRuleRef"
)
class ITelemetryRuleRef(
    _constructs_77d1e7e8.IConstruct,
    _IEnvironmentAware_f39049ee,
    typing_extensions.Protocol,
):
    '''(experimental) Indicates that this resource can be referenced as a TelemetryRule.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="telemetryRuleRef")
    def telemetry_rule_ref(self) -> "TelemetryRuleReference":
        '''(experimental) A reference to a TelemetryRule resource.

        :stability: experimental
        '''
        ...


class _ITelemetryRuleRefProxy(
    jsii.proxy_for(_constructs_77d1e7e8.IConstruct), # type: ignore[misc]
    jsii.proxy_for(_IEnvironmentAware_f39049ee), # type: ignore[misc]
):
    '''(experimental) Indicates that this resource can be referenced as a TelemetryRule.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "aws-cdk-lib.interfaces.aws_observabilityadmin.ITelemetryRuleRef"

    @builtins.property
    @jsii.member(jsii_name="telemetryRuleRef")
    def telemetry_rule_ref(self) -> "TelemetryRuleReference":
        '''(experimental) A reference to a TelemetryRule resource.

        :stability: experimental
        '''
        return typing.cast("TelemetryRuleReference", jsii.get(self, "telemetryRuleRef"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITelemetryRuleRef).__jsii_proxy_class__ = lambda : _ITelemetryRuleRefProxy


@jsii.data_type(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.OrganizationCentralizationRuleReference",
    jsii_struct_bases=[],
    name_mapping={"rule_arn": "ruleArn"},
)
class OrganizationCentralizationRuleReference:
    def __init__(self, *, rule_arn: builtins.str) -> None:
        '''A reference to a OrganizationCentralizationRule resource.

        :param rule_arn: The RuleArn of the OrganizationCentralizationRule resource.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.interfaces import aws_observabilityadmin as interfaces_aws_observabilityadmin
            
            organization_centralization_rule_reference = interfaces_aws_observabilityadmin.OrganizationCentralizationRuleReference(
                rule_arn="ruleArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__954ef56f547b852ec9d4a111054e5601faba2a807f7124bccca33ab6f2a56d71)
            check_type(argname="argument rule_arn", value=rule_arn, expected_type=type_hints["rule_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rule_arn": rule_arn,
        }

    @builtins.property
    def rule_arn(self) -> builtins.str:
        '''The RuleArn of the OrganizationCentralizationRule resource.'''
        result = self._values.get("rule_arn")
        assert result is not None, "Required property 'rule_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationCentralizationRuleReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.OrganizationTelemetryRuleReference",
    jsii_struct_bases=[],
    name_mapping={"rule_arn": "ruleArn"},
)
class OrganizationTelemetryRuleReference:
    def __init__(self, *, rule_arn: builtins.str) -> None:
        '''A reference to a OrganizationTelemetryRule resource.

        :param rule_arn: The RuleArn of the OrganizationTelemetryRule resource.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.interfaces import aws_observabilityadmin as interfaces_aws_observabilityadmin
            
            organization_telemetry_rule_reference = interfaces_aws_observabilityadmin.OrganizationTelemetryRuleReference(
                rule_arn="ruleArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbaa448311f6f304eaa3b8b6adb9dd50b4accec2ca25b614d9e0cbd75cd36503)
            check_type(argname="argument rule_arn", value=rule_arn, expected_type=type_hints["rule_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rule_arn": rule_arn,
        }

    @builtins.property
    def rule_arn(self) -> builtins.str:
        '''The RuleArn of the OrganizationTelemetryRule resource.'''
        result = self._values.get("rule_arn")
        assert result is not None, "Required property 'rule_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OrganizationTelemetryRuleReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="aws-cdk-lib.interfaces.aws_observabilityadmin.TelemetryRuleReference",
    jsii_struct_bases=[],
    name_mapping={"rule_arn": "ruleArn"},
)
class TelemetryRuleReference:
    def __init__(self, *, rule_arn: builtins.str) -> None:
        '''A reference to a TelemetryRule resource.

        :param rule_arn: The RuleArn of the TelemetryRule resource.

        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            from aws_cdk.interfaces import aws_observabilityadmin as interfaces_aws_observabilityadmin
            
            telemetry_rule_reference = interfaces_aws_observabilityadmin.TelemetryRuleReference(
                rule_arn="ruleArn"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f3442b866c7be36ef85439dc80d47ed5cfc8d0a761fa5260939a94726bf2f76)
            check_type(argname="argument rule_arn", value=rule_arn, expected_type=type_hints["rule_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "rule_arn": rule_arn,
        }

    @builtins.property
    def rule_arn(self) -> builtins.str:
        '''The RuleArn of the TelemetryRule resource.'''
        result = self._values.get("rule_arn")
        assert result is not None, "Required property 'rule_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TelemetryRuleReference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IOrganizationCentralizationRuleRef",
    "IOrganizationTelemetryRuleRef",
    "ITelemetryRuleRef",
    "OrganizationCentralizationRuleReference",
    "OrganizationTelemetryRuleReference",
    "TelemetryRuleReference",
]

publication.publish()

def _typecheckingstub__954ef56f547b852ec9d4a111054e5601faba2a807f7124bccca33ab6f2a56d71(
    *,
    rule_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbaa448311f6f304eaa3b8b6adb9dd50b4accec2ca25b614d9e0cbd75cd36503(
    *,
    rule_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3442b866c7be36ef85439dc80d47ed5cfc8d0a761fa5260939a94726bf2f76(
    *,
    rule_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IOrganizationCentralizationRuleRef, IOrganizationTelemetryRuleRef, ITelemetryRuleRef]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
