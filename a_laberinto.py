from PIL import Image
import numpy as np
import math as mth
from selenium.webdriver.common.keys import Keys
import time

class agent():
    COLOR_PATH = np.array([102, 102, 102])
    COLOR_CAR = np.array([136, 1, 46])
    COLOR_HOUSE = np.array([204, 153, 51])
    COLOR_GRASS = np.array([35, 43, 15])
    COLOR_OWL = np.array([57, 216, 206])
    COLOR_BLACK = np.zeros(3)

    def __init__(self, screen):
        self.nodos = []
        self.__stack = []
        self.ad_list = []
        self.__array_screen = screen
        self.encontrado = False
        self.road = []
        self.flecha_mover = []
        self.visited = [0 for _ in range(30)]
        self.nodo_actual = 0

    def calculate_time(self,distance):
        return distance*(0.05/5.5)
        
    def update_screen(self,new_screen):
        self.__array_screen = new_screen

    def process_image(self):
        self.__array_screen[0:30][0:88] = np.zeros(3)
        for i in range(367):
            for j in range(730):
                if ( np.equal(self.__array_screen[i][j], self.COLOR_GRASS).all()):
                    self.__array_screen[i][j] = self.COLOR_GRASS
                elif (not np.equal(self.__array_screen[i][j], self.COLOR_CAR).all()) and (not np.equal(self.__array_screen[i][j], self.COLOR_HOUSE).all()) and (not np.equal(self.__array_screen[i][j], self.COLOR_PATH).all()
                and not (self.__array_screen[i][j][0]>=53 and self.__array_screen[i][j][0]<=59 and self.__array_screen[i][j][1]>=56 and self.__array_screen[i][j][1]<=97 and 
                self.__array_screen[i][j][2]>=57 and self.__array_screen[i][j][2]<=111)):
                    self.__array_screen[i, j] = self.COLOR_BLACK
                elif (self.__array_screen[i][j][0]>=53 and self.__array_screen[i][j][0]<=59 and self.__array_screen[i][j][1]>=56 and self.__array_screen[i][j][1]<=97 and 
                self.__array_screen[i][j][2]>=57 and self.__array_screen[i][j][2]<=111) :
                    self.__array_screen[i, j] = self.COLOR_OWL
        house_position , xd = self.__find_pix(self.COLOR_HOUSE)
        self.__array_screen[house_position[1] - 20 : house_position[1]+10,house_position[0]-13:house_position[0]+15] = self.COLOR_HOUSE


    def __repeated_nodes(self,nodo):
        ans = False
        for n in self.nodos:
            if(mth.dist(nodo[0],n[0]) < 32):
                ans = True
        return ans

    def __is_known(self, position):
        for node in self.nodos:
            if node[0] == position:
                return True 
        return False

    def __index_node(self, position):
        for i in range(len(self.nodos)):
            if self.nodos[i][0] == position:
                return i

    def __make_direction(self, *args):
        """ args[0] x_min, args[1] x_max, args[2] y_min, args[3] y_max, args[4] mean_x, args[5] mean_y
            los valores ya viene procesados (x_min = x - 40)
        """
        if (args[0] > 0 and np.equal(self.__array_screen[args[5], args[0]], agent.COLOR_PATH).all()):
            return 'I'
        if (args[1] > 0 and np.equal(self.__array_screen[args[5], args[1]], agent.COLOR_PATH).all()):
            return 'D'
        if (args[2] > 0 and np.equal(self.__array_screen[args[2], args[4]], agent.COLOR_PATH).all()):
            return 'AR'
        if (args[3] > 0 and np.equal(self.__array_screen[args[3], args[4]], agent.COLOR_PATH).all()):
            return 'AB'

    def __find_pix(self, to_find):
        # to_find el color a buscar [r, g, b]
        x, y = [], []
        for i in range(367):
            aux = np.where(self.__array_screen[i] == to_find)[0]
            if aux.size != 0:
                y.append(i)
                for x_pos in aux:
                    if x_pos not in x:
                        x.append(x_pos)
        mean_x, mean_y = np.mean(x, dtype=np.int32), np.mean(y, dtype=np.int32)
        min_x , max_x = np.min(x),np.max(x)
        min_y , max_y = np.min(y),np.max(y)
        direccion = self.__make_direction(min_x - 40, max_x + 40, min_y - 40, max_y + 40, mean_x, mean_y)
        if(max_x-min_x > max_y-min_y):
            mean_y+=3
        # Retornamos la media de todas las posiciones X y Y y la direcion en la que se puede mover
        return [mean_x, mean_y], direccion

    def __add_node(self, nodo_aux, nodo_hijo):
        if not self.__is_known(nodo_hijo[0]):
            self.nodos.append(nodo_hijo)
        if len(self.ad_list) <= self.__index_node(nodo_hijo[0]):
            self.ad_list.append([])
            self.ad_list.append([])
        self.ad_list[self.__index_node(nodo_hijo[0])].append(self.__index_node(nodo_aux[0]))
        self.ad_list[self.__index_node(nodo_aux[0])].append(self.__index_node(nodo_hijo[0]))

    def sensing(self):
        self.process_image()
        image = Image.fromarray(self.__array_screen)
        car_position, direccion = self.__find_pix(self.COLOR_CAR)

        if len(self.ad_list) == 0:
            self.ad_list.append([])
            self.__graph(car_position[0], car_position[1], [direccion])

    def __graph (self, pos_x, pos_y, direccion):
        # AR = arriba, AB = abajo, D = derecha, I = izquierda, H = casa
        nodo = [[pos_x, pos_y], direccion]    
        if not self.__is_known(nodo[0]) and pos_x != -1:
            self.nodos.append(nodo)
        if pos_x != -1:
            self.__stack.append(nodo)
            self.visited[self.__index_node(nodo[0])] = 1
        if len(self.__stack) != 0:
            nodo_aux = self.__stack.pop()
            x, y = nodo_aux[0][0], nodo_aux[0][1]
            direccion = nodo_aux[1][:]
            d = direccion.pop()
            direccion_hijo = []
            find = False
            if d == 'AR':
                y -= 21
                # Linea vertical
                aux = self.__array_screen[:, x]
                for i in range(y,0,-1):
                    if (np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any()):
                        break
                i += 20
                for j in range(y,i,-1):
                    if np.equal(self.__array_screen[j - 17, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j - 37], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                        break
                    if (not np.equal(self.__array_screen[j, x + 22], self.COLOR_GRASS).all() and 
                        not np.equal(self.__array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.__array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if abs(j - i) > 37 and find:
                        direccion_hijo.append('AR')
                    if find:
                        nodo_hijo = [[x, j - 17], direccion_hijo]
                        if(not self.__repeated_nodes(nodo_hijo)):
                            self.__add_node(nodo_aux, nodo_hijo)
                            if len(direccion) != 0 and self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                self.__stack.append(nodo_hijo)
                                self.visited[self.__index_node(nodo_hijo[0])] = 1
                                return self.__graph(x, y + 21, direccion)
                            elif self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                return self.__graph(x, j - 17, direccion_hijo)
            if d == 'AB':
                y += 21
                aux = self.__array_screen[:, x]
                for i in range(y,367):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(y,i):
                    if np.equal(self.__array_screen[j + 17, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j + 27], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                        break
                    if (not np.equal(self.__array_screen[j, x + 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.__array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if abs(i - j) > 37 and find:
                        direccion_hijo.append('AB')
                    if find:
                        nodo_hijo = [[x, j + 17], direccion_hijo]
                        if(not self.__repeated_nodes(nodo_hijo)):
                            self.__add_node(nodo_aux, nodo_hijo)
                            if len(direccion) != 0 and self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                self.__stack.append(nodo_hijo)
                                self.visited[self.__index_node(nodo_hijo[0])] = 1
                                return self.__graph(x, y - 21, direccion)
                            elif self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                return self.__graph(x, j + 17, direccion_hijo)
            if d == 'I':
                x -= 21
                aux = self.__array_screen[y, :]
                for i in range(x,0,-1):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i += 20
                for j in range(x,i,-1):
                    if np.equal(self.__array_screen[y, j - 17], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j - 32, y], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                        break
                    if (not np.equal(self.__array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.__array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if abs(j - i) > 37 and find:
                        direccion_hijo.append('I')
                    if find:
                        nodo_hijo = [[j - 17, y], direccion_hijo]
                        if(not self.__repeated_nodes(nodo_hijo)):
                            self.__add_node(nodo_aux, nodo_hijo)
                            if len(direccion) != 0 and self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                self.__stack.append(nodo_hijo)
                                self.visited[self.__index_node(nodo_hijo[0])] = 1
                                return self.__graph(x + 21, y, direccion)
                            elif self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                return self.__graph(j - 17, y, direccion_hijo)
            if d == 'D':
                x += 21
                aux = self.__array_screen[y,:]
                for i in range(x,730):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(x,i):
                    if np.equal(self.__array_screen[y, j + 17], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j + 30, y], ['H']]
                        self.__add_node(nodo_aux,nodo_hijo)
                        break
                    if (not np.equal(self.__array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.__array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if abs(i - j) > 37 and find and not np.equal(self.__array_screen[y, j + 45], self.COLOR_BLACK).all():
                        direccion_hijo.append('D')
                    if find:
                        nodo_hijo = [[j + 17, y], direccion_hijo]
                        if(not self.__repeated_nodes(nodo_hijo)):
                            self.__add_node(nodo_aux, nodo_hijo)
                            if len(direccion) != 0 and self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                self.__stack.append(nodo_hijo)
                                self.visited[self.__index_node(nodo_hijo[0])] = 1
                                return self.__graph(x - 21, y, direccion)#restar 21
                            elif self.visited[self.__index_node(nodo_hijo[0])] != 1:
                                return self.__graph(j + 17, y, direccion_hijo)
            if len(direccion) != 0 and not find:
                return self.__graph(nodo_aux[0][0], nodo_aux[0][1], direccion)
            else:
                return self.__graph(-1, -1, 'NA')

    def dfs(self,u,visited):
        self.road.append(u)
        visited[u] = True
        for j in range(len(self.ad_list[u])):
            v = self.ad_list[u][j]
            if("H" in self.nodos[v][1]):
                self.encontrado = True
                self.road.append(v)
                break
            if(not visited[v] and not self.encontrado):
                self.dfs(v,visited)
            if(j==len(self.ad_list[u])-1 and not self.encontrado):
                self.road.pop()


    def thinking(self):
        visited = [False for i in range(len(self.ad_list))]
        if(not self.encontrado):
            self.dfs(0,visited)
        for i in range(len(self.road)-1):
            pos_actual = self.nodos[self.road[i]][0]
            pos_dest = self.nodos[self.road[i + 1]][0]
            if(len(self.nodos[self.road[i]][1]) == 1):
                self.flecha_mover.append([self.nodos[self.road[i]][1][0],self.calculate_time(mth.dist(pos_actual,pos_dest))])
            else:
                if(pos_actual[0] == pos_dest[0]):
                    if(pos_dest[1]>pos_actual[1]):
                        self.flecha_mover.append(['AB',self.calculate_time(abs(pos_dest[1]-pos_actual[1]))])
                    else:
                        self.flecha_mover.append(['AR',self.calculate_time(abs(pos_actual[1]-pos_dest[1]))])
                else:
                    if(pos_dest[0]>pos_actual[0]):
                        self.flecha_mover.append(['D',self.calculate_time(abs(pos_dest[0]-pos_actual[0]))])
                    else:
                        self.flecha_mover.append(['I',self.calculate_time(abs(pos_actual[0]-pos_dest[0]))])


    def acting(self,ActionChains):
        for i in self.flecha_mover:
            if(i[0] == 'AR'):
                ActionChains.key_down("w").pause(i[1]).key_up("w")
            elif(i[0] == 'AB'):
                ActionChains.key_down("s").pause(i[1]).key_up("s")
            elif(i[0] == 'D'):
                ActionChains.key_down("d").pause(i[1]).key_up("d")
            else:
                ActionChains.key_down("a").pause(i[1]).key_up("a")
        ActionChains.perform()
            

