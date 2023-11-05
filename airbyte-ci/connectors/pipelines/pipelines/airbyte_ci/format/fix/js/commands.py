# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""

    dagger_client = ctx.params["dagger_client"]
    format_container = (
        dagger_client.container()
        .from_("node:18.18.0-slim")
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y bash",
                ]
            )
        )
        .with_mounted_directory(
            "/src",
            dagger_client.host().directory(
                ".",
                include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
                exclude=DEFAULT_FORMAT_IGNORE_LIST,
            ),
        )
        .with_workdir(f"/src")
        .with_exec(["npm", "install", "-g", "npm@10.1.0"])
        .with_exec(["npm", "install", "-g", "prettier@2.8.1"])
        .with_exec(["prettier", "--write", "."])
    )

    await format_container
    await format_container.directory("/src").export(".")
