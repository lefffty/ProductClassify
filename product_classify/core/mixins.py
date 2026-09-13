from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from classes.models import ClassStruct
from classes.constants import ProductsConsts


class CommonContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fastener_classes = ClassStruct.objects.filter(
            main_class__exact=ProductsConsts.FASTENER_ID
        )
        context["fastener_classes"] = fastener_classes
        return context


class GroupRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    group_required = ()
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(
            role__code__in=self.group_required
        ).exists()


class HandbookExecutiveRequiredMixin(GroupRequiredMixin):
    group_required = ("handbook-executive",)


class HandbookUserRequiredMixin(GroupRequiredMixin):
    group_required = ("handbook-user",)


class BuilderRequiredMixin(GroupRequiredMixin):
    group_required = ("builder",)


class TechnologistRequiredMixin(GroupRequiredMixin):
    group_required = ("technologist",)


class ChiefMechanicDeptEmployeeRequiredMixin(GroupRequiredMixin):
    group_required = ("chief-mechanic-dept-employee",)


class SalesDeptEmployeeRequiredMixin(GroupRequiredMixin):
    group_required = ("sales-dept-employee",)


class ProductionDeptEmployeeRequiredMixin(GroupRequiredMixin):
    group_required = ("production-dept-employee",)


class ClientRequiredMixin(GroupRequiredMixin):
    group_required = ("client",)


class EconomicPlanningDeptEmployeeRequiredMixin(GroupRequiredMixin):
    group_required = ("economic-planning-dept-employee",)
