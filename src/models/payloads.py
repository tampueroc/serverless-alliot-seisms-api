import datetime
import logging
from typing import Optional
from pydantic import BaseModel

logging.getLogger().setLevel(logging.INFO)

class SeismEntry(BaseModel):
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

    def to_sql_query(self, limit=100):
        try:
            query = """SELECT * FROM s3object s WHERE """
            if self.country:
                query += f"s.country = '{self.country}' AND "
            if self.dateLower:
                query += f'CAST(s."timestamp" as int) >= {int(self.dateLower.strftime("%s"))} AND '
            if self.dateUpper:
                query += f'CAST(s."timestamp" as int) <= {int(self.dateUpper.strftime("%s"))} AND '
            if self.magnitudeLower:
                query += f"CAST(s.magnitude as float) >= {self.magnitudeLower} AND "
            if self.magnitudeUpper:
                query += f"CAST(s.magnitude as float) <= {self.magnitudeUpper} AND "
            query += f"1 = 1 LIMIT {limit}"  # To avoid errors when no parameters are passed
            if self.skip:
                query += f" OFFSET {self.skip}"
            return query
        except Exception as e:
            logging.error(f"Error creating SQL query from query parameters: {e}")
            raise e