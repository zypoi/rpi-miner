from gpiozero import DigitalOutputDevice
import socket
import json
from time import sleep


class Miner(DigitalOutputDevice):
    
    def __init__(self, pin, addr, port, hashrate):
        """ Initialize miner info

        :param pin: int, gpio pin number on raspberry pi
        :parm addr: str, IP address of miner
        :param port: int, API port of ethminer
        :param hashrate: int, expected hashrate of the miner
        """
        DigitalOutputDevice.__init__(self, pin=pin)
        self.miner_addr = addr
        self.miner_port = port
        self.miner_pin = pin
        self.miner_hashrate = hashrate

    def boot(self):
        """Close the relay connected to the raspberry pi for 1s
        to power on the miner, equals to press the power button
        on a computer
        """
        self.on()
        sleep(1)
        self.off()

    def poweroff(self):
        """Close the relay connected to the raspberry pi for 5s
        to power off the miner
        """
        self.on()
        sleep(5)
        self.off()

    def getstatus(self):
        """Get the status of the miner
        
        :return int: 0, normal
                     1, API connection failed
                     2, Reported hashrate less than 90% of the expected hashrate
        """

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.miner_addr, self.miner_port))
        except socket.error:
            return 1
        dict_getstatus = {"id": "17", "jsonrpc": "2.0", "method": "miner_getstat1"}
        s.send(json.dumps(dict_getstatus) + "\n")
        try:
            resp = json.loads(s.recv(1024))
        except ValueError:
            return 1

        list_hashrate_per_card = resp["result"][3].split(";")
        total_hashrate = 0
        for each in list_hashrate_per_card:
            total_hashrate = total_hashrate + int(each)

        total_hashrate = total_hashrate / 1000.0

        if total_hashrate < self.miner_hashrate * 0.7:
            return 2
        else:
            return 0
