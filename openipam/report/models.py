from django.conf import settings
from peewee import (
    MySQLDatabase,
    Model,
    IntegerField,
    CharField,
    BigIntegerField,
    PrimaryKeyField,
    DateTimeField,
)
database = MySQLDatabase(
    "librenms",
    **{
        "passwd": settings.AUTH["OBSERVIUM"]["PASSWD"],
        "host": "129.123.1.51",
        "user": settings.AUTH["OBSERVIUM"]["USER"],
    }
)

db_ref_count = 0


def database_connect():
    global db_ref_count
    try:
        if db_ref_count == 0:
            database.connect()
    finally:
        db_ref_count += 1


def database_close():
    global db_ref_count
    try:
        if db_ref_count == 1:
            database.close()
    finally:
        db_ref_count -= 1

    if db_ref_count < 0:
        raise Exception("Database closed when not connected.")


class UnknownField(object):
    pass


class BaseModel(Model):
    class Meta:
        database = database


class Ports(BaseModel):
    deleted = IntegerField()
    detailed = IntegerField()
    device = IntegerField(db_column="device_id")
    disabled = IntegerField()
    ifadminstatus = CharField(db_column="ifAdminStatus", max_length=16, null=True)
    ifalias = CharField(db_column="ifAlias", max_length=255, null=True)
    ifconnectorpresent = CharField(
        db_column="ifConnectorPresent", max_length=12, null=True
    )
    ifdescr = CharField(db_column="ifDescr", max_length=255, null=True)
    ifduplex = CharField(db_column="ifDuplex", max_length=12, null=True)
    ifhardtype = CharField(db_column="ifHardType", max_length=64, null=True)
    ifhighspeed = IntegerField(db_column="ifHighSpeed", null=True)
    ifindex = IntegerField(db_column="ifIndex")
    iflastchange = DateTimeField(db_column="ifLastChange")
    ifmtu = IntegerField(db_column="ifMtu", null=True)
    ifname = CharField(db_column="ifName", max_length=64, null=True)
    ifoperstatus = CharField(db_column="ifOperStatus", max_length=16, null=True)
    ifphysaddress = CharField(db_column="ifPhysAddress", max_length=16, null=True)
    ifpromiscuousmode = CharField(
        db_column="ifPromiscuousMode", max_length=12, null=True
    )
    ifspeed = BigIntegerField(db_column="ifSpeed", null=True)
    iftrunk = CharField(db_column="ifTrunk", max_length=8, null=True)
    iftype = CharField(db_column="ifType", max_length=32, null=True)
    ifvlan = CharField(db_column="ifVlan", max_length=16, null=True)
    ifvrf = IntegerField(db_column="ifVrf", null=True)
    ignore = IntegerField()
    pagpdeviceid = CharField(db_column="pagpDeviceId", max_length=48, null=True)
    pagpethcoperationmode = CharField(
        db_column="pagpEthcOperationMode", max_length=16, null=True
    )
    pagpgroupifindex = IntegerField(db_column="pagpGroupIfIndex", null=True)
    pagpoperationmode = CharField(
        db_column="pagpOperationMode", max_length=32, null=True
    )
    pagppartnerdeviceid = CharField(
        db_column="pagpPartnerDeviceId", max_length=48, null=True
    )
    pagppartnerdevicename = CharField(
        db_column="pagpPartnerDeviceName", max_length=128, null=True
    )
    pagppartnergroupifindex = IntegerField(
        db_column="pagpPartnerGroupIfIndex", null=True
    )
    pagppartnerifindex = IntegerField(db_column="pagpPartnerIfIndex", null=True)
    pagppartnerlearnmethod = CharField(
        db_column="pagpPartnerLearnMethod", max_length=16, null=True
    )
    pagpportstate = CharField(db_column="pagpPortState", max_length=16, null=True)
    # portname = CharField(db_column='portName', max_length=128, null=True)
    # port_64bit = IntegerField(null=True)
    port_descr_circuit = CharField(max_length=255, null=True)
    port_descr_descr = CharField(max_length=255, null=True)
    port_descr_notes = CharField(max_length=255, null=True)
    port_descr_speed = CharField(max_length=32, null=True)
    port_descr_type = CharField(max_length=255, null=True)
    port = PrimaryKeyField(db_column="port_id")
    # port_label = CharField(max_length=255)
    # iferrors_rate = IntegerField(db_column='ifErrors_rate')
    # ifinerrors = BigIntegerField(db_column='ifInErrors')
    # ifinerrors_delta = IntegerField(db_column='ifInErrors_delta')
    # ifinerrors_rate = IntegerField(db_column='ifInErrors_rate')
    ifinoctets = BigIntegerField(db_column="ifInOctets")
    ifinoctets_delta = BigIntegerField(db_column="ifInOctets_delta")
    # ifinoctets_perc = IntegerField(db_column='ifInOctets_perc')
    ifinoctets_rate = BigIntegerField(db_column="ifInOctets_rate")
    # ifinucastpkts = BigIntegerField(db_column='ifInUcastPkts')
    # ifinucastpkts_delta = IntegerField(db_column='ifInUcastPkts_delta')
    # ifinucastpkts_rate = IntegerField(db_column='ifInUcastPkts_rate')
    # ifoctets_rate = BigIntegerField(db_column='ifOctets_rate')
    # ifouterrors = BigIntegerField(db_column='ifOutErrors')
    # ifouterrors_delta = IntegerField(db_column='ifOutErrors_delta')
    # ifouterrors_rate = IntegerField(db_column='ifOutErrors_rate')
    ifoutoctets = BigIntegerField(db_column="ifOutOctets")
    ifoutoctets_delta = BigIntegerField(db_column="ifOutOctets_delta")
    # ifoutoctets_perc = IntegerField(db_column='ifOutOctets_perc')
    ifoutoctets_rate = BigIntegerField(db_column="ifOutOctets_rate")
    # ifoutucastpkts = BigIntegerField(db_column='ifOutUcastPkts')
    # ifoutucastpkts_delta = IntegerField(db_column='ifOutUcastPkts_delta')
    # ifoutucastpkts_rate = IntegerField(db_column='ifOutUcastPkts_rate')
    # ifucastpkts_rate = IntegerField(db_column='ifUcastPkts_rate')
    poll_period = IntegerField()
    poll_time = IntegerField()

    class Meta:
        db_table = "ports"


class Devices(BaseModel):
    device = PrimaryKeyField(db_column="device_id")
    sysname = CharField(db_column="sysName")

    class Meta:
        db_table = "devices"


# class Portsstate(BaseModel):
#     port = PrimaryKeyField(db_column='port_id')

#     class Meta:
#         db_table = 'ports-state'
