import subprocess

class Test:
    def __init__(self) -> None:
        self.privatekey = subprocess.getoutput('wg genkey')
        self.pubkey = subprocess.getoutput(f'echo {self.privatekey} | wg pubkey')

a = Test()
print(a.privatekey)
print(a.pubkey)
