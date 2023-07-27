import React, { useEffect, useState } from "react"
import { useApi } from "../hooks/useApi";

export const DnsRecords = () => {
    const api = useApi();
    const [dns, setDns] = useState<any>();
    const getDns = async () => {
        const results = await api.dns.get({page: 1});
        console.log(results);
        setDns(results);
    }
    useEffect(()=>{
        getDns();
    }, [])

    return (
        <div>
            <h1>DNS</h1>
            <pre>{JSON.stringify(dns, null, 2)}</pre>
            
        </div>
    )
}