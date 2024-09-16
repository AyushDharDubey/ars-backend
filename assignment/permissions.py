from rest_framework.permissions import BasePermission


class IsReviewee(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Reviewee').exists()


class IsReviewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Reviewer').exists()
