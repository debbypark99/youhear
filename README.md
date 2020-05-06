# youhear
kinetic typographic subtitle for people with hearing loss

## Local 폴더와 연결하는 법
> 1. 이거 다운받을 폴더를 하나 만들어준다.
> 2. terminal로 들어가서 cd를 통해 그 폴더로 이동
> 3. 다음 코드를 친다.

    git clone https://github.com/debbypark99/youhear.git
    
## 파일(resource, py 등) 업로드 하는 법

    git add <파일 or 폴더 이름> (업로드 할 파일이 여러 개라면 계속 add 반복)
    git commit -m "<commit에 대충 설명하는 메세지>"
    git push origin <branch name> (일단은 master에 올리면 될 듯)
    
## Local 저장소를 여기 꺼로 update 시키는 법

    git pull origin <branch name> (일단 master)
    
