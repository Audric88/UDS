import can
import udsoncan
from udsoncan.connections import PythonIsoTpConnection
from udsoncan.client import Client
import isotp

# IsoTP parameters
isotp_params = {
   'stmin' : 32,
   'blocksize' : 8,
   'wftmax' : 0,
   'tx_data_length' : 8,
   'tx_data_min_length' : None,
   'tx_padding' : 0,
   'rx_flowcontrol_timeout' : 1000,
   'rx_consecutive_frame_timeout' : 1000,
   'squash_stmin_requirement' : False,
   'max_frame_size' : 4095
}

# List of authorized requests
# These are all UDS services available in the udsoncan library.
authorized_requests = [
    udsoncan.services.DiagnosticSessionControl,
    udsoncan.services.ECUReset,
    udsoncan.services.SecurityAccess,
    udsoncan.services.CommunicationControl,
    udsoncan.services.TesterPresent,
    udsoncan.services.AccessTimingParameter,
    udsoncan.services.SecuredDataTransmission,
    udsoncan.services.ControlDTCSetting,
    udsoncan.services.ResponseOnEvent,
    udsoncan.services.LinkControl,
    udsoncan.services.ReadDataByIdentifier,
    udsoncan.services.ReadMemoryByAddress,
    udsoncan.services.ReadScalingDataByIdentifier,
    udsoncan.services.ReadDataByPeriodicIdentifier,
    udsoncan.services.DynamicallyDefineDataIdentifier,
    udsoncan.services.WriteDataByIdentifier,
    udsoncan.services.WriteMemoryByAddress,
    udsoncan.services.ClearDiagnosticInformation,
    udsoncan.services.ReadDTCInformation,
    udsoncan.services.InputOutputControlByIdentifier,
    udsoncan.services.RoutineControl,
    udsoncan.services.RequestDownload,
    udsoncan.services.RequestUpload,
    udsoncan.services.TransferData,
    udsoncan.services.RequestTransferExit,
    # ... add other services as necessary ...
]

# List of IDs
id_list = range(0xfff)

# Dictionary to store results
results = {}

for tx_id in id_list:
    try:
        bus = can.interface.Bus(channel='can0', bustype='socketcan')
        tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=tx_id, rxid=0x123)
        stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)
        conn = PythonIsoTpConnection(stack)
        with Client(conn, request_timeout=0.05) as client:
            for request in authorized_requests:
                try:
                    response = request(client)
                    if response.service_data is not None:
                        results[(tx_id, request)] = True
                        print(f'Authorized request with data field: {request.__name__} with tx_id: {tx_id}')
                    else:
                        print(f'Authorized request without data field: {request.__name__} with tx_id: {tx_id}')
                except udsoncan.exceptions.NegativeResponseException as e:
                    if e.response.code_name != 'serviceNotSupported':
                        results[(tx_id, request)] = False
                except:
                    pass
    except:
        pass

