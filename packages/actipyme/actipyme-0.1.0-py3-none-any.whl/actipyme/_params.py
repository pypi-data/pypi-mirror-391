from typing import TypedDict, NotRequired, Sequence, Literal
from pendulum import DateTime


class ParamsDict(TypedDict):
    pass


class GetParamsDict(ParamsDict):

    offset: NotRequired[int]
    limit: NotRequired[int]


class GetParamsWithNameWords(GetParamsDict):
    name: NotRequired[str]
    words: NotRequired[str]


class GetCommentsParams(GetParamsDict):

    include_referenced: NotRequired[Sequence[Literal["users"]]]


class GetCustomersParams(GetParamsWithNameWords):

    ids: NotRequired[Sequence[int]]
    sort: NotRequired[Literal["+created", "-created", "+name", "-name"]]
    archived: NotRequired[bool]


class GetDepartmentsParams(GetParamsDict):
    name: NotRequired[str]
    sort: NotRequired[Literal["+name", "-name"]]


class GetLeavetimeParams(ParamsDict):

    user_ids: NotRequired[Sequence[int]]
    leave_type_ids: NotRequired[Sequence[int]]
    date_from: DateTime
    date_to: NotRequired[DateTime]
    stop_after: NotRequired[int]
    include_referenced: NotRequired[
        Sequence[Literal["departments", "timeZoneGroups", "users", "leaveTypes"]]
    ]


class GetLeaveTypeParams(GetParamsWithNameWords):

    ids: NotRequired[Sequence[int]]
    balance: NotRequired[Literal["None", "Sick", "PTO"]]
    archived: NotRequired[bool]
    sort: NotRequired[Literal["+name", "-name"]]


class GetProjectsParams(GetParamsWithNameWords):

    ids: NotRequired[Sequence[int]]
    customer_ids: NotRequired[Sequence[int]]
    sort: NotRequired[Literal["+created", "-created", "+name", "-name"]]
    archived: NotRequired[bool]
    include_referenced: NotRequired[Sequence[Literal["customers"]]]


class GetTasksParams(GetParamsWithNameWords):
    ids: NotRequired[Sequence[int]]
    customer_ids: NotRequired[Sequence[int]]
    project_ids: NotRequired[Sequence[int]]
    type_of_work_ids: NotRequired[Sequence[int]]
    workflow_status_ids: NotRequired[Sequence[int]]
    sort: NotRequired[
        Literal["+created", "-created", "+name", "-name", "+status", "-status"]
    ]
    status: NotRequired[Literal["open", "completed"]]
    include_referenced: NotRequired[
        Sequence[Literal["customers", "typesOfWork", "projects", "workflowStatuses"]]
    ]


class GetTimetrackParams(ParamsDict):
    user_ids: NotRequired[Sequence[int]]
    task_ids: NotRequired[Sequence[int]]
    project_ids: NotRequired[Sequence[int]]
    customer_ids: NotRequired[Sequence[int]]
    approved: NotRequired[bool]
    date_from: DateTime
    date_to: NotRequired[DateTime]
    stop_after: NotRequired[int]
    include_referenced: NotRequired[
        Sequence[
            Literal[
                "departments",
                "typesOfWork",
                "timeZoneGroups",
                "comments",
                "users",
                "tasks",
                "customers",
                "approvalStatus",
                "projects",
                "workflowStatuses",
            ]
        ]
    ]


class GetTimeZoneGroupsParams(GetParamsDict):
    name: NotRequired[str]
    sort: NotRequired[Literal["+name", "-name"]]


class GetTypesOfWorkParams(GetParamsWithNameWords):

    ids: NotRequired[Sequence[int]]
    archived: NotRequired[bool]
    billable: NotRequired[bool]
    sort: NotRequired[Literal["+name", "-name"]]


class GetUsersParams(GetParamsDict):
    email: NotRequired[str]
    ids: NotRequired[Sequence[int]]
    department: NotRequired[Sequence[int]]
    time_zone_group: NotRequired[Sequence[int]]
    active: NotRequired[bool]
    username: NotRequired[str]
    name: NotRequired[str]
    sort: NotRequired[
        Literal[
            "+lastName",
            "-lastName",
            "+hired",
            "-hired",
            "+department",
            "-department",
            "+timeZoneGroup",
            "-timeZoneGroup",
            "+username",
            "-username",
        ]
    ]
    include_referenced: NotRequired[Sequence[Literal["departments", "timeZoneGroups"]]]


class GetUserScheduleParams(ParamsDict):
    date_from: DateTime
    date_to: NotRequired[DateTime]


class GetWorkflowStatusesParams(GetParamsWithNameWords):
    ids: NotRequired[Sequence[int]]
    type: NotRequired[Literal["open", "completed"]]
    sort: NotRequired[Literal["+name", "-name", "+type", "-type"]]
