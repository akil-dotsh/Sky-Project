"""
File:        apps/schedule/apps.py
Author:      Ryan Thompson (W1789088)
Module:      5COSC021W — Software Development Group Project
Description: Django AppConfig for the schedule app, registering it
             under the dotted path apps.schedule.
Co-authors:  None.
"""

from django.apps import AppConfig


class ScheduleConfig(AppConfig):
    name = 'apps.schedule'
