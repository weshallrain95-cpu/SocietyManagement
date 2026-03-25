import re
from statutory.models import LegalArtifactTemplate


PLACEHOLDER_PATTERN = r"\{\{\s*(.*?)\s*\}\}"


def extract_placeholders(template_body):
    return set(re.findall(PLACEHOLDER_PATTERN, template_body))


def scan_all_templates():

    placeholder_map = {}

    templates = LegalArtifactTemplate.objects.all()

    for template in templates:

        placeholders = extract_placeholders(template.template_body)

        placeholder_map[template.artifact_code] = list(placeholders)

    return placeholder_map
    