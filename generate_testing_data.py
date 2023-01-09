#!/usr/bin/python

import datetime
import faker
import operator
import psycopg2
import random
import re

from psycopg2 import Error


with open('postgres_auth.dat', 'r') as credentials:
    username = next(credentials).strip()
    password = next(credentials).strip()


def main():
    faker_obj = faker.Faker()
    with psycopg2.connect(user=username, password=password, host="127.0.0.1", port="5432", database="moundmusic") as connection:
        with connection.cursor() as cursor:
            album_ids = seed_album(faker_obj, cursor)
            seed_album_cover(faker_obj, cursor, album_ids)


def seed_album(faker_obj, cursor):
    cursor.execute("DELETE FROM album;")
    for _ in range(100):
        title = title_case(' '.join(faker_obj.words(random.randint(1,8))))
        number_of_discs = 1 if random.randint(0,9) else 2
        number_of_tracks = random.randint(8,20)
        release_date = faker_obj.date_between_dates(datetime.date(1990,1,1), datetime.date(2022,12,31))
        cursor.execute("INSERT INTO album (title, number_of_discs, number_of_tracks, release_date)"
                       "VALUES (%s, %s, %s, %s);", (title, number_of_discs, number_of_tracks, release_date))
    cursor.execute("COMMIT;")
    cursor.execute("SELECT album_id FROM album;")
    return list(map(operator.itemgetter(0), cursor.fetchall()))


def seed_album_cover(faker_obj, cursor, album_ids):
    if not len(album_ids):
        print("album_ids list is empty; can't seed album_cover without album_ids")
        exit(1)
    cursor.execute("DELETE FROM album_cover;")
    for album_id in album_ids:
        image_file_type = random.choice(('jpg', 'png', 'gif'))
        image_data = faker_obj.binary(1024)
        cursor.execute("INSERT INTO album_cover (image_file_type, image_data, album_id)"
                       "VALUES (%s, %s, %s);", (image_file_type, image_data, album_id))
    cursor.execute("COMMIT;")


def title_case(strval):
    title_case_lc_words = {"a", "an", "and", "as", "at", "but", "by", "even", "for", "from", "if", "in", "into", "nor",
                           "now", "of", "off", "on", "or", "out", "so", "than", "that", "the", "to", "top", "up", "upon",
                           "when", "with", "yet"}
    # Splitting on the zero-width spot where the previous character is in
    # [A-Za-zÀ-ÿ0-9._'ʼ’] and the next character is not in [A-Za-zÀ-ÿ0-9._'ʼ’],
    # or the previous character is not in [A-Za-zÀ-ÿ0-9._'ʼ’] and the next
    # character *is* in [A-Za-zÀ-ÿ0-9._'ʼ’]
    tokens = re.split("(?<=[A-Za-zÀ-ÿ0-9._'ʼ’])(?=[^A-Za-zÀ-ÿ0-9._'ʼ’])"
                          "|"
                      "(?<=[^A-Za-zÀ-ÿ0-9._'ʼ’])(?=[A-Za-zÀ-ÿ0-9._'ʼ’])", strval)
    return ''.join(token.lower() if token.lower() in title_case_lc_words else token.capitalize() for token in tokens)


if __name__ == "__main__":
    main()
