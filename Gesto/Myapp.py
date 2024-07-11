import streamlit as st
from ht import activate_camera
from htser import activate_serial
from sounds import get_base64_of_audio,move_file



st.title("Welcome to GESTO MIMICKING LIMB")

def about_us():
    st.title('About Us')
    st.write("Welcome to Gesto Mimicking Limb, where innovation meets functionality. We are a team of passionate engineers and developers dedicated to revolutionizing the way we interact with technology. Our journey began with a shared vision to harness the power of hand gestures for controlling robotic arms, and today, we proudly present our groundbreaking solution to the world.")
    st.title('Meet the Team')
    st.write('Josen P Joseph')
    st.write('DEPARTMENT OF COMPUTER SCIENCE ENGINEERING, SEMESTER 6')
    st.write('Joyal Sunoj')
    st.write('DEPARTMENT OF COMPUTER SCIENCE ENGINEERING, SEMESTER 6')
    st.write('Pavan Sreekumar')
    st.write('DEPARTMENT OF COMPUTER SCIENCE ENGINEERING, SEMESTER 6')
    st.write('Zach Saji Varghese')
    st.write('DEPARTMENT OF COMPUTER SCIENCE ENGINEERING, SEMESTER 6')
    st.title('Our Innovation')
    st.write('At the heart of our endeavor lies the seamless integration of cutting-edge technologies. Our application leverages the power of OpenCV MediaPipe Handtracking combined with Arduino programming to enable intuitive control of robotic arms through hand gestures. Whether it is Bluetooth or wired serial communication, our solution ensures reliable connectivity between your device and the robotic arm, unlocking a world of possibilities for automation and precision.')
    st.title('Our Mission')
    st.write('Driven by a passion for innovation and a commitment to excellence, we strive to empower individuals and industries alike with accessible, intuitive solutions. Our mission is to push the boundaries of whats possible, redefining the relationship between humans and machines for a brighter, more efficient future.')
    st.title('Get in Touch')
    st.write('We are always eager to connect with fellow enthusiasts, collaborators, and potential partners. If you have any questions, feedback, or inquiries, dont hesitate to reach out to us. Together, lets shape the future of technology, one gesture at a time.')




def home():
    st.header('Interact with Robo')
    st.write("Welcome to control our Gesto Mimicking Limb!")
    st.markdown('<p style="color:red">Select one of the available connections.</p>', unsafe_allow_html=True)
    if st.button("Bluetooth"):
        activate_camera()
    if st.button("Wired"):
        activate_serial()



def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ('Home', 'About Us'))

    if page == 'Home':
        
        home()
        audio_base64 = get_base64_of_audio(move_file)
        html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
        st.markdown(html, unsafe_allow_html=True)
    elif page == 'About Us':
        
        about_us()
        audio_base64 = get_base64_of_audio(move_file)
        html = f'<audio src="data:audio/mp3;base64,{audio_base64}" autoplay="autoplay" type="audio/mpeg" />'
        st.markdown(html, unsafe_allow_html=True)

    st.write("---")
   

if __name__ == "__main__":
    main()
