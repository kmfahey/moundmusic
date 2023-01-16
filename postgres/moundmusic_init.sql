\c moundmusic;

CREATE TYPE gender_type AS ENUM('male', 'female', 'nonbinary');

CREATE TABLE album (
    album_id SERIAL PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    number_of_discs SMALLINT NOT NULL DEFAULT 1,
    number_of_tracks SMALLINT NOT NULL,
    release_date DATE NOT NULL
);

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
    album_id INTEGER,
    buyer_id INTEGER
);

CREATE TABLE to_sell_listing (
    to_sell_listing_id SERIAL PRIMARY KEY,
    asking_price DECIMAL NOT NULL,
    date_posted DATE NOT NULL,
    album_id INTEGER,
    seller_id INTEGER
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
ON DELETE NO ACTION;

ALTER TABLE song_lyrics
ADD CONSTRAINT fk_songs
FOREIGN KEY (song_id)
REFERENCES song (song_id)
ON DELETE NO ACTION;

ALTER TABLE seller_account
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES user_ (user_id)
ON DELETE NO ACTION;

ALTER TABLE song
ADD CONSTRAINT fk_song_lyrics
FOREIGN KEY (song_lyrics_id)
REFERENCES song_lyrics (song_lyrics_id)
ON DELETE NO ACTION;

ALTER TABLE to_buy_listing
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE NO ACTION;

ALTER TABLE to_buy_listing
ADD CONSTRAINT fk_buyer_accounts
FOREIGN KEY (buyer_id)
REFERENCES buyer_account (buyer_id)
ON DELETE NO ACTION;

ALTER TABLE to_sell_listing
ADD CONSTRAINT fk_albums
FOREIGN KEY (album_id)
REFERENCES album (album_id)
ON DELETE NO ACTION;

ALTER TABLE to_sell_listing
ADD CONSTRAINT fk_seller_accounts
FOREIGN KEY (seller_id)
REFERENCES seller_account (seller_id)
ON DELETE NO ACTION;

ALTER TABLE user_password
ADD CONSTRAINT fk_users
FOREIGN KEY (user_id)
REFERENCES user_ (user_id)
ON DELETE NO ACTION;

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

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);

CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);

CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;

CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);

SELECT pg_catalog.setval('public.auth_permission_id_seq', 164, true);

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);

SELECT pg_catalog.setval('public.auth_user_id_seq', 1, true);

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);

SELECT pg_catalog.setval('public.django_content_type_id_seq', 41, true);

SELECT pg_catalog.setval('public.django_migrations_id_seq', 23, true);

SELECT pg_catalog.setval('public.genre_genre_id_seq', 10, true);

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


