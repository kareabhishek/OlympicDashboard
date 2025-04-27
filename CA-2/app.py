from pathlib import Path
import pandas as pd
from shiny import App, ui, render, reactive
import plotly.express as px
from shinywidgets import output_widget, render_widget

right_nav_css = """
<style>
.navbar-nav {
    margin-left: auto !important;
    flex-direction: row !important;
    justify-content: flex-end !important;
    gap: 15px; /* Adjust the space between tabs */
}
.nav-item {
    margin-right: 0 !important; /* Ensure no extra margin on individual items */
}
</style>
"""


# Loading the dataset
file_path = Path(__file__).parent / "olympics_cleaned.csv"
df = pd.read_csv(file_path)


# Creating a dataframe where "No Medal" values are removed
medal_df = df[df['Medal'] != 'No Medal']

# Getting the youngest player of the olympics
youngest_player = df[df['Age'] == df['Age'].min()][['Name', 'Sex', 'Age', 'Sport', 'Team']].iloc[0]
youngest_box = ui.value_box(
    title="Youngest Player of Olympics",
    value=f"{youngest_player['Name']} ({int(youngest_player['Age'])} yrs) - {youngest_player['Sport']} ({youngest_player['Team']})",
    style="background-color: #0066B3; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"
)


# Getting the oldest player of the olympics
oldest_player = df[df['Age'] == df['Age'].max()][['Name', 'Sex', 'Age', 'Sport', 'Team']].iloc[0]
oldest_box = ui.value_box(
    title="Oldest Player of Olympics",
    value=f"{oldest_player['Name']} ({int(oldest_player['Age'])} yrs) - {oldest_player['Sport']} ({oldest_player['Team']})",
    style="background-color: #000000; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"
)

# Getting the player with most medals
most_medals_player = (
    medal_df[medal_df['Medal'].notna()]
    .groupby(['Name', 'Team'])
    .size()
    .sort_values(ascending=False)
    .reset_index(name='MedalCount')
    .iloc[0]
)

most_medals_player_box = ui.value_box(
    title="Player with Most Medals",
    value=f"{most_medals_player['Name']} ({most_medals_player['Team']}) - {most_medals_player['MedalCount']} medals",
    style="background-color: #E4002B; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"
)


# Getting the country with most medals
most_medals_country = (
    medal_df[medal_df['Medal'].notna()]
    .groupby('NOC')
    .size()
    .sort_values(ascending=False)
    .reset_index(name='MedalCount')
    .iloc[0]
)
most_medals_country_box = ui.value_box(
    title="Country with Most Medals",
    value=f"{most_medals_country['NOC']} - {most_medals_country['MedalCount']} medals",
    style="background-color: #009639;" 
)


# Total number of unique events
total_events = df['Event'].nunique() 
total_events_box = ui.value_box(
    title="Total Number of Events",
    value=f"{total_events} events",
    style="background-color: #F6A800; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"
)






# Defining the UI
app_ui = ui.page_navbar(
    ui.nav_panel("Team Performance Analysis",
        ui.page_fluid(
            ui.input_selectize(
                "x",
                "Select a Country:",
                choices=sorted(df['Team'].unique().tolist()),
                selected='Afghanistan',
                multiple=False
            ),
            ui.hr(),
            ui.layout_column_wrap(
                width=12,
                *[
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Medal Distribution by Type</h4>'),
                        ui.output_ui("barplot")
                    ),
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Medals Over the Years</h4>'),
                        ui.input_radio_buttons(
                            "season_choice",
                            "Select Season:",
                            choices=["Summer", "Winter"],
                            selected="Summer",
                            inline=True
                        ),
                        ui.output_ui("lineplot")
                    )
                ]
            ),
            ui.layout_column_wrap(
                width=12,
                *[
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Top Medal Winning Athletes</h4>'),
                        ui.output_data_frame("athlete_df")
                    ),
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Medals by Sport</h4>'),
                        ui.output_ui("barplot_2")
                    )
                ]
            ),
            ui.hr(),
            ui.card(
    ui.output_ui("medalist_title"),
    ui.layout_column_wrap(
        width=6,
        *[
            ui.input_selectize(
                "year_filter",
                "Select Year:",
                choices=sorted(df['Year'].dropna().unique().tolist()),
                selected=None,
                multiple=False
            ),
            ui.output_ui("sport_filter_ui"),  # << sport filter will come dynamically here!
        ]
),
ui.output_ui("medalist_df")

    

)

        )
    ),




    ui.nav_panel("Medal Table",
    ui.page_fluid(
        ui.input_selectize(
            "y",
            "Select a Year:",
            choices=sorted(df['Year'].unique().tolist()),
            selected=1896,
            multiple=False
        ),
    ui.output_ui("host_info"),
    ui.hr(),
    ui.markdown('<h4 style="text-align: center;">Year Wise Team Medals</h4>'),

        ui.div(
            ui.output_ui("year_wise_df"),
            style="""
                width: 100%;
                margin-top: 10px;
                padding: 0 10px;
            """
        )

    )
),

ui.nav_panel("Additional Info",
    ui.page_fluid(
        ui.hr(),
        
        ui.layout_column_wrap(
            width=4, 
            *[
                youngest_box,
                oldest_box,
                most_medals_player_box,
            ]
        ),

        ui.layout_column_wrap(
            width=6,
            *[
    
                ui.value_box(
                    title="Country with Most Medals",
                    value=f"{most_medals_country['NOC']} - {most_medals_country['MedalCount']} medals",
                    style="background-color: #F6A800; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"  
                ),
                
                ui.value_box(
                    title="Total Number of Events",
                    value=f"{total_events} events",
                    style="background-color: #009639; color: white; padding: 15px; font-size: 16px; border-radius: 5px;"  
                ),
            ]
        ),
    


            
            ui.layout_column_wrap(
                width=12,
                *[
                    ui.card(
                        ui.input_selectize(
                            "sport_type",
                            "Select Sport:",
                            choices=sorted(df['Sport'].dropna().unique().tolist()),
                            selected=None,
                            multiple=False
                        ),
                        ui.output_ui("gender_ratio_description"),
                        ui.output_ui("gender_piechart")
                    ),
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Gender Ratio Over The Years</h4>'),
                        ui.output_ui("gender_lineplot")
                    )
                ]
            ),

        
            ui.layout_column_wrap(
                width=12,
                *[
                    ui.card(
                        ui.markdown('<h4 style="text-align: center;">Athlete Age Distribution</h4>'),
                        ui.output_ui("average_age_map")
                    )
                ]
            )
        )
    ),

    # App Title & Settings
    title=ui.HTML('<img src="https://upload.wikimedia.org/wikipedia/commons/5/5c/Olympic_rings_without_rims.svg" style="height:32px; vertical-align: middle; margin-right: 10px;">Olympic Dashboard'),
    id="main_tabs",
    selected="Team Performance Analysis",
    header=ui.tags.head(ui.HTML(right_nav_css))
)



# Defining the server
def server(input, output, session):

    # Getting the input of the user
    @reactive.calc
    def selected_team_df():
        return df[df['Team'] == input.x()]

    # Getting dataframe where "No Medal" values are not included
    @reactive.calc
    def selected_team_medals():
        return selected_team_df()[selected_team_df()['Medal'] != 'No Medal']

    # Top medal winning athletes table
    @output
    @render.data_frame
    def athlete_df():
        medal_df = selected_team_medals().drop_duplicates(subset=['Team', 'Year', 'Sport', 'Event', 'Medal'])
        athlete_performance = (
            medal_df.groupby(['Name', 'Sport'])['Medal']
            .count()
            .sort_values(ascending=False)
            .reset_index()
            [:10]
        )
        if athlete_performance.empty:
            return pd.DataFrame({"Message": ["No medal-winning athletes found for this country."]})
        return render.DataGrid(athlete_performance, width="100%", height="400px")


    # Medal distribution by type barplot
    @output
    @render.ui
    def barplot():
        medal_df = selected_team_medals()
        medal_count = medal_df['Medal'].value_counts()
        if medal_count.empty:
            return ui.h3(f"No medals have been won by {input.x()}")
        fig = px.bar(
            x=medal_count.index,
            y=medal_count.values,
            color=medal_count.index,
            color_discrete_map={'Gold': '#ffbf00', 'Bronze': '#CD7F32', 'Silver': '#c0c0c0'}
        ).update_layout(
            title={"text": f"Barplot of Medals of {input.x()}", "x": 0.5},
            yaxis_title="Count of Medals",
            xaxis_title="Medal Type"
        )
        return fig


    # Medals over the years lineplot
    @output
    @render.ui
    def lineplot():
        medal_df = selected_team_medals()
        season = input.season_choice()
        season_medal_count = medal_df.groupby(['Season', 'Year'])['Medal'].count().reset_index()
        filtered_df = season_medal_count[season_medal_count['Season'] == season]
        if filtered_df.empty:
            return ui.markdown(f"**{input.x()} did not win any medals in the {season} Olympics.**")
        fig = px.line(
            x=filtered_df.Year,
            y=filtered_df.Medal,
            markers=True
        ).update_layout(
            title={"text": f"{season} Olympics Medals Over the Years for {input.x()}", "x": 0.5},
            yaxis_title="Count of Medals",
            xaxis_title="Year"
        )
        return fig


    # Medals by sport barplot
    @output
    @render.ui
    def barplot_2():
        medal_df = selected_team_medals()
        sport_medal = medal_df.groupby('Sport')['Medal'].count().sort_values(ascending=False)[:10]
        if sport_medal.empty:
            return ui.markdown(f"**No medals have been won by {input.x()}.**")
        fig = px.bar(
            x=sport_medal.index,
            y=sport_medal.values,
            color=sport_medal.index
        ).update_layout(
            title={"text": f"Barplot of Medals Won According to Sports Type of {input.x()}", "x": 0.5},
            yaxis_title="Count of Medals",
            xaxis_title="Sport"
        )
        fig.update_xaxes(tickangle=90)
        return fig
    


    @output
    @render.ui
    def sport_filter_ui():
        selected_year = input.year_filter()
        selected_team = input.x()  # ⬅️ Country selected
        
        if selected_year is None or selected_team is None:
            return ui.HTML("<p style='text-align:center;'>Please select both Year and Country to see available sports.</p>")
        
        try:
            year = int(selected_year)
        except (ValueError, TypeError):
            return ui.HTML("<p style='text-align:center;'>Invalid year selected.</p>")
        
        # ⬇️ Filter on Year, Country, and Medal
        medalists = df[
            (df['Year'] == year) &
            (df['Team'] == selected_team) &
            (df['Medal'] != 'No Medal')
        ]
        
        if medalists.empty:
            return ui.HTML("<p style='text-align:center;'>No sports found with medalists for this country and year.</p>")
        
        available_sports = sorted(medalists['Sport'].dropna().unique().tolist())
        
        return ui.input_selectize(
            "sport_filter",
            "Select Sport:",
            choices=available_sports,
            selected=available_sports[0] if available_sports else None,
            multiple=False
        )



    # All medalists Table with Year and Sport as filters
    @output
    @render.ui
    def medalist_df():
        team_df = df[df['Team'] == input.x()]
        medal_df = team_df[team_df['Medal'] != 'No Medal']

        if input.year_filter() is None or input.sport_filter() is None:
            return ui.HTML("<p style='text-align:center;'>Please select both Year and Sport to view results.</p>")

        try:
            year = int(input.year_filter())
        except (ValueError, TypeError):
            return ui.HTML("<p style='text-align:center;'>Invalid year selected.</p>")

        filtered_df = medal_df[
            (medal_df['Year'] == year) &
            (medal_df['Sport'] == input.sport_filter())
        ]

        if filtered_df.empty:
            return ui.HTML("<p style='text-align:center;'>We couldn't find any results matching the selected criteria.</p>")

        medalist_summary = (
            filtered_df.groupby(['Name', 'Sex', 'Age', 'Height', 'Weight', 'Medal'])
            .size()
            .unstack(fill_value=0)
            .reset_index()
            .rename_axis(None, axis=1)
        )

        # Formatting medal column
        def format_medals(row):
            medal_html = ""
            if 'Gold' in row and row['Gold'] > 0:
                medal_html += f"<div class='medal gold'>{row['Gold']}</div> "
            if 'Silver' in row and row['Silver'] > 0:
                medal_html += f"<div class='medal silver'>{row['Silver']}</div> "
            if 'Bronze' in row and row['Bronze'] > 0:
                medal_html += f"<div class='medal bronze'>{row['Bronze']}</div>"
            return medal_html.strip()

        medalist_summary['Medals'] = medalist_summary.apply(format_medals, axis=1)
        medalist_summary = medalist_summary.drop(columns=['Gold', 'Silver', 'Bronze'], errors='ignore')

        # Keeping only necessary columns
        display_df = medalist_summary[['Name', 'Sex', 'Age', 'Height', 'Weight', 'Medals']]

        return ui.HTML(
            display_df.to_html(
                index=False,
                escape=False,
                classes="styled-table",
                justify="center"
            ) + """
            <style>
            .styled-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                text-align: center;
            }
            .styled-table th, .styled-table td {
                padding: 12px 15px;
                border: 1px solid #ddd;
            }
            .styled-table th {
                background-color: #f2f2f2;
            }
            .medal {
                display: inline-block;
                width: 30px;
                height: 30px;
                line-height: 30px;
                border-radius: 50%;
                color: black;
                text-align: center;
                font-weight: bold;
            }
            .gold { background: gold; }
            .silver { background: silver; color: black; }
            .bronze { background: #cd7f32; }
            </style>
            """
        )

    #
    @output
    @render.ui
    def medalist_title():
        team = input.x()
        year = input.year_filter()
        sport = input.sport_filter()

        if year is None or sport is None:
            return ui.markdown(f'<h4 style="text-align: center;">Medalists of {team}</h4>')
        
        return ui.markdown(f'<h4 style="text-align: center;">All Medalists of {team} in {year} - {sport}</h4>')


    @output
    @render.ui
    def year_wise_df():
        year_df = df[df['Year'] == int(input.y())]
        all_medal = year_df[year_df['Medal'] != 'No Medal'].drop_duplicates(subset=['Team', 'Year', 'Sport', 'Event', 'Medal'])


        # Grouping by Year and Team to get the medal count
        year_all_medals = all_medal.groupby(['Year', 'Team'])['Medal'].count().reset_index().sort_values(by=['Year', 'Medal'], ascending=[True,False]).rename(columns={'Medal':'Total'})

        # Gold medal count grouped by Year and Team
        gold_medal = year_df[year_df['Medal'] == 'Gold'].drop_duplicates(subset=['Team', 'Year', 'Sport', 'Event', 'Medal'])

        year_team_gold = gold_medal.groupby(['Year', 'Team'])['Medal'].count().reset_index().sort_values(by=['Year', 'Medal'], ascending=[True,False]).rename(columns={'Medal':'Gold'})

        # Silver medal count grouped by Year and Team
        silver_medal = year_df[year_df['Medal'] == 'Silver'].drop_duplicates(subset=['Team', 'Year', 'Sport', 'Event', 'Medal'])

        year_team_silver = silver_medal.groupby(['Year', 'Team'])['Medal'].count().reset_index().sort_values(by=['Year', 'Medal'], ascending=[True,False]).rename(columns={'Medal':'Silver'})

        # Bronze medal count grouped by Year and Team
        bronze_medal = year_df[year_df['Medal'] == 'Bronze'].drop_duplicates(subset=['Team', 'Year', 'Sport', 'Event', 'Medal'])
        year_team_bronze = bronze_medal.groupby(['Year', 'Team'])['Medal'].count().reset_index().sort_values(by=['Year', 'Medal'], ascending=[True,False]).rename(columns={'Medal':'Bronze'})
        
        # Merging gold and silver tables
        gold_silver = pd.merge(year_team_gold, year_team_silver, on=['Year', 'Team'])


        # Merging gold_silver and bronze tables
        gold_silver_bronze = pd.merge(gold_silver, year_team_bronze, on=['Year', 'Team'])


        # Merging gold_silver_bronze and all medal tables
        all_medal_df = pd.merge(gold_silver_bronze, year_all_medals, on=['Year', 'Team'])
        all_medal_df.drop('Year', inplace=True, axis=1)
        all_medal_df = all_medal_df.sort_values(by='Total', ascending=False)


        # Making the team names bold
        all_medal_df['Team'] = all_medal_df['Team'].apply(lambda x: f"<strong>{x}</strong>")


        if all_medal_df.empty:
            return pd.DataFrame({"Message": ["No data available for the selected year."]})

        def circle_span(val, bg_color):
            return f'<span style="display:inline-block;width:32px;height:32px;line-height:32px;background-color:{bg_color};color:black;font-weight:bold;border-radius:50%;text-align:center;">{int(val)}</span>'

        all_medal_df['Gold'] = all_medal_df['Gold'].apply(lambda x: circle_span(x, '#FFD700'))
        all_medal_df['Silver'] = all_medal_df['Silver'].apply(lambda x: circle_span(x, '#C0C0C0'))
        all_medal_df['Bronze'] = all_medal_df['Bronze'].apply(lambda x: circle_span(x, '#CD7F32'))

        return ui.HTML(
            all_medal_df.to_html(
                index=False,
                escape=False,
                classes="styled-table",
                justify="center"
            ) + """
            <style>
            .styled-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 16px;
                text-align: center;
            }
            .styled-table th, .styled-table td {
                padding: 12px 15px;
                border: 1px solid #ddd;
            }
            .styled-table th {
                background-color: #f2f2f2;
            }
            </style>
            """
        )


    @output
    @render.ui
    def host_info():
        year_selected = int(input.y())
        host_city = df[df['Year'] == year_selected]['City'].unique()
        if len(host_city) == 0:
            return ui.h3("No data for selected year", style="text-align:center;")

        return ui.HTML(f"""
            <div style="
                font-family: 'Olympic Headline', Helvetica, sans-serif;
                font-size: 4rem;
                line-height: 4rem;
                margin-bottom: 0px;
                margin-top: 2.4rem;
                padding-left: 1.9rem;
                text-transform: uppercase;
                width: 100%;
                font-weight: bold;
                color: navy;
            ">
                {host_city[0]} {year_selected}
            </div>
            <div style="
                font-family: 'Olympic Headline', Helvetica, sans-serif;
                font-size: 4rem;
                line-height: 4rem;
                margin-bottom: 0px;
                margin-top: 0.5rem;
                padding-left: 1.9rem;
                text-transform: uppercase;
                width: 100%;
                font-weight: bold;
            ">
                Medal Table
            </div>
        """)




    @output
    @render.ui
    def gender_ratio_description():
        sport = input.sport_type()
        if sport:
            return ui.HTML(f'<h4 style="text-align: center;">Gender ratio of participants in {sport}.</h4>')
        return ui.HTML('<h4 style="text-align: center;">Select a sport to view gender ratio details.</h4>')



    @output
    @render.ui
    def gender_piechart():
        sports_df = df[df["Sport"] == input.sport_type()]
        gender_ratio = round(sports_df['Sex'].value_counts(normalize=True) * 100, 2)

        gender_df = gender_ratio.reset_index()
        gender_df.columns = ['Sex', 'Percentage']

        fig = px.pie(
            gender_df,
            names='Sex',
            values='Percentage',
            color='Sex',
            color_discrete_map={"M": "royalblue", "F": "red"},
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(title_x=0.5)

        return fig
    
    
    @output     
    @render.ui
    def gender_lineplot():
        year_df = round(df.groupby('Year')['Sex'].value_counts(normalize=True)*100,2).reset_index()
        fig = px.line(year_df, x='Year', y='proportion', color='Sex')
        return fig
    



    @output
    @render.ui
    def average_age_map():

        noc_to_team = df[["NOC", "Team"]].drop_duplicates()

        # Group by NOC
        avg_age = round(df.groupby("NOC")["Age"].median(), 2)
        player_count = df["NOC"].value_counts()

        # Merging avg_age and player_count
        stats_df = pd.DataFrame({
            "MedianAge": avg_age,
            "PlayerCount": player_count
        }).reset_index().rename(columns={"index": "NOC"})

        # Merging with team names
        stats_df = stats_df.merge(noc_to_team, on="NOC", how="left")

        # Creating the map
        fig = px.choropleth(
            stats_df,
            locations="NOC",
            locationmode="ISO-3",
            color="MedianAge",
            color_continuous_scale="plasma",
            title="Median Age of Athletes by Country",
            hover_name="Team", 
            hover_data={
                "MedianAge": True,
                "PlayerCount": True,
                "NOC": False
            }
        )

        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=False),
            title_x=0.5,
            height=700,
            width=1400
        )

        return fig


    
    
# Run the app
app = App(app_ui, server)
