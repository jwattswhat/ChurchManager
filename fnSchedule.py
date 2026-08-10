"""Worship scheduling services with a compatibility API for ChurchManager."""

from dataclasses import dataclass
from datetime import datetime

import JSForm


def strtolist(value):
    """Decode the list format stored by the existing JSForm controls."""
    if value is None:
        return None
    if "[" not in value:
        return value
    return value.replace("[", "").replace("]", "").replace("\n", "").split("\r")


@dataclass(frozen=True)
class Service:
    id: int
    starts_at: object
    propers_id: int


@dataclass(frozen=True)
class Participant:
    id: int
    name: str
    roles: object
    schedules: object
    email: str | None


@dataclass(frozen=True)
class ScheduleRule:
    id: int
    time: str
    days: object
    months: object
    seasons: object


class WorshipRepository:
    """Keep database tuples and SQL details out of scheduling decisions."""

    def __init__(self, connection):
        self.connection = connection

    def _one(self, sql, params):
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

    def _all(self, sql, params=()):
        cursor = self.connection.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def has_assignments(self, service_id):
        return bool(self._one(
            "SELECT 1 FROM tblServiceRole WHERE ServiceID=%s LIMIT 1", (service_id,)
        ))

    def service(self, service_id):
        row = self._one("SELECT * FROM tblService WHERE ID=%s", (service_id,))
        return None if row is None else Service(row[0], row[2], row[4])

    def season(self, propers_id):
        row = self._one("SELECT * FROM tblPropers WHERE ID=%s", (propers_id,))
        return None if row is None else row[3]

    def participants(self):
        return [
            Participant(row[0], row[2], strtolist(row[3]), strtolist(row[4]), row[6])
            for row in self._all("SELECT * FROM tblParticipant ORDER BY ID")
        ]

    def schedule_rules(self):
        rules = []
        for row in self._all("SELECT * FROM tblSchedule ORDER BY ID"):
            rule_time = (datetime(2022, 1, 1) + row[2]).strftime("%I:%M %p")
            rules.append(ScheduleRule(
                row[0], rule_time, strtolist(row[3]), strtolist(row[4]),
                strtolist(row[5]),
            ))
        return rules

    def add_assignment(self, service_id, participant_id, role):
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO tblServiceRole (ServiceID, ParticipantID, Role) "
            "VALUES (%s, %s, %s)",
            (service_id, participant_id, role),
        )

    def assigned_participants(self, service_id):
        rows = self._all(
            "SELECT DISTINCT p.ID, p.Name, p.Roles, p.Schedule, p.eMail "
            "FROM tblServiceRole sr JOIN tblParticipant p ON p.ID=sr.ParticipantID "
            "WHERE sr.ServiceID=%s ORDER BY p.ID", (service_id,),
        )
        return [Participant(row[0], row[1], strtolist(row[2]), strtolist(row[3]), row[4]) for row in rows]


def _contains_or_unrestricted(options, value):
    return not options or value in options


def rule_matches(rule, starts_at, season):
    return (
        starts_at.strftime("%I:%M %p") == rule.time
        and _contains_or_unrestricted(rule.days, starts_at.strftime("%A"))
        and _contains_or_unrestricted(rule.months, starts_at.strftime("%B"))
        and _contains_or_unrestricted(rule.seasons, season)
    )


class SchedulingService:
    def __init__(self, repository):
        self.repository = repository

    def schedule(self, service_id):
        if self.repository.has_assignments(service_id):
            return 0
        service = self.repository.service(service_id)
        if service is None:
            raise ValueError("Service {} was not found".format(service_id))
        season = self.repository.season(service.propers_id)
        rules = {str(rule.id): rule for rule in self.repository.schedule_rules()}
        created = 0
        try:
            for participant in self.repository.participants():
                for schedule_id in participant.schedules or []:
                    rule = rules.get(str(schedule_id))
                    if rule and rule_matches(rule, service.starts_at, season):
                        for role in participant.roles or []:
                            self.repository.add_assignment(service.id, participant.id, role)
                            created += 1
            self.repository.connection.commit()
        except Exception:
            self.repository.connection.rollback()
            raise
        return created


class NotificationService:
    def __init__(self, repository, smtp, attachment):
        self.repository = repository
        self.smtp = smtp
        self.attachment = attachment

    def notify(self, service_id):
        participants = [p for p in self.repository.assigned_participants(service_id) if p.email]
        recipients = [p.email for p in participants]
        names = [p.name for p in participants]
        if not recipients:
            return 0
        message = [
            "Dear Member of Life in Christ\n\nYou have been scheduled to serve in "
            "Worship this coming week. Please see the attached file for more "
            "information.\n\nPastor Watt"
        ]
        self.smtp.sendeMail(recipients, names, "Worship Planning", message, self.attachment)
        return len(recipients)


def ScheduleParticipants(ServiceID, dbconn):
    """Compatibility entry point retained for existing forms."""
    return SchedulingService(WorshipRepository(dbconn)).schedule(ServiceID)


def notifyviaeMail(ServiceID, dbconn):
    """Compatibility entry point retained for existing forms."""
    attachment = JSForm.CONFIG.get_Config_Value("Location", "Report") + "CMWP01.pdf"
    return NotificationService(
        WorshipRepository(dbconn), JSForm.clsSMTP(), attachment
    ).notify(ServiceID)
