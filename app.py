import json
import streamlit as st
from streamlit_echarts import st_echarts
from millify import millify
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from transform import parse_video, youtube_metrics
import warnings
warnings.filterwarnings("ignore")
st.set_page_config(
    page_title="YouTube Analytics Dashboard"
)

def main():
    st.title('YouTube Analytics Dashboard')
    # Add subheading and description
    st.subheader(
        'Data Visualization Project by [Harshita Gupta B20CS018](https://github.com/Harshita-1107) and [Rohit B20CS055](https://github.com/rohitsingh347)')

    VIDEO_URL = st.text_input('Enter URL')

    if st.button('Example'):
        VIDEO_URL = 'https://www.youtube.com/watch?v=adLGHcj_fmA'

    try:
        if VIDEO_URL and "youtube.com/watch?v=" in VIDEO_URL:
            with st.spinner('Crunching numbers...'):
                df = parse_video(VIDEO_URL)
                df_metrics = youtube_metrics(VIDEO_URL)

                col1, col2, col3 = st.columns(3)
                col1.metric("**Views**", millify(df_metrics[0], precision=2))
                col2.metric("**Likes**", millify(df_metrics[1], precision=2))
                col3.metric("**Comments**",
                            millify(df_metrics[2], precision=2))

                st.video(VIDEO_URL)

                st.subheader("Most liked comments")
                df_top = df[['Author', 'Comment', 'Timestamp', 'Likes']].sort_values(
                    'Likes', ascending=False).reset_index(drop=True)

                gd1 = GridOptionsBuilder.from_dataframe(df_top.head(11))
                gridoptions1 = gd1.build()
                AgGrid(df_top.head(11), gridOptions=gridoptions1,
                       theme='streamlit', columns_auto_size_mode='FIT_CONTENTS',
                       update_mode='NO_UPDATE')

                st.subheader("Languages")
                df_langs = df['Language'].value_counts().rename_axis(
                    'Language').reset_index(name='count')

                options2 = {
                    "tooltip": {
                        "trigger": 'axis',
                        "axisPointer": {
                            "type": 'shadow'
                        },
                        "formatter": '{b}: {c}%'
                    },
                    "yAxis": {
                        "type": "category",
                        "data": df_langs['Language'].tolist(),
                    },
                    "xAxis": {"type": "value",
                              "axisTick": {
                                  "alignWithLabel": "true"
                              }
                              },
                    "series": [{"data": df_langs['count'].tolist(), "type": "bar"}],
                }
                st_echarts(options=options2, height="500px")

                st.subheader("Most Replied Comments")
                df_replies = df[['Author', 'Comment', 'Timestamp', 'TotalReplies']].sort_values(
                    'TotalReplies', ascending=False).reset_index(drop=True)

                gd2 = GridOptionsBuilder.from_dataframe(df_replies.head(11))
                gridoptions2 = gd2.build()
                AgGrid(df_replies.head(11), gridOptions=gridoptions2,
                       theme='streamlit', columns_auto_size_mode='FIT_CONTENTS',
                       update_mode='NO_UPDATE')

                st.subheader("Reviews")
                sentiments = df[df['Language'] == 'English']
                data_sentiments = sentiments['TextBlob_Sentiment_Type'].value_counts(
                ).rename_axis('Sentiment').reset_index(name='counts')

                data_sentiments['Review_percent'] = (
                    100. * data_sentiments['counts'] / data_sentiments['counts'].sum()).round(1)

                result = data_sentiments.to_json(orient="split")
                parsed = json.loads(result)

                options = {
                    "tooltip": {"trigger": "item",
                                "formatter": '{d}%'},
                    "legend": {"top": "5%", "left": "center"},
                    "series": [
                        {
                            "name": "Sentiment",
                            "type": "pie",
                            "radius": ["40%", "70%"],
                            "avoidLabelOverlap": False,
                            "itemStyle": {
                                "borderRadius": 10,
                                "borderColor": "#fff",
                                "borderWidth": 2,
                            },
                            "label": {"show": False, "position": "center"},
                            "emphasis": {
                                "label": {"show": True, "fontSize": "30", "fontWeight": "bold"}
                            },
                            "labelLine": {"show": False},
                            "data": [
                                # NEUTRAL
                                {"value": parsed['data'][1][2],
                                 "name": parsed['data'][1][0]},
                                # POSITIVE
                                {"value": parsed['data'][0][2],
                                 "name": parsed['data'][0][0]},
                                # NEGATIVE
                                {"value": parsed['data'][2][2],
                                 "name": parsed['data'][2][0]}
                            ],
                        }
                    ],
                }
                st_echarts(
                    options=options, height="500px",
                )

        elif VIDEO_URL:
            st.error(
                'Please provide a valid YouTube URL of the form: https://www.youtube.com/watch?v=videoID', icon="🚨")
                
    except Exception as e:
        st.error(
            f'An error occurred: {str(e)}', icon="🚨")


if __name__ == "__main__":
    main()
