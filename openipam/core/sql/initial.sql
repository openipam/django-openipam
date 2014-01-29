-- auth

CREATE TABLE "auth_permission" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(50) NOT NULL,
        "content_type_id" integer NOT NULL,
        "codename" varchar(100) NOT NULL,
        UNIQUE ("content_type_id", "codename")
)
;

SELECT table_log_init(5,'auth_permission');

CREATE TABLE "auth_group_permissions" (
        "id" serial NOT NULL PRIMARY KEY,
        "group_id" integer NOT NULL,
        "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
        UNIQUE ("group_id", "permission_id")
)
;

SELECT table_log_init(5,'auth_group_permissions');

CREATE TABLE "auth_group" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(80) NOT NULL UNIQUE
)
;

SELECT table_log_init(5,'auth_group');

ALTER TABLE "auth_group_permissions" ADD CONSTRAINT "group_id_refs_id_f4b32aac" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "auth_permission_content_type_id" ON "auth_permission" ("content_type_id");
CREATE INDEX "auth_group_permissions_group_id" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id" ON "auth_group_permissions" ("permission_id");
CREATE INDEX "auth_group_name_like" ON "auth_group" ("name" varchar_pattern_ops);

-- sessions

CREATE TABLE "django_session" (
        "session_key" varchar(40) NOT NULL PRIMARY KEY,
        "session_data" text NOT NULL,
        "expire_date" timestamp with time zone NOT NULL
)
;
CREATE INDEX "django_session_session_key_like" ON "django_session" ("session_key" varchar_pattern_ops);
CREATE INDEX "django_session_expire_date" ON "django_session" ("expire_date");

-- admin

CREATE TABLE "django_admin_log" (
        "id" serial NOT NULL PRIMARY KEY,
        "action_time" timestamp with time zone NOT NULL,
        "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
        "content_type_id" integer,
        "object_id" text,
        "object_repr" varchar(200) NOT NULL,
        "action_flag" smallint CHECK ("action_flag" >= 0) NOT NULL,
        "change_message" text NOT NULL
)
;
CREATE INDEX "django_admin_log_user_id" ON "django_admin_log" ("user_id");
CREATE INDEX "django_admin_log_content_type_id" ON "django_admin_log" ("content_type_id");

-- sites

CREATE TABLE "django_site" (
        "id" serial NOT NULL PRIMARY KEY,
        "domain" varchar(100) NOT NULL,
        "name" varchar(50) NOT NULL
)
;

SELECT table_log_init(5,'django_site');

-- contenttypes

CREATE TABLE "django_content_type" (
        "id" serial NOT NULL PRIMARY KEY,
        "name" varchar(100) NOT NULL,
        "app_label" varchar(100) NOT NULL,
        "model" varchar(100) NOT NULL,
        UNIQUE ("app_label", "model")
)
;

SELECT table_log_init(5,'django_content_type');

-- south

CREATE TABLE "south_migrationhistory" (
        "id" serial NOT NULL PRIMARY KEY,
        "app_name" varchar(255) NOT NULL,
        "migration" varchar(255) NOT NULL,
        "applied" timestamp with time zone NOT NULL
)
;

-- user

CREATE TABLE "users_groups" (
        "id" serial NOT NULL PRIMARY KEY,
        "user_id" integer NOT NULL,
        "group_id" integer NOT NULL,
        UNIQUE ("user_id", "group_id")
)
;

SELECT table_log_init(5,'users_groups');

CREATE TABLE "users_user_permissions" (
        "id" serial NOT NULL PRIMARY KEY,
        "user_id" integer NOT NULL,
        "permission_id" integer NOT NULL,
        UNIQUE ("user_id", "permission_id")
)
;

SELECT table_log_init(5,'users_user_permissions');

ALTER TABLE "users"
    ADD COLUMN "first_name" varchar(255);
ALTER TABLE "users"
    ADD COLUMN "last_name" varchar(255);
ALTER TABLE "users"
    ADD COLUMN "is_active" boolean NOT NULL DEFAULT TRUE;
ALTER TABLE "users"
    ADD COLUMN "email" varchar(255);
ALTER TABLE "users"
    ADD COLUMN "is_superuser" boolean NOT NULL DEFAULT FALSE;
ALTER TABLE "users"
    ADD COLUMN "is_staff" boolean NOT NULL DEFAULT FALSE;
ALTER TABLE "users"
    ADD COLUMN "last_login" timestamp with time zone NOT NULL DEFAULT '1970-01-01 UTC';
ALTER TABLE "users"
    ADD COLUMN "password" varchar(128) NOT NULL DEFAULT '!';
ALTER TABLE "users"
    ADD COLUMN "date_joined" timestamp with time zone NOT NULL DEFAULT '1970-01-01 UTC';

ALTER TABLE "users_log"
    ADD COLUMN "first_name" varchar(255);
ALTER TABLE "users_log"
    ADD COLUMN "last_name" varchar(255);
ALTER TABLE "users_log"
    ADD COLUMN "is_active" boolean;
ALTER TABLE "users_log"
    ADD COLUMN "email" varchar(255);
ALTER TABLE "users_log"
    ADD COLUMN "is_superuser" boolean;
ALTER TABLE "users_log"
    ADD COLUMN "is_staff" boolean;
ALTER TABLE "users_log"
    ADD COLUMN "last_login" timestamp with time zone;
ALTER TABLE "users_log"
    ADD COLUMN "password" varchar(128);
ALTER TABLE "users_log"
    ADD COLUMN "date_joined" timestamp with time zone;


-- network

CREATE TABLE "default_pools" (
    "id" serial NOT NULL PRIMARY KEY,
    "pool_id" integer REFERENCES "pools" ("id") DEFERRABLE INITIALLY DEFERRED,
    "cidr" cidr NOT NULL UNIQUE
)
;

CREATE TABLE "network_ranges" (
    "id" serial NOT NULL PRIMARY KEY,
    "range" cidr NOT NULL UNIQUE
)
;

CREATE TABLE "addresstypes_ranges" (
    "id" serial NOT NULL PRIMARY KEY,
    "addresstype_id" integer NOT NULL,
    "networkrange_id" integer NOT NULL REFERENCES "network_ranges" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("addresstype_id", "networkrange_id")
)
;

CREATE TABLE "addresstypes" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "description" text NOT NULL,
    "pool_id" integer REFERENCES "pools" ("id") DEFERRABLE INITIALLY DEFERRED,
    "is_default" boolean NOT NULL
)
;

ALTER TABLE "pools"
    ADD COLUMN "assignable" boolean NOT NULL DEFAULT FALSE;

ALTER TABLE "pools_log"
    ADD COLUMN "assignable" boolean;


-- hosts

ALTER TABLE "hosts"
    ADD COLUMN "address_type_id" integer REFERENCES "addresstypes" ("id") DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "hosts_log"
    ADD COLUMN "address_type_id" integer;


-- core

CREATE TABLE "feature_requests" (
    "id" serial NOT NULL PRIMARY KEY,
    "type" varchar(255) NOT NULL,
    "comment" text NOT NULL,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "submitted" timestamp with time zone NOT NULL
)
;


-- guardian

CREATE TABLE "guardian_userobjectpermission" (
    "id" serial NOT NULL PRIMARY KEY,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_pk" varchar(255) NOT NULL,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id", "object_pk")
)
;
CREATE TABLE "guardian_groupobjectpermission" (
    "id" serial NOT NULL PRIMARY KEY,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "object_pk" varchar(255) NOT NULL,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("group_id", "permission_id", "object_pk")
)
;


-- admin tools

CREATE TABLE "admin_tools_menu_bookmark" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "url" varchar(255) NOT NULL,
    "title" varchar(255) NOT NULL
)
;

CREATE TABLE "admin_tools_dashboard_preferences" (
    "id" serial NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED,
    "data" text NOT NULL,
    "dashboard_id" varchar(100) NOT NULL,
    UNIQUE ("user_id", "dashboard_id")
)
;


ALTER TABLE "users_groups" ADD CONSTRAINT "user_id_refs_id_1217de52" FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "users_user_permissions" ADD CONSTRAINT "user_id_refs_id_1b5f933e" FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "users_groups" ADD CONSTRAINT "group_id_refs_id_e06c3832" FOREIGN KEY ("group_id") REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "users_user_permissions" ADD CONSTRAINT "permission_id_refs_id_98f3dbf4" FOREIGN KEY ("permission_id") REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "auth_permission" ADD CONSTRAINT "content_type_id_refs_id_d043b34a" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "django_admin_log" ADD CONSTRAINT "content_type_id_refs_id_93d2d1f8" FOREIGN KEY ("content_type_id") REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "addresstypes_ranges" ADD CONSTRAINT "addresstype_id_refs_id_149c549e" FOREIGN KEY ("addresstype_id") REFERENCES "addresstypes" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "users_groups_user_id" ON "users_groups" ("user_id");
CREATE INDEX "users_groups_group_id" ON "users_groups" ("group_id");
CREATE INDEX "users_user_permissions_user_id" ON "users_user_permissions" ("user_id");
CREATE INDEX "users_user_permissions_permission_id" ON "users_user_permissions" ("permission_id");
CREATE INDEX "users_username_like" ON "users" ("username" varchar_pattern_ops);
CREATE INDEX "users_min_permissions" ON "users" ("min_permissions");
CREATE INDEX "users_source" ON "users" ("source");
CREATE INDEX "default_pools_pool_id" ON "default_pools" ("pool_id");
CREATE INDEX "addresstypes_ranges_addresstype_id" ON "addresstypes_ranges" ("addresstype_id");
CREATE INDEX "addresstypes_ranges_networkrange_id" ON "addresstypes_ranges" ("networkrange_id");
CREATE INDEX "feature_requests_user_id" ON "feature_requests" ("user_id");
CREATE INDEX "guardian_userobjectpermission_permission_id" ON "guardian_userobjectpermission" ("permission_id");
CREATE INDEX "guardian_userobjectpermission_content_type_id" ON "guardian_userobjectpermission" ("content_type_id");
CREATE INDEX "guardian_userobjectpermission_user_id" ON "guardian_userobjectpermission" ("user_id");
CREATE INDEX "guardian_groupobjectpermission_permission_id" ON "guardian_groupobjectpermission" ("permission_id");
CREATE INDEX "guardian_groupobjectpermission_content_type_id" ON "guardian_groupobjectpermission" ("content_type_id");
CREATE INDEX "guardian_groupobjectpermission_group_id" ON "guardian_groupobjectpermission" ("group_id");
CREATE INDEX "admin_tools_menu_bookmark_user_id" ON "admin_tools_menu_bookmark" ("user_id");
CREATE INDEX "admin_tools_dashboard_preferences_user_id" ON "admin_tools_dashboard_preferences" ("user_id");

