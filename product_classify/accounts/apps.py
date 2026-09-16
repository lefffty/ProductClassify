from django.apps import AppConfig
from django.db.models.signals import post_migrate


ROLE_PERMISSIONS = {
    "handbook-executive": [
        ("ei", ["add_ei", "change_ei", "delete_ei", "view_ei"]),
        ("classes", [
            "add_classstruct", "change_classstruct",
            "delete_classstruct", "view_classstruct",
        ]),
        ("classes", [
            "add_parclass", "change_parclass",
            "delete_parclass", "view_parclass",
        ]),
        ("enums", [
            "add_enums", "change_enums",
            "delete_enums", "view_enums",
        ]),
        ("products", [
            "add_prod", "change_prod",
            "delete_prod", "view_prod",
        ]),
        ("products", [
            "add_parprod", "change_parprod",
            "delete_parprod", "view_parprod",
        ]),
        ("parametr", [
            "add_parametr", "change_parametr",
            "delete_parametr", "view_parametr",
        ]),
        ("agregat", [
            "add_agregat", "change_agregat",
            "delete_agregat", "view_agregat",
        ]),
    ],

    "handbook-user": [
        ("ei", ["view_ei"]),
        ("enums", ["view_enums"]),
        ("parametr", ["view_parametr"]),
        ("classes", ["view_parclass"]),
        ("classes", ["view_classstruct"]),
        ("products", ["view_parprod"]),
        ("products", ["view_prod"]),
        ("agregat", ["view_agregat"]),
    ],

    "builder": [
        ("specifications", [
            "can_get_total_cost_ratio",
            "can_get_product_changelog",
            "can_edit_specification",
        ]),
        ("products", ["can_create_modification", "view_prod"]),
    ],

    "technologist": [
        ("route_tech", [
            "add_economicactivitysubject",
            "change_economicactivitysubject",
            "delete_economicactivitysubject",
            "view_economicactivitysubject",
        ]),
        ("route_tech", [
            "add_groupworkingcenter",
            "change_groupworkingcenter",
            "delete_groupworkingcenter",
            "view_groupworkingcenter",
        ]),
        ("route_tech", [
            "add_prodoperation",
            "change_prodoperation",
            "delete_prodoperation",
            "view_prodoperation",
        ]),
        ("route_tech", [
            "add_prodoperationpos",
            "change_prodoperationpos",
            "delete_prodoperationpos",
            "view_prodoperationpos",
        ]),
        ("enums", [
            "add_enums", "change_enums",
            "delete_enums", "view_enums",
        ]),
        ("products", ["view_prod"]),
    ],

    "chief-mechanic-dept-employee": [
        ("classes", ["keep_account_of_means_of_labor"]),
    ],
}


def assign_role_permissions(sender, apps, using, verbosity, **kwargs):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    for role_code, specs in ROLE_PERMISSIONS.items():
        group = Group.objects.filter(role__code=role_code).first()
        if group is None:
            if verbosity >= 1:
                print(f"  Роль '{role_code}' не найдена — пропускаю")
            continue

        perms = []
        for app_label, codenames in specs:
            found = list(Permission.objects.filter(
                content_type__app_label=app_label,
                codename__in=codenames,
            ))
            missing = set(codenames) - {p.codename for p in found}
            if missing and verbosity >= 1:
                print(
                    f"  [{role_code}] Не найдены: "
                    f"{app_label}.{sorted(missing)}"
                )
            perms.extend(found)

        group.permissions.add(*perms)
        if verbosity >= 2:
            print(f"  [{role_code}] назначено {len(perms)} прав")


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Учетные записи"

    def ready(self):
        post_migrate.connect(
            assign_role_permissions,
            dispatch_uid="accounts.assign_role_permissions",
        )
