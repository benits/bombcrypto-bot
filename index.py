# -*- coding: utf-8 -*-
from src.logger import logger, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

import telebot


# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

bot = telebot.TeleBot(c["telegram_token"])
account_id = '#' + str(c['accountid'])

cat = """
                                                _
                                                \`*-.
                                                 )  _`-.
                                                .  : `. .
                                                : _   '  \\
                                                ; *` _.   `*-._
                                                `-.-'          `-.
                                                  ;       `       `.
                                                  :.       .        \\
                                                  . \  .   :   .-'   .
                                                  '  `+.;  ;  '      :
                                                  :  '  |    ;       ;-.
                                                  ; '   : :`-:     _.`* ;
                                               .*' /  .*' ; .*`- +'  `*'
                                               `*-*   `*-*  `*-*'
=========================================================================
========== 💰 Have I helped you in any way? All I ask is a tip! 🧾 ======
========== ✨ Faça sua boa ação de hoje, manda aquela gorjeta! 😊 =======
=========================================================================
======================== vvv BCOIN BUSD BNB vvv =========================
============== 0xbd06182D8360FB7AC1B05e871e56c76372510dDf ===============
=========================================================================
===== https://www.paypal.com/donate?hosted_button_id=JVYSC6ZYCNQQQ ======
=========================================================================

>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be found in the config.yaml file."""


def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


def moveToWithRandomness(x, y, t):
    pyautogui.moveTo(addRandomness(x, 10), addRandomness(y, 10), t+random()/2)


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def loadHeroesToSendHome():
    """Loads the images in the path and saves them as a list"""
    file_names = listdir('./targets/heroes-to-send-home')
    heroes = []
    for file in file_names:
        path = './targets/heroes-to-send-home/' + file
        heroes.append(cv2.imread(path))

    print('>>---> %d heroes that should be sent home loaded' % len(heroes))
    return heroes


def show(rectangles, img=None):
    """ Show an popup with rectangles showing the rectangles[(x, y, w, h),...]
        over img or a printSreen if no img provided. Useful for debugging"""

    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


def clickBtn(img, timeout=3, threshold=ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches) == 0):
            has_timed_out = time.time()-start > timeout
            continue

        x, y, w, h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x, pos_click_y, 1)
        pyautogui.click()
        return True

    return False


def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def scroll():
    commoms = positions(images['commom-text'], threshold=ct['commom'])

    if (len(commoms) == 0):
        commoms = positions(images['rare-text'], threshold=ct['rare'])
        if (len(commoms) == 0):
            commoms = positions(
                images['super_rare-text'], threshold=ct['super_rare'])
            if (len(commoms) == 0):
                commoms = positions(images['epic-text'], threshold=ct['epic'])
                if (len(commoms) == 0):
                    return

    x, y, w, h = commoms[len(commoms)-1]
#
    moveToWithRandomness(x, y, 1)

    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0, -c['click_and_drag_amount'],
                          duration=1, button='left')


def clickButtons():
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    global hero_clicks

    for (x, y, w, h) in buttons:
        moveToWithRandomness(x+(w/2), y+(h/2), 1)
        pyautogui.click()

        hero_clicks += 1
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if hero_clicks > 20:
            logger('too many hero clicks, try to increase the go_to_work_btn threshold')
            return
    return len(buttons)


def isHome(hero, buttons):
    y = hero[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            # if send-home button exists, the hero is not home
            return False
    return True


def isWorking(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def isResting(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return False
    return True


def discoveryRarity(bar):
    commoms = positions(images['commom-text'], threshold=ct['commom'])
    rares = positions(images['rare-text'], threshold=ct['rare'])
    super_rares = positions(
        images['super_rare-text'], threshold=ct['super_rare'])
    epics = positions(images['epic-text'], threshold=ct['epic'])

    y = bar[1]

    for (_, button_y, _, button_h) in commoms:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'commom'

    for (_, button_y, _, button_h) in rares:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'rare'

    for (_, button_y, _, button_h) in super_rares:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'super_rare'

    for (_, button_y, _, button_h) in epics:
        isBelow = y < (button_y + button_h)
        isAbove = y > (button_y - button_h)
        if isBelow and isAbove:
            return 'epic'

    return 'null'


def clickGreenBarButtons(chests):
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 140

    green_bars = positions(images['green-bar'], threshold=ct['green_bar'])
    logger('🟩 %d green bars detected' % len(green_bars))
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])
    logger('🆗 %d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        global deveTrabalhar
        global raridade
        raridade = discoveryRarity(bar)
        deveTrabalhar = 1

        if raridade != 'commom' and (chests >= 60 or chests == 0):
            deveTrabalhar = 0

        if (not isWorking(bar, buttons)) and deveTrabalhar == 1:
            not_working_green_bars.append(bar)

    if len(not_working_green_bars) > 0:
        logger('🆗 %d buttons with green bar detected' %
               len(not_working_green_bars))
        logger('👆 Clicking in %d heroes' % len(not_working_green_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    global hero_clicks
    hero_clicks_cnt = 0

    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2), y+(h/2), 1)
        pyautogui.click()
        hero_clicks += 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger(
                '⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)


def clickFullBarButtons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=ct['default'])
    buttons = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not isWorking(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        logger('👆 Clicking in %d heroes' % len(not_working_full_bars))

    global hero_clicks

    for (x, y, w, h) in not_working_full_bars:
        moveToWithRandomness(x+offset+(w/2), y+(h/2), 1)
        pyautogui.click()

        hero_clicks += 1
    return len(not_working_full_bars)


def goToHeroes():
    select_one = randint(1, 2)
    global login_attempts

    if select_one == 1 and clickBtn(images['up-arrow']):
        if clickBtn(images['up-arrow']):
            login_attempts = 0
            time.sleep(1)
            clickBtn(images['hero-icon-inside-teasure-hunt'])
    else:
        if clickBtn(images['go-back-arrow']) or clickBtn(images['hero-icon']):
            login_attempts = 0
            time.sleep(1)
            clickBtn(images['hero-icon'])

    time.sleep(randint(1, 3))


def goToGame():
    # in case of server overload popup
    clickBtn(images['x'])
    # time.sleep(3)
    clickBtn(images['x'])

    clickBtn(images['down-arrow'])

    clickBtn(images['down-arrow'])

    clickBtn(images['treasure-hunt-icon'])


def refreshHeroesPositions():

    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['go-back-arrow'])
    clickBtn(images['treasure-hunt-icon'])

    # time.sleep(3)
    clickBtn(images['treasure-hunt-icon'])


def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl', 'f5')
        return

    if clickBtn(images['connect-wallet'], timeout=10):
        logger('🎉 Connect wallet button detected, logging in!')
        login_attempts = login_attempts + 1
        # TODO mto ele da erro e poco o botao n abre
        # time.sleep(10)

    if clickBtn(images['select-wallet-2'], timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if clickBtn(images['treasure-hunt-icon'], timeout=15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        return
        # click ok button

    if not clickBtn(images['select-wallet-1-no-hover'], ):
        if clickBtn(images['select-wallet-1-hover'], threshold=ct['select_wallet_buttons']):
            pass
            # o ideal era que ele alternasse entre checar cada um dos 2 por um tempo
            # print('sleep in case there is no metamask text removed')
            # time.sleep(20)
    else:
        pass
        # print('sleep in case there is no metamask text removed')
        # time.sleep(20)

    if clickBtn(images['select-wallet-2'], timeout=20):
        login_attempts = login_attempts + 1
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        # time.sleep(25)
        if clickBtn(images['treasure-hunt-icon'], timeout=25):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        # time.sleep(15)

    if clickBtn(images['ok'], timeout=5):
        pass
        # time.sleep(15)
        # print('ok button clicked')


def sendHeroesHome():
    if not ch['enable']:
        return
    heroes_positions = []
    for hero in home_heroes:
        hero_positions = positions(hero, threshold=ch['hero_threshold'])
        if not len(hero_positions) == 0:
            # TODO maybe pick up match with most wheight instead of first
            hero_position = hero_positions[0]
            heroes_positions.append(hero_position)

    n = len(heroes_positions)
    if n == 0:
        print('No heroes that should be sent home found.')
        return
    print(' %d heroes that should be sent home found' % n)
    # if send-home button exists, the hero is not home
    go_home_buttons = positions(
        images['send-home'], threshold=ch['home_button_threshold'])
    # TODO pass it as an argument for both this and the other function that uses it
    go_work_buttons = positions(
        images['go-work'], threshold=ct['go_to_work_btn'])

    for position in heroes_positions:
        if not isHome(position, go_home_buttons):
            print(isWorking(position, go_work_buttons))
            if(not isWorking(position, go_work_buttons)):
                print('hero not working, sending him home')
                moveToWithRandomness(
                    go_home_buttons[0][0]+go_home_buttons[0][2]/2, position[1]+position[3]/2, 1)
                pyautogui.click()
            else:
                print('hero working, not sending him home(no dark work button)')
        else:
            print('hero already home, or home full(no dark home button)')


def checkChests():
    logger('🏢 Search for baus to map')

    purpleChest = positions(images['bau-roxo'], threshold=ct['bau_roxo'])
    purpleMiddleLifeChest = positions(
        images['bau-roxo-50'], threshold=ct['bau_roxo_50'])
    purpleMiddleLessLifeChest = positions(
        images['bau-roxo-less-50'], threshold=ct['bau_roxo_50'])

    goldChest = positions(images['bau-gold'], threshold=ct['bau_gold'])
    goldMiddleLifeChest = positions(
        images['bau-gold-50'], threshold=ct['bau_gold_50'])

    blueChest = positions(images['bau-blue'], threshold=ct['bau_blue'])
    blueMiddleLifeChest = positions(
        images['bau-blue-50'], threshold=ct['bau_blue_50'])

    logger('🟪 %d baus roxo detected' % len(purpleChest))
    logger('🟪 %d baus roxo meia vida detected' % len(purpleMiddleLifeChest))
    logger('🟪 %d baus roxo menos da metade de vida detected' %
           len(purpleMiddleLessLifeChest))

    logger('🟨 %d baus gold detected' % len(goldChest))
    logger('🟨 %d baus gold meia vida detected' % len(goldMiddleLifeChest))

    logger('🟦 %d baus blue detected' % len(blueChest))
    logger('🟦 %d baus blue meia vida detected' % len(blueMiddleLifeChest))

    hasChestsLessMiddleLifes = len(purpleMiddleLessLifeChest) > 0

    hasChestsMiddleLifes = len(purpleMiddleLifeChest) > 0 or len(
        goldMiddleLifeChest) > 0 or len(blueMiddleLifeChest) > 0 or len(blueMiddleLifeChest) > 0

    hasChestsFullLifes = len(purpleChest) > 0 or len(
        goldChest) > 0 or len(blueChest) > 0

    global response
    if (hasChestsMiddleLifes or hasChestsLessMiddleLifes or hasChestsFullLifes):
        valueChestsLessMiddleLifes = len(purpleMiddleLessLifeChest)

        valueChestsMiddleLifes = len(purpleMiddleLifeChest) + len(
            goldMiddleLifeChest) + len(blueMiddleLifeChest) + len(blueMiddleLifeChest)

        valueChestsFullLifes = len(purpleChest) + len(
            goldChest) + len(blueChest)

        response = (
            (
                valueChestsLessMiddleLifes
                + valueChestsMiddleLifes
                + valueChestsFullLifes
            ) * 100
        ) / (len(purpleChest) + len(goldChest) + len(blueChest))
    else:
        response = 0

    logger('Response of checkChest {}'.format(response))
    return response


def clickRedBarButtons():
    # ele clicka nos q tao trabaiano mas axo q n importa
    offset = 200

    red_bars = positions(images['red-bar'], threshold=ct['red_bar'])
    logger('🟥 %d red bars detected' % len(red_bars))
    buttons = positions(images['go-rest'], threshold=ct['go_to_rest_btn'])
    logger('🔋 %d rest buttons detected' % len(buttons))

    buttons_work = positions(images['go-work'], threshold=ct['go_to_work_btn'])

    not_resting_red_bars = []
    for bar in red_bars:
        if (isWorking(bar, buttons_work)):
            not_resting_red_bars.append(bar)

    if len(not_resting_red_bars) > 0:
        logger('🔋 %d buttons with red bar detected' %
               len(not_resting_red_bars))
        logger('👆 Clicking in %d heroes' % len(not_resting_red_bars))

    # se tiver botao com y maior que bar y-10 e menor que y+10
    global hero_rest_clicks
    hero_clicks_cnt = 0

    for (x, y, w, h) in not_resting_red_bars:
        # isWorking(y, buttons)
        moveToWithRandomness(x+offset+(w/2), y+(h/2), 1)
        pyautogui.click()
        hero_rest_clicks += 1
        hero_clicks_cnt = hero_clicks_cnt + 1
        if hero_clicks_cnt > 20:
            logger(
                '⚠️ Too many hero clicks, try to increase the go_to_work_btn threshold')
            return
        #cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_resting_red_bars)
    # while (True):
    #     buttons = positions(images['go-rest'], threshold=ct['go_to_rest_btn'])
    #     if len(buttons) > 0:
    #         clickBtn(images['go-rest'])
    #     else:
    #         return


def refreshHeroes():
    logger('🏢 Search for heroes to work')

    global chests
    chests = checkChests()

    goToHeroes()

    if c['select_heroes_mode'] != "full":
        logger('⚒️ Sending heroes with red stamina bar to rest', 'red')

    if c['select_heroes_mode'] == "full":
        logger('⚒️ Sending heroes with full stamina bar to work', 'green')
    elif c['select_heroes_mode'] == "green":
        logger('⚒️ Sending heroes with green stamina bar to work', 'green')
    else:
        logger('⚒️ Sending all heroes to work', 'green')

    buttonsClicked = 1
    empty_scrolls_attempts = c['scroll_attemps']

    while(empty_scrolls_attempts > 0):
        if c['select_heroes_mode'] != "full":
            clickRedBarButtons()

        if c['select_heroes_mode'] == 'full':
            buttonsClicked = clickFullBarButtons()
        elif c['select_heroes_mode'] == 'green':
            buttonsClicked = clickGreenBarButtons(chests)
        else:
            buttonsClicked = clickButtons()

        sendHeroesHome()

        if buttonsClicked == 0:
            empty_scrolls_attempts -= 1

        scroll()
        time.sleep(2)

    logger('💪 {} heroes sent to work'.format(hero_clicks))

    logger('💪 {} heroes sent to work'.format(hero_rest_clicks))

    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " +
                         account_id + " 💪 AMOUNT HEROES SENDED {} TO WORK".format(hero_clicks))

    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"], "BOMBCRYPTO " +
                         account_id + " 🔋 AMOUNT HEROES SENDED {} TO  REST".format(hero_rest_clicks))

    goToGame()


def takeScreenshot():
    logger('\n Taking screenshot')
    myScreenshot = pyautogui.screenshot()
    myScreenshot.save(r'screen.png')
    photo = open('screen.png', 'rb')
    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"],
                         "BOMBCRYPTO " + account_id + " 📸 screenshot")
        bot.send_photo(c["telegram_chat_id"], photo)


def sendBalance():
    logger('\n Taking screenshot balance')
    if clickBtn(images['balance'], timeout=10, threshold=0.6):
        time.sleep(3)
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'screen.png')
        photo = open('screen.png', 'rb')
        if(c["log_telegram"] == True):
            bot.send_message(c["telegram_chat_id"],
                             "BOMBCRYPTO " + account_id + " 📈 BALANCE")
            bot.send_photo(c["telegram_chat_id"], photo)
        clickBtn(images['x'])
        clickBtn(images['x'])


def main():
    """Main execution setup and loop"""
    # ==Setup==
    global hero_clicks
    global hero_rest_clicks
    global login_attempts
    global last_log_is_progress
    global amount_maps_passed
    hero_clicks = 0
    hero_rest_clicks = 0
    login_attempts = 0
    last_log_is_progress = False
    amount_maps_passed = 0

    global images
    images = load_images()

    if ch['enable']:
        global home_heroes
        home_heroes = loadHeroesToSendHome()
    else:
        print('>>---> Home feature not enabled')
    print('\n')

    print(cat)
    time.sleep(7)
    t = c['time_intervals']

    last = {
        "login": 0,
        "heroes": 0,
        "new_map": 0,
        "check_for_captcha": 0,
        "refresh_heroes": 0,
        "screen": 0,
        "balance": 0
    }
    # =========

    if(c["log_telegram"] == True):
        bot.send_message(c["telegram_chat_id"],
                         "BOMBCRYPTO " + account_id + " 🚀 started")

    login()

    time.sleep(3)

    while True:
        now = time.time()

        if now - last["check_for_captcha"] > addRandomness(t['check_for_captcha'] * 60):
            last["check_for_captcha"] = now

        if now - last["heroes"] > addRandomness(t['send_heroes_for_work'] * 60):
            last["heroes"] = now
            refreshHeroes()
            hero_clicks = 0
            hero_rest_clicks = 0

        if now - last["screen"] > 60 * 60:
            last["screen"] = now
            takeScreenshot()
            logger("\n")

        if now - last["balance"] > 60 * 60:
            last["balance"] = now
            sendBalance()
            logger("\n")

        if now - last["login"] > addRandomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            last["login"] = now
            login()

        if now - last["new_map"] > t['check_for_new_map_button']:
            last["new_map"] = now

            if clickBtn(images['new-map']):
                amount_maps_passed += 1
                loggerMapClicked(bot, account_id, '🗺️ New Map button clicked! {} maps passed'.format(
                    amount_maps_passed))

        if now - last["refresh_heroes"] > addRandomness(t['refresh_heroes_positions'] * 60):
            last["refresh_heroes"] = now
            refreshHeroesPositions()

        # clickBtn(teasureHunt)
        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)


if __name__ == '__main__':

    main()


# cv2.imshow('img',sct_img)
# cv2.waitKey()

# colocar o botao em pt
# soh resetar posiçoes se n tiver clickado em newmap em x segundos
