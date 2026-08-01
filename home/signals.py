"""Safe automation for newly published clinic and doctor records."""

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


def _unique_child_slug(parent, preferred: str) -> str:
    base = slugify(preferred)[:220] or "profile"
    candidate = base
    suffix = 2
    while parent.get_children().filter(slug=candidate).exists():
        candidate = f"{base[:210]}-{suffix}"
        suffix += 1
    return candidate


def _site_tree_is_initialized() -> bool:
    """Avoid creating profile pages while the starter site is being imported."""

    home = HomePage.objects.first()
    return bool(home and home.get_children().exists())


def _create_profile_page(*, instance, page_model, relation_name, index_kind):
    if not instance.live or not instance.create_public_page:
        return
    if getattr(instance, "pages").exists():
        return
    if not _site_tree_is_initialized():
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
        revision = matching.save_revision()
        if instance.publish_public_page_automatically:
            revision.publish()
        return

    page = page_model(
        title=instance.name,
        slug=_unique_child_slug(parent, instance.slug or instance.name),
        introduction=(
            instance.short_bio if isinstance(instance, Doctor) else instance.address
        ),
        layout_mode="builder",
        live=False,
        has_unpublished_changes=True,
    )
    setattr(page, relation_name, instance)
    if getattr(instance, "hero_image", None):
        page.hero_image = instance.hero_image
    elif getattr(instance, "photo", None):
        page.hero_image = instance.photo

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
