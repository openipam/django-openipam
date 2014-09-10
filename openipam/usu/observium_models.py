from peewee import *

database = MySQLDatabase('observium', **{'passwd': 'N6pZUgcaPwGNrECPaXGkmM7jDzo7i0F3', 'host': 'observium.usu.edu', 'user': 'openipam'})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

class Accesspoints(BaseModel):
    accesspoint = PrimaryKeyField(db_column='accesspoint_id')
    deleted = IntegerField()
    device = IntegerField(db_column='device_id')
    mac_addr = CharField(max_length=24)
    name = CharField(max_length=255)
    radio_number = IntegerField(null=True)
    type = CharField(max_length=16)

    class Meta:
        db_table = 'accesspoints'

class Accesspointsstate(BaseModel):
    accesspoint = PrimaryKeyField(db_column='accesspoint_id')
    channel = IntegerField()
    interference = IntegerField()
    numactbssid = IntegerField()
    numasoclients = IntegerField()
    nummonbssid = IntegerField()
    nummonclients = IntegerField()
    radioutil = IntegerField()
    txpow = IntegerField()

    class Meta:
        db_table = 'accesspoints-state'

class AlertAssoc(BaseModel):
    alert_assoc = PrimaryKeyField(db_column='alert_assoc_id')
    alert_test = IntegerField(db_column='alert_test_id')
    alerter = CharField(max_length=64, null=True)
    attributes = TextField(null=True)
    count = IntegerField(null=True)
    device_attributes = TextField(null=True)
    enable = IntegerField()
    entity_type = CharField(max_length=64)
    severity = IntegerField(null=True)

    class Meta:
        db_table = 'alert_assoc'

class AlertTable(BaseModel):
    alert_assocs = CharField(max_length=64)
    alert_table = PrimaryKeyField(db_column='alert_table_id')
    alert_test = IntegerField(db_column='alert_test_id')
    delay = IntegerField()
    device = IntegerField(db_column='device_id')
    entity = IntegerField(db_column='entity_id')
    entity_type = CharField(max_length=32)
    ignore_until = IntegerField(null=True)

    class Meta:
        db_table = 'alert_table'

class AlertTablestate(BaseModel):
    alert_status = IntegerField()
    alert_table = PrimaryKeyField(db_column='alert_table_id')
    count = IntegerField()
    has_alerted = IntegerField()
    ignore_until_ok = IntegerField()
    last_alerted = IntegerField()
    last_changed = IntegerField()
    last_checked = IntegerField()
    last_failed = IntegerField()
    last_message = CharField(max_length=128)
    last_recovered = IntegerField()
    state = CharField(max_length=512)
    state_entry = IntegerField()

    class Meta:
        db_table = 'alert_table-state'

class AlertTests(BaseModel):
    alert_message = CharField(max_length=128)
    alert_name = CharField(max_length=64)
    alert_test = PrimaryKeyField(db_column='alert_test_id')
    alerter = CharField(max_length=64, null=True)
    and_ = IntegerField(db_column='and')
    conditions = TextField(null=True)
    delay = IntegerField(null=True)
    enable = IntegerField()
    entity_type = CharField(max_length=64)
    ignore_until = IntegerField(null=True)
    severity = CharField(max_length=256, null=True)

    class Meta:
        db_table = 'alert_tests'

class Alerts(BaseModel):
    alerted = IntegerField()
    device = IntegerField(db_column='device_id')
    importance = IntegerField()
    message = TextField()
    time_logged = DateTimeField()

    class Meta:
        db_table = 'alerts'

class Applications(BaseModel):
    app = PrimaryKeyField(db_column='app_id')
    app_instance = CharField(max_length=128, null=True)
    app_name = CharField(max_length=128, null=True)
    app_state = CharField(max_length=32)
    app_status = CharField(max_length=8)
    app_type = CharField(max_length=64)
    device = IntegerField(db_column='device_id')

    class Meta:
        db_table = 'applications'

class Applicationsstate(BaseModel):
    app_last_polled = IntegerField()
    app_state = CharField(max_length=1024)
    app_status = IntegerField()
    application = IntegerField(db_column='application_id')

    class Meta:
        db_table = 'applications-state'

class Authlog(BaseModel):
    address = TextField()
    datetime = DateTimeField()
    result = TextField()
    user = TextField()

    class Meta:
        db_table = 'authlog'

class Bgppeers(BaseModel):
    astext = CharField(max_length=64)
    bgppeeradminstatus = TextField(db_column='bgpPeerAdminStatus')
    bgppeeridentifier = CharField(db_column='bgpPeerIdentifier', max_length=39)
    bgppeerlocaladdr = CharField(db_column='bgpPeerLocalAddr', max_length=39)
    bgppeerremoteaddr = CharField(db_column='bgpPeerRemoteAddr', max_length=39)
    bgppeerremoteas = IntegerField(db_column='bgpPeerRemoteAs')
    bgppeerstate = TextField(db_column='bgpPeerState')
    bgppeer = PrimaryKeyField(db_column='bgpPeer_id')
    device = IntegerField(db_column='device_id')
    reverse_dns = CharField(max_length=255, null=True)

    class Meta:
        db_table = 'bgpPeers'

class Bgppeersstate(BaseModel):
    bgppeerfsmestablishedtime = IntegerField(db_column='bgpPeerFsmEstablishedTime', null=True)
    bgppeerintotalmessages = IntegerField(db_column='bgpPeerInTotalMessages', null=True)
    bgppeerintotalmessages_delta = IntegerField(db_column='bgpPeerInTotalMessages_delta', null=True)
    bgppeerintotalmessages_rate = IntegerField(db_column='bgpPeerInTotalMessages_rate', null=True)
    bgppeerinupdateelapsedtime = IntegerField(db_column='bgpPeerInUpdateElapsedTime', null=True)
    bgppeerinupdates = IntegerField(db_column='bgpPeerInUpdates', null=True)
    bgppeerinupdates_delta = IntegerField(db_column='bgpPeerInUpdates_delta', null=True)
    bgppeerinupdates_rate = IntegerField(db_column='bgpPeerInUpdates_rate', null=True)
    bgppeerouttotalmessages = IntegerField(db_column='bgpPeerOutTotalMessages', null=True)
    bgppeerouttotalmessages_delta = IntegerField(db_column='bgpPeerOutTotalMessages_delta', null=True)
    bgppeerouttotalmessages_rate = IntegerField(db_column='bgpPeerOutTotalMessages_rate', null=True)
    bgppeeroutupdates = IntegerField(db_column='bgpPeerOutUpdates', null=True)
    bgppeeroutupdates_delta = IntegerField(db_column='bgpPeerOutUpdates_delta', null=True)
    bgppeeroutupdates_rate = IntegerField(db_column='bgpPeerOutUpdates_rate', null=True)
    bgppeer = PrimaryKeyField(db_column='bgpPeer_id')
    bgppeer_polled = IntegerField(db_column='bgpPeer_polled', null=True)

    class Meta:
        db_table = 'bgpPeers-state'

class BgppeersCbgp(BaseModel):
    afi = CharField(max_length=16)
    bgppeerindex = IntegerField(db_column='bgpPeerIndex', null=True)
    bgppeerremoteaddr = CharField(db_column='bgpPeerRemoteAddr', max_length=39)
    cbgp = PrimaryKeyField(db_column='cbgp_id')
    device = IntegerField(db_column='device_id')
    safi = CharField(max_length=16)

    class Meta:
        db_table = 'bgpPeers_cbgp'

class BgppeersCbgpstate(BaseModel):
    acceptedprefixes = IntegerField(db_column='AcceptedPrefixes', null=True)
    advertisedprefixes = IntegerField(db_column='AdvertisedPrefixes', null=True)
    deniedprefixes = IntegerField(db_column='DeniedPrefixes', null=True)
    prefixadminlimit = IntegerField(db_column='PrefixAdminLimit', null=True)
    prefixclearthreshold = IntegerField(db_column='PrefixClearThreshold', null=True)
    prefixthreshold = IntegerField(db_column='PrefixThreshold', null=True)
    suppressedprefixes = IntegerField(db_column='SuppressedPrefixes', null=True)
    withdrawnprefixes = IntegerField(db_column='WithdrawnPrefixes', null=True)
    cbgp = IntegerField(db_column='cbgp_id')

    class Meta:
        db_table = 'bgpPeers_cbgp-state'

class BillData(BaseModel):
    bill = IntegerField(db_column='bill_id')
    delta = BigIntegerField()
    in_delta = BigIntegerField()
    out_delta = BigIntegerField()
    period = IntegerField()
    timestamp = DateTimeField()

    class Meta:
        db_table = 'bill_data'

class BillHistory(BaseModel):
    bill_allowed = BigIntegerField()
    bill_datefrom = DateTimeField()
    bill_dateto = DateTimeField()
    bill_hist = PrimaryKeyField(db_column='bill_hist_id')
    bill = IntegerField(db_column='bill_id')
    bill_overuse = BigIntegerField()
    bill_percent = DecimalField()
    bill_type = TextField()
    bill_used = BigIntegerField()
    dir_95th = CharField(max_length=3)
    pdf = TextField(null=True)
    rate_95th = BigIntegerField()
    rate_95th_in = BigIntegerField()
    rate_95th_out = BigIntegerField()
    rate_average = BigIntegerField()
    rate_average_in = BigIntegerField()
    rate_average_out = BigIntegerField()
    traf_in = BigIntegerField()
    traf_out = BigIntegerField()
    traf_total = BigIntegerField()
    updated = DateTimeField()

    class Meta:
        db_table = 'bill_history'

class BillPerms(BaseModel):
    bill = IntegerField(db_column='bill_id')
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'bill_perms'

class BillPorts(BaseModel):
    bill = IntegerField(db_column='bill_id')
    bill_port_autoadded = IntegerField()
    bill_port_counter_in = BigIntegerField(null=True)
    bill_port_counter_out = BigIntegerField(null=True)
    bill_port_delta_in = BigIntegerField(null=True)
    bill_port_delta_out = BigIntegerField(null=True)
    bill_port_period = IntegerField()
    bill_port_polled = IntegerField()
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'bill_ports'

class Bills(BaseModel):
    bill_autoadded = IntegerField()
    bill_cdr = BigIntegerField(null=True)
    bill_custid = CharField(max_length=64)
    bill_day = IntegerField()
    bill = IntegerField(db_column='bill_id')
    bill_last_calc = DateTimeField()
    bill_name = TextField()
    bill_notes = CharField(max_length=256)
    bill_polled = IntegerField()
    bill_quota = BigIntegerField(null=True)
    bill_ref = CharField(max_length=64)
    bill_type = TextField()
    dir_95th = CharField(max_length=3)
    rate_95th = BigIntegerField()
    rate_95th_in = BigIntegerField()
    rate_95th_out = BigIntegerField()
    rate_average = BigIntegerField()
    rate_average_in = BigIntegerField()
    rate_average_out = BigIntegerField()
    total_data = BigIntegerField()
    total_data_in = BigIntegerField()
    total_data_out = BigIntegerField()

    class Meta:
        db_table = 'bills'

class CefSwitching(BaseModel):
    afi = CharField(max_length=4)
    cef_index = IntegerField()
    cef_path = CharField(max_length=16)
    cef_switching = PrimaryKeyField(db_column='cef_switching_id')
    device = IntegerField(db_column='device_id')
    drop = IntegerField()
    drop_prev = IntegerField()
    entphysicalindex = IntegerField(db_column='entPhysicalIndex')
    punt = IntegerField()
    punt2host = IntegerField()
    punt2host_prev = IntegerField()
    punt_prev = IntegerField()
    updated = IntegerField()
    updated_prev = IntegerField()

    class Meta:
        db_table = 'cef_switching'

class Customers(BaseModel):
    customer = PrimaryKeyField(db_column='customer_id')
    level = IntegerField()
    password = CharField(max_length=32)
    string = CharField(max_length=64)
    username = CharField(max_length=64)

    class Meta:
        db_table = 'customers'

class Dbschema(BaseModel):
    version = IntegerField()

    class Meta:
        db_table = 'dbSchema'

class DeviceGraphs(BaseModel):
    device_graph = PrimaryKeyField(db_column='device_graph_id')
    device = IntegerField(db_column='device_id')
    graph = CharField(max_length=128)

    class Meta:
        db_table = 'device_graphs'

class Devices(BaseModel):
    agent_version = IntegerField(null=True)
    arch = CharField(max_length=8, null=True)
    asset_tag = CharField(max_length=32, null=True)
    authalgo = CharField(max_length=3, null=True)
    authlevel = CharField(max_length=12, null=True)
    authname = CharField(max_length=64, null=True)
    authpass = CharField(max_length=64, null=True)
    bgplocalas = CharField(db_column='bgpLocalAs', max_length=16, null=True)
    community = CharField(max_length=255, null=True)
    cryptoalgo = CharField(max_length=3, null=True)
    cryptopass = CharField(max_length=64, null=True)
    device = PrimaryKeyField(db_column='device_id')
    device_state = TextField(null=True)
    disabled = IntegerField()
    distro = CharField(max_length=32, null=True)
    distro_ver = CharField(max_length=16, null=True)
    features = TextField(null=True)
    hardware = TextField(null=True)
    hostname = CharField(max_length=128)
    icon = CharField(max_length=255, null=True)
    ignore = IntegerField()
    ignore_until = IntegerField(null=True)
    is_discovering = IntegerField()
    is_polling = IntegerField()
    kernel = CharField(max_length=64, null=True)
    last_discovered = DateTimeField(null=True)
    last_discovered_timetaken = FloatField(null=True)
    last_polled = DateTimeField(null=True)
    last_polled_timetaken = FloatField(null=True)
    location = TextField(null=True)
    location_city = CharField(max_length=32, null=True)
    location_country = CharField(max_length=32, null=True)
    location_county = CharField(max_length=32, null=True)
    location_geoapi = CharField(max_length=16, null=True)
    location_lat = CharField(max_length=16, null=True)
    location_lon = CharField(max_length=16, null=True)
    location_state = CharField(max_length=32, null=True)
    os = CharField(max_length=32, null=True)
    port = IntegerField()
    purpose = CharField(max_length=64, null=True)
    retries = IntegerField(null=True)
    serial = CharField(max_length=128, null=True)
    snmpengineid = CharField(db_column='snmpEngineID', max_length=64, null=True)
    snmpver = CharField(max_length=3)
    ssh_port = IntegerField()
    status = IntegerField()
    syscontact = TextField(db_column='sysContact', null=True)
    sysdescr = TextField(db_column='sysDescr', null=True)
    sysname = CharField(db_column='sysName', max_length=128, null=True)
    sysobjectid = CharField(db_column='sysObjectID', max_length=255, null=True)
    timeout = IntegerField(null=True)
    transport = CharField(max_length=4)
    type = CharField(max_length=20, null=True)
    uptime = BigIntegerField(null=True)
    version = TextField(null=True)

    class Meta:
        db_table = 'devices'

class DevicesAttribs(BaseModel):
    attrib = PrimaryKeyField(db_column='attrib_id')
    attrib_type = CharField(max_length=128)
    attrib_value = TextField()
    device = IntegerField(db_column='device_id')
    updated = DateTimeField()

    class Meta:
        db_table = 'devices_attribs'

class DevicesPerftimes(BaseModel):
    device = IntegerField(db_column='device_id')
    duration = FloatField()
    operation = CharField(max_length=32)
    start = IntegerField()

    class Meta:
        db_table = 'devices_perftimes'

class DevicesPerms(BaseModel):
    access_level = IntegerField()
    device = IntegerField(db_column='device_id')
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'devices_perms'

class Entphysical(BaseModel):
    device = IntegerField(db_column='device_id')
    entphysicalalias = CharField(db_column='entPhysicalAlias', max_length=32, null=True)
    entphysicalassetid = CharField(db_column='entPhysicalAssetID', max_length=32, null=True)
    entphysicalclass = TextField(db_column='entPhysicalClass')
    entphysicalcontainedin = IntegerField(db_column='entPhysicalContainedIn')
    entphysicaldescr = TextField(db_column='entPhysicalDescr')
    entphysicalfirmwarerev = CharField(db_column='entPhysicalFirmwareRev', max_length=255, null=True)
    entphysicalhardwarerev = CharField(db_column='entPhysicalHardwareRev', max_length=64, null=True)
    entphysicalindex = IntegerField(db_column='entPhysicalIndex')
    entphysicalisfru = CharField(db_column='entPhysicalIsFRU', max_length=8, null=True)
    entphysicalmfgname = TextField(db_column='entPhysicalMfgName')
    entphysicalmodelname = TextField(db_column='entPhysicalModelName')
    entphysicalname = TextField(db_column='entPhysicalName')
    entphysicalparentrelpos = IntegerField(db_column='entPhysicalParentRelPos')
    entphysicalserialnum = TextField(db_column='entPhysicalSerialNum')
    entphysicalsoftwarerev = CharField(db_column='entPhysicalSoftwareRev', max_length=255, null=True)
    entphysicalvendortype = TextField(db_column='entPhysicalVendorType', null=True)
    entphysical = PrimaryKeyField(db_column='entPhysical_id')
    ifindex = IntegerField(db_column='ifIndex', null=True)

    class Meta:
        db_table = 'entPhysical'

class Entphysicalstate(BaseModel):
    device = IntegerField(db_column='device_id')
    entphysicalindex = CharField(db_column='entPhysicalIndex', max_length=64)
    entphysical_state = PrimaryKeyField(db_column='entPhysical_state_id')
    group = CharField(max_length=64)
    key = CharField(max_length=64)
    subindex = CharField(max_length=64, null=True)
    value = CharField(max_length=255)

    class Meta:
        db_table = 'entPhysical-state'

class Eventlog(BaseModel):
    device = IntegerField(db_column='device_id')
    event = PrimaryKeyField(db_column='event_id')
    message = TextField(null=True)
    reference = CharField(max_length=64)
    timestamp = DateTimeField(null=True)
    type = CharField(max_length=64, null=True)

    class Meta:
        db_table = 'eventlog'

class GraphTypes(BaseModel):
    graph_descr = CharField(max_length=64)
    graph_order = IntegerField()
    graph_section = CharField(max_length=32)
    graph_subtype = CharField(max_length=32)
    graph_type = CharField(max_length=32)

    class Meta:
        db_table = 'graph_types'

class GraphTypesDead(BaseModel):
    graph_descr = CharField(max_length=64)
    graph_order = IntegerField()
    graph_section = CharField(max_length=32)
    graph_subtype = CharField(max_length=32)
    graph_type = CharField(max_length=32)

    class Meta:
        db_table = 'graph_types_dead'

class Hrdevice(BaseModel):
    device = IntegerField(db_column='device_id')
    hrdevicedescr = TextField(db_column='hrDeviceDescr')
    hrdeviceerrors = IntegerField(db_column='hrDeviceErrors')
    hrdeviceindex = IntegerField(db_column='hrDeviceIndex')
    hrdevicestatus = TextField(db_column='hrDeviceStatus')
    hrdevicetype = TextField(db_column='hrDeviceType')
    hrdevice = PrimaryKeyField(db_column='hrDevice_id')
    hrprocessorload = IntegerField(db_column='hrProcessorLoad', null=True)

    class Meta:
        db_table = 'hrDevice'

class IpMac(BaseModel):
    ip_address = CharField(max_length=39)
    ip_version = IntegerField()
    mac_address = CharField(max_length=12)
    mac = PrimaryKeyField(db_column='mac_id')
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ip_mac'

class IpsecTunnels(BaseModel):
    device = IntegerField(db_column='device_id')
    local_addr = CharField(max_length=64)
    local_port = IntegerField()
    peer_addr = CharField(max_length=64)
    peer_port = IntegerField()
    tunnel = PrimaryKeyField(db_column='tunnel_id')
    tunnel_name = CharField(max_length=96)
    tunnel_status = CharField(max_length=11)

    class Meta:
        db_table = 'ipsec_tunnels'

class Ipv4Addresses(BaseModel):
    ipv4_address = CharField(max_length=32)
    ipv4_address = PrimaryKeyField(db_column='ipv4_address_id')
    ipv4_network = CharField(db_column='ipv4_network_id', max_length=32)
    ipv4_prefixlen = IntegerField()
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ipv4_addresses'

class Ipv4Networks(BaseModel):
    ipv4_network = CharField(max_length=64)
    ipv4_network = PrimaryKeyField(db_column='ipv4_network_id')

    class Meta:
        db_table = 'ipv4_networks'

class Ipv6Addresses(BaseModel):
    ipv6_address = CharField(max_length=128)
    ipv6_address = PrimaryKeyField(db_column='ipv6_address_id')
    ipv6_compressed = CharField(max_length=128)
    ipv6_network = CharField(db_column='ipv6_network_id', max_length=128)
    ipv6_origin = CharField(max_length=16)
    ipv6_prefixlen = IntegerField()
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ipv6_addresses'

class Ipv6Networks(BaseModel):
    ipv6_network = CharField(max_length=64)
    ipv6_network = PrimaryKeyField(db_column='ipv6_network_id')

    class Meta:
        db_table = 'ipv6_networks'

class Juniatmvp(BaseModel):
    juniatmvp = PrimaryKeyField(db_column='juniAtmVp_id')
    port = IntegerField(db_column='port_id')
    vp_descr = CharField(max_length=32)
    vp = IntegerField(db_column='vp_id')

    class Meta:
        db_table = 'juniAtmVp'

class Links(BaseModel):
    active = IntegerField()
    local_port = IntegerField(db_column='local_port_id', null=True)
    protocol = CharField(max_length=11, null=True)
    remote_hostname = CharField(max_length=128)
    remote_platform = CharField(max_length=128)
    remote_port = CharField(max_length=128)
    remote_port = IntegerField(db_column='remote_port_id', null=True)
    remote_version = CharField(max_length=256)

    class Meta:
        db_table = 'links'

class LoadbalancerRservers(BaseModel):
    statedescr = CharField(db_column='StateDescr', max_length=64)
    device = IntegerField(db_column='device_id')
    farm = CharField(db_column='farm_id', max_length=128)
    rserver = PrimaryKeyField(db_column='rserver_id')

    class Meta:
        db_table = 'loadbalancer_rservers'

class LoadbalancerVservers(BaseModel):
    classmap = CharField(max_length=128)
    classmap = IntegerField(db_column='classmap_id')
    device = IntegerField(db_column='device_id')
    serverstate = CharField(max_length=64)

    class Meta:
        db_table = 'loadbalancer_vservers'

class MacAccounting(BaseModel):
    device = IntegerField(db_column='device_id')
    ma = PrimaryKeyField(db_column='ma_id')
    mac = CharField(max_length=32)
    port = IntegerField(db_column='port_id')
    vlan = IntegerField(db_column='vlan_id')

    class Meta:
        db_table = 'mac_accounting'

class MacAccountingstate(BaseModel):
    bytes_input = BigIntegerField(null=True)
    bytes_input_delta = BigIntegerField(null=True)
    bytes_input_rate = IntegerField(null=True)
    bytes_output = BigIntegerField(null=True)
    bytes_output_delta = BigIntegerField(null=True)
    bytes_output_rate = IntegerField(null=True)
    ma = PrimaryKeyField(db_column='ma_id')
    pkts_input = BigIntegerField(null=True)
    pkts_input_delta = BigIntegerField(null=True)
    pkts_input_rate = IntegerField(null=True)
    pkts_output = BigIntegerField(null=True)
    pkts_output_delta = BigIntegerField(null=True)
    pkts_output_rate = IntegerField(null=True)
    poll_period = IntegerField(null=True)
    poll_time = IntegerField(null=True)

    class Meta:
        db_table = 'mac_accounting-state'

class Mempools(BaseModel):
    device = IntegerField(db_column='device_id')
    entphysicalindex = IntegerField(db_column='entPhysicalIndex', null=True)
    hrdeviceindex = IntegerField(db_column='hrDeviceIndex', null=True)
    mempool_deleted = IntegerField()
    mempool_descr = CharField(max_length=64)
    mempool_hc = IntegerField()
    mempool = PrimaryKeyField(db_column='mempool_id')
    mempool_index = CharField(max_length=16)
    mempool_mib = CharField(max_length=64, null=True)
    mempool_precision = IntegerField()

    class Meta:
        db_table = 'mempools'

class Mempoolsstate(BaseModel):
    mempool_free = BigIntegerField()
    mempool = PrimaryKeyField(db_column='mempool_id')
    mempool_perc = IntegerField()
    mempool_polled = IntegerField()
    mempool_total = BigIntegerField()
    mempool_used = BigIntegerField()

    class Meta:
        db_table = 'mempools-state'

class MuninPlugins(BaseModel):
    device = IntegerField(db_column='device_id')
    mplug_args = CharField(max_length=512, null=True)
    mplug_category = CharField(max_length=32, null=True)
    mplug_graph = CharField(max_length=1)
    mplug = PrimaryKeyField(db_column='mplug_id')
    mplug_info = TextField(null=True)
    mplug_instance = CharField(max_length=128, null=True)
    mplug_title = CharField(max_length=128, null=True)
    mplug_total = CharField(max_length=1)
    mplug_type = CharField(max_length=128)
    mplug_vlabel = CharField(max_length=128, null=True)

    class Meta:
        db_table = 'munin_plugins'

class MuninPluginsDs(BaseModel):
    ds_cdef = CharField(max_length=255)
    ds_colour = CharField(max_length=32)
    ds_critical = CharField(max_length=32)
    ds_draw = CharField(max_length=64)
    ds_extinfo = TextField()
    ds_graph = CharField(max_length=3)
    ds_info = CharField(max_length=255)
    ds_label = CharField(max_length=64)
    ds_line = CharField(max_length=64)
    ds_max = CharField(max_length=32)
    ds_min = CharField(max_length=32)
    ds_name = CharField(max_length=32)
    ds_negative = CharField(max_length=32)
    ds_stack = TextField()
    ds_sum = TextField()
    ds_type = CharField(max_length=8)
    ds_warning = CharField(max_length=32)
    mplug_ds = PrimaryKeyField(db_column='mplug_ds_id')
    mplug = IntegerField(db_column='mplug_id')

    class Meta:
        db_table = 'munin_plugins_ds'

class NetscalerServices(BaseModel):
    device = IntegerField(db_column='device_id')
    svc_bps_in = IntegerField()
    svc_bps_out = IntegerField()
    svc_clients = IntegerField()
    svc_fullname = CharField(max_length=128, null=True)
    svc = PrimaryKeyField(db_column='svc_id')
    svc_ignore = IntegerField()
    svc_ignore_until = IntegerField()
    svc_ip = CharField(max_length=128)
    svc_label = CharField(max_length=128, null=True)
    svc_name = CharField(max_length=128)
    svc_port = IntegerField()
    svc_req_rate = IntegerField()
    svc_server = IntegerField()
    svc_state = CharField(max_length=32)
    svc_type = CharField(max_length=64)

    class Meta:
        db_table = 'netscaler_services'

class NetscalerServicesVservers(BaseModel):
    device = IntegerField(db_column='device_id')
    service_weight = IntegerField()
    sv = PrimaryKeyField(db_column='sv_id')
    svc_name = CharField(max_length=128)
    vsvr_name = CharField(max_length=128)

    class Meta:
        db_table = 'netscaler_services_vservers'

class NetscalerVservers(BaseModel):
    device = IntegerField(db_column='device_id')
    vsvr_bps_in = IntegerField()
    vsvr_bps_out = IntegerField()
    vsvr_clients = IntegerField()
    vsvr_entitytype = CharField(max_length=32, null=True)
    vsvr_fullname = CharField(max_length=128, null=True)
    vsvr = PrimaryKeyField(db_column='vsvr_id')
    vsvr_ignore = IntegerField()
    vsvr_ignore_until = IntegerField()
    vsvr_ip = CharField(max_length=128)
    vsvr_ipv6 = CharField(max_length=64, null=True)
    vsvr_label = CharField(max_length=128, null=True)
    vsvr_name = CharField(max_length=128)
    vsvr_port = IntegerField()
    vsvr_req_rate = IntegerField()
    vsvr_server = IntegerField()
    vsvr_state = CharField(max_length=32)
    vsvr_type = CharField(max_length=64)

    class Meta:
        db_table = 'netscaler_vservers'

class OspfAreas(BaseModel):
    device = IntegerField(db_column='device_id')
    ospfareabdrrtrcount = IntegerField(db_column='ospfAreaBdrRtrCount')
    ospfareaid = CharField(db_column='ospfAreaId', max_length=32)
    ospfarealsacksumsum = IntegerField(db_column='ospfAreaLsaCksumSum')
    ospfarealsacount = IntegerField(db_column='ospfAreaLsaCount')
    ospfareastatus = CharField(db_column='ospfAreaStatus', max_length=64)
    ospfareasummary = CharField(db_column='ospfAreaSummary', max_length=64)
    ospfasbdrrtrcount = IntegerField(db_column='ospfAsBdrRtrCount')
    ospfauthtype = CharField(db_column='ospfAuthType', max_length=64)
    ospfimportasextern = CharField(db_column='ospfImportAsExtern', max_length=128)
    ospfspfruns = IntegerField(db_column='ospfSpfRuns')

    class Meta:
        db_table = 'ospf_areas'

class OspfInstances(BaseModel):
    device = IntegerField(db_column='device_id')
    ospfasbdrrtrstatus = CharField(db_column='ospfASBdrRtrStatus', max_length=32)
    ospfadminstat = CharField(db_column='ospfAdminStat', max_length=32)
    ospfareabdrrtrstatus = CharField(db_column='ospfAreaBdrRtrStatus', max_length=32)
    ospfdemandextensions = CharField(db_column='ospfDemandExtensions', max_length=32, null=True)
    ospfexitoverflowinterval = IntegerField(db_column='ospfExitOverflowInterval', null=True)
    ospfextlsdblimit = IntegerField(db_column='ospfExtLsdbLimit', null=True)
    ospfexternlsacksumsum = IntegerField(db_column='ospfExternLsaCksumSum')
    ospfexternlsacount = IntegerField(db_column='ospfExternLsaCount')
    ospfmulticastextensions = IntegerField(db_column='ospfMulticastExtensions', null=True)
    ospforiginatenewlsas = IntegerField(db_column='ospfOriginateNewLsas')
    ospfrouterid = CharField(db_column='ospfRouterId', max_length=32)
    ospfrxnewlsas = IntegerField(db_column='ospfRxNewLsas')
    ospftossupport = CharField(db_column='ospfTOSSupport', max_length=32)
    ospfversionnumber = CharField(db_column='ospfVersionNumber', max_length=32)
    ospf_instance = IntegerField(db_column='ospf_instance_id')

    class Meta:
        db_table = 'ospf_instances'

class OspfNbrs(BaseModel):
    device = IntegerField(db_column='device_id')
    ospfnbmanbrpermanence = CharField(db_column='ospfNbmaNbrPermanence', max_length=32)
    ospfnbmanbrstatus = CharField(db_column='ospfNbmaNbrStatus', max_length=32)
    ospfnbraddresslessindex = IntegerField(db_column='ospfNbrAddressLessIndex')
    ospfnbrevents = IntegerField(db_column='ospfNbrEvents')
    ospfnbrhellosuppressed = CharField(db_column='ospfNbrHelloSuppressed', max_length=32)
    ospfnbripaddr = CharField(db_column='ospfNbrIpAddr', max_length=32)
    ospfnbrlsretransqlen = IntegerField(db_column='ospfNbrLsRetransQLen')
    ospfnbroptions = IntegerField(db_column='ospfNbrOptions')
    ospfnbrpriority = IntegerField(db_column='ospfNbrPriority')
    ospfnbrrtrid = CharField(db_column='ospfNbrRtrId', max_length=32)
    ospfnbrstate = CharField(db_column='ospfNbrState', max_length=32)
    ospf_nbr = CharField(db_column='ospf_nbr_id', max_length=32)
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ospf_nbrs'

class OspfPorts(BaseModel):
    device = IntegerField(db_column='device_id')
    ospfaddresslessif = IntegerField(db_column='ospfAddressLessIf')
    ospfifadminstat = CharField(db_column='ospfIfAdminStat', max_length=32, null=True)
    ospfifareaid = CharField(db_column='ospfIfAreaId', max_length=32)
    ospfifauthkey = CharField(db_column='ospfIfAuthKey', max_length=128, null=True)
    ospfifauthtype = CharField(db_column='ospfIfAuthType', max_length=32, null=True)
    ospfifbackupdesignatedrouter = CharField(db_column='ospfIfBackupDesignatedRouter', max_length=32, null=True)
    ospfifdemand = CharField(db_column='ospfIfDemand', max_length=32, null=True)
    ospfifdesignatedrouter = CharField(db_column='ospfIfDesignatedRouter', max_length=32, null=True)
    ospfifevents = IntegerField(db_column='ospfIfEvents', null=True)
    ospfifhellointerval = IntegerField(db_column='ospfIfHelloInterval', null=True)
    ospfifipaddress = CharField(db_column='ospfIfIpAddress', max_length=32)
    ospfifmulticastforwarding = CharField(db_column='ospfIfMulticastForwarding', max_length=32, null=True)
    ospfifpollinterval = IntegerField(db_column='ospfIfPollInterval', null=True)
    ospfifretransinterval = IntegerField(db_column='ospfIfRetransInterval', null=True)
    ospfifrtrdeadinterval = IntegerField(db_column='ospfIfRtrDeadInterval', null=True)
    ospfifrtrpriority = IntegerField(db_column='ospfIfRtrPriority', null=True)
    ospfifstate = CharField(db_column='ospfIfState', max_length=32, null=True)
    ospfifstatus = CharField(db_column='ospfIfStatus', max_length=32, null=True)
    ospfiftransitdelay = IntegerField(db_column='ospfIfTransitDelay', null=True)
    ospfiftype = CharField(db_column='ospfIfType', max_length=32, null=True)
    ospf_port = CharField(db_column='ospf_port_id', max_length=32)
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ospf_ports'

class Packages(BaseModel):
    arch = CharField(max_length=16)
    build = CharField(max_length=64)
    device = IntegerField(db_column='device_id')
    manager = CharField(max_length=16)
    name = CharField(max_length=64)
    pkg = PrimaryKeyField(db_column='pkg_id')
    size = BigIntegerField(null=True)
    status = IntegerField()
    version = CharField(max_length=64)

    class Meta:
        db_table = 'packages'

class PerfTimes(BaseModel):
    devices = IntegerField()
    doing = CharField(max_length=64)
    duration = FloatField()
    start = IntegerField()
    type = CharField(max_length=8)

    class Meta:
        db_table = 'perf_times'

class Ports(BaseModel):
    deleted = IntegerField()
    detailed = IntegerField()
    device = IntegerField(db_column='device_id')
    disabled = IntegerField()
    ifadminstatus = CharField(db_column='ifAdminStatus', max_length=16, null=True)
    ifalias = CharField(db_column='ifAlias', max_length=255, null=True)
    ifconnectorpresent = CharField(db_column='ifConnectorPresent', max_length=12, null=True)
    ifdescr = CharField(db_column='ifDescr', max_length=255, null=True)
    ifduplex = CharField(db_column='ifDuplex', max_length=12, null=True)
    ifhardtype = CharField(db_column='ifHardType', max_length=64, null=True)
    ifhighspeed = IntegerField(db_column='ifHighSpeed', null=True)
    ifindex = IntegerField(db_column='ifIndex')
    iflastchange = DateTimeField(db_column='ifLastChange')
    ifmtu = IntegerField(db_column='ifMtu', null=True)
    ifname = CharField(db_column='ifName', max_length=64, null=True)
    ifoperstatus = CharField(db_column='ifOperStatus', max_length=16, null=True)
    ifphysaddress = CharField(db_column='ifPhysAddress', max_length=16, null=True)
    ifpromiscuousmode = CharField(db_column='ifPromiscuousMode', max_length=12, null=True)
    ifspeed = BigIntegerField(db_column='ifSpeed', null=True)
    iftrunk = CharField(db_column='ifTrunk', max_length=8, null=True)
    iftype = CharField(db_column='ifType', max_length=32, null=True)
    ifvlan = CharField(db_column='ifVlan', max_length=16, null=True)
    ifvrf = IntegerField(db_column='ifVrf', null=True)
    ignore = IntegerField()
    pagpdeviceid = CharField(db_column='pagpDeviceId', max_length=48, null=True)
    pagpethcoperationmode = CharField(db_column='pagpEthcOperationMode', max_length=16, null=True)
    pagpgroupifindex = IntegerField(db_column='pagpGroupIfIndex', null=True)
    pagpoperationmode = CharField(db_column='pagpOperationMode', max_length=32, null=True)
    pagppartnerdeviceid = CharField(db_column='pagpPartnerDeviceId', max_length=48, null=True)
    pagppartnerdevicename = CharField(db_column='pagpPartnerDeviceName', max_length=128, null=True)
    pagppartnergroupifindex = IntegerField(db_column='pagpPartnerGroupIfIndex', null=True)
    pagppartnerifindex = IntegerField(db_column='pagpPartnerIfIndex', null=True)
    pagppartnerlearnmethod = CharField(db_column='pagpPartnerLearnMethod', max_length=16, null=True)
    pagpportstate = CharField(db_column='pagpPortState', max_length=16, null=True)
    portname = CharField(db_column='portName', max_length=128, null=True)
    port_64bit = IntegerField(null=True)
    port_descr_circuit = CharField(max_length=255, null=True)
    port_descr_descr = CharField(max_length=255, null=True)
    port_descr_notes = CharField(max_length=255, null=True)
    port_descr_speed = CharField(max_length=32, null=True)
    port_descr_type = CharField(max_length=255, null=True)
    port = PrimaryKeyField(db_column='port_id')
    port_label = CharField(max_length=255)

    class Meta:
        db_table = 'ports'

class Portsstate(BaseModel):
    iferrors_rate = IntegerField(db_column='ifErrors_rate')
    ifinerrors = BigIntegerField(db_column='ifInErrors')
    ifinerrors_delta = IntegerField(db_column='ifInErrors_delta')
    ifinerrors_rate = IntegerField(db_column='ifInErrors_rate')
    ifinoctets = BigIntegerField(db_column='ifInOctets')
    ifinoctets_delta = BigIntegerField(db_column='ifInOctets_delta')
    ifinoctets_perc = IntegerField(db_column='ifInOctets_perc')
    ifinoctets_rate = BigIntegerField(db_column='ifInOctets_rate')
    ifinucastpkts = BigIntegerField(db_column='ifInUcastPkts')
    ifinucastpkts_delta = IntegerField(db_column='ifInUcastPkts_delta')
    ifinucastpkts_rate = IntegerField(db_column='ifInUcastPkts_rate')
    ifoctets_rate = BigIntegerField(db_column='ifOctets_rate')
    ifouterrors = BigIntegerField(db_column='ifOutErrors')
    ifouterrors_delta = IntegerField(db_column='ifOutErrors_delta')
    ifouterrors_rate = IntegerField(db_column='ifOutErrors_rate')
    ifoutoctets = BigIntegerField(db_column='ifOutOctets')
    ifoutoctets_delta = BigIntegerField(db_column='ifOutOctets_delta')
    ifoutoctets_perc = IntegerField(db_column='ifOutOctets_perc')
    ifoutoctets_rate = BigIntegerField(db_column='ifOutOctets_rate')
    ifoutucastpkts = BigIntegerField(db_column='ifOutUcastPkts')
    ifoutucastpkts_delta = IntegerField(db_column='ifOutUcastPkts_delta')
    ifoutucastpkts_rate = IntegerField(db_column='ifOutUcastPkts_rate')
    ifucastpkts_rate = IntegerField(db_column='ifUcastPkts_rate')
    poll_period = IntegerField()
    poll_time = IntegerField()
    port = PrimaryKeyField(db_column='port_id')

    class Meta:
        db_table = 'ports-state'

class PortsAdsl(BaseModel):
    adslatucchancurrtxrate = IntegerField(db_column='adslAtucChanCurrTxRate')
    adslatuccurratn = DecimalField(db_column='adslAtucCurrAtn')
    adslatuccurrattainablerate = IntegerField(db_column='adslAtucCurrAttainableRate')
    adslatuccurroutputpwr = DecimalField(db_column='adslAtucCurrOutputPwr')
    adslatuccurrsnrmgn = DecimalField(db_column='adslAtucCurrSnrMgn')
    adslatucinvvendorid = CharField(db_column='adslAtucInvVendorID', max_length=8)
    adslatucinvversionnumber = CharField(db_column='adslAtucInvVersionNumber', max_length=8)
    adslaturchancurrtxrate = IntegerField(db_column='adslAturChanCurrTxRate')
    adslaturcurratn = DecimalField(db_column='adslAturCurrAtn')
    adslaturcurrattainablerate = IntegerField(db_column='adslAturCurrAttainableRate')
    adslaturcurroutputpwr = DecimalField(db_column='adslAturCurrOutputPwr')
    adslaturcurrsnrmgn = DecimalField(db_column='adslAturCurrSnrMgn')
    adslaturinvserialnumber = CharField(db_column='adslAturInvSerialNumber', max_length=8)
    adslaturinvvendorid = CharField(db_column='adslAturInvVendorID', max_length=8)
    adslaturinvversionnumber = CharField(db_column='adslAturInvVersionNumber', max_length=8)
    adsllinecoding = CharField(db_column='adslLineCoding', max_length=8)
    adsllinetype = CharField(db_column='adslLineType', max_length=16)
    port_adsl_updated = DateTimeField()
    port = IntegerField(db_column='port_id')

    class Meta:
        db_table = 'ports_adsl'

class PortsPerms(BaseModel):
    access_level = IntegerField()
    port = IntegerField(db_column='port_id')
    user = IntegerField(db_column='user_id')

    class Meta:
        db_table = 'ports_perms'

class PortsStack(BaseModel):
    device = IntegerField(db_column='device_id')
    ifstackstatus = CharField(db_column='ifStackStatus', max_length=32)
    port_id_high = IntegerField()
    port_id_low = IntegerField()

    class Meta:
        db_table = 'ports_stack'

class PortsVlans(BaseModel):
    baseport = IntegerField()
    cost = IntegerField()
    device = IntegerField(db_column='device_id')
    port = IntegerField(db_column='port_id')
    port_vlan = PrimaryKeyField(db_column='port_vlan_id')
    priority = BigIntegerField()
    state = CharField(max_length=16)
    vlan = IntegerField()

    class Meta:
        db_table = 'ports_vlans'

class Processors(BaseModel):
    device = IntegerField(db_column='device_id')
    entphysicalindex = IntegerField(db_column='entPhysicalIndex', null=True)
    hrdeviceindex = IntegerField(db_column='hrDeviceIndex', null=True)
    processor_descr = CharField(max_length=64)
    processor = PrimaryKeyField(db_column='processor_id')
    processor_index = CharField(max_length=32)
    processor_oid = CharField(max_length=128)
    processor_precision = IntegerField()
    processor_type = CharField(max_length=16)

    class Meta:
        db_table = 'processors'

class Processorsstate(BaseModel):
    processor = PrimaryKeyField(db_column='processor_id')
    processor_polled = IntegerField()
    processor_usage = IntegerField()

    class Meta:
        db_table = 'processors-state'

class Pseudowires(BaseModel):
    cpwoid = IntegerField(db_column='cpwOid')
    cpwvcid = IntegerField(db_column='cpwVcID')
    device = IntegerField(db_column='device_id')
    peer_addr = CharField(max_length=128)
    peer_device = IntegerField(db_column='peer_device_id', null=True)
    peer_ldp = CharField(db_column='peer_ldp_id', max_length=32, null=True)
    port = IntegerField(db_column='port_id')
    pseudowire = PrimaryKeyField(db_column='pseudowire_id')
    pw_descr = CharField(max_length=128)
    pw_local_mtu = IntegerField()
    pw_peer_mtu = IntegerField()
    pw_psntype = CharField(max_length=32)
    pw_type = CharField(max_length=32)

    class Meta:
        db_table = 'pseudowires'

class Sensors(BaseModel):
    device = IntegerField(db_column='device_id')
    entphysicalindex = CharField(db_column='entPhysicalIndex', max_length=16, null=True)
    entphysicalindex_measured = CharField(db_column='entPhysicalIndex_measured', max_length=16, null=True)
    measured_class = CharField(max_length=32, null=True)
    measured_entity = CharField(max_length=32, null=True)
    poller_type = CharField(max_length=5)
    sensor_class = CharField(max_length=64)
    sensor_custom_limit = IntegerField()
    sensor_deleted = IntegerField()
    sensor_descr = CharField(max_length=255, null=True)
    sensor_disable = IntegerField()
    sensor_divisor = IntegerField()
    sensor = PrimaryKeyField(db_column='sensor_id')
    sensor_ignore = IntegerField()
    sensor_index = CharField(max_length=64, null=True)
    sensor_limit = FloatField(null=True)
    sensor_limit_low = FloatField(null=True)
    sensor_limit_low_warn = FloatField(null=True)
    sensor_limit_warn = FloatField(null=True)
    sensor_multiplier = IntegerField()
    sensor_oid = CharField(max_length=255)
    sensor_type = CharField(max_length=255)

    class Meta:
        db_table = 'sensors'

class Sensorsstate(BaseModel):
    sensor = PrimaryKeyField(db_column='sensor_id')
    sensor_polled = IntegerField()
    sensor_value = FloatField(null=True)

    class Meta:
        db_table = 'sensors-state'

class Services(BaseModel):
    device = IntegerField(db_column='device_id')
    service_changed = IntegerField()
    service_checked = IntegerField()
    service_desc = TextField()
    service_disabled = IntegerField()
    service = PrimaryKeyField(db_column='service_id')
    service_ignore = IntegerField()
    service_ip = TextField()
    service_message = TextField()
    service_param = TextField()
    service_status = IntegerField()
    service_type = CharField(max_length=16)

    class Meta:
        db_table = 'services'

class Slas(BaseModel):
    deleted = IntegerField()
    device = IntegerField(db_column='device_id')
    owner = CharField(max_length=255)
    rtt_type = CharField(max_length=16)
    sla = PrimaryKeyField(db_column='sla_id')
    sla_nr = IntegerField()
    status = IntegerField()
    tag = CharField(max_length=255)

    class Meta:
        db_table = 'slas'

class Storage(BaseModel):
    device = IntegerField(db_column='device_id')
    storage_deleted = IntegerField()
    storage_descr = TextField()
    storage_hc = IntegerField()
    storage = PrimaryKeyField(db_column='storage_id')
    storage_index = IntegerField()
    storage_mib = CharField(max_length=64, null=True)
    storage_type = CharField(max_length=32, null=True)

    class Meta:
        db_table = 'storage'

class Storagestate(BaseModel):
    storage_free = BigIntegerField()
    storage = PrimaryKeyField(db_column='storage_id')
    storage_perc = IntegerField()
    storage_polled = IntegerField()
    storage_size = BigIntegerField()
    storage_units = IntegerField()
    storage_used = BigIntegerField()

    class Meta:
        db_table = 'storage-state'

class Syslog(BaseModel):
    device = IntegerField(db_column='device_id', null=True)
    facility = CharField(max_length=10, null=True)
    level = IntegerField()
    msg = TextField(null=True)
    priority = IntegerField()
    program = CharField(max_length=32, null=True)
    seq = BigIntegerField(primary_key=True)
    tag = CharField(max_length=10, null=True)
    timestamp = DateTimeField()

    class Meta:
        db_table = 'syslog'

class Toner(BaseModel):
    device = IntegerField(db_column='device_id')
    toner_capacity = IntegerField()
    toner_capacity_oid = CharField(max_length=64, null=True)
    toner_current = IntegerField()
    toner_descr = CharField(max_length=32)
    toner = PrimaryKeyField(db_column='toner_id')
    toner_index = IntegerField()
    toner_oid = CharField(max_length=64)
    toner_type = CharField(max_length=64)

    class Meta:
        db_table = 'toner'

class UcdDiskio(BaseModel):
    device = IntegerField(db_column='device_id')
    diskio_descr = CharField(max_length=32)
    diskio = PrimaryKeyField(db_column='diskio_id')
    diskio_index = IntegerField()

    class Meta:
        db_table = 'ucd_diskio'

class UcdDiskiostate(BaseModel):
    diskionreadx = IntegerField(db_column='diskIONReadX')
    diskionreadx_rate = IntegerField(db_column='diskIONReadX_rate')
    diskionwrittenx = IntegerField(db_column='diskIONWrittenX')
    diskionwrittenx_rate = IntegerField(db_column='diskIONWrittenX_rate')
    diskioreads = IntegerField(db_column='diskIOReads')
    diskioreads_rate = IntegerField(db_column='diskIOReads_rate')
    diskiowrites = IntegerField(db_column='diskIOWrites')
    diskiowrites_rate = IntegerField(db_column='diskIOWrites_rate')
    diskio = PrimaryKeyField(db_column='diskio_id')
    diskio_polled = IntegerField()

    class Meta:
        db_table = 'ucd_diskio-state'

class Users(BaseModel):
    can_modify_passwd = IntegerField()
    descr = CharField(max_length=30)
    email = CharField(max_length=64)
    level = IntegerField()
    password = CharField(max_length=34, null=True)
    realname = CharField(max_length=64)
    user = PrimaryKeyField(db_column='user_id')
    user_options = TextField(null=True)
    username = CharField(max_length=30)

    class Meta:
        db_table = 'users'

class UsersCkeys(BaseModel):
    expire = IntegerField()
    user_ckey = CharField(max_length=32)
    user_ckey = PrimaryKeyField(db_column='user_ckey_id')
    user_encpass = CharField(max_length=64)
    user_uniq = CharField(max_length=32)
    username = CharField(max_length=30)

    class Meta:
        db_table = 'users_ckeys'

class UsersPrefs(BaseModel):
    pref = CharField(max_length=32)
    pref = PrimaryKeyField(db_column='pref_id')
    updated = DateTimeField()
    user = IntegerField(db_column='user_id')
    value = CharField(max_length=128)

    class Meta:
        db_table = 'users_prefs'

class Vlans(BaseModel):
    device = IntegerField(db_column='device_id', null=True)
    vlan_domain = IntegerField(null=True)
    vlan = PrimaryKeyField(db_column='vlan_id')
    vlan_mtu = IntegerField(null=True)
    vlan_name = CharField(max_length=32, null=True)
    vlan_status = CharField(max_length=16)
    vlan_type = CharField(max_length=16, null=True)
    vlan_vlan = IntegerField(null=True)

    class Meta:
        db_table = 'vlans'

class VlansFdb(BaseModel):
    device = IntegerField(db_column='device_id')
    fdb_status = CharField(max_length=32)
    mac_address = CharField(max_length=32)
    port = IntegerField(db_column='port_id')
    vlan = IntegerField(db_column='vlan_id')

    class Meta:
        db_table = 'vlans_fdb'

class Vminfo(BaseModel):
    device = IntegerField(db_column='device_id')
    vm_type = CharField(max_length=16)
    vmwvmconfigfile = CharField(db_column='vmwVmConfigFile', max_length=255, null=True)
    vmwvmcpus = IntegerField(db_column='vmwVmCpus')
    vmwvmdisplayname = CharField(db_column='vmwVmDisplayName', max_length=128)
    vmwvmguestos = CharField(db_column='vmwVmGuestOS', max_length=128)
    vmwvmgueststate = CharField(db_column='vmwVmGuestState', max_length=16, null=True)
    vmwvmmemsize = IntegerField(db_column='vmwVmMemSize')
    vmwvmstate = CharField(db_column='vmwVmState', max_length=128)
    vmwvmuuid = CharField(db_column='vmwVmUUID', max_length=64, null=True)
    vmwvmvmid = IntegerField(db_column='vmwVmVMID')

    class Meta:
        db_table = 'vminfo'

class Vrfs(BaseModel):
    device = IntegerField(db_column='device_id')
    mplsvpnvrfdescription = TextField(db_column='mplsVpnVrfDescription')
    mplsvpnvrfroutedistinguisher = CharField(db_column='mplsVpnVrfRouteDistinguisher', max_length=128, null=True)
    vrf = PrimaryKeyField(db_column='vrf_id')
    vrf_name = CharField(max_length=128, null=True)
    vrf_oid = CharField(max_length=256)

    class Meta:
        db_table = 'vrfs'

