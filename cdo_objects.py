#!/usr/bin/env python3

import logging
from json import dumps
from time import sleep
from cdo.cdo import CDOObjects
from dotenv import dotenv_values

logging.basicConfig()
logger = logging.getLogger("cdo_objects")
logger.setLevel(logging.WARNING)


def write_output_file(objects: list, output_file: str) -> None:
    """Save the json output to a file"""
    with open(output_file, mode="w") as write_file:
        write_file.write(dumps(objects, indent=4))
    logger.warning(f"File written: {output_file}")


def get_objects(cdo: CDOObjects, obj_count: int, limit: int = 199) -> list[dict]:
    """Call the CDO UI API and get all network objects and object-groups"""
    objects = []
    offset = 0
    while offset < obj_count:
        logger.warning(f"Getting the objects {offset} - {offset+limit}")
        objs = cdo.get_objects(offset=offset, limit=limit)
        for obj in objs:
            objects.append(
                {
                    "name": obj.get("name"),
                    "uid": obj.get("uid"),
                    "tags": obj.get("tags"),
                    "objectType": obj.get("objectType"),
                    "elements": obj.get("elements"),
                    "overrides": obj.get("overrides", []),
                    "overrideContents": obj.get("overrideContents", []),
                }
            )
        offset += limit
        sleep(1)  # Don't hammer the CDO UI API
    logger.warning(f"{len(objects)} retrieved from CDO")
    return objects


def main(cdo_token: str, cdo_region: str, output_file="objects.json") -> None:
    cdo = CDOObjects(cdo_token, cdo_region)
    obj_count = cdo.get_objects(count=True)
    logger.warning(f"Retrieving {obj_count} objects...")
    objects = get_objects(cdo, obj_count["aggregationQueryResult"])
    logger.warning(dumps(objects, indent=4))
    write_output_file(objects, output_file)


if __name__ == "__main__":
    config = dotenv_values(".env")
    main(config.get("CDO_TOKEN"), config.get("CDO_REGION").upper())
