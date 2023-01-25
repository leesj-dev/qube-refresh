import os
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
solved = int(input("현재 답변 중인 문제 수를 입력하세요 : "))

desired_capabilities = {
    "platformName": "Android",
    "platformVersion": "13",
    "deviceName": "Android Emulator",
}

driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_capabilities)
COMMON_PATH = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/androidx.drawerlayout.widget.DrawerLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.LinearLayout"

# 로딩 중인지 확인
def chk_load():
    while True:
        # current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        try:
            # print("로딩중 [" + current_time + "]")
            driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")

        except NoSuchElementException:
            break


while True:
    ## Case 1. 모든 문제가 해결된 상태일 때
    if solved == 0:
        try:
            driver.find_element(By.XPATH, COMMON_PATH + "/android.view.ViewGroup/android.widget.LinearLayout/android.widget.TextView[1]")

        # 한 문제 이상이 새로 들어왔을 때 -> Case 2
        except NoSuchElementException:
            pass

        else:
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("문제 없음 [" + current_time + "]")
            driver.swipe(500, 500, 500, 1000, 100)
            chk_load()

    ## Case 2. 한 문제 이상이 해결 중일 때
    # 문제 목록 반환
    questions = driver.find_elements(By.XPATH, COMMON_PATH + "/android.widget.RelativeLayout[2]/android.widget.LinearLayout/android.widget.GridView/android.widget.FrameLayout")

    # Case 2-1. 아예 비어있을 때
    if not questions:
        solved = 0

    else:
        # Case 2-2. 새로운 문제가 들어왔을 때
        if len(questions) > solved:

            # 가장 뒤에서부터 신규 문제 탐색
            for i in range(1, len(questions) + 1):
                # 문제가 해결되었는지 점검
                try:
                    questions[-i].find_element(By.XPATH, ".//android.widget.ImageView")

                # 해결되지 않았다면
                except:
                    questions[-i].click()
                    break

            # Case 2-2-1. 다른 마스터가 답변 중일 때
            try:
                driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
                current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                print("문제 선점 실패 [" + current_time + "]")
                chk_load()

            # Case 2-2-2. 다른 마스터가 답변 중이지 않을 때
            except NoSuchElementException:
                # Case 2-2-2-1. 내가 이미 답변한 문제인지 확인
                try:
                    driver.find_element(By.ID, "net.megastudy.qube:id/ibtn_close").click()
                    chk_load()

                # Case 2-2-2-2. 내가 답변하지 않은 문제라면
                except NoSuchElementException:
                    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print("문제 선점 성공 [" + current_time + "]")

                    while True:
                        proceed = input("풀기는 Y, 포기하기는 N을 입력하세요: ")
                        if proceed == "Y":
                            # 앱 재실행 (다른 문제를 계속 찾기 위함)
                            driver.terminate_app("net.megastudy.qube")
                            driver.activate_app("net.megastudy.qube")
                            input("풀이가 완료되면 아무 키나 누르세요: ")
                            solved = len(questions)
                            break

                        elif proceed == "N":
                            break  # 포기하기 버튼 누르기 추가

                        else:
                            print("다시 입력해주세요.")

        # Case 2-3. 그대로라면
        elif len(questions) == solved:
            current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("문제 없음 [" + current_time + "]")

        # Case 2-4. 해결된 문제가 늘어났을 때
        else:
            solved = len(questions)

        # 새로고침 시도
        try:
            driver.find_element(By.ID, "net.megastudy.qube:id/home_main_top_refresh").click()
            chk_load()

        # 모든 문제가 해결된 경우
        except NoSuchElementException:
            solved = 0
