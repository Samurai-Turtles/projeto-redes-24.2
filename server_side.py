import socket 
import threading

MAX_FILE_SIZE = 10240
TCP_PORT = 6000
UDP_PORT = 5698

def process_udp_request(data: bytes):
    """
    Processa uma requisição recebida via UDP, interpretando os dados
    recebidos e formatando uma resposta de acordo com o protocolo definido.

    Parameters
    ----------
    data : bytes
        os dados recebidos do cliente, em formato de bytes. Espera-se
        uma string separada por vírgulas, contendo informações do protocolo.

    Returns
    -------
    str
        uma string formatada com a resposta para o cliente. Caso o protocolo
        recebido seja inválido, uma mensagem
        de erro padrão será retornada.
    """

    converted = data.decode('utf-8').split(',')
    converted[-1] = converted[-1].strip()
    out = f'RESPONSE,TCP,{TCP_PORT},{converted[-1]}'    

    if "UDP" in converted:
        out = 'ERROR,PROTOCOLO INVALIDO,,'
    # TODO, check if the target file exists...

    return out

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    
    with conn:
        data = conn.recv(MAX_FILE_SIZE)

        while not data:
            print(data.decode('utf-8'))
            conn.sendall(data)
            data = conn.recv(MAX_FILE_SIZE)
    
    print(f"TCP Client disconnected from {addr}")

def tcp_protocol():
    """
    Cria uma thread para cada cliente que estabelece uma conexão com o servidor.
    """

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('0.0.0.0', TCP_PORT)) # TODO, change to read the config data from an 'ini' file
    tcp_sock.listen(5)

    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_tcp_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

def udp_protocol():
    """
    Inicia o servidor UDP que ficará escutando na porta configurada,
    recebendo mensagens e respondendo conforme a lógica do protocolo.
    """
    print(f"UDP Received listening on port {UDP_PORT}")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', UDP_PORT)) # TODO, change to read the config data from an 'ini' file

    while True:
        data, addr = udp_sock.recvfrom(1024)
        
        if not data:
            continue
        
        print(f"UDP Received from {addr}: {data.decode('utf-8')}")
        client_request = process_udp_request(data)
        udp_sock.sendto(str.encode(client_request), addr)

def init_protocol(method):
    """
    Inicia uma thread que vai executar um método relacionado ao protocolo
    de interesse

    Parameter
    ---------
    method
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
