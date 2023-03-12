import os
import sys
import time
import logging
import discord
import asyncio
import functools
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageChops
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
USER_ID = int(os.getenv("USER_ID"))
COMMON_PATH = "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/androidx.drawerlayout.widget.DrawerLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.FrameLayout/android.widget.LinearLayout"
desired_capabilities = {
    "platformName": "Android",
    "platformVersion": "13",
    "deviceName": "Android Emulator",
    "newCommandTimeout": 900,
}

client = discord.Client(intents=discord.Intents.all())
driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_capabilities)
driver.update_settings({"waitForIdleTimeout": 100})  # click delay 문제 해결용

logging.basicConfig(
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(os.path.join(os.path.dirname(__file__), "run.log"))],
    format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def tex_to_png(eq: str, current_time: str) -> str:
    font_path = os.path.join(os.path.dirname(__file__), "Pretendard-Regular.otf")
    fm.fontManager.addfont(font_path)
    plt.switch_backend("Agg")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = fm.FontProperties(fname=font_path).get_name()
    plt.rcParams["mathtext.fontset"] = "cm"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, eq, fontsize=10)
    file_name = os.path.join(os.path.dirname(__file__), "images_latex", f"{current_time}.png")
    fig.savefig(file_name, dpi=400, transparent=False, format="png", bbox_inches="tight", pad_inches=0.1)

    return f"{current_time}.png"

def send_img(img_cnt: int):
    driver.find_element(By.ID, "net.megastudy.qube:id/ibtn_input_more").click()
    driver.find_element(By.ID, "net.megastudy.qube:id/btn_media_gallery").click()
    driver.find_element(By.ID, "net.megastudy.qube:id/sp_sort_type").click()
    folder_list = driver.find_elements(By.XPATH, "/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.TextView")
    for item in folder_list:
        if item.get_attribute("text") == "QubeImages":
            item.click()
            break
    time.sleep(1)  # 삭제하지 말 것
    image_list = driver.find_elements(By.ID, "net.megastudy.qube:id/iv_gallery_item_image")
    for i in range(1, img_cnt + 1):
        image_list[img_cnt - i].click()
    driver.find_element(By.ID, "net.megastudy.qube:id/tv_btn_save").click()
    driver.find_element(By.ID, "net.megastudy.qube:id/btn_image_save").click()

# blocking function을 non-blocking하게 실행
async def run_blocking(blocking_func, *args, **kwargs):
    func = functools.partial(blocking_func, *args, **kwargs)
    return await client.loop.run_in_executor(None, func)

class Button_finish(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=3600)
        self.channel = channel
        self.value = None

    @discord.ui.button(label="종료", style=discord.ButtonStyle.grey, custom_id="finish")
    async def callback_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "풀이 종료 선택")
        self.value = True
        self.stop()

    async def on_timeout(self):
        await self.channel.send("Timeout!")
        await run_blocking(logging.info, "timeout on button_finish")
        self.stop()


class Button_yn(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=3600)
        self.channel = channel
        self.value = None

    @discord.ui.button(label="예", style=discord.ButtonStyle.green, custom_id="yes")
    async def callback_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "예 선택")
        self.value = True
        self.stop()

    @discord.ui.button(label="아니오", style=discord.ButtonStyle.red, custom_id="no")
    async def callback_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "아니오 선택")
        self.value = False
        self.stop()

    async def on_timeout(self):
        await self.channel.send("Timeout!")
        await run_blocking(logging.info, "timeout on button_yn")
        self.stop()


class Button_solve(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=3600)
        self.channel = channel
        self.value = None

    @discord.ui.button(label="지금 풀기", style=discord.ButtonStyle.blurple, custom_id="button1")
    async def callback_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "지금 풀기 선택")
        self.value = 1
        await self.channel.send(embed=discord.Embed(title="보낼 답을 입력하거나 풀이 사진을 보내세요."), content="")
        cnt = 0

        while True:
            if cnt == 0:
                answer = await client.wait_for("message", check=lambda m: m.author.id == USER_ID, timeout=600.0)
            else:
                view_finish = Button_finish(self.channel)
                await self.channel.send(embed=discord.Embed(title="모두 답했으면 종료를 누르고,\n그렇지 않다면 계속 답하세요."), content="", view=view_finish)
                events = {asyncio.create_task(client.wait_for("message", check=lambda m: m.author.id == USER_ID, timeout=600.0)),
                          asyncio.create_task(view_finish.wait())}
                done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
                for future in pending:  # 진행중인 작업 취소
                    future.cancel()

                if view_finish.value == True:  # 버튼을 눌렀을 경우
                    break

                # 텍스트 or 이미지를 보냈을 경우
                answer = done.pop().result()
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 이미지를 보냈을 경우
            if answer.attachments:
                await run_blocking(logging.info, f"풀이 수신됨: 사진 {len(answer.attachments)}장")
                for image in answer.attachments:
                    file_name = os.path.join(os.path.dirname(__file__), "images_tea", image.filename)
                    await image.save(file_name)
                    driver.push_file(f"/storage/emulated/0/DCIM/QubeImages/{image.filename}", source_path=file_name)
                await run_blocking(logging.info, "사진 저장 완료")
                await run_blocking(send_img, len(answer.attachments))
                await run_blocking(logging.info, "사진 전송 완료")

            else:  # 텍스트를 보냈을 경우
                answer.content = fr"{answer.content}"

                # 수식 포함
                if "$" in answer.content:
                    await run_blocking(logging.info, "풀이 수신됨 (수식): " + answer.content)
                    try:
                        img_name = await run_blocking(tex_to_png, answer.content, current_time)

                    except:
                        await run_blocking(logging.info, "올바르지 않은 수식")
                        view_yn = Button_yn(self.channel)
                        await self.channel.send(embed=discord.Embed(title="올바르지 않은 수식입니다. 텍스트로 보낼까요?"), content="", view=view_yn)
                        await view_yn.wait()

                        if view_yn.value == True:
                            driver.find_element(By.ID, "net.megastudy.qube:id/et_input_text").send_keys(answer.content)
                            driver.find_element(By.ID, "net.megastudy.qube:id/btn_input_send").click()
                            await run_blocking(logging.info, "텍스트 전송 완료")
                        else:
                            await run_blocking(logging.info, "텍스트 전송 취소")

                    else:
                        file_name = os.path.join(os.path.dirname(__file__), "images_latex", f"{current_time}.png")
                        await run_blocking(logging.info, "수식 이미지 변환 완료")
                        await self.channel.send(file=discord.File(file_name))
                        view_yn = Button_yn(self.channel)
                        await self.channel.send(embed=discord.Embed(title="수식이 포함된 해당 이미지를 풀이로 보낼까요?"), content="", view=view_yn)
                        await view_yn.wait()

                        if view_yn.value == True:
                            driver.push_file(f"/storage/emulated/0/DCIM/QubeImages/{img_name}", source_path=file_name)
                            await run_blocking(send_img, 1)
                            await run_blocking(logging.info, "수식 이미지 전송 완료")
                        else:
                            await run_blocking(logging.info, "수식 이미지 전송 취소")

                # 수식 미포함
                else:
                    await run_blocking(logging.info, "풀이 수신됨 (텍스트): " + answer.content)
                    driver.find_element(By.ID, "net.megastudy.qube:id/et_input_text").send_keys(answer.content)
                    driver.find_element(By.ID, "net.megastudy.qube:id/btn_input_send").click()
                    await run_blocking(logging.info, "텍스트 전송 완료")

                cnt += 1

        await asyncio.sleep(1)  # 삭제하지 말 것
        driver.find_element(By.ID, "net.megastudy.qube:id/btn_explan_complete").click()
        driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
        driver.find_element(By.ID, "net.megastudy.qube:id/ibtn_close").click()
        await run_blocking(logging.info, "답변 완료됨")
        # solved = len(questions)
        await asyncio.sleep(4)  # 내가 답변한 걸 다시 클릭하는 것 방지

    @discord.ui.button(label="나중에 풀기", style=discord.ButtonStyle.green, custom_id="button2")
    async def callback_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        button1 = [x for x in self.children if x.custom_id=="button1"][0]
        if " ✅" in button1.label:
            button1.label = button1.label[:-2]
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "나중에 풀기 선택")
        self.value = 2
        self.stop()

    @discord.ui.button(label="포기하기", style=discord.ButtonStyle.red, custom_id="button3")
    async def callback_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.label += " ✅"
        button1 = [x for x in self.children if x.custom_id=="button1"][0]
        if " ✅" in button1.label:
            button1.label = button1.label[:-2]
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(view=self)
        await run_blocking(logging.info, "포기하기 선택")
        self.value = 3
        self.stop()

    async def on_timeout(self):
        await self.channel.send("Timeout!")
        await run_blocking(logging.info, "timeout on button_solve")
        self.stop()


@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    await run_blocking(logging.info, f"{client.user} has connected to Discord")
    solved = None  # 체크표시된 문제 수
    only_special = False  # Special Question만 있고 Qube Question이 비어있는 경우인지

    while True:
        stale_exception = False  # StaleElementReferenceException 대응

        ## Case 1. 모든 문제가 해결되었고 only_special이 False일 때
        if solved is None or solved == 0:
            if only_special is False:
                try:
                    driver.find_element(By.XPATH, COMMON_PATH + "/android.view.ViewGroup/android.widget.LinearLayout/android.widget.TextView[1]")
                    await run_blocking(logging.info, "신규 문제 없음")
                    solved = 0

                    # 새로고침 중이라면, pass
                    try:
                        driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")
                        await run_blocking(logging.info, "현재 새로고침 중")

                    # 새로고침 중이 아니라면 새로고침 하기
                    except NoSuchElementException:
                        driver.swipe(500, 500, 500, 1000, 100)
                        await run_blocking(logging.info, "새로고침 시도")

                # 한 문제 이상이 새로 들어왔거나, Special Question만 있는 경우
                except NoSuchElementException:
                    pass

        # 문제 목록 반환
        questions = driver.find_elements(By.XPATH, COMMON_PATH + "/android.widget.RelativeLayout[2]/android.widget.LinearLayout/android.widget.GridView/android.widget.FrameLayout")

        # solved가 None이라면, 변수 할당
        if solved is None:
            solved = len(questions)

        # solved가 None이 아니고, questions 목록이 비어있다면
        elif not questions:
            solved = 0

            # Special Question만 있고 Qube Question이 비어있는 경우
            try:
                driver.find_element(By.ID, "net.megastudy.qube:id/home_main_top_refresh")
                only_special = True

            except NoSuchElementException:
                only_special = False

        ## Case 2. 한 문제 이상이 해결 중일 때 + only_special이 True일 떄
        if questions or only_special is True:
            # Case 2-1. 새로운 문제가 들어왔을 때
            if len(questions) > solved:
                await run_blocking(logging.warning, "신규 문제 탐지")
                # 가장 뒤에서부터 신규 문제 탐색
                for i in range(1, len(questions) + 1):
                    # 문제가 해결되었는지 점검
                    try:
                        questions[-i].find_element(By.XPATH, ".//android.widget.ImageView")

                    # 해결되지 않았다면
                    except NoSuchElementException:
                        questions[-i].click()
                        # await asyncio.sleep(2)  # 또 새로고침하는 것 방지
                        await run_blocking(logging.warning, "신규 문제 클릭")
                        break

                    # 선점 실패되어 solved = 0으로 돌아간 경우 OR 기타 버그로 questions[-i]가 접근 불가능한 경우
                    except StaleElementReferenceException:
                        await run_blocking(logging.warning, "StaleElementReferenceException")
                        stale_exception = True
                        break

                if stale_exception is True:
                    continue  # 다음 while로 가기

                # 새로고침 중인 상태에서 클릭 시, 로딩이 모두 완료된 후에 하도록 함
                while True:
                    try:
                        driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")
                        await run_blocking(logging.info, "새로고침 될 때까지 기다림")

                    except NoSuchElementException:
                        await run_blocking(logging.info, "새로고침 완료")
                        break

                # Case 2-1-1. 다른 마스터가 답변 중일 때
                try:
                    driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
                    await run_blocking(logging.warning, "문제 선점 실패 (일반)")
                    await asyncio.sleep(3)  # 같은 문제 두 번 클릭 방지

                # Case 2-1-2. 다른 마스터가 답변 중이지 않을 때
                except NoSuchElementException:
                    driver.implicitly_wait(2)

                    try:
                        # Step 1. 선점 성공 알림 보내기
                        await run_blocking(logging.warning, "문제 선점 성공")
                        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                        await channel.send(embed=discord.Embed(title="새로운 문제가 도착했습니다."), content="")

                        # Step 2. 문제 이미지 보내기
                        thumbs = driver.find_elements(By.ID, "net.megastudy.qube:id/iv_chat_image")
                        await run_blocking(logging.info, "이미지 목록 반환 완료")
                        for i in range(len(thumbs)):
                            img_num = str(i + 1)
                            thumbs[i].click()  # StaleElementException 에러가 발생한 이력 있음
                            await asyncio.sleep(1)  # 이미지 로딩되기까지 기다림
                            image = driver.find_element(By.ID, "net.megastudy.qube:id/image")
                            file_name = os.path.join(os.path.dirname(__file__), "images_stu", f"{current_time}-{img_num}.png")
                            with open(file_name, "wb") as screenshot:
                                screenshot.write(image.screenshot_as_png)

                            # 스크린샷의 white 여백 제거
                            img = Image.open(file_name).convert("RGB")  # 원래 RGBA임
                            bg = Image.new(img.mode, img.size, (255, 255, 255))
                            diff = ImageChops.difference(img, bg)
                            bbox = ImageChops.add(diff, diff, 2.0, -100).getbbox()
                            img.crop(bbox).save(file_name)  # 파일 덮어쓰기

                            await channel.send(file=discord.File(file_name))
                            await run_blocking(logging.info, f"총 {len(thumbs)} 중 {img_num}번째 이미지 전송 완료")
                            driver.find_element(By.ID, "net.megastudy.qube:id/btn_close").click()
                            await asyncio.sleep(1)

                        # Step 3. 문제 본문 보내기
                        messages = [item.get_attribute("text") for item in driver.find_elements(By.ID, "net.megastudy.qube:id/tv_chat_text")]
                        await channel.send("\n".join(messages))
                        await run_blocking(logging.info, "본문 전송 완료")

                        # Step 4. 풀이 옵션 선택
                        view_solve = Button_solve(channel)
                        await channel.send(embed=discord.Embed(title="풀이 옵션 선택"), content="", view=view_solve)
                        await view_solve.wait()
                        await run_blocking(logging.info, "풀이 옵션 전송 완료")
                        # if view_solve.value == 1: async def 안에 있음 ('지금 풀기' 도중 다른 옵션으로 전환할 가능성 마련)
                        if view_solve.value == 2:
                            await run_blocking(logging.info, "2번 선택")
                            driver.terminate_app("net.megastudy.qube")  # 앱을 재실행하여 다른 문제를 계속 찾기 위함
                            driver.activate_app("net.megastudy.qube")
                            await run_blocking(logging.info, "앱 재실행 중")
                            # solved = len(questions)
                            await asyncio.sleep(5)  # 앱이 재시작될 동안 기다림

                            # 해결 완료 후 해시태그 입력 팝업창이 뜰 경우
                            try:
                                driver.find_element(By.ID, "net.megastudy.qube:id/bt_close").click()
                                await channel.send(embed=discord.Embed(title="앱에 접속하여 해시태그를 입력해주세요."), content="")
                                await run_blocking(logging.info, "해시태그 팝업창 뜸")

                            except NoSuchElementException:
                                pass

                        elif view_solve.value == 3:
                            await run_blocking(logging.info, "3번 선택")
                            driver.find_element(By.ID, "net.megastudy.qube:id/btn_explan_cancel").click()
                            driver.find_element(By.ID, "net.megastudy.qube:id/bt_positive").click()
                            await run_blocking(logging.info, "문제 포기 완료")
                            await asyncio.sleep(4)  # 포기 이후 메인 화면 로딩까지 기다림

                    except NoSuchElementException:
                        # Toast인 경우
                        try:
                            driver.find_element(By.XPATH, "/hierarchy/android.widget.Toast")
                            await run_blocking(logging.warning, "문제 선점 실패 (Toast)")
                            await channel.send(embed=discord.Embed(title="해당 문제는 다른 마스터가 이미 선점하였습니다."), content="")

                        # 기타 상황에 대한 예외처리
                        except NoSuchElementException:
                            await run_blocking(logging.error, "예외처리 상황 발생")

                    driver.implicitly_wait(0)

            # Case 2-2. 그대로라면
            elif len(questions) == solved:
                await run_blocking(logging.info, "신규 문제 없음")  # heartbeat block 방지하기 위해 run_blocking 처리

            # Case 2-3. 해결 중인 문제가 줄어들었을 때
            elif len(questions) < solved and len(questions) > 0:
                solved = len(questions)
                await run_blocking(logging.warning, "문제 수 줄어듦")

            # 새로고침 중이라면, pass
            try:
                driver.find_element(By.ID, "net.megastudy.qube:id/fl_progress")
                await run_blocking(logging.info, "현재 새로고침 중")

            # 새로고침 중이 아니라면 새로고침 하기
            except NoSuchElementException:
                try:
                    driver.find_element(By.ID, "net.megastudy.qube:id/home_main_top_refresh").click()
                    await run_blocking(logging.info, "새로고침 시도")

                # 기타 상황에 대한 예외처리 (element가 아직 로딩이 안 되었는 등)
                except NoSuchElementException:
                    await run_blocking(logging.error, "예외처리 상황 발생")


if __name__ == "__main__":
    client.run(TOKEN)
