from django.views.generic.base import ContextMixin
from django.db import transaction, InternalError
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


class CycleCheckFormMixin:
    cycle_check_field: str = "main_class"
    cycle_check_marker: str = ""
    cycle_check_error_msg: str = ""

    def _post_clean(self):
        super()._post_clean()

        if self.errors:
            return
        
        try:
            with transaction.atomic():
                super().save(commit=True)
                transaction.set_rollback(True)
        except InternalError as e:
            if self.cycle_check_marker in str(e):
                self.add_error(
                    self.cycle_check_field,
                    self.cycle_check_error_msg,
                )
            else:
                raise



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
