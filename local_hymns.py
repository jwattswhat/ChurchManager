"""Permanent identifier allocation and retirement for local hymn metadata."""

from __future__ import annotations

from bulletin_orders import portable_connection


LOCAL_HYMNAL_ID = 1
LOCAL_HYMN_ID_START = 5001
LOCAL_HYMN_ID_END = 9999


class LocalHymnCapacityError(RuntimeError):
    """Raised when the congregation's permanent local hymn block is exhausted."""


class LocalHymnIDAllocator:
    """Allocate the next never-used ID from the permanent local block."""

    def __init__(self, connection):
        self.connection = portable_connection(connection)

    def allocate(self):
        """Reserve and return ``(HymnID, EntrySlot)`` in one transaction."""
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "SELECT HymnID FROM tblLocalHymnIDAllocation "
                "ORDER BY HymnID DESC LIMIT 1 FOR UPDATE"
            )
            row = cursor.fetchone()
            candidate = (row[0] + 1) if row else LOCAL_HYMN_ID_START
            if candidate > LOCAL_HYMN_ID_END:
                raise LocalHymnCapacityError(
                    "The local hymn catalog has reached its permanent ID capacity."
                )
            slot = candidate - 5000
            cursor.execute(
                "INSERT INTO tblLocalHymnIDAllocation (HymnID,EntrySlot) VALUES (?,?)",
                (candidate, slot),
            )
            self.connection.commit()
            return candidate, slot
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def retire(self, hymn_id):
        """Retire local metadata without deleting or reusing its permanent ID."""
        hymn_id = int(hymn_id)
        if not LOCAL_HYMN_ID_START <= hymn_id <= LOCAL_HYMN_ID_END:
            raise ValueError("Only congregation-owned hymns can be retired here.")
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "UPDATE tblHymn SET IsActive=0 WHERE ID=? AND HymnalID=?",
                (hymn_id, LOCAL_HYMNAL_ID),
            )
            cursor.execute(
                "UPDATE tblLocalHymnIDAllocation SET RetiredAt=COALESCE(RetiredAt,CURRENT_TIMESTAMP) "
                "WHERE HymnID=?",
                (hymn_id,),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
