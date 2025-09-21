"""
Database router to direct database operations
for different apps to their respective databases.
"""


class DbRouter:
    """
    A database router to control all database operations
    on models for different apps.
    """

    route_app_labels = {
        "auth": "auth",
        "users": "users",
        "videos": "videos",
        "billing": "billing",
    }

    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to their respective databases.
        """
        return self.route_app_labels.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to their respective databases.
        """
        return self.route_app_labels.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth, users, videos,
        or billing apps is involved.
        """
        db_obj1 = self.route_app_labels.get(obj1._meta.app_label)
        db_obj2 = self.route_app_labels.get(obj2._meta.app_label)
        if db_obj1 and db_obj2:
            return db_obj1 == db_obj2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the auth, users, videos, and billing apps only
        appear in their respective databases.
        """
        if app_label in self.route_app_labels:
            return db == self.route_app_labels[app_label]
        return None
