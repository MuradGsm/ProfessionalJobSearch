


#     def total_members_count(self, session) -> int:
#         """Count of all active members including owner using SQL"""
#         result = session.execute(select(func.count(CompanyMember.id)
#         ).where(CompanyMember.company_id == self.id, CompanyMember.is_active == True)).scalar()
#         return (result or 0) + 1


#  @property
#     def active_jobs_count(self, session) -> int:
#         """Count of active non-expired jobs using SQL"""
#         from app.models.jobs_model import Job
#         result = session.execute(
#             select(func.count(Job.id))
#             .where(Job.company_id == self.id, Job.is_active == True, Job.expires_at > func.now())
#         ).scalar()
#         return result or 0
    
#     @property
#     def pending_invitations_count(self, session) -> int:
#         """Count of pending invitations using SQL"""
#         result = session.execute(
#             select(func.count(Invitations.id))
#             .where(Invitations.company_id == self.id, Invitations.is_used == False, Invitations.expires_at > func.now())
#         ).scalar()
#         return result or 0
    