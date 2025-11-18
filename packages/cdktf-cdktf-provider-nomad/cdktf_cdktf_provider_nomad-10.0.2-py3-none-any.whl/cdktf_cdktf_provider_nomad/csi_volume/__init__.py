r'''
# `nomad_csi_volume`

Refer to the Terraform Registry for docs: [`nomad_csi_volume`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume).
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


class CsiVolume(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolume",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume nomad_csi_volume}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeCapability", typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        plugin_id: builtins.str,
        volume_id: builtins.str,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        clone_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional[typing.Union["CsiVolumeMountOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["CsiVolumeTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        topology_request: typing.Optional[typing.Union["CsiVolumeTopologyRequest", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume nomad_csi_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capability CsiVolume#capability}
        :param name: The display name of the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#name CsiVolume#name}
        :param plugin_id: The ID of the CSI plugin that manages this volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#plugin_id CsiVolume#plugin_id}
        :param volume_id: The unique ID of the volume, how jobs will refer to the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#volume_id CsiVolume#volume_id}
        :param capacity_max: Defines how large the volume can be. The storage provider may return a volume that is smaller than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_max CsiVolume#capacity_max}
        :param capacity_min: Defines how small the volume can be. The storage provider may return a volume that is larger than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_min CsiVolume#capacity_min}
        :param clone_id: The volume ID to clone when creating this volume. Storage provider must support cloning. Conflicts with 'snapshot_id'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#clone_id CsiVolume#clone_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#id CsiVolume#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_options CsiVolume#mount_options}
        :param namespace: The namespace in which to create the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#namespace CsiVolume#namespace}
        :param parameters: An optional key-value map of strings passed directly to the CSI plugin to configure the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#parameters CsiVolume#parameters}
        :param secrets: An optional key-value map of strings used as credentials for publishing and unpublishing volumes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#secrets CsiVolume#secrets}
        :param snapshot_id: The snapshot ID to restore when creating this volume. Storage provider must support snapshots. Conflicts with 'clone_id'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#snapshot_id CsiVolume#snapshot_id}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#timeouts CsiVolume#timeouts}
        :param topology_request: topology_request block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology_request CsiVolume#topology_request}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__323f8a31e90dfdfff6afc1ced022a1692c87d809056a2d9e94a031e0c09fdd4b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CsiVolumeConfig(
            capability=capability,
            name=name,
            plugin_id=plugin_id,
            volume_id=volume_id,
            capacity_max=capacity_max,
            capacity_min=capacity_min,
            clone_id=clone_id,
            id=id,
            mount_options=mount_options,
            namespace=namespace,
            parameters=parameters,
            secrets=secrets,
            snapshot_id=snapshot_id,
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
        '''Generates CDKTF code for importing a CsiVolume resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CsiVolume to import.
        :param import_from_id: The id of the existing CsiVolume that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CsiVolume to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b01a427f84f2ced08b8268aec46e464dc2b13f78d2c3a7beddcb3737e85711e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCapability")
    def put_capability(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeCapability", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc71fbae3a6b5c3ea6083009f90112980e2bc61dbdfa429bea94dae3f25f30b3)
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
        :param fs_type: The file system type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#fs_type CsiVolume#fs_type}
        :param mount_flags: The flags passed to mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_flags CsiVolume#mount_flags}
        '''
        value = CsiVolumeMountOptions(fs_type=fs_type, mount_flags=mount_flags)

        return typing.cast(None, jsii.invoke(self, "putMountOptions", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#create CsiVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#delete CsiVolume#delete}.
        '''
        value = CsiVolumeTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="putTopologyRequest")
    def put_topology_request(
        self,
        *,
        preferred: typing.Optional[typing.Union["CsiVolumeTopologyRequestPreferred", typing.Dict[builtins.str, typing.Any]]] = None,
        required: typing.Optional[typing.Union["CsiVolumeTopologyRequestRequired", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preferred: preferred block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#preferred CsiVolume#preferred}
        :param required: required block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#required CsiVolume#required}
        '''
        value = CsiVolumeTopologyRequest(preferred=preferred, required=required)

        return typing.cast(None, jsii.invoke(self, "putTopologyRequest", [value]))

    @jsii.member(jsii_name="resetCapacityMax")
    def reset_capacity_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMax", []))

    @jsii.member(jsii_name="resetCapacityMin")
    def reset_capacity_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapacityMin", []))

    @jsii.member(jsii_name="resetCloneId")
    def reset_clone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloneId", []))

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

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

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
    def capability(self) -> "CsiVolumeCapabilityList":
        return typing.cast("CsiVolumeCapabilityList", jsii.get(self, "capability"))

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
    @jsii.member(jsii_name="context")
    def context(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "context"))

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
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @builtins.property
    @jsii.member(jsii_name="mountOptions")
    def mount_options(self) -> "CsiVolumeMountOptionsOutputReference":
        return typing.cast("CsiVolumeMountOptionsOutputReference", jsii.get(self, "mountOptions"))

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
    def timeouts(self) -> "CsiVolumeTimeoutsOutputReference":
        return typing.cast("CsiVolumeTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="topologies")
    def topologies(self) -> "CsiVolumeTopologiesList":
        return typing.cast("CsiVolumeTopologiesList", jsii.get(self, "topologies"))

    @builtins.property
    @jsii.member(jsii_name="topologyRequest")
    def topology_request(self) -> "CsiVolumeTopologyRequestOutputReference":
        return typing.cast("CsiVolumeTopologyRequestOutputReference", jsii.get(self, "topologyRequest"))

    @builtins.property
    @jsii.member(jsii_name="capabilityInput")
    def capability_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeCapability"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeCapability"]]], jsii.get(self, "capabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMaxInput")
    def capacity_max_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="capacityMinInput")
    def capacity_min_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "capacityMinInput"))

    @builtins.property
    @jsii.member(jsii_name="cloneIdInput")
    def clone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mountOptionsInput")
    def mount_options_input(self) -> typing.Optional["CsiVolumeMountOptions"]:
        return typing.cast(typing.Optional["CsiVolumeMountOptions"], jsii.get(self, "mountOptionsInput"))

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
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CsiVolumeTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "CsiVolumeTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="topologyRequestInput")
    def topology_request_input(self) -> typing.Optional["CsiVolumeTopologyRequest"]:
        return typing.cast(typing.Optional["CsiVolumeTopologyRequest"], jsii.get(self, "topologyRequestInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__65fc54323b76e2920c0075dfbbf6b6d3c24579f3cfada68a4de1274a7e01c811)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="capacityMin")
    def capacity_min(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "capacityMin"))

    @capacity_min.setter
    def capacity_min(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00fa1ecc9a9935cdd00846ae414377df03999770bb3b552ef4bc91faefebf2a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capacityMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloneId")
    def clone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloneId"))

    @clone_id.setter
    def clone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66e7cd367742f2360cadde864ed0778ea5c73c848d1c0625dfd8700bbe7fb4ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f34b3be4413819e496c1f5a90433800ac8cab292f159618e6927a944eed01a17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fd2b6fa88e94471d1155cd3f78b588ed75b43007fba1cfbfda3adda8b557ee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e02d06c65e4e8148622c095fa0ea78bc17770b034c227cccfa81e3e47de899f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "parameters"))

    @parameters.setter
    def parameters(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__905d5da6cb175fe70ff6794a63db25d03bcac1ba2812041ab43338c6673b6617)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginId")
    def plugin_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginId"))

    @plugin_id.setter
    def plugin_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9f63a9bde55c2d2a8edc36591b8cf031254564930102c7640a787c88ff1e8ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secrets")
    def secrets(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "secrets"))

    @secrets.setter
    def secrets(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf798a74a81b78b539363d2bf00f2c9f44ed0478ec6f0e57f925b8ac4d09d84c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secrets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ebe9f5a8c21e7fe535dc84c07b2784faec69449b9141d02be5ae804e755b51a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="volumeId")
    def volume_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "volumeId"))

    @volume_id.setter
    def volume_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8c4a16f95a09b81b3f5c69df2ea7dffc90fdf04cbfab51272a459ffe1ad6fe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "volumeId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeCapability",
    jsii_struct_bases=[],
    name_mapping={"access_mode": "accessMode", "attachment_mode": "attachmentMode"},
)
class CsiVolumeCapability:
    def __init__(
        self,
        *,
        access_mode: builtins.str,
        attachment_mode: builtins.str,
    ) -> None:
        '''
        :param access_mode: Defines whether a volume should be available concurrently. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#access_mode CsiVolume#access_mode}
        :param attachment_mode: The storage API that will be used by the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#attachment_mode CsiVolume#attachment_mode}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__086b72051a74c7348586f056f7c4c0e00095081375dc004bd8eaf8bd64412b06)
            check_type(argname="argument access_mode", value=access_mode, expected_type=type_hints["access_mode"])
            check_type(argname="argument attachment_mode", value=attachment_mode, expected_type=type_hints["attachment_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_mode": access_mode,
            "attachment_mode": attachment_mode,
        }

    @builtins.property
    def access_mode(self) -> builtins.str:
        '''Defines whether a volume should be available concurrently.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#access_mode CsiVolume#access_mode}
        '''
        result = self._values.get("access_mode")
        assert result is not None, "Required property 'access_mode' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachment_mode(self) -> builtins.str:
        '''The storage API that will be used by the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#attachment_mode CsiVolume#attachment_mode}
        '''
        result = self._values.get("attachment_mode")
        assert result is not None, "Required property 'attachment_mode' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeCapability(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeCapabilityList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeCapabilityList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14cfc486d7cc85199ec3751b63b4c2defec90ebe9d298ef0b0a0dd9a9d6cd1b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CsiVolumeCapabilityOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c9e1cc3f90cbee55daab0bc3e78007d96cc16534406a833e737b30e7a3af36e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeCapabilityOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b1b2a6231c8ec48b8941b7b5f747f549a6f52e858e43b8ef8c9fa6e06229642)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b4c50e3b784e081bed2e9561b1e0554020cf322ae809d8c964135abfbe13be0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5cb3b1a3f936b1500e67888cca5542dcb63341bfb3a7b7410774b2ff6674895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__376705853ec3486d47299ef258d94556266530e1e44fde153b55510469fe25a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CsiVolumeCapabilityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeCapabilityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9add83ec700e7df143161eb3c9f7d6997d1077724dae687141f58030825f5091)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7976c140810a1561af8c259e7cb6229a463e8ea39aa07897c69461527db28a9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="attachmentMode")
    def attachment_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "attachmentMode"))

    @attachment_mode.setter
    def attachment_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dedcc99e250f6edd663f931eecabde69148ca181dccb6b7ac22e5f8ee7ed354)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "attachmentMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeCapability]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeCapability]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeCapability]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__530979448d1e79436f09eb49ba8a21764ae38a5f9607ba89d55e693778149bd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeConfig",
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
        "volume_id": "volumeId",
        "capacity_max": "capacityMax",
        "capacity_min": "capacityMin",
        "clone_id": "cloneId",
        "id": "id",
        "mount_options": "mountOptions",
        "namespace": "namespace",
        "parameters": "parameters",
        "secrets": "secrets",
        "snapshot_id": "snapshotId",
        "timeouts": "timeouts",
        "topology_request": "topologyRequest",
    },
)
class CsiVolumeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
        name: builtins.str,
        plugin_id: builtins.str,
        volume_id: builtins.str,
        capacity_max: typing.Optional[builtins.str] = None,
        capacity_min: typing.Optional[builtins.str] = None,
        clone_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        mount_options: typing.Optional[typing.Union["CsiVolumeMountOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        namespace: typing.Optional[builtins.str] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["CsiVolumeTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        topology_request: typing.Optional[typing.Union["CsiVolumeTopologyRequest", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param capability: capability block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capability CsiVolume#capability}
        :param name: The display name of the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#name CsiVolume#name}
        :param plugin_id: The ID of the CSI plugin that manages this volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#plugin_id CsiVolume#plugin_id}
        :param volume_id: The unique ID of the volume, how jobs will refer to the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#volume_id CsiVolume#volume_id}
        :param capacity_max: Defines how large the volume can be. The storage provider may return a volume that is smaller than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_max CsiVolume#capacity_max}
        :param capacity_min: Defines how small the volume can be. The storage provider may return a volume that is larger than this value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_min CsiVolume#capacity_min}
        :param clone_id: The volume ID to clone when creating this volume. Storage provider must support cloning. Conflicts with 'snapshot_id'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#clone_id CsiVolume#clone_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#id CsiVolume#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mount_options: mount_options block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_options CsiVolume#mount_options}
        :param namespace: The namespace in which to create the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#namespace CsiVolume#namespace}
        :param parameters: An optional key-value map of strings passed directly to the CSI plugin to configure the volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#parameters CsiVolume#parameters}
        :param secrets: An optional key-value map of strings used as credentials for publishing and unpublishing volumes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#secrets CsiVolume#secrets}
        :param snapshot_id: The snapshot ID to restore when creating this volume. Storage provider must support snapshots. Conflicts with 'clone_id'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#snapshot_id CsiVolume#snapshot_id}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#timeouts CsiVolume#timeouts}
        :param topology_request: topology_request block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology_request CsiVolume#topology_request}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(mount_options, dict):
            mount_options = CsiVolumeMountOptions(**mount_options)
        if isinstance(timeouts, dict):
            timeouts = CsiVolumeTimeouts(**timeouts)
        if isinstance(topology_request, dict):
            topology_request = CsiVolumeTopologyRequest(**topology_request)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92426c8547380e2c2b78595baffa814dd5499e099531432908a5d1eda7e8e583)
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
            check_type(argname="argument volume_id", value=volume_id, expected_type=type_hints["volume_id"])
            check_type(argname="argument capacity_max", value=capacity_max, expected_type=type_hints["capacity_max"])
            check_type(argname="argument capacity_min", value=capacity_min, expected_type=type_hints["capacity_min"])
            check_type(argname="argument clone_id", value=clone_id, expected_type=type_hints["clone_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument mount_options", value=mount_options, expected_type=type_hints["mount_options"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument parameters", value=parameters, expected_type=type_hints["parameters"])
            check_type(argname="argument secrets", value=secrets, expected_type=type_hints["secrets"])
            check_type(argname="argument snapshot_id", value=snapshot_id, expected_type=type_hints["snapshot_id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument topology_request", value=topology_request, expected_type=type_hints["topology_request"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capability": capability,
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
        if capacity_max is not None:
            self._values["capacity_max"] = capacity_max
        if capacity_min is not None:
            self._values["capacity_min"] = capacity_min
        if clone_id is not None:
            self._values["clone_id"] = clone_id
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
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id
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
    def capability(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]]:
        '''capability block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capability CsiVolume#capability}
        '''
        result = self._values.get("capability")
        assert result is not None, "Required property 'capability' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The display name of the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#name CsiVolume#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def plugin_id(self) -> builtins.str:
        '''The ID of the CSI plugin that manages this volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#plugin_id CsiVolume#plugin_id}
        '''
        result = self._values.get("plugin_id")
        assert result is not None, "Required property 'plugin_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def volume_id(self) -> builtins.str:
        '''The unique ID of the volume, how jobs will refer to the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#volume_id CsiVolume#volume_id}
        '''
        result = self._values.get("volume_id")
        assert result is not None, "Required property 'volume_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def capacity_max(self) -> typing.Optional[builtins.str]:
        '''Defines how large the volume can be.

        The storage provider may return a volume that is smaller than this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_max CsiVolume#capacity_max}
        '''
        result = self._values.get("capacity_max")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def capacity_min(self) -> typing.Optional[builtins.str]:
        '''Defines how small the volume can be.

        The storage provider may return a volume that is larger than this value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#capacity_min CsiVolume#capacity_min}
        '''
        result = self._values.get("capacity_min")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def clone_id(self) -> typing.Optional[builtins.str]:
        '''The volume ID to clone when creating this volume. Storage provider must support cloning. Conflicts with 'snapshot_id'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#clone_id CsiVolume#clone_id}
        '''
        result = self._values.get("clone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#id CsiVolume#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_options(self) -> typing.Optional["CsiVolumeMountOptions"]:
        '''mount_options block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_options CsiVolume#mount_options}
        '''
        result = self._values.get("mount_options")
        return typing.cast(typing.Optional["CsiVolumeMountOptions"], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''The namespace in which to create the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#namespace CsiVolume#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional key-value map of strings passed directly to the CSI plugin to configure the volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#parameters CsiVolume#parameters}
        '''
        result = self._values.get("parameters")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def secrets(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An optional key-value map of strings used as credentials for publishing and unpublishing volumes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#secrets CsiVolume#secrets}
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''The snapshot ID to restore when creating this volume. Storage provider must support snapshots. Conflicts with 'clone_id'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#snapshot_id CsiVolume#snapshot_id}
        '''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["CsiVolumeTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#timeouts CsiVolume#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["CsiVolumeTimeouts"], result)

    @builtins.property
    def topology_request(self) -> typing.Optional["CsiVolumeTopologyRequest"]:
        '''topology_request block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology_request CsiVolume#topology_request}
        '''
        result = self._values.get("topology_request")
        return typing.cast(typing.Optional["CsiVolumeTopologyRequest"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeMountOptions",
    jsii_struct_bases=[],
    name_mapping={"fs_type": "fsType", "mount_flags": "mountFlags"},
)
class CsiVolumeMountOptions:
    def __init__(
        self,
        *,
        fs_type: typing.Optional[builtins.str] = None,
        mount_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param fs_type: The file system type. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#fs_type CsiVolume#fs_type}
        :param mount_flags: The flags passed to mount. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_flags CsiVolume#mount_flags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09abfe3957224b324a0633af208592335b5089801bc386f9a3a162f1d45208d8)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#fs_type CsiVolume#fs_type}
        '''
        result = self._values.get("fs_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mount_flags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The flags passed to mount.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#mount_flags CsiVolume#mount_flags}
        '''
        result = self._values.get("mount_flags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeMountOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeMountOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeMountOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a24e03e7c994696b348fd54595198f5058a2cb1e789cc0c184650ef225b90366)
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
            type_hints = typing.get_type_hints(_typecheckingstub__772972032279645e4ff734d26f10543143820fd98d742ada81c47933ede23e62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fsType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mountFlags")
    def mount_flags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "mountFlags"))

    @mount_flags.setter
    def mount_flags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37147aec89c6f9b6e63bfb409bcb7efc6e223a3664726466dbcf64fe58bbbd56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mountFlags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeMountOptions]:
        return typing.cast(typing.Optional[CsiVolumeMountOptions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CsiVolumeMountOptions]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244c82f0d15ddb23af73ed9d8320f3142cc68db0ca27ac8d624b29654032bbb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class CsiVolumeTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#create CsiVolume#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#delete CsiVolume#delete}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c386d9593c40a846617a6fabc43c7221184a9a0bd0620af047b15bade2d048a)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#create CsiVolume#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#delete CsiVolume#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b68738153d3c186652beb03ce713476c8f2f4b174761bb30d4b63c07032d1138)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65cf983261646ba7021b9db5b207b02cf53ece5bd1b86f430c672931a1f43115)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36c570360c1dd09d7b1d384fd138473b30339e37b0b71bc513ee11c6df82a928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46d0bb4808f69a6cf908b7305230ee16acd0b4d20cb7448060f18ef424f81431)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologies",
    jsii_struct_bases=[],
    name_mapping={},
)
class CsiVolumeTopologies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologiesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologiesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3835cf0f36c6ed370758d65477880892efac823695b594a1870977e9e136fb0d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CsiVolumeTopologiesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f53f80c7d35779b86e24f92b4db1676c3966179757f24d3cf12c97bc2a4b2809)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeTopologiesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a5f29ef8f9ab5d80edae107caac57ac041504ccbcf43bd81649ab30127a623b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f00b78e0f9495e862c1044182c218b5c855050913f8cccafbc513f0a9b4fdb09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ef9ebcd1d1c1d6b5a3b9b240aeb4aa258dc181b5f1654d9e586d7774c31c2d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class CsiVolumeTopologiesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologiesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__82455a2745b8951aae13b4fdd096746a2da9886eaec2e17ff8a8a3c634db8512)
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
    def internal_value(self) -> typing.Optional[CsiVolumeTopologies]:
        return typing.cast(typing.Optional[CsiVolumeTopologies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CsiVolumeTopologies]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c83fcbc4a0d401ed870c5e33c70b3b979592ed9724aff3e220231b0173f1ff9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequest",
    jsii_struct_bases=[],
    name_mapping={"preferred": "preferred", "required": "required"},
)
class CsiVolumeTopologyRequest:
    def __init__(
        self,
        *,
        preferred: typing.Optional[typing.Union["CsiVolumeTopologyRequestPreferred", typing.Dict[builtins.str, typing.Any]]] = None,
        required: typing.Optional[typing.Union["CsiVolumeTopologyRequestRequired", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param preferred: preferred block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#preferred CsiVolume#preferred}
        :param required: required block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#required CsiVolume#required}
        '''
        if isinstance(preferred, dict):
            preferred = CsiVolumeTopologyRequestPreferred(**preferred)
        if isinstance(required, dict):
            required = CsiVolumeTopologyRequestRequired(**required)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1f54036302c4d037195ebe562af896bb6055ffea45ba80c9645480aafd8d465)
            check_type(argname="argument preferred", value=preferred, expected_type=type_hints["preferred"])
            check_type(argname="argument required", value=required, expected_type=type_hints["required"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if preferred is not None:
            self._values["preferred"] = preferred
        if required is not None:
            self._values["required"] = required

    @builtins.property
    def preferred(self) -> typing.Optional["CsiVolumeTopologyRequestPreferred"]:
        '''preferred block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#preferred CsiVolume#preferred}
        '''
        result = self._values.get("preferred")
        return typing.cast(typing.Optional["CsiVolumeTopologyRequestPreferred"], result)

    @builtins.property
    def required(self) -> typing.Optional["CsiVolumeTopologyRequestRequired"]:
        '''required block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#required CsiVolume#required}
        '''
        result = self._values.get("required")
        return typing.cast(typing.Optional["CsiVolumeTopologyRequestRequired"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologyRequest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologyRequestOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb94904f8612f860a19aa5c78afad333b02868043c0b16a439de41b1de90fe23)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPreferred")
    def put_preferred(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestPreferredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        value = CsiVolumeTopologyRequestPreferred(topology=topology)

        return typing.cast(None, jsii.invoke(self, "putPreferred", [value]))

    @jsii.member(jsii_name="putRequired")
    def put_required(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        value = CsiVolumeTopologyRequestRequired(topology=topology)

        return typing.cast(None, jsii.invoke(self, "putRequired", [value]))

    @jsii.member(jsii_name="resetPreferred")
    def reset_preferred(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferred", []))

    @jsii.member(jsii_name="resetRequired")
    def reset_required(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequired", []))

    @builtins.property
    @jsii.member(jsii_name="preferred")
    def preferred(self) -> "CsiVolumeTopologyRequestPreferredOutputReference":
        return typing.cast("CsiVolumeTopologyRequestPreferredOutputReference", jsii.get(self, "preferred"))

    @builtins.property
    @jsii.member(jsii_name="required")
    def required(self) -> "CsiVolumeTopologyRequestRequiredOutputReference":
        return typing.cast("CsiVolumeTopologyRequestRequiredOutputReference", jsii.get(self, "required"))

    @builtins.property
    @jsii.member(jsii_name="preferredInput")
    def preferred_input(self) -> typing.Optional["CsiVolumeTopologyRequestPreferred"]:
        return typing.cast(typing.Optional["CsiVolumeTopologyRequestPreferred"], jsii.get(self, "preferredInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredInput")
    def required_input(self) -> typing.Optional["CsiVolumeTopologyRequestRequired"]:
        return typing.cast(typing.Optional["CsiVolumeTopologyRequestRequired"], jsii.get(self, "requiredInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeTopologyRequest]:
        return typing.cast(typing.Optional[CsiVolumeTopologyRequest], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CsiVolumeTopologyRequest]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf239dc6bb2bad86c8c8cebe2cec3c47ebb28c43e576779d0eaaeffe14f4d1b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestPreferred",
    jsii_struct_bases=[],
    name_mapping={"topology": "topology"},
)
class CsiVolumeTopologyRequestPreferred:
    def __init__(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestPreferredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fa9040ebaf41bc5b66f137f9c806ffc5f6cbb7a2179eea6b263f6dfd9289404)
            check_type(argname="argument topology", value=topology, expected_type=type_hints["topology"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topology": topology,
        }

    @builtins.property
    def topology(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestPreferredTopology"]]:
        '''topology block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        result = self._values.get("topology")
        assert result is not None, "Required property 'topology' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestPreferredTopology"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologyRequestPreferred(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologyRequestPreferredOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestPreferredOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b19e9c65a533029d69262d137322fe3513d27e71bf284822eae4da204a05e9df)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTopology")
    def put_topology(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestPreferredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fad8860c0360b1be7d028191c67454d2bf773b2036d6cc546ae0c7fed291db1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTopology", [value]))

    @builtins.property
    @jsii.member(jsii_name="topology")
    def topology(self) -> "CsiVolumeTopologyRequestPreferredTopologyList":
        return typing.cast("CsiVolumeTopologyRequestPreferredTopologyList", jsii.get(self, "topology"))

    @builtins.property
    @jsii.member(jsii_name="topologyInput")
    def topology_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestPreferredTopology"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestPreferredTopology"]]], jsii.get(self, "topologyInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeTopologyRequestPreferred]:
        return typing.cast(typing.Optional[CsiVolumeTopologyRequestPreferred], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeTopologyRequestPreferred],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf6a72556204b13c9a5ef87698f2480c89bf795c473b50a9ca1413a65cdeaf5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestPreferredTopology",
    jsii_struct_bases=[],
    name_mapping={"segments": "segments"},
)
class CsiVolumeTopologyRequestPreferredTopology:
    def __init__(self, *, segments: typing.Mapping[builtins.str, builtins.str]) -> None:
        '''
        :param segments: Define the attributes for the topology request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#segments CsiVolume#segments}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a436e2d474043bbb03f8a2238c505d20ab98d1a92669651786c616abaf5046ee)
            check_type(argname="argument segments", value=segments, expected_type=type_hints["segments"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "segments": segments,
        }

    @builtins.property
    def segments(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Define the attributes for the topology request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#segments CsiVolume#segments}
        '''
        result = self._values.get("segments")
        assert result is not None, "Required property 'segments' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologyRequestPreferredTopology(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologyRequestPreferredTopologyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestPreferredTopologyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0150fdd128ed4d5edef483c33b7c57efc9d67704f260e34fdb2ab20deed8137)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CsiVolumeTopologyRequestPreferredTopologyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adea7e2fe5cb7ab1c6044c1861fba135b926ead5ab5380911aa33513988b6114)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeTopologyRequestPreferredTopologyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f096c9c3145e6ff815f4447e71d17f1756b5c42456a8ea3f74f6d9a30d2eb6e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__75f2b7c18291a6e77215f01825fd4948d9943ed3c40ed3701128be21e959ca03)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3eb297b55e644a7fb7c150a5eab6d24feb184726adc9764e7696ee6bc2a8c544)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestPreferredTopology]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestPreferredTopology]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestPreferredTopology]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38ba5fd4879ba2100eeda57b5424331b9ec3f87cf4227012d977ec7bb627701e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CsiVolumeTopologyRequestPreferredTopologyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestPreferredTopologyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a65a9469075180eda6f70bf1a873173d170e3080cb52e7c08f25408527f09a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7005a749f27ce258183cc926cb3dfd77aa9eb1e7b943d3331bd299b404c5f2c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestPreferredTopology]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestPreferredTopology]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestPreferredTopology]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f32f4c519a48981ef7eb60c964da90ab3f89aa3e06154fc2bfb1cdc8a055990)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestRequired",
    jsii_struct_bases=[],
    name_mapping={"topology": "topology"},
)
class CsiVolumeTopologyRequestRequired:
    def __init__(
        self,
        *,
        topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param topology: topology block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__522442c5d5ec7e9971745d53e01e53eaddde46be9cd8de4f822317b1156be70e)
            check_type(argname="argument topology", value=topology, expected_type=type_hints["topology"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "topology": topology,
        }

    @builtins.property
    def topology(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestRequiredTopology"]]:
        '''topology block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#topology CsiVolume#topology}
        '''
        result = self._values.get("topology")
        assert result is not None, "Required property 'topology' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestRequiredTopology"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologyRequestRequired(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologyRequestRequiredOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestRequiredOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__38b5147bb501c38de076ca2931136639ed5465b007595f5127c64bf3a527230c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTopology")
    def put_topology(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CsiVolumeTopologyRequestRequiredTopology", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a63f9b5606d0c88f67e5b38d7d671cab474a97b4b638b507eef99997da7ce687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTopology", [value]))

    @builtins.property
    @jsii.member(jsii_name="topology")
    def topology(self) -> "CsiVolumeTopologyRequestRequiredTopologyList":
        return typing.cast("CsiVolumeTopologyRequestRequiredTopologyList", jsii.get(self, "topology"))

    @builtins.property
    @jsii.member(jsii_name="topologyInput")
    def topology_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestRequiredTopology"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CsiVolumeTopologyRequestRequiredTopology"]]], jsii.get(self, "topologyInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CsiVolumeTopologyRequestRequired]:
        return typing.cast(typing.Optional[CsiVolumeTopologyRequestRequired], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CsiVolumeTopologyRequestRequired],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1543033e50bf0b7c92fa4c3073c8b49ca963754366ba7e737dc21fa9cf04977e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestRequiredTopology",
    jsii_struct_bases=[],
    name_mapping={"segments": "segments"},
)
class CsiVolumeTopologyRequestRequiredTopology:
    def __init__(self, *, segments: typing.Mapping[builtins.str, builtins.str]) -> None:
        '''
        :param segments: Define the attributes for the topology request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#segments CsiVolume#segments}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a633c72a910a1b35323a629f0c69988c8788cb6dd11a4c9e9eb7fdba9788a577)
            check_type(argname="argument segments", value=segments, expected_type=type_hints["segments"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "segments": segments,
        }

    @builtins.property
    def segments(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''Define the attributes for the topology request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/csi_volume#segments CsiVolume#segments}
        '''
        result = self._values.get("segments")
        assert result is not None, "Required property 'segments' is missing"
        return typing.cast(typing.Mapping[builtins.str, builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CsiVolumeTopologyRequestRequiredTopology(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CsiVolumeTopologyRequestRequiredTopologyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestRequiredTopologyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f65e0b326c3d1adf825b755268f51dadafdbaabfd52dda6b060a1bbcff75f976)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CsiVolumeTopologyRequestRequiredTopologyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf86e941fdfb172063ac1ca833f669b7019407f33e584a2cc33500095320e0eb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CsiVolumeTopologyRequestRequiredTopologyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7b8cc70017e80d018677ec50e912e93f1a0a435fd14cab66628c478dc662829)
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
            type_hints = typing.get_type_hints(_typecheckingstub__401829e6fd0626dc68efc9f79fd930823a9511e362284d82bfd2882e9861bc94)
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
            type_hints = typing.get_type_hints(_typecheckingstub__81b90a16b5a1ac58cec9be0a81c7ca7794e9778296780ce14a59feb75a0fac62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestRequiredTopology]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestRequiredTopology]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestRequiredTopology]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92ec5a80c068ecb726c34bbe0fe30521ccfbc1dd7a9b3a5b4a0f025d1092b215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CsiVolumeTopologyRequestRequiredTopologyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.csiVolume.CsiVolumeTopologyRequestRequiredTopologyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c5fd51f3f01adedb4bc5ff4a77bbffa12d34dc40cf27d96287aa7920cd7a4b7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ed0eece61295a5cc2db128b3072c6b65955737b1a84ac71131731d48c6e99b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segments", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestRequiredTopology]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestRequiredTopology]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestRequiredTopology]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfc5be20c9a223f34f422b70f039da670fd9174fae3952dfd43df24a20df73dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CsiVolume",
    "CsiVolumeCapability",
    "CsiVolumeCapabilityList",
    "CsiVolumeCapabilityOutputReference",
    "CsiVolumeConfig",
    "CsiVolumeMountOptions",
    "CsiVolumeMountOptionsOutputReference",
    "CsiVolumeTimeouts",
    "CsiVolumeTimeoutsOutputReference",
    "CsiVolumeTopologies",
    "CsiVolumeTopologiesList",
    "CsiVolumeTopologiesOutputReference",
    "CsiVolumeTopologyRequest",
    "CsiVolumeTopologyRequestOutputReference",
    "CsiVolumeTopologyRequestPreferred",
    "CsiVolumeTopologyRequestPreferredOutputReference",
    "CsiVolumeTopologyRequestPreferredTopology",
    "CsiVolumeTopologyRequestPreferredTopologyList",
    "CsiVolumeTopologyRequestPreferredTopologyOutputReference",
    "CsiVolumeTopologyRequestRequired",
    "CsiVolumeTopologyRequestRequiredOutputReference",
    "CsiVolumeTopologyRequestRequiredTopology",
    "CsiVolumeTopologyRequestRequiredTopologyList",
    "CsiVolumeTopologyRequestRequiredTopologyOutputReference",
]

publication.publish()

def _typecheckingstub__323f8a31e90dfdfff6afc1ced022a1692c87d809056a2d9e94a031e0c09fdd4b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    plugin_id: builtins.str,
    volume_id: builtins.str,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    clone_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    mount_options: typing.Optional[typing.Union[CsiVolumeMountOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    snapshot_id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[CsiVolumeTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    topology_request: typing.Optional[typing.Union[CsiVolumeTopologyRequest, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__b01a427f84f2ced08b8268aec46e464dc2b13f78d2c3a7beddcb3737e85711e3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc71fbae3a6b5c3ea6083009f90112980e2bc61dbdfa429bea94dae3f25f30b3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65fc54323b76e2920c0075dfbbf6b6d3c24579f3cfada68a4de1274a7e01c811(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00fa1ecc9a9935cdd00846ae414377df03999770bb3b552ef4bc91faefebf2a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66e7cd367742f2360cadde864ed0778ea5c73c848d1c0625dfd8700bbe7fb4ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f34b3be4413819e496c1f5a90433800ac8cab292f159618e6927a944eed01a17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fd2b6fa88e94471d1155cd3f78b588ed75b43007fba1cfbfda3adda8b557ee2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e02d06c65e4e8148622c095fa0ea78bc17770b034c227cccfa81e3e47de899f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__905d5da6cb175fe70ff6794a63db25d03bcac1ba2812041ab43338c6673b6617(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9f63a9bde55c2d2a8edc36591b8cf031254564930102c7640a787c88ff1e8ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf798a74a81b78b539363d2bf00f2c9f44ed0478ec6f0e57f925b8ac4d09d84c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ebe9f5a8c21e7fe535dc84c07b2784faec69449b9141d02be5ae804e755b51a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8c4a16f95a09b81b3f5c69df2ea7dffc90fdf04cbfab51272a459ffe1ad6fe4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__086b72051a74c7348586f056f7c4c0e00095081375dc004bd8eaf8bd64412b06(
    *,
    access_mode: builtins.str,
    attachment_mode: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14cfc486d7cc85199ec3751b63b4c2defec90ebe9d298ef0b0a0dd9a9d6cd1b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c9e1cc3f90cbee55daab0bc3e78007d96cc16534406a833e737b30e7a3af36e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b1b2a6231c8ec48b8941b7b5f747f549a6f52e858e43b8ef8c9fa6e06229642(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4c50e3b784e081bed2e9561b1e0554020cf322ae809d8c964135abfbe13be0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5cb3b1a3f936b1500e67888cca5542dcb63341bfb3a7b7410774b2ff6674895(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__376705853ec3486d47299ef258d94556266530e1e44fde153b55510469fe25a0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeCapability]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9add83ec700e7df143161eb3c9f7d6997d1077724dae687141f58030825f5091(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7976c140810a1561af8c259e7cb6229a463e8ea39aa07897c69461527db28a9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dedcc99e250f6edd663f931eecabde69148ca181dccb6b7ac22e5f8ee7ed354(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__530979448d1e79436f09eb49ba8a21764ae38a5f9607ba89d55e693778149bd0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeCapability]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92426c8547380e2c2b78595baffa814dd5499e099531432908a5d1eda7e8e583(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    capability: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeCapability, typing.Dict[builtins.str, typing.Any]]]],
    name: builtins.str,
    plugin_id: builtins.str,
    volume_id: builtins.str,
    capacity_max: typing.Optional[builtins.str] = None,
    capacity_min: typing.Optional[builtins.str] = None,
    clone_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    mount_options: typing.Optional[typing.Union[CsiVolumeMountOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    namespace: typing.Optional[builtins.str] = None,
    parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    snapshot_id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[CsiVolumeTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    topology_request: typing.Optional[typing.Union[CsiVolumeTopologyRequest, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09abfe3957224b324a0633af208592335b5089801bc386f9a3a162f1d45208d8(
    *,
    fs_type: typing.Optional[builtins.str] = None,
    mount_flags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a24e03e7c994696b348fd54595198f5058a2cb1e789cc0c184650ef225b90366(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__772972032279645e4ff734d26f10543143820fd98d742ada81c47933ede23e62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37147aec89c6f9b6e63bfb409bcb7efc6e223a3664726466dbcf64fe58bbbd56(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244c82f0d15ddb23af73ed9d8320f3142cc68db0ca27ac8d624b29654032bbb1(
    value: typing.Optional[CsiVolumeMountOptions],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c386d9593c40a846617a6fabc43c7221184a9a0bd0620af047b15bade2d048a(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b68738153d3c186652beb03ce713476c8f2f4b174761bb30d4b63c07032d1138(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65cf983261646ba7021b9db5b207b02cf53ece5bd1b86f430c672931a1f43115(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36c570360c1dd09d7b1d384fd138473b30339e37b0b71bc513ee11c6df82a928(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46d0bb4808f69a6cf908b7305230ee16acd0b4d20cb7448060f18ef424f81431(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTimeouts]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3835cf0f36c6ed370758d65477880892efac823695b594a1870977e9e136fb0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f53f80c7d35779b86e24f92b4db1676c3966179757f24d3cf12c97bc2a4b2809(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5f29ef8f9ab5d80edae107caac57ac041504ccbcf43bd81649ab30127a623b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f00b78e0f9495e862c1044182c218b5c855050913f8cccafbc513f0a9b4fdb09(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ef9ebcd1d1c1d6b5a3b9b240aeb4aa258dc181b5f1654d9e586d7774c31c2d2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82455a2745b8951aae13b4fdd096746a2da9886eaec2e17ff8a8a3c634db8512(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c83fcbc4a0d401ed870c5e33c70b3b979592ed9724aff3e220231b0173f1ff9(
    value: typing.Optional[CsiVolumeTopologies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1f54036302c4d037195ebe562af896bb6055ffea45ba80c9645480aafd8d465(
    *,
    preferred: typing.Optional[typing.Union[CsiVolumeTopologyRequestPreferred, typing.Dict[builtins.str, typing.Any]]] = None,
    required: typing.Optional[typing.Union[CsiVolumeTopologyRequestRequired, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb94904f8612f860a19aa5c78afad333b02868043c0b16a439de41b1de90fe23(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf239dc6bb2bad86c8c8cebe2cec3c47ebb28c43e576779d0eaaeffe14f4d1b6(
    value: typing.Optional[CsiVolumeTopologyRequest],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fa9040ebaf41bc5b66f137f9c806ffc5f6cbb7a2179eea6b263f6dfd9289404(
    *,
    topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeTopologyRequestPreferredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b19e9c65a533029d69262d137322fe3513d27e71bf284822eae4da204a05e9df(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fad8860c0360b1be7d028191c67454d2bf773b2036d6cc546ae0c7fed291db1d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeTopologyRequestPreferredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf6a72556204b13c9a5ef87698f2480c89bf795c473b50a9ca1413a65cdeaf5b(
    value: typing.Optional[CsiVolumeTopologyRequestPreferred],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a436e2d474043bbb03f8a2238c505d20ab98d1a92669651786c616abaf5046ee(
    *,
    segments: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0150fdd128ed4d5edef483c33b7c57efc9d67704f260e34fdb2ab20deed8137(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adea7e2fe5cb7ab1c6044c1861fba135b926ead5ab5380911aa33513988b6114(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f096c9c3145e6ff815f4447e71d17f1756b5c42456a8ea3f74f6d9a30d2eb6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75f2b7c18291a6e77215f01825fd4948d9943ed3c40ed3701128be21e959ca03(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3eb297b55e644a7fb7c150a5eab6d24feb184726adc9764e7696ee6bc2a8c544(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38ba5fd4879ba2100eeda57b5424331b9ec3f87cf4227012d977ec7bb627701e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestPreferredTopology]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a65a9469075180eda6f70bf1a873173d170e3080cb52e7c08f25408527f09a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7005a749f27ce258183cc926cb3dfd77aa9eb1e7b943d3331bd299b404c5f2c9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f32f4c519a48981ef7eb60c964da90ab3f89aa3e06154fc2bfb1cdc8a055990(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestPreferredTopology]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__522442c5d5ec7e9971745d53e01e53eaddde46be9cd8de4f822317b1156be70e(
    *,
    topology: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeTopologyRequestRequiredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38b5147bb501c38de076ca2931136639ed5465b007595f5127c64bf3a527230c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a63f9b5606d0c88f67e5b38d7d671cab474a97b4b638b507eef99997da7ce687(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CsiVolumeTopologyRequestRequiredTopology, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1543033e50bf0b7c92fa4c3073c8b49ca963754366ba7e737dc21fa9cf04977e(
    value: typing.Optional[CsiVolumeTopologyRequestRequired],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a633c72a910a1b35323a629f0c69988c8788cb6dd11a4c9e9eb7fdba9788a577(
    *,
    segments: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f65e0b326c3d1adf825b755268f51dadafdbaabfd52dda6b060a1bbcff75f976(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf86e941fdfb172063ac1ca833f669b7019407f33e584a2cc33500095320e0eb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7b8cc70017e80d018677ec50e912e93f1a0a435fd14cab66628c478dc662829(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__401829e6fd0626dc68efc9f79fd930823a9511e362284d82bfd2882e9861bc94(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b90a16b5a1ac58cec9be0a81c7ca7794e9778296780ce14a59feb75a0fac62(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92ec5a80c068ecb726c34bbe0fe30521ccfbc1dd7a9b3a5b4a0f025d1092b215(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CsiVolumeTopologyRequestRequiredTopology]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c5fd51f3f01adedb4bc5ff4a77bbffa12d34dc40cf27d96287aa7920cd7a4b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed0eece61295a5cc2db128b3072c6b65955737b1a84ac71131731d48c6e99b5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfc5be20c9a223f34f422b70f039da670fd9174fae3952dfd43df24a20df73dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CsiVolumeTopologyRequestRequiredTopology]],
) -> None:
    """Type checking stubs"""
    pass
