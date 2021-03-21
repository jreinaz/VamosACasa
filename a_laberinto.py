from PIL import Image
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
        self.stack = []
        self.edge_list = []
        self.array_screen = screen
    
    def is_known(self, position):
        for node in self.nodos:
            if node[0] == position:
                return True 
        return False

    def make_direction(self, *args):
        """ args[0] x_min, args[1] x_max, args[2] y_min, args[3] y_max, args[4] mean_x, args[5] mean_y
            los valores ya viene procesados (x_min = x - 40)
        """
        if (args[0] > 0 and np.equal(self.array_screen[args[5], args[0]], agent.COLOR_PATH).all()):
            return 'I'
        if (args[1] > 0 and np.equal(self.array_screen[args[5], args[1]], agent.COLOR_PATH).all()):
            return 'D'
        if (args[2] > 0 and np.equal(self.array_screen[args[2], args[4]], agent.COLOR_PATH).all()):
            return 'AR'
        if (args[3] > 0 and np.equal(self.array_screen[args[3], args[4]], agent.COLOR_PATH).all()):
            return 'AB'

    def find_pix(self, to_find):
        # to_find el color a buscar [r, g, b]
        x, y = [], []
        for i in range(367):
            aux = np.where(self.array_screen[i] == to_find)[0]
            if aux.size != 0:
                y.append(i)
                for x_pos in aux:
                    if x_pos not in x:
                        x.append(x_pos)
        mean_x, mean_y = np.mean(x, dtype=np.int32), np.mean(y, dtype=np.int32)
        direccion = self.make_direction(np.min(x) - 40, np.max(x) + 40, np.min(y) - 40, np.max(y) + 40, mean_x, mean_y)
        # Retornamos la media de todas las posiciones X y Y y la direcion en la que se puede mover
        return [mean_x, mean_y], direccion

    def sensing(self):
        self.array_screen[0:30][0:88] = np.zeros(3)
        for i in range(367):
            for j in range(730):
                if ( np.equal(self.array_screen[i][j], self.COLOR_GRASS).all()):
                    self.array_screen[i][j] = self.COLOR_GRASS
                elif (not np.equal(self.array_screen[i][j], self.COLOR_CAR).all()) and (not np.equal(self.array_screen[i][j], self.COLOR_HOUSE).all()) and (not np.equal(self.array_screen[i][j], self.COLOR_PATH).all()
                and not (self.array_screen[i][j][0]>=53 and self.array_screen[i][j][0]<=59 and self.array_screen[i][j][1]>=56 and self.array_screen[i][j][1]<=97 and 
                self.array_screen[i][j][2]>=57 and self.array_screen[i][j][2]<=111)):
                    self.array_screen[i, j] = self.COLOR_BLACK
                elif (self.array_screen[i][j][0]>=53 and self.array_screen[i][j][0]<=59 and self.array_screen[i][j][1]>=56 and self.array_screen[i][j][1]<=97 and 
                self.array_screen[i][j][2]>=57 and self.array_screen[i][j][2]<=111) :
                    self.array_screen[i, j] = self.COLOR_OWL
        house_position , xd = self.find_pix(self.COLOR_HOUSE)
        a = house_position[1]-20
        b = house_position[0]-13
        c = house_position[0]+15
        self.array_screen[a:house_position[1],house_position[0]] = self.COLOR_HOUSE
        self.array_screen[house_position[1],b:c] = self.COLOR_HOUSE
        car_position, direccion = self.find_pix(self.COLOR_CAR) 
        self.graph(car_position[0], car_position[1], [direccion])

    def graph (self, pos_x, pos_y, direccion):
        # AR = arriba, AB = abajo, D = derecha, I = izquierda, H = casa
        nodo = [[pos_x, pos_y], direccion]
        if pos_x != -1:
            self.stack.append(nodo)
        if not self.is_known(nodo[0]) and pos_x != -1:
            self.nodos.append(nodo)
        if len(self.stack) != 0:
            nodo_aux = self.stack.pop()
            x, y = nodo_aux[0][0], nodo_aux[0][1]
            direccion = nodo_aux[1][:]
            d = direccion.pop()
            direccion_hijo = []
            find = False
            if d == 'AR':
                y -= 22
                # Linea vertical
                aux = self.array_screen[:, x]
                for i in range(y,0,-1):
                    if (np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any()):
                        break
                i += 20
                for j in range(y,i,-1):
                    if (not np.equal(self.array_screen[j, x + 22], self.COLOR_GRASS).all() and 
                        not np.equal(self.array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if j - i > 60 and find:
                        direccion_hijo.append('AR')
                    if np.equal(self.array_screen[j, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j], ['H']]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        self.nodos.append(nodo_hijo)
                    if find:
                        nodo_hijo = [[x, j - 20], direccion_hijo]
                        if not self.is_known(nodo_hijo[0]):
                            self.nodos.append(nodo_hijo)
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        if len(direccion) != 0:
                            self.stack.append(nodo_hijo)
                            return self.graph(x, y + 22, direccion)
                        else:
                            return self.graph(x, j - 20, direccion_hijo)
            if d == 'AB':
                y += 22
                # Linea vertical
                aux = self.array_screen[:, x]
                for i in range(y,367):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(y,i):
                    if (not np.equal(self.array_screen[j, x + 22], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[j, x + 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('D')
                        find = True
                    if (not np.equal(self.array_screen[j, x - 22], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[j, x - 22], self.COLOR_BLACK).all()):
                        direccion_hijo.append('I')
                        find = True
                    if i - j > 60 and find:
                        direccion_hijo.append('AB')
                    if np.equal(self.array_screen[j, x], self.COLOR_HOUSE).all():
                        nodo_hijo = [[x, j], ['H']]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        self.nodos.append(nodo_hijo)
                    if find:
                        nodo_hijo = [[x, j + 20], direccion_hijo]
                        if not self.is_known(nodo_hijo[0]):
                            self.nodos.append(nodo_hijo)
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        if len(direccion) != 0:
                            self.stack.append(nodo_hijo)
                            return self.graph(x, y - 22, direccion)
                        else:
                            return self.graph(x, j + 20, direccion_hijo)
            if d == 'I':
                x -= 22
                # linea horizontal
                aux = self.array_screen[y, :]
                for i in range(x,0,-1):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i += 20
                for j in range(x,i,-1):
                    if (not np.equal(self.array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if j - i > 60 and find:
                        direccion_hijo.append('I')
                    if np.equal(self.array_screen[y, j], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j, y], ['H']]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        self.nodos.append(nodo_hijo)
                    if find:
                        nodo_hijo = [[j - 20, y], direccion_hijo]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        if not self.is_known(nodo_hijo[0]):
                            self.nodos.append(nodo_hijo)
                        if len(direccion) != 0:
                            self.stack.append(nodo_hijo)
                            return self.graph(x + 22, y, direccion)
                        else:
                            return self.graph(j - 20, y, direccion_hijo)
            if d == 'D':
                x += 22
                # Linea horizontal
                aux = self.array_screen[y,:]
                for i in range(x,730):
                    if np.equal(aux[i], self.COLOR_GRASS).any() or np.equal(aux[i], self.COLOR_OWL).any():
                        break
                i -= 20
                for j in range(x,i):
                    if (not np.equal(self.array_screen[y + 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[y + 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AB')
                        find = True
                    if (not np.equal(self.array_screen[y - 22, j], self.COLOR_GRASS).all() and
                        not np.equal(self.array_screen[y - 22, j], self.COLOR_BLACK).all()):
                        direccion_hijo.append('AR')
                        find = True
                    if i - j > 60 and find and not np.equal(self.array_screen[y, j + 45], self.COLOR_BLACK).all():
                        direccion_hijo.append('D')
                    if np.equal(self.array_screen[y, j], self.COLOR_HOUSE).all():
                        nodo_hijo = [[j, y], ['H']]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        self.nodos.append(nodo_hijo)
                    if find:
                        nodo_hijo = [[j + 20, y], direccion_hijo]
                        self.edge_list.append((nodo_aux[0], nodo_hijo[0]))
                        if not self.is_known(nodo_hijo[0]):
                            self.nodos.append(nodo_hijo)
                        if len(direccion) != 0:
                            self.stack.append(nodo_hijo)
                            return self.graph(x - 22, y, direccion)
                        else:
                            return self.graph(j + 20, y, direccion_hijo)
            if len(direccion) != 0 and not find:
                return self.graph(nodo_aux[0][0], nodo_aux[0][1], direccion)
            else:
                return self.graph(-1, -1, 'NA') 