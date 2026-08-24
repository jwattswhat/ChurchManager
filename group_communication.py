"""Privacy-safe review and delivery rules for congregational Group email."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json

import JSForm

from bulletin_orders import portable_connection


@dataclass(frozen=True)
class GroupRecipient:
    """One reviewed Group member without exposing an unlisted address."""

    person_id: int
    name: str
    roles: tuple[str, ...]
    email: str
    status: str


@dataclass(frozen=True)
class GroupCommunicationPlan:
    """Immutable recipient review snapshot used for final confirmation."""

    group_id: int
    group_name: str
    effective_date: date
    recipients: tuple[GroupRecipient, ...]
    subject: str
    body: str
    fingerprint: str

    @property
    def sendable(self):
        return tuple(item for item in self.recipients if item.status == "Ready")


class GroupCommunicationRepository:
    """Read effective membership and safe contact facts from MariaDB."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def all(self, sql, values=()):
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, values)
            return cursor.fetchall()
        finally:
            cursor.close()

    def group(self, group_id):
        rows = self.all(
            "SELECT ID,Name,PrivacyClass,CommunicationEnabled FROM tblGroup WHERE ID=?",
            (group_id,),
        )
        return rows[0] if rows else None

    def members(self, group_id, effective_date):
        return self.all(
            "SELECT m.PersonID,TRIM(CONCAT_WS(' ',p.FirstName,p.LastName)),"
            "COALESCE(GROUP_CONCAT(DISTINCT r.Label ORDER BY r.DisplayOrder,r.Label SEPARATOR ', '),'') "
            "FROM tblGroupMembership m JOIN tblPerson p ON p.ID=m.PersonID "
            "LEFT JOIN tblGroupMembershipRole mr ON mr.GroupMembershipID=m.ID "
            "AND mr.StartDate<=? AND (mr.EndDate IS NULL OR mr.EndDate>=?) "
            "LEFT JOIN tblGroupRole r ON r.ID=mr.GroupRoleID "
            "WHERE m.GroupID=? AND m.StartDate<=? AND (m.EndDate IS NULL OR m.EndDate>=?) "
            "GROUP BY m.PersonID,p.FirstName,p.LastName ORDER BY p.LastName,p.FirstName,p.ID",
            (effective_date, effective_date, group_id, effective_date, effective_date),
        )

    def email_facts(self, person_id):
        return self.all(
            "SELECT Contact,COALESCE(Unlisted,0) FROM tblPersonContact "
            "WHERE PersonID=? AND LOWER(TRIM(Type)) IN ('email','e-mail') ORDER BY ID",
            (person_id,),
        )

    def audit(self, user_id, action, group_id, summary):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO tblSecurityAuditEvent (UserID,Action,EntityType,EntityID,AfterJSON) "
                "VALUES (?,?,?,?,?)",
                (user_id, action, "Group", str(group_id), json.dumps(summary, sort_keys=True)),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()


class GroupCommunicationService:
    """Prepare, revalidate, and explicitly send Group email."""

    DEFAULT_BODY = "This message is for the current members of the selected congregational Group."

    def __init__(self, repository, session, authorization, mail_service=None):
        self.repository = repository
        self.session = session
        self.authorization = authorization
        self.mail = mail_service

    def prepare(self, group_id, effective_date=None):
        self.authorization.require("groups.communication.prepare", "prepare Group communication")
        effective_date = effective_date or date.today()
        group = self.repository.group(int(group_id))
        if not group:
            raise ValueError("The selected Group is unavailable.")
        if group[2] == "RESTRICTED":
            self.authorization.require("groups.view_restricted", "prepare a restricted Group communication")
        if not group[3]:
            raise ValueError("Communication is not enabled for this Group.")
        recipients = []
        seen = set()
        for person_id, name, role_text in self.repository.members(group_id, effective_date):
            facts = self.repository.email_facts(person_id)
            listed = [str(value).strip() for value, unlisted in facts if value and not unlisted]
            has_unlisted = any(bool(unlisted) for _value, unlisted in facts)
            email = listed[0] if listed else ""
            normalized = JSForm.normalized_email(email)
            if not email:
                status = "Unlisted email" if has_unlisted else "Missing email"
            elif not JSForm.valid_email(email):
                status = "Invalid email"
            elif normalized in seen:
                status = "Shared address"
            else:
                status = "Ready"
                seen.add(normalized)
            roles = tuple(part.strip() for part in role_text.split(",") if part.strip())
            recipients.append(GroupRecipient(person_id, name, roles, email, status))
        subject = f"{group[1]} - Group Message"
        fingerprint = self._fingerprint(group_id, effective_date, recipients)
        plan = GroupCommunicationPlan(
            group_id, group[1], effective_date, tuple(recipients), subject,
            self.DEFAULT_BODY, fingerprint,
        )
        self.repository.audit(self.session.user_id, "GROUP_COMMUNICATION_REVIEWED", group_id, {
            "effective_date": effective_date.isoformat(), "recipient_count": len(plan.sendable),
            "excluded_count": len(recipients) - len(plan.sendable),
        })
        return plan

    def send(self, plan, subject, body):
        self.authorization.require("groups.communication.send", "send Group communication")
        current = self.prepare(plan.group_id, plan.effective_date)
        if current.fingerprint != plan.fingerprint:
            raise ValueError("Group membership or contact information changed. Review the recipients again.")
        if self.mail is None:
            raise RuntimeError("Mail delivery is not configured.")
        if not current.sendable:
            raise ValueError("There are no eligible Group email recipients.")
        subject = str(subject or "").strip()
        body = str(body or "").strip()
        if not subject or not body:
            raise ValueError("A subject and message are required.")
        results = self.mail.send(
            tuple(item.email for item in current.sendable), JSForm.MailMessage(subject, body),
        )
        succeeded = sum(bool(item.succeeded) for item in results)
        self.repository.audit(self.session.user_id, "GROUP_COMMUNICATION_SENT", plan.group_id, {
            "recipient_count": len(current.sendable), "succeeded_count": succeeded,
            "failed_count": len(results) - succeeded,
        })
        return results

    @staticmethod
    def _fingerprint(group_id, effective_date, recipients):
        facts = [
            (item.person_id, JSForm.normalized_email(item.email), item.status)
            for item in recipients
        ]
        raw = json.dumps([group_id, effective_date.isoformat(), facts], separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
