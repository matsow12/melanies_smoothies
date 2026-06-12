# Import python packages
import streamlit as st
import requests  
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cake: Customize Your Smoothie! :cake: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.sql("SELECT FRUIT_ID, FRUIT_NAME FROM smoothies.public.fruit_options")

# 1. Konwersja Snowpark DataFrame do Pandas DataFrame i wyciągnięcie kolumny z tekstową nazwą owocu
# Upewnij się, że wielkość liter w nazwie kolumny zgadza się z bazą (zwykle wielkie litery 'FRUIT_NAME')
pd_df = my_dataframe.to_pandas()
fruit_list = pd_df['FRUIT_NAME'].tolist()

# 2. Przekazanie gotowej listy tekstowej do komponentu multicelect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    ,my_dataframe
    ,max_selections=5
    
    )

# Wyświetlenie wyniku, jeśli użytkownik coś wybrał
if ingredients_list:

    ingredients_string =''
    for fruit_chose in ingredients_list:
        ingredients_string  += fruit_chose + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+ fruit_chosen)  
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

   
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
   

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")



