r'''
# `nomad_dynamic_host_volume`

Refer to the Terraform Registry for docs: [`nomad_dynamic_host_volume`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume).
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


class DynamicHostVolume(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolume",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume nomad_dynamic_host_volume}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeCapability", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        plugin_id: builtins.str,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        constraint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeConstraint", typing.Dict[builtins.str, typing.Any]]]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        node_id: typing.Optional[builtins.str] = None,
        node_pool: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume nomad_dynamic_host_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capability DynamicHostVolume#capability}
        :param name: Volume name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#name DynamicHostVolume#name}
        :param plugin_id: Plugin ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#plugin_id DynamicHostVolume#plugin_id}
        :param capacity_max: Requested maximum capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_max DynamicHostVolume#capacity_max}
        :param capacity_min: Requested minimum capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_min DynamicHostVolume#capacity_min}
        :param constraint: constraint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#constraint DynamicHostVolume#constraint}
        :param namespace: Volume namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#namespace DynamicHostVolume#namespace}
        :param node_id: Node ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_id DynamicHostVolume#node_id}
        :param node_pool: Node pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_pool DynamicHostVolume#node_pool}
        :param parameters: Parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#parameters DynamicHostVolume#parameters}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__329d653b0bb0629644c10c7a14891e37aff15cea01ac5bb70a6d57fbdd75f6dd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DynamicHostVolumeConfig(
            capability=capability,
            name=name,
            plugin_id=plugin_id,
            capacity_max=capacity_max,
            capacity_min=capacity_min,
            constraint=constraint,
            namespace=namespace,
            node_id=node_id,
            node_pool=node_pool,
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
        '''Generates CDKTF code for importing a DynamicHostVolume resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicHostVolume to import.
        :param import_from_id: The id of the existing DynamicHostVolume that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicHostVolume to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae1b5f43fdd7d4ab8f75d1d6c5619d5328af0b6f2dba91824425077179b68a23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCapability")
    def put_capability(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeCapability", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6341398a550fbadfc4cebeb27782d6c5c36a284ac179682aa1e542e3c9200bc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCapability", [value]))

    @jsii.member(jsii_name="putConstraint")
    def put_constraint(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeConstraint", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020a16493d6011bc0596e96ced826827dca407e5b1dd58c4f2e0476cdd46b0b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putConstraint", [value]))

    @jsii.member(jsii_name="resetCapacityMax")
    def reset_capacity_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMax", []))

    @jsii.member(jsii_name="resetCapacityMin")
    def reset_capacity_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMin", []))

    @jsii.member(jsii_name="resetConstraint")
    def reset_constraint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConstraint", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetNodeId")
    def reset_node_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeId", []))

    @jsii.member(jsii_name="resetNodePool")
    def reset_node_pool(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodePool", []))

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
    def capability(self) -> "DynamicHostVolumeCapabilityList":
        return typing.cast("DynamicHostVolumeCapabilityList", jsii.get(self, "capability"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacity"))

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
    def constraint(self) -> "DynamicHostVolumeConstraintList":
        return typing.cast("DynamicHostVolumeConstraintList", jsii.get(self, "constraint"))

    @builtins.property
    @jsii.member(jsii_name="hostPath")
    def host_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostPath"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="capabilityInput")
    def capability_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeCapability"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeCapability"]]], jsii.get(self, "capabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMaxInput")
    def capacity_max_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMinInput")
    def capacity_min_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMinInput"))

    @builtins.property
    @jsii.member(jsii_name="constraintInput")
    def constraint_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeConstraint"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeConstraint"]]], jsii.get(self, "constraintInput"))

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
    @jsii.member(jsii_name="nodePoolInput")
    def node_pool_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodePoolInput"))

    @builtins.property
    @jsii.member(jsii_name="parametersInput")
    def parameters_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "parametersInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginIdInput")
    def plugin_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pluginIdInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMax")
    def capacity_max(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacityMax"))

    @capacity_max.setter
    def capacity_max(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cb3a6f59ac95da31aef1230143f180199306825facd48ea2fe725d28e929ab3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="capacityMin")
    def capacity_min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacityMin"))

    @capacity_min.setter
    def capacity_min(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04fb1fe2eb27959de51591eb52bdab07f59b42bbbf34933828d503476c713d21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8758ee643afb8b644144f77502b98e8e69846f322e7f62a48eb82cfab0fb8fda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48ea66a2f21995bff8195c4e9f9d830f045836fc0a319402629e6e5940e3b4fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodeId")
    def node_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeId"))

    @node_id.setter
    def node_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1f95547fdd0bcab912f18ab8ef7e5546e3fe11141ea1b3b8ac539520ab5a25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nodePool")
    def node_pool(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodePool"))

    @node_pool.setter
    def node_pool(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5e5b0e2b77329d0cf21523c0db0f8d05f53cd209e0722a1a6973b0c903ad9f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodePool", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__081a3a31b8834d2e74d18f9d944693d29d8ff714d3941682497fd5a5019f7bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginId"))

    @plugin_id.setter
    def plugin_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5437ad858804642f8d25ac44e566114555819580d591d480583e619a9ced7f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeCapability",
    jsii_struct_bases=[],
    name_mapping={"access_mode": "accessMode", "attachment_mode": "attachmentMode"},
)
class DynamicHostVolumeCapability:
    def __init__(
        self,
        *,
        access_mode: builtins.str,
        attachment_mode: builtins.str,
    ) -> None:
        '''
        :param access_mode: An access mode available for the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#access_mode DynamicHostVolume#access_mode}
        :param attachment_mode: An attachment mode available for the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#attachment_mode DynamicHostVolume#attachment_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0fdb77db890fadccf11b252b1fadda522053efa49f92a0c95b3b60139bfebf0)
            check_type(argname="argument access_mode", value=access_mode, expected_type=type_hints["access_mode"])
            check_type(argname="argument attachment_mode", value=attachment_mode, expected_type=type_hints["attachment_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_mode": access_mode,
            "attachment_mode": attachment_mode,
        }

    @builtins.property
    def access_mode(self) -> builtins.str:
        '''An access mode available for the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#access_mode DynamicHostVolume#access_mode}
        '''
        result = self._values.get("access_mode")
        assert result is not None, "Required property 'access_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachment_mode(self) -> builtins.str:
        '''An attachment mode available for the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#attachment_mode DynamicHostVolume#attachment_mode}
        '''
        result = self._values.get("attachment_mode")
        assert result is not None, "Required property 'attachment_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeCapability(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamicHostVolumeCapabilityList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeCapabilityList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8dbe248108c36071346a6622aa4412470fdc77a985ff0cf9dc4e4a5170b89a4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DynamicHostVolumeCapabilityOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c2122cbaa568965fdcff14dcb7e99dce272af8f15da7ded4e487794e6813382)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DynamicHostVolumeCapabilityOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb87e82be22017ee32ce4d97de888c231a8e2cea971b0c648046293fba9f1cd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfd3baebdd3e32bc8c715b15488285503a05df83264bef59b29d1d8d3d3f45f0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9196f9e7f757238c18653682c4857de1742b512e4d9562bfb9794f3fb494546)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa18f4c31ed8aa41ad1596e9c92c709a41499deef63fc72a4900a68649286dfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DynamicHostVolumeCapabilityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeCapabilityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__84dd1931bd614ea7c3902875a63ef90013712945f0cafcd1c00575709a2a7e0a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31aba18e1e486be3d33e125e8a07ce691dd200bcf4cc2fc87fb0b01e91f94ac3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attachmentMode")
    def attachment_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachmentMode"))

    @attachment_mode.setter
    def attachment_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4745a4e8856aee39c6aef1e5fa94ce70a6f6bc4d5a1af7987317b971b95bb255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attachmentMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeCapability]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeCapability]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeCapability]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deeb858f0bd7861e0a08f084cfd56dfe40a198a38c6292dac8fca84fcef465be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeConfig",
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
        "name": "name",
        "plugin_id": "pluginId",
        "capacity_max": "capacityMax",
        "capacity_min": "capacityMin",
        "constraint": "constraint",
        "namespace": "namespace",
        "node_id": "nodeId",
        "node_pool": "nodePool",
        "parameters": "parameters",
    },
)
class DynamicHostVolumeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        plugin_id: builtins.str,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        constraint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DynamicHostVolumeConstraint", typing.Dict[builtins.str, typing.Any]]]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        node_id: typing.Optional[builtins.str] = None,
        node_pool: typing.Optional[builtins.str] = None,
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
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capability DynamicHostVolume#capability}
        :param name: Volume name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#name DynamicHostVolume#name}
        :param plugin_id: Plugin ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#plugin_id DynamicHostVolume#plugin_id}
        :param capacity_max: Requested maximum capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_max DynamicHostVolume#capacity_max}
        :param capacity_min: Requested minimum capacity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_min DynamicHostVolume#capacity_min}
        :param constraint: constraint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#constraint DynamicHostVolume#constraint}
        :param namespace: Volume namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#namespace DynamicHostVolume#namespace}
        :param node_id: Node ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_id DynamicHostVolume#node_id}
        :param node_pool: Node pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_pool DynamicHostVolume#node_pool}
        :param parameters: Parameters. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#parameters DynamicHostVolume#parameters}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeefd7432a94f2d2865271f2acd7f56c4ee7f76db57764ac915172e23373645b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument capability", value=capability, expected_type=type_hints["capability"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plugin_id", value=plugin_id, expected_type=type_hints["plugin_id"])
            check_type(argname="argument capacity_max", value=capacity_max, expected_type=type_hints["capacity_max"])
            check_type(argname="argument capacity_min", value=capacity_min, expected_type=type_hints["capacity_min"])
            check_type(argname="argument constraint", value=constraint, expected_type=type_hints["constraint"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument node_id", value=node_id, expected_type=type_hints["node_id"])
            check_type(argname="argument node_pool", value=node_pool, expected_type=type_hints["node_pool"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capability": capability,
            "name": name,
            "plugin_id": plugin_id,
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
        if capacity_max is not None:
            self._values["capacity_max"] = capacity_max
        if capacity_min is not None:
            self._values["capacity_min"] = capacity_min
        if constraint is not None:
            self._values["constraint"] = constraint
        if namespace is not None:
            self._values["namespace"] = namespace
        if node_id is not None:
            self._values["node_id"] = node_id
        if node_pool is not None:
            self._values["node_pool"] = node_pool
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
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]]:
        '''capability block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capability DynamicHostVolume#capability}
        '''
        result = self._values.get("capability")
        assert result is not None, "Required property 'capability' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Volume name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#name DynamicHostVolume#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_id(self) -> builtins.str:
        '''Plugin ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#plugin_id DynamicHostVolume#plugin_id}
        '''
        result = self._values.get("plugin_id")
        assert result is not None, "Required property 'plugin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity_max(self) -> typing.Optional[builtins.str]:
        '''Requested maximum capacity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_max DynamicHostVolume#capacity_max}
        '''
        result = self._values.get("capacity_max")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capacity_min(self) -> typing.Optional[builtins.str]:
        '''Requested minimum capacity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#capacity_min DynamicHostVolume#capacity_min}
        '''
        result = self._values.get("capacity_min")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def constraint(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeConstraint"]]]:
        '''constraint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#constraint DynamicHostVolume#constraint}
        '''
        result = self._values.get("constraint")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DynamicHostVolumeConstraint"]]], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Volume namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#namespace DynamicHostVolume#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_id(self) -> typing.Optional[builtins.str]:
        '''Node ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_id DynamicHostVolume#node_id}
        '''
        result = self._values.get("node_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_pool(self) -> typing.Optional[builtins.str]:
        '''Node pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#node_pool DynamicHostVolume#node_pool}
        '''
        result = self._values.get("node_pool")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Parameters.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#parameters DynamicHostVolume#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeConstraint",
    jsii_struct_bases=[],
    name_mapping={"attribute": "attribute", "operator": "operator", "value": "value"},
)
class DynamicHostVolumeConstraint:
    def __init__(
        self,
        *,
        attribute: builtins.str,
        operator: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param attribute: An attribute to check to constrain volume placement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#attribute DynamicHostVolume#attribute}
        :param operator: The operator to use for comparison. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#operator DynamicHostVolume#operator}
        :param value: The requested value of the attribute. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#value DynamicHostVolume#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7196924e0ec73bfd8ee13894956de7d0ba8ebee37a8bb005f5ecd3edf7cbbd7)
            check_type(argname="argument attribute", value=attribute, expected_type=type_hints["attribute"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "attribute": attribute,
        }
        if operator is not None:
            self._values["operator"] = operator
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def attribute(self) -> builtins.str:
        '''An attribute to check to constrain volume placement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#attribute DynamicHostVolume#attribute}
        '''
        result = self._values.get("attribute")
        assert result is not None, "Required property 'attribute' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''The operator to use for comparison.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#operator DynamicHostVolume#operator}
        '''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''The requested value of the attribute.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/dynamic_host_volume#value DynamicHostVolume#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicHostVolumeConstraint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DynamicHostVolumeConstraintList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeConstraintList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c06883611b2e866b70d88e363732ead3b591344f79d2c64da52f6e12ff03f22)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DynamicHostVolumeConstraintOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ac91e18be3d57bcdc6382ebacd54d1b4a028cafa53aaf51676e61c172dd9a5d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DynamicHostVolumeConstraintOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__207fccfda259f53c6ab5131e13cb286ce824d50cf77a20791186f1ad9c659592)
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
            type_hints = typing.get_type_hints(_typecheckingstub__37c12e90bf434bb06f518ffc8a15c93cc33543d5e4c771d46fea3f8e5346e7f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__caff05c1168f11fc614fa5c3e0ace227a7704ed0f9306b5066336caebfaf14fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeConstraint]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeConstraint]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeConstraint]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b26fc0953b06e0e54fc9a7088414b1296f838a585d027d9b2913982e96f7b3c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DynamicHostVolumeConstraintOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.dynamicHostVolume.DynamicHostVolumeConstraintOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__575e8fe57eaa2ec526cb12633c01a112dcae885986d4e765334b72485ea1bb72)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="attributeInput")
    def attribute_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "attributeInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="attribute")
    def attribute(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attribute"))

    @attribute.setter
    def attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a834f285c4a3d8a1d2ec6e1862f0d47f6e4e9d7981251d43c82302f58e68b3e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd4b792ed895d8da1a8a0be2920a4a37d9293692209801d1c5c221a30c0e8bee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7d28a96fb5288ebb0f1a06f9bab84b5c45e352369918027d09f500f2265c700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeConstraint]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeConstraint]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeConstraint]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81c255c0829add5214f1c35d27c5459cf08216f7f59fa46867352b8deddc255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DynamicHostVolume",
    "DynamicHostVolumeCapability",
    "DynamicHostVolumeCapabilityList",
    "DynamicHostVolumeCapabilityOutputReference",
    "DynamicHostVolumeConfig",
    "DynamicHostVolumeConstraint",
    "DynamicHostVolumeConstraintList",
    "DynamicHostVolumeConstraintOutputReference",
]

publication.publish()

def _typecheckingstub__329d653b0bb0629644c10c7a14891e37aff15cea01ac5bb70a6d57fbdd75f6dd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    plugin_id: builtins.str,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    constraint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeConstraint, typing.Dict[builtins.str, typing.Any]]]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    node_id: typing.Optional[builtins.str] = None,
    node_pool: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ae1b5f43fdd7d4ab8f75d1d6c5619d5328af0b6f2dba91824425077179b68a23(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6341398a550fbadfc4cebeb27782d6c5c36a284ac179682aa1e542e3c9200bc1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020a16493d6011bc0596e96ced826827dca407e5b1dd58c4f2e0476cdd46b0b6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeConstraint, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cb3a6f59ac95da31aef1230143f180199306825facd48ea2fe725d28e929ab3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04fb1fe2eb27959de51591eb52bdab07f59b42bbbf34933828d503476c713d21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8758ee643afb8b644144f77502b98e8e69846f322e7f62a48eb82cfab0fb8fda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ea66a2f21995bff8195c4e9f9d830f045836fc0a319402629e6e5940e3b4fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1f95547fdd0bcab912f18ab8ef7e5546e3fe11141ea1b3b8ac539520ab5a25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5e5b0e2b77329d0cf21523c0db0f8d05f53cd209e0722a1a6973b0c903ad9f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__081a3a31b8834d2e74d18f9d944693d29d8ff714d3941682497fd5a5019f7bbf(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5437ad858804642f8d25ac44e566114555819580d591d480583e619a9ced7f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fdb77db890fadccf11b252b1fadda522053efa49f92a0c95b3b60139bfebf0(
    *,
    access_mode: builtins.str,
    attachment_mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8dbe248108c36071346a6622aa4412470fdc77a985ff0cf9dc4e4a5170b89a4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c2122cbaa568965fdcff14dcb7e99dce272af8f15da7ded4e487794e6813382(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb87e82be22017ee32ce4d97de888c231a8e2cea971b0c648046293fba9f1cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfd3baebdd3e32bc8c715b15488285503a05df83264bef59b29d1d8d3d3f45f0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9196f9e7f757238c18653682c4857de1742b512e4d9562bfb9794f3fb494546(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa18f4c31ed8aa41ad1596e9c92c709a41499deef63fc72a4900a68649286dfa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeCapability]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84dd1931bd614ea7c3902875a63ef90013712945f0cafcd1c00575709a2a7e0a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31aba18e1e486be3d33e125e8a07ce691dd200bcf4cc2fc87fb0b01e91f94ac3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4745a4e8856aee39c6aef1e5fa94ce70a6f6bc4d5a1af7987317b971b95bb255(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deeb858f0bd7861e0a08f084cfd56dfe40a198a38c6292dac8fca84fcef465be(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeCapability]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeefd7432a94f2d2865271f2acd7f56c4ee7f76db57764ac915172e23373645b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    plugin_id: builtins.str,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    constraint: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DynamicHostVolumeConstraint, typing.Dict[builtins.str, typing.Any]]]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    node_id: typing.Optional[builtins.str] = None,
    node_pool: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7196924e0ec73bfd8ee13894956de7d0ba8ebee37a8bb005f5ecd3edf7cbbd7(
    *,
    attribute: builtins.str,
    operator: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c06883611b2e866b70d88e363732ead3b591344f79d2c64da52f6e12ff03f22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ac91e18be3d57bcdc6382ebacd54d1b4a028cafa53aaf51676e61c172dd9a5d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__207fccfda259f53c6ab5131e13cb286ce824d50cf77a20791186f1ad9c659592(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37c12e90bf434bb06f518ffc8a15c93cc33543d5e4c771d46fea3f8e5346e7f4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caff05c1168f11fc614fa5c3e0ace227a7704ed0f9306b5066336caebfaf14fd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b26fc0953b06e0e54fc9a7088414b1296f838a585d027d9b2913982e96f7b3c1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DynamicHostVolumeConstraint]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__575e8fe57eaa2ec526cb12633c01a112dcae885986d4e765334b72485ea1bb72(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a834f285c4a3d8a1d2ec6e1862f0d47f6e4e9d7981251d43c82302f58e68b3e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4b792ed895d8da1a8a0be2920a4a37d9293692209801d1c5c221a30c0e8bee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7d28a96fb5288ebb0f1a06f9bab84b5c45e352369918027d09f500f2265c700(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81c255c0829add5214f1c35d27c5459cf08216f7f59fa46867352b8deddc255(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DynamicHostVolumeConstraint]],
) -> None:
    """Type checking stubs"""
    pass
