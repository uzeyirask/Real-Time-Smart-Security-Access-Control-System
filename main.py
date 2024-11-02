import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width
cap.set(4, 720)   # Set height

while True:
    success, img = cap.read()  # Read a frame from the camera
    if not success:
        break  # Exit if the frame is not captured correctly

    cv2.imshow("DISPLAY", img)  # Display the captured frame
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
