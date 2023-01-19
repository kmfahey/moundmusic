#!/usr/bin/python3

import collections
import datetime
import faker
import operator
import psycopg2
import random
import re
import bcrypt

from psycopg2 import Error



with open('postgres_credentials.dat', 'r') as credentials:
    username = next(credentials).strip()
    password = next(credentials).strip()


def main():
    faker_obj = faker.Faker()
    with psycopg2.connect(user=username, password=password, host="localhost", port="5432", database="moundmusic") as connection:
        with connection.cursor() as cursor:
            table_seeder = Table_Seeder(faker_obj, cursor)

            cursor.execute("DELETE FROM artist_genre_bridge;")
            cursor.execute("DELETE FROM album_genre_bridge;")
            cursor.execute("DELETE FROM song_genre_bridge;")
            cursor.execute("DELETE FROM artist_album_bridge;")
            cursor.execute("DELETE FROM album_song_bridge;")
            cursor.execute("DELETE FROM artist_song_bridge;")

            print("Seeding `album` table....")
            table_seeder.seed_album_table()

            print("Seeding `artist` table....")
            table_seeder.seed_artist_table()

            print("Seeding `genre` table....")
            table_seeder.seed_genre_table()

            print("Seeding `song` table....")
            table_seeder.seed_song_table()
            print("Seeding `song_lyrics` table....")
            table_seeder.seed_song_lyrics_table()
            print("Updating `song` table with song_lyrics_ids....")
            table_seeder.update_song_table_with_song_lyrics_ids()

            print("Seeding `artist_genre_bridge` table....")
            table_seeder.seed_artist_genre_bridge_table()
            print("Seeding `album_genre_bridge` table....")
            table_seeder.seed_album_genre_bridge_table()
            print("Seeding `song_genre_bridge` table....")
            table_seeder.seed_song_genre_bridge_table()

            print("Seeding `artist_album_bridge` table....")
            table_seeder.seed_artist_album_bridge_table()
            print("Seeding `album_song_bridge` table....")
            table_seeder.seed_album_song_bridge_table()
            print("Seeding `artist_song_bridge` table....")
            table_seeder.seed_artist_song_bridge_table()

            print("Seeding `user_` table....")
            table_seeder.seed_user_table()
            print("Seeding `user_password` table....")
            table_seeder.seed_user_password_table()

            print("Seeding `seller_account` table....")
            table_seeder.seed_seller_account_table()
            print("Updating `user_` table with seller_ids....")
            table_seeder.update_user_table_with_seller_ids()

            print("Seeding `buyer_account` table....")
            table_seeder.seed_buyer_account_table()
            print("Updating `user_` table with buyer_ids....")

            table_seeder.update_user_table_with_buyer_ids()
            print("Seeing `to_buy_listing` table....")
            table_seeder.seed_to_buy_listing_table()
            print("Seeing `to_sell_listing` table....")
            table_seeder.seed_to_sell_listing_table()


def title_case(strval):
    title_case_lc_words = {"a", "an", "and", "as", "at", "but", "by", "even", "for", "from", "if", "in", "into", "nor",
                           "now", "of", "off", "on", "or", "out", "so", "than", "that", "the", "to", "top", "up", "upon",
                           "when", "with", "yet"}
    # Splitting on the zero-width spot where the previous character is in
    # [A-Za-zÀ-ÿ0-9._'ʼ’] and the next character is not in [A-Za-zÀ-ÿ0-9._'ʼ’],
    # or the previous character is *not* in [A-Za-zÀ-ÿ0-9._'ʼ’] and the next
    # character *is* in [A-Za-zÀ-ÿ0-9._'ʼ’]. A more advanced form of \b
    # that allows numerics and some punctuation.
    tokens = re.split("(?<=[A-Za-zÀ-ÿ0-9._'ʼ’])(?=[^A-Za-zÀ-ÿ0-9._'ʼ’])"
                          "|"
                      "(?<=[^A-Za-zÀ-ÿ0-9._'ʼ’])(?=[A-Za-zÀ-ÿ0-9._'ʼ’])", strval)
    # This ends up capitalizing a lot of whitespace but it hardly matters.
    return ''.join(token.lower() if token.lower() in title_case_lc_words else token.capitalize() for token in tokens)


class Table_Seeder(object):
    __slots__ = ("faker_obj", "cursor", "gender_list", "album_ids", "artist_ids", "genre_ids", "song_ids",
                 "total_tracks_on_albums", "song_ids_to_incidences", "song_ids_to_song_lyrics_ids",
                 "song_ids_to_song_lyrics_ids", "song_ids", "album_ids_to_artist_ids",
                 "album_ids_to_params", "album_ids_to_tracklists", "user_ids", "user_ids_to_seller_ids",
                 "user_ids_to_buyer_ids")

    Lyrics_Wordcount = 500

    Album_Params = collections.namedtuple('Album_Params', ('number_of_discs', 'number_of_tracks'))

    Album_Song_Bridge_Row = collections.namedtuple('Album_Song_Bridge_Row', ('album_id', 'disc_number', 'track_number', 'song_id'))

    def __init__(self, faker_obj, cursor):
        self.faker_obj = faker_obj
        self.cursor = cursor

    def seed_album_table(self):
        self.album_ids_to_params = dict()
        self.cursor.execute("UPDATE to_buy_listing SET album_id = NULL;")
        self.cursor.execute("DELETE FROM album;")
        album_params_list = list()
        for _ in range(100):
            title = title_case(' '.join(self.faker_obj.words(random.randint(1,8))))
            number_of_discs = 1 if random.randint(0,9) else 2
            number_of_tracks = random.randint(8,20) if number_of_discs == 1 else random.randint(16,40)
            album_params_list.append(self.Album_Params(number_of_discs, number_of_tracks))
            release_date = self.faker_obj.date_between_dates(datetime.date(1990,1,1), datetime.date(2022,12,31))
            self.cursor.execute("INSERT INTO album (title, number_of_discs, number_of_tracks, release_date)"
                           "VALUES (%s, %s, %s, %s);", (title, number_of_discs, number_of_tracks, release_date))
        self.cursor.execute("COMMIT;")
        self.cursor.execute("SELECT album_id FROM album;")
        self.album_ids = list(map(operator.itemgetter(0), self.cursor.fetchall()))
        self.album_ids_to_params.update(zip(self.album_ids, album_params_list))
        self.cursor.execute("SELECT SUM(number_of_tracks) FROM album;")
        self.total_tracks_on_albums = self.cursor.fetchone()[0]

    def _random_gender_first_last_names(self):
        gender = random.choice(("male",) * 10 + ("female",) * 10 + ("nonbinary",))
        if gender == "male":
            first_name = self.faker_obj.first_name_male()
            last_name = self.faker_obj.last_name_male()
        elif gender == "female":
            first_name = self.faker_obj.first_name_female()
            last_name = self.faker_obj.last_name_female()
        else:  # gender == "nonbinary"
            first_name = self.faker_obj.first_name_nonbinary()
            last_name = self.faker_obj.last_name_nonbinary()
        return gender, first_name, last_name

    def seed_artist_table(self):
        self.cursor.execute("DELETE FROM artist;")
        for _ in range(25):
            gender, first_name, last_name = self._random_gender_first_last_names()
            birth_date = self.faker_obj.date_between_dates(datetime.date(1925,1,1), datetime.date(1989,12,31))
            self.cursor.execute("INSERT INTO artist (first_name, last_name, gender, birth_date)"
                           "VALUES (%s, %s, %s, %s);", (first_name, last_name, gender, birth_date))
        self.cursor.execute("COMMIT;")
        self.cursor.execute("SELECT artist_id FROM artist;")
        self.artist_ids = list(map(operator.itemgetter(0), self.cursor.fetchall()))

    def seed_genre_table(self):
        self.cursor.execute("DELETE FROM genre;")
        for _ in range(10):
            genre_word_count = random.choice((1,)*17 + (3,)*3)
            if genre_word_count == 1:
                genre = title_case(self.faker_obj.word("noun"))
            else:
                genre = title_case(' '.join((self.faker_obj.word("noun"), self.faker_obj.word("noun"))))
            self.cursor.execute("INSERT INTO genre (genre_name) VALUES (%s);", (genre,))
        self.cursor.execute("COMMIT;")
        self.cursor.execute("SELECT genre_id FROM genre;")
        self.genre_ids = list(map(operator.itemgetter(0), self.cursor.fetchall()))

    def seed_song_table(self):
        self.song_ids_to_incidences = dict()
        self.cursor.execute("DELETE FROM song;")
        tracks_so_far = 0
        incidence_choices = (1,)*16 + (2,)*3 + (3,)
        incidences = list()
        while tracks_so_far < self.total_tracks_on_albums:
            incidence = random.choice(incidence_choices)
            if tracks_so_far + incidence > self.total_tracks_on_albums:
                incidence = self.total_tracks_on_albums - tracks_so_far
            title = title_case(' '.join(self.faker_obj.words(random.randint(1,5))))
            length_minutes = random.randint(0,5)
            length_seconds = random.randint(0,59)
            self.cursor.execute("INSERT INTO song (title, length_minutes, length_seconds) "
                                "VALUES (%s, %s, %s);", (title, length_minutes, length_seconds))
            incidences.append(incidence)
            tracks_so_far += incidence
        self.cursor.execute("COMMIT;")
        self.cursor.execute('SELECT song_id FROM song;')
        song_ids = list(map(operator.itemgetter(0), self.cursor.fetchall()))
        self.song_ids_to_incidences.update(zip(song_ids, incidences))

    def seed_song_lyrics_table(self):
        self.cursor.execute("DELETE FROM song_lyrics;")
        self.song_ids_to_song_lyrics_ids = dict()
        word_count = lambda sentence: len(sentence.split())
        for song_id in sorted(self.song_ids_to_incidences):
            lyrics_sentences = list()
            while sum(map(word_count, lyrics_sentences)) < self.Lyrics_Wordcount:
                lyrics_sentences.append(self.faker_obj.sentence())
            lyrics = " ".join(lyrics_sentences)
            self.cursor.execute("INSERT INTO song_lyrics (lyrics, song_id) VALUES (%s, %s);", (lyrics, song_id))
        self.cursor.execute("COMMIT;")
        self.cursor.execute('SELECT song_id, song_lyrics_id FROM song_lyrics;')
        self.song_ids_to_song_lyrics_ids.update(self.cursor.fetchall())
        self.song_ids = list(self.song_ids_to_song_lyrics_ids)

    def update_song_table_with_song_lyrics_ids(self):
        for song_id, song_lyrics_id in self.song_ids_to_song_lyrics_ids.items():
            self.cursor.execute("UPDATE song SET song_lyrics_id = %s WHERE song_id = %s;", (song_lyrics_id, song_id))
        self.cursor.execute("COMMIT;")

    def _seed_x_genre_bridge_table(self, bridge_to):
        assert bridge_to in ('song', 'album', 'artist')
        ids_list = (self.song_ids if bridge_to == 'song'
                    else self.artist_ids if bridge_to == 'artist'
                    else self.album_ids)
        table_name = bridge_to + "_genre_bridge"
        delete_sql = f"DELETE FROM {table_name};"
        insert_sql = f"INSERT INTO {table_name} ({bridge_to}_id, genre_id) VALUES (%s, %s);"
        self.cursor.execute(delete_sql)
        for datum_id in ids_list:
            genre_id = random.choice(self.genre_ids)
            self.cursor.execute(insert_sql, (datum_id, genre_id))
        self.cursor.execute("COMMIT;")

    def seed_artist_genre_bridge_table(self):
        self._seed_x_genre_bridge_table("artist")

    def seed_album_genre_bridge_table(self):
        self._seed_x_genre_bridge_table("album")

    def seed_song_genre_bridge_table(self):
        self._seed_x_genre_bridge_table("song")

    def seed_artist_album_bridge_table(self):
        self.album_ids_to_artist_ids = collections.defaultdict(set)
        self.cursor.execute("DELETE FROM artist_album_bridge;")
        for album_id in self.album_ids:
            number_of_artists = random.choice((1,) * 17 + (2,) * 2 + (3,))
            for _ in range(number_of_artists):
                artist_id = random.choice(self.artist_ids)
                self.cursor.execute("SELECT artist_id, album_id FROM artist_album_bridge WHERE album_id = %s AND artist_id = %s;",
                                    (album_id, artist_id))
                if self.cursor.fetchall():
                    continue
                self.cursor.execute("INSERT INTO artist_album_bridge (album_id, artist_id) VALUES (%s, %s);", (album_id, artist_id))
                self.album_ids_to_artist_ids[album_id].add(artist_id)
        self.cursor.execute("COMMIT;")

    def seed_album_song_bridge_table(self):
        self.cursor.execute("DELETE FROM album_song_bridge;")
        self.album_ids_to_tracklists = dict()
        song_ids_to_incidences = self.song_ids_to_incidences.copy()
        album_id_to_disc_numbers_track_numbers = dict()
        for album_id, album_params in self.album_ids_to_params.items():
            insert_values_list = list()
            if album_params.number_of_discs == 1:
                album_id_to_disc_numbers_track_numbers[album_id] = \
                        list((1, track_number) for track_number in range(1, album_params.number_of_tracks + 1))
            else:
                disc_numbers_track_numbers = list()
                for track_number in range(1, album_params.number_of_tracks // 2 + 1):
                    disc_numbers_track_numbers.append((1, track_number))
                track_number = album_params.number_of_tracks // 2 + 1
                while track_number <= album_params.number_of_tracks:
                    disc_numbers_track_numbers.append((2, track_number))
                    track_number += 1
                album_id_to_disc_numbers_track_numbers[album_id] = disc_numbers_track_numbers
                assert len(disc_numbers_track_numbers) == album_params.number_of_tracks
        song_ids = list(song_ids_to_incidences)
        for album_id, disc_numbers_track_numbers in album_id_to_disc_numbers_track_numbers.items():
            tracklist = list()
            for disc_number, track_number in sorted(disc_numbers_track_numbers):
                song_id = song_ids[random.randint(0, len(song_ids)-1)]
                if song_ids_to_incidences[song_id] == 1:
                    del song_ids_to_incidences[song_id]
                    song_ids.remove(song_id)
                else:
                    song_ids_to_incidences[song_id] -= 1
                album_song_bridge_row = self.Album_Song_Bridge_Row(album_id, 1, track_number, song_id)
                insert_values_list.append(album_song_bridge_row)
                tracklist.append((album_song_bridge_row.disc_number, album_song_bridge_row.track_number, song_id))
            self.album_ids_to_tracklists[album_id] = tracklist
        for album_song_bridge_row in insert_values_list:
            self.cursor.execute("SELECT album_id, song_id FROM album_song_bridge WHERE album_id = %s AND song_id = %s;",
                                (album_song_bridge_row.album_id, album_song_bridge_row.song_id))
            if self.cursor.fetchall():
                continue
            self.cursor.execute("INSERT INTO album_song_bridge (album_id, disc_number, track_number, song_id)"
                                "VALUES (%s, %s, %s, %s);", album_song_bridge_row)
        self.cursor.execute("COMMIT;")

    def seed_artist_song_bridge_table(self):
        album_id_to_artist_id_counts = dict()
        self.cursor.execute("DELETE FROM artist_song_bridge;")
        for album_id, tracklist in self.album_ids_to_tracklists.items():
            artist_id_counts = collections.defaultdict(int)
            for artist_id in self.album_ids_to_artist_ids[album_id]:
                for _, _, song_id in tracklist:
                    artist_id = random.choice(self.artist_ids)
                    self.cursor.execute("SELECT artist_id, song_id FROM artist_song_bridge WHERE song_id = %s AND artist_id = %s;",
                                        (song_id, artist_id))
                    if self.cursor.fetchall():
                        continue
                    self.cursor.execute("INSERT INTO artist_song_bridge (song_id, artist_id) "
                                        "VALUES (%s, %s);", (song_id, artist_id))
                    artist_id_counts[artist_id] += 1
            album_id_to_artist_id_counts[album_id] = artist_id_counts
        self.cursor.execute("COMMIT;")

    def seed_user_table(self):
        self.cursor.execute("DELETE FROM user_;")
        for _ in range(50):
            user_name = self.faker_obj.user_name()
            while len(user_name) > 16:
                user_name = self.faker_obj.user_name()
            gender, first_name, last_name = self._random_gender_first_last_names()
            birth_date = self.faker_obj.date_between_dates(datetime.date(1925,1,1), datetime.date(1989,12,31))
            age_of_majority_date = birth_date + datetime.timedelta(days=(18*365.24))
            date_joined = self.faker_obj.date_between_dates(datetime.date.today() - datetime.timedelta(days=(365.24*3)),
                                                            datetime.date.today())
            self.cursor.execute("INSERT INTO user_ (user_name, first_name, last_name, gender, date_joined) "
                                "VALUES (%s, %s, %s, %s, %s);", (user_name, first_name, last_name, gender, date_joined))
        self.cursor.execute("COMMIT;")
        self.cursor.execute("SELECT user_id FROM user_;")
        self.user_ids = list(map(operator.itemgetter(0), self.cursor.fetchall()))

    def seed_user_password_table(self):
        self.cursor.execute("DELETE FROM user_password;")
        for user_id in self.user_ids:
            password = self.faker_obj.password().encode("utf8")
            salt = bcrypt.gensalt()
            encrypted_password = bcrypt.hashpw(password, salt)
            self.cursor.execute("INSERT INTO user_password (encrypted_password, user_id) VALUES (%s, %s);", (encrypted_password, user_id))
        self.cursor.execute("COMMIT;")

    def _seed_buyer_seller_account_table(self, table_name, id_col_name, display_col_name, save_dict_attr_name):
        setattr(self, save_dict_attr_name, dict())
        delete_sql = f"DELETE FROM {table_name};"
        insert_sql = f"INSERT INTO {table_name} ({display_col_name}, date_created, user_id) VALUES (%s, %s, %s);"
        select_ids_sql = f"SELECT user_id, {id_col_name} FROM {table_name};"
        self.cursor.execute(delete_sql)
        for user_id in self.user_ids:
            if random.randint(1, 10) in (1, 2, 3, 4, 5, 6):
                display_col_value = title_case(' '.join(self.faker_obj.words(random.randint(2,6))))
                three_years_ago_date = datetime.date.today() - datetime.timedelta(days=(365.24*3))
                date_created = self.faker_obj.date_between_dates(three_years_ago_date, datetime.date.today())
                self.cursor.execute(insert_sql, (display_col_value, date_created, user_id))
        self.cursor.execute("COMMIT;")
        self.cursor.execute(select_ids_sql)
        getattr(self, save_dict_attr_name).update(self.cursor.fetchall())

    def seed_seller_account_table(self):
        self._seed_buyer_seller_account_table('seller_account', 'seller_id', 'storefront_name', 'user_ids_to_seller_ids')

    def update_user_table_with_seller_ids(self):
        for user_id, seller_id in self.user_ids_to_seller_ids.items():
            self.cursor.execute("UPDATE user_ SET seller_id = %s WHERE user_id = %s;", (seller_id, user_id))
        self.cursor.execute("COMMIT;")

    def seed_buyer_account_table(self):
        self._seed_buyer_seller_account_table('buyer_account', 'buyer_id', 'postboard_name', 'user_ids_to_buyer_ids')

    def update_user_table_with_buyer_ids(self):
        for user_id, buyer_id in self.user_ids_to_buyer_ids.items():
            self.cursor.execute("UPDATE user_ SET buyer_id = %s WHERE user_id = %s;", (buyer_id, user_id))
        self.cursor.execute("COMMIT;")

    def _seed_to_buy_or_sell_listing_table(self, table_name, id_col_name, price_col_name, saved_dict_attr_name):
        delete_sql = f"DELETE FROM {table_name};"
        insert_sql = (f"INSERT INTO {table_name} ({price_col_name}, date_posted, album_id, {id_col_name}) "
                      "VALUES (%s, %s, %s, %s);")
        self.cursor.execute(delete_sql)
        three_months_ago_date = datetime.date.today() - datetime.timedelta(days=(365.24 / 12 * 3))
        for id_datum in getattr(self, saved_dict_attr_name).values():
            for _ in range(random.randint(1,5)):
                album_id = random.choice(self.album_ids)
                price = round(2.50 + random.random() * 5.00, ndigits=2)
                date_posted = self.faker_obj.date_between_dates(three_months_ago_date, datetime.date.today())
                self.cursor.execute(insert_sql, (price, date_posted, album_id, id_datum))
        self.cursor.execute("COMMIT;")

    def seed_to_buy_listing_table(self):
        self._seed_to_buy_or_sell_listing_table('to_buy_listing', 'buyer_id', 'max_accepting_price', 'user_ids_to_buyer_ids')

    def seed_to_sell_listing_table(self):
        self._seed_to_buy_or_sell_listing_table('to_sell_listing', 'seller_id', 'asking_price', 'user_ids_to_seller_ids')



if __name__ == "__main__":
    main()
