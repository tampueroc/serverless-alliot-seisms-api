import datetime
import time
from typing import Optional
from pydantic import BaseModel


class GetSeismPayload(BaseModel):
    timestamp: int
    country: str
    magnitude: float


class GetEntriesQueryParameters(BaseModel):
    country: Optional[str] = None
    dateLower: Optional[datetime.date] = None
    dateUpper: Optional[datetime.date] = None
    magnitudeLower: Optional[float] = None
    magnitudeUpper: Optional[float] = None
    skip: Optional[int] = None

    def to_sql_query(self):
        query = """SELECT * FROM s3object s WHERE """
        if self.country:
            query += f"s.country = '{self.country}' AND "
        if self.dateLower:
            query += f's."timestamp" >= {int(time.mktime(self.dateLower.timetuple()))} AND '
        if self.dateUpper:
            # TODO: Fix this, it's not working
            query += f's."timestamp" <= {int(time.mktime(self.dateUpper.timetuple()))} AND '
        if self.magnitudeLower:
            query += f"CAST(s.magnitude as float) >= {self.magnitudeLower} AND "
        if self.magnitudeUpper:
            query += f"CAST(s.magnitude as float) <= {self.magnitudeUpper} AND "
        query += "1 = 1 "  # To avoid errors when no parameters are passed
        if self.skip:
            query += f"LIMIT 100 OFFSET {self.skip}"
        return query
