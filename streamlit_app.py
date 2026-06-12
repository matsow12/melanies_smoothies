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

# NAWIGACJA: Dodano SEARCH_ON do zapytania SQL, aby kod niżej działał
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.sql("SELECT FRUIT_ID, FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options")

# Konwersja do Pandas DataFrame
pd_df = my_dataframe.to_pandas()
# Wyciągamy listę tekstową nazw owoców
fruit_list = pd_df['FRUIT_NAME'].tolist()

# POPRAWKA 1: Przekazujemy fruit_list zamiast my_dataframe, aby widzieć nazwy, a nie ID
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Wyświetlenie wyniku, jeśli użytkownik coś wybrał
if ingredients_list:
    ingredients_string = ''
    
    # POPRAWKA 2: Ujednolicono nazwę zmiennej na fruit_chosen
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Pobieramy wartość do API z kolumny SEARCH_ON (zgodnie z Badge 3!)
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        # POPRAWKA 3: Do API przekazujemy zmienną search_on zamiast fruit_chosen!
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)  
        
        if smoothiefroot_response.status_code == 200:
            sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.warning(f"Could not find nutrition info for {fruit_chosen}")

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")



