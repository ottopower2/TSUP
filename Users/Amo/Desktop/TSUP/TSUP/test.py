import pyvisa

rm = pyvisa.ResourceManager('@py')

scope = rm.open_resource(
    "TCPIP::192.168.50.96::INSTR"
)

print(scope.query("*IDN?"))