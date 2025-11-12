import logging
import multiprocessing
import traceback
from typing import Any

import reactivex
from reactivex import Observable
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

from labels.model.ecosystem_data.aliases import AcceptedEcosystemData
from labels.model.ecosystem_data.alpine import ApkDBEntry
from labels.model.ecosystem_data.arch import AlpmDBEntry
from labels.model.ecosystem_data.debian import DpkgDBEntry
from labels.model.ecosystem_data.redhat import RpmDBEntry
from labels.model.file import Coordinates, Location
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.operations.cataloger import execute_parsers
from labels.parsers.operations.generator import gen_location_tasks
from labels.parsers.operations.handler import handle_parser
from labels.parsers.operations.utils import handle_relationships, identify_release

LOGGER = logging.getLogger(__name__)


def log_and_continue(e: Exception, file_item: str) -> Observable[None]:
    LOGGER.error(
        "Error found while resolving packages of %s: %s: %s",
        file_item,
        str(e),
        traceback.format_exc(),
    )
    return reactivex.empty()


def process_file_item(
    file_item: str,
    resolver: Resolver,
    pool_scheduler: ThreadPoolScheduler,
) -> Observable[tuple[list[Package], list[Relationship]]]:
    return reactivex.just(file_item).pipe(
        handle_parser(scheduler=pool_scheduler),
        gen_location_tasks(resolver),
        execute_parsers(resolver, Environment(linux_release=identify_release(resolver))),
        ops.catch(lambda e, _: log_and_continue(e, file_item)),
    )


def _get_language(language_str: str) -> Language:
    try:
        return Language(language_str.lower())
    except ValueError:
        return Language.UNKNOWN_LANGUAGE


def _get_licenses(licenses: list[dict[str, Any]]) -> list[str]:
    return [value for license_info in licenses if (value := license_info.get("value"))]


def _get_locations(locations: list[dict[str, Any]]) -> list[Location]:
    return [
        Location(
            access_path=location.get("path"),
            coordinates=Coordinates(
                real_path=location.get("path"),  # type: ignore[arg-type]
                file_system_id=location.get("layerID"),
            ),
        )
        for location in locations
        if (annotation := location.get("annotations"))
        and (evidence := annotation.get("evidence"))
        and evidence == "primary"
    ]


def _get_package_type(package_type: str) -> PackageType:
    try:
        return PackageType(package_type)
    except ValueError:
        return PackageType.UnknownPkg


def _get_ecosystem_data(
    metadata: dict[str, Any] | None, pkg_type: PackageType
) -> AcceptedEcosystemData | None:
    if pkg_type == PackageType.ApkPkg:
        return ApkDBEntry(
            package=metadata.get("package"),  # type: ignore[union-attr]
            version=metadata.get("version"),  # type: ignore[union-attr]
            provides=metadata.get("provides", []),  # type: ignore[union-attr]
            dependencies=metadata.get("pullDependencies", []),  # type: ignore[union-attr]
            maintainer=metadata.get("maintainer"),  # type: ignore[union-attr]
            origin_package=metadata.get("originPackage"),  # type: ignore[union-attr]
            architecture=metadata.get("architecture"),  # type: ignore[union-attr]
            licenses=None,
        )
    if pkg_type == PackageType.DebPkg:
        return DpkgDBEntry(
            package=metadata.get("package"),  # type: ignore[union-attr]
            version=metadata.get("version"),  # type: ignore[union-attr]
            source=metadata.get("source"),  # type: ignore[union-attr]
            source_version=metadata.get("sourceVersion"),  # type: ignore[union-attr]
            architecture=metadata.get("architecture"),  # type: ignore[union-attr]
            maintainer=metadata.get("maintainer"),  # type: ignore[union-attr]
            provides=metadata.get("provides", []),  # type: ignore[union-attr]
            dependencies=metadata.get("depends", []),  # type: ignore[union-attr]
            pre_dependencies=metadata.get("preDepends", []),  # type: ignore[union-attr]
        )

    if pkg_type == PackageType.RpmPkg:
        return RpmDBEntry(
            name=str(metadata.get("name")),  # type: ignore[union-attr]
            version=str(metadata.get("version")),  # type: ignore[union-attr]
            epoch=metadata.get("epoch"),  # type: ignore[union-attr]
            arch=str(metadata.get("arch")),  # type: ignore[union-attr]
            release=str(metadata.get("release")),  # type: ignore[union-attr]
            source_rpm=str(metadata.get("sourceRpm")),  # type: ignore[union-attr]
        )

    if pkg_type == PackageType.AlpmPkg:
        return AlpmDBEntry(
            licenses="",
            base_package=str(metadata.get("basepackage")),  # type: ignore[union-attr]
            package=str(metadata.get("package")),  # type: ignore[union-attr]
            version=str(metadata.get("version")),  # type: ignore[union-attr]
            architecture=str(metadata.get("architecture")),  # type: ignore[union-attr]
            packager=str(metadata.get("packager")),  # type: ignore[union-attr]
        )

    return None


def package_operations_factory_v2(
    docker_sbom: dict[str, Any],
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    for artifact_pkg in docker_sbom.get("artifacts", []):
        pkg_language = _get_language(artifact_pkg.get("language"))
        pkg_licenses = _get_licenses(artifact_pkg.get("licenses"))
        pkg_type = _get_package_type(artifact_pkg.get("type"))
        pkg_locations = _get_locations(artifact_pkg.get("locations", []))
        metadata = artifact_pkg.get("metadata")
        pkg_ecosystem_data = _get_ecosystem_data(metadata, pkg_type)

        packages.append(
            Package(
                name=artifact_pkg.get("name"),
                version=artifact_pkg.get("version"),
                language=pkg_language,
                licenses=pkg_licenses,
                locations=pkg_locations,
                type=pkg_type,
                found_by=artifact_pkg.get("foundBy"),
                p_url=artifact_pkg.get("purl"),
                ecosystem_data=pkg_ecosystem_data,
            )
        )

    return packages, []


def package_operations_factory(
    resolver: Resolver,
) -> tuple[list[Package], list[Relationship]]:
    observer: Observable[str] = reactivex.from_iterable(resolver.walk_file())
    result_packages: list[Package] = []
    result_relations: list[Relationship] = []
    completed_event = multiprocessing.Event()
    errors = []

    def on_completed() -> None:
        completed_event.set()

    def on_error(error: Exception) -> None:
        errors.append(error)
        on_completed()

    def on_next(value: tuple[list[Package], list[Relationship]]) -> None:
        packages, relations = value
        result_packages.extend(packages)
        result_relations.extend(relations)

    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    final_obs: Observable[tuple[list[Package], list[Relationship]]] = observer.pipe(
        ops.map(
            lambda file_item: process_file_item(file_item, resolver, pool_scheduler),  # type: ignore[arg-type]
        ),
        ops.merge(max_concurrent=optimal_thread_count),
    )
    final_obs.subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed)

    completed_event.wait()
    result_relations.extend(handle_relationships(result_packages))

    return result_packages, result_relations
