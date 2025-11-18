r'''
# `nomad_dynamic_host_volume_registration`

Refer to the Terraform Registry for docs: [`nomad_dynamic_host_volume_registration`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DynamicHostVolumeRegistration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistration",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration nomad_dynamic_host_volume_registration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeRegistrationCapability", typing.Dict[builtins.str, typing.Any]]]],
        host_path: builtins.str,
        name: builtins.str,
        node_id: builtins.str,
        capacity: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration nomad_dynamic_host_volume_registration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capability DynamicHostVolumeRegistration#capability}
        :param host_path: Host path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#host_path DynamicHostVolumeRegistration#host_path}
        :param name: Volume name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#name DynamicHostVolumeRegistration#name}
        :param node_id: Node ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#node_id DynamicHostVolumeRegistration#node_id}
        :param capacity: Provisioned capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capacity DynamicHostVolumeRegistration#capacity}
        :param namespace: Volume namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#namespace DynamicHostVolumeRegistration#namespace}
        :param parameters: Parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#parameters DynamicHostVolumeRegistration#parameters}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9678b244b9e2ef9361400aff6052c96a0964438dece7d1842455b4d5a93a355)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DynamicHostVolumeRegistrationConfig(
            capability=capability,
            host_path=host_path,
            name=name,
            node_id=node_id,
            capacity=capacity,
            namespace=namespace,
            parameters=parameters,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DynamicHostVolumeRegistration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicHostVolumeRegistration to import.
        :param import_from_id: The id of the existing DynamicHostVolumeRegistration that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicHostVolumeRegistration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9246115e1048d6088d68c14311b0c5121f236cd216f896de89bc9f85c6a86958)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCapability")
    def put_capability(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeRegistrationCapability", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b57630514b50c3a1d330ddb82bff0d399549bb0626d04f10ec3da70e5a689b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCapability", [value]))

    @jsii.member(jsii_name="resetCapacity")
    def reset_capacity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacity", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="capability")
    def capability(self) -> "DynamicHostVolumeRegistrationCapabilityList":
        return typing.cast("DynamicHostVolumeRegistrationCapabilityList", jsii.get(self, "capability"))

    @builtins.property
    @jsii.member(jsii_name="capacityBytes")
    def capacity_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacityBytes"))

    @builtins.property
    @jsii.member(jsii_name="capacityMaxBytes")
    def capacity_max_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacityMaxBytes"))

    @builtins.property
    @jsii.member(jsii_name="capacityMinBytes")
    def capacity_min_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacityMinBytes"))

    @builtins.property
    @jsii.member(jsii_name="constraint")
    def constraint(self) -> "DynamicHostVolumeRegistrationConstraintList":
        return typing.cast("DynamicHostVolumeRegistrationConstraintList", jsii.get(self, "constraint"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="nodePool")
    def node_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodePool"))

    @builtins.property
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginId"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="capabilityInput")
    def capability_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeRegistrationCapability"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeRegistrationCapability"]]], jsii.get(self, "capabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityInput")
    def capacity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityInput"))

    @builtins.property
    @jsii.member(jsii_name="hostPathInput")
    def host_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostPathInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeIdInput")
    def node_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))

    @capacity.setter
    def capacity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73bfae3f55a93d58399734db572e3b5c0a286bd98d97134743377fc553d61c99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostPath")
    def host_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostPath"))

    @host_path.setter
    def host_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f9ef846ac49356fcc4cf45786470528902fcff5fd889ebfa76514f4d343617c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cf2e3f79baeb644d7425e75274189b551bd39a2b7f9c8ed5bfd5ad516d4af54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba6f290692db385bea04892d9711644aede011a07b1e838694280a985916189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @node_id.setter
    def node_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3722b7b906d127eb95b7e4a42bc80c744ebb277ec087e015ff11d7aeb0e02c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e599bb2faaf5ae029cd44f42a439e264ffd47c817d9b81cf3e2dcb11d6784b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationCapability",
    jsii_struct_bases=[],
    name_mapping={"access_mode": "accessMode", "attachment_mode": "attachmentMode"},
)
class DynamicHostVolumeRegistrationCapability:
    def __init__(
        self,
        *,
        access_mode: builtins.str,
        attachment_mode: builtins.str,
    ) -> None:
        '''
        :param access_mode: An access mode available for the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#access_mode DynamicHostVolumeRegistration#access_mode}
        :param attachment_mode: An attachment mode available for the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#attachment_mode DynamicHostVolumeRegistration#attachment_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a34057905b18494d31175653a100d090751831ff967927be7d0207dfe70b0ad)
            check_type(argname="argument access_mode", value=access_mode, expected_type=type_hints["access_mode"])
            check_type(argname="argument attachment_mode", value=attachment_mode, expected_type=type_hints["attachment_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_mode": access_mode,
            "attachment_mode": attachment_mode,
        }

    @builtins.property
    def access_mode(self) -> builtins.str:
        '''An access mode available for the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#access_mode DynamicHostVolumeRegistration#access_mode}
        '''
        result = self._values.get("access_mode")
        assert result is not None, "Required property 'access_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachment_mode(self) -> builtins.str:
        '''An attachment mode available for the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#attachment_mode DynamicHostVolumeRegistration#attachment_mode}
        '''
        result = self._values.get("attachment_mode")
        assert result is not None, "Required property 'attachment_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeRegistrationCapability(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamicHostVolumeRegistrationCapabilityList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationCapabilityList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c66ce92afd1e9f372234897707e4b851d669db7d524abc0430d54ad4e8b253c4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DynamicHostVolumeRegistrationCapabilityOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d57d83ebd16ec065a1aefc851a5285deff4552c0fd7949899aa4d0bb28a080b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DynamicHostVolumeRegistrationCapabilityOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7746d6280b209f0b1ba962ea5b5c00b225762a3ad815fa6a42f395d9216221e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__089df7b3b084112964f45fa17d3f54e6bc52729cd45a1b872b56bd5ab59818ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27e1dca0f057f3dc53a20028126bc8d802c4acd2b4b0769f35d850c9ef671075)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7429e432802f83a253c2f611a5954094479e8e776875aa48ee35fbdc08392662)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DynamicHostVolumeRegistrationCapabilityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationCapabilityOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8b1326e76d40d16e533d197cc97479c94f41f4905e2db94abaa9e84f58c060d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="accessModeInput")
    def access_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessModeInput"))

    @builtins.property
    @jsii.member(jsii_name="attachmentModeInput")
    def attachment_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attachmentModeInput"))

    @builtins.property
    @jsii.member(jsii_name="accessMode")
    def access_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessMode"))

    @access_mode.setter
    def access_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a7fbd3f936257a5aae29e9c3b5558802465b323f9073659d37e7215916d9ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attachmentMode")
    def attachment_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachmentMode"))

    @attachment_mode.setter
    def attachment_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d266bb49992e3dde3b37699a1a113eed9addcfad1bdc9d7bb24454c8f495bf01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attachmentMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeRegistrationCapability]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeRegistrationCapability]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeRegistrationCapability]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fbfe7f050e6df6a5002b94a271c661a5a5d8afa86318b4a2543e98bb3e46cd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "capability": "capability",
        "host_path": "hostPath",
        "name": "name",
        "node_id": "nodeId",
        "capacity": "capacity",
        "namespace": "namespace",
        "parameters": "parameters",
    },
)
class DynamicHostVolumeRegistrationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]],
        host_path: builtins.str,
        name: builtins.str,
        node_id: builtins.str,
        capacity: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capability DynamicHostVolumeRegistration#capability}
        :param host_path: Host path. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#host_path DynamicHostVolumeRegistration#host_path}
        :param name: Volume name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#name DynamicHostVolumeRegistration#name}
        :param node_id: Node ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#node_id DynamicHostVolumeRegistration#node_id}
        :param capacity: Provisioned capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capacity DynamicHostVolumeRegistration#capacity}
        :param namespace: Volume namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#namespace DynamicHostVolumeRegistration#namespace}
        :param parameters: Parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#parameters DynamicHostVolumeRegistration#parameters}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c606e371b2c932b1ef0bef2b3e5ecfa94c900b889925a99e14eb5d42b53d7cbd)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument capability", value=capability, expected_type=type_hints["capability"])
            check_type(argname="argument host_path", value=host_path, expected_type=type_hints["host_path"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument node_id", value=node_id, expected_type=type_hints["node_id"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capability": capability,
            "host_path": host_path,
            "name": name,
            "node_id": node_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if capacity is not None:
            self._values["capacity"] = capacity
        if namespace is not None:
            self._values["namespace"] = namespace
        if parameters is not None:
            self._values["parameters"] = parameters

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def capability(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]]:
        '''capability block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capability DynamicHostVolumeRegistration#capability}
        '''
        result = self._values.get("capability")
        assert result is not None, "Required property 'capability' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]], result)

    @builtins.property
    def host_path(self) -> builtins.str:
        '''Host path.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#host_path DynamicHostVolumeRegistration#host_path}
        '''
        result = self._values.get("host_path")
        assert result is not None, "Required property 'host_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Volume name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#name DynamicHostVolumeRegistration#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def node_id(self) -> builtins.str:
        '''Node ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#node_id DynamicHostVolumeRegistration#node_id}
        '''
        result = self._values.get("node_id")
        assert result is not None, "Required property 'node_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity(self) -> typing.Optional[builtins.str]:
        '''Provisioned capacity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#capacity DynamicHostVolumeRegistration#capacity}
        '''
        result = self._values.get("capacity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Volume namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#namespace DynamicHostVolumeRegistration#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume_registration#parameters DynamicHostVolumeRegistration#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeRegistrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationConstraint",
    jsii_struct_bases=[],
    name_mapping={},
)
class DynamicHostVolumeRegistrationConstraint:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeRegistrationConstraint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamicHostVolumeRegistrationConstraintList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationConstraintList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3e45081ee5e8d4242f4ea338c6fcfcbb016c96b0caea9965b3c7404349de4c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DynamicHostVolumeRegistrationConstraintOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03590b4ec0fe7a39a27effd9d29a2ede30deb039096cfd47efa4971acae336a1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DynamicHostVolumeRegistrationConstraintOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da3d5c15f04d13687b22955dde73ccd1a608ffa404259108d7d47e5761b9b1a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__247ca70f5c9ec41efd4a0ed026781053c8bc303fc752090207e579b2af70b501)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57dafaf59893a507ea5425a16be65fb9c63dc790b56cafdfda2a59497bff52a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DynamicHostVolumeRegistrationConstraintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolumeRegistration.DynamicHostVolumeRegistrationConstraintOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde68386a3a3d1dda3c73018b89a93ab3c6cfd796451e414f43cc317affd2362)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="attribute")
    def attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attribute"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DynamicHostVolumeRegistrationConstraint]:
        return typing.cast(typing.Optional[DynamicHostVolumeRegistrationConstraint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DynamicHostVolumeRegistrationConstraint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e74cd3099f70714041182c23ecc6deeaa0119b78401761c224db4f558c20718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DynamicHostVolumeRegistration",
    "DynamicHostVolumeRegistrationCapability",
    "DynamicHostVolumeRegistrationCapabilityList",
    "DynamicHostVolumeRegistrationCapabilityOutputReference",
    "DynamicHostVolumeRegistrationConfig",
    "DynamicHostVolumeRegistrationConstraint",
    "DynamicHostVolumeRegistrationConstraintList",
    "DynamicHostVolumeRegistrationConstraintOutputReference",
]

publication.publish()

def _typecheckingstub__d9678b244b9e2ef9361400aff6052c96a0964438dece7d1842455b4d5a93a355(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]],
    host_path: builtins.str,
    name: builtins.str,
    node_id: builtins.str,
    capacity: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9246115e1048d6088d68c14311b0c5121f236cd216f896de89bc9f85c6a86958(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b57630514b50c3a1d330ddb82bff0d399549bb0626d04f10ec3da70e5a689b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73bfae3f55a93d58399734db572e3b5c0a286bd98d97134743377fc553d61c99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f9ef846ac49356fcc4cf45786470528902fcff5fd889ebfa76514f4d343617c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cf2e3f79baeb644d7425e75274189b551bd39a2b7f9c8ed5bfd5ad516d4af54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba6f290692db385bea04892d9711644aede011a07b1e838694280a985916189(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3722b7b906d127eb95b7e4a42bc80c744ebb277ec087e015ff11d7aeb0e02c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e599bb2faaf5ae029cd44f42a439e264ffd47c817d9b81cf3e2dcb11d6784b4(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a34057905b18494d31175653a100d090751831ff967927be7d0207dfe70b0ad(
    *,
    access_mode: builtins.str,
    attachment_mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c66ce92afd1e9f372234897707e4b851d669db7d524abc0430d54ad4e8b253c4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d57d83ebd16ec065a1aefc851a5285deff4552c0fd7949899aa4d0bb28a080b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7746d6280b209f0b1ba962ea5b5c00b225762a3ad815fa6a42f395d9216221e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__089df7b3b084112964f45fa17d3f54e6bc52729cd45a1b872b56bd5ab59818ed(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27e1dca0f057f3dc53a20028126bc8d802c4acd2b4b0769f35d850c9ef671075(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7429e432802f83a253c2f611a5954094479e8e776875aa48ee35fbdc08392662(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeRegistrationCapability]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8b1326e76d40d16e533d197cc97479c94f41f4905e2db94abaa9e84f58c060d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a7fbd3f936257a5aae29e9c3b5558802465b323f9073659d37e7215916d9ef3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d266bb49992e3dde3b37699a1a113eed9addcfad1bdc9d7bb24454c8f495bf01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbfe7f050e6df6a5002b94a271c661a5a5d8afa86318b4a2543e98bb3e46cd6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeRegistrationCapability]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c606e371b2c932b1ef0bef2b3e5ecfa94c900b889925a99e14eb5d42b53d7cbd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]],
    host_path: builtins.str,
    name: builtins.str,
    node_id: builtins.str,
    capacity: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3e45081ee5e8d4242f4ea338c6fcfcbb016c96b0caea9965b3c7404349de4c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03590b4ec0fe7a39a27effd9d29a2ede30deb039096cfd47efa4971acae336a1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da3d5c15f04d13687b22955dde73ccd1a608ffa404259108d7d47e5761b9b1a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__247ca70f5c9ec41efd4a0ed026781053c8bc303fc752090207e579b2af70b501(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57dafaf59893a507ea5425a16be65fb9c63dc790b56cafdfda2a59497bff52a2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde68386a3a3d1dda3c73018b89a93ab3c6cfd796451e414f43cc317affd2362(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e74cd3099f70714041182c23ecc6deeaa0119b78401761c224db4f558c20718(
    value: typing.Optional[DynamicHostVolumeRegistrationConstraint],
) -> None:
    """Type checking stubs"""
    pass
