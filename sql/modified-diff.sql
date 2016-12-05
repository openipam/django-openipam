START TRANSACTION;

----ALTER TABLE gul_recent_arp_byaddress
----	DROP CONSTRAINT gul_recent_arp_byaddress_pkey;

----ALTER TABLE gul_recent_arp_bymac
----	DROP CONSTRAINT gul_recent_arp_bymac_pkey;

----ALTER TABLE networks
----	DROP CONSTRAINT networks_pkey;

ALTER TABLE addresses
	DROP CONSTRAINT addresses_changed_by_7409950e_fk_users_id;

ALTER TABLE addresses
	DROP CONSTRAINT addresses_mac_bbedaf25_fk_hosts_mac;

ALTER TABLE addresses
	DROP CONSTRAINT addresses_network_d8c4f0d6_fk_networks_network;

ALTER TABLE addresses
	DROP CONSTRAINT addresses_pool_6908afb2_fk_pools_id;

ALTER TABLE addresstypes
	DROP CONSTRAINT addresstypes_pool_id_d09d84fe_fk_pools_id;

ALTER TABLE addresstypes_ranges
	DROP CONSTRAINT addresstypes_ranges_addresstype_id_800f01f5_uniq;

ALTER TABLE addresstypes_ranges
	DROP CONSTRAINT addresstypes_rang_networkrange_id_eecbee86_fk_network_ranges_id;

ALTER TABLE addresstypes_ranges
	DROP CONSTRAINT addresstypes_ranges_addresstype_id_ba1bdd5c_fk_addresstypes_id;

ALTER TABLE admin_tools_dashboard_preferences
	DROP CONSTRAINT admin_tools_dashboard_preferences_user_id_74da8e56_uniq;

ALTER TABLE admin_tools_dashboard_preferences
	DROP CONSTRAINT admin_tools_dashboard_preferences_user_id_8f768e6c_fk_users_id;

ALTER TABLE admin_tools_menu_bookmark
	DROP CONSTRAINT admin_tools_menu_bookmark_user_id_0382e410_fk_users_id;

ALTER TABLE attributes
	DROP CONSTRAINT attributes_changed_by_a0ce8282_fk_users_id;

ALTER TABLE freeform_attributes_to_hosts
	DROP CONSTRAINT freeform_attributes_to_hosts_aid_732dcce9_fk_attributes_id;

ALTER TABLE freeform_attributes_to_hosts
	DROP CONSTRAINT freeform_attributes_to_hosts_changed_by_e87ceb59_fk_users_id;

ALTER TABLE freeform_attributes_to_hosts
	DROP CONSTRAINT freeform_attributes_to_hosts_mac_18cdcb10_fk_hosts_mac;

ALTER TABLE structured_attribute_values
	DROP CONSTRAINT structured_attribute_values_aid_910dc527_fk_attributes_id;

ALTER TABLE structured_attribute_values
	DROP CONSTRAINT structured_attribute_values_changed_by_77ef40b9_fk_users_id;

ALTER TABLE structured_attributes_to_hosts
	DROP CONSTRAINT structured_attr_avid_c81a2a10_fk_structured_attribute_values_id;

ALTER TABLE structured_attributes_to_hosts
	DROP CONSTRAINT structured_attributes_to_hosts_changed_by_d8c5036a_fk_users_id;

ALTER TABLE structured_attributes_to_hosts
	DROP CONSTRAINT structured_attributes_to_hosts_mac_c6014278_fk_hosts_mac;

ALTER TABLE auth_group_permissions
	DROP CONSTRAINT auth_group_permissions_group_id_0cd325b0_uniq;

ALTER TABLE auth_group_permissions
	DROP CONSTRAINT auth_group_permiss_permission_id_84c5c92e_fk_auth_permission_id;

ALTER TABLE auth_group_permissions
	DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;

ALTER TABLE auth_permission
	DROP CONSTRAINT auth_permission_content_type_id_01ab375a_uniq;

ALTER TABLE auth_permission
	DROP CONSTRAINT auth_permiss_content_type_id_2f476e4b_fk_django_content_type_id;

ALTER TABLE authtoken_token
	DROP CONSTRAINT authtoken_token_user_id_35299eff_fk_users_id;

ALTER TABLE default_pools
	DROP CONSTRAINT default_pools_pool_id_df66ce5b_fk_pools_id;

ALTER TABLE dhcp_dns_records
	DROP CONSTRAINT dhcp_dns_records_name_key;

ALTER TABLE dhcp_dns_records
	DROP CONSTRAINT dhcp_dns_records_did_48c06968_fk_domains_id;

ALTER TABLE dhcp_dns_records
	DROP CONSTRAINT dhcp_dns_records_ip_content_9793c977_fk_addresses_address;

ALTER TABLE dhcp_dns_records
	DROP CONSTRAINT dhcp_dns_records_name_de22bce4_fk_hosts_hostname;

ALTER TABLE dhcp_groups
	DROP CONSTRAINT dhcp_groups_changed_by_dcfcf68e_fk_users_id;

ALTER TABLE dhcp_options_to_dhcp_groups
	DROP CONSTRAINT dhcp_options_to_dhcp_groups_changed_by_097bde67_fk_users_id;

ALTER TABLE dhcp_options_to_dhcp_groups
	DROP CONSTRAINT dhcp_options_to_dhcp_groups_gid_be49568a_fk_dhcp_groups_id;

ALTER TABLE dhcp_options_to_dhcp_groups
	DROP CONSTRAINT dhcp_options_to_dhcp_groups_oid_662b9bd6_fk_dhcp_options_id;

ALTER TABLE disabled
	DROP CONSTRAINT disabled_disabled_by_6bc555f2_fk_users_id;

ALTER TABLE django_content_type
	DROP CONSTRAINT django_content_type_app_label_76bd3d3b_uniq;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_changed_by_01775530_fk_users_id;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_did_780554e0_fk_domains_id;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_ip_content_b388d59a_fk_addresses_address;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_mac_87872210_fk_hosts_mac;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_tid_6fdb75c1_fk_dns_types_id;

ALTER TABLE dns_records
	DROP CONSTRAINT dns_records_vid_8f0b66a3_fk_dns_views_id;

ALTER TABLE dns_types
	DROP CONSTRAINT dns_types_name_key;

ALTER TABLE dns_types
	DROP CONSTRAINT dns_types_min_permissions_fc104974_fk_permissions_id;

ALTER TABLE domains
	DROP CONSTRAINT domains_name_key;

ALTER TABLE domains
	DROP CONSTRAINT domains_changed_by_418970cc_fk_users_id;

ALTER TABLE expiration_types
	DROP CONSTRAINT expiration_types_min_permissions_352f108d_fk_permissions_id;

ALTER TABLE feature_requests
	DROP CONSTRAINT feature_requests_user_id_78ca0788_fk_users_id;

ALTER TABLE guardian_groupobjectpermission
	DROP CONSTRAINT guardian_groupobjectpermission_group_id_3f189f7c_uniq;

ALTER TABLE guardian_groupobjectpermission
	DROP CONSTRAINT guardian_gro_content_type_id_7ade36b8_fk_django_content_type_id;

ALTER TABLE guardian_groupobjectpermission
	DROP CONSTRAINT guardian_groupobje_permission_id_36572738_fk_auth_permission_id;

ALTER TABLE guardian_groupobjectpermission
	DROP CONSTRAINT guardian_groupobjectpermissi_group_id_4bbbfb62_fk_auth_group_id;

ALTER TABLE guardian_userobjectpermission
	DROP CONSTRAINT guardian_userobjectpermission_user_id_b0b3d2fc_uniq;

ALTER TABLE guardian_userobjectpermission
	DROP CONSTRAINT guardian_use_content_type_id_2e892405_fk_django_content_type_id;

ALTER TABLE guardian_userobjectpermission
	DROP CONSTRAINT guardian_userobjec_permission_id_71807bfc_fk_auth_permission_id;

ALTER TABLE guardian_userobjectpermission
	DROP CONSTRAINT guardian_userobjectpermission_user_id_d5c1e964_fk_users_id;

ALTER TABLE guest_tickets
	DROP CONSTRAINT guest_tickets_uid_d6be03a4_fk_users_id;

----ALTER TABLE hosts
----	DROP CONSTRAINT hosts_mac_key;

ALTER TABLE hosts
	DROP CONSTRAINT hosts_address_type_id_e4b93b3f_fk_addresstypes_id;

ALTER TABLE hosts
	DROP CONSTRAINT hosts_changed_by_723a4ae3_fk_users_id;

ALTER TABLE hosts
	DROP CONSTRAINT hosts_dhcp_group_c5869ee2_fk_dhcp_groups_id;

ALTER TABLE users_groups
	DROP CONSTRAINT users_groups_user_id_fc7788e8_uniq;

ALTER TABLE users_groups
	DROP CONSTRAINT users_groups_group_id_2f3517aa_fk_auth_group_id;

ALTER TABLE users_groups
	DROP CONSTRAINT users_groups_user_id_f500bee5_fk_users_id;

ALTER TABLE hosts_to_pools
	DROP CONSTRAINT hosts_to_pools_changed_by_ec19c48a_fk_users_id;

ALTER TABLE hosts_to_pools
	DROP CONSTRAINT hosts_to_pools_mac_2dcf662f_fk_hosts_mac;

ALTER TABLE hosts_to_pools
	DROP CONSTRAINT hosts_to_pools_pool_id_153dfde8_fk_pools_id;

ALTER TABLE leases
	DROP CONSTRAINT leases_address_61c25e9b_fk_addresses_address;

ALTER TABLE network_taggednetworks
	DROP CONSTRAINT network_taggedne_content_object_id_15b096f6_fk_networks_network;

ALTER TABLE network_taggednetworks
	DROP CONSTRAINT network_taggednetworks_tag_id_9162cac9_fk_taggit_tag_id;

ALTER TABLE networks
	DROP CONSTRAINT networks_changed_by_121e9dce_fk_users_id;

ALTER TABLE networks
	DROP CONSTRAINT networks_dhcp_group_583e3685_fk_dhcp_groups_id;

ALTER TABLE networks
	DROP CONSTRAINT networks_shared_network_d4b59c59_fk_shared_networks_id;

ALTER TABLE networks_to_vlans
	DROP CONSTRAINT networks_to_vlans_changed_by_be0c78fc_fk_users_id;

ALTER TABLE networks_to_vlans
	DROP CONSTRAINT networks_to_vlans_network_d0859e23_fk_networks_network;

ALTER TABLE networks_to_vlans
	DROP CONSTRAINT networks_to_vlans_vlan_34819bf5_fk_vlans_id;

ALTER TABLE notifications
	DROP CONSTRAINT notifications_min_permissions_0b3d6256_fk_permissions_id;

ALTER TABLE pools
	DROP CONSTRAINT pools_dhcp_group_97f98870_fk_dhcp_groups_id;

ALTER TABLE shared_networks
	DROP CONSTRAINT shared_networks_changed_by_a3d08e7d_fk_users_id;

ALTER TABLE supermasters
	DROP CONSTRAINT supermasters_changed_by_d96f1f38_fk_users_id;

ALTER TABLE taggit_taggeditem
	DROP CONSTRAINT taggit_tagge_content_type_id_9957a03c_fk_django_content_type_id;

ALTER TABLE taggit_taggeditem
	DROP CONSTRAINT taggit_taggeditem_tag_id_f4f5b767_fk_taggit_tag_id;

ALTER TABLE user_groupsource
	DROP CONSTRAINT user_groupsource_group_id_05f3a9b1_fk_auth_group_id;

ALTER TABLE user_groupsource
	DROP CONSTRAINT user_groupsource_source_39fa839b_fk_auth_sources_id;

ALTER TABLE users
	DROP CONSTRAINT users_min_permissions_8bac820b_fk_permissions_id;

ALTER TABLE users
	DROP CONSTRAINT users_source_c3429765_fk_auth_sources_id;

ALTER TABLE users_user_permissions
	DROP CONSTRAINT users_user_permissions_user_id_3b86cbdf_uniq;

ALTER TABLE users_user_permissions
	DROP CONSTRAINT users_user_permiss_permission_id_6d08dcd2_fk_auth_permission_id;

ALTER TABLE users_user_permissions
	DROP CONSTRAINT users_user_permissions_user_id_92473840_fk_users_id;

ALTER TABLE vlans
	DROP CONSTRAINT vlans_changed_by_90a28c92_fk_users_id;

DROP INDEX addresses_140c1f12;

DROP INDEX addresses_91e02cd2;

DROP INDEX addresses_b10a8c0b;

DROP INDEX addresses_d9aad70c;

DROP INDEX addresstypes_ff383e3c;

DROP INDEX addresstypes_ranges_545030a3;

DROP INDEX addresstypes_ranges_879462cb;

DROP INDEX admin_tools_dashboard_preferences_e8701ad4;

DROP INDEX admin_tools_menu_bookmark_e8701ad4;

DROP INDEX attributes_d9aad70c;

DROP INDEX attributes_name_ec7b83a9_like;

DROP INDEX freeform_attributes_to_hosts_140c1f12;

DROP INDEX freeform_attributes_to_hosts_b99eb099;

DROP INDEX freeform_attributes_to_hosts_d9aad70c;

DROP INDEX structured_attribute_values_b99eb099;

DROP INDEX structured_attribute_values_d9aad70c;

DROP INDEX structured_attributes_to_hosts_140c1f12;

DROP INDEX structured_attributes_to_hosts_18e9e8b7;

DROP INDEX structured_attributes_to_hosts_d9aad70c;

DROP INDEX auth_group_name_a6ea08ec_like;

DROP INDEX auth_group_permissions_0e939a4f;

DROP INDEX auth_group_permissions_8373b171;

DROP INDEX auth_permission_417f1b1c;

DROP INDEX auth_sources_name_a9c1db5d_like;

DROP INDEX authtoken_token_key_10f0b77e_like;

DROP INDEX default_pools_ff383e3c;

DROP INDEX dhcp_dns_records_e48ee74e;

DROP INDEX dhcp_dns_records_ee85b622;

DROP INDEX dhcp_dns_records_name_de22bce4_like;

DROP INDEX dhcp_groups_b068931c;

DROP INDEX dhcp_groups_d9aad70c;

DROP INDEX dhcp_groups_name_e2b8daee_like;

DROP INDEX dhcp_options_name_8bf5242c_like;

DROP INDEX dhcp_options_option_9daefed1_like;

DROP INDEX dhcp_options_to_dhcp_groups_130f4311;

DROP INDEX dhcp_options_to_dhcp_groups_2d53a8fb;

DROP INDEX dhcp_options_to_dhcp_groups_d9aad70c;

DROP INDEX disabled_8cb7cfde;

DROP INDEX django_session_de54fa62;

DROP INDEX django_session_session_key_c0390e0f_like;

DROP INDEX dns_records_140c1f12;

DROP INDEX dns_records_97beaa21;

DROP INDEX dns_records_b06d9954;

DROP INDEX dns_records_d9aad70c;

DROP INDEX dns_records_e48ee74e;

DROP INDEX dns_records_ee85b622;

DROP INDEX dns_types_name_121df1cb_like;

DROP INDEX dns_views_name_6f6824be_like;

DROP INDEX domains_d9aad70c;

DROP INDEX domains_name_0e99bd93_like;

DROP INDEX feature_requests_e8701ad4;

DROP INDEX guardian_groupobjectpermission_0e939a4f;

DROP INDEX guardian_groupobjectpermission_417f1b1c;

DROP INDEX guardian_groupobjectpermission_8373b171;

DROP INDEX guardian_userobjectpermission_417f1b1c;

DROP INDEX guardian_userobjectpermission_8373b171;

DROP INDEX guardian_userobjectpermission_e8701ad4;

DROP INDEX guest_tickets_9871d3a2;

DROP INDEX guest_tickets_ticket_23fad635_like;

DROP INDEX gul_recent_arp_byaddress_884d9804;

DROP INDEX gul_recent_arp_bymac_884d9804;

DROP INDEX hosts_18232d5b;

DROP INDEX hosts_237dd1f7;

DROP INDEX hosts_d9aad70c;

DROP INDEX hosts_hostname_481ea77e_like;

DROP INDEX users_groups_0e939a4f;

DROP INDEX users_groups_e8701ad4;

DROP INDEX hosts_to_pools_140c1f12;

DROP INDEX hosts_to_pools_d9aad70c;

DROP INDEX hosts_to_pools_ff383e3c;

DROP INDEX leases_140c1f12;

DROP INDEX network_taggednetworks_09a80f33;

DROP INDEX network_taggednetworks_76f094bc;

DROP INDEX networks_237dd1f7;

DROP INDEX networks_94f6f50f;

DROP INDEX networks_d9aad70c;

DROP INDEX networks_to_vlans_1473e96a;

DROP INDEX networks_to_vlans_d9aad70c;

DROP INDEX notifications_006398d5;

DROP INDEX pools_237dd1f7;

DROP INDEX pools_b068931c;

DROP INDEX pools_name_cfabdea7_like;

DROP INDEX shared_networks_d9aad70c;

DROP INDEX shared_networks_name_19cbf1f3_like;

DROP INDEX supermasters_d9aad70c;

DROP INDEX taggit_tag_name_58eb2ed9_like;

DROP INDEX taggit_tag_slug_6be58b2c_like;

DROP INDEX taggit_taggeditem_417f1b1c;

DROP INDEX taggit_taggeditem_76f094bc;

DROP INDEX taggit_taggeditem_af31437c;

DROP INDEX taggit_taggeditem_content_type_id_196cc965_idx;

DROP INDEX user_groupsource_36cd38f4;

DROP INDEX users_36cd38f4;

DROP INDEX users_username_e8658fc8_like;

DROP INDEX users_user_permissions_8373b171;

DROP INDEX users_user_permissions_e8701ad4;

DROP INDEX vlans_d9aad70c;

----DROP TABLE django_admin_log;

----DROP TABLE email_log;

----DROP TABLE users_log;

----DROP SEQUENCE auth_sources_id_seq;
----
----DROP SEQUENCE dhcp_options_id_seq;
----
----DROP SEQUENCE django_admin_log_id_seq;
----
----DROP SEQUENCE dns_types_id_seq;
----
----DROP SEQUENCE email_log_id_seq;
----
CREATE SEQUENCE comments_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE cryptokeys_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE django_site_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE domainmetadata_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE domains_to_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE hosts_to_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE kvp_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE mac_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE networks_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE networks_to_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE notifications_to_hosts_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE pdns_zone_xfer_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE pools_to_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE south_migrationhistory_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE tsigkeys_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE SEQUENCE users_to_groups_id_seq
	START WITH 1
	INCREMENT BY 1
	NO MAXVALUE
	NO MINVALUE
	CACHE 1;

CREATE TABLE comments (
	id integer DEFAULT nextval('comments_id_seq'::regclass) NOT NULL,
	domain_id integer NOT NULL,
	name character varying(255) NOT NULL,
	type character varying(10) NOT NULL,
	modified_at integer NOT NULL,
	account character varying(40) DEFAULT NULL::character varying,
	comment character varying(65535) NOT NULL
);

CREATE TABLE cryptokeys (
	id integer DEFAULT nextval('cryptokeys_id_seq'::regclass) NOT NULL,
	domain_id integer,
	flags integer NOT NULL,
	active boolean,
	content text
);

CREATE TABLE django_site (
	id integer DEFAULT nextval('django_site_id_seq'::regclass) NOT NULL,
	"domain" character varying(100) NOT NULL,
	name character varying(50) NOT NULL
);

CREATE TABLE pdns_zone_xfer (
	id bigint DEFAULT nextval('pdns_zone_xfer_id_seq'::regclass) NOT NULL,
	domain_id integer NOT NULL,
	name character varying(255) NOT NULL,
	type character varying(10) NOT NULL,
	content character varying(255) NOT NULL,
	ttl integer DEFAULT (-1),
	priority integer,
	change_date integer
);

CREATE TABLE domainmetadata (
	id integer DEFAULT nextval('domainmetadata_id_seq'::regclass) NOT NULL,
	domain_id integer,
	kind character varying(32),
	content text
);

CREATE TABLE domains_to_groups (
	id integer DEFAULT nextval('domains_to_groups_id_seq'::regclass) NOT NULL,
	did integer NOT NULL,
	gid integer NOT NULL,
	changed timestamp with time zone DEFAULT now(),
	changed_by integer NOT NULL
);

CREATE TABLE groups (
	id integer DEFAULT nextval('groups_id_seq'::regclass) NOT NULL,
	name text,
	description text,
	changed timestamp with time zone DEFAULT now() NOT NULL,
	changed_by integer NOT NULL
);

CREATE TABLE hosts_to_groups (
	id integer DEFAULT nextval('hosts_to_groups_id_seq'::regclass) NOT NULL,
	mac macaddr NOT NULL,
	gid integer NOT NULL,
	changed timestamp with time zone DEFAULT now(),
	changed_by integer NOT NULL
);

CREATE TABLE internal_auth (
	id integer NOT NULL,
	hash character varying NOT NULL,
	name character varying,
	email character varying,
	changed timestamp with time zone DEFAULT now() NOT NULL,
	changed_by integer NOT NULL
);

CREATE TABLE kvp (
	id integer DEFAULT nextval('kvp_id_seq'::regclass) NOT NULL,
	"key" text NOT NULL,
	"value" text NOT NULL
);

CREATE TABLE mac (
	id integer DEFAULT nextval('mac_id_seq'::regclass) NOT NULL,
	field macaddr
);

CREATE TABLE networks_to_groups (
	id integer DEFAULT nextval('networks_to_groups_id_seq'::regclass) NOT NULL,
	nid pg_catalog.cidr NOT NULL,
	gid integer NOT NULL,
	changed timestamp with time zone DEFAULT now(),
	changed_by integer NOT NULL
);

CREATE TABLE notifications_to_hosts (
	id integer DEFAULT nextval('notifications_to_hosts_id_seq'::regclass) NOT NULL,
	nid integer NOT NULL,
	mac macaddr NOT NULL
);

CREATE TABLE pools_to_groups (
	id integer DEFAULT nextval('pools_to_groups_id_seq'::regclass) NOT NULL,
	pool integer NOT NULL,
	gid integer NOT NULL
);

CREATE TABLE south_migrationhistory (
	id integer DEFAULT nextval('south_migrationhistory_id_seq'::regclass) NOT NULL,
	app_name character varying(255) NOT NULL,
	migration character varying(255) NOT NULL,
	applied timestamp with time zone NOT NULL
);

CREATE TABLE tsigkeys (
	id integer DEFAULT nextval('tsigkeys_id_seq'::regclass) NOT NULL,
	name character varying(255),
	algorithm character varying(50),
	secret character varying(255)
);

CREATE TABLE users_to_groups (
	id integer DEFAULT nextval('users_to_groups_id_seq'::regclass) NOT NULL,
	uid integer NOT NULL,
	gid integer NOT NULL,
	permissions bit(8) NOT NULL,
	changed timestamp with time zone DEFAULT now(),
	changed_by integer NOT NULL,
	host_permissions bit(8) NOT NULL
);

ALTER TABLE addresses
	ALTER COLUMN address TYPE pg_catalog.inet /* TYPE change - table: addresses original: inet new: pg_catalog.inet */,
	ALTER COLUMN reserved SET DEFAULT false,
	ALTER COLUMN reserved DROP NOT NULL,
	ALTER COLUMN network TYPE pg_catalog.cidr /* TYPE change - table: addresses original: cidr new: pg_catalog.cidr */,
	ALTER COLUMN changed SET DEFAULT now();

ALTER TABLE attributes
	ALTER COLUMN structured SET DEFAULT false,
	ALTER COLUMN required SET DEFAULT false,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE freeform_attributes_to_hosts
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE structured_attribute_values
	ALTER COLUMN is_default SET DEFAULT false,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE structured_attributes_to_hosts
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE auth_permission
	ALTER COLUMN name TYPE character varying(50) /* TYPE change - table: auth_permission original: character varying(255) new: character varying(50) */;

ALTER TABLE auth_sources
	ALTER COLUMN id DROP DEFAULT,
	ALTER COLUMN name TYPE character varying /* TYPE change - table: auth_sources original: character varying(255) new: character varying */,
	ALTER COLUMN name DROP NOT NULL;

ALTER TABLE default_pools
	ALTER COLUMN cidr TYPE pg_catalog.cidr /* TYPE change - table: default_pools original: cidr new: pg_catalog.cidr */;

ALTER TABLE dhcp_dns_records
	ALTER COLUMN ip_content TYPE pg_catalog.inet /* TYPE change - table: dhcp_dns_records original: inet new: pg_catalog.inet */,
	ALTER COLUMN ttl SET DEFAULT (-1),
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE dhcp_dns_records
	SET (fillfactor=95);

ALTER TABLE dhcp_groups
	ALTER COLUMN name TYPE character varying(255) /* TYPE change - table: dhcp_groups original: character varying(50) new: character varying(255) */,
	ALTER COLUMN name DROP NOT NULL,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE dhcp_options
	ALTER COLUMN id DROP DEFAULT;

ALTER TABLE dhcp_options_to_dhcp_groups
	ALTER COLUMN changed SET DEFAULT now();

ALTER TABLE disabled
	ALTER COLUMN disabled SET DEFAULT now(),
	ALTER COLUMN disabled DROP NOT NULL;

ALTER TABLE django_content_type
	ADD COLUMN name character varying(100) DEFAULT '';

----ALTER TABLE django_content_type
----	ALTER COLUMN name DROP DEFAULT;

ALTER TABLE dns_records
	ALTER COLUMN ip_content TYPE pg_catalog.inet /* TYPE change - table: dns_records original: inet new: pg_catalog.inet */,
	ALTER COLUMN ttl SET DEFAULT 86400,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE dns_types
	ALTER COLUMN id DROP DEFAULT,
	ALTER COLUMN name DROP NOT NULL,
	ALTER COLUMN min_permissions SET DEFAULT B'11111111'::"bit";

ALTER TABLE domains
	ALTER COLUMN master SET DEFAULT NULL::character varying,
	ALTER COLUMN account SET DEFAULT NULL::character varying,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE expiration_types
	ALTER COLUMN expiration TYPE interval USING (expiration - NOW())::interval /* TYPE change - table: expiration_types original: timestamp with time zone new: interval */,
	ALTER COLUMN expiration DROP NOT NULL;

ALTER TABLE feature_requests
	ALTER COLUMN is_complete SET DEFAULT false;

----ALTER TABLE gul_recent_arp_byaddress
----	ALTER COLUMN mac TYPE macaddr /* TYPE change - table: gul_recent_arp_byaddress original: integer new: macaddr */,
----	ALTER COLUMN mac DROP NOT NULL,
----	ALTER COLUMN address TYPE pg_catalog.inet /* TYPE change - table: gul_recent_arp_byaddress original: inet new: pg_catalog.inet */,
----	ALTER COLUMN address DROP NOT NULL,
----	ALTER COLUMN stopstamp DROP NOT NULL;

----ALTER TABLE gul_recent_arp_bymac
----	ALTER COLUMN mac TYPE macaddr /* TYPE change - table: gul_recent_arp_bymac original: integer new: macaddr */,
----	ALTER COLUMN mac DROP NOT NULL,
----	ALTER COLUMN address TYPE pg_catalog.inet /* TYPE change - table: gul_recent_arp_bymac original: inet new: pg_catalog.inet */,
----	ALTER COLUMN address DROP NOT NULL,
----	ALTER COLUMN stopstamp DROP NOT NULL;

ALTER TABLE hosts
	ALTER COLUMN hostname TYPE character varying /* TYPE change - table: hosts original: character varying(255) new: character varying */,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE hosts_to_pools
	ALTER COLUMN changed SET DEFAULT now();

ALTER TABLE leases
	ALTER COLUMN address TYPE pg_catalog.inet /* TYPE change - table: leases original: inet new: pg_catalog.inet */,
	ALTER COLUMN abandoned SET DEFAULT false,
	ALTER COLUMN server TYPE character varying /* TYPE change - table: leases original: character varying(255) new: character varying */,
	ALTER COLUMN starts SET DEFAULT now();

ALTER TABLE leases
	SET (fillfactor=90);

ALTER TABLE mac_oui
	ALTER COLUMN vendor TYPE character varying /* TYPE change - table: mac_oui original: text new: character varying */;

ALTER TABLE network_ranges
	ALTER COLUMN "range" TYPE pg_catalog.cidr /* TYPE change - table: network_ranges original: cidr new: pg_catalog.cidr */;

ALTER TABLE network_taggednetworks
	ALTER COLUMN content_object_id TYPE pg_catalog.cidr /* TYPE change - table: network_taggednetworks original: cidr new: pg_catalog.cidr */;

ALTER TABLE networks
	ADD COLUMN id integer DEFAULT nextval('networks_id_seq'::regclass) NOT NULL,
	ALTER COLUMN network TYPE pg_catalog.cidr /* TYPE change - table: networks original: cidr new: pg_catalog.cidr */,
	ALTER COLUMN gateway TYPE pg_catalog.inet /* TYPE change - table: networks original: inet new: pg_catalog.inet */,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE networks_to_vlans
	ALTER COLUMN network TYPE pg_catalog.cidr /* TYPE change - table: networks_to_vlans original: cidr new: pg_catalog.cidr */,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE notifications
	ALTER COLUMN notification TYPE interval USING (notification - NOW())::interval /* TYPE change - table: notifications original: date new: interval */,
	ALTER COLUMN notification DROP NOT NULL;

ALTER TABLE permissions
	ALTER COLUMN name DROP NOT NULL,
	ALTER COLUMN description DROP NOT NULL;

ALTER TABLE pools
	ALTER COLUMN name TYPE character varying /* TYPE change - table: pools original: character varying(50) new: character varying */,
	ALTER COLUMN description DROP NOT NULL,
	ALTER COLUMN allow_unknown SET DEFAULT false,
	ALTER COLUMN assignable SET DEFAULT false;

ALTER TABLE shared_networks
	ALTER COLUMN changed SET DEFAULT now();

ALTER TABLE supermasters
	ALTER COLUMN account SET DEFAULT NULL::character varying,
	ALTER COLUMN changed SET DEFAULT now(),
	ALTER COLUMN changed DROP NOT NULL;

ALTER TABLE taggit_taggeditem
	ALTER COLUMN object_id TYPE character varying(255) /* TYPE change - table: taggit_taggeditem original: integer new: character varying(255) */;

ALTER TABLE users
	ALTER COLUMN min_permissions SET DEFAULT B'00000000'::"bit",
	ALTER COLUMN first_name DROP NOT NULL,
	ALTER COLUMN last_name DROP NOT NULL,
	ALTER COLUMN is_active SET DEFAULT true,
	ALTER COLUMN email DROP NOT NULL,
	ALTER COLUMN is_superuser SET DEFAULT false,
	ALTER COLUMN is_staff SET DEFAULT false,
	ALTER COLUMN last_login SET DEFAULT '1969-12-31 17:00:00-07'::timestamp with time zone,
	ALTER COLUMN password SET DEFAULT '!'::character varying,
	ALTER COLUMN date_joined SET DEFAULT '1969-12-31 17:00:00-07'::timestamp with time zone;

ALTER TABLE vlans
	ALTER COLUMN description DROP NOT NULL,
	ALTER COLUMN changed SET DEFAULT now();

ALTER SEQUENCE comments_id_seq
	OWNED BY comments.id;

ALTER SEQUENCE cryptokeys_id_seq
	OWNED BY cryptokeys.id;

ALTER SEQUENCE django_site_id_seq
	OWNED BY django_site.id;

ALTER SEQUENCE domainmetadata_id_seq
	OWNED BY domainmetadata.id;

ALTER SEQUENCE domains_to_groups_id_seq
	OWNED BY domains_to_groups.id;

ALTER SEQUENCE groups_id_seq
	OWNED BY groups.id;

ALTER SEQUENCE hosts_to_groups_id_seq
	OWNED BY hosts_to_groups.id;

ALTER SEQUENCE kvp_id_seq
	OWNED BY kvp.id;

ALTER SEQUENCE mac_id_seq
	OWNED BY mac.id;

ALTER SEQUENCE networks_id_seq
	OWNED BY networks.id;

ALTER SEQUENCE networks_to_groups_id_seq
	OWNED BY networks_to_groups.id;

ALTER SEQUENCE notifications_to_hosts_id_seq
	OWNED BY notifications_to_hosts.id;

ALTER SEQUENCE pdns_zone_xfer_id_seq
	OWNED BY pdns_zone_xfer.id;

ALTER SEQUENCE pools_to_groups_id_seq
	OWNED BY pools_to_groups.id;

ALTER SEQUENCE south_migrationhistory_id_seq
	OWNED BY south_migrationhistory.id;

ALTER SEQUENCE tsigkeys_id_seq
	OWNED BY tsigkeys.id;

ALTER SEQUENCE users_to_groups_id_seq
	OWNED BY users_to_groups.id;

CREATE OR REPLACE FUNCTION array_reverse(anyarray) RETURNS anyarray
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT ARRAY(
    SELECT $1[i]
    FROM generate_subscripts($1,1) AS s(i)
    ORDER BY i DESC
);
$_$;

CREATE OR REPLACE FUNCTION int64_tomacaddr(bigint) RETURNS macaddr
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/macaddr_contrib', 'int64_tomacaddr';

CREATE OR REPLACE FUNCTION macaddr_add(macaddr, bigint) RETURNS macaddr
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/macaddr_contrib', 'macaddr_add';

CREATE OR REPLACE FUNCTION macaddr_toint64(macaddr) RETURNS bigint
    LANGUAGE c IMMUTABLE STRICT
    AS '$libdir/macaddr_contrib', 'macaddr_toint64';

ALTER TABLE comments
	ADD CONSTRAINT comments_pkey PRIMARY KEY (id);

ALTER TABLE cryptokeys
	ADD CONSTRAINT cryptokeys_pkey PRIMARY KEY (id);

ALTER TABLE django_site
	ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);

ALTER TABLE pdns_zone_xfer
	ADD CONSTRAINT pdns_zone_xfer_pkey PRIMARY KEY (id);

ALTER TABLE domainmetadata
	ADD CONSTRAINT domainmetadata_pkey PRIMARY KEY (id);

ALTER TABLE domains_to_groups
	ADD CONSTRAINT domains_to_groups_pkey PRIMARY KEY (id);

ALTER TABLE groups
	ADD CONSTRAINT groups_pkey PRIMARY KEY (id);

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_pkey PRIMARY KEY (id);

ALTER TABLE internal_auth
	ADD CONSTRAINT internal_auth_pkey PRIMARY KEY (id);

ALTER TABLE mac
	ADD CONSTRAINT mac_pkey PRIMARY KEY (id);

----ALTER TABLE networks
----	ADD CONSTRAINT networks_pkey PRIMARY KEY (id);

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_pkey PRIMARY KEY (id);

ALTER TABLE notifications_to_hosts
	ADD CONSTRAINT notifications_to_hosts_pkey PRIMARY KEY (id);

ALTER TABLE pools_to_groups
	ADD CONSTRAINT pools_to_groups_pkey PRIMARY KEY (id);

ALTER TABLE south_migrationhistory
	ADD CONSTRAINT south_migrationhistory_pkey PRIMARY KEY (id);

ALTER TABLE tsigkeys
	ADD CONSTRAINT tsigkeys_pkey PRIMARY KEY (id);

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_pkey PRIMARY KEY (id);

ALTER TABLE addresses
	ADD CONSTRAINT addresses_check CHECK (((((mac IS NULL) AND (pool IS NULL)) OR ((mac IS NULL) AND (reserved IS FALSE))) OR ((pool IS NULL) AND (reserved IS FALSE))));

ALTER TABLE addresses
	ADD CONSTRAINT addresses_check1 CHECK ((address <<= (network)::pg_catalog.inet));

ALTER TABLE addresses
	ADD CONSTRAINT addresses_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE addresses
	ADD CONSTRAINT addresses_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE addresses
	ADD CONSTRAINT addresses_network_fkey FOREIGN KEY (network) REFERENCES networks(network) ON UPDATE CASCADE;

ALTER TABLE addresses
	ADD CONSTRAINT addresses_pool_fkey FOREIGN KEY (pool) REFERENCES pools(id) ON UPDATE CASCADE ON DELETE SET DEFAULT;

ALTER TABLE addresstypes
	ADD CONSTRAINT addresstypes_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES pools(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE addresstypes_ranges
	ADD CONSTRAINT addresstypes_ranges_addresstype_id_networkrange_id_key UNIQUE (addresstype_id, networkrange_id);

ALTER TABLE addresstypes_ranges
	ADD CONSTRAINT addresstype_id_refs_id_149c549e FOREIGN KEY (addresstype_id) REFERENCES addresstypes(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE addresstypes_ranges
	ADD CONSTRAINT addresstypes_ranges_networkrange_id_fkey FOREIGN KEY (networkrange_id) REFERENCES network_ranges(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE admin_tools_dashboard_preferences
	ADD CONSTRAINT admin_tools_dashboard_preferences_user_id_dashboard_id_key UNIQUE (user_id, dashboard_id);

ALTER TABLE admin_tools_dashboard_preferences
	ADD CONSTRAINT admin_tools_dashboard_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE admin_tools_menu_bookmark
	ADD CONSTRAINT admin_tools_menu_bookmark_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE attributes
	ADD CONSTRAINT attributes_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_mac_aid_value_key UNIQUE (mac, aid, value);

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_aid_fkey FOREIGN KEY (aid) REFERENCES attributes(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE structured_attribute_values
	ADD CONSTRAINT structured_attribute_values_aid_value_key UNIQUE (aid, value);

ALTER TABLE structured_attribute_values
	ADD CONSTRAINT structured_attribute_values_aid_fkey FOREIGN KEY (aid) REFERENCES attributes(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE structured_attribute_values
	ADD CONSTRAINT structured_attribute_values_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_mac_avid_key UNIQUE (mac, avid);

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_avid_fkey FOREIGN KEY (avid) REFERENCES structured_attribute_values(id);

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE auth_group_permissions
	ADD CONSTRAINT auth_group_permissions_group_id_permission_id_key UNIQUE (group_id, permission_id);

ALTER TABLE auth_group_permissions
	ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE auth_group_permissions
	ADD CONSTRAINT group_id_refs_id_f4b32aac FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE auth_permission
	ADD CONSTRAINT auth_permission_content_type_id_codename_key UNIQUE (content_type_id, codename);

ALTER TABLE auth_permission
	ADD CONSTRAINT content_type_id_refs_id_d043b34a FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE authtoken_token
	ADD CONSTRAINT authtoken_token_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE comments
	ADD CONSTRAINT c_lowercase_name CHECK (((name)::text = lower((name)::text)));

ALTER TABLE comments
	ADD CONSTRAINT domain_exists FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE;

ALTER TABLE cryptokeys
	ADD CONSTRAINT cryptokeys_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE;

ALTER TABLE default_pools
	ADD CONSTRAINT default_pools_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES pools(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_did_fkey FOREIGN KEY (did) REFERENCES domains(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_ip_content_fkey FOREIGN KEY (ip_content) REFERENCES addresses(address) ON DELETE RESTRICT;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_name_fkey FOREIGN KEY (name) REFERENCES hosts(hostname) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE dhcp_groups
	ADD CONSTRAINT dhcp_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_gid_key UNIQUE (gid, oid, value);

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_gid_fkey FOREIGN KEY (gid) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_oid_fkey FOREIGN KEY (oid) REFERENCES dhcp_options(id) ON DELETE RESTRICT;

ALTER TABLE disabled
	ADD CONSTRAINT disabled_disabled_by_fkey FOREIGN KEY (disabled_by) REFERENCES users(id);

ALTER TABLE django_content_type
	ADD CONSTRAINT django_content_type_app_label_model_key UNIQUE (app_label, model);

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_check CHECK (((((tid = 1) OR (tid = 28)) AND ((ip_content IS NOT NULL) AND (text_content IS NULL))) OR (((tid <> 1) AND (tid <> 28)) AND ((ip_content IS NULL) AND (text_content IS NOT NULL)))));

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_check1 CHECK (((tid <> 5) OR (NOT ((name)::text = (text_content)::text))));

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_did_fkey FOREIGN KEY (did) REFERENCES domains(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_ip_content_fkey FOREIGN KEY (ip_content) REFERENCES addresses(address) ON DELETE RESTRICT;

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_tid_fkey FOREIGN KEY (tid) REFERENCES dns_types(id) ON UPDATE CASCADE;

ALTER TABLE dns_records
	ADD CONSTRAINT dns_records_vid_fkey FOREIGN KEY (vid) REFERENCES dns_views(id) ON DELETE RESTRICT;

ALTER TABLE dns_types
	ADD CONSTRAINT dns_types_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE pdns_zone_xfer
	ADD CONSTRAINT pdns_zone_xfer_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE domainmetadata
	ADD CONSTRAINT domainmetadata_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE;

ALTER TABLE domains
	ADD CONSTRAINT domains_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE domains_to_groups
	ADD CONSTRAINT domains_to_groups_did_key UNIQUE (did, gid);

ALTER TABLE domains_to_groups
	ADD CONSTRAINT domains_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE domains_to_groups
	ADD CONSTRAINT domains_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE expiration_types
	ADD CONSTRAINT expiration_types_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE feature_requests
	ADD CONSTRAINT feature_requests_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE groups
	ADD CONSTRAINT groups_name_key UNIQUE (name);

ALTER TABLE groups
	ADD CONSTRAINT groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE guardian_groupobjectpermission
	ADD CONSTRAINT guardian_groupobjectpermissio_group_id_permission_id_object_key UNIQUE (group_id, permission_id, object_pk);

ALTER TABLE guardian_groupobjectpermission
	ADD CONSTRAINT guardian_groupobjectpermission_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guardian_groupobjectpermission
	ADD CONSTRAINT guardian_groupobjectpermission_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guardian_groupobjectpermission
	ADD CONSTRAINT guardian_groupobjectpermission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guardian_userobjectpermission
	ADD CONSTRAINT guardian_userobjectpermission_user_id_permission_id_object__key UNIQUE (user_id, permission_id, object_pk);

ALTER TABLE guardian_userobjectpermission
	ADD CONSTRAINT guardian_userobjectpermission_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guardian_userobjectpermission
	ADD CONSTRAINT guardian_userobjectpermission_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guardian_userobjectpermission
	ADD CONSTRAINT guardian_userobjectpermission_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE guest_tickets
	ADD CONSTRAINT guest_tickets_check CHECK ((starts < ends));

ALTER TABLE guest_tickets
	ADD CONSTRAINT guest_tickets_uid_fkey FOREIGN KEY (uid) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts
	ADD CONSTRAINT host_length_check CHECK ((char_length((hostname)::text) >= 3));

ALTER TABLE hosts
	ADD CONSTRAINT hosts_hostname_case_check CHECK (((hostname)::text = lower((hostname)::text)));

ALTER TABLE hosts
	ADD CONSTRAINT hosts_address_type_id_fkey FOREIGN KEY (address_type_id) REFERENCES addresstypes(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE hosts
	ADD CONSTRAINT hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE hosts
	ADD CONSTRAINT hosts_dhcp_group_fkey FOREIGN KEY (dhcp_group) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE users_groups
	ADD CONSTRAINT users_groups_user_id_group_id_key UNIQUE (user_id, group_id);

ALTER TABLE users_groups
	ADD CONSTRAINT group_id_refs_id_e06c3832 FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE users_groups
	ADD CONSTRAINT user_id_refs_id_1217de52 FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_mac_key UNIQUE (mac, gid);

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts_to_pools
	ADD CONSTRAINT hosts_to_pools_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE hosts_to_pools
	ADD CONSTRAINT hosts_to_pools_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts_to_pools
	ADD CONSTRAINT hosts_to_pools_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES pools(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE internal_auth
	ADD CONSTRAINT internal_auth_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE internal_auth
	ADD CONSTRAINT internal_auth_id_fkey FOREIGN KEY (id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE leases
	ADD CONSTRAINT leases_check CHECK ((((mac IS NOT NULL) AND (abandoned = false)) OR ((mac IS NULL) AND (abandoned = true))));

ALTER TABLE leases
	ADD CONSTRAINT leases_address_fkey FOREIGN KEY (address) REFERENCES addresses(address) ON DELETE CASCADE;

ALTER TABLE mac_oui
	ADD CONSTRAINT mac_oui_oui_check CHECK ((oui = trunc(oui)));

ALTER TABLE network_taggednetworks
	ADD CONSTRAINT network_taggednetworks_content_object_id_fkey FOREIGN KEY (content_object_id) REFERENCES networks(network) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE network_taggednetworks
	ADD CONSTRAINT network_taggednetworks_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES taggit_tag(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE networks
	ADD CONSTRAINT networks_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE networks
	ADD CONSTRAINT networks_dhcp_group_fkey FOREIGN KEY (dhcp_group) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE networks
	ADD CONSTRAINT networks_shared_network_fkey FOREIGN KEY (shared_network) REFERENCES shared_networks(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_nid_key UNIQUE (nid, gid);

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE networks_to_vlans
	ADD CONSTRAINT networks_to_vlans_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE networks_to_vlans
	ADD CONSTRAINT networks_to_vlans_network_fkey FOREIGN KEY (network) REFERENCES networks(network);

ALTER TABLE networks_to_vlans
	ADD CONSTRAINT networks_to_vlans_vlan_fkey FOREIGN KEY (vlan) REFERENCES vlans(id);

ALTER TABLE notifications
	ADD CONSTRAINT notifications_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE notifications_to_hosts
	ADD CONSTRAINT notifications_to_hosts_nid_fkey FOREIGN KEY (nid) REFERENCES notifications(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pools
	ADD CONSTRAINT pools_dhcp_group_fkey FOREIGN KEY (dhcp_group) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE pools_to_groups
	ADD CONSTRAINT pools_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE pools_to_groups
	ADD CONSTRAINT pools_to_groups_pool_fkey FOREIGN KEY (pool) REFERENCES pools(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE shared_networks
	ADD CONSTRAINT shared_networks_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

ALTER TABLE supermasters
	ADD CONSTRAINT supermasters_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE taggit_taggeditem
	ADD CONSTRAINT taggit_taggeditem_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE taggit_taggeditem
	ADD CONSTRAINT taggit_taggeditem_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES taggit_tag(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE tsigkeys
	ADD CONSTRAINT c_lowercase_name CHECK (((name)::text = lower((name)::text)));

ALTER TABLE user_groupsource
	ADD CONSTRAINT user_groupsource_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE user_groupsource
	ADD CONSTRAINT user_groupsource_source_fkey FOREIGN KEY (source) REFERENCES auth_sources(id);

ALTER TABLE users
	ADD CONSTRAINT users_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE users
	ADD CONSTRAINT users_source_fkey FOREIGN KEY (source) REFERENCES auth_sources(id) ON DELETE RESTRICT;

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_uid_key UNIQUE (uid, gid);

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_host_permissions_fkey FOREIGN KEY (host_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_permissions_fkey FOREIGN KEY (permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE users_to_groups
	ADD CONSTRAINT users_to_groups_uid_fkey FOREIGN KEY (uid) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE users_user_permissions
	ADD CONSTRAINT users_user_permissions_user_id_permission_id_key UNIQUE (user_id, permission_id);

ALTER TABLE users_user_permissions
	ADD CONSTRAINT permission_id_refs_id_98f3dbf4 FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE users_user_permissions
	ADD CONSTRAINT user_id_refs_id_1b5f933e FOREIGN KEY (user_id) REFERENCES users(id) DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE vlans
	ADD CONSTRAINT vlans_id_check CHECK (((id > 0) AND (id < 4096)));

ALTER TABLE vlans
	ADD CONSTRAINT vlans_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id);

CREATE INDEX addresses_changed_by_idx ON addresses USING btree (changed_by);

CREATE INDEX addresses_mac ON addresses USING btree (mac);

CREATE INDEX addresses_network_index ON addresses USING btree (network);

CREATE INDEX addresses_pool_index ON addresses USING btree (pool);

CREATE INDEX addresstypes_ranges_addresstype_id ON addresstypes_ranges USING btree (addresstype_id);

CREATE INDEX addresstypes_ranges_networkrange_id ON addresstypes_ranges USING btree (networkrange_id);

CREATE INDEX admin_tools_dashboard_preferences_user_id ON admin_tools_dashboard_preferences USING btree (user_id);

CREATE INDEX admin_tools_menu_bookmark_user_id ON admin_tools_menu_bookmark USING btree (user_id);

CREATE INDEX freeform_attributes_to_hosts_aid_idx ON freeform_attributes_to_hosts USING btree (aid);

CREATE INDEX freeform_attributes_to_hosts_changed_by_idx ON freeform_attributes_to_hosts USING btree (changed_by);

CREATE INDEX structured_attributes_to_hosts_avid_idx ON structured_attributes_to_hosts USING btree (avid);

CREATE INDEX structured_attributes_to_hosts_changed_by_idx ON structured_attributes_to_hosts USING btree (changed_by);

CREATE INDEX auth_group_name_like ON auth_group USING btree (name varchar_pattern_ops);

CREATE INDEX auth_group_permissions_group_id ON auth_group_permissions USING btree (group_id);

CREATE INDEX auth_group_permissions_permission_id ON auth_group_permissions USING btree (permission_id);

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);

CREATE INDEX authtoken_token_key_like ON authtoken_token USING btree (key varchar_pattern_ops);

CREATE INDEX comments_domain_id_idx ON comments USING btree (domain_id);

CREATE INDEX comments_name_type_idx ON comments USING btree (name, type);

CREATE INDEX comments_order_idx ON comments USING btree (domain_id, modified_at);

CREATE INDEX domainidindex ON cryptokeys USING btree (domain_id);

CREATE INDEX default_pools_pool_id ON default_pools USING btree (pool_id);

CREATE INDEX dhcp_dns_records_did_idx ON dhcp_dns_records USING btree (did);

CREATE INDEX dhcp_dns_records_ip_content_idx ON dhcp_dns_records USING btree (ip_content);

CREATE UNIQUE INDEX dhcp_dns_records_name_key ON dhcp_dns_records USING btree (name);

CREATE INDEX django_session_expire_date ON django_session USING btree (expire_date);

CREATE INDEX django_session_session_key_like ON django_session USING btree (session_key varchar_pattern_ops);

CREATE INDEX dns_records_changed_by_idx ON dns_records USING btree (changed_by);

CREATE INDEX dns_records_ip_content_idx ON dns_records USING btree (ip_content);

CREATE UNIQUE INDEX dns_records_ip_index ON dns_records USING btree (tid, vid, name, ip_content);

CREATE UNIQUE INDEX dns_records_ip_v_index ON dns_records USING btree (tid, name, ip_content) WHERE (vid IS NULL);

CREATE UNIQUE INDEX dns_records_name_key ON dns_records USING btree (name, vid, tid, text_content, ip_content);

CREATE UNIQUE INDEX dns_records_text_index ON dns_records USING btree (tid, vid, name, text_content);

CREATE UNIQUE INDEX dns_records_text_v_index ON dns_records USING btree (tid, name, text_content) WHERE (vid IS NULL);

CREATE UNIQUE INDEX dns_records_unique_cname_index ON dns_records USING btree (name, vid) WHERE (tid = 5);

CREATE UNIQUE INDEX dns_records_unique_cname_v_index ON dns_records USING btree (name) WHERE ((tid = 5) AND (vid IS NULL));

CREATE UNIQUE INDEX dns_records_unique_ptr_index ON dns_records USING btree (name, vid) WHERE (tid = 12);

CREATE UNIQUE INDEX dns_records_unique_ptr_v_index ON dns_records USING btree (name) WHERE ((tid = 12) AND (vid IS NULL));

CREATE INDEX dns_records_vid_idx ON dns_records USING btree (vid);

CREATE INDEX rec_did_index ON dns_records USING btree (did);

CREATE INDEX rec_name_index ON dns_records USING btree (name);

CREATE INDEX rec_text_content_index ON dns_records USING btree (text_content);

CREATE INDEX rec_type_index ON dns_records USING btree (name, tid);

CREATE INDEX dns_types_id_index ON dns_types USING btree (id);

CREATE INDEX pdns_zone_xfer_domain_id_index ON pdns_zone_xfer USING btree (domain_id);

CREATE INDEX pdns_zone_xfer_name_index ON pdns_zone_xfer USING btree (name);

CREATE INDEX pdns_zone_xfer_name_type_index ON pdns_zone_xfer USING btree (name, type);

CREATE INDEX domainidmetaindex ON domainmetadata USING btree (domain_id);

CREATE UNIQUE INDEX name_index ON domains USING btree (name);

CREATE INDEX feature_requests_user_id ON feature_requests USING btree (user_id);

CREATE UNIQUE INDEX groups_name_case_index ON groups USING btree (lower(name));

CREATE INDEX guardian_groupobjectpermission_content_type_id ON guardian_groupobjectpermission USING btree (content_type_id);

CREATE INDEX guardian_groupobjectpermission_group_id ON guardian_groupobjectpermission USING btree (group_id);

CREATE INDEX guardian_groupobjectpermission_permission_id ON guardian_groupobjectpermission USING btree (permission_id);

CREATE INDEX guardian_userobjectpermission_content_type_id ON guardian_userobjectpermission USING btree (content_type_id);

CREATE INDEX guardian_userobjectpermission_permission_id ON guardian_userobjectpermission USING btree (permission_id);

CREATE INDEX guardian_userobjectpermission_user_id ON guardian_userobjectpermission USING btree (user_id);

CREATE INDEX gul_recent_arp_byaddress_address_idx ON gul_recent_arp_byaddress USING btree (address);

CREATE INDEX gul_recent_arp_bymac_mac_idx ON gul_recent_arp_bymac USING btree (mac);

CREATE INDEX hosts_expires_index ON hosts USING btree (expires);

CREATE INDEX hosts_mac_hostname_dhcp_group_index ON hosts USING btree (mac, hostname, description);

CREATE UNIQUE INDEX hosts_mac_uniq ON hosts USING btree (mac);

CREATE INDEX users_groups_group_id ON users_groups USING btree (group_id);

CREATE INDEX users_groups_user_id ON users_groups USING btree (user_id);

CREATE INDEX hosts_to_groups_mac_gid_index ON hosts_to_groups USING btree (mac, gid);

CREATE INDEX hosts_to_pools_mac ON hosts_to_pools USING btree (mac);

CREATE UNIQUE INDEX hosts_to_pools_unique_host_pool_idx ON hosts_to_pools USING btree (mac, pool_id);

CREATE INDEX leases_abandoned_index ON leases USING btree (abandoned);

CREATE INDEX leases_mac_index ON leases USING btree (mac);

CREATE INDEX network_taggednetworks_content_object_id ON network_taggednetworks USING btree (content_object_id);

CREATE INDEX network_taggednetworks_tag_id ON network_taggednetworks USING btree (tag_id);

CREATE INDEX network_dhcp_group_index ON networks USING btree (dhcp_group);

CREATE INDEX network_shared_network_index ON networks USING btree (shared_network);

CREATE UNIQUE INDEX networks_network_uniq ON networks USING btree (network);

CREATE UNIQUE INDEX notifications_to_hosts_mac_nid_index ON notifications_to_hosts USING btree (mac, nid);

CREATE INDEX notifications_to_hosts_nid_idx ON notifications_to_hosts USING btree (nid);

CREATE INDEX ouis_range_index ON ouis USING btree (start, stop);

CREATE INDEX pools_allow_unknown_index ON pools USING btree (allow_unknown);

CREATE INDEX taggit_tag_name_like ON taggit_tag USING btree (name varchar_pattern_ops);

CREATE INDEX taggit_tag_slug_like ON taggit_tag USING btree (slug varchar_pattern_ops);

CREATE INDEX taggit_taggeditem_content_type_id ON taggit_taggeditem USING btree (content_type_id);

CREATE INDEX taggit_taggeditem_object_id ON taggit_taggeditem USING btree (object_id);

CREATE INDEX taggit_taggeditem_object_id_like ON taggit_taggeditem USING btree (object_id varchar_pattern_ops);

CREATE INDEX taggit_taggeditem_tag_id ON taggit_taggeditem USING btree (tag_id);

CREATE UNIQUE INDEX namealgoindex ON tsigkeys USING btree (name, algorithm);

CREATE INDEX user_groupsource_source ON user_groupsource USING btree (source);

CREATE INDEX users_min_permissions ON users USING btree (min_permissions);

CREATE INDEX users_source ON users USING btree (source);

CREATE UNIQUE INDEX users_username_case_index ON users USING btree (lower((username)::text));

CREATE INDEX users_username_like ON users USING btree (username varchar_pattern_ops);

CREATE INDEX users_to_groups_uid_gid_index ON users_to_groups USING btree (uid, gid);

CREATE INDEX users_user_permissions_permission_id ON users_user_permissions USING btree (permission_id);

CREATE INDEX users_user_permissions_user_id ON users_user_permissions USING btree (user_id);

ALTER TABLE addresses CLUSTER ON addresses_pkey;

ALTER TABLE dhcp_dns_records CLUSTER ON dhcp_dns_records_name_key;

ALTER TABLE hosts CLUSTER ON hosts_hostname_key;

ALTER TABLE hosts_to_pools CLUSTER ON hosts_to_pools_mac;

ALTER TABLE leases CLUSTER ON leases_pkey;

ALTER TABLE ouis CLUSTER ON ouis_range_index;

CREATE VIEW attributes_to_hosts AS
	SELECT a.id AS aid,
    a.name,
    a.structured,
    a.required,
    sa2h.mac,
    sa2h.avid,
    sav.value
   FROM ((attributes a
     JOIN structured_attribute_values sav ON ((sav.aid = a.id)))
     JOIN structured_attributes_to_hosts sa2h ON ((sav.id = sa2h.avid)))
UNION
 SELECT a.id AS aid,
    a.name,
    a.structured,
    a.required,
    fa2h.mac,
    NULL::integer AS avid,
    fa2h.value
   FROM (attributes a
     JOIN freeform_attributes_to_hosts fa2h ON ((a.id = fa2h.aid)));

CREATE VIEW records AS
	SELECT dns_records.id,
    dns_records.did AS domain_id,
    dns_records.name,
    dns_types.name AS type,
    dns_records.text_content AS content,
    dns_records.ttl,
    dns_records.priority AS prio,
    (date_part('epoch'::text, dns_records.changed))::integer AS change_date,
    dns_records.vid AS view_id
   FROM (dns_records
     JOIN dns_types ON ((dns_records.tid = dns_types.id)))
  WHERE ((dns_records.tid <> 1) AND (dns_records.tid <> 28))
UNION
 SELECT dns_records.id,
    dns_records.did AS domain_id,
    dns_records.name,
    dns_types.name AS type,
    (host(dns_records.ip_content))::character varying AS content,
    dns_records.ttl,
    dns_records.priority AS prio,
    (date_part('epoch'::text, dns_records.changed))::integer AS change_date,
    dns_records.vid AS view_id
   FROM (dns_records
     JOIN dns_types ON ((dns_records.tid = dns_types.id)))
  WHERE ((dns_records.tid = 1) OR (dns_records.tid = 28))
UNION
 SELECT dhcp_dns_records.id,
    dhcp_dns_records.did AS domain_id,
    dhcp_dns_records.name,
    'A'::character varying AS type,
    (host(dhcp_dns_records.ip_content))::character varying AS content,
    dhcp_dns_records.ttl,
    NULL::integer AS prio,
    (date_part('epoch'::text, dhcp_dns_records.changed))::integer AS change_date,
    NULL::integer AS view_id
   FROM dhcp_dns_records
UNION
 SELECT pdns_zone_xfer.id,
    pdns_zone_xfer.domain_id,
    pdns_zone_xfer.name,
    pdns_zone_xfer.type,
    pdns_zone_xfer.content,
    pdns_zone_xfer.ttl,
    pdns_zone_xfer.priority AS prio,
    pdns_zone_xfer.change_date,
    NULL::integer AS view_id
   FROM pdns_zone_xfer;

COMMIT TRANSACTION;
