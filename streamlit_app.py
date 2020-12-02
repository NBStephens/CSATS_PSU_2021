import io
import os
import git
import math
#import yaml
import base64
import pathlib
import requests
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import streamlit.components.v1 as components
from PIL import Image
from collections import namedtuple
from typing import Dict, Tuple, Union

#Page athestics
current_dir = pathlib.Path.cwd()
morpho_logo = "https://www.morphosource.org/themes/morphosource/graphics/morphosource/morphosourceLogo.png"
psu_logo = "https://www.underconsideration.com/brandnew/archives/penn_state_logo_detail.png"
workshop_logo = "https://www.csats.psu.edu/assets/uploads/csats-logo-new.jpg"
workshop_icon = "http://equity.psu.edu/communications-marketing/assets/psugoogle250p.jpg"
slack_link = r"https://user-images.githubusercontent.com/819186/51553744-4130b580-1e7c-11e9-889e-486937b69475.png"
plot_theme = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

st.set_page_config(page_title="CSATS Morphosource workshop",
                        page_icon=workshop_icon,
                        layout='wide',
                        initial_sidebar_state='auto')


CORRECTIONS = {
    "DOI: ": "DOI ",
    "see: ": "see ",
    "from: ": "from ",
    "tables: ": "tables ",
    "1981â€“2016": "1981-2016",
}

@st.cache
def get_CASTS_data_repo():
    """Clones the data catalogue"""
    try:
        git.Git(".").clone("https://github.com/NBStephens/streamlit-example.git")
    except git.GitCommandError:
        repo = git.Repo("apd-core")
        repo.remotes.origin.pull()


#@st.cache(suppress_st_warning=True)
def get_datasets_and_file_names() -> Dict:
    """Returns a dictionary of categories and files

    Returns
    -------
    Dict
        Key is the name of the category, value is a dictionary with information on files in that \
        category
    """
    path = pathlib.Path("Data")
    data_files = {}
    for i in path.glob("*.csv"):
        #st.write(i)
        file = str(i.parts[-1])
        data_files.update({str(file).replace(".csv", ""): file})
    return data_files


def broken_funciton():
        with file.open() as open_file:
            open_file_content = open_file.read()
            for old, new in CORRECTIONS.items():
                open_file_content = open_file_content.replace(old, new)
            #data_info = yaml.load(open_file_content, Loader=yaml.FullLoader)

        #if category in category_files:
            #category_files[category][file_name] = data_info
        #else:
         #   category_files[category] = {file_name: data_info}
    #except UnicodeDecodeError as err:
     #   category_files[category][file_name] = "NOT READABLE"
        # logging.exception("Error. Could not read %s", file.name, exc_info=err)

def get_data_info(category: str, file_name: str) -> Dict:
    """Returns a dictionary of information on the specified file

    Parameters
    ----------
    category : str
        The name of the category, like 'Sports'
    file_name : str
        A name of a file

    Returns
    -------
    Dict
        Information on the file
    """
    path = pathlib.Path("apd-core/core") / category / file_name

    with path.open() as open_file:
        data = yaml.load(open_file.read(), Loader=yaml.FullLoader)
    return data


def create_info_table(selected_data_info: Dict):
    """Writes the information to the table

    Parameters
    ----------
    selected_data_info : Dict
        The information to show
    """
    info_table = pd.DataFrame()

    data_description = selected_data_info["description"]
    if data_description:
        line = pd.Series(data_description)
        line.name = "Description"
        info_table = info_table.append(line)

    keywords = selected_data_info["keywords"]
    if keywords:
        keywords = ", ".join(keywords.lower().split(","))
        line = pd.Series(keywords)
        line.name = "Keywords"
        info_table = info_table.append(line)

    if len(info_table) > 0:
        info_table.columns = [""]
        st.table(info_table)


@st.cache()
def check_url(url: str) -> Tuple[bool, Union[str, requests.Response]]:
    """Returns information on the availability of the url

    Parameters
    ----------
    url : str
        The url to test

    Returns
    -------
    Tuple[bool, Union[str, Response]]
        Whether the url is available and a string reponse
    """
    try:
        response = requests.head(url, allow_redirects=False)
        return True, response
    except requests.exceptions.SSLError:
        return False, "SSL error"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.InvalidSchema:
        return False, "Invalid schema"
    except requests.exceptions.MissingSchema:
        return check_url("https://" + url)


def show_homepage(data_info):
    """Shows information on the availability of the url to the user"""
    homepage = data_info["homepage"]

    if homepage.startswith("http:"):
        homepage = homepage.replace("http:", "https:")

    url_status, response = check_url(homepage)

    if url_status:
        if response.status_code in [301, 302]:
            st.info(f"{homepage}\n\nRedirects to {response.headers['Location']}")
        else:
            st.success(f"{homepage}")
    else:
        if response == "Connection error":
            st.error(f"{homepage}\n\nThere is a connection issue to this website.")
        elif response == "SSL error":
            st.warning(f"There might be an SSL issue with {homepage}\n\nProceed with caution!")
        else:
            st.info(f"{homepage}")


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    Adapted from:
    https://discuss.streamlit.io/t/heres-a-download-function-that-works-for-dataframes-and-txt/4052

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)


###Begin of main application

def main():
    get_CASTS_data_repo()

    data_dict = get_datasets_and_file_names()

    csv_list = [k for k, v in data_dict.items()]
    st.sidebar.image(workshop_logo, width=275, output_format="PNG")
    st.sidebar.image([morpho_logo, psu_logo], width=130, caption=["Duke University", "FEMR Lab"], output_format="PNG")
    """
    # Welcome to CSATS Morphosource Workshop! :skull:

    """

    col1, col2 = st.beta_columns(2)
    # Writes out a thing line across the gui page.


    with col1:
        option = st.selectbox('Select dataset', csv_list, key=9990237)

        st.write('Viewing', option)

        # Have to put ?raw=True at end to get the data

        #brain_data = "https://github.com/NBStephens/streamlit-example/blob/master/Data/Powell%20Data%20-%20BrainSize%20vs%20BodySize.csv?raw=true"
        #brain_paper = "https://github.com/NBStephens/streamlit-example/blob/master/Data/Powell%20et%20al.%2C%202017.pdfraw=truu"


        current_df = pd.read_csv(f"Data/{data_dict[option]}")
        current_df_columns = current_df.columns

        #current_pdf = brain_paper


        with st.beta_expander("View/hide current dataset", expanded=True):
            if st.checkbox("Transpose"):
                current_df = current_df.T
            st.write(current_df)
            if st.checkbox("View Data types for troubleshooting"):
                st.write(current_df.dtypes)
            if st.button('Download dataset as a CSV'):
                tmp_download_link = download_link(current_df,
                                                  download_filename=f'{str(option)}.csv',
                                                  download_link_text=f'Click here to download {str(option)} data!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

    with col2:
        with st.beta_expander("Choose viewing options", expanded=True):
            option = st.selectbox('Select a display type',
                                  ('Box plots', 'Scatter plots', 'Pie charts', 'Aleph viewer'))
            if option != "Aleph viewer":
                template = st.selectbox("Plot theme", plot_theme)

        st.write('Select viewing options for', option.lower())

        if str(option) == "Aleph viewer":
            aleph_view_height = st.slider("Viewer height", min_value=1, max_value=1080, value=560)
            components.iframe("https://aleph-viewer.com/", height=int(aleph_view_height))

        elif str(option) == "Box plots":
            df = current_df
            x_list = [x for x in df.columns[df.dtypes == 'object']]
            y_list = [x for x in df.columns[df.dtypes != 'object']]
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                x_axis = st.selectbox("X axis", x_list)
                y_axis = st.selectbox("Y axis", y_list)
                try:
                    if st.checkbox("See underlying data points"):
                        see_points = "all"
                    else:
                        see_points = False
                    fig = px.box(df, x=str(x_axis), y=str(y_axis), points=see_points, color=str(x_axis), template=template)
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")
        elif str(option) == "Scatter plots":
            df = current_df
            color_list = df.columns
            size_list = [x for x in df.columns[df.dtypes != 'object']]
            x_list = df.columns
            y_list = df.columns
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                color_by = st.selectbox("Select category to color variable by", color_list)
                x_axis = st.selectbox("X axis", x_list)
                y_axis = st.selectbox("Y axis", y_list)
                try:
                    if st.checkbox("Adjust point size by another variable"):
                        point_size = st.selectbox("Point variable", size_list)
                    else:
                        point_size = None
                    fig = px.scatter(df, x=str(x_axis), y=str(y_axis), color=color_by, size=point_size, template=template)
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")


    col1_lower, col2_lower = st.beta_columns(2)
    with col1_lower:
        with st.beta_expander("Upload PDF"):
            pdf_file = st.file_uploader("", type=['pdf'])
        if pdf_file:
            with st.beta_expander("View or hide PDF"):
                pdf_view_size_ratio = st.slider("PDF viewer size", min_value=1, max_value=100, value=47)
                pdf_width = int(np.ceil(1920 * (pdf_view_size_ratio / 100)))
                pdf_height = int(np.ceil(pdf_width / 0.77))
                base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width={pdf_width} height={pdf_height} type="application/pdf">'
                st.markdown(pdf_display,
                            unsafe_allow_html=True)


    with col2_lower:
        title = st.empty()



    with st.sidebar.beta_expander("About"):
            "This app helps students visualizes scientific data to explore our evolutionary history"
            "\n\n"
            "It is maintained by [Nick Stephens](https://github.com/NBStephens/). "
            "If you have any technical issues please email nbs49@psu.edu"

    with st.sidebar.beta_expander("If you have any questions, please reach out:", expanded=True):
        """ 

        Slack Chat:speech_balloon: : [CSATS](https://app.slack.com/client/T9HGD7NBY/CTN0FTQCA)\n
        Email :email: : [Tim Ryan] (tmr21@psu.edu)\n
        Email :email: : [Nick stephens] (nbs49@psu.edu)\n    

        """
    with st.sidebar.beta_expander("Educational resources:", expanded=True):
        local_css("./visuals/style.css")
        remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

        icon("search")
        selected = st.sidebar.text_input("", "Search...")
        button_clicked = st.sidebar.button("OK")
        if button_clicked:
            st.sidebar.write("I've been clicked!")


        st.sidebar.markdown(body="""
        [MorphoSource](https://www.morphosource.org/index.php)\n
        [The Human Fossil Record](https://human-fossil-record.org/)\n             
        [<img src="https:/africanfossils.org/sites/all/themes/fossil/images/homepage_2x.png" width="250"/>](https://human-fossil-record.org/)\n
        """,
        unsafe_allow_html=True)



main()