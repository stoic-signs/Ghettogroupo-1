from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from quizzes.models import Responses
from tasks.models import Task
from groups.models import Group, Membership
from developer.models import DeveloperKey

INTERESTS = [
    ("Agriculture", "Agriculture"),
    ("Arts and Entertainment", "Arts and Entertainment"),
    ("Education", "Education"),
    ("Food", "Food"),
    ("Hardware and Automobiles", "Hardware and Automobiles"),
    ("Healthcare and Medicine", "Healthcare and Medicine"),
    ("Law and Enforcement", "Law and Enforcement"),
    ("Sales and Management", "Sales and Management"),
    ("Science and Technology", "Science and Technology"),
]

OCCUPATIONS = [
    ("Actor", "Actor"),
    ("Architecture", "Architecture"),
    ("Armed Forces", "Armed Forces"),
    ("Artisan", "Artisan"),
    ("Automobile", "Automobile"),
    ("Construction", "Construction"),
    ("Dancer", "Dancer"),
    ("Design and Creativity", "Design and Creativity"),
    ("Education", "Education"),
    ("Engineering", "Engineering"),
    ("Farming", "Farming"),
    ("Finance", "Finance"),
    ("Fine Arts", "Fine Arts"),
    ("Food and Services", "Food and Services"),
    ("Human Resources", "Human Resources"),
    ("Information Technology", "Information Technology"),
    ("Judiciary", "Judiciary"),
    ("Legislation ", "Legislation "),
    ("Marketing", "Marketing"),
    ("Medical", "Medical"),
    ("Medical practitioner", "Medical practitioner"),
    ("Musician", "Musician"),
    ("Nursing Staff", "Nursing Staff"),
    ("Pharmacist", "Pharmacist"),
    ("Producer", "Producer"),
    ("Public health executive", "Public health executive"),
    ("Researcher", "Researcher"),
    ("Sales", "Sales"),
    ("Social Sciences", "Social Sciences"),
    ("Water supply", "Water supply"),
    ("Wood and metalwork", "Wood and metalwork"),
    ("Writer", "Writer")
]


class User(AbstractUser):
    email = models.EmailField(_('Email Address'), unique=True)
    username = models.CharField(max_length=20, unique=True)
    fullName = models.CharField(_("Full Name"), max_length=20)
    USERNAME = 'username'
    REQUIRED_FIELDS = ['email', 'fullName']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    @property
    def profile(self):
        if UserProfile.objects.filter(user=self):
            return UserProfile.objects.get(user=self)
        else:
            return None

    @property
    def profileimage(self):
        return UserProfile.objects.get(user=self).image

    def hasOwnerPerm(self):
        return True if Membership.objects.filter(member=self, isOwner=True) else False
    
    def hasAssignerPerm(self):
        return True if (self.hasOwnerPerm() or Membership.objects.filter(member=self, isAssigner=True)) else False
    
    def hasManagerPerm(self):
        return True if (self.hasOwnerPerm() or Membership.objects.filter(member=self, isManager=True)) else False
    
    def hasDeveloperPerm(self):
        return True if DeveloperKey.objects.filter(user=self).first() else False
    
    def get_groups(self):
        groups = Membership.objects.filter(
            member=self
        ).values_list('group').distinct()
        return Group.objects.filter(code__in=groups)

    def get_responses(self, quiz):
        return Responses.objects.filter(respondant=self, choice__question__quiz=quiz)

    def get_marks(self, quiz):
        responses = self.get_responses(quiz)
        count = 0
        for item in responses:
            # print(item.choice, item.choice.choice_text)
            if item.choice.isAnswer:
                count += item.choice.question.max_marks
        return count
    
    def get_tasks(self, code):
        tasks = Task.objects.filter(assigned_group=code)
        task_list = []
        for task in tasks:
            if (self.pk,) in task.assigned_to().values_list('member__pk'):
                task_list.append(task.pk)
        return Task.objects.filter(pk__in=list(set(task_list)))


class Interest(models.Model):
    interest = models.CharField(_("Interest"), max_length=100, choices=INTERESTS)

    def __str__(self):
        return self.interest

    def __unicode__(self):
        return self.interest

    class Meta:
        verbose_name = 'Interest'
        verbose_name_plural = 'Interests'


class UserProfile(models.Model):
    user = models.OneToOneField(User, default='default.jpg', on_delete=models.CASCADE)
    image = models.ImageField(_("Profile Picture"), upload_to='profilepictures/')
    age = models.IntegerField(_("Age"))
    organization = models.CharField(_("Organization"), max_length=75, help_text="write full form of the organization")
    occupation = models.CharField(_("Occupation"), choices=OCCUPATIONS, max_length=100)
    interest = models.ManyToManyField(Interest)

    class Meta:
        verbose_name = 'UserProfile'
        verbose_name_plural = 'UserProfiles'

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def save(self):
        super().save()
        img = Image.open(self.image.path)
        if (img.height > 300) or (img.width > 300):
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)