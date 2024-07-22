import socket
import threading

import random, json, time

class Server:
    def __init__(self):
        self.host = "localhost"
        self.port = 1234
        self.clients = []


        self.server_infos = {
            "fruit-position":[],
            "other-players":{}
        }
        
        self.configs = json.load(open("configs.json", "r"))

    def genFrutas(self, force: bool=False):
        if len(self.server_infos['fruit-position']) == 0 or force:
            frutax = random.randrange(0, int((self.configs['tela-configs']['size'][0] - 200) / self.configs['server-configs']['scale-players'])) * self.configs['server-configs']['scale-players']
            frutay = random.randrange(0, int(self.configs['tela-configs']['size'][1] / self.configs['server-configs']['scale-players'])) * self.configs['server-configs']['scale-players']
            self.server_infos['fruit-position'] = [frutax, frutay]
            print("Gerou fruta")
            return [frutax, frutay]

    def inputPlayer(self, player):
        velocidade = self.configs['server-configs']['velocity-players']

        #Colision Limite Map and Movement Player
        if player['direcao'] == 'esquerda' and player['position'][0] < (self.configs['tela-configs']['size'][0] - 200) -self.configs['server-configs']['scale-players']:
            player['position'][0] += velocidade
        if player['direcao'] == 'direita' and player['position'][0] > 0:
            player['position'][0] -= velocidade  
        if player['direcao'] == 'cima' and player['position'][1] > 0:
            player['position'][1] -= velocidade  
        if player['direcao'] == 'baixo' and player['position'][1] < self.configs['tela-configs']['size'][1]-self.configs['server-configs']['scale-players']:
            player['position'][1] += velocidade

        #Colision Fruit
        if player['position'][0] == self.server_infos['fruit-position'][0] and player['position'][1] == self.server_infos['fruit-position'][1]:
            self.server_infos['fruit-position'] = self.genFrutas(force=True)
            player['score'] += 1
            print("[LOG] COMEU")

        return player
            

    def lenRequests(self, conn, addr):
        print(f"Conectado! {addr}")
        player_id = str(addr)
        self.server_infos['other-players'][player_id] = {
            "_id":player_id,
            "position":[0, 0],
            "score":0,
            "direcao":"parado"
        }
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("break")
                    break
                self.server_infos['other-players'][player_id] = json.loads(data.decode('utf-8'))
                print(self.server_infos)
            except Exception as e:
                print(e)
                break
        del self.server_infos['other-players'][player_id]
        self.clients.remove(conn)
        conn.close()
        print(f"{addr} desconectado!")
    
    def sendRequest(self, message, connection):
        try:
            connection.send(message)
        except:
            connection.close()
            self.clients.remove(connection)

    def UpdatePlayers(self):
        self.genFrutas()
        while True:
            for player in self.server_infos['other-players'].keys():
                self.server_infos['other-players'][player] = self.inputPlayer(self.server_infos['other-players'][player])
            # print(self.server_infos)
            message = json.dumps(self.server_infos).encode('utf-8')
            
            for client in self.clients:
                self.sendRequest(message, client)
            time.sleep(0.1)

    def main(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()
        print(f"Servidor Iniciado ({self.host}:{self.port})")
        thread1 = threading.Thread(target=self.UpdatePlayers)
        thread1.start()
        while True:
            conn, addr = server.accept()
            self.clients.append(conn)
            thread = threading.Thread(target=self.lenRequests, args=(conn, addr))
            thread.start()


Server().main()
