from django.conf import settings
from django.db.models import Model


class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """

    route_app_labels = {"auth", "contenttypes"}

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "auth_db"
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return "auth_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == "auth_db"
        return None


class ApplicationRouter:
    """
    Puts `apply` models in a different database.
    """

    APP_LABEL = "apply"
    APP_DB = settings.APP_DB

    DB_MAP = {APP_LABEL: APP_DB}

    def _get_db(self, app_label: str):
        return self.DB_MAP.get(app_label)

    def db_for_read(self, model, **hints):
        return self._get_db(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return self._get_db(model._meta.app_label)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.APP_LABEL:
            return db == self.APP_DB
        return None
