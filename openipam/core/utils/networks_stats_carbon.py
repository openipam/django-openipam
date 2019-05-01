from django.db import connection
import socket

available = """count((leases.ends < NOW() AND NOT leases.abandoned) OR (addresses.pool IS NOT NULL AND leases.address IS NULL) OR NULL)"""

query = """SELECT addresses.network,
  extract(epoch from now())::bigint as epoch,
  {available} AS available,
  count(addresses.mac) AS static,
  count(addresses.pool) AS dynamic,
  count(leases.address IS NOT NULL AND NOT leases.abandoned AND leases.ends > NOW() OR NULL) AS leased,
  count(addresses.reserved OR NULL) AS reserved,
  count(leases.abandoned OR NULL) AS abandoned,
  count(leases.ends < now() AND NOT leases.abandoned OR NULL) AS expired,
  count( 1 ) AS total,
  count(leases.address IS NULL AND addresses.pool IS NOT NULL OR NULL) AS unleased,
  CASE WHEN count(addresses.pool) > 0
    THEN {available} / count(addresses.pool)::float
    ELSE 1.0
  END AS available_ratio
FROM addresses LEFT OUTER JOIN leases ON addresses.address = leases.address
GROUP BY addresses.network;
"""

query = query.format(available=available)

query_colnames = [
    "network",
    "epoch",
    "available",
    "static",
    "dynamic",
    "leased",
    "reserved",
    "abandoned",
    "expired",
    "total",
    "unleased",
    "available_ratio",
]


def push_data(carbon_server, carbon_port):
    carbon_s = socket.socket()
    carbon_s.connect((carbon_server, carbon_port))
    cursor = connection.cursor()
    cursor.execute(query)
    counts = cursor.fetchall()
    graphite_data = []
    for count in counts:
        net = count[0]
        net_key = net.replace(".", "-").replace("/", "_")
        timestamp = count[1]
        for i in range(2, len(query_colnames)):
            item_name = query_colnames[i]
            item_value = count[i]
            line = "ipam.leases.%s.%s %s %s" % (
                net_key,
                item_name,
                item_value,
                timestamp,
            )
            graphite_data.append(line)
    carbon_s.sendall("\n".join(graphite_data))
    carbon_s.sendall("\n")
    carbon_s.close()
