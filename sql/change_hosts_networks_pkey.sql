-- Drop constraints
ALTER TABLE "addresses" DROP CONSTRAINT "addresses_mac_fkey";
ALTER TABLE "dhcp_dns_records" DROP CONSTRAINT "dhcp_dns_records_name_fkey";
ALTER TABLE "dns_records" DROP CONSTRAINT "dns_records_mac_fkey";
ALTER TABLE "freeform_attributes_to_hosts" DROP CONSTRAINT "freeform_attributes_to_hosts_mac_fkey";
ALTER TABLE "hosts_to_pools" DROP CONSTRAINT "hosts_to_pools_mac_fkey";
ALTER TABLE "structured_attributes_to_hosts" DROP CONSTRAINT "structured_attributes_to_hosts_mac_fkey";

ALTER TABLE "addresses" DROP CONSTRAINT "addresses_network_fkey";
ALTER TABLE "network_taggednetworks" DROP CONSTRAINT "network_taggednetworks_content_object_id_fkey";
ALTER TABLE "networks_to_vlans" DROP CONSTRAINT "networks_to_vlans_network_fkey";


-- Do the foo we actually wanted to do
ALTER TABLE hosts_log ADD id INTEGER DEFAULT NULL;
ALTER TABLE hosts DROP CONSTRAINT hosts_pkey;
CREATE UNIQUE INDEX hosts_mac_uniq ON hosts(mac);
ALTER TABLE hosts ADD id SERIAL PRIMARY KEY;

ALTER TABLE networks_log ADD id INTEGER DEFAULT NULL;
ALTER TABLE networks DROP CONSTRAINT networks_pkey;
CREATE UNIQUE INDEX networks_network_uniq ON networks(network);
ALTER TABLE networks ADD id SERIAL PRIMARY KEY;

-- Re-create constraints
ALTER TABLE "addresses" ADD CONSTRAINT "addresses_mac_fkey" FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE "dhcp_dns_records" ADD CONSTRAINT "dhcp_dns_records_name_fkey" FOREIGN KEY (name) REFERENCES hosts(hostname) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE "dns_records" ADD CONSTRAINT "dns_records_mac_fkey" FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE "freeform_attributes_to_hosts" ADD CONSTRAINT "freeform_attributes_to_hosts_mac_fkey" FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE "hosts_to_pools" ADD CONSTRAINT "hosts_to_pools_mac_fkey" FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE "structured_attributes_to_hosts" ADD CONSTRAINT "structured_attributes_to_hosts_mac_fkey" FOREIGN KEY (mac) REFERENCES hosts(mac) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE "addresses" ADD CONSTRAINT "addresses_network_fkey" FOREIGN KEY (network) REFERENCES networks(network) ON UPDATE CASCADE;
ALTER TABLE "network_taggednetworks" ADD CONSTRAINT "network_taggednetworks_content_object_id_fkey" FOREIGN KEY (content_object_id) REFERENCES networks(network) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "networks_to_vlans" ADD CONSTRAINT "networks_to_vlans_network_fkey" FOREIGN KEY (network) REFERENCES networks(network);


