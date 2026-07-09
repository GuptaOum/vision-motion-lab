import cv2
import mediapipe as mp
import time
import numpy as np
import torch

# Check if CUDA is available
if torch.cuda.is_available():
    print(f"GPU available: {torch.cuda.get_device_name(0)}")
    device = torch.device("cuda:0")
else:
    print("No GPU found, using CPU")
    device = torch.device("cpu")

# MediaPipe initialization with GPU
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    static_image_mode=False,
    model_complexity=2  # Using the heavy model for better accuracy when GPU is available
)

# OpenCV CUDA optimization
if hasattr(cv2, 'cuda') and cv2.cuda.getCudaEnabledDeviceCount() > 0:
    # Create CUDA Stream
    stream = cv2.cuda_Stream()
    
    # Create CUDA upload and download matrices
    def create_gpu_mat(frame):
        return cv2.cuda_GpuMat()

    def upload_to_gpu(frame, gpu_mat):
        gpu_mat.upload(frame, stream)
        return gpu_mat

    def download_from_gpu(gpu_mat):
        return gpu_mat.download()
else:
    print("OpenCV CUDA support not available")

# Initialize video capture
cap = cv2.VideoCapture(0)
pTime = 0
stage = None
stage1 = None

def to_pixel_coords(coords, img_shape):
    return int(coords[0] * img_shape[1]), int(coords[1] * img_shape[0])

@torch.cuda.amp.autocast()  # Enable automatic mixed precision for faster computation
def calculate_angle(a, b, c):
    # Convert to PyTorch tensors and move to GPU
    a = torch.tensor(a, device=device)
    b = torch.tensor(b, device=device)
    c = torch.tensor(c, device=device)
    
    ab = a - b
    bc = c - b
    
    # Dot product and magnitudes
    dot_product = torch.dot(ab, bc)
    magnitude_ab = torch.norm(ab)
    magnitude_bc = torch.norm(bc)
    
    # Cosine of the angle
    cos_theta = dot_product / (magnitude_ab * magnitude_bc + 1e-7)
    cos_theta = torch.clamp(cos_theta, -1.0, 1.0)
    
    # Angle in degrees
    angle = torch.degrees(torch.arccos(cos_theta))
    return angle.item()

counter = 0

while True:
    success, frame = cap.read()
    if not success:
        continue

    # GPU optimization for image processing
    if hasattr(cv2, 'cuda') and cv2.cuda.getCudaEnabledDeviceCount() > 0:
        # Create and upload GPU mat
        gpu_frame = create_gpu_mat(frame)
        gpu_frame = upload_to_gpu(frame, gpu_frame)
        
        # Flip and resize on GPU
        gpu_frame = cv2.cuda.flip(gpu_frame, 1)
        gpu_frame = cv2.cuda.resize(gpu_frame, (1000, 700))
        
        # Download result
        img = download_from_gpu(gpu_frame)
    else:
        img = cv2.flip(frame, 1)
        img = cv2.resize(frame, (1000, 700))

    # Convert to RGB (keeping on CPU as MediaPipe expects CPU tensor)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Process pose detection
    results = pose.process(imgRGB)

    try:
        if results.pose_landmarks:
            landmark = results.pose_landmarks.landmark

            # Get landmarks (rest of the landmark processing remains the same)
            shoulder = [landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                       landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                    landmark[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                    landmark[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            shoulder1 = [landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow1 = [landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmark[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist1 = [landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmark[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate angles using GPU-accelerated function
            angle = calculate_angle(shoulder, elbow, wrist)
            angle1 = calculate_angle(shoulder1, elbow1, wrist1)

            # Rest of the pose processing logic remains the same
            if angle > 160:
                stage = "down"
            if angle < 37 and stage == "down":
                stage = "up"
                counter += 1

            if angle1 > 160:
                stage1 = "down"
            if angle1 < 37 and stage1 == "down":
                stage1 = "up"
                counter += 1

            # Calculate bars
            if 'angle' in locals() and 'angle1' in locals():
                bar = np.interp(angle, (11, 175), (200, 650))
                bar1 = np.interp(angle1, (11, 175), (200, 650))
            else:
                bar = 200
                bar1 = 200

            # Draw visual elements
            cv2.putText(img, f'Left Angle: {int(angle)}', (11, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 201, 211), 1, cv2.LINE_AA)
            cv2.putText(img, f'Right Angle: {int(angle1)}', (700, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 201, 211), 1, cv2.LINE_AA)
            cv2.putText(img, 'REPS', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, str(counter), (120, 130), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(img, 'STAGE', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, stage, (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(img, 'STAGE1', (700, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img, stage1, (780, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 2, cv2.LINE_AA)

            # Draw rectangles
            cv2.rectangle(img, (100, 200), (200, 650), (0, 255, 0), 2)
            cv2.rectangle(img, (100, int(bar)), (200, 650), (0, 255, 0), cv2.FILLED)
            cv2.rectangle(img, (800, 200), (900, 650), (0, 255, 0), 2)
            cv2.rectangle(img, (800, int(bar1)), (900, 650), (0, 255, 0), cv2.FILLED)

            # Draw landmarks and connections
            for point in [shoulder, elbow, wrist, shoulder1, elbow1, wrist1]:
                cv2.circle(img, to_pixel_coords(point, img.shape), 5, (0, 255, 0), -1)
            cv2.line(img, to_pixel_coords(elbow, img.shape), to_pixel_coords(shoulder, img.shape), (200, 0, 0), 2)
            cv2.line(img, to_pixel_coords(elbow, img.shape), to_pixel_coords(wrist, img.shape), (200, 0, 0), 2)
            cv2.line(img, to_pixel_coords(elbow1, img.shape), to_pixel_coords(shoulder1, img.shape), (200, 0, 0), 2)
            cv2.line(img, to_pixel_coords(elbow1, img.shape), to_pixel_coords(wrist1, img.shape), (200, 0, 0), 2)

    except Exception as e:
        print(f"Error: {e}")
        pass

    # Calculate and display FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    local_time = time.ctime(cTime)
    
    cv2.putText(img, str(local_time), (560, 680), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(img, str(int(fps)), (700, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.imshow("img", img)

    key = cv2.waitKey(1)
    if key == ord('r'):
        counter = 0
    if key & 0xFF == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()

# Clean up CUDA resources
if hasattr(cv2, 'cuda') and cv2.cuda.getCudaEnabledDeviceCount() > 0:
    cv2.cuda.resetDevice()
torch.cuda.empty_cache()