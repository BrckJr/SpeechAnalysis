import os
from flask import Blueprint, jsonify, send_from_directory, request, render_template
from flask_login import login_required, current_user
from src.model.transcriber import Model
from src.database import db
from src.database.models import AudioTranscription
from src.control import actions

# Create a Blueprint for transcription routes
transcription_bp = Blueprint('transcription', __name__)

# Create an instance of the model which executes the actual logic
transcriber = Model()

# Path to the stored raw audio files and transcriptions
AUDIO_FOLDER = "src/static/output/raw_audio"
TRANSCRIPTION_FOLDER = "src/static/output/transcription"

@transcription_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Displays the user's dashboard with all their uploaded audio files.

    Retrieves the list of audio transcription records from the database
    for the authenticated user and renders them in the 'dashboard' template.
    """
    return render_template('dashboard.html', page_name='dashboard')

@transcription_bp.route('/start', methods=['POST'])
def start_recording():
    """
    Starts audio recording.

    Calls the 'start_recording_audio' method of the transcriber model to begin recording.
    """
    transcriber.start_recording_audio()
    return jsonify({"message": "Recording started"})

@transcription_bp.route('/pause', methods=['POST'])
def pause_recording():
    """
    Pauses the current audio recording.

    Calls the 'pause_recording_audio' method of the transcriber model to pause recording.
    """
    transcriber.pause_recording_audio()
    return jsonify({"message": "Recording paused"})

@transcription_bp.route('/stop', methods=['POST'])
def stop_recording():
    """
    Stops the audio recording and handles various actions based on the request.

    The function stops the recording, and depending on the user's choice, transcribes it only
    or transcribes it and analyzes it.

    """
    data = request.get_json()
    action = data.get('action')
    filename = data.get('filename')

    # Base filename and extension
    base_name, extension = filename.rsplit('.', 1) if '.' in filename else (filename, '')

    # Check for duplicates and create a unique filename
    unique_filename = filename
    filter_in_database = f"src/static/output/raw_audio/{filename}.wav"

    counter = 1
    while db.session.query(AudioTranscription).filter_by(audio_path=filter_in_database).first():
        unique_filename = f"{base_name} ({counter}){'.' + extension if extension else ''}"
        counter += 1
        filter_in_database = f"src/static/output/raw_audio/{unique_filename}.wav"

    match action:
        case 'delete_audio':
            transcriber.stop_recording_audio(False)
            return '', 204  # 204 No Content
        case 'save_audio_and_analyze':
            response, status_code, audio_filename = actions.transcribe_and_analyse(transcriber, current_user, db, unique_filename)
            return jsonify({"response": response, "dropdown_value": audio_filename}), status_code
        case _:
            return jsonify({"success": False, "message": "Action for stopping recording unknown."}), 500

@transcription_bp.route('/delete-all-files', methods=['POST'])
def delete_files():
    """
    Deletes all audio and transcription files for the authenticated user.

    This removes both the files from the file system and the corresponding database records.
    """
    try:
        # Query all records from the database of the current user
        all_files = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Delete files from the local filesystem
        actions.delete_files(all_files)

        # Clear database records for the current user only
        db.session.query(AudioTranscription).filter_by(user_id=current_user.id).delete()
        db.session.commit()

        return jsonify({"success": True, "message": "All files deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to delete all files"}), 500

@transcription_bp.route('/delete-file', methods=['POST'])
def delete_file():
    """
    Deletes all audio and transcription files for the authenticated user.

    This removes both the files from the file system and the corresponding database records.
    """
    try:
        data = request.json
        audio_filepath = data.get('filePath')
        if not audio_filepath:
            return jsonify({'success': False, 'error': 'File path is required'}), 400

        print(f"Inserted Filepath: {audio_filepath}")

        if os.path.exists(audio_filepath):
            # Query all records from the database connected to the selected audio recording
            all_files = AudioTranscription.query.filter_by(audio_path=audio_filepath).all()
            # Delete files from the local filesystem
            actions.delete_files(all_files)
            # Clear database records for the current file
            db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).delete()
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to delete file"}), 500

@transcription_bp.route('/list-files', methods=['GET'])
def list_files():
    """
    Lists all audio and transcription file paths for the authenticated user.

    Queries the database for the user's audio recordings and transcriptions, returning their full file paths in JSON format.
    """
    try:
        # Query the database for all audio recordings of the current user
        audio_recordings = AudioTranscription.query.filter_by(user_id=current_user.id).all()

        # Create a list of audio file paths
        audio_files = [recording.audio_path for recording in audio_recordings]

        # Create a list of transcription file paths
        transcription_files = [recording.transcription_path for recording in audio_recordings]#

        # Create a list of improved text file paths
        improved_text_files = [recording.improved_text_path for recording in audio_recordings]

        # Create a list of times when files where stored
        date_times = [recording.created_at for recording in audio_recordings]

        return jsonify({
            'audio_files': audio_files,
            'transcription_files': transcription_files,
            'improved_text_files': improved_text_files,
            'date_times': date_times
        })

    except Exception as e:
        return jsonify({'error': str(e), "message": "Error during loading of file lists."}), 500

@transcription_bp.route('/static/<path:filename>')
def serve_file(filename):
    """
    Serves static files from the 'static' folder.

    This route is used to retrieve and serve raw audio or transcription files from the server.
    """
    return send_from_directory('static', filename)

@transcription_bp.route('/get-analytics', methods=['POST'])
def get_analytics():
    try:
        data = request.get_json()
        audio_filepath = data.get('recording')

        if not audio_filepath:
            return jsonify({'error': 'Recording not specified'}), 400

        # Retrieve the relevant row in the database
        target_database_entry = db.session.query(AudioTranscription).filter_by(audio_path=audio_filepath).first()

        if target_database_entry:
            speech_speed_graphic_path = target_database_entry.speech_speed_graphic_path
            pitch_graphic_path = target_database_entry.pitch_graphic_path
            energy_graphic_path = target_database_entry.energy_graphic_path
            improved_text_path = target_database_entry.improved_text_path
            title = target_database_entry.title
            language = target_database_entry.language
            audio_length = target_database_entry.audio_length
            word_count = target_database_entry.word_count
            summary = target_database_entry.summary
            return jsonify({'success': True,
                            'speech_speed_graphic_path': speech_speed_graphic_path,
                            'pitch_graphic_path': pitch_graphic_path,
                            'energy_graphic_path': energy_graphic_path,
                            'improved_text_path': improved_text_path,
                            'recording_title': title,
                            'recording_language': language,
                            'audio_length': audio_length,
                            'word_count': word_count,
                            'text_summary': summary
                            }), 200
        else:
            return jsonify({'error': 'Requested audio file was not found in database'}), 404


    except Exception as e:
        return jsonify({'error': str(e), "message": "Error within execution of get analytics."}), 500

