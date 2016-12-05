ALTER TABLE addresses
	ADD CONSTRAINT addresses_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE addresses
	ADD CONSTRAINT addresses_network_fkey FOREIGN KEY (network) REFERENCES networks(network) ON UPDATE CASCADE;

ALTER TABLE addresses
	ADD CONSTRAINT addresses_pool_fkey FOREIGN KEY (pool) REFERENCES pools(id) ON UPDATE CASCADE ON DELETE SET DEFAULT;

ALTER TABLE attributes
	ADD CONSTRAINT attributes_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_aid_fkey FOREIGN KEY (aid) REFERENCES attributes(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE freeform_attributes_to_hosts
	ADD CONSTRAINT freeform_attributes_to_hosts_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE structured_attribute_values
	ADD CONSTRAINT structured_attribute_values_aid_fkey FOREIGN KEY (aid) REFERENCES attributes(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE structured_attribute_values
	ADD CONSTRAINT structured_attribute_values_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE structured_attributes_to_hosts
	ADD CONSTRAINT structured_attributes_to_hosts_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE comments
	ADD CONSTRAINT domain_exists FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE;

ALTER TABLE cryptokeys
	ADD CONSTRAINT cryptokeys_domain_id_fkey FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_did_fkey FOREIGN KEY (did) REFERENCES domains(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_ip_content_fkey FOREIGN KEY (ip_content) REFERENCES addresses(address) ON DELETE RESTRICT;

ALTER TABLE dhcp_dns_records
	ADD CONSTRAINT dhcp_dns_records_name_fkey FOREIGN KEY (name) REFERENCES hosts(hostname) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE dhcp_groups
	ADD CONSTRAINT dhcp_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_gid_fkey FOREIGN KEY (gid) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE dhcp_options_to_dhcp_groups
	ADD CONSTRAINT dhcp_options_to_dhcp_groups_oid_fkey FOREIGN KEY (oid) REFERENCES dhcp_options(id) ON DELETE RESTRICT;

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
	ADD CONSTRAINT domains_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE domains_to_groups
	ADD CONSTRAINT domains_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE expiration_types
	ADD CONSTRAINT expiration_types_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE guest_tickets
	ADD CONSTRAINT guest_tickets_uid_fkey FOREIGN KEY (uid) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts
	ADD CONSTRAINT hosts_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE hosts
	ADD CONSTRAINT hosts_dhcp_group_fkey FOREIGN KEY (dhcp_group) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE hosts_to_groups
	ADD CONSTRAINT hosts_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts_to_pools
	ADD CONSTRAINT hosts_to_pools_mac_fkey FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE hosts_to_pools
	ADD CONSTRAINT hosts_to_pools_pool_id_fkey FOREIGN KEY (pool_id) REFERENCES pools(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE internal_auth
	ADD CONSTRAINT internal_auth_id_fkey FOREIGN KEY (id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE leases
	ADD CONSTRAINT leases_address_fkey FOREIGN KEY (address) REFERENCES addresses(address) ON DELETE CASCADE;

ALTER TABLE networks
	ADD CONSTRAINT networks_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE networks
	ADD CONSTRAINT networks_dhcp_group_fkey FOREIGN KEY (dhcp_group) REFERENCES dhcp_groups(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE networks
	ADD CONSTRAINT networks_shared_network_fkey FOREIGN KEY (shared_network) REFERENCES shared_networks(id) ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE networks_to_groups
	ADD CONSTRAINT networks_to_groups_gid_fkey FOREIGN KEY (gid) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE;

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

ALTER TABLE supermasters
	ADD CONSTRAINT supermasters_changed_by_fkey FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE users
	ADD CONSTRAINT users_min_permissions_fkey FOREIGN KEY (min_permissions) REFERENCES permissions(id) ON DELETE RESTRICT;

ALTER TABLE users
	ADD CONSTRAINT users_source_fkey FOREIGN KEY (source) REFERENCES auth_sources(id) ON DELETE RESTRICT;

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

