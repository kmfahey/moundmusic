#!/usr/bin/python

import re
import random
import psycopg2
import datetime
import faker
from psycopg2 import Error


with open('postgres_auth.dat', 'r') as credentials:
    username = next(credentials).strip()
    password = next(credentials).strip()


def main():
    faker_obj = faker.Faker()
    with psycopg2.connect(user=username, password=password, host="127.0.0.1", port="5432", database="moundmusic") as connection:
        cursor = connection.cursor()
        seed_albums(faker_obj, cursor)


def seed_albums(faker_obj, cursor):
    cursor.execute("TRUNCATE albums CASCADE;")
    for _ in range(100):
        title = title_case(' '.join(faker_obj.words(random.randint(1,8))))
        number_of_discs = 1 if random.randint(0,9) else 2
        number_of_tracks = random.randint(8,20)
        release_date = faker_obj.date_between_dates(datetime.date(1990,1,1), datetime.date(2022,12,31))
        cursor.execute("INSERT INTO albums (title, number_of_discs, number_of_tracks, release_date)"
                       "VALUES (%s, %s, %s, %s);", (title, number_of_discs, number_of_tracks, release_date))


def title_case(strval):
    title_case_lc_words = {"a", "an", "and", "as", "at", "but", "by", "even", "for", "from", "if", "in", "into", "nor",
                           "now", "of", "off", "on", "or", "out", "so", "than", "that", "the", "to", "top", "up", "upon",
                           "when", "with", "yet"}
    tokens = re.split("(?<=[A-Za-zÀ-ÿ0-9._'ʼ’])(?=[^A-Za-zÀ-ÿ0-9._'ʼ’])"
                          "|"
                      "(?<=[^A-Za-zÀ-ÿ0-9._'ʼ’])(?=[A-Za-zÀ-ÿ0-9._'ʼ’])", strval)
    return ''.join(token.lower() if token.lower() in title_case_lc_words else token.capitalize() for token in tokens)

if __name__ == "__main__":
    main()
