import numpy as np

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
    
    def __is_known(self, position):
        for node in self.nodos:
            if node[0] == position:
                return True 
        return False

    def __index_node(self, position):
        for node in self.nodos:
            if node[0] == position:
                return self.nodos.index(node)

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
        direccion = self.__make_direction(np.min(x) - 40, np.max(x) + 40, np.min(y) - 40, np.max(y) + 40, mean_x, mean_y)
        # Retornamos la media de todas las posiciones X y Y y la direcion en la que se puede mover
        return [mean_x, mean_y], direccion

    def __add_node(self, nodo_aux, nodo_hijo):
        if not self.__is_known(nodo_hijo[0]):
            self.nodos.append(nodo_hijo)
        if len(self.ad_list) == self.nodos.index(nodo_hijo):
            self.ad_list.append([])
        self.ad_list[self.nodos.index(nodo_hijo)].append(self.__index_node(nodo_aux[0]))
        self.ad_list[self.__index_node(nodo_aux[0])].append(self.nodos.index(nodo_hijo))

    def sensing(self):
        self.__array_screen[0:30][0:88] = np.zeros(3)
        for i in range(367):
            for j in range(730):
                if ( np.equal(self.__array_screen[i][j], self.COLOR_GRASS).all()):
                    self.__array_screen[i][j] = self.COLOR_GRASS
                elif (not np.equal(self.__array_screen[i][j], self.COLOR_CAR).all()) and (not np.equal(self.__array_screen[i][j], self.COLOR_HOUSE).all()) and (not np.equal(self.__array_screen[i][j], self.COLOR_PATH).all()
                and not (self.__array_screen[i][j][0] >=53 and self.__array_screen[i][j][0] <= 59 and self.__array_screen[i][j][1] >= 56 and self.__array_screen[i][j][1] <= 97 and 
                self.__array_screen[i][j][2] >= 57 and self.__array_screen[i][j][2] <= 111)):
                    self.__array_screen[i, j] = self.COLOR_BLACK
                elif (self.__array_screen[i][j][0] >= 53 and self.__array_screen[i][j][0] <= 59 and self.__array_screen[i][j][1] >=56 and self.__array_screen[i][j][1] <= 97 and 
                self.__array_screen[i][j][2] >= 57 and self.__array_screen[i][j][2] <= 111):
                    self.__array_screen[i, j] = self.COLOR_OWL
        house_position , xd = self.__find_pix(self.COLOR_HOUSE)
        self.__array_screen[house_position[1] - 20 : house_position[1],house_position[0]] = self.COLOR_HOUSE
        self.__array_screen[house_position[1], house_position[0] - 13 : house_position[0] + 15] = self.COLOR_HOUSE
        car_position, direccion = self.__find_pix(self.COLOR_CAR)
        if len(self.ad_list) == 0:
            self.ad_list.append([])
            self.__graph(car_position[0], car_position[1], [direccion])

    def __graph (self, pos_x, pos_y, direccion):
        # AR = arriba, AB = abajo, D = derecha, I = izquierda, H = casa
        nodo = [[pos_x, pos_y], direccion]
        if pos_x != -1:
            self.__stack.append(nodo)
        if not self.__is_known(nodo[0]) and pos_x != -1:
            self.nodos.append(nodo)
        # print("Lista de Nodos: ", self.nodos, '\n')
        if len(self.__stack) != 0:
            nodo_aux = self.__stack.pop()
            # print("Nodo actual: ", nodo_aux)
            x, y = nodo_aux[0][0], nodo_aux[0][1]
            direccion = nodo_aux[1][:]
            d = direccion.pop()
            direccion_hijo = []
            find = False
            if d == 'AR':
                y -= 22
                # Linea vertical
                aux = self.__array_screen[:, x]
                for i in range(y,0,-1):
                    if (np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any()):
                        break
                i += 20
                for j in range(y,i,-1):
                    if (not np.equal(self.__array_screen[j, x + 22], self.COLOR_GRASS).all() and 
                        not np.equal(self.__array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.__array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if j - i > 60 and find:
                        direccion_hijo.append('AR')
                    if np.equal(self.__array_screen[j, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                    if find:
                        nodo_hijo = [[x, j - 20], direccion_hijo]
                        # print("Nodo hijo: ", nodo_hijo, '\n')
                        self.__add_node(nodo_aux, nodo_hijo)
                        if len(direccion) != 0:
                            self.__stack.append(nodo_hijo)
                            return self.__graph(x, y + 22, direccion) 
                        else:
                            return self.__graph(x, j - 20, direccion_hijo)
            if d == 'AB':
                y += 22
                # Linea vertical
                aux = self.__array_screen[:, x]
                for i in range(y,367):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(y,i):
                    if (not np.equal(self.__array_screen[j, x + 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.__array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if i - j > 60 and find:
                        direccion_hijo.append('AB')
                    if np.equal(self.__array_screen[j, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                    if find:
                        nodo_hijo = [[x, j + 20], direccion_hijo]
                        # print("Nodo hijo: ", nodo_hijo, '\n')
                        self.__add_node(nodo_aux, nodo_hijo)
                        if len(direccion) != 0:
                            self.__stack.append(nodo_hijo)
                            return self.__graph(x, y - 22, direccion)
                        else:
                            return self.__graph(x, j + 20, direccion_hijo)
            if d == 'I':
                x -= 22
                # linea horizontal
                aux = self.__array_screen[y, :]
                for i in range(x,0,-1):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i += 20
                for j in range(x,i,-1):
                    if (not np.equal(self.__array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.__array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if j - i > 60 and find:
                        direccion_hijo.append('I')
                    if np.equal(self.__array_screen[y, j], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j, y], ['H']]
                        self.__add_node(nodo_aux, nodo_hijo)
                    if find:
                        nodo_hijo = [[j - 20, y], direccion_hijo]
                        # print("Nodo hijo: ", nodo_hijo, '\n')
                        self.__add_node(nodo_aux, nodo_hijo)
                        if len(direccion) != 0:
                            self.__stack.append(nodo_hijo)
                            return self.__graph(x + 22, y, direccion)
                        else:
                            return self.__graph(j - 20, y, direccion_hijo)
            if d == 'D':
                x += 22
                # Linea horizontal
                aux = self.__array_screen[y,:]
                for i in range(x,730):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(x,i):
                    if (not np.equal(self.__array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.__array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.__array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if i - j > 60 and find and not np.equal(self.__array_screen[y, j + 45], self.COLOR_BLACK).all():
                        direccion_hijo.append('D')
                    if np.equal(self.__array_screen[y, j], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j, y], ['H']]
                        self.__add_node(nodo_aux,nodo_hijo)
                    if find:
                        nodo_hijo = [[j + 20, y], direccion_hijo]
                        # print("Nodo hijo: ", nodo_hijo, '\n')
                        self.__add_node(nodo_aux, nodo_hijo)
                        if len(direccion) != 0:
                            self.__stack.append(nodo_hijo)
                            return self.__graph(x - 22, y, direccion)
                        else:
                            return self.__graph(j + 20, y, direccion_hijo)
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
            if(not visited[v]):
                self.dfs(v,visited)
            if(j==len(self.ad_list[u])-1 and not self.encontrado):
                self.road.pop()


    def thinking(self):
        visited = [False for i in range(len(self.ad_list))]
        if(not self.encontrado):
            self.dfs(0,visited)
        return self.road





