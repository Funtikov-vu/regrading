import cv2
import os
import numpy as np

#   создаю папку, сохраняю кадры из видео после какого-то движения в момент,
#   когда они становятся довольно устойчивыми при условии фиксации коробки
#   идеи с расстоянием брал из письма и https://software.intel.com/en-us/node/754940


def distMap(frame1, frame2):
    """outputs pythagorean distance between two frames"""
    frame1_32 = np.float32(frame1)
    frame2_32 = np.float32(frame2)
    diff32 = frame1_32 - frame2_32
    norm32 = np.sqrt(diff32[:, :, 0] ** 2 + diff32[:, :, 1] ** 2 + diff32[:, :, 2] ** 2) / np.sqrt(
        255 ** 2 + 255 ** 2 + 255 ** 2)
    dist = np.uint8(norm32 * 255)
    return dist


def ft_stdev(frame1, frame2):
    dist = distMap(frame1, frame2)
    mod = cv2.GaussianBlur(dist, (9, 9), 0)
    _, stDev = cv2.meanStdDev(mod)
    return stDev


#   проверка фиксации коробки
def is_mounted(frame):
    stDev = ft_stdev(check, frame[1030:])
    if stDev <= 6:
        return 1
    return 0


try:
    os.mkdir("trg")
except OSError:
    pass

cap = cv2.VideoCapture('blending0.avi')
check = cv2.imread('tools/check_mount.jpg')
# счетчик кадров
count = 0
# порог девиации для начала движения
move_thresh = 10
# порог для отсутствия движения
static_thresh = 2

#   пропуск первых кадров
for i in range(18200):
    count += 1
    cap.read()
print("skipped")

_, frame1 = cap.read()
_, frame2 = cap.read()

is_moving = 0

while cap.isOpened():
    ret, frame3 = cap.read()

    rows, cols, _ = np.shape(frame3)
    if ret:
        stDev = ft_stdev(frame1, frame3)
        frame1 = frame2
        frame2 = frame3

        if stDev > move_thresh and is_moving == 0:
            # начало движения
            is_moving = 1
            '''
            что на последнем кадре перед движением, что на предпоследнем картинка немного смазана
            # предпоследняя неподвижная картинка
            cv2.imwrite("trg_start_prev/target_start_cpy_%d.jpg" % count, frame0)
            # последняя неподвижная картинка
            cv2.imwrite("trg_start/target_start_%d.jpg" % count, frame1)
            # первая картинка движения
            cv2.imwrite("moving/start_moving_%d.jpg" % count, frame3)
            '''
        elif stDev <= static_thresh and is_moving == 1 and is_mounted(frame3):
            # конец движения, устойчивое неподвижное состояние
            is_moving = 0
            cv2.imwrite("trg/target_%d.jpg" % count, frame3)

    else:
        break
    count += 1
    if count % 1000 == 0:
        print(count)
    # выход после обработки всех интересных кадров
    if count > 45600:
        break

cap.release()

