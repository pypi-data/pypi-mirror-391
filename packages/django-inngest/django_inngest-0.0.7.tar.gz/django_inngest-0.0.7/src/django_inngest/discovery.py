import importlib
import inspect
import logging
from pathlib import Path

from django.apps import apps
from django.conf import settings

# Import Inngest to check instance types
try:
    import inngest

    HAS_INNGEST = True
except ImportError:
    HAS_INNGEST = False
    inngest = None

logger = logging.getLogger(__name__)


def discover_inngest_functions(inactive_function_ids=None, inngest_client=None):
    """
    Automatically discover all Inngest functions decorated with
    @inngest_client.create_function across all Django apps in the project.

    Args:
        inactive_function_ids: List of function IDs (fn_id) to exclude.
                              Can be specified with or without the app_id prefix.
        inngest_client: Optional Inngest client to extract app_id from.
                       If provided, will automatically add app_id prefix to inactive IDs.

    Returns:
        List of discovered Inngest function objects
    """
    if inactive_function_ids is None:
        inactive_function_ids = []

    if not HAS_INNGEST:
        logger.error("Inngest package not found. Cannot discover functions.")
        return []

    # Get app_id prefix from client if provided
    app_id_prefix = None
    if inngest_client:
        app_id_prefix = getattr(inngest_client, "_app_id", None) or getattr(
            inngest_client, "app_id", None
        )
        if app_id_prefix:
            logger.info(f"Using app_id prefix from client: {app_id_prefix}")

    # Normalize inactive function IDs to include prefix
    normalized_inactive = []
    for inactive_id in inactive_function_ids:
        if app_id_prefix and not inactive_id.startswith(f"{app_id_prefix}-"):
            normalized_inactive.append(f"{app_id_prefix}-{inactive_id}")
        else:
            normalized_inactive.append(inactive_id)

    if normalized_inactive:
        logger.info(f"Looking for inactive function IDs: {normalized_inactive}")

    discovered_functions = []
    all_found_ids = []

    # Get all Django apps in the project
    for app_config in apps.get_app_configs():
        # Skip built-in Django apps and third-party apps
        app_path = Path(app_config.path)
        src_path = Path(settings.BASE_DIR)

        # Only process apps within our src directory
        if not str(app_path).startswith(str(src_path)):
            continue

        # Look for workflows.py in each app
        workflows_file = app_path / "workflows.py"
        if workflows_file.exists():
            try:
                # Import the workflows module
                module_name = f"{app_config.name}.workflows"
                module = importlib.import_module(module_name)

                # Inspect all members of the module
                for name, obj in inspect.getmembers(module):
                    # Skip private/magic methods
                    if name.startswith("_"):
                        continue

                    # Check if it's an Inngest Function instance
                    if isinstance(obj, inngest.Function):
                        # Get the function ID
                        fn_id = (
                            getattr(obj, "_id", None)
                            or getattr(obj, "id", None)
                            or getattr(obj, "fn_id", None)
                        )

                        if fn_id:
                            all_found_ids.append(fn_id)

                            # Check if function should be excluded
                            if fn_id in normalized_inactive:
                                logger.info(
                                    f"✓ Skipping inactive function: {fn_id} "
                                    f"from {module_name}.{name}"
                                )
                                continue

                            logger.info(
                                f"✓ Discovered active function: {fn_id} "
                                f"from {module_name}.{name}"
                            )
                            discovered_functions.append(obj)
                        else:
                            logger.warning(
                                f"Found Inngest function '{name}' in {module_name} "
                                f"but could not extract ID."
                            )

            except ImportError as e:
                logger.warning(
                    f"Workflow loading failed from {app_config.name} at {workflows_file}: {e}",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"Error discovering Inngest functions in {app_config.name}: {e}",
                    exc_info=True,
                )

    # Summary logging
    logger.info(f"\n{'=' * 60}")
    logger.info("Inngest Function Discovery Summary:")
    if app_id_prefix:
        logger.info(f"  App ID: {app_id_prefix}")
    logger.info(f"  Total functions found: {len(all_found_ids)}")
    logger.info(f"  Active functions: {len(discovered_functions)}")
    logger.info(
        f"  Inactive functions: {len(all_found_ids) - len(discovered_functions)}"
    )

    if all_found_ids:
        logger.info("\nAll discovered function IDs:")
        for fn_id in all_found_ids:
            status = "INACTIVE" if fn_id in normalized_inactive else "ACTIVE"
            logger.info(f"  - {fn_id} [{status}]")

    # Check for inactive IDs that weren't found
    not_found = set(normalized_inactive) - set(all_found_ids)
    if not_found:
        logger.warning(
            f"\n⚠ These inactive function IDs were not found: {list(not_found)}"
        )
    logger.info(f"{'=' * 60}\n")

    return discovered_functions
