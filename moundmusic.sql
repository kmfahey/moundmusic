
ALTER TABLE artists_albums DROP CONSTRAINT fk_albums;

ALTER TABLE artists_albums DROP CONSTRAINT fk_artists;

ALTER TABLE artists_songs DROP CONSTRAINT fk_songs;

ALTER TABLE artists_songs DROP CONSTRAINT fk_artists;

ALTER TABLE album_covers DROP CONSTRAINT fk_albums;

ALTER TABLE albums_genres DROP CONSTRAINT fk_albums;

ALTER TABLE albums_genres DROP CONSTRAINT fk_genres;

ALTER TABLE artists_genres DROP CONSTRAINT fk_artists;

ALTER TABLE artists_genres DROP CONSTRAINT fk_genres;

ALTER TABLE songs_genres DROP CONSTRAINT fk_songs;

ALTER TABLE songs_genres DROP CONSTRAINT fk_genres;

ALTER TABLE albums DROP CONSTRAINT fk_album_covers;

ALTER TABLE albums DROP CONSTRAINT fk_song_lyrics;

ALTER TABLE albums_songs DROP CONSTRAINT fk_albums;

ALTER TABLE albums_songs DROP CONSTRAINT fk_songs;

ALTER TABLE buyer_accounts DROP CONSTRAINT fk_users;

ALTER TABLE song_lyrics DROP CONSTRAINT fk_songs;

ALTER TABLE songs DROP CONSTRAINT fk_song_lyrics;

ALTER TABLE seller_accounts DROP CONSTRAINT fk_users;

ALTER TABLE to_buy_listings DROP CONSTRAINT fk_buyer_accounts;

ALTER TABLE to_buy_listings DROP CONSTRAINT fk_albums;

ALTER TABLE to_sell_listings DROP CONSTRAINT fk_albums;

ALTER TABLE to_sell_listings DROP CONSTRAINT fk_seller_accounts;

ALTER TABLE user_passwords DROP CONSTRAINT fk_users;


DROP INDEX IF EXISTS idx_album_covers_album_cover_id;

DROP INDEX IF EXISTS idx_artists_artist_id;

DROP INDEX IF EXISTS idx_buyer_accounts_buyer_id;

DROP INDEX IF EXISTS idx_genres_genre_id;

DROP INDEX IF EXISTS idx_song_lyrics_song_lyrics_id;

DROP INDEX IF EXISTS idx_user_passwords_password_id;

DROP INDEX IF EXISTS idx_seller_accounts_seller_id;

DROP INDEX IF EXISTS idx_songs_song_id;

DROP INDEX IF EXISTS idx_to_buy_listings_to_buy_listing_id;

DROP INDEX IF EXISTS idx_to_sell_listings_to_sell_listing_id;

DROP INDEX IF EXISTS idx_users_user_id;

DROP INDEX IF EXISTS idx_artists_albums_album_id;

DROP INDEX IF EXISTS idx_artists_albums_artist_id;

DROP INDEX IF EXISTS idx_albums_genres_album_id;

DROP INDEX IF EXISTS idx_albums_genres_genre_id;

DROP INDEX IF EXISTS idx_albums_songs_album_id;

DROP INDEX IF EXISTS idx_albums_songs_song_id;


DROP TABLE IF EXISTS album_covers;

DROP TABLE IF EXISTS albums;

DROP TABLE IF EXISTS artists;

DROP TABLE IF EXISTS buyer_accounts;

DROP TABLE IF EXISTS genres;

DROP TABLE IF EXISTS song_lyrics;

DROP TABLE IF EXISTS user_passwords;

DROP TABLE IF EXISTS seller_accounts;

DROP TABLE IF EXISTS songs;

DROP TABLE IF EXISTS to_buy_listings;

DROP TABLE IF EXISTS to_sell_listings;

DROP TABLE IF EXISTS users;

DROP TABLE IF EXISTS artists_albums;

DROP TABLE IF EXISTS artists_songs;

DROP TABLE IF EXISTS albums_genres;

DROP TABLE IF EXISTS artists_genres;

DROP TABLE IF EXISTS songs_genres;

DROP TABLE IF EXISTS albums_songs;


-- CREATE TYPE image_type AS ENUM('png', 'jpg', 'gif');


CREATE TABLE album_covers (
    album_cover_id SERIAL PRIMARY KEY,
    image_file_type image_type NOT NULL,
    image_data BYTEA NOT NULL,
    album_id INTEGER 
);


CREATE TABLE albums (
    album_id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    number_of_discs SMALLINT NOT NULL DEFAULT 1,
    number_of_tracks SMALLINT NOT NULL,
    release_date DATE,
    album_cover_id INTEGER,
    song_lyrics_id INTEGER
);

-- CREATE TYPE gender_type AS ENUM('male', 'female', 'nonbinary');


CREATE TABLE artists (
    artist_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    gender gender_type NOT NULL,
    birth_date DATE NOT NULL
);


CREATE TABLE buyer_accounts (
    buyer_id SERIAL PRIMARY KEY,
    storefront_name VARCHAR(64),
    date_created DATE NOT NULL,
    user_id INTEGER
);


CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(64) NOT NULL
);


CREATE TABLE song_lyrics (
    song_lyrics_id SERIAL PRIMARY KEY,
    lyrics TEXT NOT NULL,
    song_id INTEGER
);


CREATE TABLE user_passwords (
    password_id SERIAL PRIMARY KEY,
    password_ciphertext VARCHAR(256) NOT NULL,
    user_id INTEGER
);


CREATE TABLE seller_accounts (
    seller_id SERIAL PRIMARY KEY,
    postboard_name VARCHAR(64),
    date_created DATE NOT NULL,
    user_id INTEGER
);


CREATE TABLE songs (
    song_id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    length_minutes SMALLINT NOT NULL,
    length_seconds SMALLINT NOT NULL,
    song_lyrics_id INTEGER
);


CREATE TABLE to_buy_listings (
    to_buy_listing_id SERIAL PRIMARY KEY,
    max_accepting_price DECIMAL NOT NULL,
    date_posted DATE,
    album_id INTEGER,
    buyer_id INTEGER
);


CREATE TABLE to_sell_listings (
    to_sell_listing_id SERIAL PRIMARY KEY,
    asking_price DECIMAL NOT NULL,
    date_posted DATE,
    album_id INTEGER,
    seller_id INTEGER
);


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_handle VARCHAR(16) NOT NULL,
    user_name VARCHAR(64) NOT NULL,
    date_joined DATE NOT NULL,
    buyer_id INTEGER,
    seller_id INTEGER
);


CREATE TABLE albums_genres (
    albums_genres_id SERIAL PRIMARY KEY,
    album_id INTEGER,
    genre_id INTEGER
);

CREATE TABLE artists_genres (
    artists_genres_id SERIAL PRIMARY KEY,
    artist_id INTEGER,
    genre_id INTEGER
);

CREATE TABLE songs_genres (
    songs_genres_id SERIAL PRIMARY KEY,
    song_id INTEGER,
    genre_id INTEGER
);

CREATE TABLE albums_songs (
    albums_songs_id SERIAL PRIMARY KEY,
    album_id INTEGER,
    disc_number SMALLINT NOT NULL,
    track_number SMALLINT NOT NULL,
    song_id INTEGER
);

CREATE TABLE artists_albums (
    artists_albums_id SERIAL PRIMARY KEY,
    album_id INTEGER,
    artist_id INTEGER
);

CREATE TABLE artists_songs (
    artists_songs_id SERIAL PRIMARY KEY,
    song_id INTEGER,
    artist_id INTEGER
);


ALTER TABLE artists_albums
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE artists_albums
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artists (artist_id)
ON DELETE SET NULL;

ALTER TABLE artists_songs
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artists (artist_id)
ON DELETE SET NULL;

ALTER TABLE artists_songs
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES songs (song_id)
ON DELETE SET NULL;

ALTER TABLE album_covers
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE albums_genres
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE albums_genres
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genres (genre_id)
ON DELETE SET NULL;

ALTER TABLE artists_genres
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artists (artist_id)
ON DELETE SET NULL;

ALTER TABLE artists_genres
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genres (genre_id)
ON DELETE SET NULL;

ALTER TABLE songs_genres
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES songs (song_id)
ON DELETE SET NULL;

ALTER TABLE songs_genres
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genres (genre_id)
ON DELETE SET NULL;

ALTER TABLE albums
ADD CONSTRAINT fk_album_covers
FOREIGN KEY (album_cover_id)
REFERENCES album_covers (album_cover_id)
ON DELETE SET NULL;

ALTER TABLE albums
ADD CONSTRAINT fk_song_lyrics
FOREIGN KEY (song_lyrics_id)
REFERENCES song_lyrics (song_lyrics_id)
ON DELETE SET NULL;

ALTER TABLE albums_songs
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE albums_songs
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES songs (song_id)
ON DELETE SET NULL;

ALTER TABLE buyer_accounts
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES users (user_id)
ON DELETE SET NULL;

ALTER TABLE song_lyrics
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES songs (song_id)
ON DELETE SET NULL;

ALTER TABLE seller_accounts
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES users (user_id)
ON DELETE SET NULL;

ALTER TABLE songs
ADD CONSTRAINT fk_song_lyrics
FOREIGN KEY (song_lyrics_id)
REFERENCES song_lyrics (song_lyrics_id)
ON DELETE SET NULL;

ALTER TABLE to_buy_listings
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE to_buy_listings
ADD CONSTRAINT fk_buyer_accounts
FOREIGN KEY (buyer_id)
REFERENCES buyer_accounts (buyer_id)
ON DELETE SET NULL;

ALTER TABLE to_sell_listings
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES albums (album_id)
ON DELETE SET NULL;

ALTER TABLE to_sell_listings
ADD CONSTRAINT fk_seller_accounts
FOREIGN KEY (seller_id)
REFERENCES seller_accounts (seller_id)
ON DELETE SET NULL;

ALTER TABLE user_passwords
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES users (user_id)
ON DELETE SET NULL;


CREATE INDEX idx_album_covers_album_cover_id ON album_covers USING HASH(album_cover_id);

CREATE INDEX idx_artists_artist_id ON artists USING HASH(artist_id);

CREATE INDEX idx_buyer_accounts_buyer_id ON buyer_accounts USING HASH(buyer_id);

CREATE INDEX idx_genres_genre_id ON genres USING HASH(genre_id);

CREATE INDEX idx_song_lyrics_song_lyrics_id ON song_lyrics USING HASH(song_lyrics_id);

CREATE INDEX idx_user_passwords_password_id ON user_passwords USING HASH(password_id);

CREATE INDEX idx_seller_accounts_seller_id ON seller_accounts USING HASH(seller_id);

CREATE INDEX idx_songs_song_id ON songs USING HASH(song_id);

CREATE INDEX idx_to_buy_listings_to_buy_listing_id ON to_buy_listings USING HASH(to_buy_listing_id);

CREATE INDEX idx_to_sell_listings_to_sell_listing_id ON to_sell_listings USING HASH(to_sell_listing_id);

CREATE INDEX idx_users_user_id ON users USING HASH(user_id);

CREATE INDEX idx_artists_albums_album_id ON artists_albums USING HASH(album_id);

CREATE INDEX idx_artists_albums_artist_id ON artists_albums USING HASH(artist_id);

CREATE INDEX idx_artists_songs_song_id ON artists_songs USING HASH(song_id);

CREATE INDEX idx_artists_songs_artist_id ON artists_songs USING HASH(artist_id);

CREATE INDEX idx_albums_genres_album_id ON albums_genres USING HASH(album_id);

CREATE INDEX idx_albums_genres_genre_id ON albums_genres USING HASH(genre_id);

CREATE INDEX idx_artists_genres_artist_id ON artists_genres USING HASH(artist_id);

CREATE INDEX idx_artists_genres_genre_id ON artists_genres USING HASH(genre_id);

CREATE INDEX idx_songs_genres_song_id ON songs_genres USING HASH(song_id);

CREATE INDEX idx_songs_genres_genre_id ON songs_genres USING HASH(genre_id);

CREATE INDEX idx_albums_songs_album_id ON albums_songs USING HASH(album_id);

CREATE INDEX idx_albums_songs_song_id ON albums_songs USING HASH(song_id);
