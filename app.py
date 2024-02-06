import streamlit as st
import boto3

# Set your AWS credentials securely using a secrets file
# st.set_option('secrets', '.streamlit/secrets.toml')  # Adjust path as needed

# Function to handle file upload and S3 transfer
def upload_to_s3(file):
    bucket_name = st.secrets['AWS_BUCKET_NAME']
    region_name = 'us-east-1'  # Replace with your AWS region

    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'],
        region_name=region_name
    )

    try:
        s3.upload_fileobj(file, bucket_name, file.name)
        st.success(f"File '{file.name}' uploaded to S3 bucket '{bucket_name}' successfully!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

# Create the Streamlit UI
st.title("File Upload to S3")

uploaded_file = st.file_uploader("Choose a file to upload")

if uploaded_file is not None:
    if st.button("Upload to S3"):
        with st.spinner("Uploading..."):
            upload_to_s3(uploaded_file)
