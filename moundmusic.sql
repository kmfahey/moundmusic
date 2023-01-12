
ALTER TABLE artist_album_bridge DROP CONSTRAINT fk_albums;

ALTER TABLE artist_album_bridge DROP CONSTRAINT fk_artists;

ALTER TABLE artist_song_bridge DROP CONSTRAINT fk_songs;

ALTER TABLE artist_song_bridge DROP CONSTRAINT fk_artists;

ALTER TABLE album_cover DROP CONSTRAINT fk_albums;

ALTER TABLE album_genre_bridge DROP CONSTRAINT fk_albums;

ALTER TABLE album_genre_bridge DROP CONSTRAINT fk_genres;

ALTER TABLE artist_genre_bridge DROP CONSTRAINT fk_artists;

ALTER TABLE artist_genre_bridge DROP CONSTRAINT fk_genres;

ALTER TABLE song_genre_bridge DROP CONSTRAINT fk_songs;

ALTER TABLE song_genre_bridge DROP CONSTRAINT fk_genres;

ALTER TABLE album DROP CONSTRAINT fk_album_covers;

ALTER TABLE album_song_bridge DROP CONSTRAINT fk_albums;

ALTER TABLE album_song_bridge DROP CONSTRAINT fk_songs;

ALTER TABLE buyer_account DROP CONSTRAINT fk_users;

ALTER TABLE song_lyrics DROP CONSTRAINT fk_songs;

ALTER TABLE song DROP CONSTRAINT fk_song_lyrics;

ALTER TABLE seller_account DROP CONSTRAINT fk_users;

ALTER TABLE to_buy_listing DROP CONSTRAINT fk_buyer_accounts;

ALTER TABLE to_buy_listing DROP CONSTRAINT fk_albums;

ALTER TABLE to_sell_listing DROP CONSTRAINT fk_albums;

ALTER TABLE to_sell_listing DROP CONSTRAINT fk_seller_accounts;

ALTER TABLE user_password DROP CONSTRAINT fk_users;


DROP INDEX IF EXISTS idx_album_cover_album_cover_id;

DROP INDEX IF EXISTS idx_artist_artist_id;

DROP INDEX IF EXISTS idx_buyer_account_buyer_id;

DROP INDEX IF EXISTS idx_genre_genre_id;

DROP INDEX IF EXISTS idx_song_lyrics_song_lyrics_id;

DROP INDEX IF EXISTS idx_user_password_password_id;

DROP INDEX IF EXISTS idx_seller_account_seller_id;

DROP INDEX IF EXISTS idx_song_song_id;

DROP INDEX IF EXISTS idx_to_buy_listing_to_buy_listing_id;

DROP INDEX IF EXISTS idx_to_sell_listing_to_sell_listing_id;

DROP INDEX IF EXISTS idx_user_user_id;

DROP INDEX IF EXISTS idx_artist_album_bridge_album_id;

DROP INDEX IF EXISTS idx_artist_album_bridge_artist_id;

DROP INDEX IF EXISTS idx_album_genre_bridge_album_id;

DROP INDEX IF EXISTS idx_album_genre_bridge_genre_id;

DROP INDEX IF EXISTS idx_album_song_bridge_album_id;

DROP INDEX IF EXISTS idx_album_song_bridge_song_id;


DROP TABLE IF EXISTS album_cover;

DROP TABLE IF EXISTS album;

DROP TABLE IF EXISTS artist;

DROP TABLE IF EXISTS buyer_account;

DROP TABLE IF EXISTS genre;

DROP TABLE IF EXISTS song_lyrics;

DROP TABLE IF EXISTS user_password;

DROP TABLE IF EXISTS seller_account;

DROP TABLE IF EXISTS song;

DROP TABLE IF EXISTS to_buy_listing;

DROP TABLE IF EXISTS to_sell_listing;

DROP TABLE IF EXISTS user_;

DROP TABLE IF EXISTS artist_album_bridge;

DROP TABLE IF EXISTS artist_song_bridge;

DROP TABLE IF EXISTS album_genre_bridge;

DROP TABLE IF EXISTS artist_genre_bridge;

DROP TABLE IF EXISTS song_genre_bridge;

DROP TABLE IF EXISTS album_song_bridge;


-- CREATE TYPE image_type AS ENUM('png', 'jpg', 'gif');


CREATE TABLE album_cover (
    album_cover_id SERIAL PRIMARY KEY,
    image_file_type image_type NOT NULL,
    image_data BYTEA NOT NULL,
    album_id INTEGER 
);


CREATE TABLE album (
    album_id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    number_of_discs SMALLINT NOT NULL DEFAULT 1,
    number_of_tracks SMALLINT NOT NULL,
    release_date DATE NOT NULL,
    album_cover_id INTEGER
);

-- CREATE TYPE gender_type AS ENUM('male', 'female', 'nonbinary');


CREATE TABLE artist (
    artist_id SERIAL PRIMARY KEY,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    gender gender_type NOT NULL,
    birth_date DATE NOT NULL
);


CREATE TABLE buyer_account (
    buyer_id SERIAL PRIMARY KEY,
    postboard_name VARCHAR(64),
    date_created DATE NOT NULL,
    user_id INTEGER
);


CREATE TABLE genre (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(64) NOT NULL
);


CREATE TABLE song_lyrics (
    song_lyrics_id SERIAL PRIMARY KEY,
    lyrics TEXT NOT NULL,
    song_id INTEGER
);


CREATE TABLE user_password (
    password_id SERIAL PRIMARY KEY,
    encrypted_password BYTEA NOT NULL,
    user_id INTEGER
);


CREATE TABLE seller_account (
    seller_id SERIAL PRIMARY KEY,
    storefront_name VARCHAR(64),
    date_created DATE NOT NULL,
    user_id INTEGER
);


CREATE TABLE song (
    song_id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    length_minutes SMALLINT NOT NULL,
    length_seconds SMALLINT NOT NULL,
    song_lyrics_id INTEGER
);


CREATE TABLE to_buy_listing (
    to_buy_listing_id SERIAL PRIMARY KEY,
    max_accepting_price DECIMAL NOT NULL,
    date_posted DATE NOT NULL,
    album_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL
);


CREATE TABLE to_sell_listing (
    to_sell_listing_id SERIAL PRIMARY KEY,
    asking_price DECIMAL NOT NULL,
    date_posted DATE NOT NULL,
    album_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL
);


CREATE TABLE user_ (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(16) NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    gender gender_type NOT NULL,
    date_joined DATE NOT NULL,
    buyer_id INTEGER,
    seller_id INTEGER
);


CREATE TABLE album_genre_bridge (
    album_genre_bridge_id SERIAL PRIMARY KEY,
    album_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    UNIQUE (album_id, genre_id)
);

CREATE TABLE artist_genre_bridge (
    artist_genre_bridge_id SERIAL PRIMARY KEY,
    artist_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    UNIQUE (artist_id, genre_id)
);

CREATE TABLE song_genre_bridge (
    song_genre_bridge_id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    UNIQUE (song_id, genre_id)
);

CREATE TABLE album_song_bridge (
    album_song_bridge_id SERIAL PRIMARY KEY,
    album_id INTEGER NOT NULL,
    disc_number SMALLINT NOT NULL,
    track_number SMALLINT NOT NULL,
    song_id INTEGER NOT NULL,
    UNIQUE (album_id, song_id)
);

CREATE TABLE artist_album_bridge (
    artist_album_bridge_id SERIAL PRIMARY KEY,
    album_id INTEGER NOT NULL,
    artist_id INTEGER NOT NULL,
    UNIQUE (album_id, artist_id)
);

CREATE TABLE artist_song_bridge (
    artist_song_bridge_id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    artist_id INTEGER NOT NULL,
    UNIQUE (song_id, artist_id)
);


ALTER TABLE artist_album_bridge
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE NO ACTION;

ALTER TABLE artist_album_bridge
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artist (artist_id)
ON DELETE NO ACTION;

ALTER TABLE artist_song_bridge
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artist (artist_id)
ON DELETE NO ACTION;

ALTER TABLE artist_song_bridge
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES song (song_id)
ON DELETE NO ACTION;

ALTER TABLE album_cover
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE CASCADE;

ALTER TABLE album_genre_bridge
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE NO ACTION;

ALTER TABLE album_genre_bridge
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genre (genre_id)
ON DELETE NO ACTION;

ALTER TABLE artist_genre_bridge
ADD CONSTRAINT fk_artists
FOREIGN KEY (artist_id)
REFERENCES artist (artist_id)
ON DELETE NO ACTION;

ALTER TABLE artist_genre_bridge
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genre (genre_id)
ON DELETE NO ACTION;

ALTER TABLE song_genre_bridge
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES song (song_id)
ON DELETE NO ACTION;

ALTER TABLE song_genre_bridge
ADD CONSTRAINT fk_genres
FOREIGN KEY (genre_id)
REFERENCES genre (genre_id)
ON DELETE NO ACTION;

ALTER TABLE album
ADD CONSTRAINT fk_album_covers
FOREIGN KEY (album_cover_id)
REFERENCES album_cover (album_cover_id)
ON DELETE CASCADE;

ALTER TABLE album_song_bridge
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE NO ACTION;

ALTER TABLE album_song_bridge
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES song (song_id)
ON DELETE NO ACTION;

ALTER TABLE buyer_account
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES user_ (user_id)
ON DELETE CASCADE;

ALTER TABLE song_lyrics
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES song (song_id)
ON DELETE CASCADE;

ALTER TABLE seller_account
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES user_ (user_id)
ON DELETE CASCADE;

ALTER TABLE song
ADD CONSTRAINT fk_song_lyrics
FOREIGN KEY (song_lyrics_id)
REFERENCES song_lyrics (song_lyrics_id)
ON DELETE CASCADE;

ALTER TABLE to_buy_listing
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE CASCADE;

ALTER TABLE to_buy_listing
ADD CONSTRAINT fk_buyer_accounts
FOREIGN KEY (buyer_id)
REFERENCES buyer_account (buyer_id)
ON DELETE CASCADE;

ALTER TABLE to_sell_listing
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE CASCADE;

ALTER TABLE to_sell_listing
ADD CONSTRAINT fk_seller_accounts
FOREIGN KEY (seller_id)
REFERENCES seller_account (seller_id)
ON DELETE CASCADE;

ALTER TABLE user_password
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES user_ (user_id)
ON DELETE CASCADE;


CREATE INDEX idx_album_cover_album_cover_id ON album_cover USING HASH(album_cover_id);

CREATE INDEX idx_artist_artist_id ON artist USING HASH(artist_id);

CREATE INDEX idx_buyer_account_buyer_id ON buyer_account USING HASH(buyer_id);

CREATE INDEX idx_genre_genre_id ON genre USING HASH(genre_id);

CREATE INDEX idx_song_lyrics_song_lyrics_id ON song_lyrics USING HASH(song_lyrics_id);

CREATE INDEX idx_user_password_password_id ON user_password USING HASH(password_id);

CREATE INDEX idx_seller_account_seller_id ON seller_account USING HASH(seller_id);

CREATE INDEX idx_song_song_id ON song USING HASH(song_id);

CREATE INDEX idx_to_buy_listing_to_buy_listing_id ON to_buy_listing USING HASH(to_buy_listing_id);

CREATE INDEX idx_to_sell_listing_to_sell_listing_id ON to_sell_listing USING HASH(to_sell_listing_id);

CREATE INDEX idx_user_user_id ON user_ USING HASH(user_id);

CREATE INDEX idx_artist_album_bridge_album_id ON artist_album_bridge USING HASH(album_id);

CREATE INDEX idx_artist_album_bridge_artist_id ON artist_album_bridge USING HASH(artist_id);

CREATE INDEX idx_artist_song_bridge_song_id ON artist_song_bridge USING HASH(song_id);

CREATE INDEX idx_artist_song_bridge_artist_id ON artist_song_bridge USING HASH(artist_id);

CREATE INDEX idx_album_genre_bridge_album_id ON album_genre_bridge USING HASH(album_id);

CREATE INDEX idx_album_genre_bridge_genre_id ON album_genre_bridge USING HASH(genre_id);

CREATE INDEX idx_artist_genre_bridge_artist_id ON artist_genre_bridge USING HASH(artist_id);

CREATE INDEX idx_artist_genre_bridge_genre_id ON artist_genre_bridge USING HASH(genre_id);

CREATE INDEX idx_song_genre_bridge_song_id ON song_genre_bridge USING HASH(song_id);

CREATE INDEX idx_song_genre_bridge_genre_id ON song_genre_bridge USING HASH(genre_id);

CREATE INDEX idx_album_song_bridge_album_id ON album_song_bridge USING HASH(album_id);

CREATE INDEX idx_album_song_bridge_song_id ON album_song_bridge USING HASH(song_id);
