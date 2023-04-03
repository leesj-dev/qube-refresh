from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

desired_capabilities = {
    "platformName": "Android",
    "platformVersion": "13",
    "deviceName": "Android Emulator",
    "newCommandTimeout": 900,
}


def find_exists(parent, id):
    try:
        parent.find_element(By.ID, id)
        return True
    except NoSuchElementException:
        return False

driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_capabilities)
driver.update_settings({"waitForIdleTimeout": 100})  # click delay 문제 해결용
# driver.find_element(By.ID, "net.megastudy.qube:id/tv_order_all").click()  # 전체

i = 1
until = 16094
order = dict.fromkeys(range(1, until + 1))
while True:
    while True:
        try:  # progress bar가 존재하는지 확인
            driver.find_element(By.XPATH, "/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/androidx.drawerlayout.widget.DrawerLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.ProgressBar")
        except:
            break

    try:
        parent = driver.find_element(By.XPATH, f"/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/androidx.drawerlayout.widget.DrawerLayout/android.widget.FrameLayout/androidx.viewpager.widget.ViewPager/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.RelativeLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[{i}]")

        rank = int(parent.find_element(By.ID, "net.megastudy.qube:id/tv_profile_rank").get_attribute("text"))  # 순위
        if rank not in order.keys():  # 중복되지 않는 경우
            if rank == 1 or list(sorted(order.keys()))[-1] == rank - 1:
                temp = parent.find_element(By.ID, "net.megastudy.qube:id/tv_profile_title_01").get_attribute("text").split()  # 학교 학과 이름
                school, major, name = temp[0], temp[1], temp[2]
                if "★" in name:
                    name = name[1:]
                    special = True
                else:
                    special = False
                try:
                    teacher = parent.find_element(By.ID, "net.megastudy.qube:id/tv_profile_tag").get_attribute("text").replace(" ", "").split("#")[1:]  # 전문 선생님
                except NoSuchElementException:
                    teacher = []
                answers = int(parent.find_element(By.ID, "net.megastudy.qube:id/tv_profile_answer_count").get_attribute("text"))  # 누적 답변 수
                popular = find_exists(parent, "net.megastudy.qube:id/tv_profile_vogue")
                speed = find_exists(parent, "net.megastudy.qube:id/tv_profile_time")
                satisfaction = find_exists(parent, "net.megastudy.qube:id/tv_profile_satisfaction")
                order[rank] = [school, major, name, special, teacher, answers, popular, speed, satisfaction]
                print(rank, order[rank])
                with open("./result.txt", "a") as f:
                    f.write(str([rank, school, major, name, special, teacher, answers, popular, speed, satisfaction]) + ",\n")

            else:  # 문제를 건너뛴 경우
                i = 1
                driver.swipe(500, 850, 500, 1000, 100)

        elif rank < until:
            driver.swipe(500, 1500, 500, 500, 100)  # 빠르게 밑으로 스크롤

        i += 1

    except:
        if i == 1:  # 윗부분이 잘린 경우
            i += 1
        else:
            i = 1
            driver.swipe(500, 1000, 500, 750, 100)  # 밑으로 스크롤


"""
순위 net.megastudy.qube:id/tv_profile_rank
학교 학과 이름 net.megastudy.qube:id/tv_profile_title_01
전문 마스터 net.megastudy.qube:id/tv_profile_tag
누적 답변 수 net.megastudy.qube:id/tv_profile_answer_count
인기 net.megastudy.qube:id/tv_profile_vogue
속도 net.megastudy.qube:id/tv_profile_time
만족 net.megastudy.qube:id/tv_profile_satisfaction


상메 net.megastudy.qube:id/tv_master_comment
찜 net.megastudy.qube:id/tv_master_choice
신속도 net.megastudy.qube:id/tv_master_speed
만족도 net.megastudy.qube:id/tv_master_satis
답변 수 net.megastudy.qube:id/tv_master_count
마지막 답변일 net.megastudy.qube:id/tv_last_answer
답변 가능 과목 net.megastudy.qube:id/tv_subject_title (여러 개)
전문 선생님 net.megastudy.qube:id/tv_teacher_title (여러 개)
"""