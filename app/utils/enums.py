from enum import Enum


class ApplicationStatus(str, Enum):
    SENT = "sent"
    REVIEWED = "reviewed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class CompanyRole(str, Enum):
    OWNER = "owner"
    RECRUITER = "recruiter"
    HR_MANAGER = "hr_manager"


class CompanyPermission(str, Enum):
    MANAGE_JOBS = "manage_jobs"
    CREATE_JOBS = "create_jobs"
    EDIT_JOBS = "edit_jobs"
    DELETE_JOBS = "delete_jobs"
    VIEW_APPLICATIONS = "view_applications"
    MANAGE_APPLICATIONS = "manage_applications"
    INVITE_MEMBERS = "invite_members"
    MANAGE_MEMBERS = "manage_members"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    REMOTE = "remote"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    HYBRID = "hybrid"


class EducationLevel(str, Enum):
    NO_EDUCATION = "no_education"
    HIGH_SCHOOL = "high_school"
    VOCATIONAL = "vocational"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    CERTIFICATION = "certification"


class SkillLevel(str, Enum):
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class NotificationType(str, Enum):
    MESSAGE = "message"
    APPLICATION = "application"
    JOB_UPDATE = "job_update"
    SYSTEM = "system"


class UserRole(str, Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
