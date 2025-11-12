import httpx
from typing import Literal

from halerium_utilities.utils.api_config import (
    get_api_headers, get_api_base_url)
from halerium_utilities.logging.exceptions import (
    BundleInstallationError, StoreBundleError)
from .schemas import (
    InstallationCheck, get_installation_check_model_from_response_data,
    ConflictHandling, conflict_handling_to_install_payload)


def _get_bundle_url():
    return get_api_base_url() + "/token-access/published-apps"


def precheck_bundle_installation(bundle_id: str):
    url = _get_bundle_url().rstrip("/") + f"/{bundle_id}/validate-import"
    with httpx.Client() as client:
        response = client.get(
            url=url,
            headers=get_api_headers()
        )
        if response.status_code == 404:
            raise StoreBundleError(
                f"Bundle with id {bundle_id} was not found."
            )
        response.raise_for_status()
    data = response.json()["data"]

    return get_installation_check_model_from_response_data(data)


async def precheck_bundle_installation_async(bundle_id: str):
    url = _get_bundle_url().rstrip("/") + f"/{bundle_id}/validate-import"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url=url,
            headers=get_api_headers()
        )
        if response.status_code == 404:
            raise StoreBundleError(
                f"Bundle with id {bundle_id} was not found."
            )
        response.raise_for_status()
    data = response.json()["data"]

    return get_installation_check_model_from_response_data(data)


def install_bundle(bundle_id: str, conflict_handling: ConflictHandling = None):
    if conflict_handling:
        conflict_actions = ConflictHandling.validate(conflict_handling)
        payload = conflict_handling_to_install_payload(conflict_actions)
    else:
        payload = None
    url = _get_bundle_url().rstrip("/") + f"/{bundle_id}/import"
    with httpx.Client() as client:
        response = client.post(
            url=url,
            headers=get_api_headers(),
            json=payload,
        )
        if response.status_code == 409:
            raise BundleInstallationError(
                "Unhandled conflicts prevent installation."
                "\nConsider using the precheck_bundle_installation and "
                "create_conflict_handling_from_check functions.")
        elif response.status_code == 404:
            raise StoreBundleError(
                f"Bundle with id {bundle_id} was not found."
            )
        response.raise_for_status()
    data = response.json()["data"]

    return get_installation_check_model_from_response_data(data)


async def install_bundle_async(bundle_id: str, conflict_handling: ConflictHandling = None):
    if conflict_handling:
        conflict_actions = ConflictHandling.validate(conflict_handling)
        payload = conflict_handling_to_install_payload(conflict_actions)
    else:
        payload = None
    url = _get_bundle_url().rstrip("/") + f"/{bundle_id}/import"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            headers=get_api_headers(),
            json=payload,
        )
        if response.status_code == 409:
            raise BundleInstallationError(
                "Unhandled conflicts prevent installation."
                "\nConsider using the precheck_bundle_installation and "
                "create_conflict_handling_from_check functions.")
        elif response.status_code == 404:
            raise StoreBundleError(
                f"Bundle with id {bundle_id} was not found."
            )
        response.raise_for_status()
    data = response.json()["data"]

    return get_installation_check_model_from_response_data(data)


def create_conflict_handling_from_check(installation_check,
                                        default: Literal["skip", "replace"] = "skip"):
    installation_check = InstallationCheck.validate(installation_check)
    conflicts = installation_check.conflicts
    if not conflicts:
        return ConflictHandling()

    handling_dict = {}
    for key, value in conflicts.dict().items():
        handling_dict[key] = {}
        for item in value:
            handling_dict[key][item] = default

    return ConflictHandling.validate(handling_dict)
