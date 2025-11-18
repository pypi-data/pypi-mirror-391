r'''
# CDKTF prebuilt bindings for hashicorp/nomad provider version 2.5.2

This repo builds and publishes the [Terraform nomad provider](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-nomad](https://www.npmjs.com/package/@cdktf/provider-nomad).

`npm install @cdktf/provider-nomad`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-nomad](https://pypi.org/project/cdktf-cdktf-provider-nomad).

`pipenv install cdktf-cdktf-provider-nomad`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Nomad](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Nomad).

`dotnet add package HashiCorp.Cdktf.Providers.Nomad`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-nomad](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-nomad).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-nomad</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-nomad-go`](https://github.com/cdktf/cdktf-provider-nomad-go) package.

`go get github.com/cdktf/cdktf-provider-nomad-go/nomad/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-nomad-go/blob/main/nomad/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-nomad).

## Versioning

This project is explicitly not tracking the Terraform nomad provider version 1:1. In fact, it always tracks `latest` of `~> 2.0` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform nomad provider](https://registry.terraform.io/providers/hashicorp/nomad/2.5.2)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

__all__ = [
    "acl_auth_method",
    "acl_binding_rule",
    "acl_policy",
    "acl_role",
    "acl_token",
    "csi_volume",
    "csi_volume_registration",
    "data_nomad_acl_policies",
    "data_nomad_acl_policy",
    "data_nomad_acl_role",
    "data_nomad_acl_roles",
    "data_nomad_acl_token",
    "data_nomad_acl_tokens",
    "data_nomad_allocations",
    "data_nomad_datacenters",
    "data_nomad_deployments",
    "data_nomad_dynamic_host_volume",
    "data_nomad_job",
    "data_nomad_job_parser",
    "data_nomad_jwks",
    "data_nomad_namespace",
    "data_nomad_namespaces",
    "data_nomad_node_pool",
    "data_nomad_node_pools",
    "data_nomad_plugin",
    "data_nomad_plugins",
    "data_nomad_regions",
    "data_nomad_scaling_policies",
    "data_nomad_scaling_policy",
    "data_nomad_scheduler_config",
    "data_nomad_variable",
    "data_nomad_volumes",
    "dynamic_host_volume",
    "dynamic_host_volume_registration",
    "external_volume",
    "job",
    "namespace",
    "node_pool",
    "provider",
    "quota_specification",
    "scheduler_config",
    "sentinel_policy",
    "variable",
    "volume",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import acl_auth_method
from . import acl_binding_rule
from . import acl_policy
from . import acl_role
from . import acl_token
from . import csi_volume
from . import csi_volume_registration
from . import data_nomad_acl_policies
from . import data_nomad_acl_policy
from . import data_nomad_acl_role
from . import data_nomad_acl_roles
from . import data_nomad_acl_token
from . import data_nomad_acl_tokens
from . import data_nomad_allocations
from . import data_nomad_datacenters
from . import data_nomad_deployments
from . import data_nomad_dynamic_host_volume
from . import data_nomad_job
from . import data_nomad_job_parser
from . import data_nomad_jwks
from . import data_nomad_namespace
from . import data_nomad_namespaces
from . import data_nomad_node_pool
from . import data_nomad_node_pools
from . import data_nomad_plugin
from . import data_nomad_plugins
from . import data_nomad_regions
from . import data_nomad_scaling_policies
from . import data_nomad_scaling_policy
from . import data_nomad_scheduler_config
from . import data_nomad_variable
from . import data_nomad_volumes
from . import dynamic_host_volume
from . import dynamic_host_volume_registration
from . import external_volume
from . import job
from . import namespace
from . import node_pool
from . import provider
from . import quota_specification
from . import scheduler_config
from . import sentinel_policy
from . import variable
from . import volume
