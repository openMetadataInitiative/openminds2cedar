"""CLI for openminds2cedar."""

import argparse
import json
from pathlib import Path

from .generators import CEDARElementGenerator, CEDARTemplateGenerator
from .converters import CEDARToOpenMINDSConverter
from .api import CEDARClient
from .registry import Registry


def cmd_generate(args):
    """Generate CEDAR element from openMINDS schema."""
    registry = Registry()
    generator = CEDARElementGenerator(registry=registry)
    element = generator.generate(args.schema)

    module, name = args.schema.split(".")
    output_dir = Path(args.output) / module
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name.lower()}.json"

    with open(output_path, "w") as f:
        json.dump(element, f, indent=2)
    print(f"Generated: {output_path}")


def cmd_template(args):
    """Create template from elements or registry definition."""
    registry = Registry()
    element_generator = CEDARElementGenerator(registry=registry)
    template_generator = CEDARTemplateGenerator()

    if args.from_registry:
        # Generate from registry template definition
        tmpl_def = registry.template(args.from_registry)
        name = tmpl_def.get("name", args.from_registry)  # Use name field or fall back to key
        description = tmpl_def.get("description", "")

        elements = []
        element_ids = []
        cardinalities = []
        for elem_def in tmpl_def["elements"]:
            schema = elem_def["schema"]
            multiple = elem_def.get("multiple", False)
            elem = element_generator.generate(schema)
            elements.append(elem)
            element_ids.append(elem["@id"])
            cardinalities.append(multiple)
    else:
        # Generate from element files (original behavior)
        name = args.name
        description = args.description or ""
        elements = []
        element_ids = []
        for i, path in enumerate(args.elements):
            with open(path) as f:
                elem = json.load(f)
                elements.append(elem)
                elem_id = elem.get("@id")
                if elem_id and (elem_id.startswith("https://") or elem_id.startswith("urn:")):
                    element_ids.append(elem_id)
                else:
                    element_ids.append(f"_:local_{i}")

    cardinalities = cardinalities if args.from_registry else [False] * len(elements)
    template = template_generator.generate(elements, element_ids, name, description, cardinalities)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{name}.json"

    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)
    print(f"Created: {output_path}")


def cmd_validate(args):
    """Validate elements/templates via CEDAR API."""
    client = CEDARClient()
    path = Path(args.path)
    files = list(path.rglob("*.json")) if path.is_dir() else [path]

    print(f"Validating {len(files)} file(s)...")
    errors = []
    skipped = []
    for f in files:
        with open(f) as fp:
            data = json.load(fp)

        # Skip templates with placeholder IDs (need real element IDs from CEDAR)
        if data.get("@type") == "https://schema.metadatacenter.org/core/Template":
            content = json.dumps(data)
            if "_:local_" in content:
                skipped.append(f)
                print(f"  SKIP {f}")
                print(f"       Template uses placeholder IDs (_:local_*) - publish elements first")
                continue
            result = client.validate_template(data)
        else:
            result = client.validate(data)

        if result["valid"]:
            print(f"  OK   {f}")
        else:
            errors.append(f)
            print(f"  FAIL {f}")
            for err in result["errors"]:
                print(f"       {err}")

    validated = len(files) - len(errors) - len(skipped)
    print(f"\n{validated}/{len(files)} valid" + (f", {len(skipped)} skipped" if skipped else ""))
    return len(errors) == 0


def cmd_convert(args):
    """Convert CEDAR instance to openMINDS."""
    converter = CEDARToOpenMINDSConverter()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if input is a CEDAR URL or local path
    if args.path.startswith("https://repo.metadatacenter.org/"):
        # Fetch instance from CEDAR by ID
        client = CEDARClient()
        instance = client.get_instance(args.path)
        if not instance:
            print(f"FAIL Could not fetch instance: {args.path}")
            return

        name = instance.get("schema:name", "unnamed")
        collection = converter.convert_instance(instance)

        all_valid = True
        for obj in collection:
            failures = obj.validate()
            if failures:
                print(f"FAIL {name}: {obj.__class__.__name__} validation failed: {failures}")
                all_valid = False

        if all_valid:
            output_path = output_dir / f"{name}.jsonld"
            collection.save(str(output_path))
            print(f"OK   Converted: {args.path}")
            print(f"     Output: {output_path}")
    else:
        # Local file or directory
        path = Path(args.path)
        files = list(path.rglob("*.json")) if path.is_dir() else [path]

        for f in files:
            collection = converter.convert(f)

            all_valid = True
            for obj in collection:
                failures = obj.validate()
                if failures:
                    print(f"FAIL {f.name}: {obj.__class__.__name__} validation failed: {failures}")
                    all_valid = False

            if all_valid:
                output_path = output_dir / f"{f.stem}.jsonld"
                collection.save(str(output_path))
                print(f"OK   Converted: {f} -> {output_path}")


def cmd_sync(args):
    """Sync CEDAR resources locally."""
    client = CEDARClient()
    client.sync_to_local(args.output)


def cmd_publish(args):
    """Publish elements/templates to CEDAR."""
    client = CEDARClient()
    path = Path(args.path)
    files = list(path.rglob("*.json")) if path.is_dir() else [path]

    folder_id = args.folder if hasattr(args, 'folder') and args.folder else None

    for f in files:
        with open(f) as fp:
            data = json.load(fp)

        # Determine if element or template
        is_template = data.get("@type") == "https://schema.metadatacenter.org/core/Template"

        if is_template:
            result = client.upload_template(data, folder_id)
            resource_type = "template"
        else:
            result = client.upload(data, "element", folder_id)
            resource_type = "element"

        if result["success"]:
            print(f"OK   Published {resource_type}: {f.name} -> {result['id']}")
        else:
            print(f"FAIL {resource_type}: {f.name} - {result['error']}")


def main():
    parser = argparse.ArgumentParser(prog="openminds2cedar")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="Generate CEDAR element")
    p.add_argument("schema", help="e.g., core.Subject")
    p.add_argument("-o", "--output", default="output/elements")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("template", help="Create template from elements or registry")
    p.add_argument("name", nargs="?", help="Template name (required unless --from-registry)")
    p.add_argument("elements", nargs="*", help="Element JSON files")
    p.add_argument("-r", "--from-registry", help="Generate from registry template definition")
    p.add_argument("-d", "--description", help="Description")
    p.add_argument("-o", "--output", default="output/templates")
    p.set_defaults(func=cmd_template)

    p = sub.add_parser("validate", help="Validate locally")
    p.add_argument("path", help="File or directory")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("publish", help="Publish to CEDAR")
    p.add_argument("path", help="File or directory")
    p.add_argument("-f", "--folder", help="Target CEDAR folder ID (overrides .env)")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("sync", help="Sync from CEDAR")
    p.add_argument("-o", "--output", default="data/cedar")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("convert", help="Convert instance to openMINDS")
    p.add_argument("path", help="Instance file or directory")
    p.add_argument("-o", "--output", default="output/openminds")
    p.set_defaults(func=cmd_convert)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
