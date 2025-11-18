r'''
# `nomad_acl_policy`

Refer to the Terraform Registry for docs: [`nomad_acl_policy`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy).
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


class AclPolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclPolicy.AclPolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy nomad_acl_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        rules_hcl: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        job_acl: typing.Optional[typing.Union["AclPolicyJobAcl", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy nomad_acl_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Unique name for this policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#name AclPolicy#name}
        :param rules_hcl: HCL or JSON representation of the rules to enforce on this policy. Use file() to specify a file as input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#rules_hcl AclPolicy#rules_hcl}
        :param description: Description for this policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#description AclPolicy#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#id AclPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param job_acl: job_acl block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_acl AclPolicy#job_acl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d054e2bc8be03d28d3a28a6dab462527bcac12bbbd17e74387a2aa26d8adcbba)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AclPolicyConfig(
            name=name,
            rules_hcl=rules_hcl,
            description=description,
            id=id,
            job_acl=job_acl,
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
        '''Generates CDKTF code for importing a AclPolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AclPolicy to import.
        :param import_from_id: The id of the existing AclPolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AclPolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa98d1f4bd0707bc1428ae415af79ef892b3568aff9cf579ba4640a65c3d7efa)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putJobAcl")
    def put_job_acl(
        self,
        *,
        job_id: builtins.str,
        group: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        task: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param job_id: Job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_id AclPolicy#job_id}
        :param group: Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#group AclPolicy#group}
        :param namespace: Namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#namespace AclPolicy#namespace}
        :param task: Task. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#task AclPolicy#task}
        '''
        value = AclPolicyJobAcl(
            job_id=job_id, group=group, namespace=namespace, task=task
        )

        return typing.cast(None, jsii.invoke(self, "putJobAcl", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJobAcl")
    def reset_job_acl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJobAcl", []))

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
    @jsii.member(jsii_name="jobAcl")
    def job_acl(self) -> "AclPolicyJobAclOutputReference":
        return typing.cast("AclPolicyJobAclOutputReference", jsii.get(self, "jobAcl"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jobAclInput")
    def job_acl_input(self) -> typing.Optional["AclPolicyJobAcl"]:
        return typing.cast(typing.Optional["AclPolicyJobAcl"], jsii.get(self, "jobAclInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesHclInput")
    def rules_hcl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rulesHclInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1c518a6af38af9c1ea6b4af323f9b28cba6ff131a952056c3941b0a3e2096f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864b0571d2420729fa143a6fd63f8c41ad92415834e6fd4944a75cee2da64189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15925be4a3c98e9476037b33dd5e4fc23851b20121fec529aa15973ae339e895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rulesHcl")
    def rules_hcl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rulesHcl"))

    @rules_hcl.setter
    def rules_hcl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb7723ee7778598343f596d28e568da0d74d5b6f0cd28c6e8b44e1d3cee19bf3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rulesHcl", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclPolicy.AclPolicyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "rules_hcl": "rulesHcl",
        "description": "description",
        "id": "id",
        "job_acl": "jobAcl",
    },
)
class AclPolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        rules_hcl: builtins.str,
        description: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        job_acl: typing.Optional[typing.Union["AclPolicyJobAcl", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Unique name for this policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#name AclPolicy#name}
        :param rules_hcl: HCL or JSON representation of the rules to enforce on this policy. Use file() to specify a file as input. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#rules_hcl AclPolicy#rules_hcl}
        :param description: Description for this policy. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#description AclPolicy#description}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#id AclPolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param job_acl: job_acl block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_acl AclPolicy#job_acl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(job_acl, dict):
            job_acl = AclPolicyJobAcl(**job_acl)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9dd74b156bc04292051b30dce551bee4be12595022fa30fd6b4c7bdc7334298)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument rules_hcl", value=rules_hcl, expected_type=type_hints["rules_hcl"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument job_acl", value=job_acl, expected_type=type_hints["job_acl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "rules_hcl": rules_hcl,
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
        if description is not None:
            self._values["description"] = description
        if id is not None:
            self._values["id"] = id
        if job_acl is not None:
            self._values["job_acl"] = job_acl

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
    def name(self) -> builtins.str:
        '''Unique name for this policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#name AclPolicy#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rules_hcl(self) -> builtins.str:
        '''HCL or JSON representation of the rules to enforce on this policy.

        Use file() to specify a file as input.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#rules_hcl AclPolicy#rules_hcl}
        '''
        result = self._values.get("rules_hcl")
        assert result is not None, "Required property 'rules_hcl' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for this policy.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#description AclPolicy#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#id AclPolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def job_acl(self) -> typing.Optional["AclPolicyJobAcl"]:
        '''job_acl block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_acl AclPolicy#job_acl}
        '''
        result = self._values.get("job_acl")
        return typing.cast(typing.Optional["AclPolicyJobAcl"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclPolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclPolicy.AclPolicyJobAcl",
    jsii_struct_bases=[],
    name_mapping={
        "job_id": "jobId",
        "group": "group",
        "namespace": "namespace",
        "task": "task",
    },
)
class AclPolicyJobAcl:
    def __init__(
        self,
        *,
        job_id: builtins.str,
        group: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        task: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param job_id: Job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_id AclPolicy#job_id}
        :param group: Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#group AclPolicy#group}
        :param namespace: Namespace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#namespace AclPolicy#namespace}
        :param task: Task. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#task AclPolicy#task}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55c11f172e229d6c07918c51651e0ede33d1b0d31636863f42b8addcdc70e7b0)
            check_type(argname="argument job_id", value=job_id, expected_type=type_hints["job_id"])
            check_type(argname="argument group", value=group, expected_type=type_hints["group"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument task", value=task, expected_type=type_hints["task"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "job_id": job_id,
        }
        if group is not None:
            self._values["group"] = group
        if namespace is not None:
            self._values["namespace"] = namespace
        if task is not None:
            self._values["task"] = task

    @builtins.property
    def job_id(self) -> builtins.str:
        '''Job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#job_id AclPolicy#job_id}
        '''
        result = self._values.get("job_id")
        assert result is not None, "Required property 'job_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def group(self) -> typing.Optional[builtins.str]:
        '''Group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#group AclPolicy#group}
        '''
        result = self._values.get("group")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#namespace AclPolicy#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def task(self) -> typing.Optional[builtins.str]:
        '''Task.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_policy#task AclPolicy#task}
        '''
        result = self._values.get("task")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclPolicyJobAcl(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AclPolicyJobAclOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclPolicy.AclPolicyJobAclOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9756e1bedc796d80daeef23e9483b6474aecb9831660c2700f7f210496abd490)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetGroup")
    def reset_group(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroup", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetTask")
    def reset_task(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTask", []))

    @builtins.property
    @jsii.member(jsii_name="groupInput")
    def group_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupInput"))

    @builtins.property
    @jsii.member(jsii_name="jobIdInput")
    def job_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jobIdInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="taskInput")
    def task_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "taskInput"))

    @builtins.property
    @jsii.member(jsii_name="group")
    def group(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "group"))

    @group.setter
    def group(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a31002bed6243ecf8c26a2936f91e5c79ad8b4e2a2bc057d73d695c35364f4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "group", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jobId")
    def job_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jobId"))

    @job_id.setter
    def job_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0a61f7e24c5ccfb93a1b4720b66c969c203a4c17e47cd6945466601917e3ed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jobId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63d6f2e586bbbad96acdd5cd259d24e54918806e9b20dcb716b4981edcb8b70d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="task")
    def task(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "task"))

    @task.setter
    def task(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6058bae05f23e1d688031fd2784cca108d090f07efd31eda2dc73c7666abacd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "task", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AclPolicyJobAcl]:
        return typing.cast(typing.Optional[AclPolicyJobAcl], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AclPolicyJobAcl]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d13da50d5f50b379543886818d236d1ced1ba08ed0961c0d4e2046bc675c513c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AclPolicy",
    "AclPolicyConfig",
    "AclPolicyJobAcl",
    "AclPolicyJobAclOutputReference",
]

publication.publish()

def _typecheckingstub__d054e2bc8be03d28d3a28a6dab462527bcac12bbbd17e74387a2aa26d8adcbba(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    rules_hcl: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    job_acl: typing.Optional[typing.Union[AclPolicyJobAcl, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__aa98d1f4bd0707bc1428ae415af79ef892b3568aff9cf579ba4640a65c3d7efa(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1c518a6af38af9c1ea6b4af323f9b28cba6ff131a952056c3941b0a3e2096f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864b0571d2420729fa143a6fd63f8c41ad92415834e6fd4944a75cee2da64189(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15925be4a3c98e9476037b33dd5e4fc23851b20121fec529aa15973ae339e895(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb7723ee7778598343f596d28e568da0d74d5b6f0cd28c6e8b44e1d3cee19bf3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9dd74b156bc04292051b30dce551bee4be12595022fa30fd6b4c7bdc7334298(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    rules_hcl: builtins.str,
    description: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    job_acl: typing.Optional[typing.Union[AclPolicyJobAcl, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55c11f172e229d6c07918c51651e0ede33d1b0d31636863f42b8addcdc70e7b0(
    *,
    job_id: builtins.str,
    group: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    task: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9756e1bedc796d80daeef23e9483b6474aecb9831660c2700f7f210496abd490(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a31002bed6243ecf8c26a2936f91e5c79ad8b4e2a2bc057d73d695c35364f4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0a61f7e24c5ccfb93a1b4720b66c969c203a4c17e47cd6945466601917e3ed9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63d6f2e586bbbad96acdd5cd259d24e54918806e9b20dcb716b4981edcb8b70d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6058bae05f23e1d688031fd2784cca108d090f07efd31eda2dc73c7666abacd4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d13da50d5f50b379543886818d236d1ced1ba08ed0961c0d4e2046bc675c513c(
    value: typing.Optional[AclPolicyJobAcl],
) -> None:
    """Type checking stubs"""
    pass
