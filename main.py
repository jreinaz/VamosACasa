import io

from numpy import array
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from a_laberinto import agent

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
    agent_ = agent(array_screen)
    agent_.sensing()
    for adj, node in zip(agent_.ad_list, agent_.nodos):
        print("({}, {})".format(node[0], adj))
    # Image.fromarray(array_screen).save('C:/Users/enano/OneDrive/Documentos/Python/screen_array.png')
    # Resuelve el laberinto
