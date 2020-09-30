
from UnityManager import UnityManager
from Executor import Executor
import Formatter
from Structure import Structure
from EchoServer import EchoServer


class Manager:
    def __init__(self):
        unityManager = UnityManager()
        executor = Executor()
        structure = Structure()
        if structure.structure is None:
            return
        echoServer = EchoServer()

        echoServer.run_server(unityManager, executor, structure)


manager = Manager()