r'''
# `provider`

Refer to the Terraform Registry for docs: [`nomad`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs).
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


class NomadProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.provider.NomadProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs nomad}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        auth_jwt: typing.Optional[typing.Union["NomadProviderAuthJwt", typing.Dict[builtins.str, typing.Any]]] = None,
        ca_file: typing.Optional[builtins.str] = None,
        ca_pem: typing.Optional[builtins.str] = None,
        cert_file: typing.Optional[builtins.str] = None,
        cert_pem: typing.Optional[builtins.str] = None,
        headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NomadProviderHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_auth: typing.Optional[builtins.str] = None,
        ignore_env_vars: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]] = None,
        key_file: typing.Optional[builtins.str] = None,
        key_pem: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_id: typing.Optional[builtins.str] = None,
        skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs nomad} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: URL of the root of the target Nomad agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#address NomadProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#alias NomadProvider#alias}
        :param auth_jwt: auth_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#auth_jwt NomadProvider#auth_jwt}
        :param ca_file: A path to a PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_file NomadProvider#ca_file}
        :param ca_pem: PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_pem NomadProvider#ca_pem}
        :param cert_file: A path to a PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_file NomadProvider#cert_file}
        :param cert_pem: PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_pem NomadProvider#cert_pem}
        :param headers: headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#headers NomadProvider#headers}
        :param http_auth: HTTP basic auth configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#http_auth NomadProvider#http_auth}
        :param ignore_env_vars: A set of environment variables that are ignored by the provider when configuring the Nomad API client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ignore_env_vars NomadProvider#ignore_env_vars}
        :param key_file: A path to a PEM-encoded private key, required if cert_file or cert_pem is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_file NomadProvider#key_file}
        :param key_pem: PEM-encoded private key, required if cert_file or cert_pem is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_pem NomadProvider#key_pem}
        :param region: Region of the target Nomad agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#region NomadProvider#region}
        :param secret_id: ACL token secret for API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#secret_id NomadProvider#secret_id}
        :param skip_verify: Skip TLS verification on client side. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#skip_verify NomadProvider#skip_verify}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1135b3e0a6e5d3f7edfef684226a9a3ae7c144ae366e8b37d5ae425d916fff)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = NomadProviderConfig(
            address=address,
            alias=alias,
            auth_jwt=auth_jwt,
            ca_file=ca_file,
            ca_pem=ca_pem,
            cert_file=cert_file,
            cert_pem=cert_pem,
            headers=headers,
            http_auth=http_auth,
            ignore_env_vars=ignore_env_vars,
            key_file=key_file,
            key_pem=key_pem,
            region=region,
            secret_id=secret_id,
            skip_verify=skip_verify,
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
        '''Generates CDKTF code for importing a NomadProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the NomadProvider to import.
        :param import_from_id: The id of the existing NomadProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the NomadProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fe3e6bb963e9fe03449bc0ac46c50f7523599db7df7556b66b2f81ef712e9be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAuthJwt")
    def reset_auth_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthJwt", []))

    @jsii.member(jsii_name="resetCaFile")
    def reset_ca_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaFile", []))

    @jsii.member(jsii_name="resetCaPem")
    def reset_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaPem", []))

    @jsii.member(jsii_name="resetCertFile")
    def reset_cert_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertFile", []))

    @jsii.member(jsii_name="resetCertPem")
    def reset_cert_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertPem", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetHttpAuth")
    def reset_http_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpAuth", []))

    @jsii.member(jsii_name="resetIgnoreEnvVars")
    def reset_ignore_env_vars(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreEnvVars", []))

    @jsii.member(jsii_name="resetKeyFile")
    def reset_key_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFile", []))

    @jsii.member(jsii_name="resetKeyPem")
    def reset_key_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPem", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSecretId")
    def reset_secret_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretId", []))

    @jsii.member(jsii_name="resetSkipVerify")
    def reset_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSkipVerify", []))

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
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="authJwtInput")
    def auth_jwt_input(self) -> typing.Optional["NomadProviderAuthJwt"]:
        return typing.cast(typing.Optional["NomadProviderAuthJwt"], jsii.get(self, "authJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="caFileInput")
    def ca_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caFileInput"))

    @builtins.property
    @jsii.member(jsii_name="caPemInput")
    def ca_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPemInput"))

    @builtins.property
    @jsii.member(jsii_name="certFileInput")
    def cert_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFileInput"))

    @builtins.property
    @jsii.member(jsii_name="certPemInput")
    def cert_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPemInput"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="httpAuthInput")
    def http_auth_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpAuthInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreEnvVarsInput")
    def ignore_env_vars_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]], jsii.get(self, "ignoreEnvVarsInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFileInput")
    def key_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFileInput"))

    @builtins.property
    @jsii.member(jsii_name="keyPemInput")
    def key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="secretIdInput")
    def secret_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretIdInput"))

    @builtins.property
    @jsii.member(jsii_name="skipVerifyInput")
    def skip_verify_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipVerifyInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "address"))

    @address.setter
    def address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0beabfec8d7dd5d694d2cef5d7bc866119587940ba297f965ed9e5822f413b7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e5de19b3060e54bb9c7fdcfe267e89508ed0eb9eb0184bd9cd17c3d40a7169d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authJwt")
    def auth_jwt(self) -> typing.Optional["NomadProviderAuthJwt"]:
        return typing.cast(typing.Optional["NomadProviderAuthJwt"], jsii.get(self, "authJwt"))

    @auth_jwt.setter
    def auth_jwt(self, value: typing.Optional["NomadProviderAuthJwt"]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2487e4cf8196958a9b24bec93d76bcfbd477c7c09a2d9f03cd14d7c96b3cd31a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authJwt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caFile")
    def ca_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caFile"))

    @ca_file.setter
    def ca_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aff273426dc241a2eb068c671e754330aaf4caecdbac2821e45b146e780d272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caPem")
    def ca_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPem"))

    @ca_pem.setter
    def ca_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65ff0fb31e2b5251e5cdbef8c962770de40031fdafb80d09b48167b6a056bded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certFile")
    def cert_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFile"))

    @cert_file.setter
    def cert_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf67e2c037b05499cfe0245de807dc78ac7dfd606e54bef3181c717ce8f027d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPem"))

    @cert_pem.setter
    def cert_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a34464dbc144eb2214380e5db8e2a958ee7a2b5c2f109aa24fbbf20d538fd2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]], jsii.get(self, "headers"))

    @headers.setter
    def headers(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a3f592752af918242782f6ea70217202671f5edcc341fcf80f1cbb08d18bac6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpAuth")
    def http_auth(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpAuth"))

    @http_auth.setter
    def http_auth(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c66bf4bc162a7eec972510b0510f85519cabd45b262100f9a2076b2c9e8a8c13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreEnvVars")
    def ignore_env_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]], jsii.get(self, "ignoreEnvVars"))

    @ignore_env_vars.setter
    def ignore_env_vars(
        self,
        value: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49719b0f0dbe22ef93291f5e0a62835d823f044ce61032f370f1ba1cba2868f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreEnvVars", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyFile")
    def key_file(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFile"))

    @key_file.setter
    def key_file(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__468babcbbdb16e5670b21e9f8eba58d5bcd8045ca7ed476d317c655d74c133dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyPem")
    def key_pem(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPem"))

    @key_pem.setter
    def key_pem(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cd3c41f2552a4146e96aabcb245bb4299fffa94adf0880356e26445462328d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b04a884d329f7dcafe6ca5f0f57fbab564e8d3bb90b7b3efb1f5d2b2ec4d60a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretId")
    def secret_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretId"))

    @secret_id.setter
    def secret_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a02d46d72fb1046bdbb99d51171a00c00913f2085971c13e6a975aa870e3694b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="skipVerify")
    def skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "skipVerify"))

    @skip_verify.setter
    def skip_verify(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24301788f020684a7feadc62b6c52e1d9000b49e1582ca38fae3a11048fbc5b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "skipVerify", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.provider.NomadProviderAuthJwt",
    jsii_struct_bases=[],
    name_mapping={"auth_method": "authMethod", "login_token": "loginToken"},
)
class NomadProviderAuthJwt:
    def __init__(self, *, auth_method: builtins.str, login_token: builtins.str) -> None:
        '''
        :param auth_method: The name of the auth method to use for login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#auth_method NomadProvider#auth_method}
        :param login_token: The externally issued authentication token to be exchanged for a Nomad ACL Token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#login_token NomadProvider#login_token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d88f2761eb4bc272c47c9a6697678a075d78894aad810a825b535ae78b51b2e)
            check_type(argname="argument auth_method", value=auth_method, expected_type=type_hints["auth_method"])
            check_type(argname="argument login_token", value=login_token, expected_type=type_hints["login_token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "auth_method": auth_method,
            "login_token": login_token,
        }

    @builtins.property
    def auth_method(self) -> builtins.str:
        '''The name of the auth method to use for login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#auth_method NomadProvider#auth_method}
        '''
        result = self._values.get("auth_method")
        assert result is not None, "Required property 'auth_method' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def login_token(self) -> builtins.str:
        '''The externally issued authentication token to be exchanged for a Nomad ACL Token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#login_token NomadProvider#login_token}
        '''
        result = self._values.get("login_token")
        assert result is not None, "Required property 'login_token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NomadProviderAuthJwt(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.provider.NomadProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "alias": "alias",
        "auth_jwt": "authJwt",
        "ca_file": "caFile",
        "ca_pem": "caPem",
        "cert_file": "certFile",
        "cert_pem": "certPem",
        "headers": "headers",
        "http_auth": "httpAuth",
        "ignore_env_vars": "ignoreEnvVars",
        "key_file": "keyFile",
        "key_pem": "keyPem",
        "region": "region",
        "secret_id": "secretId",
        "skip_verify": "skipVerify",
    },
)
class NomadProviderConfig:
    def __init__(
        self,
        *,
        address: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        auth_jwt: typing.Optional[typing.Union[NomadProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
        ca_file: typing.Optional[builtins.str] = None,
        ca_pem: typing.Optional[builtins.str] = None,
        cert_file: typing.Optional[builtins.str] = None,
        cert_pem: typing.Optional[builtins.str] = None,
        headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["NomadProviderHeaders", typing.Dict[builtins.str, typing.Any]]]]] = None,
        http_auth: typing.Optional[builtins.str] = None,
        ignore_env_vars: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]] = None,
        key_file: typing.Optional[builtins.str] = None,
        key_pem: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_id: typing.Optional[builtins.str] = None,
        skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param address: URL of the root of the target Nomad agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#address NomadProvider#address}
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#alias NomadProvider#alias}
        :param auth_jwt: auth_jwt block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#auth_jwt NomadProvider#auth_jwt}
        :param ca_file: A path to a PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_file NomadProvider#ca_file}
        :param ca_pem: PEM-encoded certificate authority used to verify the remote agent's certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_pem NomadProvider#ca_pem}
        :param cert_file: A path to a PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_file NomadProvider#cert_file}
        :param cert_pem: PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_pem NomadProvider#cert_pem}
        :param headers: headers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#headers NomadProvider#headers}
        :param http_auth: HTTP basic auth configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#http_auth NomadProvider#http_auth}
        :param ignore_env_vars: A set of environment variables that are ignored by the provider when configuring the Nomad API client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ignore_env_vars NomadProvider#ignore_env_vars}
        :param key_file: A path to a PEM-encoded private key, required if cert_file or cert_pem is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_file NomadProvider#key_file}
        :param key_pem: PEM-encoded private key, required if cert_file or cert_pem is specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_pem NomadProvider#key_pem}
        :param region: Region of the target Nomad agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#region NomadProvider#region}
        :param secret_id: ACL token secret for API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#secret_id NomadProvider#secret_id}
        :param skip_verify: Skip TLS verification on client side. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#skip_verify NomadProvider#skip_verify}
        '''
        if isinstance(auth_jwt, dict):
            auth_jwt = NomadProviderAuthJwt(**auth_jwt)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e759273490438086fe5dd3d88c084b63217b1cc6e133fcd010a5f3e4c7a37ada)
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument auth_jwt", value=auth_jwt, expected_type=type_hints["auth_jwt"])
            check_type(argname="argument ca_file", value=ca_file, expected_type=type_hints["ca_file"])
            check_type(argname="argument ca_pem", value=ca_pem, expected_type=type_hints["ca_pem"])
            check_type(argname="argument cert_file", value=cert_file, expected_type=type_hints["cert_file"])
            check_type(argname="argument cert_pem", value=cert_pem, expected_type=type_hints["cert_pem"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument http_auth", value=http_auth, expected_type=type_hints["http_auth"])
            check_type(argname="argument ignore_env_vars", value=ignore_env_vars, expected_type=type_hints["ignore_env_vars"])
            check_type(argname="argument key_file", value=key_file, expected_type=type_hints["key_file"])
            check_type(argname="argument key_pem", value=key_pem, expected_type=type_hints["key_pem"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument secret_id", value=secret_id, expected_type=type_hints["secret_id"])
            check_type(argname="argument skip_verify", value=skip_verify, expected_type=type_hints["skip_verify"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
        }
        if alias is not None:
            self._values["alias"] = alias
        if auth_jwt is not None:
            self._values["auth_jwt"] = auth_jwt
        if ca_file is not None:
            self._values["ca_file"] = ca_file
        if ca_pem is not None:
            self._values["ca_pem"] = ca_pem
        if cert_file is not None:
            self._values["cert_file"] = cert_file
        if cert_pem is not None:
            self._values["cert_pem"] = cert_pem
        if headers is not None:
            self._values["headers"] = headers
        if http_auth is not None:
            self._values["http_auth"] = http_auth
        if ignore_env_vars is not None:
            self._values["ignore_env_vars"] = ignore_env_vars
        if key_file is not None:
            self._values["key_file"] = key_file
        if key_pem is not None:
            self._values["key_pem"] = key_pem
        if region is not None:
            self._values["region"] = region
        if secret_id is not None:
            self._values["secret_id"] = secret_id
        if skip_verify is not None:
            self._values["skip_verify"] = skip_verify

    @builtins.property
    def address(self) -> builtins.str:
        '''URL of the root of the target Nomad agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#address NomadProvider#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#alias NomadProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def auth_jwt(self) -> typing.Optional[NomadProviderAuthJwt]:
        '''auth_jwt block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#auth_jwt NomadProvider#auth_jwt}
        '''
        result = self._values.get("auth_jwt")
        return typing.cast(typing.Optional[NomadProviderAuthJwt], result)

    @builtins.property
    def ca_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded certificate authority used to verify the remote agent's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_file NomadProvider#ca_file}
        '''
        result = self._values.get("ca_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded certificate authority used to verify the remote agent's certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ca_pem NomadProvider#ca_pem}
        '''
        result = self._values.get("ca_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_file NomadProvider#cert_file}
        '''
        result = self._values.get("cert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded certificate provided to the remote agent; requires use of key_file or key_pem.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#cert_pem NomadProvider#cert_pem}
        '''
        result = self._values.get("cert_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def headers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]]:
        '''headers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#headers NomadProvider#headers}
        '''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["NomadProviderHeaders"]]], result)

    @builtins.property
    def http_auth(self) -> typing.Optional[builtins.str]:
        '''HTTP basic auth configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#http_auth NomadProvider#http_auth}
        '''
        result = self._values.get("http_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ignore_env_vars(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]]:
        '''A set of environment variables that are ignored by the provider when configuring the Nomad API client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#ignore_env_vars NomadProvider#ignore_env_vars}
        '''
        result = self._values.get("ignore_env_vars")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]], result)

    @builtins.property
    def key_file(self) -> typing.Optional[builtins.str]:
        '''A path to a PEM-encoded private key, required if cert_file or cert_pem is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_file NomadProvider#key_file}
        '''
        result = self._values.get("key_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pem(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded private key, required if cert_file or cert_pem is specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#key_pem NomadProvider#key_pem}
        '''
        result = self._values.get("key_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region of the target Nomad agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#region NomadProvider#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_id(self) -> typing.Optional[builtins.str]:
        '''ACL token secret for API requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#secret_id NomadProvider#secret_id}
        '''
        result = self._values.get("secret_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_verify(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Skip TLS verification on client side.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#skip_verify NomadProvider#skip_verify}
        '''
        result = self._values.get("skip_verify")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NomadProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.provider.NomadProviderHeaders",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class NomadProviderHeaders:
    def __init__(self, *, name: builtins.str, value: builtins.str) -> None:
        '''
        :param name: The header name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#name NomadProvider#name}
        :param value: The header value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#value NomadProvider#value}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e77394e5bf2f9bd34a37f003dbe588118fddb6f74338ed48dcede78167deb3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The header name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#name NomadProvider#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''The header value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs#value NomadProvider#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NomadProviderHeaders(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "NomadProvider",
    "NomadProviderAuthJwt",
    "NomadProviderConfig",
    "NomadProviderHeaders",
]

publication.publish()

def _typecheckingstub__fa1135b3e0a6e5d3f7edfef684226a9a3ae7c144ae366e8b37d5ae425d916fff(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address: builtins.str,
    alias: typing.Optional[builtins.str] = None,
    auth_jwt: typing.Optional[typing.Union[NomadProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_file: typing.Optional[builtins.str] = None,
    ca_pem: typing.Optional[builtins.str] = None,
    cert_file: typing.Optional[builtins.str] = None,
    cert_pem: typing.Optional[builtins.str] = None,
    headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NomadProviderHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_auth: typing.Optional[builtins.str] = None,
    ignore_env_vars: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]] = None,
    key_file: typing.Optional[builtins.str] = None,
    key_pem: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secret_id: typing.Optional[builtins.str] = None,
    skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fe3e6bb963e9fe03449bc0ac46c50f7523599db7df7556b66b2f81ef712e9be(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0beabfec8d7dd5d694d2cef5d7bc866119587940ba297f965ed9e5822f413b7a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e5de19b3060e54bb9c7fdcfe267e89508ed0eb9eb0184bd9cd17c3d40a7169d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2487e4cf8196958a9b24bec93d76bcfbd477c7c09a2d9f03cd14d7c96b3cd31a(
    value: typing.Optional[NomadProviderAuthJwt],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aff273426dc241a2eb068c671e754330aaf4caecdbac2821e45b146e780d272(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65ff0fb31e2b5251e5cdbef8c962770de40031fdafb80d09b48167b6a056bded(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf67e2c037b05499cfe0245de807dc78ac7dfd606e54bef3181c717ce8f027d2(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a34464dbc144eb2214380e5db8e2a958ee7a2b5c2f109aa24fbbf20d538fd2e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3f592752af918242782f6ea70217202671f5edcc341fcf80f1cbb08d18bac6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[NomadProviderHeaders]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c66bf4bc162a7eec972510b0510f85519cabd45b262100f9a2076b2c9e8a8c13(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49719b0f0dbe22ef93291f5e0a62835d823f044ce61032f370f1ba1cba2868f2(
    value: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__468babcbbdb16e5670b21e9f8eba58d5bcd8045ca7ed476d317c655d74c133dd(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cd3c41f2552a4146e96aabcb245bb4299fffa94adf0880356e26445462328d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b04a884d329f7dcafe6ca5f0f57fbab564e8d3bb90b7b3efb1f5d2b2ec4d60a7(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a02d46d72fb1046bdbb99d51171a00c00913f2085971c13e6a975aa870e3694b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24301788f020684a7feadc62b6c52e1d9000b49e1582ca38fae3a11048fbc5b0(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d88f2761eb4bc272c47c9a6697678a075d78894aad810a825b535ae78b51b2e(
    *,
    auth_method: builtins.str,
    login_token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e759273490438086fe5dd3d88c084b63217b1cc6e133fcd010a5f3e4c7a37ada(
    *,
    address: builtins.str,
    alias: typing.Optional[builtins.str] = None,
    auth_jwt: typing.Optional[typing.Union[NomadProviderAuthJwt, typing.Dict[builtins.str, typing.Any]]] = None,
    ca_file: typing.Optional[builtins.str] = None,
    ca_pem: typing.Optional[builtins.str] = None,
    cert_file: typing.Optional[builtins.str] = None,
    cert_pem: typing.Optional[builtins.str] = None,
    headers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[NomadProviderHeaders, typing.Dict[builtins.str, typing.Any]]]]] = None,
    http_auth: typing.Optional[builtins.str] = None,
    ignore_env_vars: typing.Optional[typing.Mapping[builtins.str, typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]] = None,
    key_file: typing.Optional[builtins.str] = None,
    key_pem: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secret_id: typing.Optional[builtins.str] = None,
    skip_verify: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e77394e5bf2f9bd34a37f003dbe588118fddb6f74338ed48dcede78167deb3(
    *,
    name: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
