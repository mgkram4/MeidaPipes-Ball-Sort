import random
import time

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

NUM_BALLS = 5
MAX_BALLS = 15
BALL_SPAWN_INTERVAL = 3
BIN_WIDTH = 100
BIN_HEIGHT = 150
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
GRAB_THRESHOLD = 50
RELEASE_DELAY = 1.0
BIN_OFFSET = 100

class Ball:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.size = 30
        self.x = random.randint(self.size, frame_width - self.size)
        self.y = random.randint(self.size, frame_height - BIN_HEIGHT - BIN_OFFSET - self.size)
        self.color = random.choice(COLORS)
        self.is_grabbed = False
        self.grab_offset = (0, 0)

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.size, self.color, -1)
        if self.is_grabbed:
            cv2.circle(frame, (int(self.x), int(self.y)), self.size + 5, (255, 255, 255), 2)

    def is_grabbed_by(self, hand_x, hand_y):
        distance = ((hand_x - self.x)**2 + (hand_y - self.y)**2)**0.5
        return distance < GRAB_THRESHOLD

    def update_position(self, hand_x, hand_y):
        self.x = hand_x + self.grab_offset[0]
        self.y = hand_y + self.grab_offset[1]
        self.x = max(self.size, min(self.x, self.frame_width - self.size))
        self.y = max(self.size, min(self.y, self.frame_height - self.size))

class Bin:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = BIN_WIDTH
        self.height = BIN_HEIGHT
        self.color = color

    def draw(self, frame):
        cv2.rectangle(frame, (self.x, self.y), (self.x + self.width, self.y + self.height), self.color, 2)

    def contains(self, ball):
        # Check if the ball is inside the bin
        return (self.x < ball.x < self.x + self.width and
                self.y < ball.y < self.y + self.height)

def get_hand_center(hand_landmarks, frame_width, frame_height):
    # Get the center of the hand (using index finger tip)
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    return int(index_tip.x * frame_width), int(index_tip.y * frame_height)

def game_loop(cap, hands):
    # Get frame dimensions
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Initialize balls and bins
    balls = [Ball(frame_width, frame_height) for _ in range(NUM_BALLS)]
    bins = [
        Bin(0, frame_height - BIN_HEIGHT - BIN_OFFSET, COLORS[0]),
        Bin(frame_width // 2 - BIN_WIDTH // 2, frame_height - BIN_HEIGHT - BIN_OFFSET, COLORS[1]),
        Bin(frame_width - BIN_WIDTH, frame_height - BIN_HEIGHT - BIN_OFFSET, COLORS[2])
    ]
    
    # Initialize game variables
    score = 0
    game_time = 45
    start_time = cv2.getTickCount()
    last_spawn_time = time.time()
    last_release_time = 0
    holding_ball = False

    while cap.isOpened():
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process the image and find hand landmarks
        results = hands.process(rgb_frame)

        current_time = time.time()

        # Spawn new balls at regular intervals
        if current_time - last_spawn_time > BALL_SPAWN_INTERVAL and len(balls) < MAX_BALLS:
            balls.append(Ball(frame_width, frame_height))
            last_spawn_time = current_time

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2)
                )

                # Get hand center
                hand_x, hand_y = get_hand_center(hand_landmarks, frame_width, frame_height)
                cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 255), -1)  # Draw hand center

                if holding_ball:
                    cv2.circle(frame, (hand_x, hand_y), 20, (255, 0, 255), 2)  # Purple circle when holding

                # Check ball interactions
                for ball in balls[:]:  # Use a copy of the list to safely remove items
                    if ball.is_grabbed:
                        ball.update_position(hand_x, hand_y)
                        # Check if ball is dropped in a bin
                        for bin in bins:
                            if bin.contains(ball):
                                if ball.color == bin.color:
                                    score += 1
                                    cv2.putText(frame, "+1", (int(ball.x), int(ball.y) - 20), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                                else:
                                    score -= 1
                                    cv2.putText(frame, "-1", (int(ball.x), int(ball.y) - 20), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                balls.remove(ball)
                                ball.is_grabbed = False
                                holding_ball = False
                                last_release_time = current_time
                                break
                    elif not holding_ball and current_time - last_release_time > RELEASE_DELAY:
                        if ball.is_grabbed_by(hand_x, hand_y):
                            ball.is_grabbed = True
                            holding_ball = True
                            ball.grab_offset = (ball.x - hand_x, ball.y - hand_y)

        # Draw bins and balls
        for bin in bins:
            bin.draw(frame)
        for ball in balls:
            ball.draw(frame)

        # Calculate remaining time
        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        remaining_time = max(0, game_time - int(elapsed_time))

        # Display game information
        cv2.putText(frame, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {remaining_time}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Balls: {len(balls)}/{MAX_BALLS}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        if holding_ball:
            cv2.putText(frame, "Holding Ball", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
        elif current_time - last_release_time <= RELEASE_DELAY:
            cv2.putText(frame, "Wait to Grab", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)

        # Display the frame
        cv2.imshow('Ball Sorting Game', frame)

        # Check for quit command
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27 or remaining_time == 0 or len(balls) >= MAX_BALLS:
            break

    return score

def main():
    try:
        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        # Initialize MediaPipe Hands
        with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            final_score = game_loop(cap, hands)

        # Release the webcam and close all windows
        cap.release()
        cv2.destroyAllWindows()

        print(f"Final Score: {final_score}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()