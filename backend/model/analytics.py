import matplotlib.pyplot as plt
import os

class Analytics:
    """
    The Analytics class handles the analysis of an audio recording.
    """
    def __init__(self, audio_file_path, recording_file_path, transcription_segments):
        """
        Initializes the Analytics class.
        """
        self.audio_file_path = audio_file_path
        self.recording_file_path = recording_file_path
        self.transcription_segments = transcription_segments

    def calculate_wpm(self, interval=5):
        """
        Calculate words per minute (WPM) from Whisper transcription segments.

        Args:
            interval (int): Time interval in seconds for WPM calculation.

        Returns:
            list: A list of tuples (time, wpm) for each interval.
        """
        if not self.transcription_segments:
            return []

        time_wpm = []
        current_time = 0
        current_words = []

        for segment in self.transcription_segments:
            start = segment["start"]
            end = segment["end"]
            words = segment["text"].split()

            # Add words to the current interval
            current_words.extend(words)
            # Check if we've passed the current interval
            while start >= current_time + interval:
                # Calculate WPM for the interval
                wpm = (len(current_words) / interval) * 60
                time_wpm.append((current_time, wpm))
                current_words = []  # Reset for the next interval
                current_time += interval

        # Process any remaining words at the end
        if current_words:
            wpm = (len(current_words) / interval) * 60
            time_wpm.append((current_time, wpm))

        return time_wpm

    def generate_plot_wpm(self):
        """
        Plot the WPM over time and store the generated graphic in the output/speed_graphics directory.

        Returns:
            str: Path to the stored speech speed graphic
        """
        # Get the audio filename to create filename for graphic plot
        audio_filename = self.audio_file_path.replace('output/raw_audio/', '')
        audio_filename = audio_filename[:-4]  # Removes the last 4 characters (".wav")
        graphics_filename = f"speed_graphics_for_{audio_filename}"
        os.makedirs("backend/static/output/speed_graphics", exist_ok=True)
        output_path = f"backend/static/output/speed_graphics/{graphics_filename}.png"

        time_wpm = self.calculate_wpm()
        times, wpms = zip(*time_wpm) if time_wpm else ([], [])

        plt.figure(figsize=(10, 6), facecolor='white')

        # Add red shadow regions on the y-axis (y=50 to 100 and y=200 to 250)
        plt.axhspan(200, 250, color='red', alpha=0.1)
        plt.axhspan(50, 100, color='red', alpha=0.1)

        # Add green shadow regions on the y-axis (y=50 to 100 and y=200 to 250)
        plt.axhspan(100, 200, color='green', alpha=0.1)

        # Prepare colors for WPM values based on bounds
        colors = ['red' if w < 100 or w > 200 else 'white' for w in wpms]

        # Plot each point individually with color based on the WPM range
        plt.scatter(times, wpms, c=colors, s=50, edgecolor='white')

        # Plot each segment with an appropriate color (lines connecting the points)
        for i in range(1, len(times)):
            # Connecting the points with lines and applying the color scheme
            plt.plot(times[i - 1:i + 1], wpms[i - 1:i + 1], color=colors[i], linewidth=3)


        # Set y-axis limits
        plt.ylim(50, 250)

        # Add labels, grid, and legend
        plt.xlabel("Time (seconds)", fontsize=16, fontweight='bold', color='#f1f1f1')
        plt.ylabel("WPM", fontsize=16, fontweight='bold', color='#f1f1f1')
        plt.grid(True, color='#f1f1f1')

        # Make the outer frame bolder and white
        ax = plt.gca()  # Get current axes
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(2)  # Make the frame bolder
            spine.set_color('#f1f1f1')  # Set frame color to white

        # Adjust the size and weight of tick labels (numbers on the axes)
        plt.tick_params(axis='both', which='major', labelsize=12, width=2,
                        colors='#f1f1f1')  # Tick marks and labels in white
        plt.xticks(fontsize=12, fontweight='bold', color='#f1f1f1')  # Specifically for x-axis numbers
        plt.yticks(fontsize=12, fontweight='bold', color='#f1f1f1')  # Specifically for y-axis numbers

        # Save and show the plot
        plt.savefig(output_path, format="png", dpi=300, transparent=True)
        plt.show()

        return output_path

    def get_general_info(self):
        """
        This method returns general information about the recorded audio file

        For the given audio file, this method returns information about language, length,
        topic, recording date and time, count of words, etc.


        Returns:
            tuple:
                - str: a machine generated title for the recording.
                - str: the language used in the recording.
                - ??: length of the recording in format min:sec
                - ??: Date and time when the audio was recorded.
                - int: count of words in the recording
        """
        pass