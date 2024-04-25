import streamlit as st
import requests

# Function to fetch movies based on zip code, date, and radius
def fetch_movies(zip_code, date, radius):
    params = {
        "startDate": date,
        "numDays": 1,
        "zip": zip_code,
        "radius": radius,
        "units": "mi",
        "imageSize": "Ms",
        "imageText": "true",
        "api_key": "33tvyvt9hmmc5xnkuvurwx43"
    }
    headers = {
        "X-Originating-IP": "71.63.18.27"
    }
    url = "http://data.tmsapi.com/v1.1/movies/showings"
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to format runtime
def clean_runtime(runtime):
    if not runtime:
        return ''
    return runtime.replace('PT', '').replace('H', 'h ').replace('M', 'm').strip()

# Function to display movie carousel in the Streamlit app
def display_carousel(movies):
    for movie in movies:
        col1, col2 = st.columns([1, 3])  # Reduced gap between columns
        with col1:
            if movie.get('poster_url'):
                st.image(movie['poster_url'], width=150)  # Specify width to control size
        with col2:
            st.markdown(f"#### {movie['title']}  \n*Runtime: {clean_runtime(movie.get('run_time', ''))}*")
            st.markdown(f"**Release Date:** {movie['release_date']}")
            st.markdown(f"**Genres:** {movie['genres']}")
            st.markdown(f"**Rating:** {movie['rating']}")
            if movie.get('advisories'):
                st.markdown(f"**Advisories:** {movie['advisories']}")
            st.markdown(f"**Cast:** {movie['cast']}")
            st.markdown(f"**Directors:** {movie['directors']}")

            # Organize showtimes by theatre
            theatre_dict = {}
            for showtime in movie['showtimes']:
                theatre_name = showtime['theatre']['name']
                show_time = showtime['dateTime'].split('T')[1][:5]  # Extract the time part
                ticket_link = showtime.get('ticketURI', 'No link available')
                if theatre_name not in theatre_dict:
                    theatre_dict[theatre_name] = {"times": [show_time], "ticket_link": ticket_link}
                else:
                    theatre_dict[theatre_name]["times"].append(show_time)

            for theatre, details in theatre_dict.items():
                time_str = ', '.join(details["times"])
                st.markdown(f"**{theatre}** - {time_str} - [Tickets]({details['ticket_link']})")

            with st.expander("View Description", expanded=False):
                st.write(movie['description'])
            st.markdown("---")  # Use markdown to control the separator style

# Main App
logo_col, title_col = st.columns([1, 15])
with logo_col:
    st.image('https://media.licdn.com/dms/image/C560BAQEcHQJxZidEtA/company-logo_200_200/0/1674925962550?e=1721865600&v=beta&t=-hn6nPrYzvJiqATGaDC4JlE7iSrFHZQ-r9bCZmXM9Uc', width=50)  # Adjust the path and width as needed
with title_col:
    st.markdown("### OurDate Movie Destinations", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    zip_code = st.text_input("Enter your Zip Code", max_chars=10)
with col2:
    date = st.date_input("Select Date")
with col3:
    radius = st.slider("Search Radius (miles)", min_value=1, max_value=30, value=2)

# Button to fetch movies and display results
if st.button("Find Movies"):
    with st.spinner("Fetching movies..."):
        movies_data = fetch_movies(zip_code, str(date), radius)
        if movies_data:
            st.session_state.movies_details = [
                {
                    "title": movie['title'],
                    "release_date": movie.get('releaseDate', ''),
                    "genres": ', '.join(movie.get('genres', [])),
                    "description": movie.get('longDescription', ''),
                    "cast": ', '.join(movie.get('topCast', [])),
                    "directors": ', '.join(movie.get('directors', [])),
                    "rating": movie.get('ratings', [{}])[0].get('code', 'NR'),
                    "run_time": clean_runtime(movie.get('runTime', '')),
                    "poster_url": f"https://cuso.tmsimg.com/{movie['preferredImage']['uri']}" if 'preferredImage' in movie else 'No poster URL available',
                    "showtimes": movie.get('showtimes', [])
                }
                for movie in movies_data
            ]
            # Store initial state to use later in filtering
            st.session_state.initial_movies = st.session_state.movies_details
        else:
            st.error("Failed to fetch movies. Please try again later.")

# Genre filter dropdown, displayed only if movies are fetched
if 'movies_details' in st.session_state:
    genres = set()
    for movie in st.session_state.movies_details:
        genres.update(movie['genres'].split(', '))
    selected_genre = st.selectbox("Filter by genre:", ['All'] + sorted(genres))
    
    if selected_genre == 'All':
        filtered_movies = st.session_state.initial_movies
    else:
        filtered_movies = [movie for movie in st.session_state.initial_movies if selected_genre in movie['genres']]
    
    display_carousel(filtered_movies)
