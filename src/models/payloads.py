from typing import Optional
from pydantic import BaseModel


class GetSeismPayload(BaseModel):
    timestamp: int
    country: str
    magnitude: float


class GetEntriesQueryParameters(BaseModel):
    country: Optional[str] = None
    dateLower: Optional[str] = None
    dateUpper: Optional[str] = None
    magnitudeLower: Optional[float] = None
    magnitudeUpper: Optional[float] = None
    skip: Optional[int] = None

    def to_sql_query(self):
        query = """SELECT * FROM S3Object WHERE """
        if self.country:
            query += f"country = '{self.country}' AND "
        if self.dateLower:
            query += f"timestamp >= '{self.dateLower}' AND "
        if self.dateUpper:
            query += f"timestamp <= '{self.dateUpper}' AND "
        if self.magnitudeLower:
            query += f"magnitude >= {self.magnitudeLower} AND "
        if self.magnitudeUpper:
            query += f"magnitude <= {self.magnitudeUpper} AND "
        query += "1 = 1 "  # To avoid errors when no parameters are passed
        if self.skip:
            query += f"LIMIT 100 OFFSET {self.skip}"
        return query
