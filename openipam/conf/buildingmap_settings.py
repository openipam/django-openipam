import copy


def generate_building_config():
    from openipam.report.models import database_connect, database_close

    database_connect()
    config = False

    try:
        config = _generate_building_config()
    finally:
        database_close()

    return config


def _generate_building_config():
    from openipam.report.models import Ports, Devices

    building_config = {"data": {}, "circuits": {}}
    name = abbrev = building_code = None

    devs = {}

    ports = Ports.select(Ports).where(
        (Ports.deleted == False)
        & (
            Ports.ifalias.regexp(
                r"^[A-Z][A-Za-z0-9, &()\-]+/[A-Z][A-Z0-9 \-]*/\d+[a-z\-]*$"
            )
        )
        & (Ports.ifadminstatus == "up")
    )

    for port in ports:
        combined_key = None
        if not port.device in devs:
            full_sysname = Devices.get(Devices.device == port.device).sysname
            devs[port.device] = full_sysname.split(".")[0].replace("-logan", "").upper()

        portDev = devs[port.device]
        data_key = "{0}-{1}"
        name, abbrev, building_code = port.ifalias.split("/")

        if not abbrev:
            abbrev = "".join(name.split(" "))

        devSubName = portDev.split("-")[0]
        # Check if device name is of the format *-A or *-B
        if "-A" in portDev or "-B" in portDev and portDev[-2] == "-":
            combined_key = data_key.format(building_code, devSubName + "-AB")

        if not combined_key in building_config["data"]:
            building_config["data"][combined_key] = {"id": []}

        if not building_code in building_config["circuits"]:
            building_config["circuits"][building_code] = {
                "abbrevName": abbrev,
                "buildingName": name,
                "buildingNum": building_code,
                "connections": [],
            }

        if "(" in name:
            building_config["circuits"][building_code]["remote"] = True
            portDev = "UPLINKS"
            abbrev = name.split("(")[1].split(")")[0].replace(" ", "")
            building_config["circuits"][building_code]["abbrevName"] = abbrev

        if not portDev in building_config["circuits"][building_code]["connections"]:
            building_config["circuits"][building_code]["connections"].append(portDev)

        if combined_key:
            building_config["data"][combined_key]["id"].append(port.port)
            if (
                not (devSubName + "-AB")
                in building_config["circuits"][building_code]["connections"]
            ):
                building_config["circuits"][building_code]["connections"].append(
                    devSubName + "-AB"
                )

        data_key = data_key.format(building_code, portDev)

        building_config["data"][data_key] = {"id": [port.port]}

    for circuit in building_config["circuits"]:
        building_config["circuits"][circuit]["connections"].sort()

    return building_config


LOCAL_BUILDINGMAP_DATA = {
    # 'data': building_conf['data'],
    "config": {
        "mapName": "Utah State University",
        "acronym": "USU",
        "logo": "",
        "updateInterval": 30,
        "linkStyle": {"maxWidth": 10, "minWidth": 5},
        "utilizationColors": {
            "100": "#ff0000",
            "90": "#ff0000",
            "80": "#ff0f00",
            "70": "#ff5f00",
            "60": "#ff7f00",
            "50": "#ffbf00",
            "40": "#ffff00",
            "30": "#dfef00",
            "25": "#bfdf00",
            "20": "#9fcf00",
            "15": "#7fbf00",
            "10": "#5faf00",
            "5": "#3f9f00",
            "2": "#1f8f00",
            "1": "#006600",
            "0": "#333333",
            "-1": "blue",
        },
        "nodes": {},
        "links": {},
        "buildings": True,
        "circuitsContainer": {
            "coords": [10, 10],
            "height": 1050,
            "width": 1980,
            "scale": "scale(.64)",
        },
        "utilizationURL": "/api/reports/weathermap/?format=json&buildings=true",
    }
}
