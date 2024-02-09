import streamlit as st
import boto3
from botocore.exceptions import ClientError
import streamlit_authenticator as stauth

# DynamoDB client initialization
dynamodb = boto3.resource(
  'dynamodb',
  region_name='us-east-1',
  aws_access_key_id = st.secrets['AWS_ACCESS_KEY_ID'],
  aws_secret_access_key = st.secrets['AWS_SECRET_ACCESS_KEY']
)

@st.cache
def create_table():
    table = dynamodb.create_table (
        TableName = 'Users',
        KeySchema = [
            {
                'AttributeName': 'email',
                'KeyType': 'HASH'
            },
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits':1,
                    'WriteCapacityUnits':1
                }
            
        )
    table = dynamodb.Table('Users')
    return table



def create_user(email, password,table):
    try:
        response = table.put_item(
            Item={
                'email': email,
                'password': password
            },
            ConditionExpression='attribute_not_exists(email)'
        )
        st.success("User created successfully!")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            st.error("User already exists!")
        else:
            st.error("An error occurred while creating the user.")


def verify_user(email, password, table):
    # if email or password is None:
    #     st.error('Please enter the details !')
    try:
        response = table.get_item(
            Key={
                'email': email
            }
        )
        item = response.get('Item')
        if item and item['password'] == password:
            return True
        else:
            return False
    except ClientError as e:
        st.error(e)
        st.error("An error occurred while verifying the user.")
        return False
    
def signup():
    with st.form(key='signup', clear_on_submit=True):
        st.subheader(":red[Sign Up]")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.form_submit_button("Signup"):
            if password == confirm_password:
                create_user(email, password, dynamodb.Table('Users'))
            else:
                st.error("Passwords do not match.")

def login():
    with st.form(key='login', clear_on_submit=True):   
        st.subheader(":red[Login]")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if verify_user(email, password, dynamodb.Table('Users')):
                st.success("Login successful!")
            else:
                st.error("Invalid email or password.")

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
        st.success(f"File '{file.name}' uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")


def main():
    try:
        tablename = create_table()
    except ClientError as e:
        print('table already exists')
    # Page state
    page = st.sidebar.selectbox("Navigation", ["Login", "Signup"])

    if page == "Signup":
        signup()

    elif page == "Login":
        login()
    


if __name__ == "__main__":
    main()
