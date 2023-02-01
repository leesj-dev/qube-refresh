# qube-refresh
## Step 1. Android Studio & Appium 설치
[안드로이드 앱 자동화](https://leesj.me/android-automation/) 글에 적힌 절차대로 수행합니다. 단, 코드 수정 용도가 아니라면 Appium Inspector는 다운받으실 필요가 없습니다. 이후 Play Store에서 구글 계정에 로그인하고 Qube 앱을 다운로드합니다.

## Step 2. Discord 봇 설정
1. clone하고자 하는 디렉토리로 이동한 후, 이 git을 clone해줍니다.
```
git clone https://github.com/leesj-dev/qube-refresh.git
```

2. Discord에 로그인한 후 [메인 화면](https://discord.com/channels/@me)에서 서버를 하나 만듭니다.

3. [Discord Developer Portal](https://discord.com/developers/applications)에 들어가서 로그인하고 `New Application`을 누르고, 새로운 애플리케이션을 만들어줍니다.

4. 좌측에 Bot을 클릭하여 봇을 생성하고, `Reset Token` 버튼을 눌러 토큰을 생성합니다. 이후 `Copy` 버튼을 눌러줍니다.

5. 디렉토리에 `.env` 파일을 생성한 후 다음 줄을 추가해줍니다.
```
DISCORD_TOKEN = (아까 복사한 토큰)
```

1. 좌측에 OAuth2의 URL Generator를 클릭한 후 Scopes의 `bot`을 체크하고, URL을 복사합니다. URL을 복사하여 주소창에 넣으면 디스코드 어느 서버에 초대할지 선택하라고 뜹니다. 처음에 만들어뒀던 서버를 선택합니다.

3 ~ 6단계까지의 자세한 내용은 이 [블로그](https://scvtwo.tistory.com/196)를 참고하세요.

7. 다시 [메인 화면](https://discord.com/channels/@me)으로 돌아가서 `사용자 설정`을 눌러줍니다. `고급`으로 들어가서 `개발자 모드`를 활성화시켜줍니다.

8. 메인화면에서 자신의 디스코드 서버를 선택한 후 채팅 채널을 하나 만듧니다. 이후 그 채널을 우클릭하고 `ID 복사하기` 버튼을 눌러주고 `.env` 파일에 다음 줄을 추가해줍니다.
```
CHANNEL_ID = (아까 복사한 채널 ID)
```
9. 해당 채널에 아무 메세지나 보냅니다. 방금 보낸 자신의 프로필 이미지를 우클릭하고 `ID 복사하기` 버튼을 눌러주고 `.env` 파일에 다음 줄을 추가해줍니다.
```
USER_ID = (아까 복사한 유저 ID)
```

### Step 3. 코드 실행
Qube 앱을 실행하고, Appium Server를 동작시킨 채로 `main.py`를 실행합니다. 이때 가급적이면 Appium Inspector는 코드 실행 중 동시에 실행하지 않는 것이 좋습니다.

코드가 정상적으로 실행된다면, 다음과 같은 파일 트리 구조가 형성될 것입니다:
```
├── images
│   ├── 2023-01-29 21:29:49-1.png
│   ├── 2023-01-29 22:22:04-1.png
│   ├── 2023-01-29 22:22:04-2.png
│   ├── 2023-01-29 22:52:13-1.png
├── .env
├── .gitignore
├── run.log
├── README.md
└── main.py

```