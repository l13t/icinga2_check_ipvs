# icinga2_check_ipvs
Check for ldirectord/ipvs

```bash
usage: check_ipvs.py [-h] [--proto PROTO] [--service SERVICE] [--sudo]

Check for ldirectord/ipvs

optional arguments:
  -h, --help         show this help message and exit
  --proto PROTO      Set protocol for service (tcp, udp)
  --service SERVICE  Specify service name (It should be specified like
                     <ip_address>:<port>)
  --sudo             Use SUDO to get information

Written 2016, Dmytro Prokhorenkov
```
