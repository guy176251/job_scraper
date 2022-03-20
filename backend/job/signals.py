from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CompanyName, Job


@receiver(post_save, sender=Job)
def create_application(
    sender: Job,
    instance: Job,
    created: bool,
    raw: bool,
    using,
    update_fields: set,
    **kwargs,
):
    instance.create_application()


# @receiver(post_save, sender=CompanyAlias)
# def create_slug(
#     sender: CompanyAlias,
#     instance: CompanyAlias,
#     created: bool,
#     raw: bool,
#     using,
#     update_fields: set,
#     **kwargs,
# ):
#     instance.create_slug()
