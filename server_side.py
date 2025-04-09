import socket 
import threading

def tcp_protocol():
    pass    

def udp_protocol():
    pass

def init_protocol(method):
    """
    Inicia uma thread que vai executar um método relacionado ao protocolo
    de interesse

    Parameter
    ---------
    method:
        uma referência ao método relacionado a um método.
    """

    protocol_thread = threading.Thread(target=method)
    protocol_thread.daemon = True
    protocol_thread.start()

def main():
    init_protocol(udp_protocol)
    init_protocol(tcp_protocol)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServidor Encerrado.")


if __name__ == "__main__":
    main()
