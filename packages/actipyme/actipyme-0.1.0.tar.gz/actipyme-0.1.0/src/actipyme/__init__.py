from enum import Enum
from pendulum import DateTime
from typing import (
    Optional,
    Sequence,
    Type,
    Unpack,
)
import requests
from requests.auth import AuthBase
from pydantic.alias_generators import to_camel
from .models import (
    serialize_date,
    ApiModel,
    ApiError,
    CustomerWithAllowedAction,
    CustomerList,
    CommentList,
    Department,
    DepartmentList,
    WithDetails,
    Info,
    LeaveTimeList,
    LeaveType,
    LeaveTypeList,
    ProjectWithAllowedActions,
    ProjectList,
    TaskWithAllowedActions,
    TaskList,
    TimeTrackRecord,
    TimeTrackList,
    TimeZoneGroup,
    TimeZoneGroupList,
    TypeOfWork,
    TypeOfWorkList,
    UserWithAllowedActions,
    UserList,
    UserSchedule,
    WorkflowStatusWithAllowedActions,
    WorkflowStatusList,
)
from ._params import (
    ParamsDict as _ParamsDict,
    GetCustomersParams as _GetCustomersParams,
    GetCommentsParams as _GetCommentsParams,
    GetDepartmentsParams as _GetDepartmentsParams,
    GetLeavetimeParams as _GetLeavetimeParams,
    GetLeaveTypeParams as _GetLeaveTypeParams,
    GetProjectsParams as _GetProjectsParams,
    GetTasksParams as _GetTasksParams,
    GetTimetrackParams as _GetTimetrackParams,
    GetTimeZoneGroupsParams as _GetTimeZoneGroupsParams,
    GetTypesOfWorkParams as _GetTypesOfWorkParams,
    GetUsersParams as _GetUsersParams,
    GetUserScheduleParams as _GetUserScheduleParams,
    GetWorkflowStatusesParams as _GetWorkflowStatusesParams,
)


class ApiException(Exception):

    def __init__(self, code: int, err: ApiError, *args) -> None:
        super().__init__(*args)
        self.code = code
        self.err = err


class ApiClient:

    def __init__(self, url: str, auth: tuple[str, str] | AuthBase):
        self._url = url
        self._auth = auth

    def _get(
        self, path: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ):
        res = requests.get(
            self._url + path, params=params, headers=headers, auth=self._auth
        )
        match res.status_code:
            case 200:
                return res.json()
            case _:
                err = ApiError.model_validate(res.json())
                raise ApiException(res.status_code, err)

    def _get_data[T: ApiModel](
        self,
        cls: Type[T],
        path: str,
        kw: Optional[_ParamsDict] = None,
    ):
        params = None
        if kw is not None:
            params = self.kw_to_params(kw)
        data = self._get(path, params=params)
        return cls.model_validate(data)

    # Customers

    def get_customer(self, cid: int):
        """Returns properties of customer with given id"""
        return self._get_data(CustomerWithAllowedAction, f"/customers/{cid}")

    def get_customers(self, /, **kw: Unpack[_GetCustomersParams]):
        """Returns list of customers according to provided query and user access rights"""
        return self._get_data(CustomerList, "/customers", kw)

    def get_customer_comments(self, cid: int, /, **kw: Unpack[_GetCommentsParams]):
        """Returns list of comments on the customer according to provided query
        and user access rights"""
        return self._get_data(CommentList, f"/customers/{cid}/comments", kw=kw)

    # Departments

    def get_department_by_id(self, did: int):
        """Returns properties of department with given id"""
        return self._get_data(Department, f"/departments/{did}")

    def get_departments(self, **kw: Unpack[_GetDepartmentsParams]):
        """Returns list of departments according to provided query"""
        return self._get_data(DepartmentList, "/departments", kw=kw)

    # Rest Hooks

    def get_hooks(self):
        """Returns list of available subscriptions"""
        data = self._get("/hooks")
        return [WithDetails.model_validate(d) for d in data]

    # Info

    def get_info(self):
        """Returns actiTIME instance info and settings"""
        return self._get_data(Info, "/info")

    # Leavetime

    def get_leavetime(self, **kw: Unpack[_GetLeavetimeParams]):
        """Returns leave time according to provided query. Leave time for single date is returned entirely."""
        return self._get_data(LeaveTimeList, "/leavetime", kw=kw)

    # Leave types

    def get_leavetype_by_id(self, uid: int):
        """Returns properties of leave type with given id"""
        return self._get_data(LeaveType, f"/leaveTypes/{uid}")

    def get_leavetypes(self, **kw: Unpack[_GetLeaveTypeParams]):
        """Returns list of leave types according to provided query"""
        return self._get_data(LeaveTypeList, "/leaveTypes", kw=kw)

    # Projects

    def get_project_by_id(self, uid: int):
        """Returns properties of project with given id"""
        return self._get_data(ProjectWithAllowedActions, f"/projects/{uid}")

    def get_project_comments(self, uid: int, /, **kw: Unpack[_GetCommentsParams]):
        """Returns list of comments on the project according to provided query and user access rights"""
        return self._get_data(CommentList, f"/projects/{uid}/comments", kw=kw)

    def get_ptojects(self, /, **kw: Unpack[_GetProjectsParams]):
        """Returns list of projects according to provided query and user access rights"""
        return self._get_data(ProjectList, "/projects", kw=kw)

    # Tasks

    def get_task_by_id(self, uid: int):
        """Returns properties of task with given id"""
        return self._get_data(TaskWithAllowedActions, f"/tasks/{uid}")

    def get_task_comments(self, uid: int, **kw: Unpack[_GetCommentsParams]):
        """Returns list of comments on the task according to provided query and user access rights"""
        return self._get_data(CommentList, f"/tasks/{uid}/comments", kw=kw)

    def get_tasks(self, **kw: Unpack[_GetTasksParams]):
        """Returns list of tasks according to provided query and user access rights"""
        return self._get_data(TaskList, "/tasks", kw=kw)

    # Timetrack

    def get_single_timetrack(self, user_id: int, date: DateTime, task_id: int):
        """Returns one time-track record"""
        return self._get_data(
            TimeTrackRecord, f"/timetrack/{user_id}/{serialize_date(date)}/{task_id}"
        )

    def get_timetrack(self, **kw: Unpack[_GetTimetrackParams]):
        """Returns several time-track records according to provided query."""
        return self._get_data(TimeTrackList, "/timetrack", kw=kw)

    # Time Zone Groups

    def get_time_zone_group_by_id(self, uid: int):
        """Returns properties of time zone group with given id"""
        return self._get_data(TimeZoneGroup, f"/timeZoneGroups/{uid}")

    def get_default_time_zone_group(self):
        """Returns default time zone group"""
        return self._get_data(TimeZoneGroup, "/timeZoneGroups/default")

    def get_time_zone_groups(self, **kw: Unpack[_GetTimeZoneGroupsParams]):
        """Returns list of time zone groups according to provided query"""
        return self._get_data(TimeZoneGroupList, "/timeZoneGroups", kw=kw)

    # Types of work

    def get_type_of_work_by_id(self, uid: int):
        """Returns properties of type of work with given id"""
        return self._get_data(TypeOfWork, f"/typesOfWork/{uid}")

    def get_default_type_of_work(self):
        """Returns default type of work"""
        return self._get_data(TypeOfWork, "/typesOfWork/default")

    def get_types_of_work(self, **kw: Unpack[_GetTypesOfWorkParams]):
        """Returns list of types of work according to provided query"""
        return self._get_data(TypeOfWorkList, "/typesOfWork", kw=kw)

    # Users

    def get_users(self, **kw: Unpack[_GetUsersParams]):
        """Returns list of users according to provided query"""
        return self._get_data(UserList, "/users", kw=kw)

    def get_user_by_id(self, uid: int):
        """Returns properties of user with given id"""
        return self._get_data(UserWithAllowedActions, f"/users/{uid}")

    def get_me(self):
        """Returns properties of authorized user"""
        return self._get_data(UserWithAllowedActions, "/users/me")

    def get_user_schedule(self, uid: int, **kw: Unpack[_GetUserScheduleParams]):
        """Returns user schedule for provided dates"""
        return self._get_data(UserSchedule, f"/users/{uid}/schedule", kw=kw)

    # Workflow Statuses

    def get_workflow_status_by_id(self, uid: int):
        """Returns properties of workflow status with given id"""
        return self._get_data(
            WorkflowStatusWithAllowedActions, f"/workflowStatuses/{uid}"
        )

    def get_workflow_statuses(self, **kw: Unpack[_GetWorkflowStatusesParams]):
        """Returns list of workflow statuses according to provided query"""
        return self._get_data(WorkflowStatusList, "/workflowStatuses", kw=kw)

    @staticmethod
    def kw_to_params(d: _ParamsDict):
        _params = dict()
        for k, v in d.items():
            _k = to_camel(k)
            if v is None:
                continue
            if isinstance(v, DateTime):
                _v = serialize_date(v)
            elif isinstance(v, Sequence) and not isinstance(v, str):
                _v = ",".join([str(e) for e in v])
            elif isinstance(v, Enum):
                _v = v.value
            else:
                _v = v
            _params[_k] = _v
        return _params
