# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from cryptography.hazmat.primitives import serialization
import requests  

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruit you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:", "")
st.write("The name on your Smoothie will be:", name_on_order)

auth = st.secrets["snowflake_auth"]

key = serialization.load_pem_private_key(
    auth["private_key"].encode("utf-8"),
    password=auth["passphrase"].encode("utf-8")
)

private_key_der = key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# session = get_active_session()
cnx = st.connection("snowflake", private_key=private_key_der)
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections = 5,
    accept_new_options=True
)

if ingredients_list:
    # st.write("You selected:", ingredients_list)
    # st.text(ingredients_list)

    ingredients_string = ''
    for ing in ingredients_list:
        ingredients_string += ing + ' '
        st.subheader(ing + " Nutrition Information")
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + ing)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # st.write(my_insert_stmt)
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
        


