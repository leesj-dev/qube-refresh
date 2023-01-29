import os
import discord
import asyncio
import functools
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageChops
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
USER_ID = int(os.getenv("USER_ID"))
COMMON_PATH = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/androidx.drawerlayout.widget.DrawerLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.LinearLayout"
desired_capabilities = {
    "platformName": "Android",
    "platformVersion": "13",
    "deviceName": "Android Emulator",
}

client = discord.Client(intents=discord.Intents.all())
driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_capabilities)

# 로딩 중인지 확인 (*blocking function)
def chk_load():
    while True:
        try:
            driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")
        except NoSuchElementException:
            break


# 이미지 white 여백 제거 (*blocking function)
def trim(path):
    img = Image.open(path).convert("RGB")  # 원래 RGBA임
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = ImageChops.add(diff, diff, 2.0, -100).getbbox()
    img.crop(bbox).save(path)  # 파일 덮어쓰기


# blocking function을 non-blocking하게 실행
async def run_blocking(blocking_func, *args, **kwargs):
    func = functools.partial(blocking_func, *args, **kwargs)
    return await client.loop.run_in_executor(None, func)


@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    await run_blocking(print, f"{client.user} has connected to Discord")
    solved = None  # 처음 실행 시에는 None으로 할당

    while True:
        ## Case 1. 모든 문제가 해결된 상태일 때
        if solved is None or solved == 0:
            try:
                driver.find_element(By.XPATH, COMMON_PATH + "/android.view.ViewGroup/android.widget.LinearLayout/android.widget.TextView[1]")
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
                await run_blocking(print, f"문제 없음 [{current_time}]")
                solved = 0
                driver.swipe(500, 500, 500, 1000, 100)
                await run_blocking(chk_load)

            # 한 문제 이상이 새로 들어왔을 때 -> Case 2
            except NoSuchElementException:
                if solved is None:
                    # solved가 None이라면, 변수 할당 (뒷부분과 중복이 일어나지만 어쩔 수 없음; 케이스 분류 시 코드가 너무 복잡해짐)
                    questions = driver.find_elements(By.XPATH, COMMON_PATH + "/android.widget.RelativeLayout[2]/android.widget.LinearLayout/android.widget.GridView/android.widget.FrameLayout")
                    solved = len(questions)

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
                    except NoSuchElementException:
                        questions[-i].click()
                        break

                # 새로고침 중인 상태에서 클릭 시, 로딩이 모두 완료된 후에 하도록 함
                await run_blocking(chk_load)

                # Case 2-2-1. 다른 마스터가 답변 중일 때
                try:
                    driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
                    await run_blocking(print, f"문제 선점 실패 [{current_time}]")
                    await asyncio.sleep(3)

                # Case 2-2-2. 다른 마스터가 답변 중이지 않을 때
                except NoSuchElementException:
                    # Case 2-2-2-1. 내가 이미 답변한 문제인지 확인
                    try:
                        driver.find_element(By.ID, "net.megastudy.qube:id/ibtn_close").click()

                    # Case 2-2-2-2. 내가 답변하지 않은 문제라면
                    except NoSuchElementException:
                        driver.implicitly_wait(2)

                        # Step 1. 선점 성공 알림 보내기
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
                        await run_blocking(print, f"문제 선점 성공 [{current_time}]")
                        await channel.send(f"새로운 문제가 도착했습니다 [{current_time}]")

                        # Step 2. 문제 이미지 보내기
                        thumbs = driver.find_elements(By.ID, "net.megastudy.qube:id/iv_chat_image")
                        for i in range(len(thumbs)):
                            img_num = str(i + 1)
                            file_name = os.path.join("images", f"{current_time}-{img_num}.png")
                            thumbs[i].click()
                            image = driver.find_element(By.ID, "net.megastudy.qube:id/image")
                            with open(file_name, "wb") as screenshot:
                                screenshot.write(image.screenshot_as_png)
                            await run_blocking(trim, file_name)
                            await channel.send(file=discord.File(file_name))
                            driver.find_element(By.ID, "net.megastudy.qube:id/btn_close").click()

                        # Step 3. 문제 본문 보내기
                        messages = [
                            item.get_attribute("text")
                            for item in driver.find_elements(By.ID, "net.megastudy.qube:id/tv_chat_text")
                        ]
                        await channel.send("\n".join(messages))

                        # Step 4. 풀이 옵션 선택
                        await channel.send("지금 풀기는 1, 나중에 풀기는 2, 포기는 3을 입력하세요.")
                        while True:  # 제대로 된 input값이 들어올 때까지 반복
                            proceed = await client.wait_for("message", check=lambda m: m.author.id == USER_ID, timeout=300.0)

                            if proceed.content == "1":  # 확인 필요함
                                await channel.send("*")  # 임시 (just in case)  # 보내실 답을 입력해주세요.
                                answer = await client.wait_for("message", check=lambda m: m.author.id == USER_ID, timeout=300.0)
                                driver.find_element(By.ID, "net.megastudy.qube:id/et_input_text").send_keys(answer.content)
                                driver.find_element(By.ID, "net.megastudy.qube:id/btn_input_send").click()
                                driver.find_element(By.ID, "net.megastudy.qube:id/btn_explan_complete").click()
                                break

                            elif proceed.content == "2":  # 이상 없음
                                driver.terminate_app("net.megastudy.qube")  # 앱 재실행 (다른 문제를 계속 찾기 위함)
                                driver.activate_app("net.megastudy.qube")
                                solved = len(questions)
                                await asyncio.sleep(5)  # 앱이 재시작될 동안 기다림

                                # 답변 완료 후 해시태그 입력 팝업창이 뜰 경우
                                try:
                                    driver.find_element(By.ID, "net.megastudy.qube:id/bt_close").click()
                                except:
                                    pass

                                break

                            elif proceed.content == "3":  # 이상 없음
                                driver.find_element(By.ID, "net.megastudy.qube:id/btn_explan_cancel").click()
                                driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
                                break

                            else:
                                await channel.send("다시 입력해주세요.")

            # Case 2-3. 그대로라면
            elif len(questions) == solved:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-4]
                await run_blocking(print, f"문제 없음 [{current_time}]")  # heartbeat block 방지하기 위해 run_blocking 처리

            # Case 2-4. 해결 중인 문제가 줄어들었을 때
            else:
                solved = len(questions)
                await channel.send("Qube 앱에 접속하여 해시태그를 입력해주세요.")

            driver.implicitly_wait(0)

            # 새로고침 중이라면, pass
            try:
                driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")

            # 새로고침 중이 아니라면 새로고침 하기
            except NoSuchElementException:
                try:
                    driver.find_element(By.ID, "net.megastudy.qube:id/home_main_top_refresh").click()

                # 기타 상황에 대한 예외처리
                except NoSuchElementException:
                    pass


if __name__ == "__main__":
    client.run(TOKEN)