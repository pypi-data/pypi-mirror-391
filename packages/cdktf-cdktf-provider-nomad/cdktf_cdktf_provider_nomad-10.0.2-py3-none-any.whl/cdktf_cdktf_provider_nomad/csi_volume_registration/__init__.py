r'''
# `nomad_csi_volume_registration`

Refer to the Terraform Registry for docs: [`nomad_csi_volume_registration`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration).
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


class CsiVolumeRegistration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistration",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration nomad_csi_volume_registration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        external_id: builtins.str,
        name: builtins.str,
        plugin_id: builtins.str,
        volume_id: builtins.str,
        capability: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeRegistrationCapability", typing.Dict[builtins.str, typing.Any]]]]] = None,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        deregister_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional[typing.Union["CsiVolumeRegistrationMountOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional[typing.Union["CsiVolumeRegistrationTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        topology_request: typing.Optional[typing.Union["CsiVolumeRegistrationTopologyRequest", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration nomad_csi_volume_registration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param external_id: The ID of the physical volume from the storage provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#external_id CsiVolumeRegistration#external_id}
        :param name: The display name of the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#name CsiVolumeRegistration#name}
        :param plugin_id: The ID of the CSI plugin that manages this volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#plugin_id CsiVolumeRegistration#plugin_id}
        :param volume_id: The unique ID of the volume, how jobs will refer to the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#volume_id CsiVolumeRegistration#volume_id}
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capability CsiVolumeRegistration#capability}
        :param capacity_max: Defines how large the volume can be. The storage provider may return a volume that is smaller than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_max CsiVolumeRegistration#capacity_max}
        :param capacity_min: Defines how small the volume can be. The storage provider may return a volume that is larger than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_min CsiVolumeRegistration#capacity_min}
        :param context: An optional key-value map of strings passed directly to the CSI plugin to validate the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#context CsiVolumeRegistration#context}
        :param deregister_on_destroy: If true, the volume will be deregistered on destroy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#deregister_on_destroy CsiVolumeRegistration#deregister_on_destroy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#id CsiVolumeRegistration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_options CsiVolumeRegistration#mount_options}
        :param namespace: The namespace in which to create the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#namespace CsiVolumeRegistration#namespace}
        :param parameters: An optional key-value map of strings passed directly to the CSI plugin to configure the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#parameters CsiVolumeRegistration#parameters}
        :param secrets: An optional key-value map of strings used as credentials for publishing and unpublishing volumes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#secrets CsiVolumeRegistration#secrets}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#timeouts CsiVolumeRegistration#timeouts}
        :param topology_request: topology_request block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology_request CsiVolumeRegistration#topology_request}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1fc32c6d48b10b39a7d44cfeabe60287bef0657b7ffc8d1b3c4958b2456e244)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CsiVolumeRegistrationConfig(
            external_id=external_id,
            name=name,
            plugin_id=plugin_id,
            volume_id=volume_id,
            capability=capability,
            capacity_max=capacity_max,
            capacity_min=capacity_min,
            context=context,
            deregister_on_destroy=deregister_on_destroy,
            id=id,
            mount_options=mount_options,
            namespace=namespace,
            parameters=parameters,
            secrets=secrets,
            timeouts=timeouts,
            topology_request=topology_request,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a CsiVolumeRegistration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CsiVolumeRegistration to import.
        :param import_from_id: The id of the existing CsiVolumeRegistration that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CsiVolumeRegistration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1497f5385a839aefc539632f014d49a94fa78571153d15bec1282a500bb1003e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCapability")
    def put_capability(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeRegistrationCapability", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d3121b14554d7dd5a1c43dcdece0ff21379eadc612db88928c19e5aac8514a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCapability", [value]))

    @jsii.member(jsii_name="putMountOptions")
    def put_mount_options(
        self,
        *,
        fs_type: typing.Optional[builtins.str] = None,
        mount_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fs_type: The file system type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#fs_type CsiVolumeRegistration#fs_type}
        :param mount_flags: The flags passed to mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_flags CsiVolumeRegistration#mount_flags}
        '''
        value = CsiVolumeRegistrationMountOptions(
            fs_type=fs_type, mount_flags=mount_flags
        )

        return typing.cast(None, jsii.invoke(self, "putMountOptions", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#create CsiVolumeRegistration#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#delete CsiVolumeRegistration#delete}.
        '''
        value = CsiVolumeRegistrationTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTopologyRequest")
    def put_topology_request(
        self,
        *,
        required: typing.Optional[typing.Union["CsiVolumeRegistrationTopologyRequestRequired", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param required: required block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#required CsiVolumeRegistration#required}
        '''
        value = CsiVolumeRegistrationTopologyRequest(required=required)

        return typing.cast(None, jsii.invoke(self, "putTopologyRequest", [value]))

    @jsii.member(jsii_name="resetCapability")
    def reset_capability(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapability", []))

    @jsii.member(jsii_name="resetCapacityMax")
    def reset_capacity_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMax", []))

    @jsii.member(jsii_name="resetCapacityMin")
    def reset_capacity_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMin", []))

    @jsii.member(jsii_name="resetContext")
    def reset_context(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContext", []))

    @jsii.member(jsii_name="resetDeregisterOnDestroy")
    def reset_deregister_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeregisterOnDestroy", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMountOptions")
    def reset_mount_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountOptions", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetParameters")
    def reset_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParameters", []))

    @jsii.member(jsii_name="resetSecrets")
    def reset_secrets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecrets", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetTopologyRequest")
    def reset_topology_request(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopologyRequest", []))

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
    def capability(self) -> "CsiVolumeRegistrationCapabilityList":
        return typing.cast("CsiVolumeRegistrationCapabilityList", jsii.get(self, "capability"))

    @builtins.property
    @jsii.member(jsii_name="capacity")
    def capacity(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacity"))

    @builtins.property
    @jsii.member(jsii_name="capacityMaxBytes")
    def capacity_max_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacityMaxBytes"))

    @builtins.property
    @jsii.member(jsii_name="capacityMinBytes")
    def capacity_min_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "capacityMinBytes"))

    @builtins.property
    @jsii.member(jsii_name="controllerRequired")
    def controller_required(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "controllerRequired"))

    @builtins.property
    @jsii.member(jsii_name="controllersExpected")
    def controllers_expected(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "controllersExpected"))

    @builtins.property
    @jsii.member(jsii_name="controllersHealthy")
    def controllers_healthy(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "controllersHealthy"))

    @builtins.property
    @jsii.member(jsii_name="mountOptions")
    def mount_options(self) -> "CsiVolumeRegistrationMountOptionsOutputReference":
        return typing.cast("CsiVolumeRegistrationMountOptionsOutputReference", jsii.get(self, "mountOptions"))

    @builtins.property
    @jsii.member(jsii_name="nodesExpected")
    def nodes_expected(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nodesExpected"))

    @builtins.property
    @jsii.member(jsii_name="nodesHealthy")
    def nodes_healthy(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nodesHealthy"))

    @builtins.property
    @jsii.member(jsii_name="pluginProvider")
    def plugin_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginProvider"))

    @builtins.property
    @jsii.member(jsii_name="pluginProviderVersion")
    def plugin_provider_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginProviderVersion"))

    @builtins.property
    @jsii.member(jsii_name="schedulable")
    def schedulable(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "schedulable"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "CsiVolumeRegistrationTimeoutsOutputReference":
        return typing.cast("CsiVolumeRegistrationTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="topologies")
    def topologies(self) -> "CsiVolumeRegistrationTopologiesList":
        return typing.cast("CsiVolumeRegistrationTopologiesList", jsii.get(self, "topologies"))

    @builtins.property
    @jsii.member(jsii_name="topologyRequest")
    def topology_request(self) -> "CsiVolumeRegistrationTopologyRequestOutputReference":
        return typing.cast("CsiVolumeRegistrationTopologyRequestOutputReference", jsii.get(self, "topologyRequest"))

    @builtins.property
    @jsii.member(jsii_name="capabilityInput")
    def capability_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationCapability"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationCapability"]]], jsii.get(self, "capabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMaxInput")
    def capacity_max_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMinInput")
    def capacity_min_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMinInput"))

    @builtins.property
    @jsii.member(jsii_name="contextInput")
    def context_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "contextInput"))

    @builtins.property
    @jsii.member(jsii_name="deregisterOnDestroyInput")
    def deregister_on_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deregisterOnDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="externalIdInput")
    def external_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "externalIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mountOptionsInput")
    def mount_options_input(
        self,
    ) -> typing.Optional["CsiVolumeRegistrationMountOptions"]:
        return typing.cast(typing.Optional["CsiVolumeRegistrationMountOptions"], jsii.get(self, "mountOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

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
    @jsii.member(jsii_name="secretsInput")
    def secrets_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "secretsInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CsiVolumeRegistrationTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CsiVolumeRegistrationTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="topologyRequestInput")
    def topology_request_input(
        self,
    ) -> typing.Optional["CsiVolumeRegistrationTopologyRequest"]:
        return typing.cast(typing.Optional["CsiVolumeRegistrationTopologyRequest"], jsii.get(self, "topologyRequestInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeIdInput")
    def volume_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "volumeIdInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMax")
    def capacity_max(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacityMax"))

    @capacity_max.setter
    def capacity_max(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28051e9233070cfb3d41528b8213e2a02b29f7d6c8f2741730032f14359b5109)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="capacityMin")
    def capacity_min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacityMin"))

    @capacity_min.setter
    def capacity_min(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8670e2659b1afb2a475e736cb0c0a94932291b5a8feeb9e1019ca99646bd38c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="context")
    def context(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "context"))

    @context.setter
    def context(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b3bc613f4f594fe19076816f14f43be242a2de5ecce28735fcabf79367f7f72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "context", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deregisterOnDestroy")
    def deregister_on_destroy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deregisterOnDestroy"))

    @deregister_on_destroy.setter
    def deregister_on_destroy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8566779c2c8a33687f0b1072f98d5bf12f013e25289fb07b974764646f2f023)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deregisterOnDestroy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @external_id.setter
    def external_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1326d7732c5e59e10df656ab86e7708af82005cea9367b7edc51e7b81f0de3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "externalId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c074762749caa3e9d598ca80158927094a12893c34999bbe6ceb5ddd23feb61f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddcc228c09c14466c86d20db6c6145a93d4f62d0ac8ee4c4e7b4ebe9c49bc986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fe062201e445011412a6ea370d3ca741d7ea7e173fb7129cf47a27b6a8d0358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09a22a286244592c0b80f466260c886e0600a74efec10486286a52b85635c4b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginId"))

    @plugin_id.setter
    def plugin_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1e10b91f31536617d063e9664c0fb6c68af2ee0021b0f96ca9bf050eb32616b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "secrets"))

    @secrets.setter
    def secrets(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fac6949c82c7b16c53a3b9efa85aa41d53cb685e2a093847b7ec71856e5c4621)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secrets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @volume_id.setter
    def volume_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bb373f5cdba814d3395fe79e508cea7e86b00ec7f7369b5d438429cc89cd1dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationCapability",
    jsii_struct_bases=[],
    name_mapping={"access_mode": "accessMode", "attachment_mode": "attachmentMode"},
)
class CsiVolumeRegistrationCapability:
    def __init__(
        self,
        *,
        access_mode: builtins.str,
        attachment_mode: builtins.str,
    ) -> None:
        '''
        :param access_mode: Defines whether a volume should be available concurrently. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#access_mode CsiVolumeRegistration#access_mode}
        :param attachment_mode: The storage API that will be used by the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#attachment_mode CsiVolumeRegistration#attachment_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79cfc4d984323ae04a4bcfc1f67e66d114149e746ebbad0ef73a7647041d124)
            check_type(argname="argument access_mode", value=access_mode, expected_type=type_hints["access_mode"])
            check_type(argname="argument attachment_mode", value=attachment_mode, expected_type=type_hints["attachment_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_mode": access_mode,
            "attachment_mode": attachment_mode,
        }

    @builtins.property
    def access_mode(self) -> builtins.str:
        '''Defines whether a volume should be available concurrently.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#access_mode CsiVolumeRegistration#access_mode}
        '''
        result = self._values.get("access_mode")
        assert result is not None, "Required property 'access_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachment_mode(self) -> builtins.str:
        '''The storage API that will be used by the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#attachment_mode CsiVolumeRegistration#attachment_mode}
        '''
        result = self._values.get("attachment_mode")
        assert result is not None, "Required property 'attachment_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationCapability(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationCapabilityList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationCapabilityList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae7c8dbb7eee7ac216b09f2b59fd5d2ddd88a83330ea101add89abcb9c2a2bd2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CsiVolumeRegistrationCapabilityOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5af178759a27329b8aea210115c0ee21c56d04c629ce72aa20e07ae860d4d1bd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeRegistrationCapabilityOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c02f4d6712b51d580ba5d9292c1e4c56f31de7c631347029dbfd8a1076636a2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c8dc30ad90740548d3d8b56f314edaa9a17601716523418f3653130e73de568)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f804fea8f63f7349c437f5c91edd79eb612c79881a0815fe840e083f82bab456)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f8accb79ca68ff1a10139913a13de30d33d3fa625911bf7da2cb914148fe4bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CsiVolumeRegistrationCapabilityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationCapabilityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef0c7cfab3322a6ebcdbab18b3304fbfcaf1a81f5b91a4d34b3c3b57e589fcb8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee149a37cb91a493e83d1d2bb7aa94f7825269606d2d9902c6cbbc4fd4d1a12b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attachmentMode")
    def attachment_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachmentMode"))

    @attachment_mode.setter
    def attachment_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f50b8e586f6d73c0bcafe8a5449de2d8fdfb3fc815c369045154317f70a69c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attachmentMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationCapability]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationCapability]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationCapability]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67ee1b6f5cb004bef777c8fc290251ff0f58aa852577376709fe53421710498f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "external_id": "externalId",
        "name": "name",
        "plugin_id": "pluginId",
        "volume_id": "volumeId",
        "capability": "capability",
        "capacity_max": "capacityMax",
        "capacity_min": "capacityMin",
        "context": "context",
        "deregister_on_destroy": "deregisterOnDestroy",
        "id": "id",
        "mount_options": "mountOptions",
        "namespace": "namespace",
        "parameters": "parameters",
        "secrets": "secrets",
        "timeouts": "timeouts",
        "topology_request": "topologyRequest",
    },
)
class CsiVolumeRegistrationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        external_id: builtins.str,
        name: builtins.str,
        plugin_id: builtins.str,
        volume_id: builtins.str,
        capability: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]]] = None,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        deregister_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional[typing.Union["CsiVolumeRegistrationMountOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional[typing.Union["CsiVolumeRegistrationTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        topology_request: typing.Optional[typing.Union["CsiVolumeRegistrationTopologyRequest", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param external_id: The ID of the physical volume from the storage provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#external_id CsiVolumeRegistration#external_id}
        :param name: The display name of the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#name CsiVolumeRegistration#name}
        :param plugin_id: The ID of the CSI plugin that manages this volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#plugin_id CsiVolumeRegistration#plugin_id}
        :param volume_id: The unique ID of the volume, how jobs will refer to the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#volume_id CsiVolumeRegistration#volume_id}
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capability CsiVolumeRegistration#capability}
        :param capacity_max: Defines how large the volume can be. The storage provider may return a volume that is smaller than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_max CsiVolumeRegistration#capacity_max}
        :param capacity_min: Defines how small the volume can be. The storage provider may return a volume that is larger than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_min CsiVolumeRegistration#capacity_min}
        :param context: An optional key-value map of strings passed directly to the CSI plugin to validate the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#context CsiVolumeRegistration#context}
        :param deregister_on_destroy: If true, the volume will be deregistered on destroy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#deregister_on_destroy CsiVolumeRegistration#deregister_on_destroy}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#id CsiVolumeRegistration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_options CsiVolumeRegistration#mount_options}
        :param namespace: The namespace in which to create the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#namespace CsiVolumeRegistration#namespace}
        :param parameters: An optional key-value map of strings passed directly to the CSI plugin to configure the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#parameters CsiVolumeRegistration#parameters}
        :param secrets: An optional key-value map of strings used as credentials for publishing and unpublishing volumes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#secrets CsiVolumeRegistration#secrets}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#timeouts CsiVolumeRegistration#timeouts}
        :param topology_request: topology_request block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology_request CsiVolumeRegistration#topology_request}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(mount_options, dict):
            mount_options = CsiVolumeRegistrationMountOptions(**mount_options)
        if isinstance(timeouts, dict):
            timeouts = CsiVolumeRegistrationTimeouts(**timeouts)
        if isinstance(topology_request, dict):
            topology_request = CsiVolumeRegistrationTopologyRequest(**topology_request)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5df8053c0d92e2e2791451309c3efa46118d4035b446d7283a5fb3093b887b0b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument plugin_id", value=plugin_id, expected_type=type_hints["plugin_id"])
            check_type(argname="argument volume_id", value=volume_id, expected_type=type_hints["volume_id"])
            check_type(argname="argument capability", value=capability, expected_type=type_hints["capability"])
            check_type(argname="argument capacity_max", value=capacity_max, expected_type=type_hints["capacity_max"])
            check_type(argname="argument capacity_min", value=capacity_min, expected_type=type_hints["capacity_min"])
            check_type(argname="argument context", value=context, expected_type=type_hints["context"])
            check_type(argname="argument deregister_on_destroy", value=deregister_on_destroy, expected_type=type_hints["deregister_on_destroy"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument mount_options", value=mount_options, expected_type=type_hints["mount_options"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument topology_request", value=topology_request, expected_type=type_hints["topology_request"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "external_id": external_id,
            "name": name,
            "plugin_id": plugin_id,
            "volume_id": volume_id,
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
        if capability is not None:
            self._values["capability"] = capability
        if capacity_max is not None:
            self._values["capacity_max"] = capacity_max
        if capacity_min is not None:
            self._values["capacity_min"] = capacity_min
        if context is not None:
            self._values["context"] = context
        if deregister_on_destroy is not None:
            self._values["deregister_on_destroy"] = deregister_on_destroy
        if id is not None:
            self._values["id"] = id
        if mount_options is not None:
            self._values["mount_options"] = mount_options
        if namespace is not None:
            self._values["namespace"] = namespace
        if parameters is not None:
            self._values["parameters"] = parameters
        if secrets is not None:
            self._values["secrets"] = secrets
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if topology_request is not None:
            self._values["topology_request"] = topology_request

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
    def external_id(self) -> builtins.str:
        '''The ID of the physical volume from the storage provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#external_id CsiVolumeRegistration#external_id}
        '''
        result = self._values.get("external_id")
        assert result is not None, "Required property 'external_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The display name of the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#name CsiVolumeRegistration#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_id(self) -> builtins.str:
        '''The ID of the CSI plugin that manages this volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#plugin_id CsiVolumeRegistration#plugin_id}
        '''
        result = self._values.get("plugin_id")
        assert result is not None, "Required property 'plugin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def volume_id(self) -> builtins.str:
        '''The unique ID of the volume, how jobs will refer to the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#volume_id CsiVolumeRegistration#volume_id}
        '''
        result = self._values.get("volume_id")
        assert result is not None, "Required property 'volume_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capability(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]]:
        '''capability block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capability CsiVolumeRegistration#capability}
        '''
        result = self._values.get("capability")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]], result)

    @builtins.property
    def capacity_max(self) -> typing.Optional[builtins.str]:
        '''Defines how large the volume can be.

        The storage provider may return a volume that is smaller than this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_max CsiVolumeRegistration#capacity_max}
        '''
        result = self._values.get("capacity_max")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capacity_min(self) -> typing.Optional[builtins.str]:
        '''Defines how small the volume can be.

        The storage provider may return a volume that is larger than this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#capacity_min CsiVolumeRegistration#capacity_min}
        '''
        result = self._values.get("capacity_min")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def context(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional key-value map of strings passed directly to the CSI plugin to validate the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#context CsiVolumeRegistration#context}
        '''
        result = self._values.get("context")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def deregister_on_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If true, the volume will be deregistered on destroy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#deregister_on_destroy CsiVolumeRegistration#deregister_on_destroy}
        '''
        result = self._values.get("deregister_on_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#id CsiVolumeRegistration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_options(self) -> typing.Optional["CsiVolumeRegistrationMountOptions"]:
        '''mount_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_options CsiVolumeRegistration#mount_options}
        '''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional["CsiVolumeRegistrationMountOptions"], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The namespace in which to create the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#namespace CsiVolumeRegistration#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional key-value map of strings passed directly to the CSI plugin to configure the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#parameters CsiVolumeRegistration#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def secrets(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional key-value map of strings used as credentials for publishing and unpublishing volumes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#secrets CsiVolumeRegistration#secrets}
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CsiVolumeRegistrationTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#timeouts CsiVolumeRegistration#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CsiVolumeRegistrationTimeouts"], result)

    @builtins.property
    def topology_request(
        self,
    ) -> typing.Optional["CsiVolumeRegistrationTopologyRequest"]:
        '''topology_request block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology_request CsiVolumeRegistration#topology_request}
        '''
        result = self._values.get("topology_request")
        return typing.cast(typing.Optional["CsiVolumeRegistrationTopologyRequest"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationMountOptions",
    jsii_struct_bases=[],
    name_mapping={"fs_type": "fsType", "mount_flags": "mountFlags"},
)
class CsiVolumeRegistrationMountOptions:
    def __init__(
        self,
        *,
        fs_type: typing.Optional[builtins.str] = None,
        mount_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fs_type: The file system type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#fs_type CsiVolumeRegistration#fs_type}
        :param mount_flags: The flags passed to mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_flags CsiVolumeRegistration#mount_flags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4df372dae40b784ce05d6acd0ea366c125ce3e01ec9b2322206ebe3f950eedf)
            check_type(argname="argument fs_type", value=fs_type, expected_type=type_hints["fs_type"])
            check_type(argname="argument mount_flags", value=mount_flags, expected_type=type_hints["mount_flags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if fs_type is not None:
            self._values["fs_type"] = fs_type
        if mount_flags is not None:
            self._values["mount_flags"] = mount_flags

    @builtins.property
    def fs_type(self) -> typing.Optional[builtins.str]:
        '''The file system type.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#fs_type CsiVolumeRegistration#fs_type}
        '''
        result = self._values.get("fs_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The flags passed to mount.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#mount_flags CsiVolumeRegistration#mount_flags}
        '''
        result = self._values.get("mount_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationMountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationMountOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationMountOptionsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67d3dca47861a7c597f0a459e4e4e65209253067052931f366c6642843d176fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFsType")
    def reset_fs_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFsType", []))

    @jsii.member(jsii_name="resetMountFlags")
    def reset_mount_flags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMountFlags", []))

    @builtins.property
    @jsii.member(jsii_name="fsTypeInput")
    def fs_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fsTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="mountFlagsInput")
    def mount_flags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "mountFlagsInput"))

    @builtins.property
    @jsii.member(jsii_name="fsType")
    def fs_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fsType"))

    @fs_type.setter
    def fs_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1912711cdaef6f5935682c9847c9bcf9536eb785bb2d0e9e61f5f1c4a71e06c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fsType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mountFlags")
    def mount_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mountFlags"))

    @mount_flags.setter
    def mount_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a253a3b587beb59f2879eb69eaf8508a170b795666d0347be31bfc6324d2b433)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mountFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeRegistrationMountOptions]:
        return typing.cast(typing.Optional[CsiVolumeRegistrationMountOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeRegistrationMountOptions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4caf96ca0f39feb8833b4eb6e09ea529ffd572e3ca07c70b35bbb108234f96a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class CsiVolumeRegistrationTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#create CsiVolumeRegistration#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#delete CsiVolumeRegistration#delete}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df60350af4a198b7ee7523eb6838d760edb79ae6ab29ac89f6be17c3cb779a09)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#create CsiVolumeRegistration#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#delete CsiVolumeRegistration#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9469f85bcd74123d22172f74f53a534cc6cc6fc7d27b7c38cf23e3a97517199a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff9281e8de9ac02a50fb6b142f3ff6f4c80f39a88e95e0eaa34339fb75b9f955)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e7022b3c9bed9ea0f859577454eb1ecb323521d97ff731ae0d721fb04fb69b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f49c1d4801910dd2a307d6711b2ea17e35adf853856fcc92c86ccd11ea298c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologies",
    jsii_struct_bases=[],
    name_mapping={},
)
class CsiVolumeRegistrationTopologies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationTopologies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationTopologiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__981532b55ea7a6c4bd341a3862425477ec6439fbbac0c3792e451b58332209b6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CsiVolumeRegistrationTopologiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dd446c09519e7bac5de2f8532c87f0e022599e309886a069ad85e4eaa59f949)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeRegistrationTopologiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c720a024865768b92c8b366f8341ca35da943584c66794a3fc4012ab4884547)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3142381964d78a643b5dccf32190ec81eb90b03fba22187f19660b25d9ac0c9a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bf12cb422be2a1edb1480a3e9f60185dbbceacf51d4cdffa9bc354f12ad1c70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class CsiVolumeRegistrationTopologiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__03c91afc494991d4c8fd57e500bc8fead34eb5c576503fd7ee5bfac59b452a90)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="segments")
    def segments(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "segments"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeRegistrationTopologies]:
        return typing.cast(typing.Optional[CsiVolumeRegistrationTopologies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeRegistrationTopologies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bb87ce082acc2633284c77496beafa40f1f336068343026bb5e42605366cb2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequest",
    jsii_struct_bases=[],
    name_mapping={"required": "required"},
)
class CsiVolumeRegistrationTopologyRequest:
    def __init__(
        self,
        *,
        required: typing.Optional[typing.Union["CsiVolumeRegistrationTopologyRequestRequired", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param required: required block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#required CsiVolumeRegistration#required}
        '''
        if isinstance(required, dict):
            required = CsiVolumeRegistrationTopologyRequestRequired(**required)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2591f3b8eb2e2cb4f90e0102e79753b8717ed81c9d8c55e71ea6d2d4e7f941dd)
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def required(
        self,
    ) -> typing.Optional["CsiVolumeRegistrationTopologyRequestRequired"]:
        '''required block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#required CsiVolumeRegistration#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional["CsiVolumeRegistrationTopologyRequestRequired"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationTopologyRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationTopologyRequestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88d9db5ecba535d85b68a8ffdc6a9db3b9f34a3ac939021ccdf4b21d4f3d7e3e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putRequired")
    def put_required(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeRegistrationTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology CsiVolumeRegistration#topology}
        '''
        value = CsiVolumeRegistrationTopologyRequestRequired(topology=topology)

        return typing.cast(None, jsii.invoke(self, "putRequired", [value]))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> "CsiVolumeRegistrationTopologyRequestRequiredOutputReference":
        return typing.cast("CsiVolumeRegistrationTopologyRequestRequiredOutputReference", jsii.get(self, "required"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(
        self,
    ) -> typing.Optional["CsiVolumeRegistrationTopologyRequestRequired"]:
        return typing.cast(typing.Optional["CsiVolumeRegistrationTopologyRequestRequired"], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeRegistrationTopologyRequest]:
        return typing.cast(typing.Optional[CsiVolumeRegistrationTopologyRequest], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeRegistrationTopologyRequest],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9035030838c5cde36ced62be367b6ddc0008fca0b34d567f668b89f11b3caa01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestRequired",
    jsii_struct_bases=[],
    name_mapping={"topology": "topology"},
)
class CsiVolumeRegistrationTopologyRequestRequired:
    def __init__(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeRegistrationTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology CsiVolumeRegistration#topology}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381b1ed969c97f504f8a78bd4a48a742981f0a7585c5b3c371247948845e22d9)
            check_type(argname="argument topology", value=topology, expected_type=type_hints["topology"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topology": topology,
        }

    @builtins.property
    def topology(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationTopologyRequestRequiredTopology"]]:
        '''topology block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#topology CsiVolumeRegistration#topology}
        '''
        result = self._values.get("topology")
        assert result is not None, "Required property 'topology' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationTopologyRequestRequiredTopology"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationTopologyRequestRequired(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationTopologyRequestRequiredOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestRequiredOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4ad7fec851ebf1fe860a987dd70d4895369d9fc14b67b49a68e5d6863bc6828)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTopology")
    def put_topology(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeRegistrationTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7cc400e35578cf5749f9c43a75427ba44f066525bc4dba784c53ce9270fd0fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTopology", [value]))

    @builtins.property
    @jsii.member(jsii_name="topology")
    def topology(self) -> "CsiVolumeRegistrationTopologyRequestRequiredTopologyList":
        return typing.cast("CsiVolumeRegistrationTopologyRequestRequiredTopologyList", jsii.get(self, "topology"))

    @builtins.property
    @jsii.member(jsii_name="topologyInput")
    def topology_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationTopologyRequestRequiredTopology"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeRegistrationTopologyRequestRequiredTopology"]]], jsii.get(self, "topologyInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CsiVolumeRegistrationTopologyRequestRequired]:
        return typing.cast(typing.Optional[CsiVolumeRegistrationTopologyRequestRequired], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeRegistrationTopologyRequestRequired],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b5233bb1d3f548f44a86407d40dfc3d0afc095f6446406c1d249e6d54cfbf26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestRequiredTopology",
    jsii_struct_bases=[],
    name_mapping={"segments": "segments"},
)
class CsiVolumeRegistrationTopologyRequestRequiredTopology:
    def __init__(self, *, segments: typing.Mapping[builtins.str, builtins.str]) -> None:
        '''
        :param segments: Define attributes for the topology request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#segments CsiVolumeRegistration#segments}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eb47fdae5fbec8a65ba2a37bea5e4d5fce1d3f094939a667dc670c6e026f5a8)
            check_type(argname="argument segments", value=segments, expected_type=type_hints["segments"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "segments": segments,
        }

    @builtins.property
    def segments(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Define attributes for the topology request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume_registration#segments CsiVolumeRegistration#segments}
        '''
        result = self._values.get("segments")
        assert result is not None, "Required property 'segments' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeRegistrationTopologyRequestRequiredTopology(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeRegistrationTopologyRequestRequiredTopologyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestRequiredTopologyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1f67e0be0648d80fd5c9e4ae2828f12af63b71f6d0ce59584c6b9b453ae1abbe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CsiVolumeRegistrationTopologyRequestRequiredTopologyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6e6b4bd064c6e00393b5c1d8f1074665a4edf97e4da6088abad530fd0c9472)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeRegistrationTopologyRequestRequiredTopologyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a908c53c87d850a199746381f26068c3ef82a56d3b9833cdac3a297f2b25b8e7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d271620950a12ba2691343d11f6a40d166d6934540368b446a1d69714557fb2a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7785f1cb01e85e718e5941276b8b7a7898de54800bdff1e7913235994242bdae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationTopologyRequestRequiredTopology]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationTopologyRequestRequiredTopology]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationTopologyRequestRequiredTopology]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70fc8ca3d6fbecee635491ade4594ed75ade4a78aea3a0da7ad25e1147c8b19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CsiVolumeRegistrationTopologyRequestRequiredTopologyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolumeRegistration.CsiVolumeRegistrationTopologyRequestRequiredTopologyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__43f23bcc66d0d2faec45c15ce8ae50befdc95fd9f2b7bbc9877f3699113653dd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="segmentsInput")
    def segments_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "segmentsInput"))

    @builtins.property
    @jsii.member(jsii_name="segments")
    def segments(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "segments"))

    @segments.setter
    def segments(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce05bd1894a1ac98c1979d837be6a755cd67fd4039fba37de59fb23a2a2347c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTopologyRequestRequiredTopology]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTopologyRequestRequiredTopology]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTopologyRequestRequiredTopology]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c14f7b2fe8323a29f2756d5fec5fc83b4df94fa1471755df3324fff82da102d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CsiVolumeRegistration",
    "CsiVolumeRegistrationCapability",
    "CsiVolumeRegistrationCapabilityList",
    "CsiVolumeRegistrationCapabilityOutputReference",
    "CsiVolumeRegistrationConfig",
    "CsiVolumeRegistrationMountOptions",
    "CsiVolumeRegistrationMountOptionsOutputReference",
    "CsiVolumeRegistrationTimeouts",
    "CsiVolumeRegistrationTimeoutsOutputReference",
    "CsiVolumeRegistrationTopologies",
    "CsiVolumeRegistrationTopologiesList",
    "CsiVolumeRegistrationTopologiesOutputReference",
    "CsiVolumeRegistrationTopologyRequest",
    "CsiVolumeRegistrationTopologyRequestOutputReference",
    "CsiVolumeRegistrationTopologyRequestRequired",
    "CsiVolumeRegistrationTopologyRequestRequiredOutputReference",
    "CsiVolumeRegistrationTopologyRequestRequiredTopology",
    "CsiVolumeRegistrationTopologyRequestRequiredTopologyList",
    "CsiVolumeRegistrationTopologyRequestRequiredTopologyOutputReference",
]

publication.publish()

def _typecheckingstub__d1fc32c6d48b10b39a7d44cfeabe60287bef0657b7ffc8d1b3c4958b2456e244(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    external_id: builtins.str,
    name: builtins.str,
    plugin_id: builtins.str,
    volume_id: builtins.str,
    capability: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    deregister_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    mount_options: typing.Optional[typing.Union[CsiVolumeRegistrationMountOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    timeouts: typing.Optional[typing.Union[CsiVolumeRegistrationTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    topology_request: typing.Optional[typing.Union[CsiVolumeRegistrationTopologyRequest, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__1497f5385a839aefc539632f014d49a94fa78571153d15bec1282a500bb1003e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d3121b14554d7dd5a1c43dcdece0ff21379eadc612db88928c19e5aac8514a9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28051e9233070cfb3d41528b8213e2a02b29f7d6c8f2741730032f14359b5109(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8670e2659b1afb2a475e736cb0c0a94932291b5a8feeb9e1019ca99646bd38c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b3bc613f4f594fe19076816f14f43be242a2de5ecce28735fcabf79367f7f72(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8566779c2c8a33687f0b1072f98d5bf12f013e25289fb07b974764646f2f023(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1326d7732c5e59e10df656ab86e7708af82005cea9367b7edc51e7b81f0de3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c074762749caa3e9d598ca80158927094a12893c34999bbe6ceb5ddd23feb61f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddcc228c09c14466c86d20db6c6145a93d4f62d0ac8ee4c4e7b4ebe9c49bc986(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fe062201e445011412a6ea370d3ca741d7ea7e173fb7129cf47a27b6a8d0358(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09a22a286244592c0b80f466260c886e0600a74efec10486286a52b85635c4b2(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e10b91f31536617d063e9664c0fb6c68af2ee0021b0f96ca9bf050eb32616b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac6949c82c7b16c53a3b9efa85aa41d53cb685e2a093847b7ec71856e5c4621(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bb373f5cdba814d3395fe79e508cea7e86b00ec7f7369b5d438429cc89cd1dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79cfc4d984323ae04a4bcfc1f67e66d114149e746ebbad0ef73a7647041d124(
    *,
    access_mode: builtins.str,
    attachment_mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7c8dbb7eee7ac216b09f2b59fd5d2ddd88a83330ea101add89abcb9c2a2bd2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5af178759a27329b8aea210115c0ee21c56d04c629ce72aa20e07ae860d4d1bd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c02f4d6712b51d580ba5d9292c1e4c56f31de7c631347029dbfd8a1076636a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8dc30ad90740548d3d8b56f314edaa9a17601716523418f3653130e73de568(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f804fea8f63f7349c437f5c91edd79eb612c79881a0815fe840e083f82bab456(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f8accb79ca68ff1a10139913a13de30d33d3fa625911bf7da2cb914148fe4bf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationCapability]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef0c7cfab3322a6ebcdbab18b3304fbfcaf1a81f5b91a4d34b3c3b57e589fcb8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee149a37cb91a493e83d1d2bb7aa94f7825269606d2d9902c6cbbc4fd4d1a12b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f50b8e586f6d73c0bcafe8a5449de2d8fdfb3fc815c369045154317f70a69c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ee1b6f5cb004bef777c8fc290251ff0f58aa852577376709fe53421710498f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationCapability]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5df8053c0d92e2e2791451309c3efa46118d4035b446d7283a5fb3093b887b0b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    external_id: builtins.str,
    name: builtins.str,
    plugin_id: builtins.str,
    volume_id: builtins.str,
    capability: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationCapability, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    context: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    deregister_on_destroy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    mount_options: typing.Optional[typing.Union[CsiVolumeRegistrationMountOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    timeouts: typing.Optional[typing.Union[CsiVolumeRegistrationTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    topology_request: typing.Optional[typing.Union[CsiVolumeRegistrationTopologyRequest, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4df372dae40b784ce05d6acd0ea366c125ce3e01ec9b2322206ebe3f950eedf(
    *,
    fs_type: typing.Optional[builtins.str] = None,
    mount_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67d3dca47861a7c597f0a459e4e4e65209253067052931f366c6642843d176fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1912711cdaef6f5935682c9847c9bcf9536eb785bb2d0e9e61f5f1c4a71e06c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a253a3b587beb59f2879eb69eaf8508a170b795666d0347be31bfc6324d2b433(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4caf96ca0f39feb8833b4eb6e09ea529ffd572e3ca07c70b35bbb108234f96a0(
    value: typing.Optional[CsiVolumeRegistrationMountOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df60350af4a198b7ee7523eb6838d760edb79ae6ab29ac89f6be17c3cb779a09(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9469f85bcd74123d22172f74f53a534cc6cc6fc7d27b7c38cf23e3a97517199a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff9281e8de9ac02a50fb6b142f3ff6f4c80f39a88e95e0eaa34339fb75b9f955(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e7022b3c9bed9ea0f859577454eb1ecb323521d97ff731ae0d721fb04fb69b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f49c1d4801910dd2a307d6711b2ea17e35adf853856fcc92c86ccd11ea298c9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__981532b55ea7a6c4bd341a3862425477ec6439fbbac0c3792e451b58332209b6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dd446c09519e7bac5de2f8532c87f0e022599e309886a069ad85e4eaa59f949(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c720a024865768b92c8b366f8341ca35da943584c66794a3fc4012ab4884547(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3142381964d78a643b5dccf32190ec81eb90b03fba22187f19660b25d9ac0c9a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bf12cb422be2a1edb1480a3e9f60185dbbceacf51d4cdffa9bc354f12ad1c70(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03c91afc494991d4c8fd57e500bc8fead34eb5c576503fd7ee5bfac59b452a90(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bb87ce082acc2633284c77496beafa40f1f336068343026bb5e42605366cb2a(
    value: typing.Optional[CsiVolumeRegistrationTopologies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2591f3b8eb2e2cb4f90e0102e79753b8717ed81c9d8c55e71ea6d2d4e7f941dd(
    *,
    required: typing.Optional[typing.Union[CsiVolumeRegistrationTopologyRequestRequired, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88d9db5ecba535d85b68a8ffdc6a9db3b9f34a3ac939021ccdf4b21d4f3d7e3e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9035030838c5cde36ced62be367b6ddc0008fca0b34d567f668b89f11b3caa01(
    value: typing.Optional[CsiVolumeRegistrationTopologyRequest],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381b1ed969c97f504f8a78bd4a48a742981f0a7585c5b3c371247948845e22d9(
    *,
    topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationTopologyRequestRequiredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4ad7fec851ebf1fe860a987dd70d4895369d9fc14b67b49a68e5d6863bc6828(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7cc400e35578cf5749f9c43a75427ba44f066525bc4dba784c53ce9270fd0fb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeRegistrationTopologyRequestRequiredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b5233bb1d3f548f44a86407d40dfc3d0afc095f6446406c1d249e6d54cfbf26(
    value: typing.Optional[CsiVolumeRegistrationTopologyRequestRequired],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8eb47fdae5fbec8a65ba2a37bea5e4d5fce1d3f094939a667dc670c6e026f5a8(
    *,
    segments: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f67e0be0648d80fd5c9e4ae2828f12af63b71f6d0ce59584c6b9b453ae1abbe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6e6b4bd064c6e00393b5c1d8f1074665a4edf97e4da6088abad530fd0c9472(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a908c53c87d850a199746381f26068c3ef82a56d3b9833cdac3a297f2b25b8e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d271620950a12ba2691343d11f6a40d166d6934540368b446a1d69714557fb2a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7785f1cb01e85e718e5941276b8b7a7898de54800bdff1e7913235994242bdae(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70fc8ca3d6fbecee635491ade4594ed75ade4a78aea3a0da7ad25e1147c8b19b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeRegistrationTopologyRequestRequiredTopology]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43f23bcc66d0d2faec45c15ce8ae50befdc95fd9f2b7bbc9877f3699113653dd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce05bd1894a1ac98c1979d837be6a755cd67fd4039fba37de59fb23a2a2347c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c14f7b2fe8323a29f2756d5fec5fc83b4df94fa1471755df3324fff82da102d2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeRegistrationTopologyRequestRequiredTopology]],
) -> None:
    """Type checking stubs"""
    pass
