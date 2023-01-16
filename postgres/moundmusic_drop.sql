
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


ALTER TABLE auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;

ALTER TABLE auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;

ALTER TABLE auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;

ALTER TABLE auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_group_id_97559544_fk_auth_group_id;

ALTER TABLE auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_user_id_6a12ed8b_fk_auth_user_id;

ALTER TABLE auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm;

ALTER TABLE auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id;

ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;

ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_auth_user_id;


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


DROP INDEX IF EXISTS auth_group_name_a6ea08ec_like;

DROP INDEX IF EXISTS auth_group_permissions_group_id_b120cbf9;

DROP INDEX IF EXISTS auth_group_permissions_permission_id_84c5c92e;

DROP INDEX IF EXISTS auth_permission_content_type_id_2f476e4b;

DROP INDEX IF EXISTS auth_user_groups_group_id_97559544;

DROP INDEX IF EXISTS auth_user_groups_user_id_6a12ed8b;

DROP INDEX IF EXISTS auth_user_user_permissions_permission_id_1fbb5f2c;

DROP INDEX IF EXISTS auth_user_user_permissions_user_id_a95ead1b;

DROP INDEX IF EXISTS auth_user_username_6821ab7c_like;

DROP INDEX IF EXISTS django_admin_log_content_type_id_c4bce8eb;

DROP INDEX IF EXISTS django_admin_log_user_id_c564eba6;

DROP INDEX IF EXISTS django_session_expire_date_a5c62663;

DROP INDEX IF EXISTS django_session_session_key_c0390e0f_like;


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

DROP TABLE IF EXISTS auth_group;

DROP TABLE IF EXISTS auth_group_permissions;

DROP TABLE IF EXISTS auth_permission;

DROP TABLE IF EXISTS auth_user;

DROP TABLE IF EXISTS auth_user_groups;

DROP TABLE IF EXISTS auth_user_user_permissions;

DROP TABLE IF EXISTS django_admin_log;

DROP TABLE IF EXISTS django_content_type;

DROP TABLE IF EXISTS django_migrations;

DROP TABLE IF EXISTS django_session;


DROP TYPE IF EXISTS gender_type;
