
ALTER TABLE artist_album_bridge DROP CONSTRAINT IF EXISTS fk_albums;

ALTER TABLE artist_album_bridge DROP CONSTRAINT IF EXISTS fk_artists;

ALTER TABLE artist_song_bridge DROP CONSTRAINT IF EXISTS fk_songs;

ALTER TABLE artist_song_bridge DROP CONSTRAINT IF EXISTS fk_artists;

ALTER TABLE album_genre_bridge DROP CONSTRAINT IF EXISTS fk_albums;

ALTER TABLE album_genre_bridge DROP CONSTRAINT IF EXISTS fk_genres;

ALTER TABLE artist_genre_bridge DROP CONSTRAINT IF EXISTS fk_artists;

ALTER TABLE artist_genre_bridge DROP CONSTRAINT IF EXISTS fk_genres;

ALTER TABLE song_genre_bridge DROP CONSTRAINT IF EXISTS fk_songs;

ALTER TABLE song_genre_bridge DROP CONSTRAINT IF EXISTS fk_genres;

ALTER TABLE album_song_bridge DROP CONSTRAINT IF EXISTS fk_albums;

ALTER TABLE album_song_bridge DROP CONSTRAINT IF EXISTS fk_songs;

ALTER TABLE buyer_account DROP CONSTRAINT IF EXISTS fk_users;

ALTER TABLE song_lyrics DROP CONSTRAINT IF EXISTS fk_songs;

ALTER TABLE song DROP CONSTRAINT IF EXISTS fk_song_lyrics;

ALTER TABLE seller_account DROP CONSTRAINT IF EXISTS fk_users;

ALTER TABLE to_buy_listing DROP CONSTRAINT IF EXISTS fk_buyer_accounts;

ALTER TABLE to_buy_listing DROP CONSTRAINT IF EXISTS fk_albums;

ALTER TABLE to_sell_listing DROP CONSTRAINT IF EXISTS fk_albums;

ALTER TABLE to_sell_listing DROP CONSTRAINT IF EXISTS fk_seller_accounts;

ALTER TABLE user_password DROP CONSTRAINT IF EXISTS fk_users;


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


DROP TYPE IF EXISTS gender_type;
