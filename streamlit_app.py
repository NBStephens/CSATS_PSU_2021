import git
import base64
import pathlib
import requests
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import streamlit.components.v1 as components
from typing import Dict, Tuple, Union
from matplotlib import cm
import matplotlib

#Page athestics
current_dir = pathlib.Path.cwd()
morpho_logo = "https://www.morphosource.org/themes/morphosource/graphics/morphosource/morphosourceLogo.png"
psu_logo = "https://www.underconsideration.com/brandnew/archives/penn_state_logo_detail.png"
workshop_logo = "https://www.csats.psu.edu/assets/uploads/csats-logo-new.jpg"
workshop_icon = "http://equity.psu.edu/communications-marketing/assets/psugoogle250p.jpg"
slack_link = r"https://user-images.githubusercontent.com/819186/51553744-4130b580-1e7c-11e9-889e-486937b69475.png"


plot_theme = ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
plotting_options = ['Box plots', 'Scatter plots', 'Scatter plots 3d', 'Pie charts', 'Aleph viewer', 'Histograms', "Joyplot"]



st.set_page_config(page_title="CSATS Morphosource workshop",
                        page_icon=workshop_icon,
                        layout='wide',
                        initial_sidebar_state='auto')

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


def main():
    get_CASTS_data_repo()
    data_dict = get_datasets_and_file_names()
    st.sidebar.image(workshop_logo, width=275, output_format="PNG")
    st.sidebar.image([morpho_logo, psu_logo], width=120, caption=["Duke University", "FEMR Lab"], output_format="PNG")

    csv_list = [k for k, v in data_dict.items()]
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
                                  (plotting_options))
            if option != "Aleph viewer":
                template = st.selectbox("Plot theme", plot_theme)

        st.write('Select viewing options for', option.lower())

        if str(option) == "Aleph viewer":
            aleph_view_height = st.slider("Viewer height", min_value=1, max_value=1080, value=560)
            components.iframe("https://aleph-viewer.com/", height=int(aleph_view_height))

        elif str(option) == "Box plots":
            df = current_df
            x_list = [x for x in df.columns[df.dtypes != 'float64']]
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
                scatter_trendline = None
                point_size = None
                if df[str(color_by)].nunique() > 10:
                    color_num = px.colors.qualitative.Alphabet
                else:
                    color_num = None
                try:
                    if st.checkbox("Adjust point size by another variable"):
                        point_size = st.selectbox("Point variable", size_list)
                    if st.checkbox("Fit line"):
                        fit_dict = {"Ordinary least squares": "ols", "Local regression": "lowess"}
                        fit_list = [k for k, v in fit_dict.items()]
                        scatter_trendline = st.selectbox("Fit type", fit_list)
                        scatter_trendline = fit_dict[scatter_trendline]
                    fig = px.scatter(df, x=str(x_axis), y=str(y_axis), color=df[str(color_by)].astype(str),
                                     color_discrete_sequence=color_num,
                                     size=point_size, trendline=scatter_trendline, template=template)
                    st.plotly_chart(fig, use_container_width=True)
                    #Resuls are hideous
                    #if scatter_trendline == "ols" and not None:
                        #fit_results = px.get_trendline_results(fig)
                        #st.write(fit_results)
                        #st.write(fit_results.query("Species == 'Homo sapiens'").px_fit_results.iloc[0].summary())
                        #results.query(f"sex == 'Male' and smoker == 'Yes'").px_fit_results.iloc[0].summary()
                except ValueError:
                    nans = df[str(point_size)].isnull().values.any()
                    if nans:
                        st.error(f"There are nan (not a number) values in the {point_size} column.")
                    else:
                        st.write("Select your x axis and y axis from the dropdowns")
        elif str(option) == "Scatter plots 3d":
            df = current_df
            color_list = df.columns
            size_list = [x for x in df.columns[df.dtypes != 'object']]
            x_list = [x for x in df.columns[df.dtypes != 'object']]
            y_list = [x for x in df.columns[df.dtypes != 'object']]
            z_list = [x for x in df.columns[df.dtypes != 'object']]
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                color_by = st.selectbox("Select category to color variable by", color_list)
                x_axis = st.selectbox("X axis", x_list)
                y_axis = st.selectbox("Y axis", y_list)
                z_axis = st.selectbox("Z axis", z_list)
                point_size = None
                if df[str(color_by)].nunique() > 10:
                    color_num = px.colors.qualitative.Alphabet
                else:
                    color_num = None

                if st.checkbox("Adjust point size by another variable"):
                    point_size = st.selectbox("Point variable", size_list)
                try:
                    fig = px.scatter_3d(df, x=str(x_axis), y=str(y_axis), z=str(z_axis),
                                        color=df[str(color_by)].astype(str), color_discrete_sequence=color_num,
                                        size=point_size,
                                        template=template)
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    nans = df[str(point_size)].isnull().values.any()
                    if nans:
                        st.error(f"There are nan (not a number) values in the {point_size} column.")



        elif str(option) == "Pie charts":
            df = current_df
            val_list = [x for x in df.columns[df.dtypes != 'object']]
            name_list = [x for x in df.columns[df.dtypes == 'object']]
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                pie_names = st.selectbox("Names", name_list)
                pie_vals = st.selectbox("Values", val_list)
                try:
                    fig = px.pie(df, values=pie_vals, names=pie_names, title=f'{pie_vals} colored by {pie_names}', template=template)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")

        elif str(option) == "Histograms":
            df = current_df
            val_list = [x for x in df.columns[df.dtypes != 'object']]
            name_list = df.columns
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                hist_vals = st.selectbox("Values", val_list)
                max_slider = df[hist_vals].nunique()
                hist_title = f'Histogram of {hist_vals}'
                cat_names = None
                log_val = False
                bin_num = st.slider("Number of bins", min_value=1, max_value=max_slider, value=int(max_slider*0.5))
                if st.checkbox("Separate by category"):
                    cat_names = st.selectbox("Category", name_list)
                    hist_title = f'Histogram of {hist_vals} by {cat_names}'
                if st.checkbox("Log values"):
                    log_val = True
                try:
                    fig = px.histogram(df,
                                       x=hist_vals,
                                       title=hist_title,
                                       color=cat_names,
                                       nbins=bin_num,
                                       #labels={'pie': 'total bill'},  # can specify one label per df column
                                       opacity=0.8,
                                       log_y=log_val,  # represent bars with log scale
                                       template=template
                                       )
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")
        elif str(option) == "Joyplot":
            df = current_df
            val_list = [x for x in df.columns[df.dtypes != 'object']]
            name_list = [x for x in df.columns[df.dtypes != 'float64']]
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                joy_name = st.selectbox("Groups", name_list)
                joy_vals = st.selectbox("Values", val_list)
                joy_title = f'Joyplot of {joy_vals} by {joy_name}'
                fig = px.violin(df,
                                y=joy_name,
                                x=val_list,
                                color=joy_name,
                                orientation='h',
                                title=joy_title,
                                template=template).update_traces(side='positive', width=2)
                st.plotly_chart(fig, use_container_width=True)


    #This doesn't work on the streamlit hosted version, likely due to the unsafe html setting
    #col1_lower, col2_lower = st.beta_columns(2)
    #with col1_lower:
    #    with st.beta_expander("Upload PDF"):
    #        pdf_file = st.file_uploader("", type=['pdf'])
    #    if pdf_file:
    #        with st.beta_expander("View or hide PDF"):
    #            pdf_view_size_ratio = st.slider("PDF viewer size", min_value=1, max_value=100, value=47)
    #            pdf_width = int(np.ceil(1920 * (pdf_view_size_ratio / 100)))
    #            pdf_height = int(np.ceil(pdf_width / 0.77))
    #            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    #            pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width={pdf_width} height={pdf_height} type="application/pdf">'
    #            st.markdown(pdf_display,
    #                        unsafe_allow_html=True)


    #with col2_lower:
    #    title = st.empty()



    with st.sidebar.beta_expander("About"):
            "This app helps students visualizes scientific data to explore our evolutionary history"
            "\n\n"
            "It is maintained by [Nick Stephens](https://github.com/NBStephens/). "
            "If you have any technical issues please email nbs49@psu.edu"

    with st.sidebar.beta_expander("If you have any questions, please reach out:", expanded=True):
        """ 

        Slack Chat:speech_balloon: : [CSATS](https://app.slack.com/client/T9HGD7NBY/CTN0FTQCA)\n
        Email :email: : [Tim Ryan] (tmr21@psu.edu)\n
        Email :email: : [Nick Stephens] (nbs49@psu.edu)\n    

        """
    with st.sidebar.beta_expander("Educational resources:", expanded=True):
        """
        [![MorphoSource](https://www.morphosource.org/themes/morphosource/graphics/morphosource/morphosourceLogo.png)](https://www.morphosource.org/index.php)\n     
             
        [Smithsonian Human Origins](https://humanorigins.si.edu/)\n
        
        [The Human Fossil Record](https://human-fossil-record.org/)\n
      
        [Digital Morphology](http://www.digimorph.org/index.phtml)\n    
      
        [![Africanfossils.org](https://africanfossils.org/sites/all/themes/fossil/images/homepage.png)](https://human-fossil-record.org/)\n               
        """




main()