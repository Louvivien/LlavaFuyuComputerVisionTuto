import os
import tempfile
import streamlit as st
from imgurpython import ImgurClient
import replicate
from dotenv import load_dotenv

# Load .env file
root_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)


st.set_page_config(page_title="Automated Social Media Ad Generator", layout="wide")

client_id = os.getenv('IMGUR_CLIENT_ID')
client_secret = os.getenv('IMGUR_CLIENT_SECRET')
replicate_key = os.getenv('REPLICATE_KEY')


client = ImgurClient(client_id,client_secret)



def main():
    st.title("Automated Social Media Ad Generator")

    # Sidebar for entering API keys
    st.sidebar.title("API Key Configuration")
    replicate_key = st.sidebar.text_input("Enter Replicate API token:")
    imgur_client_id = st.sidebar.text_input("Enter Imgur Client ID:")
    imgur_client_secret = st.sidebar.text_input("Enter Imgur Client Secret:")

    if st.sidebar.button("Submit"):
        st.session_state['replicate_key'] = replicate_key
        st.session_state['imgur_client_id'] = imgur_client_id
        st.session_state['imgur_client_secret'] = imgur_client_secret


# Function to identify image type using Fuyu-8B model
def get_image_type(image_url):
    """
    Utilizes the Fuyu-8B model via Replicate to identify the type of image.
    Takes the URL of the uploaded image as input and returns a string describing the image type.
    """
    output = replicate.run(
        "lucataco/fuyu-8b:42f23bc876570a46f5a90737086fbc4c3f79dd11753a28eaa39544dd391815e9",
        input={
            "image": image_url,
            "prompt": "As a professional Advertisement Analyst describe this image in a few words.",
            "max_new_tokens": 512
        }
    )
    result = ''.join(item for item in output)
    return result

# Function to generate ad description using LLaVA model
def get_description(file_path, image_type):
    """
    Utilizes the LLaVA model via Replicate to generate a captivating ad description based on the image type.
    Takes the file path of the uploaded image and the identified image type as inputs.
    Returns a string containing the generated ad description.
    """
    prompt = f"Generate a captivating and informative ad description for promoting the {image_type} shown in the image, highlighting its unique features and appealing to potential customers."
    output = replicate.run(
        "yorickvp/llava-13b:2facb4a474a0462c15041b78b1ad70952ea46b5ec6ad29583c0b29dbd4249591",
        input={
            "image": open(file_path, "rb"),
            "prompt": prompt,
        }
    )
    result = ''.join(item for item in output)
    return result



uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
        with st.spinner("Uploading image..."):
            tfile = tempfile.NamedTemporaryFile(delete=True)
            tfile.write(uploaded_file.read())
            image = client.upload_from_path(tfile.name)
            image_url = image['link']
        st.image(image_url, caption="Uploaded Image.", use_column_width=True)

        with st.spinner("Identifying image type..."):
                    image_type = get_image_type(image_url)
                    st.write(f"Image Type: {image_type}")

        with st.spinner("Generating description..."):
                    description = get_description(tfile.name, image_type)
                    st.write(f"Description: {description}")



        ad_text = st.text_area("Customize the ad text:", f"Discover the perfect {image_type.lower()}! {description}")
        if st.button("Preview Ad"):
                    st.write("## Ad Preview:")
                    st.write(ad_text)
                    st.image(image_url, use_column_width=True)



if __name__ == "__main__":
    main()