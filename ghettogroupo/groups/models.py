import uuid
from slugify import slugify

from django.urls import reverse_lazy
from django.db import models
from django.utils.translation import ugettext_lazy as _


GROUPS = [
    ("Regular", "Regular"),
    ("Education", "Educational"),
    ("Organization", "Organization")
]


class Group(models.Model):
    code = models.UUIDField(_("Code"), unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    type =  models.CharField(_("Type"), max_length=50, choices=GROUPS)
    owner = models.ForeignKey("users.User", verbose_name=_("Owner"), on_delete=models.CASCADE)
    name = models.CharField(_("Group Name"), max_length=50)
    description = models.TextField(_("Description"))

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")

    def __str__(self):
        return self.name

    def get_group_url(self, user):
        return reverse_lazy('test', kwargs={"username": user.username, "code": self.code})
    
    def get_all_members(self):
        return Membership.objects.filter(group=self)

    def get_active_members(self):
        return self.get_all_members().filter(isActive=True)
    
    def get_managers(self):
        return self.get_active_members().filter(isManager=True)
    
    def get_assigners(self):
        return self.get_active_members().filter(isAssigner=True)
    
    


class Membership(models.Model):
    membership_id = models.UUIDField(_("Membership ID"), primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey("groups.Group", verbose_name=_("Group"), on_delete=models.CASCADE)
    member = models.ForeignKey("users.User", verbose_name=_("Member"), on_delete=models.CASCADE)
    isOwner = models.BooleanField(_("Is Owner"), default=False)
    isAssigner = models.BooleanField(_("Is Assigner"), default=False)
    isManager = models.BooleanField(_("Is Manager"), default=False)
    isActive = models.BooleanField(_("Is Active"), default=True)
    

    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        unique_together = ('group', 'member')

    def __str__(self):
        return '{}\t{}'.format(self.group.code, self.member.username)