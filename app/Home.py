import streamlit as st
import pywhisper
from pathlib import Path
from tempfile import NamedTemporaryFile
from datetime import timedelta

# Set configuration
st.set_page_config(
    page_title="Daryl's Transcription Web App",
    page_icon='💬',
    layout='centered',
    initial_sidebar_state='collapsed',
    menu_items={
        'About': '''This is developed by Daryl Ku (Research Associate), Academic Quality Unit,
        Office of Strategic Planning and Academic Quality (SPAQ), NIE''',
        'Report a Bug': None,
        'Get help': None
        }
    )

# Display title
st.title(
    '''Transcribe or Translate Speech'''
    )

# Display instructions
st.markdown(
    '''
    This web application uses Open AI's _Whisper_ to automatically transcribe or translate
    speech. _Whisper_ is a neural network based automatic speech recognition system. It offers
    five levels of speed-accuracy performance:
    - Faster
    - Fast
    - Balanced
    - Accurate
    - More Accurate
    
    I am using a free Streamlit plan to host this web application. The plan provides very
    limited memory so only the models with small memory footprint can be loaded. Exceeding the
    memory allocated will crash this application so I have limited the models and the size of
    the audio and video files that can be used.

    __Do not use with audio or video files over 30 mins in duration.__ I have not tested if it
    will crash. Contact me if you want better accuracy or have files with longer duration.
    ''')

# Set transcription preview length in segments 
preview_length = 5

# Map selections to Whisper models
performance_options = {
    'Faster': 'tiny',
    'Fast': 'base',
    'Balanced': 'small',
    'Accurate': 'medium',
    'More Accurate': 'large',
    }

performance_description = {
    'Faster': '(audio duration / 2)',
    'Fast': '(audio duration)',
    'Balanced': '(audio duration x 2)',
    'Accurate': '',
    'More Accurate': '',
    }

# Set default Whisper model size
model_size = performance_options['Fast']

# Display radio box
performance = st.radio(
    'Select performance: (approximate processing time in brackets)',
    options=('Faster', 'Fast'),
    index=1,
    key='per_radio_input',
    format_func=lambda label: f"{label:<6} {performance_description[label]:<21}",
    disabled=False,
    horizontal=False,
    label_visibility='visible'  # visible, hidden, collapsed
    )

# Display a placeholder for diagnostics messages
placeholder = st.empty()
with placeholder.container():
    model_size = performance_options[performance]
    # st.write(model_size)

# Display a file uploader
file = st.file_uploader('Upload an audio or video file', type=['mp3', 'aac', 'wav', 'mp4'])
if file is not None:
    # Get file extension
    file_extension = Path(file.name).suffix[1:]  # Path(file.name).suffix returns with dot, i.e., '.wav'

    # Display an audio/video player
    if file_extension == 'mp4':
        st.video(file.read(), format='video/' + file_extension, start_time=0)
    else:
        st.audio(file.read(), format='audio/' + file_extension, start_time=0)

@st.cache(allow_output_mutation=True, show_spinner=False, suppress_st_warning=True, ttl=600)
def test_cache(file, model_size):
    if file is not None:
        # Print diagnostics message; disable in production mode
        # st.write("First run. Cached in memory.")

        # Get file extension
        file_extension = Path(file.name).suffix[1:]  # Path(file.name).suffix returns with dot, i.e., '.wav'
        
        # Write uploaded file to temp storage
        with NamedTemporaryFile(suffix=file_extension) as tempFile:
            tempFile.write(file.getvalue())  # copy value of uploaded file to temporarily created file
            tempFile.seek(0)

            # Load whisper model and transcribe
            DEVICE = 'cpu'  # 'cuda' if torch.cuda.is_available() else 'cpu'
            transcribe_message = f'No GPU acceleration, transcribing using CPU ...' if DEVICE == 'cpu' else f'Transcribing using GPU ...'
            with st.spinner(transcribe_message):
                model = pywhisper.load_model(model_size, device=DEVICE)
                result = model.transcribe(audio=tempFile.name, verbose=False, fp16=False)

        # Extract transcript from segments
        transcript_text = ''

        # Transform transcript into the srt format
        for index, segment in enumerate(result['segments']):
            start_time_delta = timedelta(seconds=int(segment['start']))  # timedelta attributes: days, seconds, microseconds
            end_time_delta = timedelta(seconds=int(segment['end']))  # timedelta attributes: days, seconds, microseconds

            start_hour0 = '0' if segment['start'] < (10 * 60 * 60) else ''  # Append '0' if less than 10 hours
            end_hour0 = '0' if segment['end'] < (10 * 60 * 60) else ''  # Append '0' if less than 10 hours

            start_milliseconds = int((segment['start'] % 1) * 1000)
            end_milliseconds = int((segment['start'] % 1) * 1000)

            start_time = start_hour0 + str(start_time_delta) + ',' + f'{start_milliseconds:03d}'
            end_time = end_hour0 + str(end_time_delta) + ',' + f'{end_milliseconds:03d}'
            text = segment['text'][1:] if segment['text'][0] == ' ' else segment['text']

            segment_id = f"{segment['id'] + 1}\n"
            segment_start_time = f"{start_time} --> {end_time}\n"
            segment_end_time = f"{text}"

            transcript_text = transcript_text + '\n\n' if transcript_text != '' else transcript_text
            transcript_text = transcript_text + segment_id + segment_start_time + segment_end_time

            if index < preview_length:
                transcript_text_preview = transcript_text

        return file, transcript_text, transcript_text_preview
    else:
        return None, None, None

audio, transcript_text, transcript_text_preview = test_cache(file, model_size)

if file is not None and transcript_text != '':
    # Display 'success' status
    st.success('Transcribed.')

    # Display preview of transcript
    preview_message = f'Previewing first {preview_length} segments of transcript.'
    st.text(preview_message)
    st.text(transcript_text_preview)
    
    # Display a file download button to download completed transcript
    st.download_button(
        label='Download Transcript',
        data=transcript_text,
        file_name=str(Path(file.name).with_suffix('.srt')),
        mime='text/srt'
        )
    st.caption('Transcript is formatted in the subtitle format. Can be opened using any text editor.', unsafe_allow_html=False)