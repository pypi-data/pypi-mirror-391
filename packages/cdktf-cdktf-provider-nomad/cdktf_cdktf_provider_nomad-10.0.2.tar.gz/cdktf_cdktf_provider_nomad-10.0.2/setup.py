import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-cdktf-provider-nomad",
    "version": "10.0.2",
    "description": "Prebuilt nomad Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/cdktf/cdktf-provider-nomad.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdktf/cdktf-provider-nomad.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdktf_cdktf_provider_nomad",
        "cdktf_cdktf_provider_nomad._jsii",
        "cdktf_cdktf_provider_nomad.acl_auth_method",
        "cdktf_cdktf_provider_nomad.acl_binding_rule",
        "cdktf_cdktf_provider_nomad.acl_policy",
        "cdktf_cdktf_provider_nomad.acl_role",
        "cdktf_cdktf_provider_nomad.acl_token",
        "cdktf_cdktf_provider_nomad.csi_volume",
        "cdktf_cdktf_provider_nomad.csi_volume_registration",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_policies",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_policy",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_role",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_roles",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_token",
        "cdktf_cdktf_provider_nomad.data_nomad_acl_tokens",
        "cdktf_cdktf_provider_nomad.data_nomad_allocations",
        "cdktf_cdktf_provider_nomad.data_nomad_datacenters",
        "cdktf_cdktf_provider_nomad.data_nomad_deployments",
        "cdktf_cdktf_provider_nomad.data_nomad_dynamic_host_volume",
        "cdktf_cdktf_provider_nomad.data_nomad_job",
        "cdktf_cdktf_provider_nomad.data_nomad_job_parser",
        "cdktf_cdktf_provider_nomad.data_nomad_jwks",
        "cdktf_cdktf_provider_nomad.data_nomad_namespace",
        "cdktf_cdktf_provider_nomad.data_nomad_namespaces",
        "cdktf_cdktf_provider_nomad.data_nomad_node_pool",
        "cdktf_cdktf_provider_nomad.data_nomad_node_pools",
        "cdktf_cdktf_provider_nomad.data_nomad_plugin",
        "cdktf_cdktf_provider_nomad.data_nomad_plugins",
        "cdktf_cdktf_provider_nomad.data_nomad_regions",
        "cdktf_cdktf_provider_nomad.data_nomad_scaling_policies",
        "cdktf_cdktf_provider_nomad.data_nomad_scaling_policy",
        "cdktf_cdktf_provider_nomad.data_nomad_scheduler_config",
        "cdktf_cdktf_provider_nomad.data_nomad_variable",
        "cdktf_cdktf_provider_nomad.data_nomad_volumes",
        "cdktf_cdktf_provider_nomad.dynamic_host_volume",
        "cdktf_cdktf_provider_nomad.dynamic_host_volume_registration",
        "cdktf_cdktf_provider_nomad.external_volume",
        "cdktf_cdktf_provider_nomad.job",
        "cdktf_cdktf_provider_nomad.namespace",
        "cdktf_cdktf_provider_nomad.node_pool",
        "cdktf_cdktf_provider_nomad.provider",
        "cdktf_cdktf_provider_nomad.quota_specification",
        "cdktf_cdktf_provider_nomad.scheduler_config",
        "cdktf_cdktf_provider_nomad.sentinel_policy",
        "cdktf_cdktf_provider_nomad.variable",
        "cdktf_cdktf_provider_nomad.volume"
    ],
    "package_data": {
        "cdktf_cdktf_provider_nomad._jsii": [
            "provider-nomad@10.0.2.jsii.tgz"
        ],
        "cdktf_cdktf_provider_nomad": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.21.0, <0.22.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.118.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
