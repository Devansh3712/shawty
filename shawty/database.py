import random
import string
from datetime import datetime
from typing import Any
from typing import List
from uuid import uuid4

import psycopg2

from shawty.config import secrets
from shawty.schema import Shawty


class Database:
    def __init__(self) -> None:
        self.connection = psycopg2.connect(secrets.DATABASE_URL)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.__setup_database()

    def __setup_database(self) -> None:
        users = """
        CREATE TABLE IF NOT EXISTS users (
            email       VARCHAR(320)                PRIMARY KEY,
            api_key     CHAR(32)                    UNIQUE NOT NULL,
            timestamp   TIMESTAMP WITH TIME ZONE    NOT NULL
        )
        """
        self.cursor.execute(users)
        urls = """
        CREATE TABLE IF NOT EXISTS urls (
            api_key     CHAR(32)                    NOT NULL,
            url         TEXT                        NOT NULL,
            hash        CHAR(5)                     UNIQUE NOT NULL,
            timestamp   TIMESTAMP WITH TIME ZONE    NOT NULL,
            visits      INT                         NOT NULL,
            CONSTRAINT fk_users
                FOREIGN KEY(api_key)
                    REFERENCES users(api_key)
                    ON DELETE CASCADE
        )
        """
        self.cursor.execute(urls)

    def get_emails(self) -> List[str]:
        query = """SELECT email FROM users"""
        self.cursor.execute(query)
        result = [data[0] for data in self.cursor.fetchall()]
        return result

    def get_hashes(self) -> List[str]:
        query = """SELECT hash FROM urls"""
        self.cursor.execute(query)
        result = [data[0] for data in self.cursor.fetchall()]
        return result

    def get_keys(self) -> List[str]:
        query = """SELECT api_key FROM users"""
        self.cursor.execute(query)
        result = [data[0] for data in self.cursor.fetchall()]
        return result

    def get_url_data(self, _hash: str) -> List[Any]:
        query = """
        SELECT * FROM urls
        WHERE hash = %s
        """
        self.cursor.execute(query, (_hash,))
        result = self.cursor.fetchone()
        return result

    def get_url(self, _hash: str) -> str:
        query = """
        SELECT url FROM urls
        WHERE hash = %s
        """
        self.cursor.execute(query, (_hash,))
        result = self.cursor.fetchone()[0]
        return result

    def get_urls(self, api_key: str) -> List[Shawty]:
        query = """
        SELECT url, hash, urls.timestamp, visits
        FROM users, urls
        WHERE users.api_key = urls.api_key
        AND users.api_key = %s
        """
        self.cursor.execute(query, (api_key,))
        response = self.cursor.fetchall()
        result: List[Shawty] = []
        for data in response:
            result.append(
                Shawty(
                    **{
                        key: data[index]
                        for index, key in enumerate(Shawty.__fields__.keys())
                    }
                )
            )
        return result

    def get_user(self, api_key: str) -> List[str]:
        query = """
        SELECT email, timestamp
        FROM users
        WHERE api_key = %s
        """
        self.cursor.execute(query, (api_key,))
        result = self.cursor.fetchone()
        return result

    @staticmethod
    def new_hash() -> str:
        chars = string.ascii_letters + string.digits
        _hash = [random.choice(chars) for _ in range(5)]
        return "".join(_hash)

    def new_key(self, email: str) -> str:
        if email in self.get_emails():
            raise
        api_key: str = uuid4().hex
        query = """
        INSERT INTO users (email, api_key, timestamp)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (email, api_key, datetime.utcnow()))
        return api_key

    def new_url(self, api_key: str, url: str) -> str:
        short_url: str = Database.new_hash()
        query = """
        INSERT INTO urls (api_key, url, hash, timestamp, visits)
        VALUES (%s, %s, %s, %s, 0)
        """
        self.cursor.execute(query, (api_key, url, short_url, datetime.utcnow()))
        return short_url

    def inc_visits(self, _hash: str):
        query = """
        UPDATE urls
        SET visits = visits + 1
        WHERE hash = %s
        """
        self.cursor.execute(query, (_hash,))
