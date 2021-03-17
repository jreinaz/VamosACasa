import io
from PIL import Image
from numpy import array
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COLOR_PATH = np.array([102, 102, 102])
COLOR_CAR = np.array([136, 1, 46])
COLOR_HOUSE = np.array([204, 153, 51])
COLOR_GRASS = np.array([35, 43, 15])
COLOR_OWL = np.array([57, 216, 206])
COLOR_BLACK = np.zeros(3)

nodos, stack, lista_aristas = [], [], []

def is_known(position):
    global nodos
    for node in nodos:
        if node[0] == position:
            return True 
    return False

def find_pix(to_find):
    # to_find el color a buscar [r, g, b]
    global array_screen , COLOR_PATH
    x = []
    y = []
    for i in range(367):
        aux = np.where(array_screen[i] == to_find)[0]
        if aux.size != 0:
            y.append(i)
            for x_pos in aux:
                if x_pos not in x:
                    x.append(x_pos)
    mean_x, mean_y = np.mean(x,dtype=np.int32), np.mean(y,dtype=np.int32)
    direccion = '?'
    if (np.min(x) - 40 > 0 and np.equal(array_screen[mean_y , np.min(x) - 40], COLOR_PATH).all()):
        direccion = 'I'
    if (np.max(x) + 40 > 0 and np.equal(array_screen[mean_y , np.max(x) + 40], COLOR_PATH).all()):
        direccion = 'D'
    if (np.min(y) - 40 > 0 and np.equal(array_screen[np.min(y) - 40, mean_x], COLOR_PATH).all()):
        direccion = 'AR'
    if (np.max(y) + 40 > 0 and np.equal(array_screen[np.max(y) + 40, mean_x], COLOR_PATH).all()):
        direccion = 'AB'
    # Retornamos la media de todas las posiciones X y Y y la direcion en la que se puede mover
    return [mean_x, mean_y], direccion

def graph (pos_x, pos_y, direccion):
    # AR = arriba, AB = abajo, D = derecha, I = izquierda, H = casa
    global array_screen, nodos, COLOR_GRASS, COLOR_OWL, COLOR_HOUSE, stack, COLOR_BLACK
    nodo = [[pos_x, pos_y], direccion]
    if pos_x != -1:
        stack.append(nodo)
    if not is_known(nodo[0]) and pos_x != -1:
        nodos.append(nodo)
    if len(stack) != 0:
        # Orientation = true vertical Orientation=false horizontal
        nodo_aux = stack.pop()
        x, y = nodo_aux[0][0], nodo_aux[0][1]
        direccion = nodo_aux[1][:]
        d = direccion.pop()
        direccion_hijo = []
        find = False
        if d == 'AR':
            y -= 22
            # Linea vertical
            aux = array_screen[:, x]
            for i in range(y,0,-1):
                if (np.equal(aux[i], COLOR_GRASS).any() or np.equal(aux[i], COLOR_OWL).any()):
                    break
            i += 20
            for j in range(y,i,-1):
                if not np.equal(array_screen[j, x + 22], COLOR_GRASS).all() and not np.equal(array_screen[j, x + 22], COLOR_BLACK).all():
                    direccion_hijo.append('D')
                    find = True
                    
                if not np.equal(array_screen[j, x - 22], COLOR_GRASS).all() and not np.equal(array_screen[j, x - 22], COLOR_BLACK).all() :
                    direccion_hijo.append('I')
                    find = True

                if j - i > 60 and find:
                    direccion_hijo.append('AR')

                if np.equal(array_screen[j, x], COLOR_HOUSE).all():
                    nodo_hijo = [[x, j], ['H']]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    nodos.append(nodo_hijo)

                if find:
                    nodo_hijo = [[x, j - 20], direccion_hijo]
                    if not is_known(nodo_hijo[0]):
                        nodos.append(nodo_hijo)
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    if len(direccion) != 0:
                        stack.append(nodo_hijo)
                        return graph(x, y + 22, direccion)
                    else:
                        return graph(x, j - 20, direccion_hijo)
        if d == 'AB':
            y += 22
            # Linea vertical
            aux = array_screen[:, x]
            for i in range(y,367):
                if np.equal(aux[i], COLOR_GRASS).any() or np.equal(aux[i], COLOR_OWL).any():
                    break
            i -= 20
            for j in range(y,i):
                if not np.equal(array_screen[j, x + 22], COLOR_GRASS).all() and not np.equal(array_screen[j, x + 22], COLOR_BLACK).all():
                    direccion_hijo.append('D')
                    find = True
                    
                if not np.equal(array_screen[j, x - 22], COLOR_GRASS).all() and not np.equal(array_screen[j, x - 22], COLOR_BLACK).all():
                    direccion_hijo.append('I')
                    find = True

                if i - j > 60 and find:
                    direccion_hijo.append('AB')

                if np.equal(array_screen[j, x], COLOR_HOUSE).all():
                    nodo_hijo = [[x, j], ['H']]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    nodos.append(nodo_hijo)

                if find:
                    nodo_hijo = [[x, j + 20], direccion_hijo]
                    if not is_known(nodo_hijo[0]):
                        nodos.append(nodo_hijo)
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    if len(direccion) != 0:
                        stack.append(nodo_hijo)
                        return graph(x, y - 22, direccion)
                    else:
                        return graph(x, j + 20, direccion_hijo)

        if d == 'I':
            x -= 22
            # linea horizontal
            aux = array_screen[y, :]
            for i in range(x,0,-1):
                if np.equal(aux[i], COLOR_GRASS).any() or np.equal(aux[i], COLOR_OWL).any():
                    break
            i += 20
            for j in range(x,i,-1):
                if not np.equal(array_screen[y + 22, j], COLOR_GRASS).all() and not np.equal(array_screen[y + 22, j], COLOR_BLACK).all():
                    direccion_hijo.append('AB')
                    find = True
                    
                if not np.equal(array_screen[y - 22, j], COLOR_GRASS).all() and not np.equal(array_screen[y - 22, j], COLOR_BLACK).all():
                    direccion_hijo.append('AR')
                    find = True

                if j - i > 60 and find:
                    direccion_hijo.append('I')

                if np.equal(array_screen[y, j], COLOR_HOUSE).all():
                    nodo_hijo = [[j, y], ['H']]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    nodos.append(nodo_hijo)

                if find:
                    nodo_hijo = [[j - 20, y], direccion_hijo]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    if not is_known(nodo_hijo[0]):
                        nodos.append(nodo_hijo)
                    if len(direccion) != 0:
                        stack.append(nodo_hijo)
                        return graph(x + 22, y, direccion)
                    else:
                        return graph(j - 20, y, direccion_hijo)
        if d == 'D':
            x += 22
            # Linea horizontal
            aux = array_screen[y,:]
            for i in range(x,730):
                if np.equal(aux[i], COLOR_GRASS).any() or np.equal(aux[i], COLOR_OWL).any():
                    break
            i -= 20
            for j in range(x,i):
                if not np.equal(array_screen[y + 22, j], COLOR_GRASS).all() and not np.equal(array_screen[y + 22, j], COLOR_BLACK).all():
                    direccion_hijo.append('AB')
                    find = True
                    
                if not np.equal(array_screen[y - 22, j], COLOR_GRASS).all() and not np.equal(array_screen[y - 22, j], COLOR_BLACK).all():
                    direccion_hijo.append('AR')
                    find = True
                
                if i - j > 60 and find and not np.equal(array_screen[y,j+45],COLOR_BLACK).all():
                    direccion_hijo.append('D')

                if np.equal(array_screen[y, j], COLOR_HOUSE).all():
                    nodo_hijo = [[j, y], ['H']]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    nodos.append(nodo_hijo)

                if find:
                    nodo_hijo = [[j + 20, y], direccion_hijo]
                    lista_aristas.append((nodo_aux[0], nodo_hijo[0]))
                    if not is_known(nodo_hijo[0]):
                        nodos.append(nodo_hijo)
                    if len(direccion) != 0:
                        stack.append(nodo_hijo)
                        return graph(x - 22, y, direccion)
                    else:
                        return graph(j + 20, y, direccion_hijo)
        if len(direccion) != 0 and not find:
            return graph(nodo_aux[0][0], nodo_aux[0][1], direccion)
        else:
            return graph(-1, -1, 'NA') 


def sensar(array_screen):
    global COLOR_CAR, COLOR_GRASS, COLOR_OWL, COLOR_BLACK
    array_screen[0:30][0:88] = np.zeros(3)
    for i in range(367):
        for j in range(730):
            if ( np.equal(array_screen[i][j], COLOR_GRASS).all()):
                array_screen[i][j] = COLOR_GRASS
            elif (not np.equal(array_screen[i][j], COLOR_CAR).all()) and (not np.equal(array_screen[i][j], COLOR_HOUSE).all()) and (not np.equal(array_screen[i][j], COLOR_PATH).all()
            and not (array_screen[i][j][0]>=53 and array_screen[i][j][0]<=59 and array_screen[i][j][1]>=56 and array_screen[i][j][1]<=97 and 
            array_screen[i][j][2]>=57 and array_screen[i][j][2]<=111)):
                array_screen[i, j] = COLOR_BLACK
            elif (array_screen[i][j][0]>=53 and array_screen[i][j][0]<=59 and array_screen[i][j][1]>=56 and array_screen[i][j][1]<=97 and 
            array_screen[i][j][2]>=57 and array_screen[i][j][2]<=111) :
                array_screen[i, j] = COLOR_OWL
    house_position , xd = find_pix(COLOR_HOUSE)
    a = house_position[1]-20
    b = house_position[0]-13
    c = house_position[0]+15
    array_screen[a:house_position[1],house_position[0]] = COLOR_HOUSE
    array_screen[house_position[1],b:c] = COLOR_HOUSE
    car_position, direccion = find_pix(COLOR_CAR) 
    graph(car_position[0], car_position[1], [direccion])
    for edge in lista_aristas:
        print(edge)


with webdriver.Chrome('C:/ChromeDriver/chromedriver') as driver:
    driver.get('https://www.juegosinfantilespum.com/laberintos-online/12-auto-buhos.php')
    gridPlay = driver.find_element(By.CSS_SELECTOR, "canvas")
    
    # driver.implicitly_wait(5) Hace lo Mismo que la linea de Abajo sin embargo 
    # Esta hara un wait cada vez que se inicie una pagina
    WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.ID, "_preload_div_")))
    
    gridPlay.click()
    element = gridPlay.screenshot_as_png
    screen = Image.open(io.BytesIO(element)).convert('RGB')
    # element.save('C:/Users/enano/OneDrive/Documentos/Python/screen.png')
    array_screen = array(screen)
    # Esta es para sensar el hambiente 
    sensar(array_screen)
    # Image.fromarray(array_screen).save('C:/Users/enano/OneDrive/Documentos/Python/screen_array.png')
    # Resuelve el laberinto