# Ball Sorting Game

This is an interactive game that uses computer vision and hand tracking to create a fun and engaging ball sorting experience. Players use their hands to grab and sort colored balls into matching bins, all through their webcam!

## Features

- Real-time hand tracking using MediaPipe
- Dynamic ball spawning and interaction
- Color-matched bins for sorting
- Score tracking and time limit
- Visual feedback for ball grabbing and releasing

## Requirements

- Python 3.7+
- OpenCV (cv2)
- MediaPipe

## Installation

1. Clone this repository or download the source code.

2. Install the required packages:

   ```
   pip install opencv-python mediapipe
   ```

## How to Play

1. Run the script:

   ```
   python ball_sorting_game.py
   ```

2. Allow access to your webcam when prompted.

3. Use your hand to grab the colored balls and sort them into the matching colored bins at the bottom of the screen.

4. Score points by placing balls in the correct bins. Lose points for incorrect placements.

5. The game ends after 45 seconds or when the maximum number of balls (15) is reached.

## Game Controls

- Move your hand in front of the camera to control the game.
- Grab balls by moving your hand close to them.
- Release balls by moving your hand over the bins.
- Press 'q' or 'ESC' to quit the game at any time.

## Scoring

- +1 point for correctly sorted balls
- -1 point for incorrectly sorted balls

## Tips

- Watch for the "Holding Ball" and "Wait to Grab" indicators to time your moves.
- Try to sort as many balls as possible before the time runs out or the screen fills up!

## Troubleshooting

If you encounter any issues:

1. Ensure your webcam is properly connected and accessible.
2. Check that you have the correct versions of OpenCV and MediaPipe installed.
3. Make sure you have adequate lighting for hand detection.

## Contributing

Feel free to fork this project and submit pull requests with improvements or bug fixes!

## License

This project is open-source and available under the MIT License.
