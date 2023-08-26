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
            query = """SELECT * FROM "seism_database"."seism_parquet" ORDER BY timestamp ASC WHERE """
            if self.country:
                query += f"country = '{self.country}' AND "
            if self.dateLower:
                query += f'timestamp >= {int(self.dateLower.strftime("%s"))} AND '
            if self.dateUpper:
                query += f'timestamp <= {int(self.dateUpper.strftime("%s"))} AND '
            if self.magnitudeLower:
                query += f"magnitude >= {self.magnitudeLower} AND "
            if self.magnitudeUpper:
                query += f"magnitude <= {self.magnitudeUpper} AND "
            query += "1 = 1 "  # Always true statement to avoid errors in case of no parameters
            if self.skip:
                query += f"OFFSET {self.skip} "
            query += f"LIMIT {limit}"  # Memory limit
            return query
        except Exception as e:
            logging.error(f"Error creating SQL query from query parameters: {e}")
            raise e
