import cv2
import numpy as np

video_path = "data.mp4"

# 동영상을 로드한다.
cap = cv2.VideoCapture(video_path)

# 가로 375 , 세로 667 -> 잘라서 저장할 때 사용
#output_size = (375,667)

# 원본 사이즈로 저장할 때 사용
output_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

# 영상을 원하는 크기만큼 잘라서 저장하기위해 선언 (output_size를 설정하지 않으면 그냥 원래 사이즈대로 저장)
# mp4v라는 코덱으로 저장.
fourcc = cv2.VideoWriter_fourcc('m','p','4','v')

# 파일의 이름 설정, 코덱, fps, output size 설정!
out = cv2.VideoWriter('%s_output.mp4' % (video_path.split('.')[0]), fourcc, cap.get(cv2.CAP_PROP_FPS), output_size)


# 동영상이 로드되지 않았을 경우 바로 종료
if not cap.isOpened():
  exit()

#   - OPENCV_OBJECT_TRACKERS
#   자세한 설명은 아래 링크
#   https://bkshin.tistory.com/entry/OpenCV-32-%EA%B0%9D%EC%B2%B4-%EC%B6%94%EC%A0%81%EC%9D%84-%EC%9C%84%ED%95%9C-Tracking-API
#   csrt,kcf,boosting,mil,tld,medianflow,mosse 등

# tracker 선언
tracker = cv2.TrackerCSRT_create()

# 비디오 프레임 크기, 전체 프레임수, FPS 등 출력
print('Frame width:', int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
print('Frame height:', int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('Frame count:', int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))

# 프레임 계산 후, waitKey에 delay를 넣어준다.
fps = cap.get(cv2.CAP_PROP_FPS)
print('FPS:', fps)
delay = round(1000 / fps)

# ROI(Region of Interest) -> 관심 영역 지정 [중요) ROI가 영상 size를 넘어가는 경우, 예외처리를 해주어야한다. 아직 미완]
# 첫번째 프레임에서 ROI를 설정하겠다는 의미.
ret , img = cap.read()

# Window의 이름 정하기
cv2.namedWindow('Select Window')
cv2.imshow('Select Window',img)

# setting ROI
# fromCenter : 센터에서 시작할거냐?
# showCrosshair : 선택하기 위한 크로스헤어(과녁)을 보이게 할거냐?
# ROI의 정보를 rect에 저장
rect = cv2.selectROI("Select Window",img,fromCenter=False,showCrosshair=True)
# Select Window창 닫기
cv2.destroyWindow('Select Window')

# ROI 설정 이후 -> Tracker 초기화 하기
# img에서 rect를 tracking하라는 의미.
tracker.init(img,rect)

while True:
  # video를 읽어서 img에 저장
  ret,img = cap.read()

  # 제대로 프레임을 읽으면 ret값이 True, 실패하면 False가 나타납니다.
  if not ret:
    exit()

  # tracker를 계속 업데이트 해주기 ( resize 전에 해주어야함. )
  success , box = tracker.update(img)

  # box에 저장되는 좌표들을 변수에 저장
  left,top,w,h = [int(v) for v in box]

  # output size는 고정이지만, 사각형 사이즈는 사용자에 따라 변동되므로 이를 output size에 맞게 고정시켜준다.
  center_x = left + w / 2
  center_y = top + h / 2

  result_top = int(center_y - output_size[1] / 2)
  result_bottom = int(center_y + output_size[1] / 2)
  result_left = int(center_x - output_size[0] / 2)
  result_right = int(center_x + output_size[0] / 2)

  result_img = img[result_top:result_bottom , result_left:result_right]

  # img영상에 사각형 그리기 (pt1은 좌측상단, pt2는 우측하단) , thickness = 굵기
  cv2.rectangle(img,pt1=(left,top),pt2=(left+w,top+h),color = (0,0,0) , thickness=3)

  #   - 보간법 : 알려진 데이터 지점 내에서 새로운 데이터 지점을 구성하는 방식
  #   - cv2.INTER_NEAREST : 최근방 이웃 보간법
  #   - cv2.INTER_LINEAR(default) : 양선형 보간법(2x2 이웃 픽셀 참조)
  #   - cv2.INTER_CUBIC : 3차 회선 보간법(4x4 이웃 픽셀 참조)
  #   - cv2.INTER_LANCZOS4 : Lanczos 보간법(8x8 이웃 픽셀 참조)
  #   - cv2.INTER_AREA : 픽셀 영역 관계를 이용한 resampling 방법으로 이미지 축소시 효과적
  # 동영상 사이즈 설정 , 보간법 적용

  #img = cv2.resize(img, (450, 650), interpolation=cv2.INTER_CUBIC)

  #cv2.imshow('result_img',result_img)
  cv2.imshow('img',img)

  out.write(img)

  # 'q'누르면 영상 종료
  if cv2.waitKey(delay) == ord('q'):
    break

cap.release()
out.release()
cv2.destroyAllWindows()