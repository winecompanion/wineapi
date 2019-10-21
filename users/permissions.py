from rest_framework.permissions import BasePermission, SAFE_METHODS

from . import WINERY
from api.models import Winery

SAFE_ACTIONS = ['list', 'retrieve']
NOT_SAFE_ACTIONS = ['create', 'update', 'partial_update', 'destroy']


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):

        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and obj.user == request.user


class IsWineryUser(BasePermission):

    def has_object_permission(self, request, view, obj):

        return True if request.user.user_type == WINERY else False


class AllowCreateUserButUpdateOwnerOnly(BasePermission):
    """
    Custom permission:
        - allow anonymous POST
        - allow authenticated GET and PUT on *own* record
        - allow all actions for staff
    """

    def has_permission(self, request, view):
        return view.action == 'create' or request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            view.action in ['retrieve', 'update', 'partial_update', 'destroy'] and obj.id == request.user.id
            or request.user.is_staff
        )


class ListAdminOnly(BasePermission):
    """
    Custom permission to only allow access to lists only for admins
    """

    def has_permission(self, request, view):
        return view.action != 'list' or request.user and request.user.is_staff


class AdminOnly(BasePermission):
    """
    Custom permission to only allow access only for admins
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class AllowWineryOwnerOrReadOnly(BasePermission):
    """
    Custom permission:
        - allow create and update only for winery owner.
        - allow anonimous GET
    """

    def has_permission(self, request, view):
        return view.action not in NOT_SAFE_ACTIONS or request.user.is_authenticated and request.user.winery

    def has_object_permission(self, request, view, obj):
        obj_winery = None
        if isinstance(obj, Winery):
            obj_winery = obj.id
        else:
            obj_winery = getattr(obj, 'winery', None)

        return (
            view.action in SAFE_ACTIONS
            or request.user.winery and obj_winery == request.user.winery
            or request.user.is_staff
        )


class AdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin to edit and create.
    """

    def has_permission(self, request, view):
        return view.action in SAFE_ACTIONS or request.user and request.user.is_staff


class AllowCreateButUpdateOwnerOnly(BasePermission):
    """
    Custom permission:
        - allow anonymous POST
        - allow authenticated GET and PUT on *own* record
        - allow all actions for staff
    """

    def has_permission(self, request, view):
        return view.action == 'create' or request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            view.action in ['retrieve', 'update', 'partial_update', 'destroy'] and obj.user.id == request.user.id
            or request.user.is_staff
        )


class LoginRequiredToEdit(BasePermission):

    def has_permission(self, request, view):
        return view.action in SAFE_ACTIONS or request.user.is_authenticated


class CreateOnlyIfWineryApproved(BasePermission):

    def has_permission(self, request, view):
        return view.action != 'create' or request.user.winery.available_since
