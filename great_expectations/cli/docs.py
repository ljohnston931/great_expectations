import os
import sys

import click

from great_expectations import DataContext, exceptions as ge_exceptions
from great_expectations.cli.logging import logger
from great_expectations.cli.util import cli_message, _offer_to_install_new_template


@click.group()
def docs():
    """data docs operations"""
    pass


@docs.command(name="build")
@click.option(
    "--directory",
    "-d",
    default=None,
    help="The project's great_expectations directory.",
)
@click.option(
    "--site_name",
    "-s",
    help="The site for which to generate documentation. See data_docs section in great_expectations.yml",
)
@click.option(
    "--view/--no-view",
    help="By default open in browser unless you specify the --no-view flag",
    default=True,
)
def docs_build(directory, site_name, view=True):
    """Build Data Docs for a project."""
    try:
        context = DataContext(directory)
        _build_docs(context, site_name=site_name)
        if view:
            context.open_data_docs()
    except ge_exceptions.ConfigNotFoundError as err:
        cli_message("<red>{}</red>".format(err.message))
        sys.exit(1)
    except ge_exceptions.ZeroDotSevenConfigVersionError as err:
        _offer_to_install_new_template(err, context.root_directory)
        return
    except ge_exceptions.PluginModuleNotFoundError as err:
        cli_message(err.cli_colored_message)
        sys.exit(1)
    except ge_exceptions.PluginClassNotFoundError as err:
        cli_message(err.cli_colored_message)
        sys.exit(1)


def _build_docs(context, site_name=None):
    """Build documentation in a context"""
    logger.debug("Starting cli.datasource.build_docs")

    cli_message("Building <green>Data Docs</green>...")

    if site_name is not None:
        site_names = [site_name]
    else:
        site_names = None

    index_page_locator_infos = context.build_data_docs(site_names=site_names)

    msg = "The following Data Docs sites were built:\n"
    for site_name, index_page_locator_info in index_page_locator_infos.items():
        if os.path.isfile(index_page_locator_info):
            msg += "- " + site_name + ":\n"
            msg += "   <green>file://" + index_page_locator_info + "</green>\n"
        else:
            msg += site_name + "\n"

    msg = msg.rstrip("\n")
    cli_message(msg)
