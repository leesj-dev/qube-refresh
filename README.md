# qube-refresh
## Step 1. Android Studio & Appium 설치
1. 최신 버전의 [Android Studio](https://developer.android.com/studio)를 설치합니다.

2. 프로그램을 실행한 후, `More Actions`을 눌러 `SDK Manager`로 가서 Android 13.0 (Tiramisu)을 다운로드합니다. 화면 상단에 보면 `Android SDK Location`이 있는데, 나중에 이 경로를 쓸 것이니 미리 복사해두기 바랍니다. 일반적으로 아래와 같습니다.
* Windows: `C:\Users\[사용자 이름]\AppData\Local\Android\SDK`
* Mac: `/Users/[사용자 이름]/Library/Android/sdk`
![android-automation-1.png](https://leesj.me/static/e37b2060e5aef35541135b05b5f0802a/36aa2/android-automation-1.png)

3. 다시 처음화면으로 돌아가 `More Actions`의 `Virtual Device Manager`로 갑니다. `Create Device`를 누르고 Pixel 4, Android 13.0 (Tiramisu)를 선택합니다.

4. 플레이 버튼을 누르면 가상 안드로이드 디바이스가 실행됩니다.
![android-automation-2.png](https://leesj.me/static/64dbe5033f6a33c361cca6fec1850024/25af7/android-automation-2.png)

5. 기존에 Java 8가 설치되어 있는 사람은 이 단계를 건너뛰면 됩니다. [JDK 8 Oracle 페이지](https://www.oracle.com/kr/java/technologies/javase/javase8u211-later-archive-downloads.html)에 들어가서 JDK(Java Development Kit)를 설치합니다.
편의상 Oracle 서버의 direct download 링크를 걸어두겠습니다. 이 글을 작성하는 시점 기준으로 8u331 버전입니다.

[JDK 8 Windows](https://javadl.oracle.com/webapps/download/GetFile/1.8.0_331-b09/165374ff4ea84ef0bbd821706e29b123/windows-i586/jdk-8u331-windows-x64.exe)

[JDK 8 Mac](https://javadl.oracle.com/webapps/download/GetFile/1.8.0_331-b09/165374ff4ea84ef0bbd821706e29b123/unix-i586/jdk-8u331-macosx-x64.dmg)

6. [Appium Server GUI](https://github.com/appium/appium-desktop/releases/tag/v1.22.3-4)를 설치한 뒤 실행합니다. Host는 `127.0.0.1`로, Port는 `4723`로 설정합니다.

7. `Edit Configurations`를 누르면 환경 변수를 설정하는 창이 뜹니다.
![android-automation-3.png](https://leesj.me/static/ce4be1d302f445a280c67332cdcda2c8/d853e/android-automation-3.png)
`ANDROID_HOME`에는 앞에서 복사했던 `Android SDK Location`를 넣어주고, `JAVA_HOME`에는 설치한 JDK의 경로를 넣어줍니다. 일반적으로 아래와 같습니다.
* Windows: `C:\Program Files\Java\jdk-[버전명]`
* Mac: `/Library/Java/JavaVirtualMachines/jdk[버전명].jdk`

Mac의 경우, Finder > Go > Go To Folder로 가서 `/Library/Java/JavaVirtualMachines/`을 입력하면 jdk 폴더가 나옵니다.

8. startServer를 눌러 서버를 실행시킵니다.

9. Play Store에서 구글 계정에 로그인하고 Qube 앱을 다운로드합니다.

<br>

## Step 2. Discord 봇 설정
1. clone하고자 하는 디렉토리로 이동한 후, 이 git을 clone해줍니다.
```
git clone https://github.com/leesj-dev/qube-refresh.git
```

2. Discord에 로그인한 후 [메인 화면](https://discord.com/channels/@me)에서 서버를 하나 만듭니다.

3. [Discord Developer Portal](https://discord.com/developers/applications)에 들어가서 로그인하고 `New Application`을 누르고, 새로운 애플리케이션을 만들어줍니다.

> 3, 4, 6단계의 자세한 내용은 이 [블로그](https://scvtwo.tistory.com/196)를 참고하세요.

4. 좌측에 `Bot`을 클릭하여 봇을 생성하고, `Reset Token` 버튼을 눌러 토큰을 생성합니다. 이후 `Copy` 버튼을 눌러줍니다.

5. 디렉토리에 `.env` 파일을 생성한 후 다음 줄을 추가해줍니다.
```
DISCORD_TOKEN = (아까 복사한 토큰)
```

6. 좌측에 `OAuth2`의 `URL Generator`를 클릭한 후 Scopes의 `bot`을 체크하고, URL을 복사합니다. URL을 복사하여 주소창에 넣으면 디스코드 어느 서버에 초대할지 선택하라고 뜹니다. 처음에 만들어뒀던 서버를 선택합니다.

7. 다시 [메인 화면](https://discord.com/channels/@me)으로 돌아가서 `사용자 설정`을 눌러줍니다. `고급`으로 들어가서 `개발자 모드`를 활성화시켜줍니다.

8. 메인화면에서 자신의 디스코드 서버를 선택한 후 채팅 채널을 하나 만듧니다. 이후 그 채널을 우클릭하고 `ID 복사하기` 버튼을 눌러주고 `.env` 파일에 다음 줄을 추가해줍니다.
```
CHANNEL_ID = (아까 복사한 채널 ID)
```

9. 해당 채널에 아무 메세지나 보냅니다. 방금 보낸 자신의 프로필 이미지를 우클릭하고 `ID 복사하기` 버튼을 눌러주고 `.env` 파일에 다음 줄을 추가해줍니다.
```
USER_ID = (아까 복사한 유저 ID)
```

10. 4단계의 `Bot` 섹션으로 다시 돌아가서, 밑으로 스크롤하여 `Privileged Gateway Intents` 부분에 해당하는 3가지를 모두 활성화해줍니다.
* Presence Intent
* Server Members Intent
* Message Content Intent

<br>

## Step 3. 코드 실행
1. 본 repo를 Clone한 후, 패키지를 설치합니다.

   `pip install -r /path/to/requirements.txt`

2. Android 에뮬레이터의 Qube 앱과 Appium Server를 실행합니다.

3. 마스터 계정으로 로그인한 상태에서 `main.py`를 실행합니다. 이 코드는 문제 선점를 도와주는 기능을 합니다.

4. 학생 계정으로 로그인한 상태에서 `마스터 보기`를 누르고 `master_crawl.py`를 실행합니다. 이 코드는 마스터 목록을 크롤링하여 `masters.txt`로 반환하는 기능을 합니다.

<br>

## Step 4. 결과
코드가 정상적으로 실행된다면, 다음과 같은 파일 트리 구조가 형성될 것입니다:
```
├── images_latex
│   ├── 2023-01-29 21:29:49-1.png
│   ├── 2023-01-29 22:22:04-1.png
│   ├── 2023-01-29 22:22:04-2.png
│   └── 2023-01-29 22:52:13-1.png
├── images_stu
│   ├── 2023-01-29 20:24:39-1.png
│   └── 2023-01-29 20:24:39-2.png
├── images_tea
│   ├── 2023-01-29 22:39:59-1.png
│   └── 2023-01-29 23:23:14-1.png
├── .env
├── .gitignore
├── requirements.txt
├── Pretendard-Regular.otf
├── run.log
├── README.md
├── main.py
├── master_crawl.py
└── masters.txt
```
