import io

from numpy import array
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
#import keyboard
import time

from a_laberinto import agent

driver = webdriver.Chrome('C:/Users/Ingenieria/Documents/ChromeDriver/chromedriver')
driver.get('https://www.juegosinfantilespum.com/laberintos-online/12-auto-buhos.php')
gridPlay = driver.find_element(By.CSS_SELECTOR, "canvas")
jugar = False;
print("Quiere jugar?(1 para si, 0 para no): ")
jugar = input()
while(jugar != '0'):
    element = gridPlay.screenshot_as_png
    screen = Image.open(io.BytesIO(element)).convert('RGB')
    screen.save('C:\Clonado P1 inteligentes\VamosACasa\screen.png')
    array_screen = array(screen)
    agent_ = agent(array_screen)
    print("SENSING.......")
    agent_.sensing()
    print("THINKING......")
    agent_.thinking()
    print("ACTING!!!!!")
    agent_.acting(ActionChains(driver))
    print("Quiere seguir jugando?(1 para si, 0 para no): ")
    jugar = input()
driver.close()
