"""Safe automation for published clinic and doctor records."""

from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import (
    ClinicLocation,
    ClinicPage,
    ContentIndexPage,
    Doctor,
    DoctorPage,
    HomePage,
)


logger = logging.getLogger(__name__)


def _parent_for(index_kind: str):
    index = (
        ContentIndexPage.objects.filter(index_kind=index_kind)
        .live()
        .public()
        .first()
    )
    return index or HomePage.objects.first()


def _unique_child_slug(parent, preferred: str, *, exclude_page=None) -> str:
    base = slugify(preferred)[:220] or "profile"
    candidate = base
    suffix = 2
    siblings = parent.get_children()
    if exclude_page is not None:
        siblings = siblings.exclude(pk=exclude_page.pk)
    while siblings.filter(slug=candidate).exists():
        candidate = f"{base[:210]}-{suffix}"
        suffix += 1
    return candidate


def _site_tree_is_initialized() -> bool:
    """Avoid creating profile pages while the starter site is being imported."""

    home = HomePage.objects.first()
    return bool(home and home.get_children().exists())


def _record_introduction(instance) -> str:
    if isinstance(instance, Doctor):
        return instance.short_bio
    return instance.address


def _record_image(instance):
    if isinstance(instance, Doctor):
        return instance.photo
    return instance.hero_image


def _persist_synced_page(page, *, publish_live=False):
    """Keep Explorer/revisions correct without bypassing live publishing."""

    if page.live:
        revision = page.save_revision()
        if publish_live:
            revision.publish()
        return revision

    # Draft pages need their concrete row updated as well as a revision;
    # otherwise Explorer continues to display the pre-sync values.
    page.save()
    return page.save_revision()


def _sync_linked_pages(instance) -> bool:
    """Synchronise pages that explicitly remain connected to their record.

    Published page URLs stay stable. A draft page may follow a corrected record
    slug because it has not yet accumulated public links or search history.
    """

    linked_pages = list(getattr(instance, "pages").all().specific())
    if not linked_pages:
        return False

    for page in linked_pages:
        if not getattr(page, "auto_sync_from_record", False):
            continue
        page.title = instance.name
        page.draft_title = instance.name
        page.introduction = _record_introduction(instance)
        image = _record_image(instance)
        if image is not None:
            page.hero_image = image
        if not page.live:
            parent = page.get_parent()
            page.slug = _unique_child_slug(
                parent,
                instance.slug or instance.name,
                exclude_page=page,
            )
        _persist_synced_page(page, publish_live=page.live)
    return True


def _create_profile_page(*, instance, page_model, relation_name, index_kind):
    if not instance.live:
        return
    if _sync_linked_pages(instance):
        return
    if not instance.create_public_page or not _site_tree_is_initialized():
        return

    parent = _parent_for(index_kind)
    if parent is None:
        logger.warning("No page-tree parent available for %s", instance)
        return

    # Reuse an unlinked matching page before creating anything new. This avoids
    # duplicate URLs when an editor creates the page and snippet in either order.
    matching = page_model.objects.child_of(parent).filter(slug=instance.slug).first()
    if matching is not None and getattr(matching, relation_name + "_id") is None:
        setattr(matching, relation_name, instance)
        matching.title = instance.name
        matching.draft_title = instance.name
        matching.introduction = _record_introduction(instance)
        image = _record_image(instance)
        if image is not None:
            matching.hero_image = image
        _persist_synced_page(
            matching,
            publish_live=(
                matching.live or instance.publish_public_page_automatically
            ),
        )
        return

    page = page_model(
        title=instance.name,
        slug=_unique_child_slug(parent, instance.slug or instance.name),
        introduction=_record_introduction(instance),
        layout_mode="builder",
        live=False,
        has_unpublished_changes=True,
    )
    setattr(page, relation_name, instance)
    image = _record_image(instance)
    if image is not None:
        page.hero_image = image

    parent.add_child(instance=page)
    revision = page.save_revision()
    if instance.publish_public_page_automatically:
        revision.publish()


@receiver(post_save, sender=Doctor, dispatch_uid="aastha_create_doctor_page")
def create_doctor_page(sender, instance, **kwargs):
    _create_profile_page(
        instance=instance,
        page_model=DoctorPage,
        relation_name="doctor",
        index_kind="doctors",
    )


@receiver(post_save, sender=ClinicLocation, dispatch_uid="aastha_create_clinic_page")
def create_clinic_page(sender, instance, **kwargs):
    _create_profile_page(
        instance=instance,
        page_model=ClinicPage,
        relation_name="clinic",
        index_kind="clinics",
    )
