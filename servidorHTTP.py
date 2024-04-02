import socket
import os

# Definindo o endereço IP do host
SERVER_HOST = ""
# Definindo o número da porta em que o servidor irá escutar pelas requisições HTTP
SERVER_PORT = 8080
# Tamanho máximo do buffer de dados recebidos em uma única transmissão TCP
BUFFER_SIZE = 4096

# Vamos criar o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vamos setar a opção de reutilizar sockets já abertos
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Atrela o socket ao endereço da máquina e ao número de porta definido
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Coloca o socket para escutar por conexões
server_socket.listen(1)

# Mensagem inicial do servidor
print("Servidor em execução...")
print("Escutando por conexões na porta %s" % SERVER_PORT)

# Função para lidar com solicitações GET
def handle_get_request(filename):
    try:
        # Abrir o arquivo e ler seu conteúdo
        with open("htdocs" + filename, 'r') as file:
            content = file.read()
            return "HTTP/1.1 200 OK\n\n" + content
    except FileNotFoundError:
        return "HTTP/1.1 404 NOT FOUND\n\n<h1>ERROR 404!<br>File Not Found!</h1>"

# Função para lidar com solicitações PUT
def handle_put_request(filename, data):
    try:
        # Escrever os dados recebidos no arquivo especificado
        with open("htdocs" + filename, 'w') as file:
            file.write(data)
        return "HTTP/1.1 200 OK\n\nFile successfully updated"
    except Exception as e:
        return "HTTP/1.1 500 INTERNAL SERVER ERROR\n\n<h1>Error: {}</h1>".format(str(e))

# Loop principal para receber conexões
while True:
    # Espera por conexões
    client_connection, client_address = server_socket.accept()

    # Pega a solicitação do cliente
    request = client_connection.recv(BUFFER_SIZE).decode()

    # Verifica se a request possui algum conteúdo (pois alguns navegadores ficam periodicamente enviando alguma string vazia)
    if request:
        # Imprime a solicitação do cliente
        print(request)
        
        # Analisa a solicitação HTTP
        headers = request.split("\n")
        # Pega o método e o nome do arquivo sendo solicitado
        method, filename = headers[0].split()[:2]

        # Verifica qual método está sendo usado e chama a função correspondente
        if method == "GET":
            response = handle_get_request(filename)
        elif method == "PUT":
            # Extrai os dados do corpo da requisição
            _, _, data = request.partition("\r\n\r\n")
            response = handle_put_request(filename, data)
        else:
            response = "HTTP/1.1 405 METHOD NOT ALLOWED\n\n<h1>Error 405!<br>Method Not Allowed!</h1>"

        # Envia a resposta HTTP
        client_connection.sendall(response.encode())

        # Fecha a conexão com o cliente
        client_connection.close()

# Fecha o socket do servidor
server_socket.close()
