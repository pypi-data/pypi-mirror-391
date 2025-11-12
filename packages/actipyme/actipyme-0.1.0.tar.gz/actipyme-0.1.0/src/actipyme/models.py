import enum
from typing import Literal, Optional, Sequence, Any, assert_type
import datetime
import pendulum
from typing_extensions import Annotated
from pydantic import BaseModel, ConfigDict, PlainValidator, PlainSerializer, Field
from pydantic.alias_generators import to_camel


_TZ = pendulum.timezone("Europe/Rome")
_DATE_FMT = "%Y-%m-%d"


def validate_date(val: Any):
    if val is None:
        return None
    dt = pendulum.DateTime.strptime(val, _DATE_FMT).astimezone(_TZ)
    return dt


def serialize_date(dt: pendulum.DateTime | None):
    if dt is None:
        return None
    return dt.strftime(_DATE_FMT)


Date = Annotated[
    pendulum.DateTime,
    PlainValidator(validate_date),
    PlainSerializer(serialize_date),
]


def validate_datetime(val: Any):
    if val is None:
        return None

    if isinstance(val, float) or isinstance(val, int):
        return pendulum.DateTime.fromtimestamp(1e-3 * val, tz=_TZ)

    raise ValueError("Invalid date type")


def serialize_datetime(dt: pendulum.DateTime | None):
    if dt is None:
        return None
    return dt.timestamp()


DateTime = Annotated[
    pendulum.DateTime,
    PlainSerializer(serialize_datetime),
    PlainValidator(validate_datetime),
]


def validate_minutes_delta(td: Any):
    if td is None:
        return None

    if isinstance(td, float) or isinstance(td, int):
        return datetime.timedelta(minutes=td)

    raise ValueError("Invalid data type")


def serialize_minutes_delta(td: datetime.timedelta):
    return td.seconds // 60


MinutesDelta = Annotated[
    datetime.timedelta,
    PlainValidator(validate_minutes_delta),
    PlainSerializer(serialize_minutes_delta),
]


def validate_id_list(l: Any):
    if not isinstance(l, str):
        raise ValueError("Value must be a str")

    return [int(e) for e in l.split(",")]


def serialize_id_list(l: Sequence[int]):
    return ",".join([str(e) for e in l])


IdList = Annotated[
    Sequence[int], PlainValidator(validate_id_list), PlainSerializer(serialize_id_list)
]


class ApiModel(BaseModel):
    """Base class for an API model"""

    model_config = ConfigDict(
        use_enum_values=True,
        alias_generator=to_camel,
    )


class ApiError(ApiModel):
    """Model of an API error"""

    key: str
    """Unique error key which defines specific case"""
    message: str
    """Human-readable error message"""
    stack_trace: Optional[str] = None
    """Stack-trace info for developers"""
    fields: Optional[str] = None
    """Field or fields (if any) related to error"""


class ItemList[A: ApiModel](ApiModel):
    """Base list of items"""

    items: Sequence[A]
    """List of items matching criteria"""
    offset: int
    """Offset position"""
    limit: int
    """Max number of returned items"""


class AllowedAction(ApiModel):

    can_modify: bool
    can_delete: bool


class WithAllowedAction(ApiModel):

    allowed_actions: AllowedAction


class WithIdModel(ApiModel):
    uid: int = Field(alias="id")
    """Unique object identifier"""


class Customer(WithIdModel):

    name: str
    """Customer name"""
    archived: bool
    """True if the customer is archived"""
    created: DateTime
    """Creation date and time"""
    url: str
    """URL of the customer"""
    description: Optional[str] = None
    """Customer description"""


class CustomerWithAllowedAction(Customer, WithAllowedAction):
    pass


class CustomerList(ItemList[CustomerWithAllowedAction]):
    pass


class User(WithIdModel):
    department_id: int
    """Unique identifier of user department"""
    time_zone_group_id: int
    """Unique identifier of user time zone group"""
    hired: Optional[Date] = None
    """User's hire date"""
    release_date: Optional[Date] = None
    """User's release date"""
    email: Optional[str] = None
    """User email"""
    full_name: str
    """Fullname: first_name + middle_name + last_name"""
    username: Optional[str] = None
    """Unique username"""
    active: bool
    """True if the user is active"""
    first_name: str
    """User's first name"""
    middle_name: str
    """User's middle name"""
    last_name: str
    """User's last name"""


class UserWithAllowedActions(User, WithAllowedAction):
    pass


class UserList(ItemList[UserWithAllowedActions]):
    departments: Optional[dict[int, "Department"]] = None
    """Map of user department id to department object. Contains departments referenced in users referenced in data list"""
    time_zone_groups: Optional[dict[int, "TimeZoneGroup"]] = None
    """Map of user time zone id to user time zone object. Contains user time zone referenced in users referenced in data list"""


class UserSchedule(ApiModel):

    date_from: Date
    """Date the schedule returned from, inclusive."""
    date_to: Date
    """Date the schedule returned to, inclusive."""
    schedule: Sequence[MinutesDelta]
    """Array of workday durations, where the first element corresponds to 'dateFrom' and the last to 'dateTo'."""


class Comment(WithIdModel):
    user_id: int
    """Unique user identifier"""
    created: DateTime
    """Creation date and time"""
    updated: DateTime
    """Date and time of last editing"""
    updating_user_id: int
    """Unique identifier of the user who made the last editing"""
    text: str
    """Text of the comment"""


class CommentList(ItemList[Comment]):
    users: Optional[dict[int, User]] = None
    """Map of userId to user"""


class Department(WithIdModel):
    name: str
    """Department name"""
    default: bool
    """True if this is the default department"""


class DepartmentList(ItemList[Department]):
    pass


class EntityFilterBean(ApiModel):
    customer_ids: IdList
    project_ids: IdList
    task_ids: IdList
    user_ids: IdList
    department_ids: IdList


class Event(str, enum.Enum):
    create = "create"
    update = "update"
    move = "move"
    delete = "delete"
    task = "task"
    task_create = "task.create"
    task_update = "task.update"
    task_move = "task.move"
    task_delete = "task.delete"
    project = "project"
    project_create = "project.create"
    project_update = "project.update"
    project_move = "project.move"
    project_delete = "project.delete"
    customer = "customer"
    customer_create = "customer.create"
    customer_update = "customer.update"
    customer_delete = "customer.delete"
    department = "department"
    department_create = "department.create"
    department_update = "department.update"
    department_delete = "department.delete"
    user = "user"
    user_create = "user.create"
    user_update = "user.update"
    user_delete = "user.delete"
    time_zone_group = "timeZoneGroup"
    time_zone_group_create = "timeZoneGroup.create"
    time_zone_group_update = "timeZoneGroup.update"
    time_zone_group_delete = "timeZoneGroup.delete"
    leave_time = "leaveTime"
    leave_time_update = "leaveTime.update"
    timetrack = "timetrack"
    timetrack_update = "timetrack.update"
    timetrack_approval_status = "timetrackApprovalStatus"
    timetrack_approval_status_update = "timetrackApprovalStatus.update"


class WithDetails(WithIdModel):
    event: Event
    """Which events shall be sent to specified URL"""
    entity_filter: EntityFilterBean = Field(alias="filter")
    """"""
    enabled: bool
    """Is this subscription active or not"""
    lastHttpStatus: int
    """HTTP Status of last call to target url"""
    lastHttpError: str
    """HTTP error of last call to target url"""
    lastHttpCall: DateTime
    """Date of last call to target url"""
    user_id: int
    """Id of creator"""
    target_url: str
    """URL which will be used to send events"""


class Company(ApiModel):
    logo_uri: str
    """Url of logo used in web interface"""
    name: str
    """Company name"""


class CustomName(ApiModel):
    singular: str
    plural: str


class CustomNames(ApiModel):
    first_level: CustomName
    second_level: CustomName
    third_level: CustomName
    department: CustomName


class TimeFormat(str, enum.Enum):
    minutes = "minutes"
    hours = "hours"


class ClockFormat(str, enum.Enum):
    clock_format_12 = "clock_format_12"
    clock_format_24 = "clock_format_24"


class Format(ApiModel):
    currency: str
    """Which currency character is set in system"""
    decimal_separator: str
    """Which decimal separator is set in system"""
    time_format: TimeFormat
    """Which time format is preferred in reports.
    If 'minutes', then HH:MM (i.e. 03:45); if 'hours', then HH. (i.e. 03.75)"""
    clock_format: ClockFormat
    """Which clock format is preferred.
    If '12-hour clock', then (1-12):MM AM/PM (i.e. 03:45 AM); if 
    '24-hors clock', then (1-24):MM (i.e. 15:45)"""
    day_of_week_start: int
    """On which day week starts. 
    Day number corresponds Javascript, i.e. 0 = sunday, 1 = monday, 6 = saturday"""


class Features(ApiModel):
    overtime_registration: bool
    """Overtime Registration feature (is time exceeding the work day duration 
    reported as overtime)"""
    departments: bool
    """Departments feature (are users grouped by departments)"""
    time_zone_groups: bool
    """Time Zone Groups feature (are users grouped by time zone groups)"""
    task_estimates: bool
    """Task Estimates feature (do tasks contain estimated time)"""
    task_workflow: bool
    """Task Workflow feature (is there are many workflow statuses or tasks have 
    only simple Open/Completed statuses)"""
    work_assignments: bool
    """Work Assignments features (is it possible to assign specific users to 
    specific tasks)"""
    types_of_work: bool
    """Types of Work feature (do tasks have assigned types of works or not)"""
    leavetime_registration: bool
    """Leave Time Tracking feature (is leave time also registered in time-sheet 
    or not)"""


class Urls(ApiModel):
    actitime: str = Field(alias="actiTime")
    """Home of actiTIME web application"""
    actiplans: Optional[str] = Field(default=None, alias="actiPlans")
    """Home of actiPLANS web application"""
    api: str
    """Base uri of API"""
    api_documentation: str
    """Uri of API documentation"""


class Limits(ApiModel):
    max_batch_size: int
    """How much requests could be sent via single batch request"""
    max_query_limit: int
    """How much results could be returned in single listing request"""


class Info(ApiModel):

    company: Company
    custom_names: CustomNames
    local_format: Format = Field(alias="format")
    features: Features
    """Describes which features are enabled in actiTIME Web UI. Note that API 
    endpoint is available even if corresponding feature is turned off"""
    urls: Urls
    limits: Limits
    server_uuid: str = Field(alias="serverUUID")


class TimeZoneGroup(WithIdModel):
    """Represents single location with associated time zone where users could
    be assigned"""

    name: str
    """Human-readable name of associated location"""
    time_zone_id: str
    """Time Zone Id in format of IANA Time Zone Database"""
    default: bool
    """True if this is default time zone group"""


class LeaveTypeBalance(str, enum.Enum):
    none = "None"
    sick = "Sick"
    pto = "PTO"


class LeaveType(WithIdModel):
    """Represents leave type object"""

    name: str
    """Name of leave type"""
    balance: LeaveTypeBalance
    """Which balance is affected by leave of this type"""
    archived: bool
    """True if this leave type is archived"""


class LeaveTimeRecord(ApiModel):
    """Contains time leaved and type of leave for specific user"""

    user_id: int
    """Unique user identifier"""
    day_offset: int
    """Offset for 'dateFrom'"""
    date: Date
    """Leave date"""
    leave_type_id: int
    """Leave type identifier"""
    leave_time: MinutesDelta
    """Duration of leave time"""


class LeaveTimeList(ApiModel):
    users: Optional[dict[int, User]] = None
    """Map of user id to user. Contains users referenced in data list."""
    departments: Optional[dict[int, Department]] = None
    """Map of user department id to department object. 
    Contains departments referenced in users referenced in data list."""
    time_zone_groups: Optional[dict[int, TimeZoneGroup]] = None
    date_from: Date
    """Start date of returned data"""
    date_to: Date
    """End date of returned data"""
    next_date_from: Optional[Date] = None
    """If not null, then only partial results were included to satisfy 
    'stopAfter' parameter - till date specified in 'dateTo'. To request more 
    you need to repeat your request from date specified in 'nextDateFrom' field.
    """
    leave_types: Optional[dict[int, LeaveType]] = None
    """Map of id to leave type. Contains leave types referenced in data list"""
    data: Sequence[LeaveTimeRecord]
    """List of user leave time records"""


class LeaveTypeList(ItemList[LeaveType]):
    pass


class Project(WithIdModel):

    customer_id: int
    name: str
    archived: bool
    created: DateTime
    url: str
    customer_name: str
    description: str | None = None


class ProjectWithAllowedActions(Project, WithAllowedAction):
    pass


class ProjectList(ItemList[ProjectWithAllowedActions]):

    customers: Optional[dict[int, Customer]] = None


class TypeOfWork(WithIdModel):
    name: str
    rate: Optional[float]
    archived: bool
    billable: bool
    default: bool


class WorkflowTypeEnum(str, enum.Enum):
    open = "open"
    completed = "completed"


class WorkflowStatus(WithIdModel):
    name: str
    type_: WorkflowTypeEnum = Field(alias="type")


class WorkflowStatusWithAllowedActions(WorkflowStatus, AllowedAction):
    pass


class WorkflowStatusList(ItemList[WorkflowStatus]):
    pass


class TaskStatus(str, enum.Enum):

    open_ = "open"
    completed = "completed"


class Task(WithIdModel):

    name: str
    description: Optional[str] = None
    created: DateTime
    status: TaskStatus
    workflow_status_id: int
    type_of_work_id: int
    url: str
    project_name: str
    customer_name: str
    workflow_status_name: str
    type_of_work_name: str
    deadline: Optional[DateTime] = None
    estimated_time: Optional[MinutesDelta] = None
    customer_id: int
    project_id: int


class TaskWithAllowedActions(Task, WithAllowedAction):
    pass


class TaskList(ItemList[TaskWithAllowedActions]):

    customers: Optional[dict[int, Customer]] = None
    projects: Optional[dict[int, Project]] = None
    types_of_work: Optional[dict[int, TypeOfWork]] = None
    workflow_statuses: Optional[dict[int, WorkflowStatus]] = None


class TimeTrackRecord(ApiModel):
    """Contains time tracked for specific task and comment"""

    task_id: int
    """Identifier of task the time is tracked for"""
    time: MinutesDelta
    """Tracked time"""
    comment: Optional[str] = None
    """Optional comment for time-track record"""


class UserDayTTDataWithDayOffset(ApiModel):
    """Contains tracked time for specified user and date. Date is defined as offset from 'dateFrom' field of wrapping object"""

    user_id: int
    """Identifier of user that tracked time"""
    records: list[TimeTrackRecord]
    """List of time-track records for day"""
    approved: Optional[bool] = None
    """Approval status of the day"""
    day_offset: int
    """Offset in days from 'dateFrom' field of wrapping object"""
    date: Date
    """Time track date"""


class TimeTrackList(ApiModel):
    """Result of time track request"""

    users: Optional[dict[int, User]] = None
    """Map of user id to user object. Contains users referenced in data list"""
    departments: Optional[dict[int, Department]] = None
    """Map of user department id to department object. Contains departments referenced in users referenced in data list"""
    time_zone_group: Optional[dict[int, TimeZoneGroup]] = None
    """Map of user time zone id to user time zone object. Contains user time zone referenced in users referenced in data list"""
    date_from: Date
    """Start date of returned data"""
    date_to: Date
    """End date of returned data. Note that this one may be smaller than requested in parameters"""
    next_date_from: Optional[Date] = None
    """If not null, then only partial results were included to satisfy 
    'stopAfter' parameter - till date specified in 'dateTo'. To request more 
    you need to repeat your request from date specified in 'nextDateFrom' 
    field."""
    customers: Optional[dict[int, Customer]] = None
    """Map of customer id to customer object. Contains customers referenced in data list"""
    projects: Optional[dict[int, Project]] = None
    """Map of project id to project object. Contains projects referenced in data list"""
    tasks: Optional[dict[int, Task]] = None
    """Map of task id to task object. Contains tasks referenced in data list"""
    types_of_work: Optional[dict[int, TypeOfWork]] = None
    """Map of type of work id to type of work object. Contains types of work referenced in tasks referenced in data list"""
    workflow_statuses: Optional[dict[int, WorkflowStatus]] = None
    """Map of workflow status id to workflow status object. Contains workflow status objects referenced in tasks referenced in data list"""
    data: list[UserDayTTDataWithDayOffset]
    """List of time track records per user per day"""


class TimeZoneGroupList(ItemList[TimeZoneGroup]):
    pass


class TypeOfWorkList(ItemList[TypeOfWork]):
    pass
