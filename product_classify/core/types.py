from collections import namedtuple


TotalCostRatioResult = namedtuple(
    "TotalCostRatioResult",
    field_names=[
        "parent_id",
        "parent_prod_name",
        "child_id",
        "child_prod_name",
        "quantity",
        "ei_short_name",
        "total_cost",
        "level",
    ],
)

SpecificationRecordResult = namedtuple(
    "SpecificationRecordResult",
    field_names=[
        "pair_id",
        "parent_id",
        "child_id",
        "prod_num",
        "quantity",
    ],
)

SpecificationLogResult = namedtuple(
    "SpecificationLogResult",
    field_names=[
        "log_id",
        "parent_id",
        "comp_id",
        "updated_at",
        "log_string",
    ],
)

ModificationResult = namedtuple(
    "ModificationResult",
    field_names=[
        "modification_id",
    ]
)

EASRecordResult = namedtuple(
    "EASRecordResult",
    field_names=[
        "id",
        "name",
        "short_name",
        "level",
    ]
)

TechRouteRecord = namedtuple(
    "TechRouteRecord",
    field_names=[
        "input_prod_name",
        "input_prod_short_name",
        "output_prod_name",
        "output_prod_short_name",
        "operation_name",
        "operation_short_name",
        "profession_name",
        "gwc_name",
        "gwc_short_name",
        "eas_name",
        "eas_short_name",
        "qualification_name",
        "input_quantity",
        "output_quantity",
        "t_pz",
        "t_sht",
        "num_of_workers",
    ]
)