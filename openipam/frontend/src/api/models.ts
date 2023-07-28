import * as datatypes from "./datatypes";
import { RequestGenerator, HttpMethod } from "./request";

export class Host {
  private requestFunctions: {
    [key: string]: (data?: { [key: string]: any }) => Promise<any>;
  } = {};

  constructor(data: datatypes.HostData.GetData) {
    // copy all properties from data to this
    Object.assign(this, data);
  }

  public async getAddresses(): Promise<datatypes.AddressData[]> {
    if (!this.requestFunctions.getAddresses) {
      this.requestFunctions.getAddresses = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/addresses/`
      );
    }
    return this.requestFunctions.getAddresses();
  }

  public async getLeases(): Promise<datatypes.LeaseData[]> {
    if (!this.requestFunctions.getLeases) {
      this.requestFunctions.getLeases = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/leases/`
      );
    }
    return this.requestFunctions.getLeases();
  }

  public async getUsers(): Promise<string[]> {
    if (!this.requestFunctions.getUsers) {
      this.requestFunctions.getUsers = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/users/`
      );
    }
    return this.requestFunctions.getUsers();
  }

  public async getGroups(): Promise<string[]> {
    if (!this.requestFunctions.getGroups) {
      this.requestFunctions.getGroups = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/groups/`
      );
    }
    return this.requestFunctions.getGroups();
  }

  public async getAttributes(): Promise<{ [key: string]: string }> {
    if (!this.requestFunctions.getAttributes) {
      this.requestFunctions.getAttributes = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/attributes/`
      );
    }
    return this.requestFunctions.getAttributes();
  }

  public async getDisabled(): Promise<datatypes.DisabledHostData> {
    if (!this.requestFunctions.getDisabled) {
      this.requestFunctions.getDisabled = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/disabled/`
      );
    }
    return this.requestFunctions.getDisabled();
  }

  public async addAddress(
    address: string,
    hostname: string
  ): Promise<datatypes.AddressData[]> {
    if (!this.requestFunctions.addAddress) {
      this.requestFunctions.addAddress = RequestGenerator(
        HttpMethod.POST,
        `/api/hosts/${this.mac}/addresses/`
      );
    }
    // Validate address
    const addressOctets = address.split(".");
    if (addressOctets.length !== 4) {
      throw new Error("Invalid address");
    }
    addressOctets.forEach((octet) => {
      const octetNum = parseInt(octet);
      if (octetNum < 0 || octetNum > 255) {
        throw new Error("Invalid address");
      }
    });
    // Validate hostname is a FQDN
    const hostnameParts = hostname.split(".");
    if (hostnameParts.length < 2) {
      throw new Error("Invalid hostname");
    }
    if (!hostnameParts.every((part) => /^[a-z0-9]+[-a-z0-9]*$/i.test(part))) {
      throw new Error("Invalid hostname");
    }
    return this.requestFunctions.addAddress({ address, hostname });
  }

  public async removeAddress(
    address: string
  ): Promise<datatypes.AddressData[]> {
    if (!this.requestFunctions[`removeAddress_${address}`]) {
      this.requestFunctions[`removeAddress_${address}`] = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/addresses/${address}/`
      );
    }
    return this.requestFunctions.removeAddress();
  }

  public async disable(reason: string): Promise<void> {
    if (!this.requestFunctions.disable) {
      this.requestFunctions.disable = RequestGenerator(
        HttpMethod.POST,
        `/api/hosts/${this.mac}/disabled/`
      );
    }
    return this.requestFunctions.disable({ reason });
  }

  public async enable(): Promise<void> {
    if (!this.requestFunctions.enable) {
      this.requestFunctions.enable = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/disabled/`
      );
    }
    return this.requestFunctions.enable();
  }

  public async addUser(user: string): Promise<string[]> {
    if (!this.requestFunctions.addUser) {
      this.requestFunctions.addUser = RequestGenerator(
        HttpMethod.POST,
        `/api/hosts/${this.mac}/users/`
      );
    }
    return this.requestFunctions.addUser({ username: user });
  }

  public async removeUser(user: string): Promise<string[]> {
    if (!this.requestFunctions[`removeUser_${user}`]) {
      this.requestFunctions[`removeUser_${user}`] = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/users/${user}/`
      );
    }
    return this.requestFunctions[`removeUser_${user}`]();
  }

  public async addGroups(groups: string[]): Promise<string[]> {
    if (!this.requestFunctions.addGroups) {
      this.requestFunctions.addGroups = RequestGenerator(
        HttpMethod.POST,
        `/api/hosts/${this.mac}/groups/`
      );
    }
    return this.requestFunctions.addGroups(groups);
  }

  public async removeGroup(group: string): Promise<string[]> {
    if (!this.requestFunctions[`removeGroup_${group}`]) {
      this.requestFunctions[`removeGroup_${group}`] = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/groups/${group}/`
      );
    }
    return this.requestFunctions[`removeGroup_${group}`]();
  }

  public async setAttributes(attributes: {
    [key: string]: string;
  }): Promise<{ [key: string]: string }> {
    if (!this.requestFunctions.setAttribute) {
      this.requestFunctions.setAttribute = RequestGenerator(
        HttpMethod.POST,
        `/api/hosts/${this.mac}/attributes/`
      );
    }
    return this.requestFunctions.setAttribute(attributes);
  }

  public async clearAttributes(): Promise<void> {
    if (!this.requestFunctions.clearAttributes) {
      this.requestFunctions.clearAttributes = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/attributes/`
      );
    }
    return this.requestFunctions.clearAttributes();
  }

  public async refresh(): Promise<void> {
    if (!this.requestFunctions.refresh) {
      this.requestFunctions.refresh = RequestGenerator(
        HttpMethod.GET,
        `/api/hosts/${this.mac}/`
      );
    }
    const data = await this.requestFunctions.refresh();
    // Update all properties
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        this[key] = data[key];
      }
    }
  }

  public async deleteHost(): Promise<void> {
    if (!this.requestFunctions.deleteHost) {
      this.requestFunctions.deleteHost = RequestGenerator(
        HttpMethod.DELETE,
        `/api/hosts/${this.mac}/`
      );
    }
    return this.requestFunctions.deleteHost();
  }
}
