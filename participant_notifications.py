"""ChurchManager planning and delivery rules for worship participant email."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import JSForm

from bulletin_orders import portable_connection


@dataclass(frozen=True)
class NotificationServiceContext:
    service_id: int
    church_id: int
    church_name: str
    service_datetime: datetime
    liturgical_date: str


@dataclass(frozen=True)
class NotificationRecipient:
    participant_id: int
    name: str
    email: str
    positions: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class NotificationPlan:
    service: NotificationServiceContext
    recipients: tuple[NotificationRecipient, ...]
    subject: str
    body: str
    attachment: Path | None = None

    @property
    def sendable_addresses(self):
        return JSForm.unique_recipients(
            recipient.email for recipient in self.recipients if recipient.status == "Ready"
        )


class ParticipantNotificationRepository:
    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def one(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchone()
        finally:
            cursor.close()

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def service_context(self, service_id):
        row = self.one(
            "SELECT s.ID,s.ChurchID,c.Church,s.DateTime,COALESCE(s.LiturgicalDate,'') "
            "FROM tblService s JOIN tblChurch c ON c.ID=s.ChurchID WHERE s.ID=?",
            (service_id,),
        )
        if not row:
            raise ValueError("The selected worship service is unavailable.")
        return NotificationServiceContext(*row)

    def assigned_participants(self, service_id):
        return self.all(
            "SELECT p.ID,COALESCE(NULLIF(p.DisplayName,''),p.Name),COALESCE(p.eMail,''),"
            "wr.Name FROM tblServiceRole sr JOIN tblParticipant p ON p.ID=sr.ParticipantID "
            "JOIN tblWorshipRole wr ON wr.ID=sr.WorshipRoleID "
            "WHERE sr.ServiceID=? AND sr.AssignmentStatus<>'DECLINED' AND p.Active=1 "
            "ORDER BY p.ID,wr.DisplayOrder,wr.Name",
            (service_id,),
        )


class ParticipantNotificationService:
    DEFAULT_BODY = (
        "You are scheduled to serve in worship. Please review the attached "
        "Worship Planning report for details."
    )

    def __init__(self, repository, authorization, report_service, mail_service=None):
        self.repository = repository
        self.authorization = authorization
        self.reports = report_service
        self.mail = mail_service

    @staticmethod
    def _subject(context):
        service_date = context.service_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        service_date = service_date.replace(" 0", " ")
        return "Worship Planning - {} - {}".format(service_date, context.church_name)

    def prepare(self, service_id):
        self.authorization.require("worship.manage", operation="Review participant notification")
        context = self.repository.service_context(service_id)
        grouped = {}
        for participant_id, name, email, position in self.repository.assigned_participants(service_id):
            item = grouped.setdefault(participant_id, [name, email.strip(), []])
            if position not in item[2]:
                item[2].append(position)
        recipients = []
        seen = set()
        for participant_id, (name, email, positions) in grouped.items():
            normalized = JSForm.normalized_email(email)
            if not email:
                status = "Missing email"
            elif not JSForm.valid_email(email):
                status = "Invalid email"
            elif normalized in seen:
                status = "Shared address"
            else:
                status = "Ready"
                seen.add(normalized)
            recipients.append(NotificationRecipient(
                participant_id, name, email, tuple(positions), status,
            ))
        return NotificationPlan(
            context, tuple(recipients), self._subject(context), self.DEFAULT_BODY,
        )

    def generate_attachment(self, plan, output=None):
        self.authorization.require("reports.worship.run", operation="Generate participant attachment")
        attachment = self.reports.render_worship_planning(
            plan.service.church_id, plan.service.service_id,
            self.repository.connection, open_output=False, output=output,
        )
        return NotificationPlan(
            plan.service, plan.recipients, plan.subject, plan.body, Path(attachment),
        )

    def send(self, plan, subject=None, body=None):
        self.authorization.require("worship.manage", operation="Send participant notification")
        if self.mail is None:
            raise RuntimeError("Mail delivery is not configured.")
        if plan.attachment is None or not plan.attachment.is_file():
            raise ValueError("Generate the current Worship Planning report before sending.")
        addresses = plan.sendable_addresses
        if not addresses:
            raise ValueError("There are no valid participant email addresses to notify.")
        return self.mail.send(
            addresses,
            JSForm.MailMessage(subject or plan.subject, body or plan.body, (plan.attachment,)),
        )
