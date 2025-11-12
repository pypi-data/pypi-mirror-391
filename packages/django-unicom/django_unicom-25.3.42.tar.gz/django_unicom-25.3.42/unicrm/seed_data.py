from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Iterable, Sequence

from django.apps import apps as django_apps
from django.core.exceptions import AppRegistryNotReady
from django.db import transaction

from .models import Segment


logger = logging.getLogger(__name__)
UNICRM_UNIBOT_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "unicrm" / "unibot"


@dataclass(frozen=True)
class SegmentSeed:
    """
    Encapsulates the metadata required to create a default Segment instance.
    """

    name: str
    description: str
    code: str


DEFAULT_SEGMENTS: Sequence[SegmentSeed] = (
    SegmentSeed(
        name="All Contacts",
        description="All contacts that have an email address.",
        code="""\
def apply(qs):
    return qs.filter(
        email__isnull=False,
    ).exclude(
        email__exact='',
    ).distinct()
""",
    ),
    SegmentSeed(
        name="Staff Contacts",
        description="Staff-owned contacts that have an email address.",
        code="""\
def apply(qs):
    return qs.filter(
        owner__isnull=False,
        owner__is_staff=True,
        email__isnull=False,
    ).exclude(
        email__exact='',
    ).distinct()
""",
    ),
    SegmentSeed(
        name="Verified Users",
        description="Contacts linked to auth users with verified email addresses.",
        code="""\
def apply(qs):
    return qs.filter(
        attributes__auth_user_id__isnull=False,
        attributes__auth_user_email_verified=True,
        email__isnull=False,
    ).exclude(
        email__exact='',
    ).distinct()
""",
    ),
    SegmentSeed(
        name="Active Users",
        description="Contacts linked to active auth users with email addresses.",
        code="""\
def apply(qs):
    return qs.filter(
        user__isnull=False,
        user__is_active=True,
        email__isnull=False,
    ).exclude(
        email__exact='',
    ).distinct()
""",
    ),
)

LEGACY_SEGMENTS_TO_REMOVE: Sequence[str] = (
    "Verified Contacts",
)

LEGACY_SEGMENT_CODE_VARIANTS: dict[str, tuple[str, ...]] = {
    "All Contacts": (
        """\
def apply(qs):
    return qs.distinct()
""",
    ),
    "Staff Contacts": (
        """\
def apply(qs):
    return qs.filter(owner__isnull=False, owner__is_staff=True).distinct()
""",
    ),
}

LEGACY_SEGMENT_DESCRIPTIONS: dict[str, tuple[str, ...]] = {
    "All Contacts": (
        "Every contact stored in the CRM.",
    ),
    "Staff Contacts": (
        "Contacts owned by staff users.",
    ),
}


def ensure_default_segments(segment_seeds: Iterable[SegmentSeed] | None = None) -> list[Segment]:
    """
    Ensure that the default Segment records exist.

    Segments are only created when missing; an existing segment is preserved
    to avoid clobbering manual edits made by administrators.
    """

    seeds = tuple(segment_seeds) if segment_seeds is not None else DEFAULT_SEGMENTS
    created_segments: list[Segment] = []

    seed_names = {seed.name for seed in seeds}

    with transaction.atomic():
        if LEGACY_SEGMENTS_TO_REMOVE:
            Segment.objects.filter(name__in=LEGACY_SEGMENTS_TO_REMOVE).exclude(
                name__in=seed_names
            ).delete()

        for seed in seeds:
            segment, created = Segment.objects.get_or_create(
                name=seed.name,
                defaults={"description": seed.description, "code": seed.code},
            )
            if not created:
                fields_to_update: dict[str, str] = {}
                legacy_desc = LEGACY_SEGMENT_DESCRIPTIONS.get(seed.name, ())
                if not segment.description or segment.description in legacy_desc:
                    fields_to_update["description"] = seed.description
                legacy_variants = {
                    variant.strip()
                    for variant in LEGACY_SEGMENT_CODE_VARIANTS.get(seed.name, ())
                }
                if not segment.code or segment.code.strip() in legacy_variants:
                    fields_to_update["code"] = seed.code

                if fields_to_update:
                    for field, value in fields_to_update.items():
                        setattr(segment, field, value)
                    segment.save(update_fields=[*fields_to_update.keys(), "updated_at"])
            else:
                created_segments.append(segment)

    return created_segments


UNICRM_BOT_NAME = "Unicrm Lead Finder"
UNICRM_BOT_CATEGORY = "unicrm"
GPT_SEARCH_TEMPLATE = "gpt_search_tool.py"
EMAIL_VALIDATION_TEMPLATE = "validate_emails_tool.py"
COMPANY_DOMAIN_TEMPLATE = "company_domain_deduplicator_tool.py"
COMPANY_AND_STAFF_TEMPLATE = "company_and_staff_import_tool.py"
UNICRM_LEAD_FINDER_BOT_TEMPLATE = "unicrm_lead_finder_bot.py"




def _unibot_models_available() -> bool:
    if not django_apps.is_installed("unibot"):
        return False
    try:
        django_apps.get_model("unibot", "Bot")
        django_apps.get_model("unibot", "Tool")
    except (LookupError, AppRegistryNotReady):
        return False
    return True


def _load_unibot_template(filename: str) -> str:
    try:
        config = django_apps.get_app_config("unibot")
    except (LookupError, AppRegistryNotReady):
        return ""
    template_path = Path(config.path) / "templates" / "unibot" / filename
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Unibot template %s was not found at %s", filename, template_path)
        return ""


def _load_unicrm_unibot_template(filename: str) -> str:
    template_path = UNICRM_UNIBOT_TEMPLATE_DIR / filename
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Unicrm unibot template %s was not found at %s", filename, template_path)
        return ""


def _ensure_tool(tool_model, name: str, description: str, code: str):
    if not code:
        logger.debug("Skipping tool %s because no code was provided.", name)
        return None
    tool, created = tool_model.objects.get_or_create(
        name=name,
        defaults={
            "description": description,
            "code": code,
        },
    )
    updates: dict[str, str] = {}
    if not created:
        if (tool.description or "") != description:
            updates["description"] = description
        existing_code = (tool.code or "").strip()
        desired_code = code.strip()
        if existing_code != desired_code:
            updates["code"] = code
        if updates:
            for field, value in updates.items():
                setattr(tool, field, value)
            tool.save(update_fields=list(updates.keys()))
    return tool


def ensure_unicrm_bot_assets() -> bool:
    """
    Ensure the Unicrm lead finder bot plus its required tools exist when unibot is installed.
    """

    if not _unibot_models_available():
        return False

    Tool = django_apps.get_model("unibot", "Tool")
    Bot = django_apps.get_model("unibot", "Bot")

    tool_specs = [
        (
            "GPT Web Search",
            "Intelligent GPT-powered web search used for researching potential companies.",
            _load_unibot_template(GPT_SEARCH_TEMPLATE),
        ),
        (
            "Email Validation",
            "Validates email addresses through the Reacher service.",
            _load_unibot_template(EMAIL_VALIDATION_TEMPLATE),
        ),
        (
            "Company Domain Deduplicator",
            "Checks if company domains already exist before attempting to create new records.",
            _load_unicrm_unibot_template(COMPANY_DOMAIN_TEMPLATE),
        ),
        (
            "Company & Staff Import",
            "Atomically creates a new company plus its validated staff contacts.",
            _load_unicrm_unibot_template(COMPANY_AND_STAFF_TEMPLATE),
        ),
    ]

    tools = [
        _ensure_tool(Tool, name, description, code)
        for name, description, code in tool_specs
    ]
    tools = [tool for tool in tools if tool is not None]
    if not tools:
        return False

    bot_code = _load_unicrm_unibot_template(UNICRM_LEAD_FINDER_BOT_TEMPLATE)
    if not bot_code:
        return False

    bot, created = Bot.objects.get_or_create(
        name=UNICRM_BOT_NAME,
        defaults={
            "category": UNICRM_BOT_CATEGORY,
            "code": bot_code,
        },
    )
    updates: dict[str, str] = {}
    if not created:
        if bot.category != UNICRM_BOT_CATEGORY:
            updates["category"] = UNICRM_BOT_CATEGORY
        if (bot.code or "").strip() != bot_code.strip():
            updates["code"] = bot_code
        if updates:
            for field, value in updates.items():
                setattr(bot, field, value)
            bot.save(update_fields=list(updates.keys()))

    existing_tool_ids = set(bot.tools.values_list("id", flat=True))
    missing_tools = [tool for tool in tools if tool.id not in existing_tool_ids]
    if missing_tools:
        bot.tools.add(*missing_tools)

    return True
