import pybcapclient.bcapclient as bcapclient    # Denso library for Cobotta access

host = '10.50.12.87'
port = 5007
timeout = 2000

try:
    # Connection processing of tcp communication
    client = bcapclient.BCAPClient(host, port, timeout)

    # start b_cap Service
    client.service_start("")

    # set Parameter
    Name = ""
    Provider = "CaoProv.DENSO.VRC"
    Machine = host
    Option = ""

    # Connect to RC8 (RC8(VRC)provider)
    RC8 = client.controller_connect(Name, Provider, Machine, Option)

    print("Cobotta connected")
except:
    print("can't connect to Cobotta")