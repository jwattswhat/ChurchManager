"""Participant notification support for normalized worship assignments."""

from dataclasses import dataclass

import JSForm


@dataclass(frozen=True)
class Participant:
    id: int
    name: str
    email: str | None


class WorshipRepository:
    def __init__(self, connection):
        self.connection = connection

    def assigned_participants(self, service_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT DISTINCT p.ID,COALESCE(NULLIF(p.DisplayName,''),p.Name),p.eMail "
                "FROM tblServiceRole sr JOIN tblParticipant p ON p.ID=sr.ParticipantID "
                "WHERE sr.ServiceID=%s AND sr.AssignmentStatus<>'DECLINED' AND p.Active=1 "
                "ORDER BY p.ID", (service_id,),
            )
            return [Participant(*row) for row in cursor.fetchall()]
        finally:
            cursor.close()


class NotificationService:
    def __init__(self, repository, smtp, attachment):
        self.repository = repository
        self.smtp = smtp
        self.attachment = attachment

    def notify(self, service_id):
        participants = [
            participant for participant in self.repository.assigned_participants(service_id)
            if participant.email
        ]
        recipients = [participant.email for participant in participants]
        names = [participant.name for participant in participants]
        if not recipients:
            return 0
        message = [
            "You have been scheduled to serve in worship this coming week. "
            "Please see the attached Worship Service Planner for details."
        ]
        self.smtp.sendeMail(recipients, names, "Worship Planning", message, self.attachment)
        return len(recipients)


def notifyviaeMail(service_id, dbconn):
    """Notify active, assigned participants who have an email address."""
    attachment = JSForm.CONFIG.get_Config_Value("Location", "Report") + "CMWS01.pdf"
    return NotificationService(
        WorshipRepository(dbconn), JSForm.clsSMTP(), attachment
    ).notify(service_id)
