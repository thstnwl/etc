import cv2
import numpy as np


def DetectRoadLine(src):
    # BGR -> GrayScale
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # edge 검출
    canny = cv2.Canny(gray, 50, 200, None, 3)

    # 검출 구역 설정 (향후에 앞에 차가 있는 부분까지만 검출하도록?)
    rectangle = np.array([[(50, canny.shape[0]), (250, 220), (390, 220), (610, canny.shape[0])]]) # 정 가운데로 주행하지 않을 시 차선이 범위 밖에 있을 경우 고려
    #rectangle = np.array([[(50, canny.shape[0]), (260, 220), (380, 220), (590, canny.shape[0])]]) # 정 가운데로 주행 시 차선 범위

    # 크기가 canny와 동일한 검은색 배경 mask 생성
    mask = np.zeros_like(canny)

    # mask의 rectangle 영역을 흰색으로 채움 -> 해당 영역의 직선만 검출할거임
    cv2.fillPoly(mask, rectangle, 255)

    # canny와 mask and연산 (rectangle 영역 안의 검출된 모서리만 나타남)
    masked_image = cv2.bitwise_and(canny, mask)
    # 직선 검출
    line_arr = cv2.HoughLinesP(masked_image, 1, np.pi / 180, 20, minLineLength=10, maxLineGap=10)

    # 중앙을 기준으로 오른쪽, 왼쪽 직선 분리 [x1, y1, x2, y2, 각도]
    line_R = np.empty((0, 5), int)
    line_L = np.empty((0, 5), int)

    # 값이 존재할때만 실행
    if line_arr is not None:
        line_arr2 = np.empty((len(line_arr), 5), int)

        #  허프 변환으로 검출된 모든  선에 대해 반복
        for i in range(0, len(line_arr)):
            temp = 0
            # line_arr[i][0]선의 좌표 정보 추출 [x1, y1, x2, y2]
            l = line_arr[i][0]

            # line_arr에 정보 추가[x1, y1, x2, y2, 각도] - 각도는 절대값으로 넣음
            line_arr2[i] = np.append(line_arr[i], abs(np.array((np.arctan2(l[1] - l[3], l[0] - l[2]) * 180) / np.pi)))

            # 시작점 끝점 위치가 반대인 경우
            if line_arr2[i][1] > line_arr2[i][3]:
                temp = line_arr2[i][0], line_arr2[i][1]
                line_arr2[i][0], line_arr2[i][1] = line_arr2[i][2], line_arr2[i][3]
                line_arr2[i][2], line_arr2[i][3] = temp

            # 좌측 차선 : 선의 시작점이 영상의 중앙(320)보다 왼쪽에 있고, 각도가 95 이상
            if line_arr2[i][0] < 320 and (abs(line_arr2[i][4]) < 170 and abs(line_arr2[i][4]) > 95):
                line_L = np.append(line_L, line_arr2[i])
            # 우측 차선 : 선의 시작점이 영상의 중앙(320)보다 오른쪽에 있고, 각도가 95 이하
            elif line_arr2[i][0] > 320 and (abs(line_arr2[i][4]) < 170 and abs(line_arr2[i][4]) > 95):
                line_R = np.append(line_R, line_arr2[i])
    # 2차원 배열 형태로 변환
    line_L = line_L.reshape(int(len(line_L) / 5), 5)
    line_R = line_R.reshape(int(len(line_R) / 5), 5)

    # GrayScale -> BGR
    masked_image = cv2.cvtColor(masked_image, cv2.COLOR_GRAY2BGR)
    degree_L, degree_R = 0, 0
    type_L, type_R = 0, 0  # 0 - 실선, 1 - 점선

    # 중앙과 가까운 왼쪽 선을 최종 차선으로
    try:
        line_L = line_L[line_L[:, 0].argsort()[-1]]
        degree_L = line_L[4]

        # 점선과 실선을 구분하기 위해 길이에 따라 선 종류 결정
        if abs(line_L[2] - line_L[0]) > 100:
            cv2.line(masked_image, (line_L[0], line_L[1]), (line_L[2], line_L[3]), (255, 0, 0), 12, cv2.LINE_AA)
            type_L = 0
        else:
            cv2.line(masked_image, (line_L[0], line_L[1]), (line_L[2], line_L[3]), (255, 0, 0), 8, cv2.LINE_AA)
            type_L = 1

    except:
        degree_L = 0
        type_L = 1

    # 중앙과 가까운 오른쪽 선을 최종 차선으로
    try:
        line_R = line_R[line_R[:, 0].argsort()[0]]
        degree_R = line_R[4]

        # 점선과 실선을 구분하기 위해 길이에 따라 선 종류 결정
        if abs(line_R[2] - line_R[0]) > 100:
            cv2.line(masked_image, (line_R[0], line_R[1]), (line_R[2], line_R[3]), (255, 0, 0), 12, cv2.LINE_AA)
            type_R = 0
        else:
            cv2.line(masked_image, (line_R[0], line_R[1]), (line_R[2], line_R[3]), (255, 0, 0), 8, cv2.LINE_AA)
            type_R = 1

    except:
        degree_R = 0
        type_R = 1

    # 원본에 최종 차선 합성
    cv2.fillPoly(src, [rectangle], color=(0, 255, 0, 30))
    result = cv2.addWeighted(src, 1, masked_image, 1, 0)
    return result, degree_L, degree_R, type_L, type_R


cap = cv2.VideoCapture('car.avi')  # 영상 로드
state = ''  # 차의 움직임 상태 (현재 차선 기준)
while cap.isOpened():
    ret, frame = cap.read()  # T/F, frame/Nan

    if not ret:  # F -> 종료
        break
    frame = cv2.resize(frame, (640, 360))
    cv2.imshow('ImageWindow', DetectRoadLine(frame)[0])
    dgree_L, dgree_R = DetectRoadLine(frame)[1], DetectRoadLine(frame)[2]
    change_L, change_R = DetectRoadLine(frame)[3], DetectRoadLine(frame)[4]
    #print(dgree_L, dgree_R, change_L, change_R)
    ########################################
    # 0이 실선, 1이 점선이므로 실선인데 해당 방향으로 차선 변경하면 알림주기
    if abs(dgree_L) > 155 or abs(dgree_R) > 155:
        if change_L == 0:
            print("left")
        elif change_R == 0:
            print("right")

    # print(state)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    ########################################

cap.release()  # 카메라 객체 해제(메모리 해제)
cv2.destroyAllWindows()  # 지금까지 열렸던 모든 창 종료
