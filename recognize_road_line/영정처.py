import cv2
import numpy as np

def DetectRoadLine(src):
    # 흑백화
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # 모서리 검출
    can = cv2.Canny(gray, 50, 200, None, 3)
    ######### Canny Edge 결과  출력#########
    #cv2.imshow('Lines', can)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #######################################

    # 관심 구역 설정
    height = can.shape[0]
    rectangle = np.array([[(0, height), (120, 300), (520, 300), (640, height)]])
    mask = np.zeros_like(can)
    cv2.fillPoly(mask, rectangle, 255)
    masked_image = cv2.bitwise_and(can, mask)
    ccan = cv2.cvtColor(masked_image, cv2.COLOR_GRAY2BGR)
    ############### 검출되는 구역(차선) 출력###############
    # 직선 좌표 정의
    #line1 = np.array([(0, height), (120, 300)], dtype=np.int32)
    #line2 = np.array([(120, 300), (520, 300)], dtype=np.int32)
    #line3 = np.array([(520, 300), (640, height)], dtype=np.int32)
    # 직선을 이미지에 그리기 (파란색)
    #cv2.polylines(masked_image, [line1, line2, line3], isClosed=False, color=(255, 0, 0), thickness=2)
    # 이미지 표시
    #cv2.imshow('Lines', masked_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    ####################################################

    # 직선 검출
    line_arr = cv2.HoughLinesP(masked_image, 1, np.pi / 180, 20, minLineLength=10, maxLineGap=10)
    ######### 검출된 직선 출력 #########
    #for line in line_arr:
    #    x1, y1, x2, y2 = line[0]
    #    cv2.line(masked_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    #cv2.imshow('Lines', masked_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    ###################################

    # 중앙을 기준으로 오른쪽, 왼쪽 직선 분리
    line_R = np.empty((0, 5), int)
    line_L = np.empty((0, 5), int)
    if line_arr is not None:
        line_arr2 = np.empty((len(line_arr), 5), int)
        for i in range(0, len(line_arr)):
            temp = 0
            l = line_arr[i][0]
            line_arr2[i] = np.append(line_arr[i], np.array((np.arctan2(l[1] - l[3], l[0] - l[2]) * 180) / np.pi))
            if line_arr2[i][1] > line_arr2[i][3]:
                temp = line_arr2[i][0], line_arr2[i][1]
                line_arr2[i][0], line_arr2[i][1] = line_arr2[i][2], line_arr2[i][3]
                line_arr2[i][2], line_arr2[i][3] = temp
            if line_arr2[i][0] < 320 and (abs(line_arr2[i][4]) < 170 and abs(line_arr2[i][4]) > 95):
                line_L = np.append(line_L, line_arr2[i])
            elif line_arr2[i][0] > 320 and (abs(line_arr2[i][4]) < 170 and abs(line_arr2[i][4]) > 95):
                line_R = np.append(line_R, line_arr2[i])
    line_L = line_L.reshape(int(len(line_L) / 5), 5)
    line_R = line_R.reshape(int(len(line_R) / 5), 5)

    # 중앙과 가까운 오른쪽, 왼쪽 선을 최종 차선으로 인식
    try:
        line_L = line_L[line_L[:, 0].argsort()[-1]]
        degree_L = line_L[4]
        cv2.line(ccan, (line_L[0], line_L[1]), (line_L[2], line_L[3]), (255, 0, 0), 10, cv2.LINE_AA)
    except:
        degree_L = 0
    try:
        line_R = line_R[line_R[:, 0].argsort()[0]]
        degree_R = line_R[4]
        cv2.line(ccan, (line_R[0], line_R[1]), (line_R[2], line_R[3]), (255, 0, 0), 10, cv2.LINE_AA)
    except:
        degree_R = 0

    # 원본에 최종 차선 합성
    mimg = cv2.addWeighted(src, 1, ccan, 1, 0)
    return mimg, degree_L, degree_R


cap = cv2.VideoCapture('car.avi')   # 영상 로드
state = ''                          # 차의 움직임 상태 (현재 차선 기준)
while cap.isOpened():
    ret, frame = cap.read()         # T/F, frame/Nan

    if not ret:     # F -> 종료
        break

    cv2.imshow('ImageWindow', DetectRoadLine(frame)[0])
    l, r = DetectRoadLine(frame)[1], DetectRoadLine(frame)[2]
    ########################################
    if abs(l) <= 155 or abs(r) <= 155:
        if l == 0 or r == 0:
            state = 'Left' if (l < 0 or r < 0) else ('Right' if(l > 0 or r > 0) else '')
        elif abs(l - 15) > abs(r):
            state = 'Right'
        elif abs(r + 15) > abs(l):
            state = 'Left'
        #else:
            #state = 'Go'
    else:
        if l > 155 or r > 155:
            state = 'hard right'
        elif l < -155 or r < -155:
            state = 'hard left'
    print(state)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    ########################################

cap.release()            # 카메라 객체 해제(메모리 해제)
cv2.destroyAllWindows()  # 지금까지 열렸던 모든 창 종료
