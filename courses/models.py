from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class Channel(models.Model):
    owner = models.OneToOneField(to=User,
                                 on_delete=models.DO_NOTHING)
    # owner of the channel

    title = models.CharField(max_length=100)
    # title of the channel

    background_color = models.CharField(max_length=10, blank=True)
    # background color of the channel main page

    preview_image = models.ImageField(upload_to='channel_preview_images/')
    # On the channel list / boards

    background_image = models.ImageField(blank=True, upload_to='channel_background_images/')
    # background image at the back of the channel main page

    cover_image = models.ImageField(upload_to='channel_cover_images/', blank=True)
    # like 1440x900 img at the top of the channel description

    channel_description = models.TextField(blank=True)
    # description of channel at the top of channel page

    owner_full_name = models.CharField(max_length=200)
    # full name of channel owner

    owner_photo = models.ImageField(upload_to='channel_owner_photos/')
    # real photo of channel owner

    owner_interview = models.TextField()
    # little interview about channel owner

    subscribers = models.ManyToManyField(to=User, related_name='subscribes', blank=True)
    # many-to-may relationship between users and channels implementing subscribe system


class CourseThemes(models.TextChoices):
    ARITHMETIC = 'ARITHMETIC', _('Арифметика')
    MATH = 'MATH', _('Математика')
    ALGEBRA = 'ALGEBRA', _('Алгебра')
    CALCULUS = 'CALCULUS', _('Математический анализ')
    T_W_I_M_S = 'T_W_I_M_S', _('Теория вероятностей и математическая статистика')
    DISCRETE_MATH = 'DISCRETE_MATH', _('Дискретная математика')
    NUMBER_THEORY = 'NUMBER_THEORY', _('Теория чисел')
    WEB = 'WEB', _('Web-Программирование')
    DATA_SCIENCE = 'DATA_SCIENCE', _('Data science / Наука о данных')
    NEURAL_NET_MACHINE_LEARNING = 'NEURAL_MACHINE', _('Нейронные сети и машинное обучение')
    ALGORITHMS = 'ALGORITHMS', _('Алгоритмы и структуры данных')
    MOBILE = 'MOBILE', _('Мобильная разработка')
    TESTING = 'TESTING', _('Тестирование')
    DEV_OPS = 'DEV_OPS', _('DevOps')
    MANAGEMENT = 'MANAGEMENT', _('Менеджмент')
    BUSINESS = 'BUSINESS', _('Бизнес')
    FOREIGN_LANGUAGES = 'FOREIGN_LANGUAGES', _('Иностранные языки')
    ABSTRACT = 'NONE', _('Без направления')


class Course(models.Model):
    owner = models.ForeignKey(to=User,
                              on_delete=models.DO_NOTHING,
                              related_name='own_courses',
                              default=None)
    # owner of the channel->course

    channel = models.ForeignKey(to=Channel,
                                on_delete=models.CASCADE,
                                related_name='courses',
                                null=True,
                                default=None)
    # channel where course implemented

    title = models.CharField(max_length=150)
    # title of the course

    slug = models.SlugField(unique=True, max_length=100, default=title)
    # course unique identifier in url

    theme = models.TextField(choices=CourseThemes.choices, default=CourseThemes.ABSTRACT)
    # course theme / tag

    created = models.DateTimeField(default=now, editable=False)
    # time of course creation

    preview_picture = models.ImageField(upload_to='course_preview_images/', blank=True)
    # preview image at the courses list

    main_picture = models.ImageField(upload_to='course_main_pictures/', blank=True)

    # picture at the course main page

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(to=Course,
                               on_delete=models.CASCADE,
                               related_name='modules')
    # heading course of module

    title = models.CharField(max_length=200)
    # title of the module

    description = models.TextField(blank=True)

    # some information about module content

    def __str__(self):
        return self.title


class ModuleDescriptionListElement(models.Model):
    module = models.ForeignKey(to=Module,
                               on_delete=models.CASCADE,
                               related_name='list_elements')
    text = models.TextField(blank=True)

    class Meta:
        ordering = ('-id',)


class CourseDescriptionBlockImagePosition(models.TextChoices):
    LEFT = 'LEFT', _('Слева от текста')
    UP = 'UP', _('Сверху над текстом')
    DOWN = 'DOWN', _('Снизу под текстом')
    RIGHT = 'RIGHT', _('Справа от текста')


class CourseDescriptionBlock(models.Model):
    course = models.ForeignKey(to=Course,
                               on_delete=models.CASCADE,
                               related_name='description_blocks')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='course_description_block_images/', blank=True)
    image_position = models.TextField(choices=CourseDescriptionBlockImagePosition.choices,
                                      default=CourseDescriptionBlockImagePosition.LEFT)
    created = models.DateTimeField(default=now, editable=False)

    class Meta:
        ordering = ('-created',)
