import git
import base64
import pathlib
import requests
import pandas as pd
import altair as alt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
plotting_options = ['Box plots', 'Violin plots', 'Scatter plots', 'Scatter plots 3d', 'Line plot', 'Histograms', 'Pie charts', 'Joyplot', 'Aleph viewer']



st.set_page_config(page_title="CSATS Morphosource workshop",
                        page_icon=workshop_icon,
                        layout='wide',
                        initial_sidebar_state='auto')

@st.cache
def get_CASTS_data_repo():
    """Clones the data catalogue"""
    try:
        git.Git(".").clone("https://github.com/NBStephens/CSATS_PSU_2021.git")
    except git.GitCommandError:
        try:
            repo = git.Repo("./")
            repo.remotes.origin.pull()
        except:
            pass


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
    if len(data_files) == 0:
        path = pathlib.Path.cwd().joinpath("CSATS_PSU_2021").joinpath("Data")
        for i in path.glob("*.csv"):
            # st.write(i)
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


    # TODO bar graph
    # TODO Remove log names

    option = st.selectbox('Select dataset', csv_list, key=9990237)
    st.write('Viewing', option)
    # Have to put ?raw=True at end to get the data

    with st.beta_expander("View/hide current dataset", expanded=True):
        if option:
            try:
                current_df = pd.read_csv(f"Data/{data_dict[option]}")
            except:
                current_df = pd.read_csv(pathlib.Path.cwd().joinpath("CSATS_PSU_2021").joinpath(f"Data/{data_dict[option]}"))
        else:
            st.write("Please select a dataset from the drop down")
        if len(current_df) != 0:
            if st.checkbox("Transpose"):
                current_df = current_df.T
            st.write(current_df)
            if st.checkbox("View Data types for troubleshooting (internal use, this will be hidden)"):
                st.write(current_df.dtypes)
            if st.button('Download dataset as a CSV'):
                tmp_download_link = download_link(current_df,
                                                  download_filename=f'{str(option)}.csv',
                                                  download_link_text=f'Click here to download {str(option)} data!')
                st.markdown(tmp_download_link, unsafe_allow_html=True)
        else:
            current_df = pd.DataFrame()

    if len(current_df) != 0:
        with st.beta_expander(f"View/Hide plotting options"):
            plotting_col1, plotting_col2, plotting_col3 = st.beta_columns((1, 1, 3))
            with plotting_col1:
                option = st.selectbox('Select a display type',
                                      (plotting_options))
            with plotting_col2:
                if option != "Aleph viewer":
                    template = st.selectbox("Plot theme", plot_theme)
            with plotting_col3:
                st.empty()
            st.write('Select viewing options for', option.lower())

        if str(option) == "Aleph viewer":
            aleph_view_height = st.slider("Viewer height", min_value=1, max_value=1080, value=560)
            components.iframe("https://aleph-viewer.com/", height=int(aleph_view_height))

        elif str(option) == "Box plots":
            df = current_df
            x_list = [x for x in df.columns[df.dtypes != 'float64']]
            y_list = [x for x in df.columns[df.dtypes != 'object']]
            with st.beta_expander(f"View/Hide {option.lower()}"):
                col1, col2, col3, col4, col5 = st.beta_columns((1, 1, 2, 1, 1))
                with col1:
                    x_axis = st.selectbox("X axis", x_list)
                with col2:
                    y_axis = st.selectbox("Y axis", y_list)
                with col4:
                    st.write("\n")
                    st.write("\n")
                    if st.checkbox("See data points"):
                        see_points = "all"
                    else:
                        see_points = False
                with col5:
                    st.write("\n")
                    st.write("\n")
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False

            fig = px.box(df, x=str(x_axis), y=str(y_axis), points=see_points, color=str(x_axis), template=template)
            fig.update_layout(showlegend=view_legend)
            st.plotly_chart(fig, use_container_width=True)

        elif str(option) == "Scatter plots":
            df = current_df
            color_list = df.columns
            size_list = [x for x in df.columns[df.dtypes != 'object']]
            x_list = df.columns
            y_list = df.columns
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                col1, col2, col3, col4, col5, col6 = st.beta_columns((1, 1, 1, 1, 1, 1))
                with col1:
                    color_by = st.selectbox("Color points by", color_list)
                    if df[str(color_by)].nunique() > 10:
                        color_num = px.colors.qualitative.Alphabet
                    else:
                        color_num = None
                with col2:
                    x_axis = st.selectbox("X axis", x_list)
                with col3:
                    y_axis = st.selectbox("Y axis", y_list)
                with col4:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False
                with col5:
                    if st.checkbox("Scale points variable"):
                        point_size = st.selectbox("Point variable", size_list)
                        figure_title = f"Scatter plot of {x_axis} by {y_axis} with points scaled by {point_size}"
                    else:
                        point_size = None
                        figure_title = f"Scatter plot of {x_axis} by {y_axis}"
                with col6:
                    if st.checkbox("Fit line"):
                        fit_dict = {"Ordinary least squares": "ols", "Local regression": "lowess"}
                        fit_list = [k for k, v in fit_dict.items()]
                        scatter_trendline = st.selectbox("Fit type", fit_list)
                        scatter_trendline = fit_dict[scatter_trendline]
                    else:
                        scatter_trendline = None
                try:
                    fig = px.scatter(df, x=str(x_axis), y=str(y_axis), color=df[str(color_by)].astype(str),
                                     color_discrete_sequence=color_num, title=figure_title,
                                     size=point_size, trendline=scatter_trendline, template=template)
                    fig.update_layout(showlegend=view_legend, legend_title_text=f'{color_by}')
                    st.plotly_chart(fig, use_container_width=True)
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
                col1, col2, col3, col4, col5, col6 = st.beta_columns((1, 1, 1, 1, 1, 1))
                with col1:
                    color_by = st.selectbox("Color points by", color_list)
                    if df[str(color_by)].nunique() > 10:
                        color_num = px.colors.qualitative.Alphabet
                    else:
                        color_num = None
                with col2:
                    x_axis = st.selectbox("X axis", x_list)
                with col3:
                    y_axis = st.selectbox("Y axis", y_list)
                with col4:
                    z_axis = st.selectbox("Z axis", z_list)
                with col5:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False
                with col6:
                    if st.checkbox("Scale points variable"):
                        point_size = st.selectbox("Point variable", size_list)
                        figure_title = f"Scatter plot of {x_axis} by {y_axis} by {z_axis }with points scaled by {point_size}"
                    else:
                        point_size = None
                        figure_title = f"Scatter plot of {x_axis} by {y_axis} by {z_axis}"
                if df[str(color_by)].nunique() > 10:
                    color_num = px.colors.qualitative.Alphabet
                else:
                    color_num = None
                try:
                    fig = px.scatter_3d(df, x=str(x_axis), y=str(y_axis), z=str(z_axis),
                                        color=df[str(color_by)].astype(str), color_discrete_sequence=color_num,
                                        size=point_size, title=figure_title,
                                        template=template)
                    fig.update_layout(showlegend=view_legend, legend_title_text=f'{color_by}')
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
                col1, col2, col3, col4, col5, col6 = st.beta_columns((1, 1, 1, 1, 1, 1))
                with col1:
                    pie_names = st.selectbox("Divide pie by", name_list)
                    if df[str(pie_names)].nunique() > 10:
                        pie_pie_names = px.colors.qualitative.Alphabet
                    else:
                        pie_pie_names = None
                with col2:
                    pie_vals = st.selectbox("Values", val_list)
                with col5:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False
                with col6:
                    if st.checkbox("Remove small text"):
                        small_text = 'hide'
                    else:
                        small_text = False

                try:
                    fig = px.pie(df, values=pie_vals, names=pie_names,
                                 title=f'Pie chart of {pie_vals} colored by {pie_names}',
                                 template=template, color_discrete_sequence=pie_pie_names)
                    fig.update_traces(textposition='inside', textinfo='percent+label', insidetextorientation='radial')
                    fig.update_layout(showlegend=view_legend, legend_title_text=f'{pie_names}',
                                      uniformtext_minsize=12, uniformtext_mode=small_text)
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")

        elif str(option) == "Histograms":
            df = current_df
            val_list = [x for x in df.columns[df.dtypes != 'object']]
            name_list = df.columns
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                col1, col2, col3, col4, col5 = st.beta_columns((1, 3, 1, 1, 1))
                with col1:
                    hist_vals = st.selectbox("X-axis values", val_list)
                with col2:
                    max_slider = df[hist_vals].nunique()
                    bin_num = st.slider("Number of bins", min_value=1, max_value=max_slider, value=int(max_slider*0.5))
                    bar_opacity = float(st.slider("Bar opacity", min_value=0, max_value=100, value=80)/100)
                with col3:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False

                with col4:
                    if st.checkbox("Plot by variable"):
                        cat_names = st.selectbox("Category", name_list)
                        hist_title = f'Histogram of {hist_vals} by {cat_names}'
                        legend_title = f'{cat_names}'
                    else:
                        cat_names = None
                        hist_title = f'Histogram of {hist_vals}'
                        legend_title = f'{hist_vals}'
                    if cat_names:
                        if df[str(cat_names)].nunique() > 10:
                            cat_color = px.colors.qualitative.Alphabet
                        else:
                            cat_color = None
                    else:
                        cat_color = None
                with col5:
                    if st.checkbox("Log values"):
                        log_val = True
                    else:
                        log_val = False
                try:
                    fig = px.histogram(df, x=hist_vals, title=hist_title,
                                       color=cat_names, nbins=bin_num,
                                       opacity=bar_opacity, log_y=log_val,  # represent bars with log scale
                                       template=template, color_discrete_sequence=cat_color)
                    fig.update_layout(showlegend=view_legend, legend_title_text=legend_title)
                    st.plotly_chart(fig, use_container_width=True)
                except ValueError:
                    st.write("Select your x axis and y axis from the dropdowns")

        elif str(option) == "Violin plots":
            df = current_df
            val_list = df.columns
            binary_list = [x for x in df.columns if df[str(x)].nunique() == 2]
            name_list = df.columns
            split_plot = False
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                col1, col2, col3, col4, col5 = st.beta_columns((1, 1, 1, 1, 1))
                with col1:
                    violin_x_vals = st.selectbox("X-axis values", val_list)
                    legend_title = f'{violin_x_vals}'
                    if df[str(violin_x_vals)].nunique() > 10:
                        cat_color = px.colors.qualitative.Alphabet
                    else:
                        cat_color = None
                with col2:
                    violin_y_vals = st.selectbox("Y-axis values", val_list)
                    if st.checkbox("Second Y-axis"):
                        grouped_violin = True
                        violin_y_vals_2 = st.selectbox("Second y-axis values", val_list)
                        legend_title = f''
                        violin_title = f'Violin plot of {violin_y_vals} and {violin_y_vals_2} by {violin_x_vals} '
                    else:
                        grouped_violin = False
                        violin_title = f'Violin plot of {violin_y_vals} by {violin_x_vals}'


                with col3:
                    chart_height = st.slider("Chart height", min_value=1, max_value=1440, value=500, step=1)
                    cat_spacing = float(st.slider("Distribution overlap", min_value=1, max_value=100, value=20, step=1)*0.1)

                with col4:
                    if grouped_violin:
                        st.empty()
                    else:
                        if st.checkbox("Separate by variable"):
                            cat_names = st.selectbox("Category", name_list)
                            violin_title = f'Violin plot of {violin_y_vals} by {violin_x_vals} divided by {cat_names}'
                            legend_title = f'{cat_names}'
                            if df[str(cat_names)].nunique() > 10:
                                cat_color = px.colors.qualitative.Alphabet
                            else:
                                cat_color = None
                        else:
                            cat_names = violin_x_vals
                    if binary_list:
                        if st.checkbox("Split by variable"):
                            split_plot = True
                            split_names = st.selectbox("Split by", binary_list)
                            split_left = str(df[str(split_names)].unique()[0])
                            split_right = str(df[str(split_names)].unique()[1])
                            legend_title = f'{split_names}'
                            violin_title = f'Violin plot of {violin_y_vals} by {violin_x_vals} split by {split_names}'
                        else:
                            split_plot = False

                with col5:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False
                    if st.checkbox("View data points"):
                        view_points = "all"
                    else:
                        view_points = False
                    if st.checkbox("Overlay box plot"):
                        view_box = True
                    else:
                        view_box = False
                if grouped_violin:
                    group1 = go.Violin(x=df[f'{violin_x_vals}'],
                                            y=df[f'{violin_y_vals}'], name=f"{violin_y_vals}",
                                            box_visible=view_box, meanline_visible=True, points=view_points)
                    group2 = go.Violin(x=df[f'{violin_x_vals}'],
                                            y=df[f'{violin_y_vals_2}'], name=f"{violin_y_vals_2}",
                                            box_visible=view_box, meanline_visible=True, points=view_points)

                    fig = go.Figure(data=[group1, group2], layout={"violinmode": "group"})
                    fig.update_layout(showlegend=view_legend, title_text=violin_title, legend_title_text=legend_title,
                                      height=chart_height, width=1000,
                                      violingap=float(cat_spacing * 0.10))

                elif split_plot:
                    fig = go.Figure()
                    fig.add_trace(go.Violin(x=df[f'{violin_x_vals}'][df[f'{split_names}'] == split_left],
                                            y=df[f'{violin_y_vals}'][df[f'{split_names}'] == split_left],
                                            legendgroup='Yes', scalegroup='Yes', name=f"{split_left}",
                                            side='negative', box_visible=view_box)
                                  )
                    fig.add_trace(go.Violin(x=df[f'{violin_x_vals}'][df[f'{split_names}'] == split_right],
                                            y=df[f'{violin_y_vals}'][df[f'{split_names}'] == split_right],
                                            legendgroup='No', scalegroup='No', name=f"{split_right}",
                                            side='positive', box_visible=view_box)
                                  )
                    fig.update_traces(meanline_visible=True, width=cat_spacing, points=view_points)
                    fig.update_layout(showlegend=view_legend, title_text=violin_title, legend_title_text=legend_title, height=chart_height,
                                      violingap=float(cat_spacing * 0.10), violinmode='overlay')

                else:
                    fig = px.violin(df, x=f"{violin_x_vals}", y=f"{violin_y_vals}", color=f"{cat_names}", title=violin_title,
                                    box=view_box, points=view_points, template=template, color_discrete_sequence=cat_color,
                                    height=chart_height).update_traces(side=None, width=cat_spacing, meanline_visible=True)
                    fig.update_layout(showlegend=view_legend, legend_title_text=legend_title)
                st.plotly_chart(fig, use_container_width=True)


        elif str(option) == "Line plot":
            df = current_df
            val_list = df.columns
            name_list = df.columns
            st.warning("Line charts work best with time series data, and the preloaded datasets don't really work here")
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                col1, col2, col3, col4, col5 = st.beta_columns((1, 1, 1, 1, 1))
                with col1:
                    line_x_vals = st.selectbox("X-axis values", val_list)
                with col2:
                    line_y_vals = st.selectbox("Y-axis values", val_list)
                with col3:
                    if st.checkbox("Color line by variable"):
                        line_names = st.selectbox("Color lines by", name_list)
                        line_title = f'Line plot of {line_x_vals} by {line_y_vals} colored by {line_names}'
                        legend_title = f'{line_names}'
                        if df[str(line_names)].nunique() > 10:
                            line_palette = px.colors.qualitative.Alphabet
                        else:
                            line_palette = None

                    else:
                        line_names = None
                        line_palette = None
                        legend_title = None
                        line_title = f'Line plot of {line_x_vals} by {line_y_vals}'

                with col4:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False

                with col5:
                    st.empty()

                fig = px.line(df, x=line_x_vals, y=line_y_vals, title=line_title,
                                   color=line_names, template=template, color_discrete_sequence=line_palette)
                fig.update_layout(showlegend=view_legend, legend_title_text=legend_title)
                st.plotly_chart(fig, use_container_width=True)


        elif str(option) == "Joyplot":
            df = current_df
            val_list = [x for x in df.columns[df.dtypes != 'object']]
            name_list = [x for x in df.columns[df.dtypes != 'float64']]
            with st.beta_expander(f"View/Hide {option.lower()}", expanded=True):
                col1, col2, col3, col4, col5, col6 = st.beta_columns((1, 1, 2, 1, 1, 1))
                with col1:
                    joy_name = st.selectbox("Groups", name_list)
                with col2:
                    joy_vals = st.selectbox("Values", val_list)
                    min_val = float(df[f"{joy_vals}"].min())
                    std_val = float(df[f"{joy_vals}"].std())
                    max_val = float(df[f"{joy_vals}"].max()) + (3.00 * std_val)
                    if min_val > 0:
                        range_x = [0, max_val]
                    else:
                        range_x = [min_val, max_val]
                with col3:
                    chart_height = st.slider("Chart height", min_value=1, max_value=1440, value=500, step=1)
                    cat_spacing = float(st.slider("Distribution overlap", min_value=1, max_value=100, value=20, step=1)*0.1)
                with col5:
                    if st.checkbox("View legend"):
                        view_legend = True
                    else:
                        view_legend = False
                joy_title = f'Joyplot of {joy_vals} by {joy_name}'
                legend_title = f"{joy_name}"
                #st.help(px.violin)
                fig = px.violin(df, y=joy_name, x=val_list, range_x=range_x,
                                color=joy_name, orientation='h',
                                title=joy_title, template=template,
                                height=chart_height).update_traces(side='positive', width=cat_spacing)
                fig.update_layout(showlegend=view_legend, legend_title_text=legend_title)
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
      
        [![Africanfossils.org](https://africanfossils.org/sites/all/themes/fossil/images/homepage.png)](https://africanfossils.org/)\n               
        """




main()