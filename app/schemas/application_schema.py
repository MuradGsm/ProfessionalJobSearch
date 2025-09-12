from pydantic import BaseModel
from app.schemas.notification_schema import NotificationSchema
from app.utils.enums import ApplicationStatus


class ApplicationBase(BaseModel):
    # ИСПРАВЛЕНО: ApplicationStatus вместо ApplicationStatusEnum
    status: ApplicationStatus = ApplicationStatus.SENT
    job_id: int


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class ApplicationWithNotificationResponse(BaseModel):
    application: ApplicationResponse
    notification: NotificationSchema

    class Config:
        from_attributes = True
        
