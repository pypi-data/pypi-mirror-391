r'''
# `nomad_acl_auth_method`

Refer to the Terraform Registry for docs: [`nomad_acl_auth_method`](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method).
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


class AclAuthMethod(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethod",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method nomad_acl_auth_method}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        config: typing.Union["AclAuthMethodConfigA", typing.Dict[builtins.str, typing.Any]],
        max_token_ttl: builtins.str,
        name: builtins.str,
        token_locality: builtins.str,
        type: builtins.str,
        default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        token_name_format: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method nomad_acl_auth_method} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#config AclAuthMethod#config}
        :param max_token_ttl: Defines the maximum life of a token created by this method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#max_token_ttl AclAuthMethod#max_token_ttl}
        :param name: The identifier of the ACL Auth Method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#name AclAuthMethod#name}
        :param token_locality: Defines whether the ACL Auth Method creates a local or global token when performing SSO login. This field must be set to either "local" or "global". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_locality AclAuthMethod#token_locality}
        :param type: ACL Auth Method SSO workflow type. Currently, the only supported type is "OIDC.". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#type AclAuthMethod#type}
        :param default: Defines whether this ACL Auth Method is to be set as default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#default AclAuthMethod#default}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#id AclAuthMethod#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param token_name_format: Defines the token format for the authenticated users. This can be lightly templated using HIL '${foo}' syntax. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_name_format AclAuthMethod#token_name_format}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88e5e1175a243f6912e5cc0a978f498ad783f5331b4aa12703ed9829e4b6f791)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = AclAuthMethodConfig(
            config=config,
            max_token_ttl=max_token_ttl,
            name=name,
            token_locality=token_locality,
            type=type,
            default=default,
            id=id,
            token_name_format=token_name_format,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a AclAuthMethod resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AclAuthMethod to import.
        :param import_from_id: The id of the existing AclAuthMethod that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AclAuthMethod to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e991f027a417fd71ec449e59eab0028db7d507dd7c20c4f784bf7f4886353db)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_issuer: typing.Optional[typing.Sequence[builtins.str]] = None,
        claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        clock_skew_leeway: typing.Optional[builtins.str] = None,
        discovery_ca_pem: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration_leeway: typing.Optional[builtins.str] = None,
        jwks_ca_cert: typing.Optional[builtins.str] = None,
        jwks_url: typing.Optional[builtins.str] = None,
        jwt_validation_pub_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        list_claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        not_before_leeway: typing.Optional[builtins.str] = None,
        oidc_client_assertion: typing.Optional[typing.Union["AclAuthMethodConfigOidcClientAssertion", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc_client_id: typing.Optional[builtins.str] = None,
        oidc_client_secret: typing.Optional[builtins.str] = None,
        oidc_disable_userinfo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_discovery_url: typing.Optional[builtins.str] = None,
        oidc_enable_pkce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        signing_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
        verbose_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param allowed_redirect_uris: A list of allowed values that can be used for the redirect URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#allowed_redirect_uris AclAuthMethod#allowed_redirect_uris}
        :param bound_audiences: List of auth claims that are valid for login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_audiences AclAuthMethod#bound_audiences}
        :param bound_issuer: The value against which to match the iss claim in a JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_issuer AclAuthMethod#bound_issuer}
        :param claim_mappings: Mappings of claims (key) that will be copied to a metadata field (value). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#claim_mappings AclAuthMethod#claim_mappings}
        :param clock_skew_leeway: Duration of leeway when validating all claims in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#clock_skew_leeway AclAuthMethod#clock_skew_leeway}
        :param discovery_ca_pem: PEM encoded CA certs for use by the TLS client used to talk with the OIDC Discovery URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#discovery_ca_pem AclAuthMethod#discovery_ca_pem}
        :param expiration_leeway: Duration of leeway when validating expiration of a JWT in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#expiration_leeway AclAuthMethod#expiration_leeway}
        :param jwks_ca_cert: PEM encoded CA cert for use by the TLS client used to talk with the JWKS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_ca_cert AclAuthMethod#jwks_ca_cert}
        :param jwks_url: JSON Web Key Sets url for authenticating signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_url AclAuthMethod#jwks_url}
        :param jwt_validation_pub_keys: List of PEM-encoded public keys to use to authenticate signatures locally. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwt_validation_pub_keys AclAuthMethod#jwt_validation_pub_keys}
        :param list_claim_mappings: Mappings of list claims (key) that will be copied to a metadata field (value). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#list_claim_mappings AclAuthMethod#list_claim_mappings}
        :param not_before_leeway: Duration of leeway when validating not before values of a token in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#not_before_leeway AclAuthMethod#not_before_leeway}
        :param oidc_client_assertion: oidc_client_assertion block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_assertion AclAuthMethod#oidc_client_assertion}
        :param oidc_client_id: The OAuth Client ID configured with the OIDC provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_id AclAuthMethod#oidc_client_id}
        :param oidc_client_secret: The OAuth Client Secret configured with the OIDC provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_secret AclAuthMethod#oidc_client_secret}
        :param oidc_disable_userinfo: Nomad will not make a request to the identity provider to get OIDC UserInfo. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_disable_userinfo AclAuthMethod#oidc_disable_userinfo}
        :param oidc_discovery_url: The OIDC Discovery URL, without any .well-known component (base path). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_discovery_url AclAuthMethod#oidc_discovery_url}
        :param oidc_enable_pkce: Nomad include PKCE challenge in OIDC auth requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_enable_pkce AclAuthMethod#oidc_enable_pkce}
        :param oidc_scopes: List of OIDC scopes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_scopes AclAuthMethod#oidc_scopes}
        :param signing_algs: A list of supported signing algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#signing_algs AclAuthMethod#signing_algs}
        :param verbose_logging: Enable OIDC verbose logging on the Nomad server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#verbose_logging AclAuthMethod#verbose_logging}
        '''
        value = AclAuthMethodConfigA(
            allowed_redirect_uris=allowed_redirect_uris,
            bound_audiences=bound_audiences,
            bound_issuer=bound_issuer,
            claim_mappings=claim_mappings,
            clock_skew_leeway=clock_skew_leeway,
            discovery_ca_pem=discovery_ca_pem,
            expiration_leeway=expiration_leeway,
            jwks_ca_cert=jwks_ca_cert,
            jwks_url=jwks_url,
            jwt_validation_pub_keys=jwt_validation_pub_keys,
            list_claim_mappings=list_claim_mappings,
            not_before_leeway=not_before_leeway,
            oidc_client_assertion=oidc_client_assertion,
            oidc_client_id=oidc_client_id,
            oidc_client_secret=oidc_client_secret,
            oidc_disable_userinfo=oidc_disable_userinfo,
            oidc_discovery_url=oidc_discovery_url,
            oidc_enable_pkce=oidc_enable_pkce,
            oidc_scopes=oidc_scopes,
            signing_algs=signing_algs,
            verbose_logging=verbose_logging,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetDefault")
    def reset_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefault", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTokenNameFormat")
    def reset_token_name_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenNameFormat", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "AclAuthMethodConfigAOutputReference":
        return typing.cast("AclAuthMethodConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["AclAuthMethodConfigA"]:
        return typing.cast(typing.Optional["AclAuthMethodConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultInput")
    def default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "defaultInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTokenTtlInput")
    def max_token_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxTokenTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenLocalityInput")
    def token_locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenLocalityInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenNameFormatInput")
    def token_name_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenNameFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "default"))

    @default.setter
    def default(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__874f660ea3ddbf1c73fffeaab17d193d5e6d48ff3f5f8716bd9ddcc49cb94edf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f32dde41415211740dd5a6c9ef230400f520d9a34ce1df7ed9ff0102fa386149)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTokenTtl")
    def max_token_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxTokenTtl"))

    @max_token_ttl.setter
    def max_token_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be346925ec08d59afc244cdf08358c5cddc35c9a6481a1575c62add0de39591f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTokenTtl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0366dc74861723b8324b57cbbfafb5d109b3951b4d5f721069d5a334f158249)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenLocality")
    def token_locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenLocality"))

    @token_locality.setter
    def token_locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a47177f31deef12a5653bec19bfc71cf83a83f71c0ac42083a67d7ffa1982df1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenLocality", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokenNameFormat")
    def token_name_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenNameFormat"))

    @token_name_format.setter
    def token_name_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e037d609120502442e896f26318c9012a7e84f4c5903793789947743a6351be0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenNameFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff887f1006e7e39f2298eebc35f93c98f81c647f24c0c9dedc3bfd3ff3f17e3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "max_token_ttl": "maxTokenTtl",
        "name": "name",
        "token_locality": "tokenLocality",
        "type": "type",
        "default": "default",
        "id": "id",
        "token_name_format": "tokenNameFormat",
    },
)
class AclAuthMethodConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: typing.Union["AclAuthMethodConfigA", typing.Dict[builtins.str, typing.Any]],
        max_token_ttl: builtins.str,
        name: builtins.str,
        token_locality: builtins.str,
        type: builtins.str,
        default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        token_name_format: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#config AclAuthMethod#config}
        :param max_token_ttl: Defines the maximum life of a token created by this method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#max_token_ttl AclAuthMethod#max_token_ttl}
        :param name: The identifier of the ACL Auth Method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#name AclAuthMethod#name}
        :param token_locality: Defines whether the ACL Auth Method creates a local or global token when performing SSO login. This field must be set to either "local" or "global". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_locality AclAuthMethod#token_locality}
        :param type: ACL Auth Method SSO workflow type. Currently, the only supported type is "OIDC.". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#type AclAuthMethod#type}
        :param default: Defines whether this ACL Auth Method is to be set as default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#default AclAuthMethod#default}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#id AclAuthMethod#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param token_name_format: Defines the token format for the authenticated users. This can be lightly templated using HIL '${foo}' syntax. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_name_format AclAuthMethod#token_name_format}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = AclAuthMethodConfigA(**config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ef4f91358041c3bf59857d24ac90f1be8c39fc9517b566fbfaeb4e118df2d44)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument max_token_ttl", value=max_token_ttl, expected_type=type_hints["max_token_ttl"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument token_locality", value=token_locality, expected_type=type_hints["token_locality"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument default", value=default, expected_type=type_hints["default"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument token_name_format", value=token_name_format, expected_type=type_hints["token_name_format"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "max_token_ttl": max_token_ttl,
            "name": name,
            "token_locality": token_locality,
            "type": type,
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
        if default is not None:
            self._values["default"] = default
        if id is not None:
            self._values["id"] = id
        if token_name_format is not None:
            self._values["token_name_format"] = token_name_format

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
    def config(self) -> "AclAuthMethodConfigA":
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#config AclAuthMethod#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("AclAuthMethodConfigA", result)

    @builtins.property
    def max_token_ttl(self) -> builtins.str:
        '''Defines the maximum life of a token created by this method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#max_token_ttl AclAuthMethod#max_token_ttl}
        '''
        result = self._values.get("max_token_ttl")
        assert result is not None, "Required property 'max_token_ttl' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The identifier of the ACL Auth Method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#name AclAuthMethod#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def token_locality(self) -> builtins.str:
        '''Defines whether the ACL Auth Method creates a local or global token when performing SSO login.

        This field must be set to either "local" or "global".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_locality AclAuthMethod#token_locality}
        '''
        result = self._values.get("token_locality")
        assert result is not None, "Required property 'token_locality' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''ACL Auth Method SSO workflow type. Currently, the only supported type is "OIDC.".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#type AclAuthMethod#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Defines whether this ACL Auth Method is to be set as default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#default AclAuthMethod#default}
        '''
        result = self._values.get("default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#id AclAuthMethod#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_name_format(self) -> typing.Optional[builtins.str]:
        '''Defines the token format for the authenticated users. This can be lightly templated using HIL '${foo}' syntax.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#token_name_format AclAuthMethod#token_name_format}
        '''
        result = self._values.get("token_name_format")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclAuthMethodConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_redirect_uris": "allowedRedirectUris",
        "bound_audiences": "boundAudiences",
        "bound_issuer": "boundIssuer",
        "claim_mappings": "claimMappings",
        "clock_skew_leeway": "clockSkewLeeway",
        "discovery_ca_pem": "discoveryCaPem",
        "expiration_leeway": "expirationLeeway",
        "jwks_ca_cert": "jwksCaCert",
        "jwks_url": "jwksUrl",
        "jwt_validation_pub_keys": "jwtValidationPubKeys",
        "list_claim_mappings": "listClaimMappings",
        "not_before_leeway": "notBeforeLeeway",
        "oidc_client_assertion": "oidcClientAssertion",
        "oidc_client_id": "oidcClientId",
        "oidc_client_secret": "oidcClientSecret",
        "oidc_disable_userinfo": "oidcDisableUserinfo",
        "oidc_discovery_url": "oidcDiscoveryUrl",
        "oidc_enable_pkce": "oidcEnablePkce",
        "oidc_scopes": "oidcScopes",
        "signing_algs": "signingAlgs",
        "verbose_logging": "verboseLogging",
    },
)
class AclAuthMethodConfigA:
    def __init__(
        self,
        *,
        allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_issuer: typing.Optional[typing.Sequence[builtins.str]] = None,
        claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        clock_skew_leeway: typing.Optional[builtins.str] = None,
        discovery_ca_pem: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration_leeway: typing.Optional[builtins.str] = None,
        jwks_ca_cert: typing.Optional[builtins.str] = None,
        jwks_url: typing.Optional[builtins.str] = None,
        jwt_validation_pub_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        list_claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        not_before_leeway: typing.Optional[builtins.str] = None,
        oidc_client_assertion: typing.Optional[typing.Union["AclAuthMethodConfigOidcClientAssertion", typing.Dict[builtins.str, typing.Any]]] = None,
        oidc_client_id: typing.Optional[builtins.str] = None,
        oidc_client_secret: typing.Optional[builtins.str] = None,
        oidc_disable_userinfo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_discovery_url: typing.Optional[builtins.str] = None,
        oidc_enable_pkce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        signing_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
        verbose_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param allowed_redirect_uris: A list of allowed values that can be used for the redirect URI. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#allowed_redirect_uris AclAuthMethod#allowed_redirect_uris}
        :param bound_audiences: List of auth claims that are valid for login. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_audiences AclAuthMethod#bound_audiences}
        :param bound_issuer: The value against which to match the iss claim in a JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_issuer AclAuthMethod#bound_issuer}
        :param claim_mappings: Mappings of claims (key) that will be copied to a metadata field (value). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#claim_mappings AclAuthMethod#claim_mappings}
        :param clock_skew_leeway: Duration of leeway when validating all claims in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#clock_skew_leeway AclAuthMethod#clock_skew_leeway}
        :param discovery_ca_pem: PEM encoded CA certs for use by the TLS client used to talk with the OIDC Discovery URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#discovery_ca_pem AclAuthMethod#discovery_ca_pem}
        :param expiration_leeway: Duration of leeway when validating expiration of a JWT in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#expiration_leeway AclAuthMethod#expiration_leeway}
        :param jwks_ca_cert: PEM encoded CA cert for use by the TLS client used to talk with the JWKS server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_ca_cert AclAuthMethod#jwks_ca_cert}
        :param jwks_url: JSON Web Key Sets url for authenticating signatures. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_url AclAuthMethod#jwks_url}
        :param jwt_validation_pub_keys: List of PEM-encoded public keys to use to authenticate signatures locally. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwt_validation_pub_keys AclAuthMethod#jwt_validation_pub_keys}
        :param list_claim_mappings: Mappings of list claims (key) that will be copied to a metadata field (value). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#list_claim_mappings AclAuthMethod#list_claim_mappings}
        :param not_before_leeway: Duration of leeway when validating not before values of a token in the form of a time duration such as "5m" or "1h". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#not_before_leeway AclAuthMethod#not_before_leeway}
        :param oidc_client_assertion: oidc_client_assertion block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_assertion AclAuthMethod#oidc_client_assertion}
        :param oidc_client_id: The OAuth Client ID configured with the OIDC provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_id AclAuthMethod#oidc_client_id}
        :param oidc_client_secret: The OAuth Client Secret configured with the OIDC provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_secret AclAuthMethod#oidc_client_secret}
        :param oidc_disable_userinfo: Nomad will not make a request to the identity provider to get OIDC UserInfo. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_disable_userinfo AclAuthMethod#oidc_disable_userinfo}
        :param oidc_discovery_url: The OIDC Discovery URL, without any .well-known component (base path). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_discovery_url AclAuthMethod#oidc_discovery_url}
        :param oidc_enable_pkce: Nomad include PKCE challenge in OIDC auth requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_enable_pkce AclAuthMethod#oidc_enable_pkce}
        :param oidc_scopes: List of OIDC scopes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_scopes AclAuthMethod#oidc_scopes}
        :param signing_algs: A list of supported signing algorithms. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#signing_algs AclAuthMethod#signing_algs}
        :param verbose_logging: Enable OIDC verbose logging on the Nomad server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#verbose_logging AclAuthMethod#verbose_logging}
        '''
        if isinstance(oidc_client_assertion, dict):
            oidc_client_assertion = AclAuthMethodConfigOidcClientAssertion(**oidc_client_assertion)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdf814662741aef41134aaad0673de2654a0b04aa478103f3a5714ba9205daa8)
            check_type(argname="argument allowed_redirect_uris", value=allowed_redirect_uris, expected_type=type_hints["allowed_redirect_uris"])
            check_type(argname="argument bound_audiences", value=bound_audiences, expected_type=type_hints["bound_audiences"])
            check_type(argname="argument bound_issuer", value=bound_issuer, expected_type=type_hints["bound_issuer"])
            check_type(argname="argument claim_mappings", value=claim_mappings, expected_type=type_hints["claim_mappings"])
            check_type(argname="argument clock_skew_leeway", value=clock_skew_leeway, expected_type=type_hints["clock_skew_leeway"])
            check_type(argname="argument discovery_ca_pem", value=discovery_ca_pem, expected_type=type_hints["discovery_ca_pem"])
            check_type(argname="argument expiration_leeway", value=expiration_leeway, expected_type=type_hints["expiration_leeway"])
            check_type(argname="argument jwks_ca_cert", value=jwks_ca_cert, expected_type=type_hints["jwks_ca_cert"])
            check_type(argname="argument jwks_url", value=jwks_url, expected_type=type_hints["jwks_url"])
            check_type(argname="argument jwt_validation_pub_keys", value=jwt_validation_pub_keys, expected_type=type_hints["jwt_validation_pub_keys"])
            check_type(argname="argument list_claim_mappings", value=list_claim_mappings, expected_type=type_hints["list_claim_mappings"])
            check_type(argname="argument not_before_leeway", value=not_before_leeway, expected_type=type_hints["not_before_leeway"])
            check_type(argname="argument oidc_client_assertion", value=oidc_client_assertion, expected_type=type_hints["oidc_client_assertion"])
            check_type(argname="argument oidc_client_id", value=oidc_client_id, expected_type=type_hints["oidc_client_id"])
            check_type(argname="argument oidc_client_secret", value=oidc_client_secret, expected_type=type_hints["oidc_client_secret"])
            check_type(argname="argument oidc_disable_userinfo", value=oidc_disable_userinfo, expected_type=type_hints["oidc_disable_userinfo"])
            check_type(argname="argument oidc_discovery_url", value=oidc_discovery_url, expected_type=type_hints["oidc_discovery_url"])
            check_type(argname="argument oidc_enable_pkce", value=oidc_enable_pkce, expected_type=type_hints["oidc_enable_pkce"])
            check_type(argname="argument oidc_scopes", value=oidc_scopes, expected_type=type_hints["oidc_scopes"])
            check_type(argname="argument signing_algs", value=signing_algs, expected_type=type_hints["signing_algs"])
            check_type(argname="argument verbose_logging", value=verbose_logging, expected_type=type_hints["verbose_logging"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_redirect_uris is not None:
            self._values["allowed_redirect_uris"] = allowed_redirect_uris
        if bound_audiences is not None:
            self._values["bound_audiences"] = bound_audiences
        if bound_issuer is not None:
            self._values["bound_issuer"] = bound_issuer
        if claim_mappings is not None:
            self._values["claim_mappings"] = claim_mappings
        if clock_skew_leeway is not None:
            self._values["clock_skew_leeway"] = clock_skew_leeway
        if discovery_ca_pem is not None:
            self._values["discovery_ca_pem"] = discovery_ca_pem
        if expiration_leeway is not None:
            self._values["expiration_leeway"] = expiration_leeway
        if jwks_ca_cert is not None:
            self._values["jwks_ca_cert"] = jwks_ca_cert
        if jwks_url is not None:
            self._values["jwks_url"] = jwks_url
        if jwt_validation_pub_keys is not None:
            self._values["jwt_validation_pub_keys"] = jwt_validation_pub_keys
        if list_claim_mappings is not None:
            self._values["list_claim_mappings"] = list_claim_mappings
        if not_before_leeway is not None:
            self._values["not_before_leeway"] = not_before_leeway
        if oidc_client_assertion is not None:
            self._values["oidc_client_assertion"] = oidc_client_assertion
        if oidc_client_id is not None:
            self._values["oidc_client_id"] = oidc_client_id
        if oidc_client_secret is not None:
            self._values["oidc_client_secret"] = oidc_client_secret
        if oidc_disable_userinfo is not None:
            self._values["oidc_disable_userinfo"] = oidc_disable_userinfo
        if oidc_discovery_url is not None:
            self._values["oidc_discovery_url"] = oidc_discovery_url
        if oidc_enable_pkce is not None:
            self._values["oidc_enable_pkce"] = oidc_enable_pkce
        if oidc_scopes is not None:
            self._values["oidc_scopes"] = oidc_scopes
        if signing_algs is not None:
            self._values["signing_algs"] = signing_algs
        if verbose_logging is not None:
            self._values["verbose_logging"] = verbose_logging

    @builtins.property
    def allowed_redirect_uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of allowed values that can be used for the redirect URI.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#allowed_redirect_uris AclAuthMethod#allowed_redirect_uris}
        '''
        result = self._values.get("allowed_redirect_uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_audiences(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of auth claims that are valid for login.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_audiences AclAuthMethod#bound_audiences}
        '''
        result = self._values.get("bound_audiences")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_issuer(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The value against which to match the iss claim in a JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#bound_issuer AclAuthMethod#bound_issuer}
        '''
        result = self._values.get("bound_issuer")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def claim_mappings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Mappings of claims (key) that will be copied to a metadata field (value).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#claim_mappings AclAuthMethod#claim_mappings}
        '''
        result = self._values.get("claim_mappings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def clock_skew_leeway(self) -> typing.Optional[builtins.str]:
        '''Duration of leeway when validating all claims in the form of a time duration such as "5m" or "1h".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#clock_skew_leeway AclAuthMethod#clock_skew_leeway}
        '''
        result = self._values.get("clock_skew_leeway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def discovery_ca_pem(self) -> typing.Optional[typing.List[builtins.str]]:
        '''PEM encoded CA certs for use by the TLS client used to talk with the OIDC Discovery URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#discovery_ca_pem AclAuthMethod#discovery_ca_pem}
        '''
        result = self._values.get("discovery_ca_pem")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expiration_leeway(self) -> typing.Optional[builtins.str]:
        '''Duration of leeway when validating expiration of a JWT in the form of a time duration such as "5m" or "1h".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#expiration_leeway AclAuthMethod#expiration_leeway}
        '''
        result = self._values.get("expiration_leeway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_ca_cert(self) -> typing.Optional[builtins.str]:
        '''PEM encoded CA cert for use by the TLS client used to talk with the JWKS server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_ca_cert AclAuthMethod#jwks_ca_cert}
        '''
        result = self._values.get("jwks_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_url(self) -> typing.Optional[builtins.str]:
        '''JSON Web Key Sets url for authenticating signatures.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwks_url AclAuthMethod#jwks_url}
        '''
        result = self._values.get("jwks_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_validation_pub_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of PEM-encoded public keys to use to authenticate signatures locally.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#jwt_validation_pub_keys AclAuthMethod#jwt_validation_pub_keys}
        '''
        result = self._values.get("jwt_validation_pub_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def list_claim_mappings(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Mappings of list claims (key) that will be copied to a metadata field (value).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#list_claim_mappings AclAuthMethod#list_claim_mappings}
        '''
        result = self._values.get("list_claim_mappings")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def not_before_leeway(self) -> typing.Optional[builtins.str]:
        '''Duration of leeway when validating not before values of a token in the form of a time duration such as "5m" or "1h".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#not_before_leeway AclAuthMethod#not_before_leeway}
        '''
        result = self._values.get("not_before_leeway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_client_assertion(
        self,
    ) -> typing.Optional["AclAuthMethodConfigOidcClientAssertion"]:
        '''oidc_client_assertion block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_assertion AclAuthMethod#oidc_client_assertion}
        '''
        result = self._values.get("oidc_client_assertion")
        return typing.cast(typing.Optional["AclAuthMethodConfigOidcClientAssertion"], result)

    @builtins.property
    def oidc_client_id(self) -> typing.Optional[builtins.str]:
        '''The OAuth Client ID configured with the OIDC provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_id AclAuthMethod#oidc_client_id}
        '''
        result = self._values.get("oidc_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_client_secret(self) -> typing.Optional[builtins.str]:
        '''The OAuth Client Secret configured with the OIDC provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_client_secret AclAuthMethod#oidc_client_secret}
        '''
        result = self._values.get("oidc_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_disable_userinfo(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Nomad will not make a request to the identity provider to get OIDC UserInfo.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_disable_userinfo AclAuthMethod#oidc_disable_userinfo}
        '''
        result = self._values.get("oidc_disable_userinfo")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oidc_discovery_url(self) -> typing.Optional[builtins.str]:
        '''The OIDC Discovery URL, without any .well-known component (base path).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_discovery_url AclAuthMethod#oidc_discovery_url}
        '''
        result = self._values.get("oidc_discovery_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def oidc_enable_pkce(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Nomad include PKCE challenge in OIDC auth requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_enable_pkce AclAuthMethod#oidc_enable_pkce}
        '''
        result = self._values.get("oidc_enable_pkce")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oidc_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of OIDC scopes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#oidc_scopes AclAuthMethod#oidc_scopes}
        '''
        result = self._values.get("oidc_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def signing_algs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of supported signing algorithms.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#signing_algs AclAuthMethod#signing_algs}
        '''
        result = self._values.get("signing_algs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def verbose_logging(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable OIDC verbose logging on the Nomad server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#verbose_logging AclAuthMethod#verbose_logging}
        '''
        result = self._values.get("verbose_logging")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclAuthMethodConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AclAuthMethodConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigAOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e1f3cb6d40cd42ba3feb184212321b36f13a09ad639358b7f94f04fc0b55e92)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putOidcClientAssertion")
    def put_oidc_client_assertion(
        self,
        *,
        key_source: builtins.str,
        audience: typing.Optional[typing.Sequence[builtins.str]] = None,
        extra_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[typing.Union["AclAuthMethodConfigOidcClientAssertionPrivateKey", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param key_source: The source of the key Nomad will use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_source AclAuthMethod#key_source}
        :param audience: List of audiences to accept the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#audience AclAuthMethod#audience}
        :param extra_headers: Additional headers to include on the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#extra_headers AclAuthMethod#extra_headers}
        :param key_algorithm: Algorithm of the key used to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_algorithm AclAuthMethod#key_algorithm}
        :param private_key: private_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#private_key AclAuthMethod#private_key}
        '''
        value = AclAuthMethodConfigOidcClientAssertion(
            key_source=key_source,
            audience=audience,
            extra_headers=extra_headers,
            key_algorithm=key_algorithm,
            private_key=private_key,
        )

        return typing.cast(None, jsii.invoke(self, "putOidcClientAssertion", [value]))

    @jsii.member(jsii_name="resetAllowedRedirectUris")
    def reset_allowed_redirect_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedRedirectUris", []))

    @jsii.member(jsii_name="resetBoundAudiences")
    def reset_bound_audiences(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundAudiences", []))

    @jsii.member(jsii_name="resetBoundIssuer")
    def reset_bound_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIssuer", []))

    @jsii.member(jsii_name="resetClaimMappings")
    def reset_claim_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClaimMappings", []))

    @jsii.member(jsii_name="resetClockSkewLeeway")
    def reset_clock_skew_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClockSkewLeeway", []))

    @jsii.member(jsii_name="resetDiscoveryCaPem")
    def reset_discovery_ca_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiscoveryCaPem", []))

    @jsii.member(jsii_name="resetExpirationLeeway")
    def reset_expiration_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationLeeway", []))

    @jsii.member(jsii_name="resetJwksCaCert")
    def reset_jwks_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksCaCert", []))

    @jsii.member(jsii_name="resetJwksUrl")
    def reset_jwks_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksUrl", []))

    @jsii.member(jsii_name="resetJwtValidationPubKeys")
    def reset_jwt_validation_pub_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtValidationPubKeys", []))

    @jsii.member(jsii_name="resetListClaimMappings")
    def reset_list_claim_mappings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetListClaimMappings", []))

    @jsii.member(jsii_name="resetNotBeforeLeeway")
    def reset_not_before_leeway(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotBeforeLeeway", []))

    @jsii.member(jsii_name="resetOidcClientAssertion")
    def reset_oidc_client_assertion(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcClientAssertion", []))

    @jsii.member(jsii_name="resetOidcClientId")
    def reset_oidc_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcClientId", []))

    @jsii.member(jsii_name="resetOidcClientSecret")
    def reset_oidc_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcClientSecret", []))

    @jsii.member(jsii_name="resetOidcDisableUserinfo")
    def reset_oidc_disable_userinfo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcDisableUserinfo", []))

    @jsii.member(jsii_name="resetOidcDiscoveryUrl")
    def reset_oidc_discovery_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcDiscoveryUrl", []))

    @jsii.member(jsii_name="resetOidcEnablePkce")
    def reset_oidc_enable_pkce(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcEnablePkce", []))

    @jsii.member(jsii_name="resetOidcScopes")
    def reset_oidc_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOidcScopes", []))

    @jsii.member(jsii_name="resetSigningAlgs")
    def reset_signing_algs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSigningAlgs", []))

    @jsii.member(jsii_name="resetVerboseLogging")
    def reset_verbose_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerboseLogging", []))

    @builtins.property
    @jsii.member(jsii_name="oidcClientAssertion")
    def oidc_client_assertion(
        self,
    ) -> "AclAuthMethodConfigOidcClientAssertionOutputReference":
        return typing.cast("AclAuthMethodConfigOidcClientAssertionOutputReference", jsii.get(self, "oidcClientAssertion"))

    @builtins.property
    @jsii.member(jsii_name="allowedRedirectUrisInput")
    def allowed_redirect_uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedRedirectUrisInput"))

    @builtins.property
    @jsii.member(jsii_name="boundAudiencesInput")
    def bound_audiences_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundAudiencesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIssuerInput")
    def bound_issuer_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="claimMappingsInput")
    def claim_mappings_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "claimMappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="clockSkewLeewayInput")
    def clock_skew_leeway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clockSkewLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="discoveryCaPemInput")
    def discovery_ca_pem_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "discoveryCaPemInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationLeewayInput")
    def expiration_leeway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expirationLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksCaCertInput")
    def jwks_ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksCaCertInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksUrlInput")
    def jwks_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtValidationPubKeysInput")
    def jwt_validation_pub_keys_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "jwtValidationPubKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="listClaimMappingsInput")
    def list_claim_mappings_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "listClaimMappingsInput"))

    @builtins.property
    @jsii.member(jsii_name="notBeforeLeewayInput")
    def not_before_leeway_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notBeforeLeewayInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcClientAssertionInput")
    def oidc_client_assertion_input(
        self,
    ) -> typing.Optional["AclAuthMethodConfigOidcClientAssertion"]:
        return typing.cast(typing.Optional["AclAuthMethodConfigOidcClientAssertion"], jsii.get(self, "oidcClientAssertionInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcClientIdInput")
    def oidc_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcClientSecretInput")
    def oidc_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcDisableUserinfoInput")
    def oidc_disable_userinfo_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "oidcDisableUserinfoInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryUrlInput")
    def oidc_discovery_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "oidcDiscoveryUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcEnablePkceInput")
    def oidc_enable_pkce_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "oidcEnablePkceInput"))

    @builtins.property
    @jsii.member(jsii_name="oidcScopesInput")
    def oidc_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "oidcScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="signingAlgsInput")
    def signing_algs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "signingAlgsInput"))

    @builtins.property
    @jsii.member(jsii_name="verboseLoggingInput")
    def verbose_logging_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "verboseLoggingInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedRedirectUris")
    def allowed_redirect_uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedRedirectUris"))

    @allowed_redirect_uris.setter
    def allowed_redirect_uris(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f3813ddd9811f2f8521e5e70f2d8c7f4b27729883a58964148ad311454b2c3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedRedirectUris", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundAudiences")
    def bound_audiences(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundAudiences"))

    @bound_audiences.setter
    def bound_audiences(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e1abdfdaf8b95e8ca43bc15656db572b05f1cb080c37fb19e8c8f3ac4413c2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundAudiences", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="boundIssuer")
    def bound_issuer(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIssuer"))

    @bound_issuer.setter
    def bound_issuer(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e29f20cd6fc2b94bfcb10ecaf7387e52b2a7f0cdc0bc5ccdf3c62c3632ef402b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIssuer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="claimMappings")
    def claim_mappings(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "claimMappings"))

    @claim_mappings.setter
    def claim_mappings(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e0fc8cf67658e546bdc1303d703b65d49f3ffeda2a8f6b487e2aaa8bf88e4f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "claimMappings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clockSkewLeeway")
    def clock_skew_leeway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clockSkewLeeway"))

    @clock_skew_leeway.setter
    def clock_skew_leeway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__942356060cac8dedd5234e4930d16a354f986f83089741f49a0fd5045334c5a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clockSkewLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="discoveryCaPem")
    def discovery_ca_pem(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "discoveryCaPem"))

    @discovery_ca_pem.setter
    def discovery_ca_pem(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a51fc63187bc29f2e6cd275c276dcbe940a867f9d5ec431d74bcff44168ddd7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "discoveryCaPem", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expirationLeeway")
    def expiration_leeway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationLeeway"))

    @expiration_leeway.setter
    def expiration_leeway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5de0a2b519a404d21cd872814a3a4d1ca241d943230cf5582dbd48e308e1027)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwksCaCert")
    def jwks_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksCaCert"))

    @jwks_ca_cert.setter
    def jwks_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b258b525265eb224fb7015fd114eccff385f9761d23bf4859cd10df022a51523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksCaCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwksUrl")
    def jwks_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksUrl"))

    @jwks_url.setter
    def jwks_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36818c3b205c541ffeddd31985fa8aae3a93ff88775ae553fcdc56a182a380fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jwtValidationPubKeys")
    def jwt_validation_pub_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "jwtValidationPubKeys"))

    @jwt_validation_pub_keys.setter
    def jwt_validation_pub_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58e2a846c9d0b386bdabd2f9cea149262d7c104f373080989d2423f73c34f572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtValidationPubKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="listClaimMappings")
    def list_claim_mappings(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "listClaimMappings"))

    @list_claim_mappings.setter
    def list_claim_mappings(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4516d781fe1e8bc8f518f37d26716577836564c44e443db3c7f8379f98c45fc5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "listClaimMappings", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notBeforeLeeway")
    def not_before_leeway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBeforeLeeway"))

    @not_before_leeway.setter
    def not_before_leeway(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d522db3980259b05977d8a6c334bb4cd8903b28ee05ead77e00c38a790cf5cb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notBeforeLeeway", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcClientId")
    def oidc_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcClientId"))

    @oidc_client_id.setter
    def oidc_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fee9aac5ec2f4252aff0c8419dcd9c9d23379996c4af771af47a690e5b4fab6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcClientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcClientSecret")
    def oidc_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcClientSecret"))

    @oidc_client_secret.setter
    def oidc_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f006e856f57ebc1f767bbf60bab9bfb1bd05f7062fd99b700c07531ffdb2077e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcClientSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcDisableUserinfo")
    def oidc_disable_userinfo(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "oidcDisableUserinfo"))

    @oidc_disable_userinfo.setter
    def oidc_disable_userinfo(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62198682fb26c4c8caf9023906575997dd9b1081bff045ba59bf86fc3c28df9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcDisableUserinfo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcDiscoveryUrl")
    def oidc_discovery_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oidcDiscoveryUrl"))

    @oidc_discovery_url.setter
    def oidc_discovery_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d08fc806e59b4b273f16d87da2bcde9a076cb4ee30251b071b89f4a8dff5f60d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcDiscoveryUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcEnablePkce")
    def oidc_enable_pkce(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "oidcEnablePkce"))

    @oidc_enable_pkce.setter
    def oidc_enable_pkce(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__becddf2448887d033a5048fb10c224d58e3e4c3b03c5a08943a62b6e1e9f1388)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcEnablePkce", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oidcScopes")
    def oidc_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "oidcScopes"))

    @oidc_scopes.setter
    def oidc_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__748f78180c8079b4aebad3a822b131f71deaee6bfa338acc6e61e77ac9728d0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oidcScopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="signingAlgs")
    def signing_algs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "signingAlgs"))

    @signing_algs.setter
    def signing_algs(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ad32103935369bb305a4460c52d4609cb201ca65812645eb8c155124b146dde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signingAlgs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="verboseLogging")
    def verbose_logging(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "verboseLogging"))

    @verbose_logging.setter
    def verbose_logging(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fa996869bdf2a8a6ffb5b1aeb9f2e10a2c622546a062b72df2c57888d8c6845)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "verboseLogging", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AclAuthMethodConfigA]:
        return typing.cast(typing.Optional[AclAuthMethodConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AclAuthMethodConfigA]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8634cefe5196e1065a07b1e65202964388dae125936c71050d9cee663c46451d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigOidcClientAssertion",
    jsii_struct_bases=[],
    name_mapping={
        "key_source": "keySource",
        "audience": "audience",
        "extra_headers": "extraHeaders",
        "key_algorithm": "keyAlgorithm",
        "private_key": "privateKey",
    },
)
class AclAuthMethodConfigOidcClientAssertion:
    def __init__(
        self,
        *,
        key_source: builtins.str,
        audience: typing.Optional[typing.Sequence[builtins.str]] = None,
        extra_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        private_key: typing.Optional[typing.Union["AclAuthMethodConfigOidcClientAssertionPrivateKey", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param key_source: The source of the key Nomad will use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_source AclAuthMethod#key_source}
        :param audience: List of audiences to accept the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#audience AclAuthMethod#audience}
        :param extra_headers: Additional headers to include on the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#extra_headers AclAuthMethod#extra_headers}
        :param key_algorithm: Algorithm of the key used to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_algorithm AclAuthMethod#key_algorithm}
        :param private_key: private_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#private_key AclAuthMethod#private_key}
        '''
        if isinstance(private_key, dict):
            private_key = AclAuthMethodConfigOidcClientAssertionPrivateKey(**private_key)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7523ba1a072193a2c7686216bac46beb7b41a6883fa15d39d783853f73f2d058)
            check_type(argname="argument key_source", value=key_source, expected_type=type_hints["key_source"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument extra_headers", value=extra_headers, expected_type=type_hints["extra_headers"])
            check_type(argname="argument key_algorithm", value=key_algorithm, expected_type=type_hints["key_algorithm"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key_source": key_source,
        }
        if audience is not None:
            self._values["audience"] = audience
        if extra_headers is not None:
            self._values["extra_headers"] = extra_headers
        if key_algorithm is not None:
            self._values["key_algorithm"] = key_algorithm
        if private_key is not None:
            self._values["private_key"] = private_key

    @builtins.property
    def key_source(self) -> builtins.str:
        '''The source of the key Nomad will use to sign the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_source AclAuthMethod#key_source}
        '''
        result = self._values.get("key_source")
        assert result is not None, "Required property 'key_source' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audience(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of audiences to accept the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#audience AclAuthMethod#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def extra_headers(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional headers to include on the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#extra_headers AclAuthMethod#extra_headers}
        '''
        result = self._values.get("extra_headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def key_algorithm(self) -> typing.Optional[builtins.str]:
        '''Algorithm of the key used to sign the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_algorithm AclAuthMethod#key_algorithm}
        '''
        result = self._values.get("key_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key(
        self,
    ) -> typing.Optional["AclAuthMethodConfigOidcClientAssertionPrivateKey"]:
        '''private_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#private_key AclAuthMethod#private_key}
        '''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional["AclAuthMethodConfigOidcClientAssertionPrivateKey"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclAuthMethodConfigOidcClientAssertion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AclAuthMethodConfigOidcClientAssertionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigOidcClientAssertionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c86e245d41a7aa97e55915a3f37029b542d94dfc725efc4b3e2413eb17a274a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putPrivateKey")
    def put_private_key(
        self,
        *,
        key_id: typing.Optional[builtins.str] = None,
        key_id_header: typing.Optional[builtins.str] = None,
        pem_cert: typing.Optional[builtins.str] = None,
        pem_cert_file: typing.Optional[builtins.str] = None,
        pem_key: typing.Optional[builtins.str] = None,
        pem_key_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key_id: Specific 'kid' header to set on the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id AclAuthMethod#key_id}
        :param key_id_header: Name of the header the IDP will use to find the cert to verify the JWT signature. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id_header AclAuthMethod#key_id_header}
        :param pem_cert: An x509 certificate PEM to derive a key ID header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert AclAuthMethod#pem_cert}
        :param pem_cert_file: Path to an x509 certificate PEM on Nomad servers to derive a key ID header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert_file AclAuthMethod#pem_cert_file}
        :param pem_key: RSA private key PEM to use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key AclAuthMethod#pem_key}
        :param pem_key_file: Path to an RSA private key PEM on Nomad servers to use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key_file AclAuthMethod#pem_key_file}
        '''
        value = AclAuthMethodConfigOidcClientAssertionPrivateKey(
            key_id=key_id,
            key_id_header=key_id_header,
            pem_cert=pem_cert,
            pem_cert_file=pem_cert_file,
            pem_key=pem_key,
            pem_key_file=pem_key_file,
        )

        return typing.cast(None, jsii.invoke(self, "putPrivateKey", [value]))

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @jsii.member(jsii_name="resetExtraHeaders")
    def reset_extra_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtraHeaders", []))

    @jsii.member(jsii_name="resetKeyAlgorithm")
    def reset_key_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyAlgorithm", []))

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(
        self,
    ) -> "AclAuthMethodConfigOidcClientAssertionPrivateKeyOutputReference":
        return typing.cast("AclAuthMethodConfigOidcClientAssertionPrivateKeyOutputReference", jsii.get(self, "privateKey"))

    @builtins.property
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="extraHeadersInput")
    def extra_headers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "extraHeadersInput"))

    @builtins.property
    @jsii.member(jsii_name="keyAlgorithmInput")
    def key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="keySourceInput")
    def key_source_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keySourceInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(
        self,
    ) -> typing.Optional["AclAuthMethodConfigOidcClientAssertionPrivateKey"]:
        return typing.cast(typing.Optional["AclAuthMethodConfigOidcClientAssertionPrivateKey"], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9b5d8ca5c5121f8e93ee97e77f3cb366ec866668c191ce51d5682fee170699a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="extraHeaders")
    def extra_headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extraHeaders"))

    @extra_headers.setter
    def extra_headers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36a7d830a47a5c371f63e483f9ffef4f4d21b982efa281ed8903987fc3576ba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extraHeaders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyAlgorithm")
    def key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyAlgorithm"))

    @key_algorithm.setter
    def key_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f205c4ce569b763f29d550c2d873c15df8534fb9c12beed2d82de0ecd90f4bc7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keySource")
    def key_source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keySource"))

    @key_source.setter
    def key_source(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02d97bc10a8f1105fac967138cc32d0d8d4567f964aee358f2c0a8e10a5fd248)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keySource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AclAuthMethodConfigOidcClientAssertion]:
        return typing.cast(typing.Optional[AclAuthMethodConfigOidcClientAssertion], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AclAuthMethodConfigOidcClientAssertion],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29d2d42c2d38b1d3118b5ba0e1db626fd1f825e51797f3d4ba270d21d976e347)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigOidcClientAssertionPrivateKey",
    jsii_struct_bases=[],
    name_mapping={
        "key_id": "keyId",
        "key_id_header": "keyIdHeader",
        "pem_cert": "pemCert",
        "pem_cert_file": "pemCertFile",
        "pem_key": "pemKey",
        "pem_key_file": "pemKeyFile",
    },
)
class AclAuthMethodConfigOidcClientAssertionPrivateKey:
    def __init__(
        self,
        *,
        key_id: typing.Optional[builtins.str] = None,
        key_id_header: typing.Optional[builtins.str] = None,
        pem_cert: typing.Optional[builtins.str] = None,
        pem_cert_file: typing.Optional[builtins.str] = None,
        pem_key: typing.Optional[builtins.str] = None,
        pem_key_file: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key_id: Specific 'kid' header to set on the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id AclAuthMethod#key_id}
        :param key_id_header: Name of the header the IDP will use to find the cert to verify the JWT signature. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id_header AclAuthMethod#key_id_header}
        :param pem_cert: An x509 certificate PEM to derive a key ID header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert AclAuthMethod#pem_cert}
        :param pem_cert_file: Path to an x509 certificate PEM on Nomad servers to derive a key ID header. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert_file AclAuthMethod#pem_cert_file}
        :param pem_key: RSA private key PEM to use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key AclAuthMethod#pem_key}
        :param pem_key_file: Path to an RSA private key PEM on Nomad servers to use to sign the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key_file AclAuthMethod#pem_key_file}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d271f436f5740b06677cd44d8e1004dfe3940358c571a91d368f3a97c64f1d3)
            check_type(argname="argument key_id", value=key_id, expected_type=type_hints["key_id"])
            check_type(argname="argument key_id_header", value=key_id_header, expected_type=type_hints["key_id_header"])
            check_type(argname="argument pem_cert", value=pem_cert, expected_type=type_hints["pem_cert"])
            check_type(argname="argument pem_cert_file", value=pem_cert_file, expected_type=type_hints["pem_cert_file"])
            check_type(argname="argument pem_key", value=pem_key, expected_type=type_hints["pem_key"])
            check_type(argname="argument pem_key_file", value=pem_key_file, expected_type=type_hints["pem_key_file"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key_id is not None:
            self._values["key_id"] = key_id
        if key_id_header is not None:
            self._values["key_id_header"] = key_id_header
        if pem_cert is not None:
            self._values["pem_cert"] = pem_cert
        if pem_cert_file is not None:
            self._values["pem_cert_file"] = pem_cert_file
        if pem_key is not None:
            self._values["pem_key"] = pem_key
        if pem_key_file is not None:
            self._values["pem_key_file"] = pem_key_file

    @builtins.property
    def key_id(self) -> typing.Optional[builtins.str]:
        '''Specific 'kid' header to set on the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id AclAuthMethod#key_id}
        '''
        result = self._values.get("key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_id_header(self) -> typing.Optional[builtins.str]:
        '''Name of the header the IDP will use to find the cert to verify the JWT signature.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#key_id_header AclAuthMethod#key_id_header}
        '''
        result = self._values.get("key_id_header")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_cert(self) -> typing.Optional[builtins.str]:
        '''An x509 certificate PEM to derive a key ID header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert AclAuthMethod#pem_cert}
        '''
        result = self._values.get("pem_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_cert_file(self) -> typing.Optional[builtins.str]:
        '''Path to an x509 certificate PEM on Nomad servers to derive a key ID header.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_cert_file AclAuthMethod#pem_cert_file}
        '''
        result = self._values.get("pem_cert_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_key(self) -> typing.Optional[builtins.str]:
        '''RSA private key PEM to use to sign the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key AclAuthMethod#pem_key}
        '''
        result = self._values.get("pem_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pem_key_file(self) -> typing.Optional[builtins.str]:
        '''Path to an RSA private key PEM on Nomad servers to use to sign the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs/resources/acl_auth_method#pem_key_file AclAuthMethod#pem_key_file}
        '''
        result = self._values.get("pem_key_file")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AclAuthMethodConfigOidcClientAssertionPrivateKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AclAuthMethodConfigOidcClientAssertionPrivateKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-nomad.aclAuthMethod.AclAuthMethodConfigOidcClientAssertionPrivateKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d9da0ba449cad2ca99c2f2b9933a4a2e869cf0503ae62d4d9306f7a368f73b7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetKeyId")
    def reset_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyId", []))

    @jsii.member(jsii_name="resetKeyIdHeader")
    def reset_key_id_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyIdHeader", []))

    @jsii.member(jsii_name="resetPemCert")
    def reset_pem_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemCert", []))

    @jsii.member(jsii_name="resetPemCertFile")
    def reset_pem_cert_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemCertFile", []))

    @jsii.member(jsii_name="resetPemKey")
    def reset_pem_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemKey", []))

    @jsii.member(jsii_name="resetPemKeyFile")
    def reset_pem_key_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPemKeyFile", []))

    @builtins.property
    @jsii.member(jsii_name="keyIdHeaderInput")
    def key_id_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="keyIdInput")
    def key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="pemCertFileInput")
    def pem_cert_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemCertFileInput"))

    @builtins.property
    @jsii.member(jsii_name="pemCertInput")
    def pem_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemCertInput"))

    @builtins.property
    @jsii.member(jsii_name="pemKeyFileInput")
    def pem_key_file_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemKeyFileInput"))

    @builtins.property
    @jsii.member(jsii_name="pemKeyInput")
    def pem_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pemKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @key_id.setter
    def key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb70b8b90d9e40cf7cd65090a9457f827a7059154327757dee62be2d5f405bce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyIdHeader")
    def key_id_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyIdHeader"))

    @key_id_header.setter
    def key_id_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07ba57cfb5b3fbd5c8cf8b020bc3cc7d95e4c387420a71114021411bb5680e2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyIdHeader", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemCert")
    def pem_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemCert"))

    @pem_cert.setter
    def pem_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13aa3a009a3100dbcff218449dd5b8268b25bf16296ad6359715fe9848889f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemCert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemCertFile")
    def pem_cert_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemCertFile"))

    @pem_cert_file.setter
    def pem_cert_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e31f2fbde86308c68a65290a03351f37745d368d5438c02a22403367e191401c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemCertFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemKey")
    def pem_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemKey"))

    @pem_key.setter
    def pem_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b22d78c26fc73ec29a4a4e00fe8144267494386688bbbc6c091175e2e8be791)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pemKeyFile")
    def pem_key_file(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pemKeyFile"))

    @pem_key_file.setter
    def pem_key_file(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2598b45a83ad4dfe77b64d598a96abaca1881901b2fc3cd7d7f25ef1a3e378)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pemKeyFile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[AclAuthMethodConfigOidcClientAssertionPrivateKey]:
        return typing.cast(typing.Optional[AclAuthMethodConfigOidcClientAssertionPrivateKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AclAuthMethodConfigOidcClientAssertionPrivateKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66fdb4284ef327b7d396af270b711168159443a7bb8fff17fbc9d906f58dbc5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AclAuthMethod",
    "AclAuthMethodConfig",
    "AclAuthMethodConfigA",
    "AclAuthMethodConfigAOutputReference",
    "AclAuthMethodConfigOidcClientAssertion",
    "AclAuthMethodConfigOidcClientAssertionOutputReference",
    "AclAuthMethodConfigOidcClientAssertionPrivateKey",
    "AclAuthMethodConfigOidcClientAssertionPrivateKeyOutputReference",
]

publication.publish()

def _typecheckingstub__88e5e1175a243f6912e5cc0a978f498ad783f5331b4aa12703ed9829e4b6f791(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    config: typing.Union[AclAuthMethodConfigA, typing.Dict[builtins.str, typing.Any]],
    max_token_ttl: builtins.str,
    name: builtins.str,
    token_locality: builtins.str,
    type: builtins.str,
    default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    token_name_format: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2e991f027a417fd71ec449e59eab0028db7d507dd7c20c4f784bf7f4886353db(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__874f660ea3ddbf1c73fffeaab17d193d5e6d48ff3f5f8716bd9ddcc49cb94edf(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f32dde41415211740dd5a6c9ef230400f520d9a34ce1df7ed9ff0102fa386149(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be346925ec08d59afc244cdf08358c5cddc35c9a6481a1575c62add0de39591f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0366dc74861723b8324b57cbbfafb5d109b3951b4d5f721069d5a334f158249(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47177f31deef12a5653bec19bfc71cf83a83f71c0ac42083a67d7ffa1982df1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e037d609120502442e896f26318c9012a7e84f4c5903793789947743a6351be0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff887f1006e7e39f2298eebc35f93c98f81c647f24c0c9dedc3bfd3ff3f17e3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ef4f91358041c3bf59857d24ac90f1be8c39fc9517b566fbfaeb4e118df2d44(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: typing.Union[AclAuthMethodConfigA, typing.Dict[builtins.str, typing.Any]],
    max_token_ttl: builtins.str,
    name: builtins.str,
    token_locality: builtins.str,
    type: builtins.str,
    default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    token_name_format: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdf814662741aef41134aaad0673de2654a0b04aa478103f3a5714ba9205daa8(
    *,
    allowed_redirect_uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_audiences: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_issuer: typing.Optional[typing.Sequence[builtins.str]] = None,
    claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    clock_skew_leeway: typing.Optional[builtins.str] = None,
    discovery_ca_pem: typing.Optional[typing.Sequence[builtins.str]] = None,
    expiration_leeway: typing.Optional[builtins.str] = None,
    jwks_ca_cert: typing.Optional[builtins.str] = None,
    jwks_url: typing.Optional[builtins.str] = None,
    jwt_validation_pub_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    list_claim_mappings: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    not_before_leeway: typing.Optional[builtins.str] = None,
    oidc_client_assertion: typing.Optional[typing.Union[AclAuthMethodConfigOidcClientAssertion, typing.Dict[builtins.str, typing.Any]]] = None,
    oidc_client_id: typing.Optional[builtins.str] = None,
    oidc_client_secret: typing.Optional[builtins.str] = None,
    oidc_disable_userinfo: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oidc_discovery_url: typing.Optional[builtins.str] = None,
    oidc_enable_pkce: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oidc_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    signing_algs: typing.Optional[typing.Sequence[builtins.str]] = None,
    verbose_logging: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1f3cb6d40cd42ba3feb184212321b36f13a09ad639358b7f94f04fc0b55e92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f3813ddd9811f2f8521e5e70f2d8c7f4b27729883a58964148ad311454b2c3a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e1abdfdaf8b95e8ca43bc15656db572b05f1cb080c37fb19e8c8f3ac4413c2e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e29f20cd6fc2b94bfcb10ecaf7387e52b2a7f0cdc0bc5ccdf3c62c3632ef402b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e0fc8cf67658e546bdc1303d703b65d49f3ffeda2a8f6b487e2aaa8bf88e4f7(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__942356060cac8dedd5234e4930d16a354f986f83089741f49a0fd5045334c5a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a51fc63187bc29f2e6cd275c276dcbe940a867f9d5ec431d74bcff44168ddd7a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5de0a2b519a404d21cd872814a3a4d1ca241d943230cf5582dbd48e308e1027(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b258b525265eb224fb7015fd114eccff385f9761d23bf4859cd10df022a51523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36818c3b205c541ffeddd31985fa8aae3a93ff88775ae553fcdc56a182a380fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e2a846c9d0b386bdabd2f9cea149262d7c104f373080989d2423f73c34f572(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4516d781fe1e8bc8f518f37d26716577836564c44e443db3c7f8379f98c45fc5(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d522db3980259b05977d8a6c334bb4cd8903b28ee05ead77e00c38a790cf5cb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fee9aac5ec2f4252aff0c8419dcd9c9d23379996c4af771af47a690e5b4fab6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f006e856f57ebc1f767bbf60bab9bfb1bd05f7062fd99b700c07531ffdb2077e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62198682fb26c4c8caf9023906575997dd9b1081bff045ba59bf86fc3c28df9a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d08fc806e59b4b273f16d87da2bcde9a076cb4ee30251b071b89f4a8dff5f60d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__becddf2448887d033a5048fb10c224d58e3e4c3b03c5a08943a62b6e1e9f1388(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__748f78180c8079b4aebad3a822b131f71deaee6bfa338acc6e61e77ac9728d0d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ad32103935369bb305a4460c52d4609cb201ca65812645eb8c155124b146dde(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fa996869bdf2a8a6ffb5b1aeb9f2e10a2c622546a062b72df2c57888d8c6845(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8634cefe5196e1065a07b1e65202964388dae125936c71050d9cee663c46451d(
    value: typing.Optional[AclAuthMethodConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7523ba1a072193a2c7686216bac46beb7b41a6883fa15d39d783853f73f2d058(
    *,
    key_source: builtins.str,
    audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    extra_headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    key_algorithm: typing.Optional[builtins.str] = None,
    private_key: typing.Optional[typing.Union[AclAuthMethodConfigOidcClientAssertionPrivateKey, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86e245d41a7aa97e55915a3f37029b542d94dfc725efc4b3e2413eb17a274a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9b5d8ca5c5121f8e93ee97e77f3cb366ec866668c191ce51d5682fee170699a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36a7d830a47a5c371f63e483f9ffef4f4d21b982efa281ed8903987fc3576ba4(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f205c4ce569b763f29d550c2d873c15df8534fb9c12beed2d82de0ecd90f4bc7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02d97bc10a8f1105fac967138cc32d0d8d4567f964aee358f2c0a8e10a5fd248(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29d2d42c2d38b1d3118b5ba0e1db626fd1f825e51797f3d4ba270d21d976e347(
    value: typing.Optional[AclAuthMethodConfigOidcClientAssertion],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d271f436f5740b06677cd44d8e1004dfe3940358c571a91d368f3a97c64f1d3(
    *,
    key_id: typing.Optional[builtins.str] = None,
    key_id_header: typing.Optional[builtins.str] = None,
    pem_cert: typing.Optional[builtins.str] = None,
    pem_cert_file: typing.Optional[builtins.str] = None,
    pem_key: typing.Optional[builtins.str] = None,
    pem_key_file: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9da0ba449cad2ca99c2f2b9933a4a2e869cf0503ae62d4d9306f7a368f73b7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb70b8b90d9e40cf7cd65090a9457f827a7059154327757dee62be2d5f405bce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07ba57cfb5b3fbd5c8cf8b020bc3cc7d95e4c387420a71114021411bb5680e2d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13aa3a009a3100dbcff218449dd5b8268b25bf16296ad6359715fe9848889f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31f2fbde86308c68a65290a03351f37745d368d5438c02a22403367e191401c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b22d78c26fc73ec29a4a4e00fe8144267494386688bbbc6c091175e2e8be791(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2598b45a83ad4dfe77b64d598a96abaca1881901b2fc3cd7d7f25ef1a3e378(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66fdb4284ef327b7d396af270b711168159443a7bb8fff17fbc9d906f58dbc5a(
    value: typing.Optional[AclAuthMethodConfigOidcClientAssertionPrivateKey],
) -> None:
    """Type checking stubs"""
    pass
