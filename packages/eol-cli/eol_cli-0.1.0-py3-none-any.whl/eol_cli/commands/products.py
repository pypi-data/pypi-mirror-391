"""Products commands - Query for products."""

import click

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.formatters import (
    format_json,
    format_product_details,
    format_product_list,
    format_release_details,
    format_xml,
)


@click.group(name="products")
def products():
    """Query for products and their release cycles."""
    pass


@products.command(name="list")
@click.option("--full", is_flag=True, help="Get full product details (includes all releases)")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def list_products(full: bool, output_json: bool, output_xml: bool):
    """List all products.

    By default, returns a summary of each product. Use --full to get
    complete product information including all release cycles.

    Examples:
        eol products list
        eol products list --full
        eol products list --json
    """
    # Validate mutually exclusive format options
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        if full:
            data = client.list_products_full()
        else:
            data = client.list_products()

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_product_list(data, full=full)

    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()


def _fetch_products(client: EOLClient, product_list: list[str]) -> tuple[list, list]:
    """Fetch product data for multiple products.

    Returns:
        tuple: (all_data, errors) where all_data is list of successful fetches
               and errors is list of error messages
    """
    all_data = []
    errors = []

    for product in product_list:
        try:
            data = client.get_product(product)
            all_data.append(data)
        except EOLNotFoundError:
            errors.append(f"Product '{product}' not found")
        except EOLAPIError as e:
            errors.append(f"Error fetching '{product}': {e}")

    return all_data, errors


def _create_aggregated_response(all_data: list) -> dict:
    """Create aggregated response for multiple products."""
    return {
        "schema_version": all_data[0].get("schema_version", "1.2.0"),
        "total": len(all_data),
        "products": all_data,
    }


def _output_json_format(all_data: list):
    """Output products in JSON format."""
    if len(all_data) == 1:
        click.echo(format_json(all_data[0]))
    else:
        click.echo(format_json(_create_aggregated_response(all_data)))


def _output_xml_format(all_data: list):
    """Output products in XML format."""
    if len(all_data) == 1:
        click.echo(format_xml(all_data[0]))
    else:
        click.echo(format_xml(_create_aggregated_response(all_data)))


def _output_rich_format(all_data: list, show_all: bool):
    """Output products in Rich terminal format."""
    for i, data in enumerate(all_data):
        if i > 0:
            click.echo("\n" + "=" * 80 + "\n")
        format_product_details(data, show_all=show_all)


@products.command(name="get")
@click.argument("products")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
@click.option(
    "--all", "show_all", is_flag=True, help="Show all product details (info, links, identifiers)"
)
def get_product(products: str, output_json: bool, output_xml: bool, show_all: bool):
    """Get detailed information about one or more products.

    By default, only shows the releases table. Use --all to see complete details.
    You can query multiple products by separating them with commas.

    PRODUCTS: One or more product names separated by commas (e.g., 'python', 'ubuntu,nodejs')

    Examples:
        eol-cli products get python
        eol-cli products get python --all
        eol-cli products get fortinet,apache
        eol-cli products get ubuntu,python,nodejs --json
        eol-cli products get apache,nginx --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    product_list = [p.strip() for p in products.split(",")]
    client = EOLClient()

    try:
        all_data, errors = _fetch_products(client, product_list)

        if errors:
            for error in errors:
                click.echo(f"Warning: {error}", err=True)
            if not all_data:
                click.echo("\nNo valid products found", err=True)
                raise click.Abort() from None

        if output_json:
            _output_json_format(all_data)
        elif output_xml:
            _output_xml_format(all_data)
        else:
            _output_rich_format(all_data, show_all)

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()


@products.command(name="release")
@click.argument("product")
@click.argument("release")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def get_release(product: str, release: str, output_json: bool, output_xml: bool):
    """Get information about a specific product release cycle.

    PRODUCT: The product name (e.g., 'ubuntu', 'python')

    RELEASE: The release cycle name (e.g., '22.04', '3.11') or 'latest'

    Examples:
        eol-cli products release ubuntu 22.04
        eol-cli products release python 3.11
        eol-cli products release ubuntu latest
        eol-cli products release python latest --json
        eol-cli products release python latest --xml
    """
    # Validate mutually exclusive format options
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        if release.lower() == "latest":
            data = client.get_product_latest_release(product)
        else:
            data = client.get_product_release(product, release)

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_release_details(data)

    except EOLNotFoundError:
        if release.lower() == "latest":
            click.echo(f"Error: Product '{product}' not found", err=True)
        else:
            click.echo(f"Error: Release '{release}' not found for product '{product}'", err=True)
        click.echo("Tip: Use 'eol-cli products get <product>' to see available releases", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()
