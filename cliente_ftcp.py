import socket
from sys import argv

MAX_FILE_SIZE = 10240
SERVER_IP = "127.0.0.1"
UDP_PORT = 5698  # Alterar posteriormente


def request_file_over_udp(filename: str) -> str:
    """
    Esse passo é dividido em duas etapas:

    1. Cliente solicita, via UDP, a transferência de um arquivo
    2. Servidor responde conforme a validade da requisição
        - Se a requisição for válida, retorna a porta do servidor TCP e o arquivo solicitado
        - Caso contrário, retorna uma mensagem de erro, conforme o problema ocorrido
          (e.g. arquivo inexistente)
    """

    server_address = (SERVER_IP, UDP_PORT)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    request_msg = f"REQUEST,TCP,{filename}"

    udp_socket.sendto(request_msg.encode("utf-8"), server_address)
    data, _ = udp_socket.recvfrom(1024)

    decoded_data = data.decode("utf-8")

    print(decoded_data)
    return decoded_data


def download_file_over_tcp(filename: str, response: str):
    """
    Este passo é dividido em quatro etapas:

    1. Cliente estabelece conexão com o servidor TCP
    2. Cliente solicita o arquivo para transferência
    3. Servidor transfere o arquivo solicitado
    4. Cliente verifica o tamanho da arquivo e retorna um ACK para o servidor
    """
    # Estabelecimento de Conexão
    split_response = response.split(",")
    tcp_port = int(split_response[-2])

    server_address = (SERVER_IP, tcp_port)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(server_address)
    print(f"Connected to server at {SERVER_IP}:{tcp_port}")

    # Solicitação do Arquivo
    file_request = f"get,{filename}"
    tcp_socket.sendall(file_request.encode("utf-8"))

    # Envio dos Dados
    response = tcp_socket.recv(MAX_FILE_SIZE)

    # Confirmação pelo Cliente (ACK)
    num_bytes = MAX_FILE_SIZE # TODO: somehow calculate the file size
    ack = f"ftcp_ack,{num_bytes}"
    tcp_socket.sendall(ack.encode("utf-8"))

    # Encerramento da Conexão
    tcp_socket.close()


if __name__ == "__main__":
    requested_file = argv[1] # TODO: add argument amount validation?
    response = request_file_over_udp(requested_file)
    download_file_over_tcp(requested_file, response)
